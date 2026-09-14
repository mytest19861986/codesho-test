# P6_PILOT_ADMISSION_QWEN_PACKAGE.md - Codesho / SSD

**TO**: Qwen (Lead Systems Architect)
**FROM**: Codex (Implementation Engineer)
**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**SUBJECT**: Phase 6 Pilot Admission FSM, Dual-Custody Governance, Scope Envelope, and N6 Matrix Review

---

## 1. Architectural Overview & Context
Commander AI has authorized Phase 6 Discovery (`P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`). In this phase, we design the boundary architecture, admission FSM, governance controls, and negative invariants for a future, strictly controlled real pilot.

### Core Boundaries:
- `REAL_PILOT`: `LOCKED` (Awaiting explicit human manager approval).
- `REAL_DATA`: `SYNTHETIC_ONLY` (Zero real learners, guardians, or PII).
- `PRODUCTION_DEPLOY`: `LOCKED`.
- `MERGE_TO_MAIN`: `LOCKED_FOR_MANAGER`.

---

## 2. Review Artifacts Staged
Please audit the following staged architectural specifications:
1. `P6_REAL_PILOT_BOUNDARY_ARCHITECTURE.md` (Pilot Admission FSM, Scope Envelope, and Invariants).
2. `P6_REAL_PILOT_WRITE_MANIFEST.md` (Zero wildcards, exact paths for future implementation).
3. `P6_SYNTHETIC_DRESS_REHEARSAL_PLAN.md` (Scenarios P6-R1 through P6-R20).
4. `P6_NEGATIVE_TEST_MATRIX.md` (Negative cases N6-01 through N6-30).

---

## 3. Specific Focus Questions for Qwen
1. Does the canonical Pilot Admission FSM adequately prevent state transitions beyond `MANAGER_DECISION_REQUIRED` without cryptographic manager signature?
2. Are the concurrency, race condition, and replay protections (N6-22, N6-23, N6-24) robust against dual-custody race conditions?
3. Does the scope envelope adequately enforce bounded limits on organizations, operators, and learners?

---

## 4. Expected Review Format
Please provide your architectural assessment in the standard format:
```text
QWEN_PHASE6_DISCOVERY: PASS / BLOCK
QWEN_PHASE6_DISCOVERY_BLOCKERS: 0
FINDINGS:
- ...
```
