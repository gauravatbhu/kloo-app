# Kloo copy guide, v1

Kloo is a calm friend who remembers what you saved. It's plain, warm and
short. Every claim must be literally true (PRINCIPLES.md 12).

## Voice

- **Plain.** Use words a busy person reads in one glance: "Ask your saves",
  not "Query your knowledge base".
- **Warm, not cute.** Use no exclamation marks in system copy, no emoji in
  UI, and no jokes in errors.
- **Short.** Headlines are 8 words or fewer. Body text is one or two
  sentences. Buttons are 1–3 words and start with a verb ("Add the video",
  "Turn on backup").
- **Active.** Write "Kloo reads the video on your phone", not "The video is
  processed locally".
- **Who is speaking:**
  - In conversation surfaces (the Save sheet and Ask answers), Kloo speaks
    as "I": "What I found in the video", "I couldn't find that in your saves".
  - Everywhere else (settings, permissions, privacy, payments), use "Kloo"
    or "we" for the company, so it's clear who does what.
  - Never say "I" in privacy or legal statements.
- **Sentence case** everywhere. DM Mono labels are uppercase only through
  styling.
- **Numbers** are digits ("3 recipes", "12 saves"). Dates are relative
  ("3 weeks ago").

## Words we use and avoid

| Use | Avoid | Why |
|---|---|---|
| save, saves | content, items, assets, bookmarks | What users call them |
| reel, video, post | media, clip (unless the user uses it) | Platform words people know |
| ask | search, query, prompt | The core action |
| collection | folder, board (boards are shared, a later feature), category (internal) | |
| file / filing ("Help me file these") | organise with AI, auto-tag | Human verb |
| read, listen, "read the text on screen" | watch, see, understand, know | Literal description of what on-device AI does |
| on this phone / on your phone | locally, on-device, edge | Plain |
| backup, encrypted backup | cloud, sync, upload (alone) | Backup is the one thing that leaves the phone, and it is encrypted |
| Not now | No thanks, Maybe later, "I don't want to stay safe" | Neutral decline, no shaming |
| Pro | Premium, Plus, Unlock | One name |
| Download, then share | rip, grab, save offline | Matches the platform's own Download button |
| Ad | Sponsored, Promoted, Recommended | Clearest label |

Also avoid: "smart", "magic", "AI-powered", "second brain", "seamless",
"just", "simply", "oops", and anything that blames the user.

## Privacy and AI claims

Each allowed claim must be covered by a test in `evals/privacy/` before it
ships (PRINCIPLES.md 12). The security-privacy agent signs off on any new claim.

### Allowed

| Claim | Where | Why it's true |
|---|---|---|
| "Your saves never leave your phone." | Welcome, Save sheet, settings | PRINCIPLES 1. When backup is on, use the backup version below instead, so the claim is never stretched. |
| "Answered on this phone." | Under every Ask answer | All answer tiers run on the device (docs/architecture.md). |
| "Your backup is encrypted on this phone before it's uploaded. Only you can unlock it." | Backup screen | E2E, the keys never leave the device (PRINCIPLES 2). |
| "We can't read your saves or your backup." | Backup, Pro, FAQ | Servers hold no readable content. |
| "Kloo never asks for your Instagram or TikTok password." | How your saves get here | PRINCIPLES 10 |
| "Ads in Kloo aren't personalised and aren't based on your saves." | About this ad | PRINCIPLES 6 |
| "Your voice is turned into text on this phone." | Microphone explainer | On-device speech-to-text |
| "Crash reports are off unless you turn them on." | Settings | PRINCIPLES 3 |

### Not allowed

