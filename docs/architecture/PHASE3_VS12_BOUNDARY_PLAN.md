# P3-VS12 Boundary Plan: Student Learning Portfolio & Journey Narrative
**Version**: 1.5.1  
**Date**: 2026-09-09  
**Status**: APPROVED_ARCHITECTURAL_BLUEPRINT  
**Review Scope**: Triple Fleet Consensus Standard (Gemini + GLM + Qwen)  
**Task ID**: `P3-VS12-STUDENT-LEARNING-PORTFOLIO-AND-JOURNEY-NARRATIVE`  

---

## 1. System Invariants & Non-Negotiable Tenets
1. **Tenant Session Isolation Protocol**: All transactions enforce `SET LOCAL app.current_tenant = %s` inside `transaction.atomic()` prior to any tenant query.
2. **Row-Level Security (RLS)**: Enforced via `ALTER TABLE ... FORCE ROW LEVEL SECURITY` with `NOBYPASSRLS` standard across all tables.
3. **Zero Bare UUIDs**: All relational columns enforce composite foreign keys `(tenant_id, target_id)` matching source uniqueness constraints.
4. **Child Privacy & Fail-Closed Visibility**: Default portfolio visibility is strictly `'PRIVATE'`. Default moderation status is strictly `'PENDING'`. Guardian access requires verified `'ACTIVE'` status with timestamp.
5. **Showcase Moderation & Consent Invariant**: A portfolio can ONLY transition to `'TENANT_PUBLIC'` if `moderation_status = 'APPROVED'` AND `public_consent_active = TRUE`. Enforced by database CHECK constraint `portfolio_public_guard`.
6. **Append-Only Moderation & Consent Audit**: All moderation and consent events are recorded in `learning_portfoliomoderationaction` with `REVOKE UPDATE, DELETE FROM app_role`, `ON DELETE CASCADE` on tenant (allowing clean tenant offboarding), and `ON DELETE NO ACTION` on target entities (preserving minor evidence integrity while eliminating multi-path cascade order deadlock).
7. **Zero PII Exposure**: Narrative timelines and artifacts strictly forbid PII keys in JSONB storage via database CHECK constraints and service validation.

---

## 2. Architecture & Data Flow

```
+-----------------------------------------------------------------------------------+
|                                 TENANT CONTEXT                                    |
|                                                                                   |
|  +---------------------------+             +----------------------------------+   |
|  |   GuardianAccessGrant     |             |         LearningPortfolio        |   |
|  | - status: PENDING/ACTIVE  |             | - visibility: PRIVATE (default)  |   |
|  | - Composite FK to Member  |             | - moderation: PENDING (default)  |   |
|  +-------------+-------------+             | - public_consent_active: FALSE   |   |
|                |                           +-----------------+----------------+   |
|                v (Grants View)                               | (Owns)             |
|  +---------------------------+                               v                    |
|  |   Student Profile View    |<====================+--------------------------+   |
|  +---------------------------+                     |   AchievementArtifact    |   |
|                                                    | - reflection_notes       |   |
|                                                    | - mentor_endorsement     |   |
|                                                    | - source Composite FKs   |   |
|                                                    +--------------------------+   |
|                                                              | (Chronological)    |
|                                                              v                    |
|                                                    +--------------------------+   |
|                                                    |  StudentJourneyTimeline  |   |
|                                                    | - milestone narrative    |   |
|                                                    +--------------------------+   |
|                                                                                   |
|                                                    +--------------------------+   |
|                                                    | PortfolioModerationAction|   |
|                                                    | - APPEND-ONLY AUDIT      |   |
|                                                    | - Composite FKs to Target|   |
|                                                    +--------------------------+   |
+-----------------------------------------------------------------------------------+
```

### 2.1 Verification of External Source Prerequisites
The following external tables from prior slices provide prerequisite composite uniqueness constraints:
- `learning_submission(tenant_id, id)` via `learning_submission_tenant_id_uniq` (VS1)
- `learning_coursecertificate(tenant_id, id)` via `learning_coursecert_tenant_id_uniq` (VS6)
- `platform_tenant_tenantmembership(tenant_id, user_id)` via `membership_tenant_user_uniq` (Platform Foundation)
- Requirement: PostgreSQL >= 15 for column-list `ON DELETE SET NULL (column_name)`.

