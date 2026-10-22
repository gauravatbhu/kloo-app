#!/usr/bin/env python3
"""Kloo speech eval runner (engine-agnostic).

Scores hypothesis transcripts from any engine (whisper.cpp, WhisperKit,
IndicConformer, ...) against the speech golden set, and writes result lines in
the format evals/run_evals.py expects:

  {"suite":"speech","id":"...","lang":"en|hi","reference":"...","hypothesis":"...", ...}

"reference" and "hypothesis" are written already normalised (English: strict;
Hindi/Hinglish: script-agnostic Hinglish skeleton, see speech_normalise.py), so
run_evals.py computes exactly the WER this runner reports. Extra fields
(variety, topic, conditions, engine, model, device, tier, normaliser, raw
texts) are ignored by run_evals.py but kept for error analysis.

Golden-set layout (see evals/golden/speech/README.md):
  GOLDEN/manifest.jsonl       one JSON object per clip: id, lang, variety, ...
  GOLDEN/refs/<id>.txt        reference transcript, UTF-8
  GOLDEN/audio/<id>.wav       16 kHz mono 16-bit PCM (NOT in git; optional here)
Hypothesis folder:
  HYPS/<id>.txt | <id>.srt | <id>.vtt   engine output; timestamps are stripped

Usage:
  python3 evals/speech/run_speech_eval.py --golden evals/speech/example \
      --hyps evals/speech/example/hyps --out /tmp/speech_results.jsonl \
      --engine whisper.cpp --model ggml-small-q5_1 --device "Pixel 9" --tier 1

  python3 evals/run_evals.py --results /tmp/speech_results.jsonl

Exit codes: 0 ok, 2 input problems (bad manifest, missing reference, missing
hypothesis unless --missing empty, audio check failures with --check-audio).
"""
import argparse
import hashlib
import importlib
import json
import os
import re
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from speech_normalise import (  # noqa: E402
    NORMALISER_VERSION, hinglish_normalise, load_lexicon, script_profile, strict_normalise,
)

LANGS = ("en", "hi")
VARIETIES = {"en": {"english"}, "hi": {"hindi", "hinglish"}}
# Public-set utterances are short (2-30 s); pseudo-reels run up to 90 s.
MIN_SECONDS, MAX_SECONDS = 2.0, 90.0
_TS_LINE = re.compile(r"^\s*(\d+\s*$|WEBVTT|NOTE\b|\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s*-->)")
_TS_PREFIX = re.compile(r"^\s*\[\s*\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s*-->\s*[\d:.,]+\s*\]\s*")


# ---------------------------------------------------------------- scoring
def edit_ops(ref, hyp):
    """Levenshtein distance plus (substitutions, deletions, insertions)."""
    rows = len(ref) + 1
    cols = len(hyp) + 1
    d = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        d[i][0] = i
    for j in range(cols):
        d[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1,
                          d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]))
    i, j, s, dl, ins = len(ref), len(hyp), 0, 0, 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
            s += ref[i - 1] != hyp[j - 1]
            i, j = i - 1, j - 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            dl += 1
            i -= 1
        else:
            ins += 1
            j -= 1
    return d[-1][-1], s, dl, ins


def score_pair(ref_text, hyp_text):
    """Word errors, ref word count and char errors/count on space-joined text."""
    rw, hw = ref_text.split(), hyp_text.split()
    werr, sub, dele, ins = edit_ops(rw, hw)
    cerr, _, _, _ = edit_ops(list(" ".join(rw)), list(" ".join(hw)))
    return {"word_errors": werr, "ref_words": len(rw), "sub": sub, "del": dele, "ins": ins,
            "char_errors": cerr, "ref_chars": len(" ".join(rw))}


# ---------------------------------------------------------------- inputs
def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def clean_hypothesis(raw):
    """Strip whisper.cpp / SRT / VTT timing so only spoken text remains."""
    lines = []
    for line in raw.splitlines():
        if _TS_LINE.match(line):
            continue
        lines.append(_TS_PREFIX.sub("", line))
    return " ".join(" ".join(lines).split())


def find_hypothesis(hyp_dir, clip_id):
    for ext in (".txt", ".srt", ".vtt"):
        p = os.path.join(hyp_dir, clip_id + ext)
        if os.path.isfile(p):
            return p
    return None


