# Evaluations

Evaluation runs from day 1 so the product and the agents don't drift.
Owner: `qa-eval`. Thresholds: `thresholds.json`. Reports: `reports/`.

## Suites
| Suite | Metric | Golden set (to build) | Target |
|---|---|---|---|
| Privacy promise | Pass rate of egress test (allowlist + canaries) | Automated UI test run with a planted test library | 100%, blocks release |
| Speech | Word error rate, per language | Public datasets (IndicVoices, Lahaja, MUCS, Svarah, ...) with reel-style augmentation; see `golden/speech/README.md` | EN ≤ 15%; HI ≤ 35%, baseline in week 2 |
| On-screen text | Character accuracy | 100 frames with captions, EN + HI | EN ≥ 95% |
| Filing | Topic accuracy | 300 labelled saves | ≥ 85% |
| Search | Recall@5 | 200 real questions, incl. Hinglish and vague memories | ≥ 90% |
| Answers | Grounded rate (every claim backed by a cited save) | 100 questions; AI judge + weekly human spot-check | 100% |
| Speed and size | Reel read time, Ask time, app size | Reference phones in `devices.md` | ≤ 30 s, ≤ 1 s, ≤ 2 GB (models bundled, decision 0003) |
| Product (beta) | Saves reused/user/week, week-4 retention, download-habit rate | Beta analytics (opt-in, no content) | 3+, 30%, tracked |

## Rules
- Golden sets are never used for training or prompt tuning examples.
- Add every bug or hard case found in the beta to a golden set.
- Include prompt-injection cases: reels whose text tries to instruct the app.
- Report per device tier (1: built-in AI, 2: bundled Gemma, 3: cards only) and per language.
- Golden-set media must be content we have rights to use: public datasets whose licences allow commercial use, or our own material. Never scraped, never from social platforms.

## Run
```
python3 evals/privacy/check_egress.py evals/privacy/sample_capture.jsonl --json > /tmp/privacy.json
python3 evals/run_evals.py --results evals/golden/sample_results.jsonl
```
Speech results come from `evals/speech/run_speech_eval.py`, which scores any
engine's transcripts against `evals/golden/speech/` (spec, Hinglish rules and
consent form in its README). Tests: `python3 -m unittest discover -s evals/speech`.

`sample_results.jsonl` is synthetic demo data that shows the format; replace it
with real harness output from the apps.