---

## 3. Data Schema & DDL Specifications

### 3.1 `GuardianAccessGrant` (Tenant Membership Composite Verification)
```sql
CREATE TABLE platform_tenant_guardianaccessgrant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    guardian_user_id UUID NOT NULL,
    student_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    decided_at TIMESTAMPTZ NULL,
    revoked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT guardian_grant_tenant_fk FOREIGN KEY (tenant_id) REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT guardian_grant_guardian_membership_fk FOREIGN KEY (tenant_id, guardian_user_id) 
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT guardian_grant_student_membership_fk FOREIGN KEY (tenant_id, student_id) 
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT guardian_grant_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT guardian_grant_status_check CHECK (status IN ('PENDING', 'ACTIVE', 'REVOKED')),
    CONSTRAINT guardian_grant_revoked_check CHECK ((status = 'REVOKED') = (revoked_at IS NOT NULL)),
    CONSTRAINT guardian_grant_active_check CHECK (status <> 'ACTIVE' OR decided_at IS NOT NULL)
);
ALTER TABLE platform_tenant_guardianaccessgrant ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_tenant_guardianaccessgrant FORCE ROW LEVEL SECURITY;
CREATE POLICY guardian_grant_tenant_isolation ON platform_tenant_guardianaccessgrant
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Conditional uniqueness: Only one active or pending grant allowed at a time between guardian and student
CREATE UNIQUE INDEX guardian_grant_active_pending_uniq 
    ON platform_tenant_guardianaccessgrant (tenant_id, guardian_user_id, student_id)
    WHERE status IN ('PENDING', 'ACTIVE');
```

### 3.2 `LearningPortfolio`
```sql
CREATE TABLE learning_learningportfolio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    headline VARCHAR(200) NOT NULL,
    summary_narrative TEXT NOT NULL DEFAULT '',
    featured_artifact_count SMALLINT NOT NULL DEFAULT 0,
    visibility VARCHAR(20) NOT NULL DEFAULT 'PRIVATE',
    moderation_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    public_consent_active BOOLEAN NOT NULL DEFAULT FALSE,
    public_consent_by UUID NULL,
    public_consent_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT portfolio_tenant_fk FOREIGN KEY (tenant_id) REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT portfolio_student_membership_fk FOREIGN KEY (tenant_id, student_id) 
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT portfolio_public_consent_fk FOREIGN KEY (tenant_id, public_consent_by)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE SET NULL (public_consent_by),
    CONSTRAINT portfolio_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT portfolio_tenant_student_uniq UNIQUE (tenant_id, student_id),
    CONSTRAINT portfolio_visibility_check CHECK (visibility IN ('PRIVATE', 'GUARDIAN_SHARED', 'TENANT_PUBLIC')),
    CONSTRAINT portfolio_moderation_check CHECK (moderation_status IN ('PENDING', 'APPROVED', 'FLAGGED', 'REMOVED')),
    CONSTRAINT portfolio_headline_len_check CHECK (length(headline) >= 5),
    CONSTRAINT portfolio_featured_count_check CHECK (featured_artifact_count >= 0),
    CONSTRAINT portfolio_public_guard CHECK (
        visibility <> 'TENANT_PUBLIC' OR (
            moderation_status = 'APPROVED' AND public_consent_active = TRUE
        )
    )
);
ALTER TABLE learning_learningportfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningportfolio FORCE ROW LEVEL SECURITY;
CREATE POLICY portfolio_tenant_isolation ON learning_learningportfolio
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
```

