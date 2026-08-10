# Task80A — Course/Lesson Read-Contract Architecture

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

Implementation branch: `codex/task80a-learning-course-lesson-read-contract-architecture`

Provider-readiness closeout PR: `#36`

Status: `ARCHITECTURE MERGED / CLOSEOUT MERGED / POST-MERGE GREEN / PROVIDER_TRANSPORT_BLOCKED`

## Objective

Define a bounded, tenant-safe, read-only Course/Lesson contract for a later separately authorized implementation task.

## Reviewed architecture packet

Reviewed architecture HEAD: `0eeb107e064bb99669c7ea0e94d52654df4687fe`.

Exact immutable provider file/blob bindings:

1. `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md`
   - blob: `5ad991af630f107a72edcd9d6e30af26eb78d4db`
2. `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`
   - blob: `78f8f83cecd881651466b9c092f1454060968a9a`
3. `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`
   - blob: `03b1143e698eeff778bbb1aef84cdbe9f99c0415`

The provider packet remains bound to those three blobs. Later readiness/closeout revisions are evidence only and must not replace the reviewed architecture packet.

## Architecture scope

- future read surface limited to two GET proposals: Course list and lessons-by-course list;
- published Course/Lesson rows only;
- tenant authority from the validated existing request/session boundary;
- active tenant membership remains the admission boundary;
- cross-tenant and hidden parent identifiers must not disclose existence;
- Course fields: id, code, title, state;
- Lesson fields: id, code, title, position, state;
- pagination default 20, maximum 100;
- truthful empty states;
- no runtime/API/OpenAPI canonical schema, migration, SQL/RLS, model, frontend, cohort/progress, PII activation, Release, Deployment, Production, or protected `codesho` change in Task80A.

## Architecture validation and merge evidence

Pre-merge architecture CI: `31402531075` — `SUCCESS`.

Pre-merge architecture Compose: `31402530817` — `SUCCESS`.

Architecture PR: `#35`.

Architecture merge commit on `main`: `813db363411f857d35bc5774b7856cdc71b49e41`.

Architecture post-merge CI: `31402907652` — `SUCCESS`.

Architecture post-merge Compose: `31402907634` — `SUCCESS`.

Evidence included backend full tests, frontend checks/build, canonical OpenAPI parity, PostgreSQL RLS/connection-reuse, and backup/restore.

## Provider-readiness closeout evidence

Readiness exact HEAD: `6883cfb91f5480879e4a6dbeb4e26aa3d7a94f37`.

Readiness diff: exactly two docs-only files:

- `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`;
- `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`.

Readiness pre-merge CI: `31403967254` — `SUCCESS`.

Readiness pre-merge Compose: `31403966932` — `SUCCESS`.

Readiness PR `#36` was marked Ready and squash-merged race-safely with expected head SHA `6883cfb91f5480879e4a6dbeb4e26aa3d7a94f37`.

Readiness merge commit on `main`: `ff1723c5b1fde651bacf4d49c414ca94b8f513db`.

Readiness post-merge CI: `31404270837` — `SUCCESS`.

Readiness post-merge Compose: `31404270834` — `SUCCESS`.

Post-merge readiness evidence specifically confirms:

- backend full tests: `SUCCESS`;
- frontend checks/build: `SUCCESS`;
- canonical OpenAPI parity: `SUCCESS`;
- backend runtime image inspection: `SUCCESS`;
- PostgreSQL RLS and connection-reuse tests: `SUCCESS`;
- backup create/restore/verify: `SUCCESS`.

## Provider transport blocker

Blocker classification: `PENDING_PROVIDER_TRANSPORT`.

This is an operational transport/tooling blocker only. It is neither a Qwen/Claude architecture verdict nor a substantive architecture finding.

### Checked permitted paths

1. Plugin discovery query: `Qwen OR Claude OR Anthropic`.
   - result: no direct Qwen, Claude, or Anthropic connector available; only unrelated Vercel/Base44 suggestions.
   - disposition: unrelated providers are not substitutes.
2. GitHub repository code search: `claude qwen runner browser`.
   - repository: `mytest19861986/codesho-test`.
   - result: `results=[]`, connector error `null`.
3. GitHub repository code search: `claude_brave`.
   - result: `results=[]`, connector error `null`.
4. GitHub repository code search: `qwen`.
   - result: `results=[]`, connector error `null`.
5. Available GitHub connector capabilities were inspected.
   - result: repository/PR/Actions operations are available, but no external Qwen/Claude model-session invocation exists.

A previous attempt to create the final evidence branch using a direct SHA was rejected by the tool safety check; the permitted `base_ref=main` path was then used after re-verifying `main@ff1723c5b1fde651bacf4d49c414ca94b8f513db`. This did not affect repository content or provider status.

### Safety rules while blocked

- do not fabricate a provider response;
- do not infer provider PASS from Commander preflight, CI, Compose, or absence of findings;
- do not use unrelated model services as substitutes;
- do not bypass quota, authentication, browser/profile locks, file-attachment restrictions, or other provider controls;
- do not disrupt shared authenticated browser/profile sessions;
- Qwen must run first;
- Claude must run only after a real Qwen PASS.

## Resumable provider checkpoint

Checkpoint: `TASK80A_PROVIDER_GATE_READY_TO_RESUME`.

Qwen prompt ID: `QWEN_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_REVIEW_01_V1`.

Qwen PASS condition:

- `CONTENT_RECEIVED_COMPLETE=YES`;
- `P0_COUNT=0`;
- `P1_COUNT=0`;
- `OPEN_BLOCKERS=0`;
- `IMPLEMENTATION_RECOMMENDATION=READY_FOR_CLAUDE`.

Claude prompt ID: `CLAUDE_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_HARD_GATE_01_V1`.

Claude receives the identical three-blob architecture packet plus Qwen's complete real response and runs only after Qwen PASS.

Claude PASS condition:

- `CONTENT_RECEIVED_COMPLETE=YES`;
- `P0_COUNT=0`;
- `P1_COUNT=0`;
- `OPEN_BLOCKERS=0`;
- `IMPLEMENTATION_RECOMMENDATION=READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.

Resume procedure:

1. Confirm a permitted authenticated Qwen transport is available.
2. Re-bind the three immutable provider blobs.
3. Send the complete, untruncated three-file packet to Qwen.
4. Record Qwen's complete real response.
5. If Qwen is not a PASS, stop before Claude and remediate only documented architecture issues.
6. If Qwen PASSes, send the identical packet plus Qwen result to Claude.
7. Record Claude's complete real response.
8. Only after both real PASS results may a separately bounded runtime successor be started.

## Runtime successor gate

Runtime/API/OpenAPI implementation is `BLOCKED`.

No runtime successor may start while provider transport is unavailable or while either provider gate is incomplete.

Independent work permitted while blocked is limited to docs-only provenance/readiness/coordination that does not alter the reviewed architecture packet.

## Final disposition

Task80A architecture and provider-readiness closeout are merged and fully validated in `codesho-test`.

Provider transport remains the only open blocker.

Runtime successor remains blocked pending real sequential Qwen→Claude PASS results.

No Release, Deployment, Production, or protected `codesho` action occurred.
