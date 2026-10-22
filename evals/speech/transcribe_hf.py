#!/usr/bin/env python3
"""Desktop reference transcription with a Hugging Face Whisper-family model.

Writes HYPS/<id>.txt for every clip in the manifest (optionally one language
only) plus HYPS/_timing.json (seconds of audio, seconds of compute, RTF).
This measures ACCURACY on a desktop CPU. Phone speed is measured separately
on real devices (evals/devices.md); desktop RTF is only a rough guide.

  python3 evals/speech/transcribe_hf.py --golden G --audio A --hyps H \
      --model openai/whisper-small --langs hi,en
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
    ap.add_argument("--model", required=True)
    ap.add_argument("--langs", default="hi,en")
    ap.add_argument("--limit", type=int, default=0, help="max clips per language (0 = all)")
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args(argv)

    import torch
    from transformers import pipeline

    torch.set_num_threads(os.cpu_count() or 4)
    asr = pipeline("automatic-speech-recognition", model=a.model, device="cpu",
                   torch_dtype=torch.float32)
    langs = [x for x in a.langs.split(",") if x]
    clips = []
    with open(os.path.join(a.golden, "manifest.jsonl"), encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c["lang"] in langs:
                clips.append(c)
    if a.limit:
        per = {}
        clips = [c for c in clips if per.setdefault(c["lang"], []).append(1) or len(per[c["lang"]]) <= a.limit]
    os.makedirs(a.hyps, exist_ok=True)

    def run(batch, lang):
        audios = [{"raw": read_wav(os.path.join(a.audio, c["id"] + ".wav")), "sampling_rate": 16000}
                  for c in batch]
        kwargs = {"task": "transcribe", "language": lang}
        try:
            return asr(audios, batch_size=len(audios), chunk_length_s=30,
                       generate_kwargs=kwargs), sum(len(x["raw"]) for x in audios) / 16000
        except Exception as e:  # older fine-tunes lack language tokens in generation_config
            print(f"language kwarg failed ({e}); retrying with forced_decoder_ids", file=sys.stderr)
            ids = asr.tokenizer.get_decoder_prompt_ids(language=lang, task="transcribe")
            asr.model.generation_config.forced_decoder_ids = ids
            return asr(audios, batch_size=len(audios), chunk_length_s=30), \
                sum(len(x["raw"]) for x in audios) / 16000

    timing = {}
    for lang in langs:
        todo = [c for c in clips if c["lang"] == lang]
        audio_s = compute_s = 0.0
        for i in range(0, len(todo), a.batch):
            batch = todo[i:i + a.batch]
            t0 = time.time()
            out, secs = run(batch, {"hi": "hindi", "en": "english"}[lang])
            compute_s += time.time() - t0
            audio_s += secs
            for c, o in zip(batch, out):
                with open(os.path.join(a.hyps, c["id"] + ".txt"), "w", encoding="utf-8") as f:
                    f.write(o["text"].strip() + "\n")
            print(f"{a.model} {lang}: {min(i + a.batch, len(todo))}/{len(todo)} "
                  f"RTF {compute_s / max(audio_s, 1e-9):.3f}", flush=True)
        timing[lang] = {"clips": len(todo), "audio_s": round(audio_s, 1),
                        "compute_s": round(compute_s, 1),
                        "rtf": round(compute_s / audio_s, 3) if audio_s else None}
    with open(os.path.join(a.hyps, "_timing.json"), "w") as f:
        json.dump({"model": a.model, "cpu_count": os.cpu_count(), "timing": timing}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
