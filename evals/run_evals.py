#!/usr/bin/env python3
"""Kloo evaluation runner.

Reads a JSONL file of per-item results produced by the apps' eval harnesses,
computes each suite's metric, checks it against evals/thresholds.json (and the
previous summary, if given), writes a markdown report plus a JSON summary, and
exits 1 if anything fails.

Result line formats (one JSON object per line, "suite" decides the shape):
  speech   {"suite":"speech","id":"...","lang":"en|hi","reference":"...","hypothesis":"..."}
  ocr      {"suite":"ocr","id":"...","lang":"en|hi","reference":"...","hypothesis":"..."}
  filing   {"suite":"filing","id":"...","expected":"Recipe","predicted":"Recipe"}
  search   {"suite":"search","id":"...","relevant_ids":["s1"],"ranked_ids":["s9","s1",...]}
  answers  {"suite":"answers","id":"...","grounded":true,"citations_valid":true}
  speed    {"suite":"speed","metric":"reel_read_seconds_p50","value":24.0}
  privacy  {"suite":"privacy","passed":true}   (from evals/privacy/check_egress.py --json)

Usage:
  python3 evals/run_evals.py --results RESULTS.jsonl [--previous PREV_SUMMARY.json]
                             [--thresholds evals/thresholds.json] [--out-dir evals/reports]
"""
import argparse
import datetime as dt
import json
import os
import sys
import unicodedata


def norm_words(text):
    text = unicodedata.normalize("NFC", text or "").lower()
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        # keep letters, digits, combining marks (Devanagari vowel signs) and spaces
        out.append(ch if cat[0] in ("L", "N", "M") or ch.isspace() else " ")
    return "".join(out).split()


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def error_rate(pairs, unit):
    errors = total = 0
    for ref, hyp in pairs:
        if unit == "word":
            r, h = norm_words(ref), norm_words(hyp)
        else:
            r = list(" ".join(norm_words(ref)))
            h = list(" ".join(norm_words(hyp)))
        errors += edit_distance(r, h)
        total += max(len(r), 1)
    return errors / total if total else None


def compute(rows):
    by_suite = {}
    for row in rows:
        by_suite.setdefault(row.get("suite"), []).append(row)
    m = {}
    for lang in ("en", "hi"):
        sp = [(r["reference"], r["hypothesis"]) for r in by_suite.get("speech", []) if r.get("lang") == lang]
        if sp:
            m[f"speech.wer_{lang}"] = error_rate(sp, "word")
        oc = [(r["reference"], r["hypothesis"]) for r in by_suite.get("ocr", []) if r.get("lang") == lang]
        if oc:
            m[f"ocr.char_accuracy_{lang}"] = 1 - error_rate(oc, "char")
    fl = by_suite.get("filing", [])
    if fl:
        m["filing.accuracy"] = sum(r["expected"] == r["predicted"] for r in fl) / len(fl)
    se = by_suite.get("search", [])
    if se:
        hits = sum(bool(set(r["relevant_ids"]) & set(r["ranked_ids"][:5])) for r in se)
        m["search.recall_at_5"] = hits / len(se)
    an = by_suite.get("answers", [])
    if an:
        m["answers.grounded_rate"] = sum(bool(r["grounded"]) and bool(r.get("citations_valid", True)) for r in an) / len(an)
    for r in by_suite.get("speed", []):
        m[f"speed.{r['metric']}"] = float(r["value"])
    pv = by_suite.get("privacy", [])
    if pv:
        m["privacy.pass_rate"] = sum(bool(r["passed"]) for r in pv) / len(pv)
    counts = {k: len(v) for k, v in by_suite.items() if k}
    return m, counts


def check(metrics, thresholds, previous):
    rows, failed = [], False
    for name in sorted(set(metrics) | set(thresholds)):
        rule = thresholds.get(name, {})
        val = metrics.get(name)
        prev = previous.get(name) if previous else None
        status = "ok"
        if val is None:
            status = "missing" if rule.get("required") else "not run"
            failed = failed or bool(rule.get("required"))
        else:
            if "min" in rule and val < rule["min"]:
                status = "below target"
            if "max" in rule and val > rule["max"]:
                status = "above limit"
            if prev is not None and "max_drop" in rule:
                lower_is_better = "max" in rule and "min" not in rule
                drop = (val - prev) if lower_is_better else (prev - val)
                if drop > rule["max_drop"]:
                    status = "regressed"
            if status != "ok" and rule.get("blocking", True):
                failed = True
        rows.append((name, val, prev, rule, status))
    return rows, failed


def fmt(v):
    if v is None:
        return "—"
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def rule_text(rule):
    parts = []
    if "min" in rule:
        parts.append(f"≥ {rule['min']}")
    if "max" in rule:
        parts.append(f"≤ {rule['max']}")
    if "max_drop" in rule:
        parts.append(f"drop ≤ {rule['max_drop']}")
    return ", ".join(parts) or "tracked"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--previous")
    ap.add_argument("--thresholds", default=os.path.join(here, "thresholds.json"))
    ap.add_argument("--out-dir", default=os.path.join(here, "reports"))
    a = ap.parse_args()

    with open(a.results, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    with open(a.thresholds, encoding="utf-8") as f:
        thresholds = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    previous = None
    if a.previous:
        with open(a.previous, encoding="utf-8") as f:
            previous = json.load(f).get("metrics")

    metrics, counts = compute(rows)
    table, failed = check(metrics, thresholds, previous)

    os.makedirs(a.out_dir, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    verdict = "RED: do not ship; fix before new feature work" if failed else "GREEN: all suites within thresholds"
    lines = [f"# Eval report {stamp}", "", f"**{verdict}**", "",
             "| Metric | Value | Previous | Threshold | Status |", "|---|---|---|---|---|"]
    for name, val, prev, rule, status in table:
        lines.append(f"| {name} | {fmt(val)} | {fmt(prev)} | {rule_text(rule)} | {status} |")
    lines += ["", "Items per suite: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))]
    report = "\n".join(lines) + "\n"
    with open(os.path.join(a.out_dir, f"{stamp}.md"), "w", encoding="utf-8") as f:
        f.write(report)
    with open(os.path.join(a.out_dir, f"{stamp}.json"), "w", encoding="utf-8") as f:
        json.dump({"timestamp": stamp, "failed": failed, "metrics": metrics, "counts": counts}, f, indent=2)
    print(report)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