def load_manifest(path):
    clips, problems, seen = [], [], set()
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                c = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"manifest line {n}: invalid JSON ({e})")
                continue
            cid, lang = c.get("id"), c.get("lang")
            if not cid or lang not in LANGS:
                problems.append(f"manifest line {n}: needs 'id' and 'lang' in {LANGS}")
                continue
            if cid in seen:
                problems.append(f"manifest line {n}: duplicate id {cid}")
                continue
            seen.add(cid)
            variety = c.get("variety") or ("english" if lang == "en" else "hindi")
            if variety not in VARIETIES[lang]:
                problems.append(f"{cid}: variety '{variety}' not valid for lang '{lang}'")
            c["variety"] = variety
            clips.append(c)
    return clips, problems


def check_audio(path, expected_sha=None):
    """Return a list of problems for one audio file (stdlib only; WAV)."""
    problems = []
    if not os.path.isfile(path):
        return [f"missing audio {os.path.basename(path)}"]
    if expected_sha:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
        if h.hexdigest() != expected_sha.lower():
            problems.append(f"{os.path.basename(path)}: sha256 mismatch")
    if not path.lower().endswith(".wav"):
        return problems + [f"{os.path.basename(path)}: expected .wav"]
    try:
        with wave.open(path, "rb") as w:
            ch, rate, width, frames = w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes()
    except (wave.Error, EOFError) as e:
        return problems + [f"{os.path.basename(path)}: unreadable WAV ({e})"]
    if (ch, rate, width) != (1, 16000, 2):
        problems.append(f"{os.path.basename(path)}: need mono 16 kHz 16-bit, got "
                        f"{ch} ch {rate} Hz {8 * width}-bit")
    secs = frames / float(rate or 1)
    if not MIN_SECONDS <= secs <= MAX_SECONDS:
        problems.append(f"{os.path.basename(path)}: {secs:.1f} s outside {MIN_SECONDS:.0f}-{MAX_SECONDS:.0f} s")
    return problems


def load_translit(spec):
    """'package.module:function' -> callable(token) -> str."""
    if not spec:
        return None
    mod_name, _, fn_name = spec.partition(":")
    fn = getattr(importlib.import_module(mod_name), fn_name or "transliterate")
    if not callable(fn):
        raise SystemExit(f"--translit {spec} is not callable")
    return fn


# ---------------------------------------------------------------- main logic
def evaluate(clips, golden_dir, hyp_dir, lexicon, translit, missing="error"):
    rows, problems = [], []
    for c in clips:
        cid, lang = c["id"], c["lang"]
        ref_path = os.path.join(golden_dir, "refs", cid + ".txt")
        if not os.path.isfile(ref_path):
            problems.append(f"{cid}: missing reference {ref_path}")
            continue
        raw_ref = read_text(ref_path)
        hyp_path = find_hypothesis(hyp_dir, cid)
        if hyp_path is None:
            if missing == "error":
                problems.append(f"{cid}: missing hypothesis in {hyp_dir}")
                continue
            raw_hyp = ""
        else:
            raw_hyp = clean_hypothesis(read_text(hyp_path))

        strict_ref, strict_hyp = strict_normalise(raw_ref), strict_normalise(raw_hyp)
        if lang == "hi":
            ref = hinglish_normalise(raw_ref, lexicon, translit)
            hyp = hinglish_normalise(raw_hyp, lexicon, translit)
        else:
            ref, hyp = strict_ref, strict_hyp
        if not ref:
            problems.append(f"{cid}: reference is empty after normalisation")
            continue
        sc = score_pair(ref, hyp)
        st = score_pair(strict_ref, strict_hyp)
        prof = script_profile(raw_hyp)
        rows.append({
            "suite": "speech", "id": cid, "lang": lang,
            "reference": ref, "hypothesis": hyp,
            "variety": c["variety"], "topic": c.get("topic"),
            "source": c.get("source"), "licence": c.get("licence"),
            "synthetic": bool(c.get("synthetic")),
            "conditions": c.get("conditions", []), "injection": bool(c.get("injection")),
            "normaliser": NORMALISER_VERSION,
            "missing_hypothesis": hyp_path is None,
            "hyp_script": {k: round(v, 3) for k, v in prof.items()},
            "scores": {"official": sc, "strict": st},
            "raw_reference": raw_ref.strip(), "raw_hypothesis": raw_hyp,
        })
    return rows, problems


def _rate(rows, kind, num, den):
    n = sum(r["scores"][kind][num] for r in rows)
    d = sum(r["scores"][kind][den] for r in rows)
    return round(n / d, 4) if d else None


