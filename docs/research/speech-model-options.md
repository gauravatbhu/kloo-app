# On-device speech options for Hindi, Hinglish and Indian English

Author: ml-engineer. Date: 2026-10-22. Status: desk research. **Nothing here was
measured by us yet**: no weights or datasets could be downloaded in this
environment. The golden set is now built from public datasets
(evals/golden/speech/README.md), not recorded by volunteers. Every WER below is someone else's number on
someone else's test set. Speed figures marked *estimate* are reasoning, not
measurements.

## What Kloo needs
- A 60 s reel read (transcribe + OCR + filing + embedding) in ≤ 30 s p50 on a
  ₹15–25k Android phone (evals/README.md). Transcription should take about half
  of that, so a real-time factor (RTF) around **0.3 or better** on CPU.
- Size: **not a constraint** (founders, 2026-10-22). Models ship inside the
  app (docs/decisions/0003), within store limits: Google Play install-time
  asset packs up to 1.5 GB each and 4 GB in total; App Store 4 GB
  uncompressed. So we can bundle two speech models (English + Hindi) and use
  higher-precision quantisation (q8 instead of q5) where it helps accuracy.
- English, Hindi and Hinglish (code-mixed, often typed in Roman script by
  users) all first-class; transcripts feed search and filing, so getting the
  words right matters more than which script they are in.
- Weights and runtime licensed for commercial use; training data provenance
  that would not embarrass a privacy-first product.

## Read published Hindi WERs with care
The same model on the same test set gets very different Hindi WERs depending
on the text normaliser. Whisper's own `BasicTextNormalizer` strips Devanagari
vowel signs, which hides errors:

| Whisper small, zero-shot, FLEURS Hindi test | WER | Normaliser |
|---|---|---|
| collabora model card | 67.4% | Whisper normaliser |
| collabora model card | 89.7% | Indic normaliser |
| Abhigyan1805/hindi-voice-asr (418 utts) | 79.2% | custom, keeps vowel signs |
| Vocova benchmark (50 utts) | 42.4% | Whisper `BasicTextNormalizer` |

FLEURS and Kathbath are clean read speech. Benchmarks with spontaneous or noisy
speech (Gramvaani, Vaani, Vividh-ASR tiers C/D) run 10–15 points worse, and
reels add music. Our golden set uses its own lenient, script-agnostic
normaliser (evals/golden/speech/README.md), so **our numbers will not line up
with any figure below**. Use these figures to rank models, not to predict our
numbers.

## Options

Size = quantised file the phone would download. Speed = RTF on a mid-range
Android CPU (Snapdragon 7-series / Dimensity 7000-class, 4 threads) unless
stated; RTF 0.5 means a 60 s reel takes 30 s.

### Whisper family (whisper.cpp on Android, WhisperKit on iOS)
Runtimes: whisper.cpp (MIT), WhisperKit (MIT). Weights: OpenAI Whisper (MIT).

| Model | Params | Quantised size | Published Hindi WER (zero-shot) | Speed, mid-range Android (*estimate*) |
|---|---|---|---|---|
| tiny | 39M | 32 MB q5_1, 44 MB q8_0; WhisperKit 66 MB | No reliable figure found; expect unusable (>70%) | RTF ~0.1 |
| base | 74M | 60 MB q5_1, 82 MB q8_0; WhisperKit 145 MB | No reliable figure found; expect >60% | RTF ~0.2 |
| **small** | 244M | **190 MB q5_1**, 264 MB q8_0; WhisperKit 483 MB | 42.4% FLEURS (Vocova); 67–79% FLEURS with stricter normalisers (collabora, Abhigyan1805) | RTF ~0.5–1.0 on CPU. On the Snapdragon 7 Gen 4 NPU via Qualcomm AI Hub (not whisper.cpp): 95 ms encoder per 30 s window, 10 ms per output token |
| medium | 769M | 539 MB q5_0, 823 MB q8_0 | 42.6% Kathbath (arXiv 2412.19785); 43.0% FLEURS (Abhigyan1805) | RTF ~2–3: too slow |
| large-v3-turbo | 809M (4-layer decoder) | 574 MB q5_0, 874 MB q8_0; WhisperKit compressed 547/626 MB | 22.3% FLEURS (Vocova, 50 utts) | RTF ~2–4; the encoder is as big as large-v3. Only realistic on tier-1 phones with NPU/ANE |
| large-v3 (reference only) | 1.55B | 1.08 GB q5_0 | 15.7% FLEURS (Vocova, 50 utts); 24.1% FLEURS (asr-norm-check, 50 clips) | Not a phone model |

