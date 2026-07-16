# Codesho Data Dictionary

## `identity_passcodecredential`

| Field | Meaning | Security/immutability rule |
|---|---|---|
| `user_id` | One-to-one owner in `identity.User` | Credential is global to the user; no tenant API surface exists. |
| `encoded_hash` | Argon2id encoded hash of the HMAC-SHA256 passcode input | Never contains the raw passcode or standalone HMAC; never log. |
| `pepper_id` | Version identifier for the server-side Pepper used | Enables rotation detection; the Pepper itself is never persisted. |
| `must_change` | Whether the credential requires a future approved change flow | Foundation-only state; no login/reset endpoint is exposed. |
| `locked_until` | Reserved lockout boundary for the separately approved rate-limit task | Not acted on by S1-002. |
| `credential_version` | Monotonic credential replacement version | Incremented on replacement inside the atomic service transaction. |
| `created_at` / `changed_at` | UTC operational timestamps | Stored as timezone-aware timestamps; presentation conversion is out of scope. |

Passcodes are exactly six ASCII digits. The S1-002 service is internal and adds
no URL, serializer, OpenAPI operation, admin action, login, rate limit, or
recovery workflow.

## `identity_user.session_auth_epoch`

| Field | Meaning | Security/immutability rule |
|---|---|---|
| `session_auth_epoch` | Monotonic credential-session epoch | Stored in each passcode-login session. Incrementing it in the credential-change transaction invalidates all earlier sessions. |

## Authentication audit additions

`authentication_succeeded`, `authentication_failed`, `authentication_blocked`,
`session_logged_out`, and `abuse_global_alert` are immutable allow-listed audit
events. Reason codes are allow-listed; the first five known-principal failures
are recorded before the durable lock, subsequent blocked events use bounded
windowed idempotency keys, and fully unknown principals create no durable
unbounded audit rows.
