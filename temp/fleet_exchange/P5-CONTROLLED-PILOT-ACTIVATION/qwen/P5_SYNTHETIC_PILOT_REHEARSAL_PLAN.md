# P5 Synthetic Pilot Rehearsal Plan (Scenarios R1 - R16)

## Status: DISCOVERY_AND_ARCHITECTURE_ACTIVE
## Authority: COMMANDER_P5_DISCOVERY_EXECUTION_ORDER
## Baseline: `e8a9a421466de31b53c22191e3673a94a0eba78a` / `f999314505dbcb03e9f4c7f96186be11e9627e29`

---

### Overview
This plan specifies 16 comprehensive synthetic rehearsal scenarios (R1 through R16) covering the full operational, security, lifecycle, and recovery envelope of the pilot. All scenarios execute exclusively against synthetic data with zero real PII and zero production credentials.

---

### Scenario Specifications

#### R1: PILOT_TENANT_PROVISIONING
- **PRECONDITIONS**: Empty DB or staging schema; tenant catalog clean; operator authenticated.
- **ACTORS**: `TENANT_PROVISIONER`, `TECH_ARCHITECT`.
- **INPUTS**: Synthetic tenant identifier `tenant_synthetic_alpha`, synthetic domain config, quota limits.
- **EXPECTED_STATE_TRANSITIONS**: `DRAFT` -> `ELIGIBILITY_REVIEW` -> `PREREQUISITES_PENDING`.
- **EXPECTED_DENIALS**: Duplicate tenant ID denied; missing domain slug denied.
- **AUDIT_EVENTS**: `TENANT_PROVISIONING_INITIATED`, `TENANT_CONFIG_VALIDATED`.
- **ROLLBACK / RECOVERY**: Purge uncommitted tenant metadata.
- **PASS_CRITERIA**: Tenant isolated with private schema/RLS context; zero cross-tenant visibility.

#### R2: OPERATOR_ONBOARDING
- **PRECONDITIONS**: Tenant registered; operator credentials generated in staging vault.
- **ACTORS**: `SEC_ADMIN`, `OPERATOR_CANDIDATE`.
- **INPUTS**: Public key, MFA registration payload, least-privilege role assignment (`TENANT_OPERATOR`).
- **EXPECTED_STATE_TRANSITIONS**: `INVITED` -> `MFA_CHALLENGE` -> `ONBOARDED`.
- **EXPECTED_DENIALS**: Self-elevation to superuser denied; non-MFA login denied.
- **AUDIT_EVENTS**: `OPERATOR_INVITED`, `MFA_ENROLLED`, `OPERATOR_BOUND_TO_TENANT`.
- **ROLLBACK / RECOVERY**: Invalidate invitation token and session keys.
- **PASS_CRITERIA**: Operator can authenticate and access only designated synthetic tenant.

#### R3: SYNTHETIC_LEARNER_GUARDIAN_ACTIVATION
- **PRECONDITIONS**: Tenant active; synthetic consent policy published.
- **ACTORS**: `SYNTHETIC_GUARDIAN`, `SYNTHETIC_LEARNER`.
- **INPUTS**: Synthetic guardian name ("ولي فرضی"), synthetic learner ("دانش‌آموز تستی ۱"), dummy consent token.
- **EXPECTED_STATE_TRANSITIONS**: `CONSENT_REQUESTED` -> `CONSENT_GRANTED` -> `LEARNER_ENROLLED`.
- **EXPECTED_DENIALS**: Real national ID rejected; real phone/email rejected by regex scrubber.
- **AUDIT_EVENTS**: `SYNTHETIC_CONSENT_RECORDED`, `LEARNER_REGISTERED_ZERO_PII`.
- **ROLLBACK / RECOVERY**: Immediate cascade delete of synthetic profile on refusal.
- **PASS_CRITERIA**: Enrollment successful with 100% synthetic data; zero ranking computed.

