# Phase 3 Vertical Slice 13: Boundary & Architecture Plan (v1.1)

## Task ID: P3-VS13-STUDENT-GROWTH-INSIGHTS-AND-LONGITUDINAL-LEARNING-INTELLIGENCE

---

### 1. Executive Summary & Problem Space
The Codesho platform requires an intelligent, longitudinal learning analytics and growth insight engine that tracks student development across competencies, milestones, and learning trajectories without introducing toxic comparative ranking or public leaderboards.
In accordance with Commander Directive `COMMANDER_P3_VS13_DISCOVERY_START`, this engine operates strictly on pure event-driven projections derived from source-of-truth events (submissions, assessments, completions, milestones).
This document establishes the certifiable architectural contract (v1.1) incorporating full PostgreSQL 17 DDL, strict composite foreign keys, fail-closed `FORCE ROW LEVEL SECURITY`, comprehensive CHECK constraints, JSONB PII protections, finite state machines, and intra-tenant role-based authorization.

---

### 2. Strict Invariants & Non-Negotiables

1. **GUC Session Protocol Inside Atomic Transactions**:
   - Every tenant interaction MUST establish the session variable `SET LOCAL app.current_tenant = '<tenant_id>'` inside `transaction.atomic()` prior to any tenant table queries.
   - If the variable is missing or empty, database queries return 0 rows and mutations fail closed.

2. **Projection Only from Source of Truth (Pure Projections)**:
   - Insights, metric snapshots, and trends are derived idempotently from historical immutable learning events.
   - Zero duplicated or competing mutable state. All recalculations are deterministic.

3. **Zero Bare UUIDs & Multi-Tenant Composite Foreign Keys**:
   - Every entity enforces `FORCE ROW LEVEL SECURITY`.
   - Primary and composite foreign keys strictly follow `(tenant_id, id)` and `(tenant_id, student_id)`.
   - Cross-tenant references are physically impossible at the database constraint level.

4. **Zero Student Ranking / Growth Over Comparison (Child Protection Guarantee)**:
   - Absolutely no competitive leaderboards, peer ranking, percentiles, or comparative shaming mechanisms.
   - Analytics focus exclusively on intra-individual progress (student growth against their own baseline and learning milestones).
   - Schema design strictly excludes peer identifiers or comparative aggregation columns.

5. **Tamper-Proof Milestone Evidence & Digest Integrity**:
   - Milestone achievements capture immutable digital digests (`evidence_digest`) linking to source events (submissions, certificates).

6. **JSONB PII Scrubbing**:
   - All JSONB payloads (`metadata`, `competency_vectors`, `evidence_payload`) strictly forbid PII attributes (`name`, `phone`, `email`, `national_id`, `location`, `avatar_url`) enforced by database CHECK constraints.

7. **Append-Only Immutability for Audit/Event Tables**:
   - `learning_insightgenerationevent` is strictly Append-Only. `app_role` has `REVOKE UPDATE, DELETE` applied.

---

### 2.1 Inter-Slice Prerequisites & Upstream Schema Assurances
This slice builds directly upon canonical schema entities from previous slices:
- `platform_tenant_tenant(id)`
- `platform_tenant_tenantmembership(tenant_id, user_id)` via unique composite constraint `membership_tenant_user_uniq`
- `learning_submission(tenant_id, id)` (VS1)
- `learning_coursecertificate(tenant_id, id)` (VS6)
- `platform_tenant_guardianaccessgrant(tenant_id, student_id, guardian_user_id)` (VS12)

---

### 3. Complete Data Schema & PostgreSQL 17 DDL Specifications

