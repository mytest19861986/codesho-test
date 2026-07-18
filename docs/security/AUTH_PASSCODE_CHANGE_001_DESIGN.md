# AUTH-PASSCODE-CHANGE-001A - Forced Passcode Change Design

Status: `AUTHORIZED_ANALYSIS_ONLY`

Base: `db4e778794e82f0dfd75088c34b64c847e7368e5`

This document specifies the future backend contract for the mandatory
passcode-change state. It authorizes no source code, migration, route, test,
package, commit, or release. The implemented login contract remains the
authority until `AUTH-PASSCODE-CHANGE-001B` is explicitly assigned.

## Scope and non-negotiable invariants

- A challenge is issued only after the current passcode has been verified for
  the exact tenant member and credential.
- Its lifetime is exactly 600 seconds; it is one-time, opaque,
  replay-resistant, tenant-bound, credential-bound, purpose-bound, and
  credential-version-bound.
- PostgreSQL is the authoritative challenge store. There is exactly one active
  challenge per credential; a successful new issuance atomically revokes the
  previous active challenge.
- The browser holds the challenge selector and high-entropy secret only in a
  host-only, root-path-scoped `HttpOnly`, `Secure`, `SameSite=Lax` cookie.
  PostgreSQL stores a non-secret selector and only a versioned Pepper-HMAC
  digest, never the secret.
- Completion requires same-origin CSRF protection. No session is created
  before the passcode is changed successfully.
- Successful completion replaces the credential using Argon2id and the active
  Pepper, requires exactly six ASCII digits, advances the authentication epoch,
  invalidates prior sessions, clears the challenge cookie, and creates no
  session. A fresh login with the new passcode is required.
- No passcode or challenge secret may appear in logs, telemetry, an URL,
  exception text, audit payload, client storage, or a response body.
- Real Alpha release remains blocked until this design is implemented,
  security-reviewed, tested, and accepted in a separately authorized task.

## Existing contract and design boundary

The current login endpoint verifies an exact, case-sensitive username and six
ASCII-digit passcode. A valid credential with `must_change=true` results in
`403 passcode_change_required` and no authenticated session. Existing
`PasscodeCredential` already has `encoded_hash`, `pepper_id`,
`credential_version`, and `must_change`; `User.session_auth_epoch` invalidates
sessions whose stored epoch no longer matches. The audit ledger is immutable
and is appended through its restricted PostgreSQL function.

The change flow must not turn login, recovery, guardian, signup, OAuth, or a
client-side flag into a credential-change bypass. It is a new, narrowly scoped
pre-authentication protocol for a verified member who must change a credential.

## Threat model

| Threat | Required mitigation |
| --- | --- |
| Stolen browser cookie | Cookie is `HttpOnly`, `Secure`, host-only and `SameSite=Lax`; completion additionally requires CSRF. Its selector and opaque secret are never readable by application JavaScript. |
| Replay or parallel completion | A row lock, `active`/`consumed` state transition, version binding and atomic transaction allow exactly one success. Concurrent duplicates receive the same neutral terminal result without a second credential replacement. |
| Token database disclosure | Store a non-secret random selector and only HMAC(secret, versioned Pepper); use at least 256 bits of CSPRNG secret entropy; no plaintext secret or unsalted SHA-256 token hash is stored. |
| Cross-tenant use | Tenant context is established fail-closed inside `transaction.atomic()` before challenge or credential queries; every row is tenant-bound and covered by RLS. |
| Credential changed after issuance | Challenge records the credential version. Completion requires equality while holding the credential lock. Any mismatch is revoked/rejected. |
| Session fixation or stale session | No session precedes or is created by completion. On success, advance `session_auth_epoch`; middleware flushes old-epoch sessions. The user performs a fresh login after commit. |
| Passcode reuse | Under the credential lock, verify the proposed passcode against the current credential before replacement; equal values are rejected without consuming a valid challenge. |
| Online guessing and resource exhaustion | Reuse account/IP/device controls for issuance; add challenge-scoped completion limits. Redis is an accelerator/abuse gate only; PostgreSQL remains authoritative. Fail closed when a required abuse or audit dependency is unavailable. |
| Enumeration | Unknown, inactive, non-member, wrong-passcode, expired/revoked/missing challenge and digest mismatch do not disclose principal, challenge state, or token validity. External errors are deliberately coarse. |
| Audit or log disclosure | Audit records bounded event/reason codes and IDs/version only. It never contains passcode, secret, digest, cookie value, IP/device raw values, or request body. |
| Cleanup race | Expiry is enforced in completion from database time; bounded cleanup also transitions abandoned expired active rows to `expired`, clears their digest, appends idempotent audit evidence, then later deletes only old terminal rows. |

