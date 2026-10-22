# Architecture

Native apps sharing one Kotlin core, open-source on-device models, and a
deliberately tiny backend. Target running cost: about $15–25 a month at launch.

## App structure
| Layer | Choice |
|---|---|
| iOS UI | SwiftUI + Share Extension |
| Android UI | Jetpack Compose + share target |
| Shared core | Kotlin Multiplatform: data model, filing, search ranking, actions, backup/sync logic |
| Local DB | SQLite encrypted with SQLCipher; FTS5 keyword search; vector extension for embeddings |

## On-device AI
| Job | Engine | Notes |
|---|---|---|
| Speech to text | whisper.cpp (Android), WhisperKit (iOS) | MIT. Start with multilingual Whisper "small"; evaluate larger for Hindi |
| On-screen text | Apple Vision; Google ML Kit text recognition | Offline |
| Embeddings | EmbeddingGemma 308M, 256-dim (Matryoshka) | <200 MB RAM quantised, 100+ languages |
| Answers, tier 1 | Apple Foundation Models; Gemini Nano (ML Kit Prompt API, alpha) | Recent flagships only; Apple has no Hindi yet |
| Answers, tier 2 | Gemma 3 1B via LiteRT-LM (~1 GB optional download) | LiteRT-LM Swift is early preview; llama.cpp fallback on iOS |
| Answers, tier 3 | Result cards only | Older phones |

## Video pipeline (on device)
1. Receive file (share or "you just downloaded a reel" via limited photo access).
2. Extract audio (16 kHz mono) and ~6 key frames.
3. Transcribe; OCR frames; read watermark handle.
4. Small model (or rules on tier 3) fills fields: topic, title, entities, steps.
5. Embed title + summary + transcript chunks; write to encrypted SQLite.
6. Delete working copy; offer to remove the reel from Photos.
Runs as background work, preferring Wi-Fi and charging.

## Backend
| Need | Service |
|---|---|
| Sign-in, account IDs, board membership | Supabase Auth + Postgres (free tier) |
| Encrypted backup blobs | Cloudflare R2 ($0.015/GB-month, 10 GB free, zero egress) |
| Subscriptions | StoreKit 2 / Play Billing, verified on device |
| Ads | AdMob, non-personalised |
| Crash reports | Sentry, opt-in, scrubbed |
| CI | GitHub Actions; Xcode Cloud for iOS |

## Encryption
- Library key generated on device, stored in Secure Enclave / Android Keystore.
- Backup: libsodium XChaCha20-Poly1305, chunked; recovery key shown once,
  saved to the OS password manager; device-to-device approval as backup path.
- Shared boards: per-board key, wrapped for each invited member.

## Not used, on purpose
Custom AI server, hosted vector DB, RevenueCat, Firebase Analytics, any SDK
that can read the library.