| Claim | Why not | Say instead |
|---|---|---|
| "Nothing leaves your phone." | Ads, backups, sign-in and model downloads all use the network. | "Your saves never leave your phone." |
| "100% private", "completely private", "bank-grade/military-grade" | Vague, so they can't be tested | A specific, tested claim |
| "Works fully offline" | Model download, backup and ads need the network | "Answers work without internet once Kloo is set up." Only use this if tested on every tier. |
| "We don't collect any data" | We hold account IDs, receipts and encrypted blobs | "We can't read your saves or your backup." |
| "No tracking" | The ad SDK and opt-in crash reports exist | "Ads aren't personalised. Kloo never uses your advertising ID." |
| "Anonymous" | Accounts exist | Leave it out |
| "Kloo watches your reels" / "understands everything" | It transcribes audio and reads a handful of frames | "Kloo listens to the video and reads the text on screen." |
| "Always finds it" | False when nothing matches (PRINCIPLES 13) | "Ask, and Kloo looks through your saves." |

## Permission explanations

Each one is a single sentence shown on the permission explainer, before the
OS prompt. The OS dialog's own purpose string (iOS `NS…UsageDescription`,
Android rationale) uses the same sentence.

| Permission | Title | Sentence | Buttons |
|---|---|---|---|
| Photos (limited) | Pick up reels you download | "Kloo only checks for new videos you download, so your saved reels show up here without sharing each one." | Continue / Not now |
| Notifications | Get a nudge when it helps | "Kloo can tell you when a reel is ready to ask about and remind you of an old save now and then." | Continue / Not now |
| Microphone | Ask by voice | "Your voice is turned into text on this phone, and the recording isn't kept." | Continue / Not now |

Notes
- The photo sentence is only true if engineering limits access to new videos
  (PRINCIPLES 4). The "isn't kept" part of the microphone sentence needs a
  privacy test. If either can't be met, the sentence changes, not the test.
- If the user denied a permission earlier, show "You turned this off. You can
  turn it on in Settings." with the buttons "Open Settings" / "Not now".

## Error messages

The pattern is: what happened, then what to do. Don't blame the user, don't
show error codes on screen (log them), and don't use exclamation marks.

| Situation | Copy |
|---|---|
| Link shared without video | "Link saved. Add the video so I can read it." |
| Video file can't be opened | "I couldn't open this video. Try downloading it again, then share it to Kloo." |
| No speech or text found | "I couldn't hear speech or find text in this video. Add a note so you can find it later." |
| Video too long (if there's a limit) | "This video is longer than {n} minutes. I saved the link and the first {n} minutes." Only if true. |
| Phone storage full | "Your phone is almost full, so I paused reading videos. Free up some space and I'll carry on." |
| Answer model still downloading | "Getting ready to answer. This needs Wi-Fi once, about {size}." |
| Ask: nothing matches | "I couldn't find that in your saves." Then: "Try other words, or save a reel about it." |
| Backup failed | "Backup didn't finish. Your saves are safe on this phone. We'll try again on Wi-Fi." |
| Purchase failed | "The payment didn't go through. You haven't been charged." Only if the store confirms this; otherwise: "The payment didn't go through. Check your App Store / Play Store purchases." |
| No connection (backup, sign-in) | "You're offline. Your saves still work. Backup will catch up later." |

## Hinglish (India)

The India headline is: **"Jo reel save ki thi, bas pooch lo."** It means
"The reel you saved? Just ask."

**Use Hinglish:**
- Only when the device region is India and the app language is English, or
  the user picks Hindi. Never for US users.
- In headlines and short marketing lines only: the Welcome headline, store
  screenshots, Home empty-state headline, and social posts.
- Written in Latin script, with spelling as people type it in chats ("pooch
  lo", not "poochh lo"). Keep it to one line.

**Use plain English (or proper Hindi once localised) for:**
- privacy claims, permission explanations, errors, payments, backup and
  recovery keys, age gate, terms, and anything legal
- buttons, because people must understand the action exactly

Never mix languages inside one sentence of instructional copy. Don't
translate privacy claims into Hinglish: precision matters more than tone
there.

A native speaker on the team should check each new Hinglish line before it ships.

## Checklist for any new string

1. Can it be shorter?
2. Is it named the way users talk?
3. If it says anything about privacy or AI, is it on the allowed list and
   covered by a test?
4. Is the decline option as clear as the accept option?
5. Does it still read well at 200% text size, and when read aloud by a
   screen reader?
