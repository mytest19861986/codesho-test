# UI-AUTH-003A Authentication Alpha Specification

Status: `APPROVED_FOR_ALPHA_TEST_UI`

Decision record: `DR-AUTH-ALPHA-001` through `DR-AUTH-ALPHA-006` in
`docs/decisions/2026-07-17-auth-alpha-decisions.md`.

Base SHA: `79e3034cb7352611d7a7d861f73da4f62b91bed5`. This approval authorizes
only a future Alpha test UI that consumes the existing same-origin passcode
contract. It creates no route, provider, source, asset, signup, recovery,
OAuth, onboarding, or production release authorization.

## Evidence and contract boundary

This audit compares `H:\codesho\UI\ui new\desktop+mobile+tablet\signup+onboard.png`
with `docs/openapi.yaml`, `backend/config/auth_views.py`,
`backend/tests/test_passcode_login.py`, and the S1-005 review summary. The
only implemented public auth endpoints are tenant-host CSRF, passcode login,
session state, and logout. Login UI, signup, onboarding, recovery, guardian,
and notification workflows are explicitly out of scope in Sprint 1.

## Endpoint inventory

| Endpoint | Method | Preconditions | Success | Failure contract | UI consequence |
|---|---|---|---|---|---|
| `/api/v1/auth/csrf/` | GET | exact tenant host | 204; CSRF cookie and, if absent/invalid, signed HttpOnly device cookie | 400 `invalid_request` | Bootstrap before any mutation; never display cookie values. |
| `/api/v1/auth/passcode/login/` | POST JSON | exact tenant host, prior CSRF cookie and `X-CSRFToken` | 204; rotated Django session, auth epoch | 400 `invalid_request`; 401 `invalid_credentials`; 403 `passcode_change_required`; 429 `try_again_later` + `Retry-After`; 503 `authentication_temporarily_unavailable` | Only username + six ASCII digits are supported. |
| `/api/v1/auth/session/` | GET | authenticated tenant session | 200 `{authenticated:true,user:{id,username},tenant:{id,slug,role}}` | 401 `invalid_credentials` | Current-user/session bootstrap only; no profile/onboarding data. |
| `/api/v1/auth/logout/` | POST | authenticated session, CSRF header | 204 and session flush | 403 `csrf_failed` | Clear local UI state only after 204; no fake success. |

`passcode_change_required` is a valid credential state but creates no session.
Unknown, inactive, non-member, and wrong-passcode attempts all return the same
401 code; UI must not branch into account-existence messages. Username lookup
is exact/case-sensitive. The server owns all passcode validation and abuse
decisions.

## Lifecycle, tenant, cookies, and device signal

1. Resolve the tenant from the approved host before presenting a mutation.
2. GET the exact CSRF endpoint with same-origin credentials; retain browser
   cookies and read only the CSRF token needed for the request header.
3. POST login with `credentials: "same-origin"`, JSON username/passcode, and
   `X-CSRFToken`. Do not persist passcode, device ID, session ID, or token in
   local/session storage, logs, telemetry, URL, or error state.
4. On 204, GET session and route only after a valid response. The backend
   rotates the session key and pins `session_auth_epoch`; passcode replacement
   invalidates prior sessions.
5. Device ID is server-signed, HttpOnly, Secure in production, SameSite=Lax,
   and non-authoritative. A corrupt/missing value is replaced server-side; UI
   must neither manufacture nor display one.
6. Logout repeats CSRF bootstrap if needed, POSTs with CSRF, and treats 403 as
   a failed mutation, not a completed logout.

## Approved Alpha session and credential rules

- The browser session has an **absolute 12-hour lifetime** (`43,200` seconds).
  There is no sliding refresh, persistent-session option, or “remember me”
  control. A future UI must not refresh or extend the session clock.
- The login identifier is `username`. Lookup is exact and case-sensitive:
  `learner` and `LEARNER` are different inputs. The UI must transmit the
  entered username unchanged; it must not lowercase, trim, Unicode-normalize,
  or offer email/phone login.