## Selected alternatives

| Decision | Selected design | Rejected alternative and reason |
| --- | --- | --- |
| Secret transport | HttpOnly host-only cookie | A body token exposes the bearer secret to JavaScript, client storage, browser history/telemetry mistakes, and accidental response handling. |
| Post-change authentication | Fresh login after a successful change | No session is emitted from the credential/audit transaction, avoiding a partial-success session. This is settled by Commander disposition; automatic post-change login is outside this design. |
| Authoritative storage | PostgreSQL | Redis-only loses durable one-time semantics, RLS/grant controls, and crash-safe revocation/consumption. Redis remains only an abuse-control dependency. |
| Stored verifier | Versioned Pepper-HMAC digest | Bare SHA-256 permits inexpensive offline guessing after database disclosure; Pepper-HMAC requires the protected server secret and supports rotation. |
| Active rows | One active challenge per credential | Multiple active rows enlarge replay surface and make supersession ambiguous. New issuance revokes the previous row atomically. |

## State machine

```text
none --successful must-change login--> active
active --successful must-change login--> revoked then replacement active
active --database time >= expires_at--> expired
active --successful completion transaction--> consumed
active --credential version mismatch / administrative invalidation--> revoked
revoked, expired, consumed --retention expiry--> deleted
```

Only `active` may enter `consumed`. `consumed`, `revoked`, and `expired` are
terminal and cannot become active. A completion with the same proposed
passcode leaves the challenge active until its expiry so the verified user can
choose a different passcode; rate limits still apply.

## API contract (future OpenAPI addition)

All endpoints are exact tenant-host paths, same-origin only, JSON only, and
use `credentials: "same-origin"`. No endpoint accepts or returns a challenge
selector or secret in JSON. Field names below are design contracts, not
implemented API.

### Existing `POST /api/v1/auth/passcode/login/` - issuance extension

The change flow adds no separate challenge-issuance endpoint and never asks
the browser to submit the current passcode twice. The existing login request
and its established tenant, CSRF, account/IP/device-abuse, exact-user, and
Argon2id/Pepper verification controls remain authoritative.

When the verified credential has `must_change=true`, the login transaction
locks the credential, revokes any active forced-change challenge, creates its
replacement, appends the bounded issuance audit event, and commits. The
response remains `403 passcode_change_required`, sets the challenge cookie,
and creates no session. A failed login, a login for another user, or an
ineligible login clears any pre-existing change cookie with matching cookie
attributes. The existing non-enumerating login failure contract is unchanged.

### `POST /api/v1/auth/passcode/change/complete/`

Preconditions: tenant host resolved; CSRF cookie/header valid; challenge cookie
present; body is `{ "newPasscode": "^[0-9]{6}$" }`. The request must not
include username, current passcode, challenge ID, or challenge secret.

Success: `204 No Content`, clear the challenge cookie, increment the auth
epoch, and create no session. The user must perform a new normal login with
the replacement passcode after the response commits.

External failures:

