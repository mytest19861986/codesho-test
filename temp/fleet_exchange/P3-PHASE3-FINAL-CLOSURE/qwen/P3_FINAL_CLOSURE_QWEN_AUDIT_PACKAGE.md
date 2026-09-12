# PHASE 3 FINAL SYSTEM CLOSURE: QWEN AUDIT PACKAGE
**Task ID**: `P3-FINAL-SYSTEM-CLOSURE-AND-PRE-PILOT-GO-NO-GO`
**Branch**: `codex/phase3-product-platform-foundation`
**Commit SHA**: `1b8263592859972baee4c997757bd9d5aefddfe6`
**Target Agent**: Qwen
**Scope**: Epics 1 - 28 Integration, Invariants, Authorization, FSMs, and Anti-Ranking

---

## 1. Domain Architecture & Modular Monolith Invariants
1. **Separation of Concerns**:
   - Django 5.2 + DRF owns 100% of business logic, state transitions, domain validation, and transactional integrity.
   - Next.js App Router functions strictly as a presentation tier with zero direct database connectivity.
   - Celery tasks inherit `BaseTenantTask` and enforce fail-closed tenant scoping.
2. **Tenant Context Protocol**:
   - Inside `transaction.atomic()`, PostgreSQL GUC `app.current_tenant` is set before executing tenant queries.
   - All tenant queries fail closed if context is missing or malformed.
3. **Outbox Pattern**:
   - Outbox events (`PlatformEventOutbox`) are appended atomically within the business transaction.
   - Zero side-effects or external network calls inside database transactions.

---

## 2. Integrated FSM Lifecycles (Epics 1 - 28)
Every stateful entity implements strict, forward-only finite state machines:
- **Curriculum Authoring & Release (Epics 23-25)**:
  - `CurriculumPackage`: `DRAFT` -> `IN_REVIEW` -> `APPROVED` -> `RELEASED` / `ARCHIVED`.
  - `PedagogicalReleasePlan`: `PROPOSED` -> `CANARY_ACTIVE` -> `GENERAL_ACTIVE` -> `HALTED` / `SUPERSEDED`.
  - Direct jumps or unauthorized state transitions raise `ValidationError`.
- **Learning Operations & Check-ins (Epics 17-19)**:
  - `LearningCheckIn`: `SCHEDULED` -> `IN_PROGRESS` -> `COMPLETED` / `RESCHEDULED` / `CANCELLED`.
  - `SupportQueueItem`: `PENDING` -> `IN_REVIEW` -> `RESOLVED` / `DISMISSED`.
  - Timing ordering invariant: `chk_checkin_timing_order` (`actual_start >= scheduled_start` and `actual_start <= actual_end`).
- **Learner Coaching & Agency (Epic 16)**:
  - `CoachingSession`: `SCHEDULED` -> `IN_PROGRESS` -> `COMPLETED` / `CANCELLED`.
  - `SupportIntervention`: `PROPOSED` -> `ACCEPTED` / `DECLINED` -> `ACTIVE` -> `PAUSED` -> `COMPLETED`.
  - Strictly non-authoritative: `is_authoritative = False` enforced by schema check constraint `chk_intervention_non_authoritative`.
- **Governance & Access Review (Epics 26-28)**:
  - `AccessReviewCampaign`: `PLANNED` -> `ACTIVE` -> `CONCLUDED` / `CANCELLED`.
  - `AccessReviewDecision`: `MAINTAIN` / `REVOKE` / `RESTRICT`.

---

## 3. Negative Authorization & Principle of Least Privilege
- **Self-Grant Prevention**: `user_id == granted_by_id` raises `ValidationError` (`PRIVILEGE_SELF_GRANT: DENY`).
- **Role Isolation**:
  - `STUDENT` role cannot resolve support queues (HTTP 403).
  - Mentors cannot force-accept student interventions (HTTP 403: student agency invariant).
  - Cross-tenant user linkage is blocked across all foreign keys and memberships.
- **Audit Immutability**:
  - `MentorOperationsAuditLog`, `CoachingAuditLog`, `CurriculumAuditLog`, and `PrivilegedActionAudit` are strictly append-only.
  - Updates and deletes raise `ValidationError` at application layer and are prohibited by DB permissions.

---

## 4. Anti-Ranking & Child Protection Invariants
- Query parameters including `rank`, `rank_by`, `leaderboard`, `sort_by=score`, or `percentile` are rejected with HTTP 400 (`ranking_queries_prohibited`).
- Anti-Authoritative Decider: Automated models and algorithms are strictly advisory (`is_authoritative = False`).
- 21-Key PII Blacklist: Strictly blocks email, national ID, phone, SSN, card number, password, biometric, and raw credentials in free text and JSONB metadata.

---

## 5. Machine Test Evidence
- **Total Backend Tests**: 338 collected.
- **Pass Rate**: 337 passed, 1 skipped, 0 failed (100% pass rate).
- **PostgreSQL Migration Drift**: 0 unapplied, 0 drift (`No changes detected`).