#### R4: RELEASE_CANDIDATE_PROMOTION
- **PRECONDITIONS**: All CI gates pass; staging deployment running certified SHA.
- **ACTORS**: `RELEASE_OFFICER`, `TECH_LEAD`.
- **INPUTS**: Commit SHA, signed build manifest, immutable artifact hash.
- **EXPECTED_STATE_TRANSITIONS**: `RC_STAGED` -> `DUAL_SIGNATURE_VERIFIED` -> `PROMOTED_TO_PILOT`.
- **EXPECTED_DENIALS**: Unsigned commit promotion denied; single-approver promotion denied.
- **AUDIT_EVENTS**: `RC_SIGNATURE_VERIFIED`, `RELEASE_PROMOTED_DUAL_CUSTODY`.
- **ROLLBACK / RECOVERY**: Automated fallback to previous verified release tag.
- **PASS_CRITERIA**: Artifact promoted only after dual cryptographic signature verification.

#### R5: FAILED_HEALTH_GATE
- **PRECONDITIONS**: Running pilot instance; synthetic traffic active.
- **ACTORS**: `CHAOS_TESTER`, `AUTOMATED_HEALTH_MONITOR`.
- **INPUTS**: Injected DB latency spikes (>2000ms) or Redis disconnection.
- **EXPECTED_STATE_TRANSITIONS**: `HEALTHY` -> `DEGRADED` -> `CIRCUIT_BREAKER_TRIPPED`.
- **EXPECTED_DENIALS**: New request ingestion denied with HTTP 503 while degraded.
- **AUDIT_EVENTS**: `HEALTH_GATE_FAILED`, `CIRCUIT_BREAKER_ENGAGED`.
- **ROLLBACK / RECOVERY**: Route traffic to maintenance fallback; reset connection pool.
- **PASS_CRITERIA**: System fails closed gracefully without leaking partial state or errors.

#### R6: ROLLBACK
- **PRECONDITIONS**: Active incident or regression discovered in active release.
- **ACTORS**: `INCIDENT_COMMANDER`, `OPS_ENGINEER`.
- **INPUTS**: Rollback trigger command with exact string confirmation `CONFIRM-ROLLBACK`.
- **EXPECTED_STATE_TRANSITIONS**: `PILOT_ACTIVE` -> `ROLLBACK_INITIATED` -> `PRIOR_BASELINE_ACTIVE`.
- **EXPECTED_DENIALS**: Rollback without exact confirmation token denied; unauthorized actor denied.
- **AUDIT_EVENTS**: `ROLLBACK_TRIGGERED`, `STATE_REVERTED_TO_CERTIFIED_BASELINE`.
- **ROLLBACK / RECOVERY**: Standby environment holds traffic while active node rolls back.
- **PASS_CRITERIA**: Zero downtime or clean drain; full integrity verified against baseline SHA.

#### R7: SEV1_INCIDENT
- **PRECONDITIONS**: Normal operation; simulated core service crash or data boundary threat.
- **ACTORS**: `MONITORING_DAEMON`, `INCIDENT_COMMANDER`, `ON_CALL_OPS`.
- **INPUTS**: Injected critical alert: `DATA_STORE_CORRUPTION_SUSPECTED`.
- **EXPECTED_STATE_TRANSITIONS**: `NORMAL` -> `SEV1_DECLARED` -> `EMERGENCY_FREEZE_ACTIVE`.
- **EXPECTED_DENIALS**: Mutation requests denied during emergency freeze.
- **AUDIT_EVENTS**: `SEV1_ALERT_FIRED`, `PAGER_ENGAGED`, `EMERGENCY_FREEZE_ENABLED`.
- **ROLLBACK / RECOVERY**: Automated execution of emergency snapshot and container isolation.
- **PASS_CRITERIA**: Incident containment within $<30$ seconds; immutable audit trail preserved.