```sql
-- =============================================================================
-- ENTITY 1: GrowthMetricSnapshot
-- Purpose: Point-in-time snapshot of student growth across defined competencies
-- Immutability: Append-Only projection per snapshot date
-- =============================================================================

CREATE TABLE learning_growthmetricsnapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    metric_key VARCHAR(64) NOT NULL,
    metric_value NUMERIC(8, 2) NOT NULL,
    baseline_value NUMERIC(8, 2) NULL,
    growth_delta NUMERIC(8, 2) GENERATED ALWAYS AS (
        COALESCE(metric_value - baseline_value, 0.00)
    ) STORED,
    calculation_run_id UUID NOT NULL,
    snapshot_date DATE NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT growth_metric_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT growth_metric_student_membership_fk FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT growth_metric_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT growth_metric_daily_student_uniq UNIQUE (tenant_id, student_id, metric_key, snapshot_date),

    CONSTRAINT growth_metric_key_check CHECK (
        metric_key IN ('CODING_VELOCITY', 'CONCEPT_MASTERY', 'PROBLEM_SOLVING', 'PERSISTENCE', 'CODE_QUALITY')
    ),
    CONSTRAINT growth_metric_value_range CHECK (metric_value >= 0.00 AND metric_value <= 1000.00),
    CONSTRAINT growth_metric_baseline_range CHECK (baseline_value IS NULL OR (baseline_value >= 0.00 AND baseline_value <= 1000.00)),
    CONSTRAINT growth_metric_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object' AND
        NOT (metadata ?| ARRAY['name', 'phone', 'email', 'national_id', 'location', 'avatar_url'])
    )
);

ALTER TABLE learning_growthmetricsnapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_growthmetricsnapshot FORCE ROW LEVEL SECURITY;

CREATE POLICY growth_metric_tenant_isolation ON learning_growthmetricsnapshot
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);


-- =============================================================================
-- ENTITY 2: StudentGrowthTrend
-- Purpose: Current consolidated competency vectors and longitudinal trajectory
-- Immutability: Mutable-Latest projection updated during recalculation runs
-- =============================================================================

CREATE TABLE learning_studentgrowthtrend (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    competency_domain VARCHAR(64) NOT NULL,
    trend_direction VARCHAR(32) NOT NULL DEFAULT 'DEVELOPING',
    current_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    velocity_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    total_milestones_achieved INTEGER NOT NULL DEFAULT 0,
    competency_vectors JSONB NOT NULL DEFAULT '{"mastery": 0, "consistency": 0, "resilience": 0}'::jsonb,
    calculation_run_id UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT growth_trend_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT growth_trend_student_membership_fk FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT growth_trend_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT growth_trend_domain_uniq UNIQUE (tenant_id, student_id, competency_domain),

    CONSTRAINT growth_trend_direction_check CHECK (
        trend_direction IN ('ACCELERATING', 'STEADY', 'DEVELOPING', 'NEEDS_SUPPORT')
    ),
    CONSTRAINT growth_trend_score_range CHECK (current_score >= 0.00 AND current_score <= 100.00),
    CONSTRAINT growth_trend_milestones_non_negative CHECK (total_milestones_achieved >= 0),
    CONSTRAINT growth_trend_vectors_no_pii CHECK (
        jsonb_typeof(competency_vectors) = 'object' AND
        NOT (competency_vectors ?| ARRAY['name', 'phone', 'email', 'national_id', 'location', 'avatar_url'])
    )
);

ALTER TABLE learning_studentgrowthtrend ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentgrowthtrend FORCE ROW LEVEL SECURITY;

CREATE POLICY growth_trend_tenant_isolation ON learning_studentgrowthtrend
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);


-- =============================================================================
-- ENTITY 3: LearningMilestone
-- Purpose: Formative milestones reached by student with cryptographic evidence digest
-- Immutability: Formative record; revocable only via formal RETRACTED status
-- =============================================================================

CREATE TABLE learning_learningmilestone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    milestone_code VARCHAR(64) NOT NULL,
    title VARCHAR(160) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status VARCHAR(20) NOT NULL DEFAULT 'ACHIEVED',
    achieved_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    retracted_at TIMESTAMPTZ NULL,
    retraction_reason TEXT NULL,
    source_submission_id UUID NULL,
    source_certificate_id UUID NULL,
    evidence_digest VARCHAR(64) NOT NULL,
    evidence_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT milestone_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT milestone_student_membership_fk FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT milestone_submission_fk FOREIGN KEY (tenant_id, source_submission_id)
        REFERENCES learning_submission(tenant_id, id) ON DELETE NO ACTION,
    CONSTRAINT milestone_certificate_fk FOREIGN KEY (tenant_id, source_certificate_id)
        REFERENCES learning_coursecertificate(tenant_id, id) ON DELETE NO ACTION,
    CONSTRAINT milestone_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT milestone_student_code_uniq UNIQUE (tenant_id, student_id, milestone_code),

    CONSTRAINT milestone_status_check CHECK (status IN ('ACHIEVED', 'RETRACTED')),
    CONSTRAINT milestone_retraction_check CHECK (
        (status = 'RETRACTED' AND retracted_at IS NOT NULL AND retraction_reason IS NOT NULL) OR
        (status = 'ACHIEVED' AND retracted_at IS NULL AND retraction_reason IS NULL)
    ),
    CONSTRAINT milestone_title_len_check CHECK (length(title) >= 3),
    CONSTRAINT milestone_digest_len_check CHECK (length(evidence_digest) = 64),
    CONSTRAINT milestone_evidence_no_pii CHECK (
        jsonb_typeof(evidence_payload) = 'object' AND
        NOT (evidence_payload ?| ARRAY['name', 'phone', 'email', 'national_id', 'location', 'avatar_url'])
    )
);

ALTER TABLE learning_learningmilestone ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningmilestone FORCE ROW LEVEL SECURITY;

CREATE POLICY milestone_tenant_isolation ON learning_learningmilestone
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);


-- =============================================================================
-- ENTITY 4: LearningInsight
-- Purpose: Qualitative personalized formative insight generated for student
-- Lifecycle: ACTIVE -> SUPERSEDED (on re-derivation) or RETRACTED
-- =============================================================================

CREATE TABLE learning_learninginsight (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    insight_type VARCHAR(40) NOT NULL,
    title VARCHAR(180) NOT NULL,
    description TEXT NOT NULL,
    confidence_level VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
    lifecycle_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    calculation_run_id UUID NOT NULL,
    valid_until TIMESTAMPTZ NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT insight_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT insight_student_membership_fk FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT insight_tenant_id_uniq UNIQUE (tenant_id, id),

    CONSTRAINT insight_type_check CHECK (
        insight_type IN ('COMPETENCY_GROWTH', 'STRENGTH_AREA', 'MOMENTUM_STREAK', 'FOCUS_RECOMMENDATION', 'MASTERY_MILESTONE')
    ),
    CONSTRAINT insight_confidence_check CHECK (confidence_level IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT insight_lifecycle_check CHECK (lifecycle_status IN ('ACTIVE', 'SUPERSEDED', 'RETRACTED')),
    CONSTRAINT insight_title_len_check CHECK (length(title) >= 5),
    CONSTRAINT insight_desc_len_check CHECK (length(description) >= 15),
    CONSTRAINT insight_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object' AND
        NOT (metadata ?| ARRAY['name', 'phone', 'email', 'national_id', 'location', 'avatar_url'])
    )
);

ALTER TABLE learning_learninginsight ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learninginsight FORCE ROW LEVEL SECURITY;

CREATE POLICY insight_tenant_isolation ON learning_learninginsight
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);


-- =============================================================================
-- ENTITY 5: InsightGenerationEvent (Append-Only Audit & Idempotency Log)
-- Purpose: Ensures strict idempotency and auditability of recalculation runs
-- Immutability: STRICT APPEND-ONLY. UPDATE and DELETE revoked from app_role.
-- =============================================================================

CREATE TABLE learning_insightgenerationevent (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    event_key VARCHAR(128) NOT NULL,
    calculation_run_id UUID NOT NULL,
    sequence_id BIGINT NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'PROCESSED',
    failure_reason TEXT NULL,
    retry_count SMALLINT NOT NULL DEFAULT 0,
    triggered_by UUID NOT NULL,
    payload_digest VARCHAR(64) NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT generation_event_tenant_fk FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT generation_event_student_membership_fk FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT generation_event_triggered_by_fk FOREIGN KEY (tenant_id, triggered_by)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE NO ACTION,
    CONSTRAINT generation_event_tenant_id_uniq UNIQUE (tenant_id, id),
    CONSTRAINT generation_event_idempotency_uniq UNIQUE (tenant_id, student_id, event_type, event_key),

    CONSTRAINT generation_event_status_check CHECK (status IN ('PROCESSED', 'REJECTED', 'FAILED')),
    CONSTRAINT generation_event_retry_count_check CHECK (retry_count >= 0 AND retry_count <= 10),
    CONSTRAINT generation_event_failure_check CHECK (
        (status IN ('REJECTED', 'FAILED') AND failure_reason IS NOT NULL) OR
        (status = 'PROCESSED' AND failure_reason IS NULL)
    ),
    CONSTRAINT generation_event_digest_len_check CHECK (length(payload_digest) = 64)
);

ALTER TABLE learning_insightgenerationevent ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_insightgenerationevent FORCE ROW LEVEL SECURITY;

CREATE POLICY generation_event_tenant_isolation ON learning_insightgenerationevent
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Strictly enforce Append-Only security for the application runtime role
REVOKE UPDATE, DELETE ON learning_insightgenerationevent FROM app_role;
```

