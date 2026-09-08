# Phase 3 Vertical Slice 10 Discovery Dossier (P3-VS10)

## 1. Executive Summary & Directive
- **Task ID**: `P3-VS10-LEARNING-COMMUNITY-DISCUSSION-AND-PEER-INTERACTION`
- **Scope Title (Farsi)**: سامانه تعاملات جمعی یادگیری، تالار گفتگوی کوهورت و درس و بازخورد همتایان
- **Authority**: `COMMANDER_P3_VS10_DISCOVERY_UNLOCK`
- **Status**: `DISCOVERY_COMPLETED / FLEET_CONSENSUS_CERTIFIED / AWAITING_RUNTIME_UNLOCK`
- **Working Tree**: `G:\project\codesho\codesho\worktrees\phase1-engineering-readiness` (Branch: `codex/phase3-product-platform-foundation`)

---

## 2. Triple Fleet Scope Consensus (100% Certified)

| Fleet Member | Review Focus & Responsibility | Verdict | Official Evidence / Response Artifact |
| :--- | :--- | :---: | :--- |
| **Gemini** | UX/UI, BiDi/RTL, WCAG 2.2 AA, Component Hierarchy | **`GEMINI_SCOPE: PASS`** | `scratch/gemini_vs10_response.txt` (Certified) |
| **GLM (Z.ai)** | DB Architecture, Composite FK Integrity, Audit Security, RLS Fail-Closed | **`GLM_SCOPE: PASS`** | `scratch/glm_vs10_final_pass_response.txt` (Certified v1.3) |
| **Qwen** | DDD Domain Models, Moderation Safety State Machine, Access Policy Matrix | **`QWEN_SCOPE: PASS`** | `scratch/qwen_vs10_final_pass_response.txt` (Certified v1.3) |

---

## 3. Core Architectural Contracts & Invariants (Boundary Plan v1.3)

1. **Child Safety & State Machine (Default PENDING)**:
   - Initial status on both `DiscussionThread` and `DiscussionComment` is strictly `default='PENDING'`.
   - DB CHECK constraint: `CHECK (status IN ('PENDING', 'APPROVED', 'FLAGGED', 'REMOVED'))`.
   - 4-Tier Visibility Matrix:
     - Authors & Mentors/Staff can see `PENDING`.
     - Peers/Students ONLY see `APPROVED`.
     - `FLAGGED` hidden from regular students.
     - `REMOVED` is strictly terminal for automated flows; `RESTORE` is staff-only and strictly audit-logged.

2. **Single-Path Scope Integrity (DB XOR)**:
   - On `DiscussionThread`, threads are scoped exclusively to either a Cohort OR a Lesson:
     `CHECK ((cohort_id IS NOT NULL AND lesson_id IS NULL) OR (cohort_id IS NULL AND lesson_id IS NOT NULL))`

3. **Hierarchical Comment & Same-Thread Guarantee**:
   - Comments enforce composite uniqueness and self-referencing foreign keys bound to the same thread:
     `UNIQUE (tenant_id, id, thread_id)`
     `FOREIGN KEY (tenant_id, parent_id, thread_id) REFERENCES learning_discussioncomment(tenant_id, id, thread_id) ON DELETE CASCADE`
   - Self-referencing prevention: `CHECK (parent_id IS NULL OR parent_id <> id)`.

4. **Audit Trail Immutability & Evidence Retention**:
   - `DiscussionModerationAction` table is strictly append-only:
     `REVOKE UPDATE, DELETE ON learning_moderationaction FROM app_role;`
   - Foreign keys to moderation targets (`target_thread_id`, `target_comment_id`) use `ON DELETE RESTRICT` to prevent destruction of compliance evidence.
   - Separate XOR constraint on moderation targets.

5. **Multi-Tenant Composite FK & RLS Isolation**:
   - Zero Bare UUIDs. Every reference enforces composite `(tenant_id, target_id)`.
   - On mentor endorsement SET NULL: `ON DELETE SET NULL (endorsed_by_id)` preserving `tenant_id`.
   - PostgreSQL 17 `FORCE ROW LEVEL SECURITY` with `NULLIF(current_setting('app.current_tenant', true), '')::uuid`.

