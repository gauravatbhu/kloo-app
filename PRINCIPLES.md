# Principles (non-negotiable)

Every agent checks its work against this file before calling a task done.
`security-privacy` can block any change that breaks one of these. Changing
this file needs both founders' approval and a decision record in
`docs/decisions/`.

## Privacy
1. A user's saves, videos, transcripts, frames, notes, questions and answers
   never leave their phone, except inside an end-to-end encrypted backup or
   shared board that only the user (and people they invited) can decrypt.
2. Kloo's servers never hold readable user content. Keys never leave devices.
3. No analytics SDK receives content. Crash reports are opt-in and scrubbed.
4. Photo access is limited and only used to find newly downloaded reels.
5. Clipboard is read only after an explicit user tap.

## Ads and money
6. Ads are non-personalised only. Never request the advertising ID.
7. Ads appear only as one labelled card on Home. Never in saving, Ask,
   answers, lists, onboarding. Never "watch an ad to unlock".
8. Blocked ad categories: loans and instant credit, gambling, crypto, dating,
   alcohol, political.
9. Never sell or share data. Never paywall a user's existing saves.

## Content and platforms
10. No scraping, no third-party downloaders, no logging into users'
    Instagram or TikTok accounts. Video arrives only as files the user
    downloaded or recorded with platform and phone tools.
11. Transcripts and summaries are private to each user and always link back
    to the original post.

## Honesty
12. Every privacy or AI claim in the app is literally true and covered by a
    test in `evals/privacy/`.
13. Answers are grounded only in the user's own saves; when nothing matches,
    say so.

## Users
14. Age gate: 18+ in India, 13+ in the US.
15. Accessible by default: real buttons and labels, 44 pt touch targets,
    4.5:1 text contrast, Dynamic Type and TalkBack/VoiceOver support.
