# Speech round 1: desktop accuracy on open public data

Date: 2026-10-23. Runs: GitHub Actions, 4-core CPU, `transformers` 4.46.3,
float32. Set: `speech-public-v1` built from the **ungated** sources only (FLEURS
Hindi and English test, MUCS 2021 Hindi-English test), with half the clips
also sped up 1.15× and AAC re-encoded. No music or noise yet (MUSAN not
downloaded in CI). Normaliser `kloo-speech-norm-1`. Decoding: greedy, with
temperature retries only for outputs that loop (openai-whisper's
compression-ratio rule). Per-model summaries and timings are in the folders
next to this file (`whisper-small-greedy` is the earlier run without retries).

**This measures accuracy only.** Speed below is a desktop CPU, not a phone.

## Hindi and Hinglish: same 445 clips for every model

Clips that every model transcribed (250 FLEURS Hindi, 195 MUCS Hinglish).
Words wrong (WER). Lower is better. Target: `speech.wer_hi` ≤ 35%.

| Model | Size | FLEURS Hindi (read news-style) | MUCS Hinglish (software tutorials) | All 445 | Desktop speed (s of compute per s of Hindi audio) |
|---|---|---|---|---|---|
| Whisper small, stock | 244M | 49.4% | 77.9% | **57.9%** ✗ | 0.69 greedy |
| Whisper small Hindi (vasista22) | 244M | **12.2%** | 75.2% | **30.9%** ✓ | 0.71 |
| Hindi2Hinglish Prime (Oriserve) | ~1.5B (large-v3 base) | 19.7% | **38.9%** | **25.4%** ✓ | 1.29 |
| Whisper large-v3-turbo (reference ceiling) | 809M | 24.5% | 46.4% | 31.0% ✓ | 1.86 |

Sped-up and re-encoded copies score within ±2 points of clean ones for every
model, so speed and compression are not the problem; vocabulary and script are.

## English

| Model | FLEURS English | Target ≤ 15% |
|---|---|---|
| Whisper small, stock (457 clips) | 9.4% (clean 8.8%, fast 10.4%) | ✓ |
| Whisper large-v3-turbo (250 clips) | 5.2% | ✓ |

## What we learned
1. **Stock Whisper small cannot do Hindi.** 58% WER, and it gets stuck repeating
   a word ("तो तो तो…") on 14% of Hindi and 48% of Hinglish clips when decoded
   greedily. Retries fix the loops but the words are still wrong.
2. **A small Hindi fine-tune closes most of the gap at no speed cost.**
   vasista22 is the same size and speed as stock small and gets 12% on
   FLEURS. Caveat: it was trained on FLEURS train/dev (different sentences
   and speakers, same style), so its FLEURS number is flattering.
3. **Hinglish needs a different model.** The Hinglish-trained model (writes
   Hindi in Roman letters, English words in English) is the only one under
   40% on MUCS. It is about 6× bigger and about 2× slower than small on
   desktop.
4. **Part of the Hinglish gap looked like our scorer**, because English
   loanwords can be written in Devanagari. Round 2 added a diagnostic
   (WERph) and showed this explains only 4–6 points.
5. **English is fine with Whisper small.**

## Caveats
- Desktop float32 transformers; phone engines (whisper.cpp, WhisperKit)
  quantise and will differ slightly in accuracy and a lot in speed.
- Stock small's run hit its time budget: it covers all FLEURS Hindi but
  only 195 of 457 MUCS clips. The large models were capped at 250 clips per
  source. The 445-clip table compares like with like.
- Hindi2Hinglish Prime was trained on ~550 h of proprietary data; its card
  does not name the sources. Licence Apache-2.0.
- vasista22 licence Apache-2.0; training data includes Shrutilipi (All India
  Radio) and FLEURS. Check data licences before shipping.
