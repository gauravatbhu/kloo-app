#!/usr/bin/env python3
"""Convert downloaded open speech datasets into the Kaldi-style folders that
prepare_public_set.py reads with --local NAME=DIR.

  fleurs  DIR_WITH_TSV_AND_AUDIO  OUT   (FLEURS <split>.tsv + extracted audio/)
  mucs    EXTRACTED_TAR_DIR       OUT   (MUCS 2021 Hindi-English test)

Both writers produce: text, wav.scp (absolute paths), optional segments,
utt2spk. The MUCS layout is not documented on OpenSLR, so the converter
searches the tree for the Kaldi files and matches recordings to audio by
file name. It prints what it found so a CI log shows any surprise.
"""
import os
import sys


def write_folder(out, texts, wavs, segments=None, spk=None):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "text"), "w", encoding="utf-8") as f:
        for utt, t in texts:
            f.write(f"{utt} {t}\n")
    with open(os.path.join(out, "wav.scp"), "w", encoding="utf-8") as f:
        for rec, path in sorted(wavs.items()):
            f.write(f"{rec} {os.path.abspath(path)}\n")
    if segments:
        with open(os.path.join(out, "segments"), "w", encoding="utf-8") as f:
            for utt, (rec, s, e) in segments.items():
                f.write(f"{utt} {rec} {s} {e}\n")
    if spk:
        with open(os.path.join(out, "utt2spk"), "w", encoding="utf-8") as f:
            for utt, s in spk.items():
                f.write(f"{utt} {s}\n")
    print(f"{out}: {len(texts)} utterances, {len(wavs)} recordings, "
          f"{len(segments or {})} segments")


def audio_index(root):
    idx = {}
    for d, _, files in os.walk(root):
        for name in files:
            if name.lower().endswith((".wav", ".flac", ".mp3")):
                idx.setdefault(os.path.splitext(name)[0], os.path.join(d, name))
    return idx


def fleurs(src, out):
    tsv = next((os.path.join(src, f) for f in os.listdir(src) if f.endswith(".tsv")), None)
    if not tsv:
        raise SystemExit(f"no .tsv in {src}")
    audio = audio_index(src)
    texts, wavs = [], {}
    with open(tsv, encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            # id, file_name, raw_transcription, transcription, chars, num_samples, gender
            name = next((c for c in cols if c.endswith(".wav")), None)
            if not name or len(cols) < 4:
                continue
            rec = os.path.splitext(name)[0]
            if rec not in audio:
                continue
            raw = cols[cols.index(name) + 1].strip()
            if raw:
                texts.append((rec, " ".join(raw.split())))
                wavs[rec] = audio[rec]
    write_folder(out, texts, wavs)


def find_file(root, name):
    hits = []
    for d, _, files in os.walk(root):
        if name in files:
            hits.append(os.path.join(d, name))
    return sorted(hits, key=len)


def mucs(src, out):
    text_files = find_file(src, "text")
    print("MUCS text files:", text_files[:5])
    if not text_files:
        for d, dirs, files in os.walk(src):
            print(" ", d, dirs[:5], files[:8])
        raise SystemExit("MUCS: no Kaldi 'text' file found")
    tdir = os.path.dirname(text_files[0])
    texts = []
    with open(text_files[0], encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                texts.append((parts[0], parts[1]))
    segments = {}
    seg_path = os.path.join(tdir, "segments")
    if os.path.isfile(seg_path):
        with open(seg_path, encoding="utf-8") as f:
            for line in f:
                p = line.split()
                if len(p) == 4:
                    segments[p[0]] = (p[1], p[2], p[3])
    spk = {}
    u2s = os.path.join(tdir, "utt2spk")
    if os.path.isfile(u2s):
        with open(u2s, encoding="utf-8") as f:
            for line in f:
                p = line.split()
                if len(p) == 2:
                    spk[p[0]] = p[1]
    audio = audio_index(src)
    recs = {segments[u][0] if u in segments else u for u, _ in texts}
    wavs = {r: audio[r] for r in recs if r in audio}
    missing = len(recs) - len(wavs)
    print(f"MUCS: {len(recs)} recordings referenced, {missing} without audio; "
          f"sample text: {texts[:2]}")
    texts = [(u, t) for u, t in texts if (segments[u][0] if u in segments else u) in wavs]
    write_folder(out, texts, wavs, segments or None, spk or None)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("fleurs", "mucs"):
        raise SystemExit(__doc__)
    {"fleurs": fleurs, "mucs": mucs}[sys.argv[1]](sys.argv[2], sys.argv[3])