---

### 4. Indexing Strategy & Performance Justification

```sql
-- Point-in-time metric retrieval and date-range filtering
CREATE INDEX idx_growth_metric_student_timeline 
    ON learning_growthmetricsnapshot (tenant_id, student_id, metric_key, snapshot_date DESC);

-- Fast lookup of active trends by student and domain
CREATE INDEX idx_growth_trend_student_domain 
    ON learning_studentgrowthtrend (tenant_id, student_id, competency_domain);

-- Chronological timeline of achieved milestones
CREATE INDEX idx_learning_milestone_chronological 
    ON learning_learningmilestone (tenant_id, student_id, achieved_at DESC)
    WHERE status = 'ACHIEVED';

-- Active insights retrieval for student dashboard
CREATE INDEX idx_learning_insight_active_feed 
    ON learning_learninginsight (tenant_id, student_id, lifecycle_status, created_at DESC)
    WHERE lifecycle_status = 'ACTIVE';

-- Idempotency and audit lookups
CREATE INDEX idx_insight_event_audit 
    ON learning_insightgenerationevent (tenant_id, student_id, calculation_run_id);
```

---

### 5. Finite State Machines (FSM) & Recalculation Protocols

#### 5.1 `LearningInsight` Lifecycle FSM
```
[ACTIVE] --------(New Recalculation Run / Superseded)--------> [SUPERSEDED]
   |
   +------------(Source Assessment Retracted)----------------> [RETRACTED]
```