### 3.3 `AchievementArtifact`
```sql
CREATE TABLE learning_achievementartifact (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    portfolio_id UUID NOT NULL,
    artifact_type VARCHAR(32) NOT NULL,
    title VARCHAR(160) NOT NULL,
    reflection_notes TEXT NOT NULL DEFAULT '',
    mentor_endorsement TEXT NOT NULL DEFAULT '',
    mentor_user_id UUID NULL,
    source_submission_id UUID NULL,
    source_certificate_id UUID NULL,
    moderation_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT artifact_tenant_fk FOREIGN KEY (tenant_id) REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT artifact_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT artifact_composite_portfolio_fk FOREIGN KEY (tenant_id, portfolio_id) 
        REFERENCES learning_learningportfolio(tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT artifact_mentor_membership_fk FOREIGN KEY (tenant_id, mentor_user_id) 
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE SET NULL (mentor_user_id),
    CONSTRAINT artifact_source_submission_fk FOREIGN KEY (tenant_id, source_submission_id)
        REFERENCES learning_submission(tenant_id, id) ON DELETE NO ACTION,
    CONSTRAINT artifact_source_certificate_fk FOREIGN KEY (tenant_id, source_certificate_id)
        REFERENCES learning_coursecertificate(tenant_id, id) ON DELETE NO ACTION,
    CONSTRAINT artifact_type_check CHECK (artifact_type IN ('PROJECT_CODE', 'CAPSTONE_SUBMISSION', 'CERTIFICATE', 'BADGE_HIGHLIGHT')),
    CONSTRAINT artifact_moderation_check CHECK (moderation_status IN ('PENDING', 'APPROVED', 'FLAGGED', 'REMOVED')),
    CONSTRAINT artifact_title_len_check CHECK (length(title) >= 3),
    CONSTRAINT artifact_source_mutual_exclusivity CHECK (num_nonnulls(source_submission_id, source_certificate_id) <= 1),
    CONSTRAINT artifact_type_source_mapping_check CHECK (
        (artifact_type = 'CAPSTONE_SUBMISSION' AND source_submission_id IS NOT NULL) OR
        (artifact_type = 'CERTIFICATE' AND source_certificate_id IS NOT NULL) OR
        (artifact_type IN ('PROJECT_CODE', 'BADGE_HIGHLIGHT'))
    )
);
ALTER TABLE learning_achievementartifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_achievementartifact FORCE ROW LEVEL SECURITY;
CREATE POLICY artifact_tenant_isolation ON learning_achievementartifact
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
```

### 3.4 `StudentJourneyTimeline`
```sql
CREATE TABLE learning_studentjourneytimeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    event_key VARCHAR(64) NOT NULL,
    event_title VARCHAR(160) NOT NULL,
    narrative_description TEXT NOT NULL,
    milestone_date DATE NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT timeline_tenant_fk FOREIGN KEY (tenant_id) REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT timeline_student_membership_fk FOREIGN KEY (tenant_id, student_id) 
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT timeline_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT timeline_tenant_event_uniq UNIQUE (tenant_id, student_id, event_key),
    CONSTRAINT timeline_title_len_check CHECK (length(event_title) >= 3),
    CONSTRAINT timeline_desc_len_check CHECK (length(narrative_description) >= 10),
    CONSTRAINT timeline_metadata_no_pii_check CHECK (
        jsonb_typeof(metadata) = 'object' AND
        NOT (metadata ?| ARRAY['name', 'phone', 'email', 'avatar_url', 'national_id', 'location'])
    )
);
ALTER TABLE learning_studentjourneytimeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentjourneytimeline FORCE ROW LEVEL SECURITY;
CREATE POLICY timeline_tenant_isolation ON learning_studentjourneytimeline
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
```

### 3.5 `PortfolioModerationAction` (Append-Only Audit Trail)
```sql
CREATE TABLE learning_portfoliomoderationaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    target_portfolio_id UUID NULL,
    target_artifact_id UUID NULL,
    actor_id UUID NOT NULL,
    action_type VARCHAR(32) NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT modaction_tenant_fk FOREIGN KEY (tenant_id) REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT modaction_portfolio_fk FOREIGN KEY (tenant_id, target_portfolio_id)
        REFERENCES learning_learningportfolio(tenant_id, id) ON DELETE NO ACTION,
    CONSTRAINT modaction_artifact_fk FOREIGN KEY (tenant_id, target_artifact_id)
        REFERENCES learning_achievementartifact(tenant_id, id) ON DELETE NO ACTION,
    CONSTRAINT modaction_actor_membership_fk FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE NO ACTION,
    CONSTRAINT modaction_action_type_check CHECK (action_type IN ('APPROVE', 'UNFLAG', 'FLAG', 'REMOVE', 'RESTORE', 'CONSENT_GRANT', 'CONSENT_REVOKE')),
    CONSTRAINT modaction_target_check CHECK (num_nonnulls(target_portfolio_id, target_artifact_id) = 1)
);
ALTER TABLE learning_portfoliomoderationaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_portfoliomoderationaction FORCE ROW LEVEL SECURITY;
CREATE POLICY modaction_tenant_isolation ON learning_portfoliomoderationaction
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Strictly enforce Append-Only security for the application runtime role
REVOKE UPDATE, DELETE ON learning_portfoliomoderationaction FROM app_role;
```

