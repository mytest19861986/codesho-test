# COMPONENT_USAGE_MATRIX.md — CodeSho Component Cross-Role Usage Matrix

> **Wave 5.12 Phase 3 Deliverable**  
> **Status**: COMPONENT_USAGE_MAPPED ✅  
> **Hard Rule**: `Component Availability ≠ Permission` (UI visibility does not grant domain authorization)

---

## 1. Cross-Role Matrix

| Component Name | Student (`/student`) | Mentor (`/mentor`) | Parent (`/parent`) | Admin (`/admin`) | Governance Constraints |
|---|---|---|---|---|---|
| `AppShell` | ✅ Active (Light Pill) | ✅ Active (Deep Pill) | ✅ Active (Soft Pill) | ✅ Active (Dark Navy) | Role theme switches visual styling; layout architecture remains invariant |
| `Card` (Base) | ✅ Active | ✅ Active | ✅ Active | ✅ Active | Universal container; padding scales responsively |
| `GrowthCard` | ✅ Primary Owner | ⚠️ Read Context Only | ✅ Primary Read View | ❌ Forbidden | Never accessible to Admin; anti-ranking enforced |
| `PortfolioCard` | ✅ Owner (Upload/Edit) | ✅ Review Context | ❌ (Viewed as Narrative) | ❌ Forbidden | Student owns artifacts; mentors review; parents see story |
| `LearningTimeline` | ✅ Full Personal View | ✅ Student Context View | ✅ Milestone View | ⚠️ Aggregate Metrics | Filtered to appropriate telemetry level per persona |
| `ReflectionPanel` | ✅ Private Student Space| ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | Strictly confidential to the learner |
| `MentorWorkspace` | ❌ Forbidden | ✅ Primary Owner | ❌ Forbidden | ❌ Forbidden | Confidential coaching and rubric grading zone |
| `AuditPanel` / Explorer | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | ✅ Primary Owner | Immutable governance logs; admin only |
| `TenantHealthCard` | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | ✅ Primary Owner | System operational controls |
| `NotificationPopover`| ✅ Personal Alerts | ✅ Submission Alerts | ✅ Milestone Updates | ✅ System Alerts | Scoped strictly to current user context |
| `Button` / `Input` | ✅ Standard Controls | ✅ Standard Controls | ✅ Standard Controls | ✅ Standard Controls | Core atomic controls shared universally |

---

## 2. Anti-Ranking & Anti-Leakage Rules
1. **Zero Cross-Student Comparison**: `GrowthCard` must never display cohort percentiles, leaderboard standings, or competitive scores.
2. **Pedagogical Privacy Firewall**: Private notes in `MentorWorkspace` never project into `Parent` or `Student` views without explicit published status.
3. **Tenant Context Boundary**: Every component query must fail closed if tenant isolation header is missing.
