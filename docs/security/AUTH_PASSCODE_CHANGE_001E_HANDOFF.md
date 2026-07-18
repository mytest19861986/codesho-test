# AUTH-PASSCODE-CHANGE-001E handoff

Status: implementation in progress; no commit or push is authorized before
the three required sequential Claude reviews and Commander disposition.

Scope is limited to lifecycle expiry, retention cleanup, tenant task support,
tests, migration/grants, and this runbook. No production schedule, UI, Alpha
activation, release, or protected-repository promotion is included.

## Commander fallback packet: Review 03 provider exception

Prompt ID: `CLAUDE_AUTH_PASSCODE_CHANGE_001E_TASK_RUNBOOK_REVIEW_03_V1`.
The provider supplied a complete finding-by-finding review but explicitly
refused the required completion marker. Commander selected fallback review and
forbade further Claude retries or marker workarounds.

Reviewed files and SHA-256:

- `backend/modules/identity/tasks.py`:
  `263775043957688A2DC0B2D40FA55E1E432A3912A269A90E2E1F33E6E8D5E31F`
- `backend/modules/platform_tenant/tasks.py`:
  `17B9A7BD2276C726A37B1E41DD0C5400C1EA95CE6BD98E20B8764A08F0328D1B`
- `backend/modules/identity/passcode_change_cleanup.py`:
  `66079627A4C12A9D594CDB2B1BB058155A232645F65E5B7AA2BCDB390A18C69B`
- `backend/modules/identity/migrations/0006_passcode_change_cleanup_function.py`:
  `EA6856E0F2A419B6795252E954DC00854D258799FB5D7416325F56D01BB0956A`
- `docs/security/AUTH_PASSCODE_CHANGE_001E_RUNBOOK.md`:
  `2823A1CFC7D6B04442C3C24CD260C1EEF50D44118F7D4B932BB0B02E35BA5A74`

Faithful Review 03 findings and Codex dispositions:

1. Low/Info: verify that `tenant_atomic` resets context on success and error.
   **REJECT_WITH_EVIDENCE.** `BaseTenantTask.__call__` requires a UUID
   `tenant_id` and invokes `tenant_atomic`; `tenant_atomic` wraps
   `transaction.atomic()`, calls PostgreSQL `set_config(..., true)`, stores a
   ContextVar token and resets it in `finally`. Existing focused task tests
   cover required ID, invalid ID, observed context and clean post-success
   context; the `finally` is deterministic for failure/retry paths.
2. Low: task relies on `current_tenant_id` rather than an explicit run
   argument. **ACCEPTED_NO_CHANGE.** This is the deliberate `BaseTenantTask`
   contract: it prevents `run()` from accepting an untrusted replacement tenant
   ID after the wrapper has established the atomic context.
3. Info: retry/concurrency safety was not visible in the initial packet.
   **REJECT_WITH_EVIDENCE.** Cleanup validates batch input `1..500`, locks
   expiry and retention candidates with `FOR UPDATE SKIP LOCKED`, makes the
   state/digest transition atomic, and uses stable expiry audit IDs and
   idempotency keys. A duplicate cannot reselect an already terminal row.
4. Pass: production scheduling is absent. **ACCEPTED_NO_CHANGE.** No Celery
   beat schedule, periodic task, cron or production activation was added.
5. Medium: review asserted the runbook ceiling was not enforced in the visible
   task wrapper. **REJECT_WITH_EVIDENCE.** The task passes `batch_size` only to
   `cleanup_passcode_change_challenges`, which rejects every value outside
   `1..500`; the operational default is
   `PASSCODE_CHANGE_CLEANUP_BATCH_SIZE=100`. The restricted function repeats
   the same `1..500` bound and uses `LIMIT p_batch_size`.
6. Info: retention/legal boundary needed code evidence. **REJECT_WITH_EVIDENCE.**
   The restricted function deletes only `consumed`, `revoked`, or `expired`
   rows with a terminal timestamp at least 30 days old; the runbook preserves
   the Legal/Production gate.
7. Pass: Pepper compromise remains non-automated. **ACCEPTED_NO_CHANGE.**

Additional security evidence:

- Runtime has no direct DELETE/TRUNCATE grant from identity migration 0004;
  migration 0005 limits runtime UPDATE columns. The sole retention delete is
  the `codesho_migrator`-owned `SECURITY DEFINER` function with fixed
  `pg_catalog, codesho, pg_temp` search path, tenant GUC equality check,
  `PUBLIC` revoke and runtime-only EXECUTE.
- The implementation stores no passcode, challenge secret, digest, cookie or
  raw tenant/security signal in logs, audit metadata, task result, or runbook.
- Runbook now documents no scheduling, approved per-tenant invocation,
  monitoring, non-destructive rollback, Pepper-revocation non-automation and
  the Legal/Production retention gate.

Focused checks: `python -m pytest backend/tests/test_passcode_change_cleanup.py
backend/tests/test_tasks.py -q` => `9 passed`. Full local gate before packet:
Ruff, MyPy (41 sources), migration-drift, Django check and `pytest -q` =>
`129 passed, 27 skipped`; `git diff --check` passed. PostgreSQL-specific
migration/RLS/connection-reuse and Compose gates require the post-authorization
remote CI path because local Docker is unavailable.

Status: `COMMANDER_FALLBACK_REVIEW_PENDING`. No commit or push is authorized.
