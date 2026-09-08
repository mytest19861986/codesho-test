# Current Task: P3-VS6-DISCOVERY

## Active Phase 3 Vertical Slice 6 — 2026-09-08

- Status: `DISCOVERY_ACTIVE / RUNTIME_LOCKED`.
- Branch: `codex/phase3-product-platform-foundation`.
- Authority: `COMMANDER_P3_VS5_FINAL_DISPOSITION`.
- Previous Slices:
  - `P3-VS1`: COMPLETE_FINAL / CLOSED.
  - `P3-VS2`: COMPLETE_FINAL / CLOSED (Commit `112fe85`).
  - `P3-VS3`: COMPLETE_FINAL_ACCEPTED / CLOSED (Commit `936f971`).
  - `P3-VS4`: COMPLETE_FINAL_ACCEPTED / CLOSED (Commit `312a3f7`).
  - `P3-VS5`: COMPLETE_FINAL_ACCEPTED / CLOSED (Commit `5c43136`).
    * Cohort capacity enforcement via atomic `select_for_update`.
    * Course enrollment state machine and cycle-free prerequisite DAG.
    * PostgreSQL 17 FORCE RLS (0016, 0017).
    * `EnrollmentCard` and `CohortBadge` integrated into dashboard.
    * 12-screenshot regression sweep verified on all 6 routes.
- Current Invariants for P3-VS6:
  - Scope: `P3-VS6-STUDENT-ASSIGNMENT-SUBMISSION-AND-MENTOR-FEEDBACK-WORKFLOW`.
  - NO RUNTIME IMPLEMENTATION until Discovery is fully complete and approved.
  - Required Artifacts:
    * `docs/architecture/PHASE3_VS6_BOUNDARY_PLAN.md`
    * `docs/coordination/PHASE3_VS6_WRITE_MANIFEST.md` (ZERO_WILDCARDS: YES, EXACT_PATHS_ONLY: YES, UNREVIEWED_PATHS: 0)
  - Fleet Scope Reviews Required:
    * `Qwen 3.8 Max`: Assignment submission lifecycle, scoring rules, mentor review workflow.
    * `GLM 5.3`: PostgreSQL 17 FORCE RLS, cross-tenant isolation, atomic review commits, zero-PII auditability.
    * `Gemini 3.8`: Submission UI, mentor review queue, RTL, WCAG 2.2 AA.
  - Open Blockers: 0 (R3_R4 = 0).