---

## 4. Indexing Strategy
```sql
CREATE INDEX idx_portfolio_showcase ON learning_learningportfolio (tenant_id, visibility, moderation_status);
CREATE INDEX idx_artifact_portfolio ON learning_achievementartifact (tenant_id, portfolio_id, is_featured);
CREATE INDEX idx_guardian_grant_lookup ON platform_tenant_guardianaccessgrant (tenant_id, student_id, status);
CREATE INDEX idx_timeline_chronological ON learning_studentjourneytimeline (tenant_id, student_id, milestone_date DESC);
CREATE INDEX idx_modaction_target_portfolio ON learning_portfoliomoderationaction (tenant_id, target_portfolio_id);
CREATE INDEX idx_modaction_target_artifact ON learning_portfoliomoderationaction (tenant_id, target_artifact_id) WHERE target_artifact_id IS NOT NULL;
```

---

## 5. Finite State Machines (FSM)

### 5.1 Visibility Transitions
| Current State | Target State | Actor | Required Precondition | Audit Event |
| :--- | :--- | :--- | :--- | :--- |
| `PRIVATE` | `GUARDIAN_SHARED` | Student | Active guardian grant exists | N/A |
| `GUARDIAN_SHARED` | `PRIVATE` | Student | None (Fail-closed) | N/A |
| `GUARDIAN_SHARED` | `TENANT_PUBLIC` | Student | `moderation_status == 'APPROVED'` AND `public_consent_active == TRUE` | `CONSENT_GRANT` |
| `TENANT_PUBLIC` | `GUARDIAN_SHARED` | Student | None (Instant retraction: sets `public_consent_active = FALSE`) | `CONSENT_REVOKE` |
| `TENANT_PUBLIC` | `PRIVATE` | Student | None (Instant retraction: sets `public_consent_active = FALSE`) | `CONSENT_REVOKE` |

### 5.2 Content Moderation FSM & Actor Matrix
```
[PENDING] ----(Approve)----> [APPROVED] <====(Unflag)==== [FLAGGED] ----(Remove)----> [REMOVED]
    |                            |                                                       |
    +---------(Remove)-----------+                                                       |
    |                                                                                    |
    +================================(Staff Restore)=====================================+
```

| Action | Permitted Actor Roles | Prohibited Actors | Self-Action Guard |
| :--- | :--- | :--- | :--- |
| `APPROVE` | Staff, Moderator, Assigned Mentor | Student, Guardian, Unassigned Mentor | Student cannot self-approve content |
| `FLAG` | Staff, Moderator, Mentor, Guardian | Unauthenticated | N/A |
| `UNFLAG` | Staff, Moderator | Student, Author Mentor | Author cannot unflag own report |
| `REMOVE` | Staff, Moderator | Student, Guardian | N/A |
| `RESTORE` | Tenant Admin, Staff Only | Student, Mentor | N/A (Transition to `PENDING` for re-audit) |

- Transitioning to `TENANT_PUBLIC` strictly requires DB CHECK verification (`portfolio_public_guard`).

---

## 6. Complete Negative Test Matrix (N1-N42)

