# UI-AUTH-003A Authentication Alpha Finalization Handoff

Status: `APPROVED_FOR_ALPHA_TEST_UI`

## Delivered documentation

- `UI_AUTH_003_SPEC.md` now records the approved test-UI status, the absolute
  12-hour non-sliding session policy, exact case-sensitive username handling,
  localized-digit-to-ASCII passcode handling, and backend `must_change`
  enforcement.
- `2026-07-17-auth-alpha-decisions.md` records
  `DR-AUTH-ALPHA-001` through `DR-AUTH-ALPHA-006`.
- The specification makes `AUTH-PASSCODE-CHANGE-001` an explicit real-Alpha
  release gate: a one-time, ten-minute, single-purpose change challenge after
  valid credential verification, without a session before replacement.
- Signup, OAuth, Recovery, and Onboarding remain deferred and absent.

## Evidence basis

The documentation follows the implemented OpenAPI and backend contracts at
`79e3034cb7352611d7a7d861f73da4f62b91bed5`:

- `docs/openapi.yaml` defines only CSRF, passcode login, session, and logout.
- `backend/config/settings/base.py` sets `SESSION_COOKIE_AGE = 43,200`.
- `backend/config/authentication.py` performs exact username lookup and
  returns the backend-owned `passcode_change_required` status.
- `backend/modules/identity/passcodes.py` enforces exactly six ASCII digits.
- `backend/tests/test_passcode_login.py` proves case sensitivity and that
  `must_change` returns 403 without creating a session.

## Scope and verification

Exactly three documentation paths are changed by this task:

1. `docs/ui/UI_AUTH_003_SPEC.md`
2. `docs/decisions/2026-07-17-auth-alpha-decisions.md`
3. `docs/ui/UI_AUTH_003A_HANDOFF.md`

All three files are UTF-8 without a BOM. No source, route, asset, dependency,
test, OpenAPI, provider, or protected-repository change is included.

Required final checks: UTF-8/no-BOM scan and `git diff --check`. After the
authorized documentation commit is pushed to `codesho-test/main`, verify the
resulting exact-SHA GitHub Actions and Compose workflows through the approved
browser channel. Do not promote to protected `codesho`.

## Next approved dependency

No real Alpha release may proceed until `AUTH-PASSCODE-CHANGE-001` has its own
approved backend/UI task, security review, tests, and employer/Commander
acceptance.
