# Task80A — Course/Lesson Read-Contract Architecture

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

Implementation branch: `codex/task80a-learning-course-lesson-read-contract-architecture`

Closeout branch: `codex/task80a-closeout`

Status: `ARCHITECTURE MERGED / POST-MERGE GREEN / PROVIDER HARD-GATES PENDING / PROVIDER_TRANSPORT_BLOCKED`

## Objective

Define a bounded, tenant-safe, read-only Course/Lesson contract for a later separately authorized implementation task.

## Authorized architecture files

1. `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md`
2. `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`
3. `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`

No runtime Python/TypeScript, API route, serializer, URL, canonical OpenAPI schema, migration, SQL, RLS, grant, model, frontend, fixture, cohort, progress, learner-specific state, PII activation, Release, Deployment, Production, or protected `codesho` change was introduced.

## Contract decisions

- Future read surface is limited to two GET proposals: Course list and lessons-by-course list.
- Learner-visible rows are published only.
- Tenant authority comes only from the validated existing request/session boundary.
- Existing active tenant membership remains the admission boundary.
- Cross-tenant and hidden parent identifiers must not disclose existence.
- Course response fields: id, code, title, state.
- Lesson response fields: id, code, title, position, state.
- Default page size: 20.
- Maximum page size: 100.
- Empty states are truthful empty collections; no fabricated academic values.
- Current canonical six-operation OpenAPI file remained unchanged in Task80A.

## Exact architecture provenance

Reviewed architecture HEAD: `0eeb107e064bb99669c7ea0e94d52654df4687fe`

Exact changed-file count: `3`.

Exact file/blob bindings:

1. `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md`
   - blob: `5ad991af630f107a72edcd9d6e30af26eb78d4db`
2. `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`
   - blob: `78f8f83cecd881651466b9c092f1454060968a9a`
3. `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`
   - blob: `03b1143e698eeff778bbb1aef84cdbe9f99c0415`

The provider packet is permanently bound to those three blobs. Closeout/readiness documentation created after merge is evidence only and must not replace the reviewed architecture packet.

## Pre-merge evidence

- CI run `31402531075`: `SUCCESS`.
- Compose smoke/restore run `31402530817`: `SUCCESS`.
- Exact diff: three documentation files only.
- Runtime/API/OpenAPI canonical schema diff: none.

## Merge evidence

PR: `#35`.

Merge method: race-safe squash with expected head SHA.

Expected/reviewed head: `0eeb107e064bb99669c7ea0e94d52654df4687fe`.

Merged commit on `main`: `813db363411f857d35bc5774b7856cdc71b49e41`.

PR state after merge: `CLOSED / MERGED`.

## Post-merge evidence

Post-merge CI on `main@813db363411f857d35bc5774b7856cdc71b49e41`:

- run `31402907652`: `SUCCESS`;
- backend full tests: `SUCCESS`;
- frontend checks/build: `SUCCESS`;
- migration/OpenAPI/runtime-image checks: `SUCCESS`.

Post-merge Compose smoke/restore:

- run `31402907634`: `SUCCESS`;
- PostgreSQL RLS and connection-reuse tests: `SUCCESS`;
- backup/restore verification: `SUCCESS`.

## Provider transport blocker

Blocker classification: `PENDING_PROVIDER_TRANSPORT`.

This is an operational transport/tooling blocker only. It is not a Qwen or Claude architecture verdict and is not a substantive architecture finding.

### Permitted-path checks and evidence

1. Provider connector discovery
   - command/query: plugin discovery for `Qwen OR Claude OR Anthropic`.
   - result: no Qwen, Claude, or Anthropic connector was available; unrelated Vercel/Base44 suggestions were returned only.
   - disposition: unusable as substitutes; no provider call made.
2. Repository provider-runner discovery
   - command/query: GitHub code search `claude qwen runner browser` in `mytest19861986/codesho-test`.
   - result: `results=[]`, connector error `null`.
3. Claude-specific runner discovery
   - command/query: GitHub code search `claude_brave` in `mytest19861986/codesho-test`.
   - result: `results=[]`, connector error `null`.
4. Qwen-specific runner discovery
   - command/query: GitHub code search `qwen` in `mytest19861986/codesho-test`.
   - result: `results=[]`, connector error `null`.
5. Available GitHub connector capability inspection
   - result: GitHub actions can read/write repository state and CI evidence but expose no external Qwen/Claude model-session invocation.

No command above failed due to architecture content. The blocking outcome is absence of a permitted provider transport in the current execution environment.

### Operational safety rules while blocked

- do not fabricate a provider response;
- do not use unrelated provider services as substitutes;
- do not bypass quotas, authentication, browser/profile locks, or attachment restrictions;
- do not retry aggressively or disrupt a shared authenticated browser/profile;
- Qwen must run first on the exact three-blob packet;
- Claude must run only after a real Qwen PASS and must receive the same packet plus Qwen's complete response.

## Resumable provider checkpoint

Checkpoint state: `TASK80A_PROVIDER_GATE_READY_TO_RESUME`.

Resume prerequisites:

1. A permitted, authenticated Qwen transport becomes available.
2. It can receive complete, untruncated contents of the three fixed architecture blobs.
3. No architecture blob or reviewed architecture HEAD is changed before Qwen review.

Resume procedure:

1. Re-bind the three blob SHAs listed above.
2. Send `QWEN_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_REVIEW_01_V1` with the complete three-file packet.
3. Accept Qwen PASS only when `CONTENT_RECEIVED_COMPLETE=YES`, `P0_COUNT=0`, `P1_COUNT=0`, `OPEN_BLOCKERS=0`, and `IMPLEMENTATION_RECOMMENDATION=READY_FOR_CLAUDE`.
4. If Qwen fails or blocks, stop before Claude and return the real result to Commander.
5. If Qwen passes, send `CLAUDE_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_HARD_GATE_01_V1` sequentially using the identical three-file packet plus Qwen's complete response.
6. Accept Claude PASS only when `CONTENT_RECEIVED_COMPLETE=YES`, `P0_COUNT=0`, `P1_COUNT=0`, `OPEN_BLOCKERS=0`, and `IMPLEMENTATION_RECOMMENDATION=READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.
7. Only after both real PASS results may Commander authorize a separately bounded runtime successor.

## Required provider sequence

### Qwen

Prompt ID: `QWEN_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_REVIEW_01_V1`.

Current status: `PENDING_PROVIDER_TRANSPORT`.

### Claude

Prompt ID: `CLAUDE_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_HARD_GATE_01_V1`.

Current status: `BLOCKED_ON_QWEN_AND_PROVIDER_TRANSPORT`.

## Runtime successor gate

No runtime/API/OpenAPI implementation successor may start until both real provider reviews complete and the Claude PASS condition above is satisfied.

While provider transport is unavailable, only documentation/readiness/provenance work that cannot change the reviewed architecture packet is permitted.

## Final disposition at this checkpoint

Architecture documentation is merged and post-merge green.

Provider packet provenance is fixed and audited.

Provider transport absence is recorded with commands/results and a resumable checkpoint.

Runtime implementation remains blocked by sequential provider hard gates.

No Release, Deployment, Production, or protected `codesho` action occurred.
