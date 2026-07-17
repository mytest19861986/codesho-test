# Authentication Alpha Decisions

Status: `APPROVED_FOR_ALPHA_TEST_UI`

Date: 2026-07-17

Scope: UI-AUTH-003A documentation and a future same-origin Authentication
Alpha test UI. These decisions do not authorize a production release, a new
endpoint, a route, an identity provider, or a credential-change implementation.

## Decision records

### DR-AUTH-ALPHA-001 — absolute session lifetime

The Alpha browser session is exactly 12 hours (43,200 seconds) from issuance.
It has no sliding refresh, renewal endpoint, persistent-session choice, or
“remember me” control. The UI must not present or simulate any of those.

### DR-AUTH-ALPHA-002 — exact username identifier

Authentication uses the existing `username` field only. Lookup is exact and
case-sensitive. The UI sends the entered username unchanged and does not
lowercase, trim, Unicode-normalize, or substitute email/phone identifiers.

### DR-AUTH-ALPHA-003 — localized passcode entry, strict wire format

The UI may normalize Persian (`۰`–`۹`) and Arabic-Indic (`٠`–`٩`) numerals to
ASCII (`0`–`9`) only for passcode entry. It then validates and sends exactly
six ASCII digits. Neither raw nor normalized passcode values may be stored,
logged, included in telemetry, or placed in a URL.

### DR-AUTH-ALPHA-004 — mandatory credential-change boundary

`must_change` remains enforced by the backend. A
`403 passcode_change_required` outcome creates no session and is a neutral
blocked state, not a successful login. `AUTH-PASSCODE-CHANGE-001` must issue a
single-purpose, one-time challenge only after valid credential verification;
the challenge expires after exactly ten minutes. It must not be implemented as
a Login, Recovery, or Guardian bypass.

### DR-AUTH-ALPHA-005 — deferred and absent capabilities

Signup, OAuth (including Google and GitHub), Recovery, and Onboarding are
deferred and absent from the Alpha UI and backend scope. The UI must not render
interactive provider, signup, recovery, onboarding, or account-creation flows
or claim that any such action is available.

### DR-AUTH-ALPHA-006 — release gate

The Authentication Alpha test UI may be specified and later implemented in an
approved bounded task, but a real Alpha release is blocked until
`AUTH-PASSCODE-CHANGE-001` is implemented, reviewed, tested, and approved.
Manually clearing `must_change` or limiting provisioning to avoid the state is
not an acceptable release workaround.

## Invariants retained from the implemented contract

- Tenant host resolution and CSRF bootstrap precede the login mutation.
- Unknown, inactive, non-member, and wrong-passcode attempts remain
  non-enumerating `401 invalid_credentials` outcomes.
- `429` uses a neutral Retry-After presentation and `503` remains fail-closed.
- A successful login rotates the session and binds the authentication epoch;
  credential replacement invalidates prior sessions.
- All user-facing future copy remains typed and Persian/RTL accessible; no
  fabricated account, provider, recovery, or onboarding data is permitted.
