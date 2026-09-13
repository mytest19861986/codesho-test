# P5 Controlled Pilot Activation Discovery Dossier

## Status: DISCOVERY_AND_ARCHITECTURE_ACTIVE
## Authority: COMMANDER_P5_DISCOVERY_EXECUTION_ORDER
## Baseline: `e8a9a421466de31b53c22191e3673a94a0eba78a` / `f999314505dbcb03e9f4c7f96186be11e9627e29`

---

### 1. Executive Summary

In strict compliance with `COMMANDER_P5_DISCOVERY_EXECUTION_ORDER`, this dossier establishes the technical, architectural, operational, and governance foundation for **Phase 5: Controlled Pilot Activation**.

During Phase 5 Discovery:
- The canonical Pilot Lifecycle FSM is locked with a hard ceiling at `MANAGER_APPROVAL_REQUIRED`.
- The boundary between synthetic sandboxes and real data admission is mathematically secured with 11 prerequisite gates.
- All 16 synthetic rehearsal scenarios (R1 through R16) and 24 negative test scenarios (N5-01 through N5-24) are fully documented and formalized.
- The Write Manifest enforces zero wildcards and explicitly classifies prospective runtime files as design-only.
- All invariants (zero real PII, zero student ranking, zero production credentials, fail-closed RLS, and immutable audit logs) remain 100% intact.

---

### 2. Dossier Artifact Index

1. **Boundary & Architecture Plan**: [`docs/architecture/P5_CONTROLLED_PILOT_ACTIVATION_BOUNDARY_PLAN.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/P5_CONTROLLED_PILOT_ACTIVATION_BOUNDARY_PLAN.md)
   - Canonical 10-state Pilot Lifecycle FSM.
   - Non-overlapping Actor Matrix with strict Dual-Custody.
   - Real-Data Admission Gate and Data Minimization requirements.

2. **Pilot Go / No-Go Control Matrix**: [`docs/coordination/P5_PILOT_GO_NO_GO_CONTROL_MATRIX.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P5_PILOT_GO_NO_GO_CONTROL_MATRIX.md)
   - 17 Control domains (Security, Privacy, DB, RLS, Rollback, PITR, A11y, Legal, Offboarding).
   - Zero-exception hard-stop policy; any FAIL enforces `PILOT_DECISION: NO_GO`.

3. **Synthetic Pilot Rehearsal Plan**: [`docs/coordination/P5_SYNTHETIC_PILOT_REHEARSAL_PLAN.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P5_SYNTHETIC_PILOT_REHEARSAL_PLAN.md)
   - 16 End-to-end synthetic rehearsal scenarios (R1 through R16).
   - Explicit preconditions, actors, inputs, transitions, denials, audit events, rollback, and pass criteria.

4. **Negative Test Matrix**: [`docs/coordination/P5_NEGATIVE_TEST_MATRIX.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P5_NEGATIVE_TEST_MATRIX.md)
   - 24 Locked negative security and governance scenarios (N5-01 through N5-24).
   - Verification of fail-closed behavior, dual-custody enforcement, PII scrubbers, and anti-ranking rules.

5. **Write Manifest**: [`docs/coordination/P5_CONTROLLED_PILOT_ACTIVATION_WRITE_MANIFEST.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P5_CONTROLLED_PILOT_ACTIVATION_WRITE_MANIFEST.md)
   - Exact paths only, zero wildcards, 0 unreviewed paths.
   - Clear demarcation between active discovery artifacts and prospective runtime implementation.

---

### 3. Specialized Fleet Alignment

- **Qwen (Domain & Lifecycle Governance)**: Focuses on FSM transitions, dual custody, idempotency, replay safety, suspension, offboarding, and N5 business invariants.
- **GLM (Database & Infrastructure)**: Focuses on tenant provisioning, role topology (`codesho_runtime`), `FORCE RLS`, `NOBYPASSRLS`, additive DDL, audit immutability, backup/restore, and PITR.
- **Gemini (Human Factors & UI/UX)**: Focuses on the Pilot Activation Control Board, prerequisite checklist, Go/No-Go view, two-step frictional confirmations (`CONFIRM-ROLLBACK`), WCAG 2.2 AA touch targets $\ge 44$px, and RTL/BiDi `<bdi dir="ltr">`.

---

### 4. Mandatory Invariant State
- `REAL_CHILD_DATA`: **0**
- `REAL_GUARDIAN_DATA`: **0**
- `REAL_CONTACT_DATA`: **0**
- `STUDENT_RANKING`: **0**
- `PRODUCTION_CREDENTIALS`: **0**
- `PRODUCTION_DEPLOY`: **0**
- `MERGE_TO_MAIN`: **LOCKED_FOR_MANAGER**
- `P5_RUNTIME`: **LOCKED**
- `P5_FLEET_DISPATCH`: **LOCKED**
