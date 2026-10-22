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
import zlib

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
    ap.add_argument("--limit", type=int, default=0,
                    help="max clips per source, in manifest order (0 = all); a seeded spread")
    ap.add_argument("--greedy", action="store_true", help="disable temperature fallback")
    ap.add_argument("--max-minutes", type=float, default=0,
                    help="stop transcribing after this long (0 = no limit); clips run in a seeded "
                         "interleaved order, so a partial run still covers every source")
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args(argv)

    import torch
    from transformers import AutoProcessor, WhisperForConditionalGeneration

    torch.set_num_threads(os.cpu_count() or 4)
    processor = AutoProcessor.from_pretrained(a.model)
    model = WhisperForConditionalGeneration.from_pretrained(a.model, torch_dtype=torch.float32).eval()
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
        keep = set()
        for src, cs in by_src.items():
            cs = sorted(cs, key=lambda c: c["id"])  # ids are hashes: a stable pseudo-random spread
            keep.update(c["id"] for c in cs[:a.limit])
        clips = [c for c in clips if c["id"] in keep]
    os.makedirs(a.hyps, exist_ok=True)
    window = 30 * 16000

    # Greedy decode, then retry only outputs that look like a repetition loop at
    # rising temperature. This mirrors openai-whisper / whisper.cpp fallback
    # (text compression ratio > 2.4), without paying for it on every clip.
    temps = () if a.greedy else (0.2, 0.4, 0.6, 0.8, 1.0)

    def looping(text):
        b = text.encode("utf-8")
        return len(b) > 40 and len(b) / max(len(zlib.compress(b)), 1) > 2.4

    def fix_generation_config():
        from transformers import GenerationConfig
        cfg = model.config
        base = {384: "tiny", 512: "base", 768: "small", 1024: "medium"}.get(cfg.d_model)
        if base is None:
            base = "large-v3" if cfg.num_mel_bins == 128 else "large-v2"
        print(f"generation config outdated; using openai/whisper-{base}'s", file=sys.stderr)
        model.generation_config = GenerationConfig.from_pretrained(f"openai/whisper-{base}")

    def generate(features, lang, **kw):
        """Pin language + transcribe. Older fine-tunes need a borrowed generation config."""
        with torch.inference_mode():
            try:
                return model.generate(features, language=lang, task="transcribe",
                                      max_new_tokens=440, **kw)
            except ValueError as e:
                if "generation config is outdated" not in str(e):
                    raise
                fix_generation_config()
                return model.generate(features, language=lang, task="transcribe",
                                      max_new_tokens=440, **kw)

    retries = {"looped": 0, "fixed": 0}

    def decode(features, lang):
        texts = processor.batch_decode(generate(features, lang), skip_special_tokens=True)
        for k, t in enumerate(texts):
            if not temps or not looping(t):
                continue
            retries["looped"] += 1
            for temp in temps:
                torch.manual_seed(k)
                t2 = processor.batch_decode(generate(features[k:k + 1], lang, do_sample=True,
                                                     temperature=temp),
                                            skip_special_tokens=True)[0]
                if not looping(t2):
                    texts[k] = t2
                    retries["fixed"] += 1
                    break
        return texts

    def run(batch, lang):
        # Split anything longer than 30 s into consecutive 30 s windows (rare: pseudo-reels).
        pieces, owner = [], []
        for k, c in enumerate(batch):
            audio = read_wav(os.path.join(a.audio, c["id"] + ".wav"))
            for start in range(0, max(len(audio), 1), window):
                pieces.append(audio[start:start + window])
                owner.append(k)
        feats = processor.feature_extractor(pieces, sampling_rate=16000, return_tensors="pt").input_features
        texts = decode(feats, lang)
        out = [""] * len(batch)
        for k, t in zip(owner, texts):
            out[k] = (out[k] + " " + t.strip()).strip()
        return out, sum(len(p) for p in pieces) / 16000

    deadline = time.time() + a.max_minutes * 60 if a.max_minutes else None
    budget_share = {lang: sum(1 for c in clips if c["lang"] == lang) for lang in langs}
    total = sum(budget_share.values()) or 1
    timing = {}
    for lang in langs:
        # ids are hashes, so sorting by id interleaves sources and conditions
        todo = sorted((c for c in clips if c["lang"] == lang), key=lambda c: c["id"])
        lang_deadline = None
        if deadline:
            lang_deadline = time.time() + (deadline - time.time()) * budget_share[lang] / total
            total -= budget_share[lang]
        audio_s = compute_s = 0.0
        done = 0
        for i in range(0, len(todo), a.batch):
            if lang_deadline and time.time() > lang_deadline:
                print(f"{lang}: time budget reached after {done}/{len(todo)} clips", flush=True)
                break
            batch = todo[i:i + a.batch]
            done += len(batch)
            t0 = time.time()
            out, secs = run(batch, {"hi": "hindi", "en": "english"}[lang])
            compute_s += time.time() - t0
            audio_s += secs
            for c, o in zip(batch, out):
                with open(os.path.join(a.hyps, c["id"] + ".txt"), "w", encoding="utf-8") as f:
                    f.write(o + "\n")
            print(f"{a.model} {lang}: {min(i + a.batch, len(todo))}/{len(todo)} "
                  f"RTF {compute_s / max(audio_s, 1e-9):.3f}", flush=True)
        timing[lang] = {"clips": done, "planned": len(todo), "audio_s": round(audio_s, 1),
                        "compute_s": round(compute_s, 1),
                        "rtf": round(compute_s / audio_s, 3) if audio_s else None}
    with open(os.path.join(a.hyps, "_timing.json"), "w") as f:
        json.dump({"model": a.model, "cpu_count": os.cpu_count(), "timing": timing,
                   "loop_retries": retries, "decoding": "greedy" if a.greedy else "greedy+loop-fallback"}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