6. **Active Enrollment Access Policy**:
   - `DiscussionAccessPolicy` service gate: Participation requires confirmed `Active Enrollment` in the corresponding cohort/course, enforcing strict RBAC.

7. **Atomic Reply Counters**:
   - `replies_count` is updated atomically and exclusively during transitions into or out of `APPROVED` status.

---

## 4. Comprehensive Negative & Boundary Test Matrix (N1-N20 + Addendums)

- **N1**: Cross-tenant thread read attempt -> Fail-Closed (404/Empty).
- **N2**: Cross-tenant comment insert -> DB Composite FK violation / RLS reject.
- **N3**: Unenrolled student creating thread -> 403 Forbidden.
- **N4**: Non-member viewing cohort discussion -> 403 / 404.
- **N5**: Student attempting to set `is_pinned = True` -> 403 Forbidden / ignored.
- **N6**: Student attempting to endorse comment (`is_mentor_endorsed`) -> 403 Forbidden.
- **N7**: Modifying or deleting audit record in `DiscussionModerationAction` -> DB Error (Permission Denied).
- **N8**: Comment reply referencing parent from different thread -> DB Foreign Key violation.
- **N9**: Thread with both `cohort_id` AND `lesson_id` set -> DB CHECK constraint violation.
- **N10**: Thread with neither `cohort_id` NOR `lesson_id` set -> DB CHECK constraint violation.
- **N11**: Peer viewing `PENDING` comment from another student -> Filtered out (Invisible).
- **N12**: Peer viewing `FLAGGED` or `REMOVED` comment -> Filtered out (Invisible).
- **N13**: Replying to a locked/closed thread (`is_locked = True`) -> 400/403 Rejected.
- **N14**: Comment attempting self-parenting (`parent_id = id`) -> DB CHECK violation.
- **N15**: Query execution with missing `app.current_tenant` GUC -> 0 rows / reject.
- **N16**: Query execution with blank GUC (`app.current_tenant = ''`) -> 0 rows (NULLIF behavior).
- **N17**: Non-UUID format in GUC -> Explicit DB Syntax/Type Error.
- **N18**: Attempting GUC mutation outside `transaction.atomic()` context -> Rejected.
- **N19**: Raw SQL insert with invalid status string -> Rejected by DB CHECK constraint.
- **N20**: Cohort cascade deletion with existing ModerationAction records -> DB RESTRICT holds evidence safely.

---

## 5. Write Manifest Scope (Target Files)

### Backend (Django 5.2 / PostgreSQL 17):
- `backend/apps/learning/models.py`: Add `DiscussionThread`, `DiscussionComment`, `DiscussionModerationAction`.
- `backend/apps/learning/migrations/000X_p3_vs10_learning_discussions.py`: DDL, Composite FKs, RLS policies, DB CHECKs.
- `backend/apps/learning/services/discussion_service.py`: `DiscussionAccessPolicy`, moderation workflows, atomic counter updates.
- `backend/apps/learning/views.py`: ViewSets for threads, comments, endorsements, pins, flags.
- `backend/apps/learning/serializers.py`: Sanitized serializers respecting 4-tier visibility matrix.
- `backend/apps/learning/tests/test_p3_vs10_discussions.py`: Comprehensive test suite implementing N1-N20.

### Contract & Documentation:
- `docs/openapi.yaml`: Register 6 community discussion endpoints.
- `docs/architecture/PHASE3_VS10_BOUNDARY_PLAN.md`: Authoritative v1.3 architecture specification.

### Frontend (Next.js App Router / TypeScript / BiDi):
- `frontend/src/components/discussion/DiscussionThreadList.tsx`: Filterable thread list with RTL/BiDi tags.
- `frontend/src/components/discussion/DiscussionThreadDetail.tsx`: 2-level hierarchical comment tree, mentor endorsement badges.
- `frontend/src/components/discussion/DiscussionReplyComposer.tsx`: Input form with child-safety pre-moderation notices.
- `frontend/src/components/discussion/ModerationActionModal.tsx`: Staff moderation tooling with audit logging.
