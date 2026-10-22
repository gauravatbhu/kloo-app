# Team

Two founders and ten AI agents. Agents are defined in `.claude/agents/`.
Call one in a Claude Code session by asking for it by name, for example
"use the ios-engineer agent to build the share extension".

| Agent | Owns | Reviews | Done means |
|---|---|---|---|
| architect | Architecture, decision records | Cross-layer changes | ADR written; principles intact |
| ios-engineer | `apps/ios` | — | Builds; unit + UI tests; accessibility |
| android-engineer | `apps/android` | — | Builds; unit + UI tests; accessibility |
| core-engineer | `core/` | Shared-logic changes | 80%+ coverage on core logic |
| ml-engineer | `models/`, model evals | Model changes | No quality eval drops > threshold |
| backend-engineer | `backend/` | Server changes | Integration tests; nothing readable server-side |
| security-privacy | Threat model, compliance checklists | Data, network, storage, permissions, SDKs | Privacy suite 100%; sign-off |
| qa-eval | `evals/`, device matrix | Every build | Eval report published |
| design | Design system, screens, copy | UI and copy | Matches system; copy true to principles |
| growth-research | Competitors, store listing, pricing tests, interviews | Marketing claims | Sources cited |

## Cadence
- **Per change:** tests + affected evals; required reviews (see CLAUDE.md).
- **Nightly:** all eval suites, report to `evals/reports/`.
- **Weekly:** founders review evals, product metrics, decision log; write
  `docs/weekly/YYYY-WW.md` with next priorities.
- **Drift alarm:** any principle breach, or an eval drop past
  `evals/thresholds.json`, freezes feature work until fixed.

## What only Gaurav does
Spending money, contracts, legal sign-off, app store and developer accounts,
store submissions, pricing changes going live, anything irreversible.
