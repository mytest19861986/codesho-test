# P8 Real Pilot Admission Discovery Dossier

## 1. Executive Summary & Directive Authority
- **TASK_ID**: `P8-REAL-PILOT-ADMISSION-DECISION-AND-CONTROLLED-ACTIVATION-PREPARATION-DISCOVERY`
- **STATUS**: `DISCOVERY_ACTIVE`
- **AUTHORITY**: Commander AI Directive (2026-09-16) following terminal Phase 7 Acceptance (`COMPLETE_FINAL_ACCEPTED`).
- **GOVERNANCE BOUNDARY**: All real-world actions remain strictly locked:
  - `REAL_PILOT`: LOCKED
  - `REAL_DATA`: LOCKED
  - `PRODUCTION`: LOCKED
  - `MERGE_TO_MAIN`: LOCKED_FOR_MANAGER
  - `DECISION_AUTHORITY`: EXCLUSIVELY HUMAN MANAGER (GO / NO_GO / DEFER)

## 2. P8 Admission Problem Statement
Phase 7 technically qualified the decision control planes (Decision Ledger, Cryptographic Scope Hash, Synthetic Tokens, Hard Stops).
Phase 8 Discovery defines the strict, fail-closed contracts, preconditions, data classifications, consent lifecycle models, operational readiness parameters, and emergency rollback pathways necessary for a human manager to safely evaluate real-world pilot admission without premature runtime exposure or unverified execution.

## 3. The 13 Canonical Discovery Artifacts
1. `docs/coordination/P8_REAL_PILOT_ADMISSION_DISCOVERY_DOSSIER.md` (Master Discovery Dossier)
2. `docs/architecture/P8_REAL_PILOT_ACTIVATION_ARCHITECTURE.md` (Controlled Activation Architecture)
3. `docs/coordination/P8_REAL_PILOT_WRITE_MANIFEST.md` (Strict Write Allow-list)
4. `docs/coordination/P8_MANAGER_GO_NO_GO_DEFER_PACKAGE.md` (Manager Decision Package Specification)
5. `docs/coordination/P8_REAL_PILOT_SCOPE_AND_LIMITS.md` (Bounded Capacity & Cohort Constraints)
6. `docs/coordination/P8_REAL_DATA_ADMISSION_MATRIX.md` (Zero-Unvetted Data Ingestion & Classifications)
7. `docs/coordination/P8_CONSENT_AND_AUTHORIZATION_READINESS.md` (Guardian/Student Consent & Revocation)
8. `docs/coordination/P8_PRODUCTION_READINESS_MATRIX.md` (Operational Gates, Secrets, Monitoring)
9. `docs/coordination/P8_OPERATIONS_SUPPORT_AND_INCIDENT_PLAN.md` (On-Call, SLA, Triage, Severity Matrix)
10. `docs/coordination/P8_CONTROLLED_ACTIVATION_PROTOCOL.md` (Sequential Cryptographic Activation Steps)
11. `docs/coordination/P8_EXIT_ROLLBACK_EMERGENCY_PLAN.md` (Instant Kill-Switch, Crypto-Shredding, DSR)
12. `docs/coordination/P8_SYNTHETIC_ACTIVATION_REHEARSAL.md` (End-to-End Synthetic Dry-Run Protocol)
13. `docs/coordination/P8_NEGATIVE_TEST_MATRIX.md` (30+ Fail-Closed Adversarial & Boundary Scenarios)

## 4. Key Architectural Invariants
- **Non-Waivable Hard Stops**: Any stale evidence (>24h), unapproved scope delta, or unapplied security policy automatically renders the candidate `NO_GO`.
- **Zero Weighted-Average Overrides**: Hard stops cannot be softened or bypassed by positive metrics.
- **Fail-Closed Admission**: Absence of an explicit, fresh, cryptographic token results in immediate rejection (`403 Forbidden` / `401 Unauthorized`).
- **Student Privacy & Non-Ranking**: Absolute prohibition of comparative student percentiles, public scoreboards, or automated punitive actions.
- **BiDi / RTL First-Class Compliance**: Strict isolation of technical keys, UUIDs, and hashes using `<bdi dir="ltr">` in RTL UI context.
