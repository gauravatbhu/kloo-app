# 0002 — All AI on device; backend limited to sign-in, encrypted backup and receipts

- Status: accepted
- Date: 2026-10-22
- Deciders: Gaurav, Claude

## Context
User trust is the product's foundation (PRINCIPLES.md 1–3). Cloud AI would
cost $60–210 a month at 100–1,000 users and would see user content.

## Decision
Speech, OCR, embeddings and answers run on the phone (see
docs/architecture.md). The backend only handles sign-in, encrypted backup
blobs and shared-board membership.

## Consequences
- Near-zero cost per user; strongest privacy claim.
- Answer quality varies by device tier; Hindi is weaker on Apple's model.
- More engineering: model packaging, background processing, E2E crypto.
- The eval suites in `evals/` must track quality per device tier.
