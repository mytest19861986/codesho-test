# Codesho Repository Instructions

## Authority and scope

- The employer approves product scope, architecture, paid infrastructure,
  legal decisions, production releases, and promotion to the protected
  `codesho` repository.
- Commander AI owns task assignment, technical coordination, and review.
  Codex implements only approved, in-scope work; Gemini reviews UI; Claude
  reviews high-risk architecture, security, and database changes.
- Resolve material ambiguity with Commander and record the decision in the
  coordination artifacts. Do not restart cancelled, completed, or blocked
  work without a new approved task.

## Fixed architecture and security rules

- Use Django 5.2 + DRF, Next.js App Router + TypeScript, PostgreSQL, Redis,
  Celery, a modular monolith, REST, and OpenAPI. Business logic belongs in
  Django; Next.js never accesses PostgreSQL directly.
- Do not put workflows in Django signals or serializers, call external
  providers inside database transactions, or use AI at runtime without a new
  ADR and approval.
- Tenant context fails closed and is established inside `transaction.atomic()`
  before tenant queries. Tenant Celery tasks inherit `BaseTenantTask`.
- Never log or commit secrets, tokens, OTPs, passcodes, cookies, sensitive
  child data, review attachments, or raw provider responses. Persist IRR minor
  units and UTC `TIMESTAMPTZ`; toman and Jalali are presentation-only.
- Published content, consent, receipts, evidence, and audit events are
  immutable. Keep API changes represented in OpenAPI.

## Bootstrap and repository workflow

- Project root: `H:\codesho\codesho\codesho`; coordination root:
  `H:\codesho\codesho`. At the start of each session read `AGENTS.md`,
  `docs/coordination/CODEX_MASTER_PROMPT_FA.md`, `PROJECT_STATE.md`,
  `CURRENT_TASK.md`, relevant decisions, and (if present)
  `chatgpt\COMMANDER_TO_CODEX.md`.
- Inspect `.git`, `git status -sb`, `git remote -v`, current HEAD, recent
  commits, and the latest relevant CI before changing files. Treat live code
  and tests as authoritative; preserve all unrelated local changes.
- `codesho-test` permits approved sprint work. Never push or promote to the
  protected `codesho` remote without explicit employer approval. Make small,
  scoped commits and push only completed, authorized work.
- Current task, CI evidence, sprint status, temporary blockers, and handoff
  details belong in `docs/coordination/` and `chatgpt/CODEX_TO_COMMANDER.md`,
  not in this durable instruction file.

## Execution, review, and verification

- Work continuously inside the active task: inspect, plan, implement, test,
  review the diff, fix, retest, document, checkpoint, and monitor CI. Stop
  only when acceptance criteria pass or the remaining work needs external
  authority, credentials, assets, provider access, or a product decision.
- Run relevant backend/frontend lint, type checks, tests, migrations from an
  empty database, OpenAPI checks, tenant/RLS negatives, session/CSRF,
  outbox-idempotency, and `git diff --check`. Do not weaken tests to make them
  pass. If local Docker/PostgreSQL is unavailable, use the required real CI
  workflow and report that evidence accurately.
- Every Gemini or Claude request uses an exact, versioned prompt. Keep its
  exact prompt, attachments, screenshots, and raw response outside the
  repository; commit only an auditable findings/disposition summary.
- Claude uses a free account: reviews are sequential, never parallel, and
  contain at most five files. Prefer one large file or at most two tightly
  related files. On a Claude rate limit, do not bypass quota, change accounts,
  hammer retries, or alter authentication; stop calls and record resumable
  state.
- Gemini may provide a fallback review only when labelled
  `GEMINI_FALLBACK_REVIEW` and `NOT_CLAUDE_VERIFIED`. Critical security,
  database, authentication, authorization, tenant-isolation, payment, and
  privacy gates still require later Claude verification. Disposition findings
  before applying them.
- For a blocker, attempt bounded safe diagnostics, approved fallback, and
  independent in-scope work first. Record the exact command/error, evidence,
  remaining decision, and resumable checkpoint in coordination artifacts.

## Shared browser session

- Use the existing shared Brave session first through `127.0.0.1:9222`.
  Preserve it; never close the browser or shared session for automation,
  cleanup, or recovery. Only open the existing Profile 13 if no session is
  available, and do not change its profile/configuration without employer
  approval.