| Status | Code | Required behavior |
| --- | --- | --- |
| 400 | `invalid_request` | Invalid body or new passcode format. Do not consume challenge. |
| 401 | `challenge_invalid_or_expired` | Neutral missing, expired, revoked, consumed, digest-mismatch, wrong-tenant, or credential-version-mismatch result. Clear the cookie. |
| 409 | `passcode_same_as_current` | Proposed value verifies against current credential. Do not consume challenge; retain it until expiry so a different value can be submitted. |
| 403 | `csrf_failed` | CSRF validation failed. Do not consume challenge. |
| 429 | `try_again_later` | Neutral completion abuse limit; include `Retry-After`. |
| 503 | `authentication_temporarily_unavailable` | Required abuse, audit, or database dependency unavailable; no successful response and no partial credential update. Completion intentionally has no session dependency. |

`challenge_invalid_or_expired` deliberately does not distinguish terminal
state, token validity, tenant, or credential existence. The distinct 409
same-as-current result is authorized because the caller has already proven
possession of the challenge cookie and CSRF token.

## Cookie lifecycle

Cookie name (production): `__Host-codesho-passcode-change`.

- Set only from a successful `must_change` login with
  `v1.<challenge_selector>.<challenge_secret>`. The selector is a non-secret
  UUID or random identifier; the secret is at least 32 CSPRNG bytes and is
  base64url encoded. Both are cookie-only and neither may appear in JSON, a
  URL, telemetry, logs, audit metadata, or client storage. Set `Path=/`, no `Domain`,
  `HttpOnly`, `Secure`, `SameSite=Lax`, `Max-Age=600`, and `Expires` matching
  the exact server-issued expiry.
- The `__Host-` prefix requires host-only, secure, root-path scope; deployment
  must reject a configuration that cannot honor it.
- Overwrite it on replacement issuance, and clear it with matching attributes
  after success, terminal completion failure, logout, or an explicit cancelled
  flow. Browser expiry is not security enforcement; PostgreSQL time decides
  expiry.
- Never set it on a GET route, append it to a URL, expose it in JSON, copy it
  to CSRF/local/session storage, or log it. CSRF uses the existing separate
  Django CSRF cookie/header mechanism.

## PostgreSQL data model, RLS, and grants

Proposed table: `codesho.passcode_change_challenge`.

| Column | Constraint / purpose |
| --- | --- |
| `id uuid` | Primary key; opaque internal identifier, never sent to client. |
| `selector uuid` | Not null, unique non-secret random selector. It is cookie-only and is used with tenant and purpose to locate the candidate row before the Pepper version is known. |
| `tenant_id uuid` | Not null; FK to tenant; tenant isolation key. |
| `credential_id uuid` | Not null; FK to `PasscodeCredential` with `ON DELETE RESTRICT` and `ON UPDATE RESTRICT`. Any credential retirement/deletion flow must first revoke active challenges and append the bounded revocation audit event in its own approved transaction; no implicit cascade may bypass the state machine. |
| `credential_version integer` | Not null, positive; exact version verified at issuance. |
| `purpose varchar(64)` | Check constraint limited to `forced_passcode_change`. |
| `secret_digest bytea` | Nullable fixed-length versioned Pepper-HMAC-SHA-256 digest; required only while the row is `active`, then immediately nulled on every terminal transition. |
| `pepper_id varchar(64)` | Not null; references configured key version, never the Pepper material. |
| `state varchar(16)` | Check constraint: `active`, `consumed`, `revoked`, `expired`. |
| `issued_at`, `expires_at`, `consumed_at`, `revoked_at`, `expired_at timestamptz` | UTC timestamps; issuance explicitly sets `expires_at = issued_at + interval '600 seconds'` exactly, and the database `CHECK` below enforces that relationship. |
| `created_by_event_id uuid` | Optional immutable audit correlation, not a secret. |
| `correlation_id uuid` | Not null; request correlation without raw request data. |

Required indexes/constraints:

1. Primary key on `id` and unique index on `selector`.
2. Unique partial index on `(credential_id, purpose)` where `state='active'`.
3. Lookup index on `(tenant_id, selector, purpose, state)` and cleanup index
   on `(state, expires_at)`.
