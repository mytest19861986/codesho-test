# Tenant-Safe Security Cleanup Scheduling Architecture

## Decision

Recommend Option C: a database-authoritative, bounded work-claim model in a
future implementation task, with an approved control-plane eligibility query,
short-lived database leases, and one explicit tenant task per claimed unit.
The scheduler may claim at most a bounded page of eligible tenant work and may
enqueue only the claimed units. The worker remains the sole component allowed
to execute cleanup, and every task carries exactly one validated `tenant_id`.

This document is an architecture decision only. It does not add a scheduling
table, lease code, Celery Beat, a queue, a migration, or production behavior.

## Context

Task76A established tenant-scoped passcode-change cleanup. The current task
`identity.cleanup_passcode_change_challenges` inherits `BaseTenantTask`, which
rejects a missing or invalid UUID and establishes `tenant_atomic` before
calling `cleanup_current_tenant`. Cleanup itself uses database-authoritative
time, bounded batches, row locks with `skip_locked`, and atomic security audit
updates. No periodic schedule or global cleanup task exists.

## Current Guarantees

- A cleanup invocation operates on one explicit tenant only.
- Ambient, missing, malformed, or default tenant context fails closed.
- Worker execution is tenant-scoped and remains protected by PostgreSQL/RLS.
- Work is bounded by the existing cleanup batch-size limit.
- Audit and cleanup state changes remain atomic.
- No raw passcodes, digests, credentials, or sensitive PII enter scheduling
  payloads, logs, metrics, or coordination documents.
- No Production, real-user, Ready, merge, or protected-repository action is
  authorized by this decision.

## Threat Model

The design defends against a compromised or duplicated scheduler, stale or
deleted tenants, broker redelivery, worker retries, two workers processing the
same tenant, unbounded fan-out, retry storms, stale leases, clock skew,
cross-tenant queries, privilege escalation through scheduler payloads, and
secret leakage through operational metadata. Celery is treated as at-least-once
delivery; exactly-once delivery is never a correctness assumption.

## Considered Architectures

### Option A

A central scheduler enumerates tenants and dispatches one explicit task per
tenant. It is simple for a small system, but a scheduler crash or compromise
can repeatedly enumerate and flood the broker. Without a durable claim, two
schedulers duplicate work and fairness/backpressure are difficult to prove.

### Option B

An external control plane supplies per-tenant triggers. This gives strong
administrative separation, but introduces an additional availability and
authorization boundary, requires a trustworthy tenant eligibility feed, and
does not by itself solve duplicate delivery, leases, backlog fairness, or
bounded retries.

### Option C

A database-authoritative work-claim mechanism selects eligible maintenance
units in bounded pages, claims them with a short lease and ownership token,
then dispatches one explicit tenant task per claim. PostgreSQL provides the
shared ordering, row locking, time authority, and recovery semantics. The
scheduler never performs cleanup and cannot create an unbounded fan-out.

### Option D

A per-tenant queue or a Redis-only lease was considered and rejected. It adds
queue and lifecycle complexity, makes durable eligibility and recovery harder,
and would make Redis clock/eviction behavior part of a security correctness
boundary. Redis/Celery remains a delivery mechanism, not the source of truth.

## Decision Matrix

| Criterion | A: enumerate/dispatch | B: external triggers | C: DB claim + lease | D: Redis-only/per-tenant queues |
|---|---|---|---|---|
| Isolation/security | medium | high if feed is trusted | high, explicit claims | medium |
| Correctness/concurrency | weak without claims | medium | high with DB locks | medium |
| Backpressure/fairness | weak | medium | high, bounded ordering | medium |
| Failure recovery | medium | medium | high, expiry/reclaim | weak-medium |
| Operational complexity | low | high | medium | high |
| Auditability | medium | high | high | medium |
| Small-system maintainability | high | low-medium | high | low |

## Chosen Architecture

Future Task77B must implement a bounded database work-claim path. The claim
source is an approved control-plane/database projection of active, eligible
tenants; it is not request context, the first tenant, a default tenant, or
worker-local state. A scheduler transaction selects a bounded page ordered by
`next_due_at` and a stable tenant key, skips currently leased rows, and claims
each row with a unique ownership token and database `CURRENT_TIMESTAMP`.

The scheduler commits claims before publishing. A publish failure leaves the
claim recoverable after lease expiry. A successful publish carries only the
opaque, approved tenant UUID and a claim identifier; the worker revalidates
tenant existence, enabled state, claim ownership, and freshness before running.

## Tenant Discovery Contract

Only the approved control-plane/database component may discover eligibility.
Discovery is read-only with respect to tenant business data and must use a
role explicitly authorized for the tenant registry projection. It must apply
active/enabled and due-time predicates, stable ordering, a hard page limit, and
no implicit tenant. Deleted, disabled, or stale tenants are skipped or marked
non-eligible without dispatch. A tenant UUID is not accepted from an end-user
request as scheduler authority.

## Dispatch Contract

One dispatch unit contains exactly one valid `tenant_id`, one claim identifier,
and a non-secret task version. It contains no wildcard, nullable tenant, raw
credential, digest, passcode, session secret, or PII. The scheduler emits no
more than the configured page size per cycle and publishes only committed
claims. A task name never contains a tenant UUID or security data.

## Worker Contract