Hindi-specific concern: Whisper's byte-level BPE tokeniser spends several
tokens per Devanagari word (the motivation for arXiv 2412.19785), so Hindi
decoding is several times slower per second of audio than English. Hindi RTF
will be worse than any English benchmark suggests.

Whisper fine-tuned for Hindi (same runtime, same size, drop-in GGML/CoreML
conversion):

| Model | Base | Licence | Published Hindi WER | Notes |
|---|---|---|---|---|
| vasista22/whisper-hindi-small | small | Apache-2.0 | 9.0% FLEURS, 14.1% Common Voice 11 (self-reported) | Trained on GramVaani, ULCA, Shrutilipi, FLEURS train/dev. Check each corpus licence before shipping |
| collabora/whisper-small-hindi | small | CC-BY-4.0 (attribution) | 7.2% FLEURS (Whisper normaliser), 15.1% (Indic normaliser) | Training data includes YODAS (YouTube-derived) and snow-mountain (CC-BY-SA). Provenance risk for us |
| Fine-tuned small (research) | small | n/a | 13.8–14.4% Kathbath (arXiv 2412.19785); 18.7% Vividh-ASR (adalat-ai) | Shows what a Hindi-tuned small can reach |
| IndicWhisper (AI4Bharat Vistaar) | medium | MIT | 10.3% Kathbath, 11.4% FLEURS, 26.8% Gramvaani (Vistaar Table 3); 25.0% Vividh-ASR | Too big and slow for phones; useful accuracy reference |
| Oriserve Whisper-Hindi2Hinglish-Prime | large-v3 | Apache-2.0 | 28.7% FLEURS, 32.4% Common Voice in romanised Hinglish (self-reported; large-v3 scored 50.8% / 61.9% on the same scoring) | Outputs Roman-script Hinglish. ~1.5B params: too big; worth watching for a smaller "Swift"-style release |

A Hindi fine-tune usually gets worse at English. Shipping one implies language
routing (detect language, then pick the English or Hindi model) or two models.

### Indian-language models (non-Whisper)

| Model | Params | Quantised size | Published Hindi WER | Speed (*estimate* unless stated) | Licence |
|---|---|---|---|---|---|
| **AI4Bharat IndicConformer, Hindi** (hybrid CTC/RNNT) | ~120M | ~120–230 MB (int8 ONNX; GGUF Q8_0 225 MB) | 13.5% Kathbath, 15.2% FLEURS (reported by the GGUF converter, not AI4Bharat) | Non-autoregressive CTC: no token-by-token decode. Desktop CPU RTF 0.06 (GGUF page). Phone CPU likely RTF ~0.1–0.3 | MIT on AI4Bharat's Hugging Face card (gated: accept terms). One community conversion relabels it CC-BY-4.0; convert from the original ourselves and record the terms |
| IndicConformer multilingual | 600M | ~600 MB int8 | Not found | Slower | MIT (repo) |
| NVIDIA NeMo Conformer-CTC Hindi (Vistaar "Nvidia-large") | 120M | ~120 MB int8 | 12.7% Kathbath, 15.7% FLEURS, 42.6% Gramvaani (Vistaar) | As IndicConformer | Check NGC terms |
| Vosk small Hindi (Kaldi) | n/a | 42 MB | 20.9% IITM, 24.7% MUCS (Vosk site) | Fast, real time on old phones | Apache-2.0 |
| Vosk small Indian English | n/a | 36 MB | 49.1% NPTEL (Vosk site) | Fast | Apache-2.0 |
| Qwen3-ASR 0.6B | ~0.9B | GGUF ~1.8 GB as published; ≥600 MB at 8-bit | No Hindi-only figure. The 1.7B model scored 11.2% vs large-v3's 24.1% on asr-norm-check's FLEURS Hindi slice | Mobile runtimes immature (community ONNX/GGUF only) | Apache-2.0 |
| "Srota" Hinglish fine-tune of Qwen3-ASR 0.6B | ~0.78B | as above | 15.9% HiACC conversational (base 24.7%) | as above | Apache-2.0 claimed; training data licences not stated |

Runtime for Conformer/CTC models on phones: sherpa-onnx (Apache-2.0) or ONNX
Runtime Mobile (MIT) on both platforms, after exporting from NeMo.

Not usable commercially, so excluded: Meta MMS and SeamlessM4T (CC-BY-NC-4.0).
NVIDIA Parakeet TDT 0.6B v3 does not cover Hindi. The phones' built-in speech
recognisers can't reliably transcribe arbitrary audio files offline on
Android, and their output varies by device, so they are out of scope.