4. Check `expires_at = issued_at + interval '600 seconds'` exactly (not merely
   greater-than). `state='active'` requires `secret_digest IS NOT NULL` and
   all terminal timestamps null. Every terminal state requires
   `secret_digest IS NULL`; `consumed` requires only `consumed_at`, `revoked`
   requires only `revoked_at`, and `expired` requires only `expired_at` among
   those terminal timestamps. These are explicit database checks, not service
   conventions.
5. No index on plaintext secret (none exists); digest comparison occurs only
   after selector, tenant, and purpose have located a candidate active row.

RLS must be enabled and forced. Tenant policy must compare `tenant_id` with
the established transaction tenant context and fail closed if context is
missing. Runtime queries occur only after `tenant_atomic(tenant.id)` and before
any tenant challenge query. `codesho_migrator` owns DDL/RLS policy creation;
`codesho_runtime` gets only the minimum table privileges required for the
service (`SELECT`, `INSERT`, `UPDATE` on this table, no `DELETE`, `TRUNCATE`,
DDL, ownership, or `BYPASSRLS`). `PUBLIC` receives no schema/table access.
Cleanup uses an approved restricted worker/service identity and RLS-aware,
bounded state transitions followed by terminal-row deletes; it is not a client endpoint. Existing audit table privileges
remain append-only through `audit.append_identity_security_event` and are not
broadened.

## Digest, issuance, and atomic locking algorithm

The secret is at least 32 random bytes from the operating-system CSPRNG and is
base64url encoded only for cookie transport. Store:

`digest = HMAC-SHA-256(pepper[pepper_id], secret_bytes)`

Comparison uses constant-time comparison. Digest computation uses the active
Pepper on issuance; completion reads the row's `pepper_id` so rotation remains
verifiable while that Pepper version is retained. No digest is returned or
logged. Every Pepper version used by an active challenge must remain available
for at least the 600-second challenge lifetime plus the configured clock-skew
and transaction grace. Emergency Pepper revocation instead force-revokes all
active challenges referencing that `pepper_id` in the rotation runbook; the
revoked Pepper is never retained merely to complete those challenges.

### Issuance inside the existing login transaction

1. The existing login endpoint validates its established request and CSRF
   requirements, derives trusted IP/device signals, runs its login abuse
   preflight, resolves the exact tenant member inside `transaction.atomic()`,
   and verifies the submitted current passcode exactly once. Unknown or
   ineligible principals retain equivalent dummy verification and the existing
   uniform failure contract.
2. When that verified credential has `must_change=true`, lock its user and
   credential. Lock any active challenge for its credential/purpose, mark it
   `revoked` with database time, null its digest, and insert the replacement
   row with a random selector, credential version, digest, exact 600-second
   expiry, and correlation ID. The partial unique index is the final
   concurrency backstop.
3. Append a bounded immutable `passcode_change_challenge_issued` audit event
   in the same failure domain. If audit persistence fails, roll back the row
   and return the fail-closed login error. Commit, set the challenge cookie,
   return the existing `403 passcode_change_required`, and create no session.

Concurrent issuances serialize on the credential row. The second issuer
revokes the first newly active row and receives the only usable cookie. A
unique-index conflict is retried only within the single transaction after a
fresh lock; it is not a client-visible retry loop.

### Completion transaction

1. Validate CSRF and new-passcode shape; parse the HttpOnly cookie strictly as
   `v1.<selector>.<secret>`. Apply challenge/IP/device/account completion
   preflight before expensive work.
2. Establish tenant context. Without locking, find a candidate row only by
   selector, tenant, and purpose; read its `credential_id`. Then lock the
   credential first with `FOR UPDATE`, and re-read/lock the challenge second
   with `FOR UPDATE`. Absence returns the neutral terminal error and clears
   the cookie.