- When a new calculation run completes successfully, existing `ACTIVE` insights of the same category are atomically transitioned to `SUPERSEDED` with `valid_until = clock_timestamp()`.
- If an underlying milestone or submission is formally retracted, impacted insights transition to `RETRACTED`.

#### 5.2 `LearningMilestone` Achievement FSM
```
[ACHIEVED] --------(Evidence Invalidation / Mentor Review)--------> [RETRACTED]
```

- Milestones are immutable historical achievements. If evidence is invalidated, the record is marked `RETRACTED` with an auditable `retraction_reason` and `retracted_at` timestamp.

#### 5.3 Deterministic Recalculation & Rebuild Protocol (Rebuild Mechanics)
When source data changes or a recalculation is triggered:
1. An idempotent `InsightGenerationEvent` is registered within `transaction.atomic()`.
2. A new unique `calculation_run_id` (UUID) is generated for the session.
3. Projections are re-derived:
   - `GrowthMetricSnapshot`: Re-calculated and upserted based on `(tenant_id, student_id, metric_key, snapshot_date)`.
   - `StudentGrowthTrend`: Updated in-place with latest vectors and `calculation_run_id`.
   - `LearningInsight`: Previous `ACTIVE` insights are marked `SUPERSEDED`, and new insights tagged with `calculation_run_id` are inserted.

