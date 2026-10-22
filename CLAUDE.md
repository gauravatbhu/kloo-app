# Kloo (working name) — project guide for Claude and the agent team

Kloo lets people save reels and posts from Instagram, TikTok and YouTube,
reads them on the phone, and answers questions about them. Everything runs
on-device. Name is a placeholder until trademark checks finish.

The full product brief lives in the "Social Media Second Brain — Product
Brief" doc. This repository plus `docs/decisions/` is the team's shared
memory: write decisions down, because no session remembers the last one.

## Read first
- `PRINCIPLES.md` — non-negotiables. Check every change against it.
- `docs/architecture.md` — the stack and why.
- `docs/team.md` — who does what, and how work flows.
- `evals/README.md` — what "good" means, measured.

## Founders
- Gaurav: final say on strategy, money, legal, accounts, store releases,
  anything irreversible.
- Claude: strategy partner, architect, orchestrates agents, runs the weekly
  review, keeps the decision log.

Agents never spend money, sign anything, publish to stores, change account
or billing settings, or push to `main` without review. Ask Gaurav.

## Repository layout (target)
```
apps/ios/            SwiftUI app + Share Extension
apps/android/        Jetpack Compose app + share target
core/                Kotlin Multiplatform shared logic
models/              on-device model configs and download manifests (no weights in git)
backend/             Supabase migrations, Cloudflare R2 backup worker
evals/               eval suites, golden sets, runners, reports
docs/                architecture, decisions, team, research
.claude/agents/      agent definitions
```

## How work flows
1. Founders agree the weekly priorities (in `docs/weekly/YYYY-WW.md`).
2. Claude breaks them into issues and assigns an agent per issue.
3. The agent works on a branch, with tests and any eval it affects.
4. Required reviews: `security-privacy` for anything touching data, network,
   storage, permissions or third-party SDKs; `design` for UI and copy;
   `architect` for cross-layer changes.
5. `qa-eval` runs the eval suites; no regression beyond thresholds in
   `evals/thresholds.json`.
6. Gaurav merges, or approves Claude to merge.

## Definition of done (every task)
- Principles checked; tests added or updated; evals not regressed.
- Docs or a decision record updated if behaviour or architecture changed.
- User-facing copy is plain, short and literally true.

## Commands
- Run evals on sample data: `python3 evals/run_evals.py --results evals/golden/sample_results.jsonl`
- Check a network capture against the privacy allowlist:
  `python3 evals/privacy/check_egress.py evals/privacy/sample_capture.jsonl`
