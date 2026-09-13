# PHASE 4: CONTROLLED PILOT PREPARATION BOUNDARY PLAN

**Document Identifier**: `P4_CONTROLLED_PILOT_PREPARATION_BOUNDARY_PLAN`
**Scope**: Architectural Guardrails, State Machines, Invariants, and Non-Negotiable Boundaries
**Phase**: Phase 4 Discovery
**Date**: 2026-09-13

---

## 1. System Boundaries & Invariant Enforcements
The Phase 4 preparation boundary enforces six mandatory architectural gates:

| Invariant Code | Gate Description | Mechanism | Violation Penalty |
|---|---|---|---|
| `P4-GATE-01` | **No Real PII / Synthetic Only** | Data scrubbers, regex validation, synthetic seed factory | Build Failure |
| `P4-GATE-02` | **Zero Automated Production Deploy** | Advisory state flag (`deployment_ready = False`), air-gapped CI deploy steps | Build Failure |
| `P4-GATE-03` | **Non-Competitive Learner UX** | Pure mastery rubrics, zero student sorting, zero leaderboards | Lint / Audit Rejection |
| `P4-GATE-04` | **Tenant Context Fail-Closed** | `SET LOCAL app.current_tenant`, PostgreSQL 17 FORCE RLS | `TenantSecurityError` |
| `P4-GATE-05` | **Immutable Operational Audit** | Append-only audit tables with REVOKE UPDATE, DELETE | SQL Permission Denied |
| `P4-GATE-06` | **Idempotent Migration Rollbacks** | Additive schema migrations, zero destructive drops in pilot | Migration Check Failure |

---

## 2. Release & Incident FSM Lifecycles

### Release Candidate (RC) Lifecycle
```
[DRAFT] -> (PREPARE_RC) -> [CANDIDATE_TAGGED] -> (RUN_SMOKE_TESTS) -> [VERIFIED_ON_STAGING]
                                      \
                                    (FAIL) -> [ABORTED]
```

### Incident Management Lifecycle
```
[DETECTED] -> (TRIAGE_SEV) -> [INVESTIGATING] -> (APPLY_MITIGATION) -> [MITIGATED] -> (POSTMORTEM) -> [RESOLVED]
```

---

## 3. Negative Boundary Test Matrix (Phase 4 Target)
- `N4-01`: Attempt to deploy to production without human signature token -> `FAIL_CLOSED`.
- `N4-02`: Injection of real child email/phone into staging telemetry -> `REDACTED_OR_REJECTED`.
- `N4-03`: Rollback of pilot release without database backup check -> `ABORTED`.
- `N4-04`: Cross-tenant telemetry query from operator console -> `BLOCKED_BY_RLS`.
- `N4-05`: Direct destructive deletion of audit log during incident triage -> `PERMISSION_DENIED`.