#### R8: SEV2_INCIDENT
- **PRECONDITIONS**: Normal operation; simulated secondary component outage (e.g. async reporting).
- **ACTORS**: `CELERY_MONITOR`, `SECONDARY_ON_CALL`.
- **INPUTS**: Celery worker queue backlog exceeding threshold (>10,000 tasks).
- **EXPECTED_STATE_TRANSITIONS**: `NORMAL` -> `SEV2_DECLARED` -> `WORKER_AUTO_SCALED`.
- **EXPECTED_DENIALS**: Dropping persistent tasks denied; silent failure denied.
- **AUDIT_EVENTS**: `SEV2_ALERT_FIRED`, `AUTOSCALE_SPAWNED`, `QUEUE_DRAINED`.
- **ROLLBACK / RECOVERY**: Queue restart from persistent Redis broker.
- **PASS_CRITERIA**: Core pilot remains operational; degraded subsystem recovers without data loss.

#### R9: CROSS_TENANT_ATTACK
- **PRECONDITIONS**: Two active synthetic tenants (`Tenant_A`, `Tenant_B`).
- **ACTORS**: `PENETRATION_TESTER` (acting as Tenant_A authenticated user).
- **INPUTS**: Direct object reference manipulation (IDOR) targeting Tenant_B resource IDs.
- **EXPECTED_STATE_TRANSITIONS**: No tenant state transition.
- **EXPECTED_DENIALS**: DB query blocked by PostgreSQL `FORCE RLS`; HTTP 404 / 403 returned.
- **AUDIT_EVENTS**: `SECURITY_VIOLATION_BLOCKED`, `CROSS_TENANT_ACCESS_DENIED`.
- **ROLLBACK / RECOVERY**: Temporary IP rate limit and session token revocation.
- **PASS_CRITERIA**: Zero bytes of Tenant_B data visible; intrusion attempt logged in audit table.

#### R10: TELEMETRY_PII_REJECTION
- **PRECONDITIONS**: Logger and OpenTelemetry collectors running.
- **ACTORS**: `CHAOS_TESTER`.
- **INPUTS**: API request containing fake National ID ("0012345678") and phone in header/payload.
- **EXPECTED_STATE_TRANSITIONS**: Payload processed by scrubbing pipeline.
- **EXPECTED_DENIALS**: Log emission with raw digits denied; plaintext storage denied.
- **AUDIT_EVENTS**: `PII_SCRUBBER_TRIGGERED`, `TELEMETRY_SANITIZED`.
- **ROLLBACK / RECOVERY**: Purge log buffer if unmasked pattern detected.
- **PASS_CRITERIA**: Log lines show `[REDACTED_NATIONAL_ID]`; regex confirms zero digits leaked.

#### R11: BACKUP_RESTORE
- **PRECONDITIONS**: Staging PostgreSQL database populated with synthetic test suite records.
- **ACTORS**: `BACKUP_CUSTODIAN`, `AUTOMATION_RUNNER`.
- **INPUTS**: Execution of `scripts/restore-verify.sh` against newly generated dump archive.
- **EXPECTED_STATE_TRANSITIONS**: `DUMPING` -> `ISOLATED_CONTAINER_SPINUP` -> `RESTORED` -> `VERIFIED`.
- **EXPECTED_DENIALS**: Restore into production DB denied; checksum mismatch dump denied.
- **AUDIT_EVENTS**: `BACKUP_INITIATED`, `CHECKSUM_VALIDATED`, `RESTORE_REHEARSAL_SUCCESS`.
- **ROLLBACK / RECOVERY**: Teardown sandbox container; alert on checksum discrepancy.
- **PASS_CRITERIA**: 100% record parity between source and restored sandbox; 0 errors.

#### R12: PITR_RECOVERY
- **PRECONDITIONS**: PostgreSQL WAL archiving active; continuous streaming to archive directory.
- **ACTORS**: `DBA_SPECIALIST`, `DISASTER_RECOVERY_LEAD`.
- **INPUTS**: Simulated drop table or corruption at $T_0$; target timestamp $T_{recovery} = T_0 - 10s$.
- **EXPECTED_STATE_TRANSITIONS**: `CRASH` -> `WAL_REPLAY` -> `CONSISTENT_SNAPSHOT_MOUNTED`.
- **EXPECTED_DENIALS**: Replay past recovery target denied; non-archived WAL replay denied.
- **AUDIT_EVENTS**: `PITR_TRIGGERED`, `WAL_SEGMENT_REPLAYED`, `TARGET_TIME_REACHED`.
- **ROLLBACK / RECOVERY**: Revert container volume to pre-rehearsal snapshot.
- **PASS_CRITERIA**: Database successfully recovered to exact target timestamp with transaction consistency.

