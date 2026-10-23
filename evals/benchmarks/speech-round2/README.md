# Speech round 2: Hinglish models compared (desktop, open public data)

Date: 2026-10-23. Same setup as round 1 (`../speech-round1/README.md`):
GitHub Actions, 4-core CPU, transformers float32, greedy decoding with
retries for looping outputs. Same open sources (FLEURS Hindi and English,
MUCS Hinglish); the gated sets (IndicVoices, Lahaja, Svarah) and
IndicConformer were **not available**, because Hugging Face had not yet granted the account
access. New this round: Oriserve **Apex** (whisper-large-v3-turbo based,
0.8B) and **WERph**, a diagnostic score that forgives the script and spelling
of English loanwords ("फाइल" = "file").

## Hindi and Hinglish: same 240 clips for every model
120 FLEURS Hindi + 120 MUCS Hinglish. Words wrong (WER), with WERph in
brackets. Target `speech.wer_hi` ≤ 35%.

| Model | Size | FLEURS Hindi | MUCS Hinglish | All 240 | Desktop speed (Hindi) |
|---|---|---|---|---|---|
| Whisper small, stock | 0.24B | 50.8% (41.3%) | 82.5% (74.6%) | 62.0% ✗ | 2.16 (with loop retries) |
| Whisper small Hindi (vasista22) | 0.24B | **11.7%** (9.6%) | 78.1% (70.1%) | 35.1% ≈ | **0.71** |
| Hindi2Hinglish **Apex** (Oriserve) | 0.8B | 20.7% (14.3%) | **39.2%** (35.0%) | **27.2%** ✓ | 1.77 |
| Hindi2Hinglish Prime (Oriserve) | 1.5B | 19.6% (13.3%) | 41.2% (36.8%) | 27.2% ✓ | 1.71 |

English, Whisper small, 200 FLEURS clips: **7.3%** (target ≤ 15%), desktop
speed 0.34.

## What we learned
1. **Apex replaces Prime.** Same accuracy at half the parameters, so about
   half the size in the app (roughly 0.5 GB quantised vs 1 GB). Its
   "up to 8× faster" claim did not show on CPU (1.77 vs 1.71); the encoder
   dominates CPU time, and turbo only shrinks the decoder.
2. **The Hindi fine-tune's Hinglish weakness is real, not a scoring artefact.**
   With loanword script forgiven (WERph) it still gets 70% wrong on MUCS. It
   is excellent on plain Hindi (under 12%).
3. **Script accounts for about 4–6 points** of every model's Hindi WER
   (official minus WERph). Worth fixing in search (match romanised and
   Devanagari forms), not only in scoring.
4. **Stock Whisper small loops a lot on Hindi** (119 of 400 clips needed
   retries), which also makes it the slowest. It should only ever handle
   English.

## Proposed speech setup (for founders' decision)
- English: Whisper small.
- Hindi and Hinglish: **Apex** as the main model; the small Hindi fine-tune
  as the fast fallback on phones too slow for Apex.
- Everything depends on phone speed: Apex at 1.8 s per second of audio on
  a desktop CPU will be slower on a phone, so a 60 s reel would take minutes
  on CPU. Next: measure quantised whisper.cpp (q5/q8) on a real mid-range
  phone, including its NPU/GPU path, and decide whether reading happens
  in the background (on charge) with a quick first pass by the small model.

## Not yet done
- Gated natural-speech sets and IndicConformer (needs Hugging Face access
  to be granted; then re-run this workflow by editing
  `evals/speech/round2/TRIGGER`).
- Music and street-noise augmentation (MUSAN not downloaded yet).
- Phone speed.
