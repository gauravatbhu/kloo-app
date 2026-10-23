#!/usr/bin/env python3
"""Combine per-model speech summaries into one Markdown report.

  python3 evals/speech/round_report.py RESULTS_DIR OUT.md
RESULTS_DIR/<model-slug>/summary.json and timing.json (from transcribe_hf.py).
"""
import json
import os
import sys

TARGET = {"en": 0.15, "hi": 0.35}
ROWS = [
    ("Hindi + Hinglish (official `wer_hi`)", "lang=hi"),
    ("Hindi only", "variety=hindi"),
    ("Hinglish only", "variety=hinglish"),
    ("FLEURS Hindi (read)", "lang=hi/source=fleurs_hi"),
    ("MUCS Hinglish (lectures)", "lang=hi/source=mucs"),
    ("Hindi, clean audio", "lang=hi/condition=clean"),
    ("Hindi, fast + re-encoded", "lang=hi/condition=fast"),
    ("English (official `wer_en`)", "lang=en"),
    ("English, fast + re-encoded", "lang=en/condition=fast"),
]


def pct(v):
    return "—" if v is None else f"{100 * v:.1f}%"


def main(results_dir, out):
    models = []
    for slug in sorted(os.listdir(results_dir)):
        p = os.path.join(results_dir, slug, "summary.json")
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
        t = {}
        tp = os.path.join(results_dir, slug, "timing.json")
        if os.path.isfile(tp):
            with open(tp) as f:
                t = json.load(f)
        models.append((s["meta"]["model"], s, t))
    lines = ["| | " + " | ".join(f"`{m}`" for m, _, _ in models) + " |",
             "|---|" + "---|" * len(models)]
    for label, key in ROWS:
        cells = []
        for _, s, _ in models:
            g = s["groups"].get(key)
            cells.append("n/a" if not g else f"{pct(g['wer'])} ({g['clips']})")
        if any(c != "n/a" for c in cells):
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
    strict = []
    for _, s, _ in models:
        g = s["groups"].get("lang=hi")
        strict.append("n/a" if not g else f"{pct(g['wer_strict'])} / CER {pct(g['cer_strict'])}")
    lines.append("| Hindi, script-preserving WER / CER | " + " | ".join(strict) + " |")
    urdu = [str(s["groups"].get("lang=hi", {}).get("wrong_script_clips", "n/a")) for _, s, _ in models]
    lines.append("| Hindi clips answered in Urdu script | " + " | ".join(urdu) + " |")
    rtf = []
    for _, _, t in models:
        tm = t.get("timing", {})
        rtf.append(", ".join(f"{k} {v['rtf']}" for k, v in tm.items() if v.get("rtf")) or "n/a")
    lines.append("| Desktop CPU real-time factor | " + " | ".join(rtf) + " |")
    verdict = []
    for m, s, _ in models:
        parts = []
        for lang in ("hi", "en"):
            g = s["groups"].get(f"lang={lang}")
            if g and g["wer"] is not None:
                ok = g["wer"] <= TARGET[lang]
                parts.append(f"{lang} {'meets' if ok else 'misses'} {int(TARGET[lang] * 100)}%")
        verdict.append(f"- `{m}`: " + ("; ".join(parts) or "no scores"))
    text = "\n".join(lines) + "\n\nTargets (evals/thresholds.json): " + \
        "\n".join([""] + verdict) + "\n\nCells: WER (clips). Lower is better.\n"
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