3. Under those locks, re-check database `expires_at`, state, tenant,
   selector, `credential_version`, and the constant-time Pepper-HMAC made with
   the `pepper_id` read from the locked row. Terminal, mismatch, or expired
   rows are never consumed successfully; an expired active row is atomically
   marked `expired`, its digest is nulled, and its bounded audit event is
   appended before the neutral response.
4. Verify the new passcode against the current credential. If it matches,
   return `passcode_same_as_current` / 409 without changing the credential or
   consuming the active challenge.
5. Hash the new value with Argon2id and the current active Pepper; update the
   credential atomically, set `must_change=false`, increment
   `credential_version`, and increment `User.session_auth_epoch`.
6. Mark the challenge `consumed`, null its digest, append bounded
   `passcode_changed` and `passcode_change_challenge_consumed` audit events
   with the new credential version, and atomically clear eligible
   account/challenge counters. Any audit or required abuse failure rolls back
   all security state.
7. Commit first; clear the challenge cookie and return 204 with no session.
   The post-change user must perform a fresh normal login. No middleware or
   session-engine write is part of this transaction.

The combination of row locks, state transition, credential version, partial
unique index and transaction rollback makes completion replay-resistant.
Double submits serialize: one consumes and changes the passcode; the other
observes terminal/version-mismatch state and cannot create a second change or
session.

## Abuse controls

Use distinct namespaced counters for login-triggered issuance and completion
while retaining the existing HMAC-anonymized account/IP/device signal handling.
Required dimensions are account, trusted client IP, signed device ID, and the
challenge selector-derived subject. Counters store no raw selector, secret, or
passcode. The following thresholds are **SETTLED_BY_EMPLOYER**:

| Completion dimension | Limit |
| --- | --- |
| Account | 5 failures per 10 minutes |
| Active challenge | 5 failures per 10 minutes and no longer than its TTL |
| Signed device | 10 failures per 10 minutes |
| Trusted IP | 30 failures per 10 minutes |
| Global detection | 100 failures or 20 distinct account/selector subjects per 10 minutes; alert only |

- Issuance inherits the existing S1-003 thresholds. A valid `must_change`
  verification may clear only the existing eligible account failure counter;
  unrelated IP, device, challenge, and global counters remain unchanged.
- Completion failures use the settled bounds and a neutral `Retry-After`.
  Malformed-body or CSRF failures increment only IP and device counters; they
  do not consume or mutate a challenge. Invalid selector or secret failures
  increment only IP, device, and global signals; they never increment or lock
  an account or challenge. Same-as-current increments only account and
  challenge counters while leaving credential and challenge unchanged.
- There is **no global automatic lockout**. Global signals are alert-only and
  may trigger operational investigation, not automatic credential mutation or
  lockout.
- Successful completion atomically clears only eligible account and challenge
  failure counters; it never clears unrelated IP, device, or global signals.
- Required Redis unavailability returns 503 only for sensitive issuance or
  completion operations that require abuse control. Session status and logout
  remain independent. Required audit or database failure during a sensitive
  transaction rolls back all credential, challenge, epoch, and audit state and
  returns 503. PostgreSQL challenge state is never reconstructed from Redis.

## Session, audit, retention, and cleanup

The successful change increments `session_auth_epoch`. Every authenticated
request checks that epoch; sessions carrying an old epoch are rejected or
flushed. Physical session-row deletion is optional cleanup. Completion creates
no new session; a later normal login creates the only post-change session.
Logout clears the challenge cookie as defense in depth.

The settled bounded, forward-only audit allow-list contains event types
`passcode_change_challenge_issued`, `passcode_change_challenge_revoked`,
`passcode_change_challenge_consumed`, `passcode_change_challenge_expired`, and
`passcode_change_rejected`; reason codes `challenge_issued`,
`challenge_superseded`, `challenge_consumed`, `challenge_expired`,
`challenge_invalid`, `passcode_same_as_current`, and
`challenge_revoked_pepper_rotation`. The last code is reserved exclusively
for emergency Pepper compromise/rotation revocation so it remains
distinguishable from ordinary supersession. Audit metadata contains
tenant ID, subject/actor user IDs, credential version, correlation ID and
idempotency key only. Abuse-control signals are never written to the immutable
audit ledger: no raw, hashed, HMAC-derived, or otherwise transformed IP,
device, account-signal, or challenge-signal value is an audit field. They exist
only in short-lived Redis counters and explicitly approved operational metrics,
with namespace-separated keys and no secret or passcode material. Do not add
unbounded free-text reasons.

