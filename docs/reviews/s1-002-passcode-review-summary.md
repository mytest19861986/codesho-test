# S1-002 Passcode Foundation Review Closure

Date: 2026-07-15
Implementation checkpoint: `d29fd1c` (service hardening follows Review 01)

## Sequential external reviews

- Claude Review 01, service only: marker
  `CLAUDE_S1_002_PASSCODE_SERVICE_REVIEW_01_COMPLETED`.
- Claude Review 02, model and migration only: marker
  `CLAUDE_S1_002_MODEL_MIGRATION_REVIEW_02_COMPLETED`.
- Versioned prompts and raw responses are retained outside the repository in
  `H:\codesho\codesho\claude\`.

## Dispositions

| Finding | Disposition | Resolution |
|---|---|---|
| Service F1 Argon2 implicit defaults | accepted | Explicit Argon2id profile: time 3, memory 65536 KiB, parallelism 2, hash 32, salt 16. |
| Service F2 missing Argon2 rehash check | accepted | `check_needs_rehash` is combined with Pepper-version detection. |
| Service F3 missing-credential timing | rejected-with-reason | No public verification endpoint exists; login/timing policy is out of scope. |
| Service F4 config exception boundary | accepted | Unknown Pepper uses explicit `PasscodeConfigurationError`; production settings fail-fast. |
| Service F5/F7 crypto/API safety | accepted | Raw passcode/HMAC are never persisted/logged; no API surface exists. |
| Service F6 duplicate validation | accepted | HMAC input is the single enforcement point. |
| Service F8 credential version | accepted | Model review confirmed field; future concurrent writers must remain atomic. |
| Model F1/F3 indexes | rejected-with-reason | No rotation/lockout query exists in Foundation; add only with those approved workflows. |
| Model F2 one-to-one | accepted | OneToOneField creates the database uniqueness constraint. |
| Model F4 version monotonicity | accepted | Current service uses select-for-update and atomic replacement. |
| Model F5/F8 migration safety | accepted | Empty-DB migration check passes and 0002 depends on 0001. |
| Model F6/F7 secret/API safety | accepted | No raw secret fields, admin registration, serializer, view, or URL. |
| Model F9 hash length | accepted | 256 characters provides sufficient Argon2id encoding headroom. |

No finding requires employer decision. No P0/P1 blocker remains.

## Acceptance state

`PASSCODE_MODEL_CREATED`, `ARGON2ID_ENABLED`, `VERSIONED_PEPPER_ENABLED`,
`PRODUCTION_FAILS_WITHOUT_VALID_PEPPER`, `RAW_PASSCODE_NEVER_PERSISTED_OR_LOGGED`,
`NO_PUBLIC_API_ADDED`, `REVIEW_TRACEABILITY_RECORDED`. CI and Compose remain
the final checkpoint after this review traceability commit. Rate Limit, Login,
Recovery, and UI remain out of scope.