### 6.1 GUC & Tenant Isolation Core (Canonical Fleet Standards)
- **N1**: Cross-tenant portfolio query rejected by RLS (Fail-closed).
- **N2**: Unauthenticated request returns 401/403.
- **N3**: Unlinked parent attempting to access non-child portfolio returns 403.
- **N4**: Linked parent can access `GUARDIAN_SHARED` but forbidden from `PRIVATE`.
- **N5**: Student cannot create multiple portfolios in the same tenant (`UNIQUE (tenant, student)`).
- **N6**: Duplicate journey timeline milestone rejected (`UNIQUE (tenant, student, event_key)`).
- **N7**: Short portfolio headline (< 5 chars) rejected.
- **N8**: Short artifact title (< 3 chars) rejected.
- **N9**: Short narrative description (< 10 chars) rejected.
- **N10**: Invalid visibility state choice rejected.
- **N11**: Invalid artifact type choice rejected.
- **N12**: Direct database cross-tenant foreign key assignment blocked by Composite FK.
- **N13**: Deleting portfolio without moderation audit history cascades deletion to related artifacts.
- **N14**: Revoked parent grant fails closed immediately (verified with preserved `decided_at` timestamp).
- **N15**: Transition to `TENANT_PUBLIC` without `moderation_status == 'APPROVED'` rejected by `portfolio_public_guard`.
- **N16**: Featured artifacts counter automatically increments/decrements atomically (`F('featured_artifact_count')`).
- **N17**: Tenant public showcase strictly filtered by current tenant setting.
- **N18**: HTML injection in reflection notes sanitized.
- **N19**: RTL text direction maintained in journey narrative rendering.
- **N20**: WCAG 2.2 AA touch target compliance (>= 44px) on artifact action controls.
- **N21**: Student B forbidden from viewing Student A's `PRIVATE` portfolio within the same tenant.
- **N22**: Cross-tenant spoofing attempt on `app.current_tenant` rejected.
- **N23**: Deletion of tenant cascades `GuardianAccessGrant`.
- **N24**: Deletion of student membership without active audit log cascades portfolio; when audit log exists, service layer archives evidence prior to membership deletion.
- **N25**: Idempotent event replay with identical `event_key` leaves timeline unchanged.

### 6.2 Security & Fleet Compliance Tests
- **N26**: Database session without `app.current_tenant` established returns 0 rows and rejects INSERT.
- **N27**: Empty string `app.current_tenant` returns 0 rows via `NULLIF(..., '')::uuid`.
- **N28**: Non-UUID `app.current_tenant` raises database syntax error (Fail-closed).
- **N29**: Artifact with `moderation_status == 'PENDING'` is invisible in `TENANT_PUBLIC` showcase.
- **N30**: Guardian with `status == 'PENDING'` denied access to `GUARDIAN_SHARED` portfolio.
- **N31**: Artifact endorsement by non-mentor user returns 403 Forbidden.
- **N32**: Illegal moderation transition `REMOVED -> APPROVED` rejected.
- **N33**: Instant retraction from showcase (`TENANT_PUBLIC -> GUARDIAN_SHARED / PRIVATE`) immediately revokes public visibility.

### 6.3 Domain Invariant Guard Tests (v1.4, v1.5 & v1.5.1 Additions)
- **N34**: `app_role` attempting `UPDATE` or `DELETE` on `learning_portfoliomoderationaction` raises `Permission Denied` (Append-Only immutability).
- **N35**: Moderation action referring to non-existent portfolio or cross-tenant portfolio rejected by Composite FK.
- **N36**: Offboarding a tenant cascades cleanly without foreign key deadlocks under `NO ACTION` evaluation in statement boundary.
- **N37**: Author student attempting self-approval (`can_moderate` guard) returns 403 Forbidden.
- **N38**: Transition to `TENANT_PUBLIC` with `public_consent_active = FALSE` rejected by DB CHECK constraint.
- **N39**: Achievement artifact referring to cross-tenant submission or cross-tenant certificate rejected by Composite FK.
- **N40**: Artifact type `CAPSTONE_SUBMISSION` without `source_submission_id` or `CERTIFICATE` without `source_certificate_id` rejected by `artifact_type_source_mapping_check`.
- **N41**: Creating new guardian grant while active or pending grant exists blocked by conditional unique index; allowed after prior grant is `REVOKED`.
- **N42**: Direct deletion of a portfolio having moderation audit history is blocked by `NO ACTION` referential constraint, preserving child evidence integrity.
