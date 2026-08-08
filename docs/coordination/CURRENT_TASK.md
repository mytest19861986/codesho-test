# Current Task: SPRINT1-IDENTITY-PASSCODE-CHANGE-CLEANUP-HARDENING-76A

- Owner: Codex, directed by Commander AI.
- Status: `IMPLEMENTED / FOCUSED_GATES_PASS / FULL_SUITE_ONE_UNRELATED_FAILURE`
- Base SHA: `cb967c26e0faf9a5868e9adc74d59a09c6a42b99`.
- Branch: `codex/task76a-passcode-change-cleanup-hardening`.
- Scope: tenant-scoped passcode-change challenge cleanup hardening only; no
  migration, beat schedule, global fan-out, or protected-repository promotion.
- Current checkpoint: cleanup settings are now represented in `.env.example`
  and validated as bounded configuration at settings load. Existing cleanup
  orchestration and tenant task code were preserved because inspection found
  no confirmed defect in those paths.
- Verification: focused cleanup tests pass (`7 passed`); related tests pass
  (`22 passed`); Ruff, Django check, migration check, compileall, and
  `git diff --check` pass. Full backend suite is `213 passed, 49 skipped, 1
  failed`: the unrelated OpenAPI canonical-byte test detects generated LF
  versus committed CRLF in `docs/openapi.yaml`, outside this task allow-list.
- Review blocker: required Claude prompt
  `CLAUDE_TASK76A_PASSCODE_CHANGE_CLEANUP_IMPLEMENTATION_REVIEW_01_V1` remains
  pending because Claude mediation is unavailable in this session.

- Owner: Codex, directed by Commander AI.
- Status: `COMPLETE / LOCAL_GATES_PASS / CI_COMPOSE_PASS / CLAUDE_PASS`.
- Base branch: `codesho-test/main`.
- Base SHA: `dca0800fd74fb3e852aacb9122e6c533538d2629`.
- Branch: `codex/task73b-openapi-contract-drift`.

## Goal

Eliminate OpenAPI contract drift through an isolated `drf-spectacular`
projection while preserving runtime URLs, auth, sessions, CSRF, cookies,
tenant middleware and business logic.

## Exact allow-list

1. `backend/config/openapi_schema.py`
2. `backend/config/openapi_urls.py`
3. `backend/config/settings/base.py`
4. `backend/tests/test_openapi_contract.py`
5. `docs/openapi.yaml`
6. `.github/workflows/ci.yml`
7. `docs/coordination/CURRENT_TASK.md`
8. `docs/coordination/PROJECT_STATE.md`
9. `docs/coordination/CODEX_TO_COMMANDER.md`
10. `.github/workflows/compose-smoke.yml` (Commander-approved CI remediation)

No other file may change.

## Acceptance

- Generated schema is deterministic and exposes exactly six approved operations.
- Generated schema is byte-equal to `docs/openapi.yaml`; schema and Swagger
  are fail-closed for anonymous and non-staff users.
- Runtime/projection path names, callback identities and HTTP methods are
  parity-tested; unapproved endpoints are absent.
- Runtime CSRF, session, cookie, status and Retry-After behavior is unchanged.
- Ruff, MyPy, Django check, migration check, focused/full backend tests,
  schema validation and `git diff --check` pass.
- Claude implementation Review 02 passed with zero open blockers. Review 03's
  only P1 (real Compose execution) is resolved by successful remote execution;
  final evidence-closure Review 04 passed with zero open blockers.

## Remote evidence

- Commit: `264d85d06fc7c48c4eb2a721e69f53b58a57f7c5`.
- CI: `31078717976` — SUCCESS (backend and frontend).
- Compose smoke and restore: `31078717914` — SUCCESS.
- Documentation checkpoint CI: `31078984692` — SUCCESS.
- Documentation checkpoint Compose smoke and restore: `31078984491` — SUCCESS.
- Final Claude evidence-closure review:
  `CLAUDE_TASK73B_CI_COMPOSE_EVIDENCE_CLOSURE_REVIEW_04_V1` — PASS / 0 open
  blockers.
- Draft PR: `https://github.com/mytest19861986/codesho-test/pull/16` (Draft;
  Ready, merge and protected-repository promotion remain forbidden).

`FINAL_MARKER: CLAUDE_TASK73B_OPENAPI_CONTRACT_IMPLEMENTATION_REVIEW_02_V1`

## Authority and exclusions

Commit, normal branch push and Draft PR are authorized after final gates.
Direct-main, Ready, merge, force-push and branch deletion are forbidden.

No model, schema, migration, API/OpenAPI, UI, code/state-machine implementation,
PII/real data, account, credential, session, active membership, role, public
endpoint, email/SMS/OAuth/provider integration, Guardian/Recovery
implementation, deployment, Alpha, Production or protected `codesho`
promotion is authorized.