- The backend accepts exactly six ASCII passcode digits (`0` through `9`). A
  future Persian UI may normalize only Persian digits (`۰`–`۹`) and Arabic-Indic
  digits (`٠`–`٩`) deterministically to the corresponding ASCII digits before
  client validation and transmission. It must send exactly six ASCII digits,
  retain no raw or normalized passcode, and never log either value.
- `must_change` remains a backend-enforced credential state. A valid credential
  requiring change produces `403 passcode_change_required`, appends the typed
  audit event, and creates no authenticated session. UI must show a neutral
  blocked state; it must not clear `must_change`, treat login as successful, or
  redirect to a protected screen.

## Reference-to-backend capability matrix

| Reference element | Status | Contract disposition |
|---|---|---|
| Email/phone identifier field | design_only | Backend accepts only `username`; employer/backend decision required before labels, normalization, email, or phone login. |
| Password field | forbidden_for_alpha | Do not substitute a normal password for the six-digit ASCII passcode contract. |
| Passcode login | supported | Future UI may expose username + six digits only after approved implementation slice. |
| Remember me | employer_decision_required | Backend session policy is fixed at 12 hours; no persistent-session choice endpoint exists. |
| Forgot password | deferred | Requires approved Recovery flow, guardian/legal boundary, and provider policy. |
| Google / GitHub | forbidden_for_alpha | Reference-only; no OAuth provider, callback, account linking, or backend contract exists. |
| Signup | deferred | No registration endpoint or contract exists. |
| Onboarding goals/skills/path/schedule/mentor | deferred | No profile, curriculum, scheduling, mentor, or persistence contract exists. |
| Completion/success screen | design_only | Cannot claim account creation, plan creation, or mentor assignment. |

## Proposed routes and component tree (not created)

Proposed only after approvals: `/login`, `/signup`, `/onboarding`. The current
implemented contract could support only a tenant-host `/login` screen.
Suggested future tree: `AuthPage` -> `TenantAuthShell` -> `PasscodeLoginForm`
with `CsrfBootstrap`, `AuthErrorRegion`, and `SessionRedirectGuard`. Signup and
onboarding require separate approved contracts; do not render their forms as
working flows beforehand. PublicShell may be reused only after an approved
auth-shell decision; ApplicationShell must not render before session evidence.

## UX, RTL, accessibility, responsive and error rules

- Persian/RTL labels, logical spacing, `dir="rtl"`, visible focus, semantic
  `label`/input association, keyboard submit, `aria-live="polite"` error
  region, and no color-only validation are required.
- Passcode input must mask appropriately without logging; client validation is
  usability-only and must not imply account knowledge. Send no mutation before
  CSRF bootstrap.
- 401 gets one uniform Persian credential-failure message. 429 may present a
  neutral retry timer from `Retry-After`, never the abuse reason/counter.
  503 is a neutral temporary-service message. 403 CSRF requires a safe retry
  bootstrap; `passcode_change_required` must stop login and wait for the
  approved Recovery/credential-change task.
- 1440: two-column reference composition is design-only; keep auth form
  reading order first. 1024: form remains primary with no hidden provider
  controls. 390: single column, 44px-equivalent targets, no horizontal
  overflow, numeric passcode keyboard hint only after a real UI task.

## Guardian/teen and security boundaries

The authenticated session returns tenant role but no guardian relation,
consent, minor profile, recovery, or notification contract. Guardian linking,
teen recovery, parental notice, and age/consent decisions require a dedicated
approved Recovery/Guardian task and employer/legal decisions. Never expose
whether a username belongs to a teen, guardian, tenant, or inactive account.

## Mandatory passcode-change gap

Login UI may authenticate only a user whose credential does not require a
change. A `403 passcode_change_required` response is a neutral blocked state,
creates no session, and must not be represented as a successful login. The UI
must not reuse Login, Recovery, or Guardian flows to change a passcode.

Real Alpha onboarding/provisioning is release-blocked until a dedicated
backend contract exists. Manually disabling `must_change` is not an acceptable
Production workaround. A login implementation may be a bounded technical
slice, but real user onboarding/release remains blocked by
`AUTH-PASSCODE-CHANGE-001` unless every Alpha credential already follows the
approved secure lifecycle without a bypass.

