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

Checked permitted paths in the Commander session:

1. Installed/available plugin discovery for `Qwen`, `Claude`, and `Anthropic`: no direct provider connector was available.
2. GitHub repository search for a checked-in `Qwen`/`Claude` runner, browser bridge, or provider transport: no usable runner/bridge was found.
3. Available GitHub connector capabilities do not invoke external Qwen or Claude model sessions.
4. No verdict may be inferred from Commander preflight analysis, CI, Compose, or absence of findings.

Operational rules while blocked:

- do not fabricate a provider response;
- do not use unrelated provider services as substitutes;
- do not bypass quotas, authentication, browser/profile locks, or attachment restrictions;
- do not retry aggressively or disrupt a shared authenticated browser/profile;
- Qwen must run first on the exact three-blob packet;
- Claude must run only after a real Qwen PASS and must receive the same packet plus Qwen's complete response.

## Required provider sequence

### Qwen

Prompt ID: `QWEN_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_REVIEW_01_V1`.

PASS requires:

- `CONTENT_RECEIVED_COMPLETE=YES`;
- `P0_COUNT=0`;
- `P1_COUNT=0`;
- `OPEN_BLOCKERS=0`;
- `IMPLEMENTATION_RECOMMENDATION=READY_FOR_CLAUDE`.

Current status: `PENDING_PROVIDER_TRANSPORT`.

### Claude

Prompt ID: `CLAUDE_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_HARD_GATE_01_V1`.

Claude must run sequentially only after Qwen PASS on the same exact architecture packet.

PASS requires:

- `CONTENT_RECEIVED_COMPLETE=YES`;
- `P0_COUNT=0`;
- `P1_COUNT=0`;
- `OPEN_BLOCKERS=0`;
- `IMPLEMENTATION_RECOMMENDATION=READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.

Current status: `BLOCKED_ON_QWEN_AND_PROVIDER_TRANSPORT`.

## Runtime successor gate

No runtime/API/OpenAPI implementation successor may start until both real provider reviews complete and the Claude PASS condition above is satisfied.

While provider transport is unavailable, only documentation/readiness/provenance work that cannot change the reviewed architecture packet is permitted.

## Final disposition at this checkpoint

Architecture documentation is merged and post-merge green.

Provider packet provenance is fixed and audited.

Runtime implementation remains blocked by sequential provider hard gates.

No Release, Deployment, Production, or protected `codesho` action occurred.
