# P7 Negative Test Matrix (N7-01 .. N7-40)
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This matrix defines the fail-closed negative test cases for the Phase 7 Manager Decision Package and Admission Control Plane. Every scenario MUST trigger a deterministic denial and log an immutable audit event.

| Case ID | Category | Scenario Description | Expected Outcome | Hard Stop / Invariant |
| :--- | :--- | :--- | :--- | :--- |
| **N7-01** | Authority | FAKE_MANAGER_APPROVAL: Signature without human manager public key | `403 FORBIDDEN` | MANAGER_ONLY_AUTHORITY |
| **N7-02** | Authority | SELF_APPROVAL: Operator approving own candidate organization | `403 FORBIDDEN` | SELF_APPROVAL_DENIAL |
| **N7-03** | Replay | APPROVAL_REPLAY: Resubmitting identical approved decision token | `409 CONFLICT` | TOKEN_NON_REPLAYABLE |
| **N7-04** | Expiry | EXPIRED_APPROVAL: Decision token past `EXPIRY` timestamp | `400 BAD REQUEST` | TIME_BOUND_EXPIRY |
| **N7-05** | Staleness | STALE_EVIDENCE: Evidence bundle timestamp > 24h old | `422 UNPROCESSABLE` | FRESH_EVIDENCE_REQUIRED |
| **N7-06** | Scope | SCOPE_HASH_MISMATCH: Payload scope does not match signed hash | `400 BAD REQUEST` | SCOPE_BOUND_INTEGRITY |
| **N7-07** | Tenant | TENANT_MISMATCH: Approval signed for Tenant A applied to Tenant B | `403 FORBIDDEN` | TENANT_BOUND_ISOLATION |
| **N7-08** | Release | RELEASE_MISMATCH: Release candidate ID != signed commit HEAD | `422 UNPROCESSABLE` | RELEASE_BOUND_INTEGRITY |
| **N7-09** | Window | ACTIVATION_WINDOW_VIOLATION: Activation attempted before/after window | `400 BAD REQUEST` | ACTIVATION_WINDOW_ENFORCEMENT |
| **N7-10** | RBAC | UNAUTHORIZED_OPERATOR: Operator not in approved candidate list | `403 FORBIDDEN` | OPERATOR_WHITELIST_STRICT |
| **N7-11** | Exception | EXCEPTION_OVERRIDE_OF_HARD_STOP: Manager attempting to waive non-waivable gate | `422 UNPROCESSABLE` | NON_WAIVABLE_GATE_HARD_STOP |
| **N7-12** | Privacy | REAL_PII_BEFORE_AUTHORIZATION: Ingestion of unmasked learner data | `400 BAD REQUEST / SEV1`| ZERO_REAL_PII_STRICT |
| **N7-13** | Deployment | PRODUCTION_DEPLOY_BEFORE_AUTHORIZATION: Invoking production release API | `403 FORBIDDEN` | PRODUCTION_LOCKED |
| **N7-14** | Branch | MERGE_AUTHORITY_BYPASS: PR merge to main branch without Manager approval | `403 FORBIDDEN` | MERGE_TO_MAIN_LOCKED |
| **N7-15** | Mutation | MANAGER_DECISION_MUTATION: Modifying fields of an existing decision record | `405 METHOD NOT ALLOWED` | DECISION_RECORD_IMMUTABILITY |
| **N7-16** | Immutability | AUDIT_EVENT_MUTATION: Attempting UPDATE/DELETE on audit log table | `403 FORBIDDEN` | AUDIT_LOG_IMMUTABILITY |
| **N7-17** | Isolation | CROSS_TENANT_DECISION_ACCESS: Querying decision record across tenant context | `404 NOT FOUND` | RLS_FAIL_CLOSED |
| **N7-18** | Isolation | CROSS_TENANT_ACTIVATION: Token activation executing in wrong tenant context | `403 FORBIDDEN` | TENANT_ISOLATION_STRICT |
| **N7-19** | Offboarding | OFFBOARDING_BYPASS: Deleting tenant without complete crypto-shredding | `422 UNPROCESSABLE` | CRYPTO_SHREDDING_REQUIRED |
| **N7-20** | Revocation | REVOCATION_BYPASS: Operating under an explicitly revoked decision token | `403 FORBIDDEN` | REVOCATION_ENFORCEMENT |
| **N7-21** | Killswitch | EMERGENCY_STOP_BYPASS: Executing runtime operations during ACTIVE_KILLSWITCH | `503 SERVICE UNAVAILABLE`| EMERGENCY_HARD_STOP_ACTIVE |
| **N7-22** | Token | TOKEN_REPLAY: Duplicate submission of single-use activation nonce | `409 CONFLICT` | NONCE_UNIQUENESS_ENFORCEMENT |
| **N7-23** | Token | TOKEN_TRANSFER: Passing activation token to unlisted operator | `403 FORBIDDEN` | OPERATOR_TOKEN_BINDING |
| **N7-24** | Token | TOKEN_SCOPE_ESCALATION: Submitting token with elevated learner quota | `400 BAD REQUEST` | QUOTA_BOUND_ENFORCEMENT |
| **N7-25** | Channel | UNAUTHORIZED_NOTIFICATION_CHANNEL: Attempting SMS/Email dispatch | `403 FORBIDDEN` | NOTIFICATION_MOCK_SANDBOX |
| **N7-26** | Schema | UNAUTHORIZED_DATA_CLASS: Ingesting payment or sensitive biometric fields | `422 UNPROCESSABLE` | DATA_MINIMIZATION_STRICT |
| **N7-27** | Capacity | PILOT_CAPACITY_BREACH: Exceeding 50 learners or 50 guardians | `422 UNPROCESSABLE` | PILOT_SCOPE_ENVELOPE_CEILING |
| **N7-28** | Duration | PILOT_DURATION_BREACH: Pilot operations extending beyond 30 days | `403 FORBIDDEN` | TIME_BOUND_PILOT_EXPIRY |
| **N7-29** | Feature | UNAPPROVED_FEATURE_ENABLEMENT: Enabling runtime AI without ADR | `403 FORBIDDEN` | ZERO_RUNTIME_AI_WITHOUT_ADR |
| **N7-30** | Stale Review | STALE_SECURITY_REVIEW: Security qualification evidence > 7 days old | `422 UNPROCESSABLE` | FRESH_SECURITY_AUDIT_REQ |
| **N7-31** | Stale Review | STALE_PRIVACY_REVIEW: Privacy review evidence > 7 days old | `422 UNPROCESSABLE` | FRESH_PRIVACY_AUDIT_REQ |
| **N7-32** | Stale DR | STALE_DR_EVIDENCE: PITR / Backup rehearsal older than baseline | `422 UNPROCESSABLE` | FRESH_DR_PROOF_REQUIRED |
| **N7-33** | Versioning | DECISION_VERSION_ROLLBACK: Reverting decision record to earlier version | `400 BAD REQUEST` | DECISION_VERSION_MONOTONIC |
| **N7-34** | Concurrency | SUPERSEDED_DECISION_REUSE: Operating under superseded decision | `409 CONFLICT` | ACTIVE_DECISION_UNIQUENESS |
| **N7-35** | Token | TOKEN_USED_AFTER_REVOCATION: Using activation token after manager REVOKE | `403 FORBIDDEN` | INSTANT_TOKEN_INVALIDATION |
| **N7-36** | Identity | CANDIDATE_IDENTITY_MISMATCH: Org legal reg ID does not match signed dossier | `422 UNPROCESSABLE` | ORG_IDENTITY_VERIFICATION |
| **N7-37** | Integrity | EVIDENCE_SNAPSHOT_HASH_MISMATCH: Hash of attached evidence does not match | `422 UNPROCESSABLE` | EVIDENCE_HASH_INTEGRITY |
| **N7-38** | Gate | APPROVAL_WITH_MISSING_HARD_GATE: Manager approving with 1 gate unfulfilled | `422 UNPROCESSABLE` | ZERO_UNMET_HARD_GATES |
| **N7-39** | Exception | GO_WITH_REQUIRED_EXCEPTION_PENDING: Issuing GO with unapproved exception | `422 UNPROCESSABLE` | EXCEPTION_DUAL_APPROVAL_REQ |
| **N7-40** | Exit | EXIT_WITH_UNRESOLVED_DATA_DISPOSITION: Closing pilot without crypto-shred proof | `422 UNPROCESSABLE` | CRYPTO_SHRED_RECEIPT_REQ |