Terminal non-secret challenge metadata is retained for 30 days after terminal
state for incident correlation. Legal review remains required before
Production. Cleanup first selects expired `active` rows
in RLS-aware bounded batches using PostgreSQL time, locks them, marks them
`expired`, nulls their digests, and appends idempotent bounded audit events.
It never deletes an active row. Only after that transition may it delete
terminal rows past the approved retention period. On every transition to
`consumed`, `revoked`, or `expired`, `secret_digest` is immediately nulled;
only non-secret metadata needed for incident correlation remains during the
30-day window. Immutable audit events follow their separate approved retention
policy and are never altered/deleted by this feature.

## OpenAPI, migration, and rollback plan

The implementation task must extend the existing login POST contract with its
must-change challenge-cookie behavior and add only the completion POST path,
including JSON schemas, cookie security behavior, exact response codes,
`Retry-After` for 429, and non-enumerating error semantics to
`docs/openapi.yaml`. It must not expose selector, secret, digest, challenge
ID, implementation state, user existence, or raw abuse reason.

Forward migration sequence:

1. Create the table, checks, indexes, RLS policies and least-privilege grants
   with `codesho_migrator` from an empty PostgreSQL database.
2. Add audited reason/event allow-list entries atomically and forward-only.
3. Deploy dormant code behind no public route; validate grants/RLS and cleanup
   job behavior.
4. Enable login-triggered issuance/completion only after all tests and
   required review pass.

Rollback is non-destructive: first disable routes/job scheduling and clear
challenge cookies by response policy; retain rows and immutable audit evidence.
Do not reverse or drop the audit allow-list or challenge table in production.
Any schema-removal request is a later retention/legal decision. If a code
rollback occurs after a credential update, epoch invalidation remains in force;
never restore an old credential hash or session epoch.

## Required test matrix

| Area | Required evidence |
| --- | --- |
| Login-triggered issuance | Exact tenant/current passcode/must-change eligibility; existing login remains 403 with no session and sets cookie only after success; failed or other-user login clears an old cookie. |
| Cookie/CSRF | Exact `__Host-` attributes and `v1.selector.secret` grammar; host-only secure production behavior; selector/secret never appear in body/URL/storage; CSRF is required for completion. |
| Challenge state | Exact 600-second database expiry, single active row, superseding must-change login revokes predecessor and nulls digest, terminal state immutability, restart durability. |
| Concurrency | Parallel must-change logins leave one active row; double completion yields one credential version increment/audit success and one neutral terminal result, with no session from either response. |
| Replay/binding | Wrong tenant, selector, credential, purpose, version, secret, expired/revoked/consumed cookie cannot complete; locked-row HMAC comparison is constant-time. |
| Passcode policy | Six ASCII only: backend validation is a strict `^[0-9]{6}$` ASCII regex match with no Unicode normalization or digit folding. Persian/Arabic digit normalization remains a future UI concern; same-as-current rejection leaves valid challenge usable for a different value; Argon2id/current Pepper metadata is asserted. |
| Abuse | Settled account/challenge/device/IP/global thresholds and counter dimensions, neutral Retry-After, no global automatic lockout, Redis/audit outage fail-closed, no raw signals in logs. |
| Sessions | No session before or during completion; every authenticated request checks epoch and old-epoch sessions are rejected/flushed; only a later normal login creates a session; logout cleanup behavior. |
| Database security | Empty-db migration, PostgreSQL RLS negatives, connection-reuse tenant leakage negatives, runtime cannot DDL/alter grants/bypass RLS, migrator-only DDL. |
| Audit/retention | Bounded reason codes, immutable append, idempotency, no secrets; cleanup expires abandoned active rows first, nulls their digests, then deletes only terminal rows after policy interval. |
| API/quality | OpenAPI validation, response schemas, tenant-host/CSRF negatives, Ruff/MyPy/pytest, frontend contract tests if a UI is later authorized, `git diff --check`. |