For usability, a future UI may accept Persian and Arabic-Indic numerals and
normalize them locally and deterministically to ASCII. It must validate and
send exactly six ASCII digits, retain the current strict Backend contract, and
never persist or log either raw or normalized passcode.

`AUTH-PASSCODE-CHANGE-001` is the mandatory pre-release dependency for any
real Alpha credential that could encounter `must_change`. Its approved design
boundary is a one-time, single-purpose challenge that is issued only after
valid credential verification; it expires after exactly ten minutes and is
consumed on first use. It creates no authenticated session before a successful
replacement. The future implementation must preserve Argon2id with the active
Pepper version, policy-approved reuse prevention, abuse controls, immutable
audit events, session/auth-epoch invalidation, and applicable guardian/legal
handling. Login, Recovery, or Guardian must not be repurposed as a bypass.

**Release gate:** a real Alpha release is blocked until
`AUTH-PASSCODE-CHANGE-001` is implemented, reviewed, tested, and approved.
The present status permits test UI only; it does not waive that gate.

## Test matrix for a future approved login slice

| Area | Required evidence |
|---|---|
| Contract | exact host; CSRF-before-POST; JSON schema; same-origin credentials; 204 then session fetch |
| Errors | 400/401 uniform handling; 403 CSRF vs must-change distinction; 429 Retry-After neutral UI; 503 fail-closed UI |
| Security | no passcode/device/session logging or storage; session rotation/epoch invalidation; no enumeration; no fake success |
| Accessibility | keyboard, labels, focus, live errors, RTL, screen-reader error association |
| Responsive | 1440/1024/390 screenshot/DOM evidence, no overflow, no unavailable provider/link |
| Regression | OpenAPI contract test, tenant-host negative, logout CSRF, role/session bootstrap |

## Exact bounded implementation slices (after approval)

1. `UI-AUTH-003B`: Login-only UI consuming the four existing endpoints; no
   signup, recovery, providers, remember-me control, or new route unless
   separately authorized.
2. `AUTH-RECOVERY-*`: backend contract, guardian/legal decision, audit and
   notification/provider decisions before any forgot-passcode UX.
3. `AUTH-SIGNUP-*`: registration/consent/tenant-membership backend contract
   before signup UI.
4. `ONBOARDING-*`: profile/curriculum persistence contract before any wizard.
5. `AUTH-PASSCODE-CHANGE-001`: a dedicated backend and UI contract for a
   short-lived, single-purpose challenge issued only after valid credential
   verification. It requires ten-minute expiry, one-time use, no authenticated
   session before successful replacement, Argon2id with the current Pepper
   version, policy-approved reuse prevention, abuse control and immutable
   audit events, guardian/legal handling where applicable, session/auth-epoch
   invalidation, and no credential/passcode logging.

## Employer approval matrix

| Decision | Required before | Owner |
|---|---|---|
| Public origin, tenant-host discovery and final login route | Login implementation | Employer + Commander |
| Username versus email/phone identifier and normalization | Identifier labels/validation | Employer + backend approval |
| Session duration and remember-me policy | Any remember-me control | Employer/security |
| Recovery, guardian relation, minor consent and retention | Forgot-passcode/guardian UX | Employer + legal + Commander |
| OAuth Google/GitHub provider, account linking, privacy and cost | Any social button/callback | Employer |
| Signup identity, verification, tenant admission and consent | Signup UI/API | Employer + Commander |
| Onboarding data model, curriculum, mentor claims and scheduling | Wizard/persistence | Employer + Commander |
| Notification provider/templates/consent | Recovery or security notices | Employer + legal |
| Mandatory passcode-change workflow and challenge lifetime | `AUTH-PASSCODE-CHANGE-001` | Employer + security + Commander |
| Whether Alpha may onboard users before that workflow exists | Any real Alpha onboarding/release | Employer + Commander |
| Persian/Arabic digit UX with strict ASCII transmission | Any passcode UI | Employer + security |

## Acceptance conclusion

The reference is a visual input only. It proves no supported password, OAuth,
signup, recovery, or onboarding capability. The only safe future alpha is a
tenant-host username/passcode login UI after the route/host decision; all
other visible reference capabilities remain deferred, forbidden, or awaiting
employer decisions above.
