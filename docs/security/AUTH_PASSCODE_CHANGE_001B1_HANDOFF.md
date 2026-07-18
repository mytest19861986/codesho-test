# AUTH-PASSCODE-CHANGE-001B1 Foundation Handoff

Status: `CI_ROLE_REMEDIATION_IN_PROGRESS`

## CI role remediation 001

Commander authorized `AUTH-PASSCODE-CHANGE-001B1-CI-FIX-001` from base
`448617225243adf26c04587354cebf6079c9dc0c`. The resolved orchestration files
are `.github/workflows/ci.yml` and `.github/workflows/compose-smoke.yml`.

Before this remediation, the failing commands use the runtime role for the
Django test lifecycle:

- CI: `DATABASE_URL="$DATABASE_RUNTIME_URL" pytest --reuse-db ...`
- Compose test container: `DATABASE_URL=postgresql://codesho_runtime:...`

Both will select the existing migrator *test* URL only for Django test database
creation, migration, flush, and teardown. Runtime test URLs stay separately
available to explicit privilege/RLS tests; application and Compose services
continue to use their existing runtime URLs. No database URL is logged.

Resolved owner paths before implementation:

- Model app: `backend/modules/identity/models.py`
- Migration app: `backend/modules/identity/migrations/0004_passcodechangechallenge.py`
- Cryptographic helper: `backend/modules/identity/challenge.py`
- Focused tests: `backend/tests/test_passcode_change_challenge.py` and
  `backend/tests/test_passcode_change_challenge_postgres.py`

`rg` found exactly one `PasscodeCredential` model definition, in the identity
app. No ownership ambiguity exists.

This slice is dormant foundation only. It does not add issuance, completion,
HTTP cookies, URLs, audit allow-list changes, Redis controls, cleanup work,
session mutation, credential replacement, or frontend behavior.

## Claude migration review 01 disposition

Prompt ID: `CLAUDE_AUTH_PASSCODE_CHANGE_001B1_MIGRATION_REVIEW_01_V1`.

- P0 accepted: migration documents the existing transaction-scoped
  `set_config(..., true)` tenant context and rejects a superuser/BYPASSRLS
  runtime role before applying RLS.
- P1 accepted: table ownership is pinned to `codesho_migrator`; the HMAC-SHA-256
  digest is limited to 32 bytes in model state and PostgreSQL SQL.
- P1 confirmed: Django creates per-FK indexes unless `db_index=False`; this
  model does not disable them. PostgreSQL CI verifies the resulting contract.
- P2 accepted as a future issuance invariant: this dormant slice stores the
  credential version supplied by a future locked issuance transaction; it does
  not add a trigger or active issuance path.
- P3 accepted: PostgreSQL-specific RLS/grant/TTL tests are intentionally
  skipped locally without PostgreSQL and required on the final CI/Compose gate.

## Claude crypto review 02 disposition

Prompt ID: `CLAUDE_AUTH_PASSCODE_CHANGE_001B1_CRYPTO_REVIEW_02_V1`.

- Verdict: `APPROVE`; no P0 or P1 findings.
- P2 documented: a removed Pepper fails closed with `ImproperlyConfigured`,
  and malformed internal secret bytes raise `ValueError`. A boundary introduced
  in a later authorized slice must normalize either condition to authentication
  failure. This dormant helper now documents that contract and tests unknown
  Pepper failure.
- P3 confirmed: selector generation uses UUID4, secret generation uses
  `secrets.token_bytes(32)`, and the helper has no logging.

The raw Claude prompts/responses are retained outside the repository. No
Claude retry is pending for either completed review packet.

## Local verification

- Focused foundation suite: `8 passed, 5 skipped`.
- Full backend suite: `67 passed, 21 skipped`.
- Ruff, MyPy, migration drift, OpenAPI validation, and `git diff --check` pass.
- Frontend lint, typecheck, and production build pass.
- PostgreSQL-only tests are skipped locally because Docker Desktop's Linux
  daemon is unavailable; exact PostgreSQL migration/RLS/grant/TTL evidence is
  required from the final CI and Compose workflows.

The next step is a scoped commit, push to `codesho-test/main`, and exact-SHA CI
and Compose verification.