### Hinglish and script, per engine
| Engine | Output for "ये cafe इंदिरानगर में है" style speech |
|---|---|
| Whisper, `language=hi` | Mostly Devanagari, with English words often transliterated (`कैफ़े`) and sometimes in Latin. Sometimes emits Urdu script for Hindi speech. Smaller sizes hallucinate and repeat more on music and noise |
| Whisper, `language=en` or auto-detect on Hinglish | Auto-detect flips between `hi` and `en`; with `en` Whisper often translates into English, which loses the original words. Pin or route the language |
| Whisper Hindi fine-tunes | Devanagari; English words usually transliterated |
| Oriserve Hindi2Hinglish | Roman-script Hinglish |
| IndicConformer, NeMo, Vosk | Devanagari only. English words always come out in Devanagari; English-only reels need another model |
| Qwen3-ASR base / Srota | Base: all-Devanagari transliteration; Srota: mixed script |

Script choice is handled at scoring time (transliteration + Hinglish skeleton)
and should be handled at search time (index a romanised form next to the
transcript) rather than by forcing one engine to output one script.

## Round 1 results (2026-10-23)
Measured on public data, desktop CPU: see `evals/benchmarks/speech-round1/README.md (round 2: evals/benchmarks/speech-round2/README.md)`.
On the same 445 Hindi/Hinglish clips: stock Whisper small 57.9% WER, Hindi
fine-tune (vasista22) 30.9%, Hinglish model (Oriserve Prime) 25.4%,
large-v3-turbo 31.0%. English: Whisper small 9.4%. Round 2: Oriserve Apex
(0.8B) matches Prime at 27.2% on the same clips at half the size; the Hindi
fine-tune's Hinglish weakness is real (70% even with script forgiven). Phone
speed not yet measured.

## Recommendation: what to benchmark first

Because size no longer matters, the likely shipping setup is **both**: stock
Whisper small for English plus the best Hindi model, with language routing.
Round 1 picks the Hindi model.

Round 1 (on the golden set, one tier-2 Android phone plus an iPhone 12/13,
language pinned from the manifest, then auto-detect):

1. **Whisper small multilingual, stock** (whisper.cpp q5_1, 190 MB; WhisperKit).
   It is the architecture's default and the English baseline. Expected: English
   fine, Hindi far from target.
2. **Whisper small Hindi fine-tune: vasista22/whisper-hindi-small** (Apache-2.0).
   Same runtime and size, so it is the cheapest possible Hindi upgrade. Run it
   on Hindi and Hinglish clips only, and measure how much English it loses.
   First check the licences of its training corpora.
3. **IndicConformer Hindi** (MIT, ~120M, CTC) via sherpa-onnx int8. Likely the
   best Hindi accuracy per MB and per second, and fast enough to fit the time
   budget. Costs: a second runtime, Devanagari-only output, and Hindi only.
4. **Ceiling reference, desktop only**: large-v3-turbo (q5_0) on the same
   clips, to see how much headroom bigger models offer before spending effort
   on them.

Also time **base** on the slowest tier-2 phone as a speed floor for tier 3.

