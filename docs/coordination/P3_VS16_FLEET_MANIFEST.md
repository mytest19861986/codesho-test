# P3-VS16 Targeted Triple Fleet Discovery Review Manifest

## Task Identifier
- Task: `P3-VS16-MENTOR-STUDENT-SUCCESS-COACHING-AND-INTERVENTION-WORKFLOW`
- Documents:
  - [`docs/coordination/P3_VS16_BOUNDARY_PLAN.md`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/P3_VS16_BOUNDARY_PLAN.md)
  - [`docs/architecture/p3_vs16_schema_ddl.sql`](file:///g:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/p3_vs16_schema_ddl.sql)

---

## 1. Domain-Specific Invariants Under Review

### For Qwen (Domain Logic, Lifecycle & Authorization):
1. **SupportIntervention FSM**: PROPOSED -> ACCEPTED / DECLINED -> ACTIVE -> COMPLETED (or PAUSED).
2. **Learner Agency Mandatory**: Mentors or system CANNOT force ACCEPTED status. Acceptance or decline is 100% student controlled.
3. **Anti-Punitive Guard**: Interventions only support academic scaffolding and study strategy. Zero disciplinary or punitive categories.
4. **Non-Authoritative AI**: `is_authoritative = FALSE` enforced at database and API levels.
5. **Authorization Matrix**: Students access only self-assigned sessions/interventions; mentors access only their assigned cohort students.

### For GLM (PostgreSQL 17 RLS, Concurrency & Security):
1. **Multi-Tenant Isolation**: Restricted strictly by `tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid` on all 5 tables.
2. **Security Gates**: `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY` applied across all tables.
3. **Composite Foreign Keys**: All cross-table relations enforce `(tenant_id, target_id)`. Zero bare single-column UUID foreign keys.
4. **Append-Only Immutability**: `learning_coachingauditlog` is strictly append-only.
5. **Concurrency Serialization**: `pg_advisory_xact_lock` used for state transitions on active coaching sessions and interventions.

### For Gemini (UI/UX, Psychology & Accessibility):
1. **Learner Agency UX**: Interventions presented as invitations for support, not mandates. Acceptance/decline buttons provide equal weight and respectful, supportive copy.
2. **Anti-Ranking Invariant**: Zero percentiles, zero leaderboards, zero peer comparison across mentor and student views.
3. **Growth Mindset & Non-Punitive Feedback**: Formative, supportive notes emphasizing strengths and concrete steps.
4. **Accessibility & Responsive Layout**: WCAG 2.2 AA, touch targets >= 44px, contrast >= 4.5:1, BiDi isolation with `<bdi dir="ltr">` for IDs/codes, RTL layout.
