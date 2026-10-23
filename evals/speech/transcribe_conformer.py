#!/usr/bin/env python3
"""Desktop reference transcription with AI4Bharat IndicConformer (CTC or RNNT).

Same inputs and outputs as transcribe_hf.py: HYPS/<id>.txt per clip and
HYPS/_timing.json. The model is gated: HF_TOKEN must belong to an account that
accepted its terms. Model code is loaded with trust_remote_code from the
pinned revision below, so a change upstream cannot change what runs here.

  python3 evals/speech/transcribe_conformer.py --golden G --audio A --hyps H \
      --model ai4bharat/indic-conformer-600m-multilingual --decoder ctc --limit 300
"""
import argparse
import json
import os
import sys
import time
import wave

import numpy as np


def read_wav(path):
    with wave.open(path, "rb") as w:
        data = w.readframes(w.getnframes())
    return np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--hyps", required=True)
    ap.add_argument("--model", default="ai4bharat/indic-conformer-600m-multilingual")
    ap.add_argument("--revision", default=None, help="pin a commit of the model repo")
    ap.add_argument("--decoder", choices=("ctc", "rnnt"), default="ctc")
    ap.add_argument("--langs", default="hi")
    ap.add_argument("--limit", type=int, default=0, help="max clips per source (0 = all)")
    ap.add_argument("--max-minutes", type=float, default=0)
    a = ap.parse_args(argv)

    import torch
    from transformers import AutoModel

    torch.set_num_threads(os.cpu_count() or 4)
    model = AutoModel.from_pretrained(a.model, trust_remote_code=True, revision=a.revision,
                                      token=os.environ.get("HF_TOKEN"))
    langs = [x for x in a.langs.split(",") if x]
    clips = []
    with open(os.path.join(a.golden, "manifest.jsonl"), encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c["lang"] in langs:
                clips.append(c)
    if a.limit:
        by_src = {}
        for c in clips:
            by_src.setdefault(c.get("source") or c["lang"], []).append(c)
        keep = {c["id"] for cs in by_src.values() for c in sorted(cs, key=lambda c: c["id"])[:a.limit]}
        clips = [c for c in clips if c["id"] in keep]
    os.makedirs(a.hyps, exist_ok=True)

    deadline = time.time() + a.max_minutes * 60 if a.max_minutes else None
    timing = {}
    for lang in langs:
        todo = sorted((c for c in clips if c["lang"] == lang), key=lambda c: c["id"])
        audio_s = compute_s = 0.0
        done = 0
        for c in todo:
            if deadline and time.time() > deadline:
                print(f"{lang}: time budget reached after {done}/{len(todo)} clips", flush=True)
                break
            audio = read_wav(os.path.join(a.audio, c["id"] + ".wav"))
            wav = torch.from_numpy(audio).unsqueeze(0)
            t0 = time.time()
            with torch.inference_mode():
                text = model(wav, lang, a.decoder)
            compute_s += time.time() - t0
            audio_s += len(audio) / 16000
            if isinstance(text, (list, tuple)):
                text = " ".join(map(str, text))
            with open(os.path.join(a.hyps, c["id"] + ".txt"), "w", encoding="utf-8") as f:
                f.write(str(text).strip() + "\n")
            done += 1
            if done % 25 == 0:
                print(f"{a.model} {lang}: {done}/{len(todo)} RTF {compute_s / max(audio_s, 1e-9):.3f}",
                      flush=True)
        timing[lang] = {"clips": done, "planned": len(todo), "audio_s": round(audio_s, 1),
                        "compute_s": round(compute_s, 1),
                        "rtf": round(compute_s / audio_s, 3) if audio_s else None}
    with open(os.path.join(a.hyps, "_timing.json"), "w") as f:
        json.dump({"model": a.model, "decoder": a.decoder, "cpu_count": os.cpu_count(),
                   "timing": timing}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
