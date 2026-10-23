# 0003 — Ship on-device models inside the app; no model download server

- Status: proposed (needs Gaurav's merge)
- Date: 2026-10-22
- Deciders: Gaurav, Claude

## Context
The earlier plan kept the app under 150 MB and fetched the speech and answer
models as an optional first-run download from a Kloo-run host. Research on
Hindi speech (docs/research/speech-model-options.md) showed no good speech
model fits in 150 MB, and the answer model (Gemma 3 1B) is about 0.5–1 GB.

Founders' decision (2026-10-22): app size going up is acceptable.

Store limits (checked 2026-10-22):
- Google Play: base module up to 500 MB compressed; install-time asset packs
  up to 1.5 GB each and 4 GB for the whole app.
- App Store: up to 4 GB uncompressed; downloads over 200 MB ask the user
  before using mobile data.

## Decision
Every model the app uses ships with the app at install time:
- **Android**: models in Play Asset Delivery **install-time** asset packs
  (installed with the app, served by Google Play). Later, device-tier
  targeting can skip the answer model on phones that have Gemini Nano.
- **iOS**: models inside the app bundle.

Bundled at launch (estimates, to be replaced by measured sizes):

| Model | Purpose | Approx. size |
|---|---|---|
| Whisper small multilingual (q8) | English speech | ~260 MB |
| Best Hindi speech model from round 1 (Whisper small Hindi fine-tune or IndicConformer) | Hindi / Hinglish speech | ~150–260 MB |
| EmbeddingGemma 308M (quantised) | Search | ~200 MB |
| Gemma 3 1B (int4) | Answers on tier 2 | ~550–700 MB |
| **Total with app code** | | **~1.2–1.5 GB** |

Size budget: app ≤ 2 GB installed (`speed.app_size_mb` max 2000). Every model
added or changed must report its size in the PR.

## Alternatives considered
- **Optional first-run download from our own host.** Smaller install, but adds
  a server, a network host on the privacy allowlist, a security review of the
  download path, and a broken first experience if the download fails.
  Rejected now that size is acceptable.
- **Apple-hosted Background Assets / Play on-demand packs.** No Kloo server,
  but still a later download that can fail. Keep as the fallback if install
  size proves to hurt sign-ups.

## Consequences
- **Privacy**: one fewer network host. The model download host is removed
  from `evals/privacy/allowlist.txt`, and model files can't be swapped by a
  server.
- **First run works offline**: every feature works the moment the app is
  installed. No "downloading model" screen in onboarding.
- **Install size ~1.2–1.5 GB**: on mid-range Android phones with little free
  storage, some people will not install. growth-research tracks Play Console
  install conversion and uninstall reasons; if it hurts, revisit with
  device-tier targeting or the on-demand fallback.
- **iOS** shows a "download over mobile data?" prompt for apps over 200 MB.
  Store listing copy should say "Works offline. Large download: use Wi-Fi."
- **Model updates ship as app updates.** Slower to iterate, but every model
  change goes through review and the eval suites like any other change.
- **Device tiers** are now defined by what the phone can run, not by what was
  downloaded: tier 1 built-in AI, tier 2 bundled Gemma, tier 3 cards only
  (phones too slow or low on RAM for Gemma).
