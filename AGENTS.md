# Codesho Repository Instructions

## Authority and scope

- Commander AI is the final technical authority for `codesho-test`. It may select and sequence technical tasks, refine architecture inside the approved product boundary, implement or direct implementation, create branches/commits/PRs, mark PRs Ready, merge PRs into `codesho-test/main`, re-run CI, remediate CI failures, refactor, add migrations, and continue to the next technical task without requesting a separate employer approval for each step.
- Codex executes Commander-directed work and may continue autonomously inside the active technical scope. Routine technical ambiguity is resolved by Commander and recorded in coordination artifacts; it is not escalated to the employer.
- Claude is the mandatory independent hard gate before `codesho-test` merge for material authentication, authorization, tenant-isolation/RLS, security, privacy-sensitive data handling, database/schema/migration, payment, supply-chain, or production-infrastructure architecture changes. A hard-gated change requires `PASS` with zero open P0/P1 blockers, unless Commander records a technically justified rejection of an inapplicable finding and obtains a second independent review.
- Qwen is the preferred adversarial challenger/second engineering brain for complex architecture, concurrency, failure-mode, test-strategy, or disputed-review decisions. Commander owns the final technical disposition after considering the evidence.
- Gemini owns UI/product-design review and may assist on frontend implementation decisions. It does not replace Claude for the hard-gate categories above.
- Employer approval is required only for: material product-scope/business-policy changes; legal/counsel decisions; new paid infrastructure or material recurring spend; collection/activation of real-user PII where a legal/product decision is unresolved; irreversible/destructive business-data operations; Release/Deployment/Production activation; or any push/promotion/merge to the protected `codesho` repository.
- The employer may override or pause any decision at any time. Otherwise, absence of a new employer message is not a blocker for technical progress in `codesho-test`.

## Fixed architecture and security rules

- Use Django 5.2 + DRF, Next.js App Router + TypeScript, PostgreSQL, Redis,
  Celery, a modular monolith, REST, and OpenAPI. Business logic belongs in
  Django; Next.js never accesses PostgreSQL directly.
- Technical changes to this architecture may be approved by Commander without employer confirmation when they remain inside the approved product scope. Material/high-risk changes must pass the Claude hard gate defined above and be recorded in an ADR/decision artifact.
- Do not put workflows in Django signals or serializers, call external
  providers inside database transactions, or enable AI at runtime without a recorded ADR and the applicable technical/security review.
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
- `codesho-test` is the autonomous engineering/integration repository. Commander/Codex may branch, commit, push, open/Ready/retarget/close/merge PRs, and re-run CI there when acceptance and review gates are satisfied. Never push or promote to the protected `codesho` remote without explicit employer approval.
- Use small, scoped commits, expected-head checks for risky PR mutations, no force-push by default, and preserve unrelated work. If a stacked/squash history creates an integration conflict, rebuild the task delta on current `main` rather than rewriting shared history.
- Current task, CI evidence, sprint status, temporary blockers, and handoff
  details belong in `docs/coordination/` and `chatgpt/CODEX_TO_COMMANDER.md`,
  not in this durable instruction file.

## Execution, review, and verification

- Work continuously inside the active task: inspect, plan, implement, test,
  review the diff, fix, retest, document, checkpoint, push to `codesho-test`, monitor CI, remediate failures, and complete the integration gate. Continue to the next technically ready task without asking the employer for routine continuation/Ready/Merge approval.
- Stop only when acceptance criteria pass and no next technical task is ready, or when the remaining work truly requires employer-only authority, external credentials/assets/provider access, legal/counsel judgment, protected-repository promotion, or Production/Release authority.
- Run relevant backend/frontend lint, type checks, tests, migrations from an
  empty database, OpenAPI checks, tenant/RLS negatives, session/CSRF,
  outbox-idempotency, and `git diff --check`. Do not weaken tests to make them
  pass. If local Docker/PostgreSQL is unavailable, use the required real CI
  workflow and report that evidence accurately.
- Before merging into `codesho-test/main`, verify exact head/base, diff scope, required local/remote gates, unresolved review threads, and applicable AI review gates. Use expected-head merge protection when available.
- Every Qwen/Gemini/Claude request uses an exact, versioned prompt. Keep its
  exact prompt, attachments, screenshots, and raw response outside the
  repository; commit only an auditable findings/disposition summary.
- Claude reviews are sequential, not parallel. On a rate limit, do not bypass quota, change accounts, hammer retries, or alter authentication; record resumable state and continue independent safe work. If Claude is temporarily unavailable for a hard-gated change, the change may remain in a Draft/Ready PR but must not merge until the hard gate closes.
- A Qwen disagreement does not automatically block progress. Commander must record whether each finding is accepted, rejected with technical evidence, or escalated to Claude because of material risk.
- For every Gemini interaction, first read
  `H:\codesho\codesho\gemini\GEMII_REVIEW_GUIDE.md` and use the primary
  `H:\codesho\codesho\gemini\GEMIN_REVIEW.py` channel with its project
  defaults. Use `H:\codesho\codesho\gemini api\gemini` only after the
  primary channel fails to return a complete response; do not call both
  channels in parallel. Record the exact primary-channel failure before using
  the API fallback.
- For a blocker, attempt bounded safe diagnostics, a safe fallback, and
  independent in-scope work first. Record the exact command/error, evidence,
  remaining decision, and resumable checkpoint in coordination artifacts.

## Shared browser session

- Use the existing shared Brave session first through `127.0.0.1:9222`.
  Preserve it; never close the browser or shared session for automation,
  cleanup, or recovery. Reuse existing authenticated AI conversations whenever possible. Commander may decide technical browser-automation recovery actions, but must not expose credentials, bypass authentication, evade provider safeguards, or destroy user browser data.
