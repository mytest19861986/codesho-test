# Phase 3 Vertical Slice 10 Boundary Plan (P3-VS10) - Version 1.3

## 1. Context and Authority
- **Authority**: `COMMANDER_P3_VS10_DISCOVERY_UNLOCK` (Official Commander Directive Issued)
- **Task ID**: `P3-VS10-LEARNING-COMMUNITY-DISCUSSION-AND-PEER-INTERACTION`
- **Scope Title (Farsi)**: سامانه تعاملات جمعی یادگیری، تالار گفتگوی کوهورت و درس و بازخورد همتایان
- **Status**: `DISCOVERY_ACTIVE / RUNTIME_LOCKED` (Strictly No Code Changes until Fleet Approval & Commander Runtime Unlock)
- **Fundamental Invariants**:
  * **Runtime Locked**: Zero runtime code modification before triple fleet PASS and Commander Runtime Unlock.
  * **Zero PII**: Strictly synthetic student/peer identifiers, author UUIDs, and sanitized educational community content.
  * **Fail-Closed Multi-Tenancy & NOBYPASSRLS**: Strict PostgreSQL 17 `ALTER TABLE ... FORCE ROW LEVEL SECURITY` on all tenant-scoped tables with tenant isolation policy:
    ```sql
    CREATE POLICY p3_vs10_tenant_isolation ON <table>
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
    ALTER TABLE <table> FORCE ROW LEVEL SECURITY;
    ```
  * **Tenant Session Protocol (SET LOCAL)**: Handled exclusively inside `transaction.atomic()` via `SET LOCAL app.current_tenant = %s`.
  * **Strict Child Safety & B1 Moderation Enforcement**: Initial state is strictly `PENDING` (`default='PENDING'`). No student-generated content is publicly visible before moderator review. Peered learners see ONLY `APPROVED` content.
  * **Single-Path Cohort/Lesson Scope (DB XOR)**: Discussions are strictly bound to either a specific `Cohort` or `Lesson` within the verified active enrollment of the student.
  * **Complete Composite Foreign Key Integrity (Zero Bare UUIDs)**: All relational columns (`tenant_id`, `cohort_id`, `lesson_id`, `author_id`, `parent_id`, `thread_id`, `endorsed_by_id`, `target_thread_id`, `target_comment_id`, `actor_id`) are strictly bound by DB-level Composite Foreign Keys `(tenant_id, target_id)`.
  * **Thread-Scoped Comment Hierarchy (Parent in Same Thread)**: Comments must belong to the exact same thread as their parent comment.
  * **Immutable Audit Trail (ModerationAction)**: Strict Append-Only audit table. UPDATE and DELETE permissions are permanently revoked (`REVOKE UPDATE, DELETE ON learning_moderationaction FROM app_role;`). Target references are protected via `ON DELETE RESTRICT`.

---

## 2. Core Domain Architecture & Data Models (Zero Bare UUIDs)

### 2.1 Prerequisite Unique Constraints Verification (From VS01-VS09)
The following composite unique constraints are verified as present in the database from previous slices:
- `learning_cohort (tenant_id, id)`: Guaranteed by `UNIQUE (tenant_id, id)`
- `learning_lesson (tenant_id, id)`: Guaranteed by `UNIQUE (tenant_id, id)`
- `platform_tenant_tenantmembership (tenant_id, user_id)`: Guaranteed by `UNIQUE (tenant_id, user_id)`

### 2.2 `DiscussionThread` (رشته گفتگوی درس/کوهورت)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `cohort`: ForeignKey(`learning.Cohort`, on_delete=CASCADE, null=True, blank=True, related_name="discussion_threads")
- `lesson`: ForeignKey(`learning.Lesson`, on_delete=CASCADE, null=True, blank=True, related_name="discussion_threads")
- `author_id`: UUIDField(db_index=True)
- `title`: CharField(max_length=200)
- `content`: TextField()  # Sanitized, Max 10,000 chars, no raw HTML
- `is_pinned`: BooleanField(default=False)
- `is_closed`: BooleanField(default=False)
- `moderation_status`: CharField(max_length=16, choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('FLAGGED', 'Flagged'), ('REMOVED', 'Removed')], default='PENDING')
- `replies_count`: PositiveIntegerField(default=0)  # Atomic count of APPROVED replies exclusively
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- **Unique Constraint for Referencing**:
  * `UNIQUE (tenant_id, id)`
