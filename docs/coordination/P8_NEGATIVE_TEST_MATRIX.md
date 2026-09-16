# P8 Negative Test Matrix (35 Fail-Closed Scenarios)

| Scenario ID | Test Name | Adversarial / Failure Condition | Expected Fail-Closed Behavior |
|---|---|---|---|
| N8-01 | UNAUTHORIZED_MANAGER | Token issuance attempted by non-manager or automated script | 403 Forbidden (`ERR_UNAUTHORIZED_MANAGER`) |
| N8-02 | SELF_APPROVAL_DENIED | Manager approves an admission package they created | 400 Bad Request (`ERR_SELF_APPROVAL_PROHIBITED`) |
| N8-03 | STALE_EVIDENCE_GATE | Evidence snapshot is >24 hours old | Rejection with `REQUIRED_EVIDENCE_STALE` |
| N8-04 | EXPIRED_EVIDENCE_GATE | Required compliance snapshot marked EXPIRED | Hard stop NO_GO (`ERR_EVIDENCE_EXPIRED`) |
| N8-05 | SCOPE_HASH_MISMATCH | Runtime payload scope hash differs from approved hash | Immediate halt (`SCOPE_HASH_MISMATCH`) |
| N8-06 | RELEASE_MISMATCH | Submitted release candidate commit SHA differs from signed RC | Immediate halt (`RELEASE_MISMATCH`) |
| N8-07 | TENANT_MISMATCH | Activation token submitted to different tenant domain | 404/403 Cross-tenant access denied |
| N8-08 | OPERATOR_MISMATCH | Nonce executed by operator other than `authorized_operator_id` | 403 Forbidden (`OPERATOR_UNAUTHORIZED`) |
| N8-09 | TOKEN_REPLAY | Re-submitting an already consumed activation token | 409 Conflict (`TOKEN_ALREADY_CONSUMED`) |
| N8-10 | TOKEN_EXPIRED | Token submitted after `token_expiry` timestamp | 401 Unauthorized (`TOKEN_EXPIRED`) |
| N8-11 | TOKEN_REVOKED | Token submitted after manager issued revocation | 403 Forbidden (`TOKEN_REVOKED`) |
| N8-12 | PREMATURE_ACTIVATION | Submission prior to `activation_window_start` | 400 Bad Request (`ACTIVATION_WINDOW_NOT_OPEN`) |
| N8-13 | POST_WINDOW_ACTIVATION | Submission after `activation_window_end` | 400 Bad Request (`ACTIVATION_WINDOW_CLOSED`) |
| N8-14 | CAPACITY_BREACH | Admitted cohort size exceeds pilot quota (e.g. >50 students) | 422 Unprocessable (`PILOT_CAPACITY_EXCEEDED`) |
| N8-15 | DURATION_BREACH | Pilot period requested exceeds authorized maximum (e.g. >14 days) | 422 Unprocessable (`PILOT_DURATION_EXCEEDED`) |
| N8-16 | UNAPPROVED_FEATURE | Enabling features outside approved scope (e.g. live payments) | Immediate block (`UNAPPROVED_FEATURE_FLAGS`) |
| N8-17 | UNAPPROVED_DATA_CLASS | Admission of unvetted sensitive biometric or financial fields | Hard rejection (`DATA_CLASSIFICATION_VIOLATION`) |
| N8-18 | UNAPPROVED_CHANNEL | Invoking external SMS/Email without human manager signoff | Mock/Null driver fallback (`CHANNEL_LOCKED`) |
| N8-19 | CONSENT_MISSING | Admitting minor student without guardian consent record | Admission denied (`GUARDIAN_CONSENT_REQUIRED`) |
| N8-20 | CONSENT_EXPIRED | Guardian consent timestamp exceeds annual validity | Admission paused (`CONSENT_EXPIRED`) |
| N8-21 | CONSENT_REVOKED | Guardian revokes consent mid-pilot | Immediate student de-provisioning & data lock |
| N8-22 | OPEN_CRITICAL_INCIDENT | P0/P1 security incident unresolved in ledger | Hard stop (`ACTIVE_INCIDENT_BLOCKER`) |
| N8-23 | BACKUP_STALE | PostgreSQL daily physical backup is >24h old | Activation gate fails closed (`BACKUP_NOT_CURRENT`) |
| N8-24 | PITR_UNQUALIFIED | Point-in-time recovery rehearsal unverified within 7 days | Activation gate fails closed (`PITR_UNQUALIFIED`) |
| N8-25 | ROLLBACK_NOT_READY | Automated down-migration or crypto-shredder script unverified | Activation blocked (`ROLLBACK_PLAN_INCOMPLETE`) |
| N8-26 | PROD_CREDENTIAL_LEAK | Raw secrets detected in admission payload or manifest | Rejection & security audit trigger (`PII_SECRET_DETECTED`) |
| N8-27 | ORG_MISMATCH | Pilot token submitted for non-pilot organization | 403 Forbidden (`ORGANIZATION_NOT_IN_PILOT_REGISTRY`) |
| N8-28 | DECISION_ROLLBACK | Attempting to mutate an existing terminal GO/NO_GO record | Database trigger error (`MUTATION_NOT_PERMITTED`) |
| N8-29 | SUPERSEDED_DECISION | Attempting to consume a token tied to a superseded decision | 409 Conflict (`DECISION_SUPERSEDED`) |
| N8-30 | AUDIT_MUTATION_ATTEMPT | Attempting to update or delete rows in security audit log | PostgreSQL trigger raises exception (`IMMUTABLE_LOG`) |
| N8-31 | CROSS_TENANT_LEAKAGE | Querying admission state across tenants | RLS zero-row return |
| N8-32 | PEER_RANKING_ATTEMPT | UI or API attempting to render student ranking/leaderboard | Hard architectural exception (`STUDENT_RANKING_PROHIBITED`) |
| N8-33 | EMERGENCY_KILL_SWITCH | Operator triggers emergency kill switch | Immediate instant revocation across all pilot tokens |
| N8-34 | CRYPTO_SHRED_RECEIPT | Verifying unalterable receipt emission on exit deletion | Must generate immutable `SHRED-RECEIPT-*` |
| N8-35 | BIDI_CORRUPTION_ATTEMPT| Injecting LTR tokens into RTL strings without `<bdi>` wrapper | UI accessibility & BiDi isolation assertion failure |
