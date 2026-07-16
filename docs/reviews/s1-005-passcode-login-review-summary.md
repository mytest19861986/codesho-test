# S1-005 passcode login and session review summary

All raw Claude prompts, attachments and replies are retained outside the
repository in the controlled Claude review workspace. Reviews were sequential.

## Review 01 — authentication boundary

- Prompt: `CLAUDE_S1_005_AUTH_REVIEW_01_V1`
- Files: `config/authentication.py`, `config/auth_views.py`
- Completion marker: `CLAUDE_S1_005_AUTH_REVIEW_01_COMPLETED`

| Finding | Disposition |
|---|---|
| P0 session-key rotation was implicit | Accepted and fixed: `request.session.cycle_key()` now precedes explicit Django login; regression test proves pre/post keys differ. |
| P0 Redis success-clear atomicity evidence | Accepted and fixed: `abuse.py` documents atomic Redis `EVAL`; timeout regression confirms fail-closed result. |
| P1 failure event dedup undercounted forensic evidence | Accepted and fixed: up to five known-principal failures are recorded before durable lock; blocked events are window-deduplicated. |
| P1 wrong-tenant login could affect another tenant's account counter | Accepted and fixed: account and account-device signals are tenant-scoped. |
| P1 timing shape / malformed-IP telemetry | Rejected as a bypass: Redis Lua key shape is independent of credential existence and malformed IP rejects before verification, fail-closed. The request-signal module retains no raw signal logging. |
| P2 device-cookie churn / session-role freshness | Rejected with reason: device is a non-authoritative signal alongside account/IP controls; membership is loaded fresh under the resolved tenant for every authenticated request. |

## Review 02 — tenant and session epoch

- Prompt: `CLAUDE_S1_005_SESSION_TENANT_REVIEW_02_V1`
- Files: `middleware.py`, `passcodes.py`
- Completion marker: `CLAUDE_S1_005_SESSION_TENANT_REVIEW_02_COMPLETED`

| Finding | Disposition |
|---|---|
| P0 prefix tenant bypass | Accepted and fixed: bypass and pre-auth settings are exact-path allow-lists; regression test rejects prefix extensions. |
| P1 pre-auth context boundary | Accepted as documentation hardening: tenant-resolution transaction closes before the view can invoke Redis; only exact authentication endpoints are pre-auth. |
| P1 concurrent initial credential creation | Accepted and fixed: the parent user row is locked before `get_or_create`, serializing first credential creation. |
| P1 middleware order / cookie scope evidence | Accepted and fixed: settings put `SessionEpochMiddleware` before tenant authorization and explicitly prohibit shared cookie domains; regression tests pin both invariants. |
| P2 dummy verification call-site | Rejected as missing evidence: Review 01 covered and tests exercise the `verify_dummy_passcode` branch. |

## Review 03 — audit migration

- Prompt: `CLAUDE_S1_005_AUDIT_MIGRATION_REVIEW_03_V1`
- File: `0005_authentication_security_events.py`
- Completion marker: `CLAUDE_S1_005_AUDIT_MIGRATION_REVIEW_03_COMPLETED`

| Finding | Disposition |
|---|---|
| P0 DROP/ADD allow-list constraint atomicity | Accepted and fixed: migration explicitly sets `atomic = True`; PostgreSQL ACCESS EXCLUSIVE locking covers each transactional replacement. |
| P1 additive / forward-only migration evidence | Accepted and fixed: regression test asserts both prior allow-lists are subsets of the new lists, migration is atomic, and reversal raises `IrreversibleError`. |
| P2 grants and SECURITY DEFINER coupling | Rejected with evidence: this migration changes only check constraints; prior append-function/grant verification remains covered by audit privilege tests. |

No unresolved Claude P0 or P1 remains in the reviewed S1-005 scope.