def summarise(rows):
    """Corpus-level WER per group: lang, variety, source, condition, topic, injection."""
    groups = {}

    def add(key, r):
        groups.setdefault(key, []).append(r)

    for r in rows:
        add(f"lang={r['lang']}", r)
        add(f"variety={r['variety']}", r)
        if r.get("source"):
            add(f"lang={r['lang']}/source={r['source']}", r)
        if r.get("topic"):
            add(f"lang={r['lang']}/topic={r['topic']}", r)
        for cond in r.get("conditions") or ["clean"]:
            add(f"lang={r['lang']}/condition={cond}", r)
        if r.get("injection"):
            add(f"lang={r['lang']}/injection", r)
    out = {}
    for key in sorted(groups):
        rs = groups[key]
        out[key] = {
            "clips": len(rs),
            "ref_words": sum(r["scores"]["official"]["ref_words"] for r in rs),
            "wer": _rate(rs, "official", "word_errors", "ref_words"),
            "wer_strict": _rate(rs, "strict", "word_errors", "ref_words"),
            "cer_strict": _rate(rs, "strict", "char_errors", "ref_chars"),
            "wrong_script_clips": sum(1 for r in rs if r["hyp_script"]["arab"] > 0.2),
            "missing_hypotheses": sum(1 for r in rs if r["missing_hypothesis"]),
        }
    return out


def format_summary(summary, meta):
    lines = [f"Speech eval: engine={meta.get('engine')} model={meta.get('model')} "
             f"device={meta.get('device')} tier={meta.get('tier')} normaliser={NORMALISER_VERSION}",
             f"{'group':44} {'clips':>5} {'words':>6} {'WER':>7} {'WERstr':>7} {'CERstr':>7}"
             f" {'urdu':>4} {'miss':>4}"]
    for key, s in summary.items():
        f = lambda v: "   —   " if v is None else f"{100 * v:6.1f}%"  # noqa: E731
        lines.append(f"{key:44} {s['clips']:5d} {s['ref_words']:6d} {f(s['wer'])} "
                     f"{f(s['wer_strict'])} {f(s['cer_strict'])}"
                     f" {s['wrong_script_clips']:4d} {s['missing_hypotheses']:4d}")
    lines.append("WER = official (en: strict; hi: script-agnostic Hinglish skeleton). "
                 "WERstr/CERstr = script-preserving. urdu = clips whose output is >20% Arabic script.")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--golden", required=True, help="folder with manifest.jsonl, refs/, audio/")
    ap.add_argument("--hyps", required=True, help="folder of <id>.txt|.srt|.vtt engine outputs")
    ap.add_argument("--out", required=True, help="results JSONL for evals/run_evals.py")
    ap.add_argument("--append", action="store_true", help="append to --out instead of overwriting")
    ap.add_argument("--summary", help="also write the per-group summary as JSON")
    ap.add_argument("--audio", help="audio folder (default GOLDEN/audio)")
    ap.add_argument("--check-audio", action="store_true",
                    help="fail if audio is missing, not 16 kHz mono 16-bit WAV, or outside 15-90 s")
    ap.add_argument("--verify-checksums", action="store_true", help="check manifest sha256 per clip")
    ap.add_argument("--lexicon", default=os.path.join(HERE, "translit_lexicon.tsv"))
    ap.add_argument("--translit", help="transliteration hook 'module:function' for Devanagari tokens")
    ap.add_argument("--missing", choices=("error", "empty"), default="error",
                    help="missing hypothesis: fail (default) or score as empty transcript")
    ap.add_argument("--engine", default="unknown")
    ap.add_argument("--model", default="unknown")
    ap.add_argument("--device", default="unknown")
    ap.add_argument("--tier", default=None)
    a = ap.parse_args(argv)

    clips, problems = load_manifest(os.path.join(a.golden, "manifest.jsonl"))
    lexicon = load_lexicon(a.lexicon) if a.lexicon and os.path.isfile(a.lexicon) else {}
    translit = load_translit(a.translit)

    audio_dir = a.audio or os.path.join(a.golden, "audio")
    if a.check_audio or a.verify_checksums:
        for c in clips:
            path = os.path.join(audio_dir, c.get("audio") or c["id"] + ".wav")
            sha = c.get("sha256") if a.verify_checksums else None
            problems += check_audio(path, sha)

    rows, eval_problems = evaluate(clips, a.golden, a.hyps, lexicon, translit, a.missing)
    problems += eval_problems

    meta = {"engine": a.engine, "model": a.model, "device": a.device, "tier": a.tier}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "a" if a.append else "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({**r, **meta}, ensure_ascii=False) + "\n")

    summary = summarise(rows)
    print(format_summary(summary, meta))
    if a.summary:
        with open(a.summary, "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "normaliser": NORMALISER_VERSION, "groups": summary},
                      f, indent=2, ensure_ascii=False)
    if problems:
        print("\nProblems:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