## Rollout and implementation slices

1. **001B foundation:** model/migration/RLS/grants, digest helper, service
   interfaces, OpenAPI draft and isolated tests; no UI.
2. **001C login issuance:** extend the existing login transaction with cookie
   lifecycle, abuse/audit integration, concurrency and tenant negatives.
3. **001D completion:** atomic replacement, same-as-current behavior, epoch
   invalidation/no-session behavior, replay and double-submit tests.
4. **001E hardening:** cleanup worker/runbook, retention decision, empty-db
   migration/restore, full CI/Compose and sequential Claude review.
5. **001F release gate:** Commander/employer acceptance only after all prior
   slices are green; a separately approved UI task may then consume the API.

No slice authorizes Signup, OAuth, Recovery, Guardian, Onboarding, provider
integration, protected-repository promotion, or a real Alpha release by
itself.

## Final decision matrix and remaining approvals

| Topic | Design decision | Status / required owner |
| --- | --- | --- |
| Issuance | Extend the existing successful `POST /api/v1/auth/passcode/login/` must-change branch; do not add a challenge endpoint or resend the current passcode. | Settled by Commander review. |
| Cookie | `__Host-codesho-passcode-change`, `v1.<selector>.<secret>`, host-only, `Path=/`, `HttpOnly`, `Secure`, `SameSite=Lax`, exact 600-second expiry. | Settled design; deployment must prove fail-fast secure production configuration. |
| Challenge selector | Non-secret UUID/random selector in the cookie and unique database column; selector identifies the candidate row before its `pepper_id` is read. | Settled by Commander review. |
| Authoritative state | PostgreSQL, one active row per credential/purpose, row locks and database checks; Redis is abuse control only. | Settled. |
| Same-as-current | Return `409 passcode_same_as_current` to a holder of a valid cookie and CSRF token; do not consume the active challenge. | Settled by Commander disposition. |
| Session after change | Clear the challenge cookie and return 204 with no session; require a fresh normal login after epoch increment. | Settled by Commander disposition. |
| Challenge metadata retention | Retain terminal non-secret metadata for 30 days; bounded cleanup expires abandoned active rows first, then deletes terminal rows. | Settled for Alpha design; Legal review is required before Production. |
| Abuse controls | Settled completion limits: account 5, active challenge 5, signed device 10, trusted IP 30 failures per 10 minutes; global detection 100 failures or 20 distinct account/selector subjects per 10 minutes, alert only; no global automatic lockout. | SETTLED_BY_EMPLOYER. Operational monitoring and runbook verification remain implementation gates. |
| Audit governance | Forward-only bounded event/reason allow-list, including emergency Pepper-revocation reason. | Settled design; its migration requires an independent blocking review. |

Secure `__Host-` deployment evidence, operational monitoring/runbook
verification, and legal review of the 30-day terminal-metadata retention are
Production or implementation gates. None authorizes implementation.

Employer/Commander must authorize `AUTH-PASSCODE-CHANGE-001B` before any
source, migration, API, test, package, commit, or push begins.

## Review handoff

Claude review prompt ID: `CLAUDE_AUTH_PASSCODE_CHANGE_001A_DESIGN_REVIEW_01_V1`.
Claude was unavailable: its initial response did not provide a completion
marker, and the one permitted completion request had no retained attachment
context. No further Claude retry is authorized. Commander accepted this outage
and supplied fallback review marker
`COMMANDER_AUTH_PASSCODE_CHANGE_001A_DESIGN_REVIEW_01_COMPLETED`.
