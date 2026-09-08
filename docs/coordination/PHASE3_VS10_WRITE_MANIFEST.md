# Phase 3 Vertical Slice 10 Write Manifest (P3-VS10)

## Task Identification
- **Slice**: P3-VS10: Learning Community Discussion and Peer Interaction
- **Status**: `DISCOVERY_COMPLETED / FLEET_CONSENSUS_CERTIFIED`
- **Security Posture**: Composite Foreign Keys, Force RLS, Append-Only Audit, Strict Child Safety (Pending First)

## Target Files & Operations

### 1. Database & Backend Models
- `backend/apps/learning/models.py`
  - `DiscussionThread`: `(tenant_id, cohort_id)` XOR `(tenant_id, lesson_id)`, `status` (PENDING default), `is_pinned`, `is_locked`, `replies_count`.
  - `DiscussionComment`: `(tenant_id, thread_id)`, `parent_id` (self-referencing composite FK), `status` (PENDING default), `is_mentor_endorsed`, `endorsed_by_id` (`ON DELETE SET NULL (endorsed_by_id)`).
  - `DiscussionModerationAction`: Append-only, `REVOKE UPDATE, DELETE`, target FKs `ON DELETE RESTRICT`.

### 2. Migrations
- `backend/apps/learning/migrations/000X_p3_vs10_learning_discussions.py`
  - Tables DDL, Composite FKs, DB CHECKs (XOR, status enum, parent_id <> id), FORCE RLS policies, Permissions revoke.

### 3. Service Layer & Access Control
- `backend/apps/learning/services/discussion_service.py`
  - `DiscussionAccessPolicy`: Enforces Active Enrollment, mentor/staff privileges.
  - Moderation service: `approve`, `flag`, `remove`, `restore` with mandatory audit logging.
  - Atomic counter maintenance for `replies_count`.

### 4. API & Serializers
- `backend/apps/learning/serializers.py`
  - Thread and Comment serializers enforcing 4-tier visibility matrix (Peers see only APPROVED).
- `backend/apps/learning/views.py`
  - ThreadViewSet, CommentViewSet, ModerationViewSet.
- `docs/openapi.yaml`
  - REST endpoint contracts.

### 5. Automated Tests (Fail-Closed Matrix N1-N20)
- `backend/apps/learning/tests/test_p3_vs10_discussions.py`
  - Tests covering N1 to N20.

### 6. Frontend UI Components (RTL / BiDi / WCAG 2.2 AA)
- `frontend/src/components/discussion/DiscussionThreadList.tsx`
- `frontend/src/components/discussion/DiscussionThreadDetail.tsx`
- `frontend/src/components/discussion/DiscussionReplyComposer.tsx`
- `frontend/src/components/discussion/ModerationActionModal.tsx`
