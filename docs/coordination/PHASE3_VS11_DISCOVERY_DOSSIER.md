# Phase 3 Vertical Slice 11 Discovery Dossier (P3-VS11)

## 1. Executive Summary
- **Slice ID**: `P3-VS11`
- **Task ID**: `P3-VS11-LEARNING-PERSONALIZATION-AND-ADAPTIVE-PROGRESSION-ENGINE`
- **Scope Title (Farsi)**: موتور شخصی‌سازی یادگیری، تحلیل مسیر رشد دانش‌آموز و سیستم پیشنهاد مسیر آموزشی تطبیقی
- **Authority**: `COMMANDER_P3_VS11_DISCOVERY_DIRECTIVE`
- **Discovery Status**: `TRIPLE_FLEET_CONSENSUS_ACHIEVED` (Unanimous `PASS` from Gemini, GLM, and Qwen).
- **Runtime Lock Status**: `AWAITING_COMMANDER_RUNTIME_UNLOCK` (Strictly Zero Runtime Code Modifications until Commander Unlock).
- **Core Architecture Document**: [docs/architecture/PHASE3_VS11_BOUNDARY_PLAN.md](file:///G:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/PHASE3_VS11_BOUNDARY_PLAN.md) (Version 1.2).
- **Write Manifest**: [docs/coordination/PHASE3_VS11_WRITE_MANIFEST.md](file:///G:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/coordination/PHASE3_VS11_WRITE_MANIFEST.md) (`ZERO_WILDCARDS: YES`).

---

## 2. Triple Fleet Scope Review Consensus Matrix

| Reviewer | Specialized Domain Role | Formal Review Verdict | Consensus Status | Raw Review Transcript Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | UI/UX, Educational Psychology & Accessibility (WCAG 2.2 AA) | `GEMINI_SCOPE: PASS` | **APPROVED** | `scratch/gemini_vs11_response.txt` (10,635 chars) |
| **GLM (Z.ai)** | Principal Database & Security Architect | `GLM_SCOPE: PASS` | **APPROVED** | `scratch/glm_vs11_full_extracted.txt` (103,304 chars) |
| **Qwen** | Principal Domain Architect & Distributed Systems Specialist | `QWEN_SCOPE: PASS` | **APPROVED** | `scratch/qwen_vs11_official_pass.txt` (223,627 chars) |

---

## 3. Architecture Pillars & Invariants Formally Accepted

### 3.1 Directed Acyclic Graph (DAG) Invariant (B1 Enforced)
- Database trigger `trg_skill_dag_guard` using PostgreSQL Recursive CTE and transactional advisory lock (`pg_advisory_xact_lock(hashtextextended(NEW.tenant_id::text, 42))`) strictly prevents cyclic dependencies and concurrent phantom-cycle race conditions.
- Strict rejection of self-dependencies (`source_skill_id <> target_skill_id`).

### 3.2 Zero Bare UUIDs & Complete Composite Foreign Keys (B2 Enforced)
- All inter-table relations enforce database-level Composite Foreign Keys `(tenant_id, target_id)`.
- `target_lesson_id` on `LearningRecommendation` references `(tenant_id, id)` of `learning_lesson` on delete cascade.

### 3.3 Strict Single-Target Exclusive Selection (B3 Enforced)
- `CHECK (num_nonnulls(target_course_id, target_lesson_id, target_skill_id) = 1)`.

### 3.4 Explainability First (M3 Enforced)
- Every recommendation must carry structured pedagogical evidence: `CHECK (evidence_context <> '{}'::jsonb)` and `length(recommendation_reason) >= 10`.

### 3.5 Idempotent Event Processing (Qwen Invariant 1 Enforced)
- Dedicated `ProcessedLearningEvent` model with `UNIQUE (tenant_id, event_id, event_type)` ensures learning events are processed strictly once, preventing runaway increments on `practice_count`.

### 3.6 Monotonic Mastery Progression (Qwen Invariant 4 Enforced)
- Deterministic formulas for mastery level transitions (`BEGINNER -> DEVELOPING -> PROFICIENT -> MASTERED`).
- Established mastery levels are monotonic and cannot be regressed by late-arriving low assessment scores.

### 3.7 Immutable Transition Audit Logging (Qwen Invariant 3 Enforced)
- `RecommendationTransitionLog` with `REVOKE UPDATE, DELETE FROM app_role` maintains a complete, non-repudiation audit trail of all recommendation life-cycle transitions.

### 3.8 Active Target Lifecycle & Inactive Policy (Qwen Invariant 5 Enforced)
- Recommendations and dependencies are forbidden from targeting inactive artifacts (`is_active=False`).
- Deactivation of a target automatically transitions active recommendations to `SUPERSEDED`.

### 3.9 Adolescent Educational Psychology & Accessibility (Gemini Invariants)
- "Guide, Don't Judge": Zero demotivating labels ("نقاط ضعف" replaced with "مهارت‌های در حال شکوفایی").
- Mandatory `<bdi dir="ltr">` isolation for slugs and code tokens in RTL layouts.
- Full WCAG 2.2 AA compliance: contrast ratio $> 4.5:1$, touch targets $\ge 44\text{px}$, non-color dependency for mastery badges.

---

## 4. Comprehensive Fail-Closed Test Matrix (N1-N33)
The slice requires full automated implementation of the 33 negative isolation tests detailed in §5 of [PHASE3_VS11_BOUNDARY_PLAN.md](file:///G:/project/codesho/codesho/worktrees/phase1-engineering-readiness/docs/architecture/PHASE3_VS11_BOUNDARY_PLAN.md).

---

## 5. Submission to Commander
The technical fleet has achieved 100% unanimous consensus. We hereby request Commander review and formal issuance of:
`COMMANDER_P3_VS11_RUNTIME_UNLOCK: GRANTED`