The worker remains `BaseTenantTask`-based. It validates the UUID, establishes
tenant context inside `tenant_atomic`, rechecks claim ownership and tenant
eligibility, and invokes the existing bounded cleanup for that tenant only.
The worker never enumerates tenants and never calls a global cleanup function.
Claim completion is recorded only after successful cleanup; stale or missing
claims fail closed and are safe to redeliver.

## Concurrency / Idempotency Contract

Database row locking and a unique active-claim constraint prevent two live
claims for the same tenant/work period. A scheduler restart or duplicate
delivery is harmless: the claim token and status are checked transactionally.
Worker cleanup remains authoritative for per-row idempotency, deterministic
audit identifiers, and `skip_locked` behavior. Duplicate claimants exit or
redeliver after lease expiry; they do not bypass ownership checks.

Leases use an opaque random ownership token, database-authoritative expiry,
and a bounded renewal only while the worker is making progress. An abandoned
lease is reclaimable after expiry. No wall-clock comparison from application
hosts is used for correctness.

## Retry / Backpressure Contract

Each cycle has hard limits for tenants considered, claims created, concurrent
cleanup tasks, and attempts per claim. Transient database/broker failures use
bounded exponential backoff with jitter. Invalid tenant IDs, deleted tenants,
authorization failures, and malformed claims are non-retryable and go to
reviewable dead/poison handling without exposing payload secrets. Queue
pressure pauses or reduces claiming; it never causes unlimited enqueue.

Ordering is oldest-due-first with a stable tenant-key tie-breaker and a bounded
per-tenant batch. This provides fairness so one noisy tenant cannot starve the
rest. Backlog age, saturation, and retry thresholds are operational signals,
not reasons to fail open.

## Observability Contract

Emit non-sensitive counters/timings for cycle result, tenants considered,
claims created/skipped/reclaimed, task success/failure, expired/deleted counts,
backlog age, retries, and dead/poison work. Labels may include task version and
coarse outcome, but never credentials, digests, passcodes, secrets, or sensitive
PII. Durable audit is reserved for security-relevant claim authorization,
manual trigger, terminal failure, and kill-switch changes; routine polling and
successful duplicate suppression remain metrics/logs to avoid audit explosion.

## Failure Matrix

| Failure | Required behavior |
|---|---|
| Database unavailable | Do not claim or dispatch; bounded retry and alert. |
| Broker unavailable | Keep committed claims recoverable; bounded retry, then reclaim. |
| Task timeout | Lease expires/reclaims; bounded retry; no fail-open behavior. |
| Malformed tenant ID | Reject permanently, record non-sensitive poison outcome. |
| Tenant missing/disabled | Skip safely and close/release claim. |
| Audit failure | Atomic worker transaction fails; retry only if classified transient. |
| Partial cleanup failure | Roll back the unit and use bounded retry; never mark complete. |
| Scheduler crash | Claims recover after database lease expiry. |

## Kill Switch

The future implementation must have an independently controlled, default-safe
kill switch that stops new claims and dispatches. It must not disable explicit
manual cleanup for a known authorized tenant, and it must not cancel already
running work. Existing claims finish or expire under the normal bounded policy.
Changing the switch is durable, audited, authorized, and observable.

## Manual Fallback

An operator may request cleanup for one known, validated tenant UUID through an
authenticated control-plane path. The path must authorize the operator,
revalidate tenant state, create one bounded explicit claim/task, and produce a
durable audit event. There is no cleanup-all command, wildcard tenant, or
request-context fallback. The same worker contract and RLS protections apply.

## RLS / Database Roles

The scheduler's discovery role is a narrowly granted control-plane role over
the approved tenant eligibility projection; it is not the runtime worker role
and does not grant access to tenant secrets. The runtime worker role remains
subject to FORCE RLS and receives tenant context through `tenant_atomic` before
tenant queries. No scheduler design may require workers to bypass RLS. Any
migrator-only DDL role remains separate and is not used by scheduler or worker.

## Security Considerations

The broker is untrusted delivery infrastructure. Claim ownership, eligibility,
tenant state, and time are revalidated in PostgreSQL. Payload minimization,
bounded fan-out, explicit authorization, fail-closed errors, and immutable
security audit boundaries limit blast radius. No secrets or raw provider data
are introduced.

## Rejected Alternatives

Option A is rejected as the primary pattern because enumeration plus enqueue
has no durable claim/backpressure boundary. Option B is rejected as the sole
mechanism because an external trigger does not solve leases and duplicate
delivery. Option D is rejected because Redis-only coordination would make
eviction and non-authoritative clocks security-critical.

## Follow-up Tasks

- **Task77B — Scheduling foundation implementation:** implement only the
  approved claim schema/path, bounded scheduler adapter, explicit dispatch,
  kill switch, and worker claim revalidation; no product or real-user scope.
- **Task77C — Concurrency/failure/backpressure verification:** exercise leases,
  duplicate schedulers/deliveries, retries, fairness, saturation, and poison
  handling against real PostgreSQL/Redis/Compose.
- **Task77D — Operational evidence/deployment-readiness validation:** validate
  metrics, audit volume, alerts, rollback/kill-switch operations, restore,
  and deployment evidence without enabling Production or real users.

## Explicit Non-Goals

No scheduler, Celery Beat, periodic decorator, queue, Redis service, table,
migration, worker change, settings change, deployment, merge, Production,
real-user onboarding, public signup, Guardian/Recovery, payment, SMS, video,
object storage, or provider integration is included.
