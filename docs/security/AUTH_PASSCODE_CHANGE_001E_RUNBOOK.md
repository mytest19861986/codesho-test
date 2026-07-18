# AUTH-PASSCODE-CHANGE-001E lifecycle runbook

The cleanup task is deliberately unscheduled in production. An approved operator
enqueues `identity.cleanup_passcode_change_challenges` separately for each tenant
with `tenant_id` and an optional batch size of at most 500. It uses PostgreSQL
time, locks no more than 100 rows by default with `SKIP LOCKED`, and is safe to
retry or run concurrently.

Expired active rows become `expired`, lose their digest in the same transaction,
and receive a bounded idempotent audit event. Retention removes only terminal
rows whose terminal timestamp is at least 30 days old through the restricted
database function; active rows are never deleted.

Monitor each approved run for expired/deleted counts, failed task executions,
database errors, and audit-append failures; alert on repeated failures without
including a challenge selector, digest, cookie, tenant-security signal, or
passcode in logs. For rollback, first stop enqueuing the task and retain the
function, terminal metadata, and immutable audit evidence. Do not restore a
digest, reactivate a terminal challenge, or delete the migration in Production.

Do not automate Pepper-compromise handling. Disable affected authentication
flows, preserve evidence, rotate the Pepper under a separately approved incident
procedure, and use the existing bounded pepper-rotation audit reason. Legal must
approve any production change to the 30-day metadata retention period.
