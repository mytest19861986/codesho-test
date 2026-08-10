# Codesho Active Gate

Status: `TASK80A_VALIDATED / PROVIDER_TRANSPORT_BLOCKED / RUNTIME_SUCCESSOR_BLOCKED`

This file is the concise operational pointer for the current Codesho execution state. Historical sections in `CURRENT_TASK.md` and `PROJECT_STATE.md` remain evidence and may be stale; they must not override this active gate.

## Current validated main

- Repository: `mytest19861986/codesho-test`
- Validated main before this docs-only checkpoint: `38d84c88fd76c391b6b75b5a195b43d19c4524d9`
- Task80A: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`
- Task80A state: `ARCHITECTURE MERGED / CLOSEOUT MERGED / POST-MERGE GREEN`
- Runtime/API/OpenAPI implementation successor: `BLOCKED`

## Immutable provider review packet

Provider reviews must use the exact three reviewed Task80A blobs below, not later closeout revisions:

1. `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md`
   - blob: `5ad991af630f107a72edcd9d6e30af26eb78d4db`
2. `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`
   - blob: `78f8f83cecd881651466b9c092f1454060968a9a`
3. `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`
   - blob: `03b1143e698eeff778bbb1aef84cdbe9f99c0415`

Reviewed architecture HEAD: `0eeb107e064bb99669c7ea0e94d52654df4687fe`.

## Validation evidence

Architecture and closeout evidence is recorded in `TASK80A_COURSE_LESSON_READ_CONTRACT.md`.

Latest final evidence merge on main before this pointer:

- merge: `38d84c88fd76c391b6b75b5a195b43d19c4524d9`
- post-merge CI: `31405071954` — `SUCCESS`
- post-merge Compose: `31405071933` — `SUCCESS`
- backend full tests: `SUCCESS`
- canonical OpenAPI parity: `SUCCESS`
- PostgreSQL RLS / connection reuse: `SUCCESS`
- backup create / restore / verify: `SUCCESS`

## Provider transport blocker

Classification: `PENDING_PROVIDER_TRANSPORT`.

This is an operational transport/tooling blocker only. It is not a provider verdict or architecture defect.

Checked permitted paths:

- plugin discovery for `Qwen OR Claude OR Anthropic`: no direct Qwen/Claude/Anthropic connector available;
- repository search for `claude qwen runner browser`: no usable result;
- repository search for `claude_brave`: no usable result;
- repository search for `qwen`: no usable result;
- available GitHub connector exposes repository/PR/Actions operations but no Qwen/Claude model-session invocation.

Do not fabricate provider responses, substitute unrelated providers, bypass quota/authentication/browser restrictions, or disrupt shared authenticated profiles.

## Resumable sequential provider gate

Checkpoint: `TASK80A_PROVIDER_GATE_READY_TO_RESUME`.

1. Obtain a permitted authenticated Qwen transport.
2. Re-bind the three immutable blobs above.
3. Run `QWEN_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_REVIEW_01_V1` with complete untruncated contents.
4. Qwen PASS requires `CONTENT_RECEIVED_COMPLETE=YES`, `P0_COUNT=0`, `P1_COUNT=0`, `OPEN_BLOCKERS=0`, and `IMPLEMENTATION_RECOMMENDATION=READY_FOR_CLAUDE`.
5. Only after real Qwen PASS, run `CLAUDE_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_HARD_GATE_01_V1` with the identical packet plus Qwen's complete response.
6. Claude PASS requires `CONTENT_RECEIVED_COMPLETE=YES`, `P0_COUNT=0`, `P1_COUNT=0`, `OPEN_BLOCKERS=0`, and `IMPLEMENTATION_RECOMMENDATION=READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.
7. Only after both real PASS results may Commander define a separately bounded runtime successor with explicit Acceptance Criteria.

## Guardrails

No runtime/API/OpenAPI canonical schema work may start while this gate is active.

No Release, Deployment, Production, or protected `codesho` action is authorized.