---

### 6. Intra-Tenant Authorization Actor Matrix (Child Protection & Scoped AuthZ)

| Action / Endpoint | Student | Guardian (Active Grant) | Assigned Mentor | Unassigned Mentor | Tenant Staff / Admin |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET /insights/` (Own/Ward Feed) | Allowed (Self) | Allowed (Ward only) | Allowed (Assigned student) | Forbidden (403) | Allowed |
| `GET /insights/trends/` (Longitudinal) | Allowed (Self) | Allowed (Ward only) | Allowed (Assigned student) | Forbidden (403) | Allowed |
| `GET /insights/milestones/` (Timeline) | Allowed (Self) | Allowed (Ward only) | Allowed (Assigned student) | Forbidden (403) | Allowed |
| `POST /insights/derive/` (Recalculate) | Forbidden (403) | Forbidden (403) | Allowed (Assigned student only, Rate-Limited) | Forbidden (403) | Allowed |
| `PATCH /milestones/retract/` | Forbidden (403) | Forbidden (403) | Allowed (With auditable reason) | Forbidden (403) | Allowed |

- **Zero Peer Visibility**: A student or guardian CANNOT view another student's insights under any circumstance.
- **Intra-Tenant Scoping**: Mentor access is strictly restricted to students actively enrolled in cohorts assigned to that mentor.

---

### 7. Comprehensive Negative & Compliance Test Matrix (N1 - N45)

#### 7.1 PostgreSQL 17 Multi-Tenant & RLS Isolation Core
- **N1**: Cross-tenant query on `learning_growthmetricsnapshot` returns 0 rows (Fail-closed).
- **N2**: Cross-tenant query on `learning_studentgrowthtrend` returns 0 rows.
- **N3**: Cross-tenant query on `learning_learningmilestone` returns 0 rows.
- **N4**: Cross-tenant query on `learning_learninginsight` returns 0 rows.
- **N5**: Cross-tenant query on `learning_insightgenerationevent` returns 0 rows.
- **N6**: Missing GUC `app.current_tenant` returns 0 rows and rejects INSERT on all 5 entities.
- **N7**: Empty string `app.current_tenant` returns 0 rows via `NULLIF(..., '')::uuid`.
- **N8**: Malformed/Non-UUID `app.current_tenant` raises database syntax error (Fail-closed).
- **N9**: Cross-tenant spoofing attempt on `tenant_id` raises foreign key or policy error.
- **N10**: Tenant deletion cascades all 5 growth entities cleanly.

#### 7.2 Composite Foreign Keys & Database Constraints
- **N11**: Direct INSERT with mismatched `(tenant_id, student_id)` rejected by membership composite FK.
- **N12**: Deletion of student membership cascades metric snapshots, trends, milestones, and insights.
- **N13**: Milestone referencing cross-tenant submission rejected by `milestone_submission_fk`.
- **N14**: Milestone referencing cross-tenant certificate rejected by `milestone_certificate_fk`.
- **N15**: Deletion of referenced submission/certificate blocked (`ON DELETE NO ACTION`) to preserve audit trail.

#### 7.3 Uniqueness, Idempotency & Rebuild Mechanics
- **N16**: Duplicate metric snapshot on same date rejected by `growth_metric_daily_student_uniq`.
- **N17**: Duplicate trend for same competency domain rejected by `growth_trend_domain_uniq`.
- **N18**: Duplicate milestone for same student and code rejected by `milestone_student_code_uniq`.
- **N19**: Duplicate generation event with identical `(tenant_id, student_id, event_type, event_key)` rejected by `generation_event_idempotency_uniq`.
- **N20**: Re-running derivation with new `calculation_run_id` supersedes previous active insights without orphan records.

#### 7.4 Child Protection, Growth-Over-Comparison & Anti-Ranking
- **N21**: Any endpoint request attempting to pass peer comparison parameters returns 400 Bad Request.
- **N22**: Verification that responses contain zero peer percentiles, class rankings, or comparative labels.
- **N23**: Verification that student cannot query another student's metrics (403 Forbidden).
- **N24**: Verification that guardian without `ACTIVE` grant (e.g. `PENDING` or `REVOKED`) is denied access (403 Forbidden).
- **N25**: Verification that unassigned mentor cannot trigger `/derive/` or view student metrics (403 Forbidden).

#### 7.5 JSONB PII Protection & Data Sanitization
- **N26**: Attempt to store `name` inside `growthmetricsnapshot.metadata` rejected by `growth_metric_metadata_no_pii`.
- **N27**: Attempt to store `phone` inside `studentgrowthtrend.competency_vectors` rejected by `growth_trend_vectors_no_pii`.
- **N28**: Attempt to store `national_id` inside `learningmilestone.evidence_payload` rejected by `milestone_evidence_no_pii`.
- **N29**: Attempt to store `email` inside `learninginsight.metadata` rejected by `insight_metadata_no_pii`.
- **N30**: HTML/XSS injection inside milestone title or description is sanitized by service layer.

#### 7.6 State Machines & Immutability Rules
- **N31**: Direct `UPDATE` or `DELETE` on `learning_insightgenerationevent` by `app_role` raises Permission Denied.
- **N32**: Transitioning milestone to `RETRACTED` without `retraction_reason` rejected by DB CHECK.
- **N33**: Transitioning milestone to `ACHIEVED` with non-null `retracted_at` rejected by DB CHECK.
- **N34**: Milestone with invalid `evidence_digest` length (!= 64) rejected by DB CHECK.
- **N35**: Metric snapshot with negative `metric_value` rejected by DB CHECK.
- **N36**: Student growth trend with invalid `trend_direction` rejected by DB CHECK.
- **N37**: Generation event with `retry_count > 10` rejected by DB CHECK.
- **N38**: Generation event with `status = 'FAILED'` without `failure_reason` rejected by DB CHECK.

#### 7.7 UI/UX, BiDi & Accessibility Invariants
- **N39**: Persian RTL layout isolation: Numbers, dates, and metrics wrapped in `<bdi dir="ltr">`.
- **N40**: WCAG 2.2 AA touch targets on timeline action buttons (>= 44px x 44px).
- **N41**: Color contrast on growth milestone cards meets or exceeds 4.5:1 ratio.
- **N42**: Rate-limiting on `POST /derive/` prevents denial-of-service against calculation worker.
- **N43**: Rebuilding trend from empty baseline gracefully defaults `growth_delta` to 0.00 without division-by-zero.
- **N44**: Guardian access strictly scoped to granted ward; cross-ward enumeration returns 404/403.
- **N45**: Audit log preservation: `InsightGenerationEvent` accurately records `triggered_by` actor membership.

---

### 8. Frontend Architecture & Design System Integration

1. **`GrowthJourneyDashboard.tsx`**:
   - Primary personal dashboard emphasizing individual progress, milestones achieved, and focus areas.
   - Strictly devoid of peer comparisons, rank tags, or leaderboard widgets.
2. **`ProgressStoryCard.tsx`**:
   - Formative celebratory cards displaying skill development trajectories and narrative growth feedback.
3. **`LearningInsightTimeline.tsx`**:
   - Accessible vertical timeline illustrating milestone achievements, evidence digests, and teacher endorsements.
   - Built with full Persian RTL orientation, BiDi numerical wrappers, and WCAG 2.2 AA touch target compliance.
