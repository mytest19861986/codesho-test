# Phase 6 Controlled Real Pilot Readiness: Qwen Runtime Audit Package

## Overview
- Architecture: 13-State Controlled Real Pilot Readiness FSM & 14 Pre-Admission Gate Domains
- Scope: Synthetic Rehearsal Only (1 Org / 5 Operators / 50 Learners / 50 Guardians)
- Real Data / Pilot: LOCKED (Zero Real PII)
- Execution Integrity: 51/51 PASS in `test_p6_admission_fsm.py` and `test_p6_negative_matrix.py`

## Core Artifacts
1. `models.py`:
   - `PilotLifecycleState`: 13 discrete states (`CANDIDATE` -> `DUE_DILIGENCE` -> `SECURITY_REVIEW` -> `PRIVACY_REVIEW` -> `OPERATIONAL_REVIEW` -> `TECHNICAL_READY` -> `MANAGER_DECISION_REQUIRED` -> `MANAGER_AUTHORIZED` -> `ACTIVATION_WINDOW` -> `ACTIVE` -> `SUSPENDED` -> `EXITING` -> `CLOSED`).
   - Self-approval denial invariant enforced across all readiness review gates.
   - Real-world cap: `MANAGER_DECISION_REQUIRED`.
2. `enterprise_governance_service.py`:
   - PostgreSQL advisory locking (`pg_advisory_xact_lock`).
   - 14-gate verification before entering `TECHNICAL_READY`.
   - Two-person dual custody with anti-replay nonce tracking.
3. `test_p6_admission_fsm.py`: Canonical 13-state FSM flow and rehearsal scenarios P6-R1 through P6-R20.
4. `test_p6_negative_matrix.py`: Complete negative matrix coverage N6-01 through N6-30.