Why this order: the gap that matters is Hindi, and the two levers are a Hindi
fine-tune of the model we already planned (no new runtime) versus a different,
faster architecture (new runtime, but likely solves speed too). Round 1 tells
us which lever is worth it. The likely end state is language routing:
detect the language (Whisper's own detector or a tiny LID), then use stock
Whisper small for English and a Hindi model for Hindi and Hinglish.

## Realistic expectations on our reel-style golden set
*Estimates from the published numbers above, adjusted for spontaneous speech,
music and street noise; to be replaced by the round-1 report.*

| Language | Stock Whisper small | Hindi-tuned small or IndicConformer |
|---|---|---|
| English (Indian English heavy) | 10–18% WER | n/a (route to stock) |
| Hindi + Hinglish (official, script-agnostic) | 40–65% WER | 20–35% WER |

So the current targets (`speech.wer_en` ≤ 15%, `speech.wer_hi` ≤ 35%) are
reachable, but **stock Whisper small will not meet the Hindi target**. That is
a model choice to make, not a reason to relax the threshold, so
`evals/thresholds.json` is unchanged. The week-2 Hindi baseline will likely
be RED with stock small; tighten `wer_hi` toward ~25% once a Hindi model is
in.

## Risks
1. **Speed on mid-range Android** (biggest): Whisper small on CPU probably
   runs at RTF 0.5–1.0 for English and slower for Hindi (tokeniser), which
   blows the ≤ 30 s reel read target. Mitigations: CTC model for Hindi, NPU
   paths (Qualcomm AI Hub, MediaTek NeuroPilot; vendor-specific), background
   processing on charge (already planned), or transcribing only the first N
   seconds immediately and the rest later.
2. **Size** (resolved): founders accepted a larger app, so speech models are
   bundled (docs/decisions/0003). No download server, no extra network host.
   Remaining cost: a bigger install may lose some installs on low-storage
   phones; growth-research tracks install conversion against app size.
3. **Hinglish script chaos**: engines disagree on script and Whisper sometimes
   emits Urdu script or translates. Pin the language per clip, and make search
   script-agnostic.
4. **Licence and data provenance** of community fine-tunes: weights may be
   permissive while training data is YouTube-derived or share-alike.
5. **Golden-set realism**: public datasets are cleaner and more formal than
   reels, and the only commercially usable Hinglish set (MUCS 2021) is
   lecture speech. Augmentation (music, noise, speed, re-encode, pseudo-reels)
   narrows the gap but real-world WER will be somewhat worse than measured.
6. **Test-set contamination**: AI4Bharat models (IndicConformer, IndicWhisper)
   are trained on AI4Bharat corpora (likely including IndicVoices and
   Kathbath training splits; confirm on each model card before round 1). We score on held-out splits and Lahaja (a benchmark-only set), and
   report per source so contaminated sources can be excluded per model.

## Licences recorded
| Component | Licence | Commercial use |
|---|---|---|
| whisper.cpp | MIT | Yes |
| WhisperKit (Argmax OSS) | MIT | Yes |
| OpenAI Whisper weights (all sizes) | MIT | Yes |
| vasista22/whisper-hindi-small | Apache-2.0 | Yes (verify training corpora) |
| collabora/whisper-small-hindi | CC-BY-4.0 | Yes with attribution (data provenance risk) |
| IndicWhisper (Vistaar) | MIT | Yes |
| AI4Bharat IndicConformer | MIT (gated download, accept terms) | Yes (record the terms text) |
| Oriserve Whisper-Hindi2Hinglish-Prime | Apache-2.0 | Yes |
| Qwen3-ASR 0.6B / 1.7B | Apache-2.0 | Yes |
| Vosk models listed | Apache-2.0 | Yes |
| sherpa-onnx | Apache-2.0 | Yes |
| Meta MMS, SeamlessM4T | CC-BY-NC-4.0 | **No**: excluded |

Evaluation datasets and their licences are recorded in
evals/golden/speech/README.md (all allow commercial use).

## Sources
- Vistaar / IndicWhisper benchmark: https://arxiv.org/abs/2305.15386 , code and licence https://github.com/AI4Bharat/vistaar
- Whisper fine-tuning and tokenisation for Indian languages (Kathbath WERs): https://arxiv.org/html/2412.19785v1
- Vividh-ASR studio-bias benchmark: https://huggingface.co/blog/adalat-ai/vividh-benchmark
- Whisper small/medium zero-shot FLEURS Hindi: https://github.com/Abhigyan1805/hindi-voice-asr
- Whisper large-v3 / turbo / small FLEURS Hindi and English (50 utts): https://vocova.app/blog/ai-transcription-accuracy-benchmark-2026
- Whisper large-v3 vs Qwen3-ASR 1.7B Hindi, normalisation sensitivity: https://github.com/elrond298/asr-norm-check
- whisper.cpp quantised model sizes: https://huggingface.co/ggerganov/whisper.cpp/tree/main
- WhisperKit CoreML model sizes and licence: https://huggingface.co/argmaxinc/whisperkit-coreml
- Qualcomm AI Hub Whisper-Small-Quantized latencies: https://huggingface.co/qualcomm/Whisper-Small-Quantized
- IndicConformer: https://github.com/AI4Bharat/IndicConformerASR , https://huggingface.co/ai4bharat/indicconformer_stt_hi_hybrid_ctc_rnnt_large , GGUF conversion and reported WER/speed https://huggingface.co/Singla0009/IndicConformer-GGUF , ONNX conversion https://huggingface.co/OpenVoiceOS/ai4bharat-indicconformer-hi-onnx
- Hindi Whisper fine-tunes: https://huggingface.co/vasista22/whisper-hindi-small , https://huggingface.co/collabora/whisper-small-hindi , https://huggingface.co/ARTPARK-IISc/whisper-large-v3-vaani-hindi
- Oriserve Hinglish model: https://huggingface.co/Oriserve/Whisper-Hindi2Hinglish-Prime , https://oriserve.com/blog/oriserve-open-sources-india-focused-ai-speech-model-fine-tuned-on-whisper
- Qwen3-ASR: https://huggingface.co/Qwen/Qwen3-ASR-0.6B , Srota Hinglish fine-tune https://discuss.huggingface.co/t/open-source-hinglish-asr-fine-tuned-from-qwen3-asr-0-6b-15-85-wer-on-conversational-test/176416
- Vosk models: https://alphacephei.com/vosk/models
