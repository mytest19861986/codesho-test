# Task67A adult signup review summary

## Scope

This checkpoint covers only the internal synthetic-data adult age-attestation
foundation. It creates no account, credential, membership, session, frontend
route, Guardian/Recovery path, real-user activation, or deployment setting.

## Codex implementation review

| Area | Result |
|---|---|
| Environment boundary | `disabled` is the default; production settings reject `internal_test`. |
| Data minimization | Only tenant UUID, synthetic subject UUIDv4, constant status/source, policy version, UTC timestamp, and audit UUID are persisted. |
| Explicit consent | The exact JSON contract requires a real boolean `true`; missing, numeric, defaulted, or extra fields fail closed. |
| Prohibited data | Birth date/year, numeric age, identity/national identifiers, Guardian data, raw IP, payloads, and free text are absent from the model and rejected as request extensions. |
| Abuse boundary | Redis keys use HMAC-anonymous subject and client-IP dimensions; Redis or HMAC failure blocks the endpoint. |
| Atomicity/idempotency | Tenant+subject+policy uniqueness and one outer database transaction bind the attestation to its accepted audit append. |
| Immutability | Application methods and a PostgreSQL trigger reject mutation; runtime update/delete/truncate privileges are revoked. |
| Tenant boundary | The exact pre-auth path resolves an active tenant; evidence uniqueness is tenant-scoped. |
| API claim | OpenAPI states explicitly that no account, credential, membership, or session is created. |

No unresolved issue was found in the local Codex review after remediation of
strict boolean/UUID validation, rate-limit backend handling, policy-version
length validation, and manual OpenAPI validation.

## Verification evidence

```text
Ruff: PASS
MyPy strict: PASS (46 source files)
Module boundaries: PASS
Django system check: PASS
Migration drift: PASS
Empty SQLite migration: PASS
Generated OpenAPI validation: PASS
Versioned docs/openapi.yaml validation: PASS
Focused Task67A tests: PASS (27 passed, 2 PostgreSQL-only skipped locally)
Full backend suite: PASS (189 passed, 32 PostgreSQL-only skipped locally)
Backend coverage: PASS (87.04%, gate 80%)
Frontend UI policy tests: PASS (10)
Frontend policy/lint/typecheck/build: PASS
git diff --check: PASS
```

The initial frontend install attempt failed because the environment forced an
unwritable `/root/.npm` cache and left an incomplete `node_modules`. The
incomplete directory was moved to `/tmp`; `npm ci` and all frontend checks
then passed with an explicit `/tmp` cache. No tracked frontend file changed.

## Remaining gates

- PostgreSQL migration, trigger, runtime-grant, and real audit-function tests
  require the repository CI service because Docker/PostgreSQL is unavailable
  locally.
- The repository requires sequential Claude security/privacy/database review
  before Merge. No Claude review was available in this execution environment,
  so the checkpoint is explicitly `NOT_CLAUDE_VERIFIED`.
- Real-user Legal approval, Ready for Review, Merge, Deployment, and protected
  repository promotion remain unauthorized.
