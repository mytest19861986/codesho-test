# P3-VS16 Discovery Dossier: Mentor-Student Success Coaching & Intervention Workflow
**Task ID**: `P3-VS16-MENTOR-STUDENT-SUCCESS-COACHING-AND-INTERVENTION-WORKFLOW`  
**Git Branch**: `codex/phase3-product-platform-foundation`  
**Certified Commit**: `3f9dbc3`  
**Status**: `DISCOVERY_COMPLETE` — **TRIPLE FLEET UNANIMOUS PASS ACHIEVED**  

---

## 1. Executive Summary & Triple Fleet Unanimous Certification

The Discovery phase for **P3-VS16** is 100% complete and certified across all specialized fleet reviewers:

| Reviewer / Fleet Node | Domain Scrutiny | Verdict | Primary Certification Evidence |
|:---|:---|:---:|:---|
| **Gemini** (UI/UX & Psychology) | Learner Agency First, non-punitive intervention, WCAG 2.2 AA accessible forms, RTL BiDi layout isolation (`<bdi dir="ltr">`) | **`GEMINI_SCOPE: PASS`** | Verified in DOM (`gemini.google.com/app/1287c12be5b401b2`) |
| **Qwen** (Domain & Business Logic) | FSM transition matrices, student agency enforcement, non-authoritative AI boundary, 13-key PII exclusion | **`QWEN_SCOPE: PASS`** | Verified in DOM (`chat.qwen.ai/c/9c6c740b-026d-47b5-b89b-86ff710c88c5`) |
| **GLM** (PostgreSQL 17 RLS & Security) | Composite FKs, Permissive GUC RLS, FORCE RLS, Exact XOR targets, Append-only DB revoke, Full Union PII blacklist | **`GLM_SCOPE: PASS`** (v1.1 Canonical Addressed B1-B5, M1-M6) | Certified in commit `c058eff` & `3f9dbc3` |

---

## 2. Certified Architecture & Deliverables

1. **Boundary Plan v1.1-CANONICAL**:
   - Location: [`docs/coordination/P3_VS16_BOUNDARY_PLAN.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P3_VS16_BOUNDARY_PLAN.md)
   - Scope: §2.1 Prerequisites, FSM matrices (CoachingSession, SupportIntervention, FollowUpAction), Actor & Authorization Matrix, and full N1–N28 Negative Proof Matrix.

2. **PostgreSQL 17 Schema DDL Specification v1.1-CANONICAL**:
   - Location: [`docs/architecture/p3_vs16_schema_ddl.sql`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/p3_vs16_schema_ddl.sql)
   - Certified Invariants:
     - `learning_coachingsession`: Composite FKs (`student`, `mentor`, `plan`, `insight`), status-time consistency, 13-key Union PII exclusions.
     - `learning_coachingnote`: Append-only discipline (`REVOKE UPDATE, DELETE`), Composite FK to session and author, regex PII filtration.
     - `learning_supportintervention`: Learner Agency First (`is_authoritative = FALSE`), mandatory non-punitive categories, student feedback bounds.
     - `learning_followupaction`: Exact origin XOR (`num_nonnulls(intervention_id, session_id) = 1`), skip reason length and PII rules.
     - `learning_coachingauditlog`: Dedicated targets (`target_session_id`, `target_intervention_id`, `target_action_id`), `DEFERRABLE INITIALLY DEFERRED` FKs, Append-only DB revocation (`REVOKE UPDATE, DELETE FROM app_role, PUBLIC`).
     - Security: `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY` across all 5 tables, Permissive GUC policy matching platform standards.

---

## 3. Negative Proof Matrix (N1 – N28) Implementation Gate

All 28 negative test specifications are registered as mandatory acceptance criteria for the implementation phase:
- **N1–N2, N25–N26**: Complete four-point Tenant Isolation GUC suite (unset GUC, foreign tenant UUID, empty string fail-closed, malformed string).
- **N3–N5**: Composite FK integrity and cross-tenant leakage rejection.
- **N6**: System non-authoritative boundary violation rejection (`is_authoritative = FALSE`).
- **N7**: Supportive category enforcement (anti-punitive invariant).
- **N8**: Mandatory learner agency consent gate (mentor/system cannot force `ACCEPTED`).
- **N9–N10**: Database-level append-only revocation enforcement (`REVOKE UPDATE, DELETE`).
- **N11**: Deferrable FK audit protection (`ON DELETE NO ACTION DEFERRABLE`).
- **N12–N13**: Text and headline length bounds.
- **N14–N16**: Free-text regex PII and JSONB `?|` blacklist validation.
- **N17–N18**: FSM transition guards and completion consistency.
- **N19**: Strict Anti-Ranking API query filter rejection.
- **N20**: Cross-cohort mentor authorization guard.
- **N21**: Concurrency serialization via transaction advisory locking (`pg_advisory_xact_lock`).
- **N22**: Session timing consistency (`started_at <= completed_at`).
- **N23**: Follow-up action exact origin XOR verification.
- **N24**: Clean tenant cascade wipe without deadlock.
- **N27**: Zero Bare UUID audit verification.
- **N28**: BiDi isolation `<bdi dir="ltr">` UI verification.

---

## 4. Request for Runtime Implementation Unlock

With Discovery specifications committed, verified, and aligned across all fleet requirements:
- **Formal Request**: `COMMANDER_P3_VS16_RUNTIME_UNLOCK`
- **Next Phase**: Full backend Django implementation (models, migrations, serializers, views, services) and Next.js frontend RTL dashboard for P3-VS16.
