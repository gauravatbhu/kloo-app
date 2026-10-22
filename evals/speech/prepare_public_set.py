#!/usr/bin/env python3
"""Build Kloo's speech golden set from public, commercially-licensed datasets.

See evals/golden/speech/README.md for the sources, licences and rules. This
script:
  1. streams each source (Hugging Face, or a local Kaldi-style folder),
  2. picks a deterministic sample (hash of source id + seed),
  3. writes 16 kHz mono 16-bit WAVs to --audio-out (never into git),
  4. writes refs/<id>.txt, manifest.jsonl and ATTRIBUTION.md to --out,
  5. adds reel-style copies: music, noise, fast, AAC re-encode, pseudo-reels,
     and prompt-injection clips (if --injection is given).

Network sources need the `datasets` package and HF_TOKEN (a read-only token
for an account that accepted each gated dataset's terms). Local folders
(--local NAME=DIR) need only numpy and ffmpeg, which is how the tests run.

Kaldi-style folder: `text` (utt_id transcript), `wav.scp` (rec_id path),
optional `segments` (utt_id rec_id start end) and `utt2spk` (utt_id speaker).
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

SET_VERSION = "speech-public-v1"
DEFAULT_SEED = "kloo-speech-v1"
RATE = 16000
MIN_S, MAX_S = 2.0, 30.0
REEL_MIN_S, REEL_MAX_S = 30.0, 75.0

# Field names for Hugging Face sources are tried in order; the first present
# wins. If none is present the script stops and prints the available keys, so
# a changed dataset card is caught on the first run rather than silently.
SOURCES = {
    "indicvoices": dict(kind="hf", repo="ai4bharat/IndicVoices", config="hindi", split="valid",
                        lang="hi", variety="hindi", licence="CC-BY-4.0", n=400, keep=0.25,
                        prefix="iv", pseudo_reels=40,
                        url="https://huggingface.co/datasets/ai4bharat/IndicVoices"),
    "lahaja": dict(kind="hf", repo="ai4bharat/Lahaja", config=None, split="test",
                   lang="hi", variety="hindi", licence="CC-BY-4.0", n=300, keep=0.1,
                   prefix="lj", url="https://huggingface.co/datasets/ai4bharat/Lahaja"),
    "kathbath": dict(kind="hf", repo="ai4bharat/Kathbath", config="hindi", split="test",
                     lang="hi", variety="hindi", licence="CC-BY-4.0", n=200, keep=0.1,
                     prefix="kb", url="https://huggingface.co/datasets/ai4bharat/Kathbath"),
    "fleurs_hi": dict(kind="hf", repo="google/fleurs", config="hi_in", split="test",
                      lang="hi", variety="hindi", licence="CC-BY-4.0", n=None, keep=1.0,
                      prefix="flhi", url="https://huggingface.co/datasets/google/fleurs"),
    "mucs": dict(kind="kaldi", lang="hi", variety="hinglish", licence="CC-BY-SA-4.0", n=300,
                 keep=0.15, prefix="mucs", url="https://openslr.org/104/"),
    "svarah": dict(kind="hf", repo="ai4bharat/Svarah", config=None, split="test",
                   lang="en", variety="english", licence="CC-BY-4.0", n=400, keep=0.25,
                   prefix="sv", url="https://huggingface.co/datasets/ai4bharat/Svarah"),
    "fleurs_en": dict(kind="hf", repo="google/fleurs", config="en_us", split="test",
                      lang="en", variety="english", licence="CC-BY-4.0", n=300, keep=0.5,
                      prefix="flen", url="https://huggingface.co/datasets/google/fleurs"),
}
TEXT_KEYS = ("raw_transcription", "transcription", "text", "transcript", "verbatim", "sentence")
ID_KEYS = ("path", "id", "utterance_id", "audio_filepath", "file", "fname")
SPEAKER_KEYS = ("speaker_id", "speaker", "client_id", "spk_id")
BAD_REF = re.compile(r"<\s*(unk|noise|overlap)\s*>|\[\s*(unk|unclear)\s*\]|\*\*", re.I)
LATIN_WORD = re.compile(r"^[A-Za-z][A-Za-z'\-]*$")

# Augmentation plan, applied to a seeded 50% of base clips (README table).
AUGMENT_SHARE = 0.5
CONDITION_WEIGHTS = (("music", 0.40), ("noise", 0.30), ("fast", 0.20), ("music_noise", 0.10))


# ---------------------------------------------------------------- helpers
def h01(*parts):
    """Deterministic number in [0, 1) from strings."""
    digest = hashlib.sha256(":".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(1 << 48)


def short_hash(*parts):
    return hashlib.sha256(":".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:10]


def ffmpeg(args, stdin=None):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args,
                       input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed: " + p.stderr.decode("utf-8", "replace")[-500:])
    return p.stdout


def load_audio_file(path, start=None, end=None):
    """Any audio file -> float32 mono 16 kHz."""
    args = []
    if start is not None:
        args += ["-ss", f"{start:.3f}"]
    if end is not None:
        args += ["-to", f"{end:.3f}"]
    out = ffmpeg(["-i", path] + args + ["-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"])
    return np.frombuffer(out, dtype=np.float32).copy()


def resample(array, rate):
    array = np.asarray(array, dtype=np.float32)
    if array.ndim > 1:
        array = array.mean(axis=1 if array.shape[0] > array.shape[1] else 0)
    if rate == RATE:
        return array
    out = ffmpeg(["-f", "f32le", "-ar", str(rate), "-ac", "1", "-i", "-",
                  "-ar", str(RATE), "-f", "f32le", "-"], stdin=array.tobytes())
    return np.frombuffer(out, dtype=np.float32).copy()


def write_wav(path, audio):
    audio = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    pcm = (audio * 32767.0).astype("<i2")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def latin_share(text):
    words = text.split()
    if not words:
        return 0.0
    return sum(1 for w in words if LATIN_WORD.match(w.strip(".,!?;:\"()"))) / len(words)


# ---------------------------------------------------------------- augmentation
def power(x):
    return float(np.mean(np.square(x, dtype=np.float64))) + 1e-12


def fit_length(bg, n, offset_seed):
    """Loop or crop background to n samples, starting at a seeded offset."""
    if len(bg) == 0:
        return np.zeros(n, dtype=np.float32)
    reps = int(np.ceil((n + len(bg)) / len(bg)))
    tiled = np.tile(bg, reps)
    start = int(h01(offset_seed) * len(bg))
    return tiled[start:start + n]


def mix_at_snr(speech, bg, snr_db, offset_seed="0"):
    """Mix background under speech so that 10*log10(P_speech/P_bg) == snr_db."""
    bg = fit_length(bg, len(speech), offset_seed)
    scale = np.sqrt(power(speech) / (power(bg) * (10.0 ** (snr_db / 10.0))))
    mixed = speech + scale * bg
    peak = float(np.max(np.abs(mixed))) if len(mixed) else 0.0
    return (mixed / peak * 0.95 if peak > 0.99 else mixed).astype(np.float32)


def tempo(audio, factor):
    out = ffmpeg(["-f", "f32le", "-ar", str(RATE), "-ac", "1", "-i", "-",
                  "-filter:a", f"atempo={factor}", "-f", "f32le", "-"], stdin=audio.tobytes())
    return np.frombuffer(out, dtype=np.float32).copy()


def reencode_aac(audio, tmp_dir, tag):
    """AAC 128 kbps 44.1 kHz round trip, like a platform upload."""
    m4a = os.path.join(tmp_dir, f"_re_{tag}.m4a")
    ffmpeg(["-f", "f32le", "-ar", str(RATE), "-ac", "1", "-i", "-", "-ar", "44100",
            "-c:a", "aac", "-b:a", "128k", m4a], stdin=audio.tobytes())
    try:
        return load_audio_file(m4a)
    finally:
        os.remove(m4a)


class Backgrounds:
    """MUSAN music/noise pools (lazy-loaded, deterministic choice)."""

    def __init__(self, musan_dir):
        self.pools = {}
        for kind in ("music", "noise"):
            files = sorted(glob.glob(os.path.join(musan_dir or "", kind, "**", "*.wav"),
                                     recursive=True)) if musan_dir else []
            self.pools[kind] = files
        self.root = musan_dir
        self._cache = {}

    def available(self, kind):
        return bool(self.pools.get(kind))

    def pick(self, kind, seed):
        files = self.pools[kind]
        path = files[int(h01(kind, seed) * len(files))]
        if path not in self._cache:
            if len(self._cache) > 32:
                self._cache.clear()
            self._cache[path] = load_audio_file(path)
        rel = os.path.relpath(path, self.root).replace(os.sep, "/")
        return self._cache[path], "musan/" + rel


def choose_condition(seed):
    r, acc = h01("cond", seed), 0.0
    for name, w in CONDITION_WEIGHTS:
        acc += w
        if r < acc:
            return name
    return CONDITION_WEIGHTS[-1][0]


def augment(clip_id, audio, bgs, tmp_dir, seed):
    """Return (suffix, audio, extra_manifest_fields) for one degraded copy, or None."""
    cond = choose_condition(seed + clip_id)
    fields = {}
    if cond in ("music", "music_noise") and not bgs.available("music"):
        cond = "fast"
    if cond == "noise" and not bgs.available("noise"):
        cond = "fast"
    out = audio
    conditions = []
    if cond in ("music", "music_noise"):
        snr = 5 if h01("snr", seed, clip_id) < 1 / 3 else 10
        bg, name = bgs.pick("music", seed + clip_id)
        out = mix_at_snr(out, bg, snr, seed + clip_id)
        conditions.append("music")
        fields.update(snr_db=snr, background=name)
    if cond in ("noise", "music_noise"):
        snr = 5 + round(h01("nsnr", seed, clip_id) * 10)
        bg, name = bgs.pick("noise", seed + clip_id)
        out = mix_at_snr(out, bg, snr, "n" + seed + clip_id)
        conditions.append("noise")
        key = "noise_snr_db" if "snr_db" in fields else "snr_db"
        fields[key] = snr
        fields["background" if "background" not in fields else "background2"] = name
    if cond == "fast":
        out = tempo(out, 1.15)
        conditions.append("fast")
        fields["tempo"] = 1.15
    out = reencode_aac(out, tmp_dir, short_hash(clip_id, cond))
    conditions.append("reencode")
    suffix = {"music": "music", "noise": "noise", "fast": "fast", "music_noise": "mixnoise"}[cond]
    if "snr_db" in fields and cond != "fast":
        suffix += str(fields["snr_db"])
    return suffix, out, conditions, fields


# ---------------------------------------------------------------- sources
def pick_key(row, keys, what, source):
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return k
    raise SystemExit(f"{source}: no {what} field among {keys}; row has {sorted(row)}. "
                     f"Update SOURCES/keys in {os.path.basename(__file__)}.")


def iter_hf(name, cfg, token):
    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit("pip install -r evals/speech/requirements.txt (needs `datasets`)")
    kwargs = dict(split=cfg["split"], streaming=True, token=token)
    ds = load_dataset(cfg["repo"], cfg["config"], **kwargs) if cfg.get("config") \
        else load_dataset(cfg["repo"], **kwargs)
    keys = None
    for row in ds:
        if keys is None:
            keys = (pick_key(row, TEXT_KEYS, "transcript", name),
                    pick_key(row, ID_KEYS, "id", name))
            spk = next((k for k in SPEAKER_KEYS if k in row), None)
        tk, ik = keys
        audio = row.get("audio") or {}
        sid = row[ik]
        if isinstance(sid, str) and ("/" in sid or "\\" in sid):
            sid = os.path.basename(sid)
        yield {
            "source_id": str(sid),
            "text": str(row[tk]),
            "speaker": str(row[spk]) if spk else None,
            "load": (lambda a=audio: resample(a["array"], a["sampling_rate"])),
            "duration": (len(audio["array"]) / float(audio["sampling_rate"]))
            if audio.get("array") is not None else None,
        }


def read_table(path, n_fields):
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(None, n_fields - 1)
            if len(parts) == n_fields:
                rows.append(parts)
    return rows


def iter_kaldi(name, folder):
    text = read_table(os.path.join(folder, "text"), 2)
    if not text:
        raise SystemExit(f"{name}: no 'text' file in {folder}")
    wavs = dict(read_table(os.path.join(folder, "wav.scp"), 2))
    segs = {u: (r, float(s), float(e)) for u, r, s, e in read_table(os.path.join(folder, "segments"), 4)}
    spk = dict(read_table(os.path.join(folder, "utt2spk"), 2))
    for utt, transcript in text:
        if utt in segs:
            rec, start, end = segs[utt]
        else:
            rec, start, end = utt, None, None
        path = wavs.get(rec)
        if not path:
            continue
        if not os.path.isabs(path):
            path = os.path.join(folder, path)
        yield {
            "source_id": utt, "text": transcript, "speaker": spk.get(utt),
            "load": (lambda p=path, s=start, e=end: load_audio_file(p, s, e)),
            "duration": (end - start) if start is not None else None,
        }


# ---------------------------------------------------------------- build
class Builder:
    def __init__(self, out_dir, audio_dir, seed, backgrounds, scale=1.0, log=print):
        self.out_dir, self.audio_dir, self.seed = out_dir, audio_dir, seed
        self.bgs, self.scale, self.log = backgrounds, scale, log
        self.manifest, self.used_sources = [], {}
        self.tmp = os.path.join(audio_dir, "_tmp")
        os.makedirs(os.path.join(out_dir, "refs"), exist_ok=True)
        os.makedirs(self.tmp, exist_ok=True)

    def emit(self, clip_id, audio, ref, base):
        sha = write_wav(os.path.join(self.audio_dir, clip_id + ".wav"), audio)
        with open(os.path.join(self.out_dir, "refs", clip_id + ".txt"), "w", encoding="utf-8") as f:
            f.write(ref.strip() + "\n")
        entry = dict(base, id=clip_id, duration_s=round(len(audio) / RATE, 2), sha256=sha,
                     set_version=SET_VERSION)
        self.manifest.append(entry)
        return entry

    def add_source(self, name, cfg, rows):
        n = cfg["n"] if cfg["n"] is None else max(1, int(round(cfg["n"] * self.scale)))
        reels_wanted = int(round(cfg.get("pseudo_reels", 0) * self.scale))
        taken = reels = 0
        run, run_spk = [], None
        base_clean = []

        def flush_run():
            nonlocal reels
            if reels >= reels_wanted or not run:
                return
            total = sum(len(a) for a, _, _ in run) / RATE
            if total < REEL_MIN_S or h01("reel", self.seed, name, run[0][2]) >= 0.5:
                return
            gap = np.zeros(int(0.3 * RATE), dtype=np.float32)
            parts, refs, dur = [], [], 0.0
            for a, t, _ in run:
                if dur + len(a) / RATE > REEL_MAX_S:
                    break
                parts += [a, gap]
                refs.append(t)
                dur += len(a) / RATE + 0.3
            if dur < REEL_MIN_S:
                return
            cid = f"{cfg['prefix']}-{cfg['lang']}-{short_hash(name, run[0][2])}__long"
            self.emit(cid, np.concatenate(parts[:-1]), " ".join(refs), dict(
                lang=cfg["lang"], variety=self._variety(cfg, " ".join(refs)), source=name,
                source_id="+".join(r[2] for r in run[:len(refs)]), licence=cfg["licence"],
                conditions=["long"], speaker_id=f"{name}:{run_spk}", injection=False,
                synthetic=False))
            reels += 1

        for row in rows:
            if (n is not None and taken >= n) and reels >= reels_wanted:
                break
            text = " ".join(row["text"].split())
            if not text or BAD_REF.search(text):
                continue
            want_base = (n is None or taken < n) and h01(self.seed, name, row["source_id"]) < cfg["keep"]
            want_reel = reels_wanted and reels < reels_wanted and row.get("speaker")
            if not want_base and not want_reel:
                continue
            if row.get("duration") is not None and not want_reel and \
                    not MIN_S <= row["duration"] <= MAX_S:
                continue
            audio = row["load"]()
            secs = len(audio) / RATE
            if want_reel:
                if row["speaker"] != run_spk:
                    flush_run()
                    run, run_spk = [], row["speaker"]
                if MIN_S <= secs <= MAX_S:
                    run.append((audio, text, row["source_id"]))
                    if sum(len(a) for a, _, _ in run) / RATE >= REEL_MAX_S:
                        flush_run()
                        run = []
            if not want_base or not MIN_S <= secs <= MAX_S:
                continue
            cid = f"{cfg['prefix']}-{cfg['lang']}-{short_hash(name, row['source_id'])}"
            base = dict(lang=cfg["lang"], variety=self._variety(cfg, text), source=name,
                        source_id=row["source_id"], licence=cfg["licence"],
                        speaker_id=f"{name}:{row['speaker']}" if row.get("speaker") else None,
                        injection=False, synthetic=False)
            self.emit(cid, audio, text, dict(base, conditions=["clean"]))
            base_clean.append((cid, audio, text, base))
            if h01("aug", self.seed, cid) < AUGMENT_SHARE:
                suffix, aud2, conds, fields = augment(cid, audio, self.bgs, self.tmp, self.seed)
                self.emit(f"{cid}__{suffix}", aud2, text, dict(base, conditions=conds, **fields))
            taken += 1
        flush_run()
        self.used_sources[name] = cfg
        self.log(f"{name}: {taken} base clips, {reels} pseudo-reels")
        return base_clean

    @staticmethod
    def _variety(cfg, text):
        if cfg["lang"] == "hi" and cfg["variety"] == "hindi" and latin_share(text) >= 0.15:
            return "hinglish"
        return cfg["variety"]

    def add_injections(self, inj_dir, clean_by_lang, per_lang=10):
        """inj_dir holds <lang>-<k>.wav + <lang>-<k>.txt (synthesised lines)."""
        for lang, clips in clean_by_lang.items():
            lines = sorted(glob.glob(os.path.join(inj_dir, f"{lang}-*.wav")))
            if not lines or len(clips) < 2:
                continue
            ordered = sorted(clips, key=lambda c: h01("inj", self.seed, c[0]))
            for k in range(min(per_lang, len(ordered) // 2)):
                (ida, a, ta, base), (_, b, tb, _) = ordered[2 * k], ordered[2 * k + 1]
                line_wav = lines[k % len(lines)]
                with open(line_wav[:-4] + ".txt", encoding="utf-8") as f:
                    line_txt = f.read().strip()
                line_audio = load_audio_file(line_wav)
                gap = np.zeros(int(0.3 * RATE), dtype=np.float32)
                audio = np.concatenate([a, gap, line_audio, gap, b])
                self.emit(f"{ida}__inject", audio, f"{ta} {line_txt} {tb}", dict(
                    base, conditions=["clean"], injection=True, synthetic=True,
                    injection_line=os.path.basename(line_wav)))

    def finish(self):
        with open(os.path.join(self.out_dir, "manifest.jsonl"), "w", encoding="utf-8") as f:
            for e in self.manifest:
                f.write(json.dumps({k: v for k, v in e.items() if v is not None},
                                   ensure_ascii=False) + "\n")
        lines = ["# Speech golden set: attribution", "",
                 f"Set version `{SET_VERSION}`, seed `{self.seed}`. Generated by "
                 "`evals/speech/prepare_public_set.py`. Audio is not redistributed.", "",
                 "| Source | Licence | Link |", "|---|---|---|"]
        for name, cfg in self.used_sources.items():
            lines.append(f"| {name} | {cfg['licence']} | {cfg['url']} |")
        if self.bgs.root:
            lines.append("| MUSAN (augmentation backgrounds) | CC-BY-4.0 | https://openslr.org/17/ |")
        lines += ["", "Gated datasets: paste the terms text you accepted below, with the date.", ""]
        with open(os.path.join(self.out_dir, "ATTRIBUTION.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        try:
            os.rmdir(self.tmp)
        except OSError:
            pass
        return self.manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="golden-set folder (manifest, refs)")
    ap.add_argument("--audio-out", required=True, help="where WAVs go (NOT inside git)")
    ap.add_argument("--sources", default=",".join(SOURCES), help="comma list of source names")
    ap.add_argument("--local", action="append", default=[], metavar="NAME=DIR",
                    help="read source NAME from a Kaldi-style folder instead of the network")
    ap.add_argument("--mucs", help="Kaldi-style MUCS 2021 Hindi-English test folder")
    ap.add_argument("--musan", help="unpacked MUSAN folder (music/, noise/)")
    ap.add_argument("--injection", help="folder of synthesised injection lines (<lang>-<k>.wav/.txt)")
    ap.add_argument("--seed", default=DEFAULT_SEED)
    ap.add_argument("--scale", type=float, default=1.0, help="multiply sample sizes (smoke tests)")
    args = ap.parse_args(argv)

    if os.path.commonpath([os.path.abspath(args.audio_out), os.path.abspath(args.out)]) == \
            os.path.abspath(args.out):
        print("note: --audio-out is inside --out; .gitignore blocks audio/ and *.wav there")
    local = dict(item.split("=", 1) for item in args.local)
    if args.mucs:
        local.setdefault("mucs", args.mucs)
    token = os.environ.get("HF_TOKEN")
    builder = Builder(args.out, args.audio_out, args.seed, Backgrounds(args.musan), args.scale)
    clean_by_lang = {}
    for name in [s.strip() for s in args.sources.split(",") if s.strip()]:
        if name not in SOURCES:
            raise SystemExit(f"unknown source {name}; known: {', '.join(SOURCES)}")
        cfg = SOURCES[name]
        if name in local:
            rows = iter_kaldi(name, local[name])
        elif cfg["kind"] == "kaldi":
            print(f"{name}: skipped (pass --local {name}=DIR or --{name})", file=sys.stderr)
            continue
        else:
            if not token:
                print(f"{name}: skipped (HF_TOKEN not set)", file=sys.stderr)
                continue
            rows = iter_hf(name, cfg, token)
        clean = builder.add_source(name, cfg, rows)
        clean_by_lang.setdefault(cfg["lang"], []).extend(clean)
    if args.injection:
        builder.add_injections(args.injection, clean_by_lang)
    manifest = builder.finish()
    print(f"wrote {len(manifest)} clips to {args.out} (audio in {args.audio_out})")
    return 0 if manifest else 2


if __name__ == "__main__":
    sys.exit(main())