#### R13: EMERGENCY_SUSPENSION
- **PRECONDITIONS**: Pilot tenant operating normally (`PILOT_ACTIVE`).
- **ACTORS**: `SECURITY_AUDITOR` or `HUMAN_MANAGER`.
- **INPUTS**: Emergency suspension invocation with reason code: `UNAUTHORIZED_PROBE_DETECTED`.
- **EXPECTED_STATE_TRANSITIONS**: `PILOT_ACTIVE` -> `SUSPENDED`.
- **EXPECTED_DENIALS**: All non-admin API requests rejected with HTTP 423 (Locked).
- **AUDIT_EVENTS**: `TENANT_EMERGENCY_SUSPENDED`, `SUSPENSION_REASON_LOGGED`.
- **ROLLBACK / RECOVERY**: Reactivation requires dual-custody re-certification review.
- **PASS_CRITERIA**: Tenant completely frozen instantly; read-only access for compliance audit only.

#### R14: OFFBOARDING
- **PRECONDITIONS**: Pilot tenant in `SUSPENDED` or `EXITING` state.
- **ACTORS**: `COMPLIANCE_OFFICER`, `TENANT_ADMIN`.
- **INPUTS**: Offboarding request with dual-signature verification token.
- **EXPECTED_STATE_TRANSITIONS**: `EXITING` -> `DATA_EXPORTED` -> `PURGED` -> `CLOSED`.
- **EXPECTED_DENIALS**: Partial purge denied; offboarding without data export receipt denied.
- **AUDIT_EVENTS**: `TENANT_OFFBOARDING_INITIATED`, `TENANT_EXPORT_SEALED`, `DATA_ZEROIZED`.
- **ROLLBACK / RECOVERY**: Hold encrypted export in cold escrow for 30 days.
- **PASS_CRITERIA**: All synthetic operational records erased from active DB; foreign keys cleaned.

#### R15: RETENTION_DISPOSITION
- **PRECONDITIONS**: Expired retention records identified in audit/telemetry tables ($T > TTL$).
- **ACTORS**: `RETENTION_DAEMON`.
- **INPUTS**: Automated retention cycle execution.
- **EXPECTED_STATE_TRANSITIONS**: `ACTIVE_RECORD` -> `PURGED`.
- **EXPECTED_DENIALS**: Deletion of records subject to legal hold denied.
- **AUDIT_EVENTS**: `RETENTION_SWEEP_EXECUTED`, `EXPIRED_RECORDS_PURGED`.
- **ROLLBACK / RECOVERY**: Log failed purge ids and retry on next hourly interval.
- **PASS_CRITERIA**: Expired records permanently removed; active and hold records untouched.

#### R16: FAILED_ACTIVATION_PREREQUISITE
- **PRECONDITIONS**: Tenant in `PREREQUISITES_PENDING` with 1 prerequisite incomplete (e.g. consent unverified).
- **ACTORS**: `MALICIOUS_OPERATOR` or `TEST_HARNESS`.
- **INPUTS**: Direct call to `POST /api/v1/governance/pilot/activate`.
- **EXPECTED_STATE_TRANSITIONS**: State remains `PREREQUISITES_PENDING` (no transition).
- **EXPECTED_DENIALS**: Activation rejected with HTTP 412 (Precondition Failed) and detailed missing checklist.
- **AUDIT_EVENTS**: `ACTIVATION_ATTEMPT_DENIED_MISSING_PREREQUISITES`.
- **ROLLBACK / RECOVERY**: No state change; audit event logged.
- **PASS_CRITERIA**: Activation fails closed; cannot bypass prerequisite validation.