- **Composite Foreign Key Definitions (PostgreSQL 17)**:
  * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, lesson_id) REFERENCES learning_lesson (tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, author_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
- **DB Check Constraints**:
  * `CHECK ((cohort_id IS NOT NULL AND lesson_id IS NULL) OR (cohort_id IS NULL AND lesson_id IS NOT NULL))` (Strict XOR scope).
  * `CHECK (length(title) <= 200)`
  * `CHECK (length(content) <= 10000)`
  * `CHECK (moderation_status IN ('PENDING', 'APPROVED', 'FLAGGED', 'REMOVED'))`

### 2.3 `DiscussionComment` (پاسخ‌ها و کامنت‌های رشته گفتگو)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `thread`: ForeignKey(`DiscussionThread`, on_delete=CASCADE, related_name="comments")
- `parent`: ForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name="replies")
- `author_id`: UUIDField(db_index=True)
- `content`: TextField()  # Sanitized, Max 5,000 chars
- `is_mentor_endorsed`: BooleanField(default=False)
- `endorsed_by_id`: UUIDField(null=True, blank=True)
- `endorsed_at`: DateTimeField(null=True, blank=True)
- `moderation_status`: CharField(max_length=16, choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('FLAGGED', 'Flagged'), ('REMOVED', 'Removed')], default='PENDING')
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- **Composite Foreign Key Definitions & Constraints (PostgreSQL 17)**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, id, thread_id)`
  * `FOREIGN KEY (tenant_id, thread_id) REFERENCES learning_discussionthread (tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, parent_id, thread_id) REFERENCES learning_discussioncomment (tenant_id, id, thread_id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, author_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
  * `FOREIGN KEY (tenant_id, endorsed_by_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE SET NULL (endorsed_by_id)`
- **DB Check Constraints**:
  * `CHECK (length(content) <= 5000)`
  * `CHECK (moderation_status IN ('PENDING', 'APPROVED', 'FLAGGED', 'REMOVED'))`

### 2.4 `ModerationAction` (جدول لاگ و حسابرسی اقدامات مدیرتی و نظارت بر محتوا - Append Only)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `target_thread`: ForeignKey(`DiscussionThread`, on_delete=RESTRICT, null=True, blank=True, related_name="moderation_actions")
- `target_comment`: ForeignKey(`DiscussionComment`, on_delete=RESTRICT, null=True, blank=True, related_name="moderation_actions")
- `actor_id`: UUIDField(db_index=True)
- `action_type`: CharField(max_length=32, choices=[('APPROVE', 'Approve'), ('FLAG', 'Flag'), ('REMOVE', 'Remove'), ('RESTORE', 'Restore'), ('ENDORSE', 'Endorse'), ('PIN', 'Pin'), ('CLOSE', 'Close')])
- `reason`: TextField(blank=True, default='')
- `created_at`: DateTimeField(auto_now_add=True)
- **Composite Foreign Key Definitions (PostgreSQL 17)**:
  * `FOREIGN KEY (tenant_id, target_thread_id) REFERENCES learning_discussionthread (tenant_id, id) ON DELETE RESTRICT`
  * `FOREIGN KEY (tenant_id, target_comment_id) REFERENCES learning_discussioncomment (tenant_id, id) ON DELETE RESTRICT`
  * `FOREIGN KEY (tenant_id, actor_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
- **DB Check Constraint**:
  * `CHECK ((target_thread_id IS NOT NULL AND target_comment_id IS NULL) OR (target_thread_id IS NULL AND target_comment_id IS NOT NULL))`
- **Append-Only Immutability Enforcement (DDL Level)**:
  * `REVOKE UPDATE, DELETE ON learning_moderationaction FROM app_role;`

---

## 3. Discussion Access Policy & Enrollment Guards (`DiscussionAccessPolicy`)
Access is strictly enforced at the service layer prior to query or mutation:
1. **`can_create_thread(user, cohort_or_lesson)`**:
   - User must have active tenant membership.
   - For cohort: Student must have `Enrollment(cohort=cohort, status='ACTIVE')`, or user must be assigned Mentor/Admin.
   - For lesson: Student must have active enrollment in the cohort containing the lesson's course.
2. **`can_read_thread(user, thread)`**:
   - Must belong to the same tenant (`app.current_tenant`).
   - Thread must be `APPROVED` (or user is author or mentor/staff).
   - User must be enrolled in the related cohort or lesson.
3. **`can_comment(user, thread)`**:
   - Thread must not be `is_closed=True`.
   - Thread must not be `moderation_status='REMOVED'`.
   - User must hold active enrollment or mentor role.
4. **`can_moderate(user, thread_or_comment)`**:
   - User must have role `MENTOR` or `ADMIN` within the tenant.

---

## 4. Moderation State Machine & Child Safety Visibility Matrix
```
       [PENDING] (Default for all newly submitted content)
         /    \
        v      v
   [APPROVED] <---> [FLAGGED]
        |             |
        v             v
       [REMOVED] (Terminal for automated feeds; RESTORE is staff-only & audited)
```
- **Visibility Matrix**:
  * `APPROVED`: Visible to all active enrolled students and staff.
  * `PENDING`: Visible strictly to the author and mentors/staff.
  * `FLAGGED`: Hidden from general student feed; visible to author with warning banner and to mentors for disposition.
  * `REMOVED`: Completely inaccessible via student APIs; retained strictly for tenant audit trails. Terminal for normal workflow; RESTORE by authorized staff is the sole exception and is strictly audit-logged.
- **Replies Count Invariant (M5 Strategy)**:
  * `replies_count` is updated atomically using database-level `UPDATE ... SET replies_count = replies_count +/- 1` or Django `F('replies_count') + 1` within `transaction.atomic()`, exclusively when a comment transitions to or from `APPROVED`.
- **Endorsement Rules**:
  * Only verified mentors can endorse (`is_mentor_endorsed=True`).
  * If a comment is marked `REMOVED`, `is_mentor_endorsed` is immediately stripped.

---

## 5. Indexing & Query Optimization
- `DiscussionThread`:
  * Composite index on `(tenant_id, cohort_id, moderation_status, created_at)`
  * Composite index on `(tenant_id, lesson_id, moderation_status, created_at)`
- `DiscussionComment`:
  * Composite index on `(tenant_id, thread_id, moderation_status, created_at)`
  * Composite index on `(tenant_id, parent_id, created_at)`
- `ModerationAction`:
  * Composite index on `(tenant_id, created_at)`

---

## 6. Comprehensive Negative Isolation & Fail-Closed Test Matrix (N1-N20)
- `N1`: Cross-tenant thread access fails closed (404 / RLS isolation).
- `N2`: Cross-tenant comment insertion fails closed with FK violation.
- `N3`: Comment parent belonging to another thread or another tenant fails closed via `FOREIGN KEY (tenant_id, parent_id, thread_id)`.
- `N4`: Thread with both `cohort_id` AND `lesson_id` set is rejected by DB XOR CHECK.
- `N5`: Thread with neither `cohort_id` NOR `lesson_id` set is rejected by DB XOR CHECK.
- `N6`: Non-mentor endorsement attempt fails with 403 Forbidden.
- `N7`: Attempt to modify or delete immutable `ModerationAction` fails via `REVOKE UPDATE, DELETE`.
- `N8`: Student without active enrollment cannot query or post in cohort discussions.
- `N9`: Deletion of member (`user_id`) with existing posts is protected by `ON DELETE RESTRICT`.
- `N10`: Reply to closed thread (`is_closed=True`) is rejected with 400 Bad Request.
- `N11`: Content exceeding length limits (200 title / 10,000 content / 5,000 comment) rejected by DB CHECK.
- `N12`: PII or unescaped HTML injection is sanitized and escaped.
- `N13`: Transition `REMOVED -> APPROVED` without staff action is rejected.
- `N14`: Student with suspended enrollment immediately loses thread creation permissions.
- `N15`: Session without `app.current_tenant` fails closed (0 rows / INSERT rejected).
- `N16`: `app.current_tenant = ''` returns 0 rows (strict `NULLIF` behavior).
- `N17`: Non-UUID GUC value (`not-a-uuid`) raises fatal DB ERROR (fail-closed).
- `N18`: GUC configuration attempt outside valid `transaction.atomic()` context (spoofing attempt) is rejected.
- `N19`: Raw SQL insertion with invalid moderation status (e.g. `moderation_status='BOGUS'`) rejected by DB CHECK.
- `N20`: Cohort deletion cascades discussion hierarchy, verifies replies count, and respects `ModerationAction` `RESTRICT` integrity.

---

## 7. Frontend & Accessibility Requirements
- BiDi Isolation: Thread titles, user handles, and code snippets within `<bdi dir="ltr">`.
- WCAG 2.2 AA: Pinned/Endorsed badges have high-contrast icon + text token.
- Keyboard navigation through conversation list and reply forms.
- Maximum nesting depth of 2 levels for discussion UI clarity and ergonomics.
