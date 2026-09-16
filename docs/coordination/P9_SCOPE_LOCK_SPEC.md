# P9 Scope Lock Specification

## 1. Overview & Immutable Boundary
The Scope Lock freezes all operational and data boundaries before any synthetic activation occurs. Once frozen, the scope cannot be modified without invalidating the active token and terminating the session.

## 2. Frozen Scope Fields
1. `TENANT_ID`: The exact synthetic tenant UUID bound to `app.current_tenant`.
2. `USER_CLASSES`: `[SYNTHETIC_STUDENT, SYNTHETIC_PARENT, SYNTHETIC_MENTOR, SYNTHETIC_STAFF]`. Zero real users.
3. `DATA_CLASSES`: `[SYNTHETIC, TEST_FIXTURE, NON_PII]`. Any `REAL_*` or `UNKNOWN` is strictly forbidden.
4. `FEATURES`: `[COURSES, EXERCISES, ATTENDANCE, QUIZZES]`.
5. `DURATION`: Maximum duration (rehearsal default: 14 days).
6. `ALLOWED_OPERATIONS`: `[READ, MUTATE_SYNTHETIC, AUDIT, TEST]`.
7. `COMMUNICATION_MODE`: `STUB_DISABLED` (Real SMS/Email/Push count = 0).
8. `PAYMENT_MODE`: `STUB_DISABLED` (Real payment gateway count = 0).
9. `ENVIRONMENT`: `LOCAL_TEST_SYNTHETIC`.
10. `ACTIVATION_VERSION`: `P9.0.1`.

## 3. Scope Digest Invariant
The canonical JSON representation of the scope dictionary is serialized (`sort_keys=True`) and hashed using SHA-256.
```python
scope_digest = hashlib.sha256(canonical_json_bytes).hexdigest()
```
If any component of the scope is altered in-flight, the digest check fails immediately, triggering a transition to `FAILED_CLOSED` and logging an incident event.
