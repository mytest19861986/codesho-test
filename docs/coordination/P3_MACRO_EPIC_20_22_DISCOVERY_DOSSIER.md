# P3-MACRO-EPIC-20-22 Discovery Dossier

## 1. Executive Summary
- **Target Epic**: `P3-MACRO-EPIC-20-22-CURRICULUM-DELIVERY-AND-PROGRAM-OPERATIONS`
- **Delivery Mode**: `MACRO_FAST_ENTERPRISE`
- **Status**: DISCOVERY PHASE (Pre-Review Fleet Consensus)
- **Primary Objective**: Establish immutable curriculum versioning and snapshotting, deterministic cohort learning schedule orchestration, and operational program delivery monitoring without automated high-stakes learner actions or competitive ranking.

---

## 2. Invariant & Safety Checklist
- [x] **Published Immutability**: `PUBLISHED` curriculum versions cannot be modified or deleted.
- [x] **Snapshot Integrity**: Module and lesson snapshots are strictly immutable with `REVOKE UPDATE, DELETE`.
- [x] **Historical Rebind Prohibition**: Existing student progress retains original version foreign keys.
- [x] **Zero Real Third-Party Providers**: No calendar, SMS, or email provider integrations.
- [x] **Zero Automated Punitive Actions**: Absence from sessions generates zero punitive grading or disciplinary actions.
- [x] **Anti-Ranking Compliance**: Zero student leaderboards, zero competitive metrics, zero psychological profiling.
- [x] **PostgreSQL 17 FORCE RLS**: Mandatory across all 15 tables with fail-closed default.
- [x] **Zero Bare UUIDs**: All inter-table relations use composite foreign keys `(tenant_id, id)`.
- [x] **Append-Only Audit**: Audit logs have `REVOKE UPDATE, DELETE` enforced at SQL level.
- [x] **WCAG 2.2 AA & BiDi Isolation**: LTR data wrapped in `<bdi dir="ltr">`, 44px touch targets.

---

## 3. Fleet Review Focus Areas
1. **Qwen (Lifecycle & Invariants)**:
   - Verification of FSM transitions for versions (`DRAFT` -> `REVIEW` -> `APPROVED` -> `PUBLISHED` -> `RETIRED`) and sessions (`SCHEDULED` -> `IN_SESSION` -> `COMPLETED`/`RESCHEDULED`/`CANCELLED`).
   - Verification that historical submissions cannot be rebound to new releases.
2. **GLM (Database & Security Architecture)**:
   - Verification of PostgreSQL 17 FORCE RLS syntax, composite foreign keys, and absence of bare UUIDs.
   - Verification of check constraints (`chk_deliveryagg_non_authoritative`, `chk_curriculum_audit_xor`, semver format).
3. **Gemini (UX, BiDi & Accessibility)**:
   - Review of `CurriculumOperationsWorkspace` for RTL flow, keyboard navigability, 4.5:1 contrast, and absence of gamified ranking elements.
