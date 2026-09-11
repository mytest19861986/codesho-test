# Current Task: P3-MACRO-EPIC-17-19-RUNTIME-ACTIVE

## Active Phase 3 Macro Epic 17-19 — 2026-09-11

- Status: `RUNTIME_ACTIVE_CONCURRENT_EXECUTION`
- Mode: `MACRO_FAST_ENTERPRISE` (Authorized by Commander Directive `COMMANDER_P3_MACRO_EPIC_17_19_RUNTIME_UNLOCK: GRANTED`)
- Authority: `COMMANDER_P3_MACRO_EPIC_17_19_RUNTIME_UNLOCK: GRANTED` (12,086 chars full directive)
- Discovery Baseline: `40805bb` (`TRIPLE_FLEET_UNANIMOUS_PASS: Qwen PASS, Gemini PASS, GLM PASS`)
- Active Epic ID: `P3-MACRO-EPIC-17-19-MENTOR-OPERATIONS-AND-PROGRAM-SUCCESS`
- Persian Title: مرکز عملیات منتور، هماهنگی تداوم یادگیری و هوشمندی موفقیت برنامه آموزشی
- English Title: Mentor Operations, Learning Continuity Orchestration & Program Success Intelligence
- Sub-Slices Included in One Delivery Package:
  1. `P3-VS17-MENTOR-CASELOAD-AND-SUPPORT-QUEUE-OPERATIONS`: مدیریت بار کاری منتور و صف عملیات حمایتی دانش‌آموزان
  2. `P3-VS18-LEARNING-CHECKINS-SCHEDULING-AND-FOLLOWUP-ORCHESTRATION`: برنامه‌ریزی جلسات پیگیری، چک‌این‌های آموزشی و هماهنگی اقدامات بعدی
  3. `P3-VS19-PROGRAM-SUCCESS-OPERATIONS-AND-SUPPORT-ANALYTICS`: داشبورد عملیاتی موفقیت برنامه و تحلیل اثربخشی حمایت آموزشی
- Key Directives:
  - Six Canonical Models: `MentorCaseloadAssignment`, `SupportQueueItem`, `LearningCheckIn`, `FollowUpCommitment`, `ProgramSupportAggregate`, `MentorOperationsAuditLog`.
  - Service Layer: `mentor_operations_service.py` with transactional Outbox and FSM transitions.
  - Endpoints: `/api/v1/learning/mentor/...` for caseload, check-ins, and analytics.
  - Mandatory Negative Proof Matrix: N1 to N33 pass criteria.
  - Zero wildcards, anti-ranking, fail-closed tenant isolation, learner agency, child safety.
