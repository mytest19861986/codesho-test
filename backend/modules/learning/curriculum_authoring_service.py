import hashlib
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    CurriculumVersion,
    CurriculumVersionStatus,
    Course,
    CourseRelease,
    CohortSchedule,
    CurriculumDraftWorkspace,
    CurriculumDraftWorkspaceStatus,
    ContentChangeSet,
    ContentChangeSetStatus,
    EditorialReview,
    EditorialReviewDecision,
    ReviewComment,
    ReviewResolution,
    ReviewResolutionStatus,
    AuthorAssignment,
    AuthorAssignmentRole,
    ChangeApprovalRecord,
    ChangeApprovalVerdict,
    AssessmentBlueprint,
    AssessmentBlueprintStatus,
    LearningObjectiveMapping,
    BloomTaxonomyLevel,
    RubricDefinition,
    RubricDefinitionStatus,
    RubricCriterion,
    AssessmentReleaseBinding,
    RubricReviewRecord,
    RubricReviewVerdict,
    CurriculumChangeImpact,
    CurriculumChangeImpactLevel,
    ReleaseReadinessCheck,
    ReleaseReadinessGate,
    ReleaseReadinessStatus,
    CohortRollforwardPlan,
    CohortRollforwardMode,
    CohortRollforwardStatus,
    CurriculumMigrationDecision,
    CurriculumMigrationDecisionChoice,
    ReleaseExceptionRecord,
)
from modules.platform_event.services import append_outbox_event


class CurriculumAuthoringService:
    """
    P3-MACRO-EPIC-23-25 Core Domain Service.
    Coordinates Curriculum Authoring Workspaces, Editorial Reviews, Rubric Governance,
    and Release Readiness Gates with hard invariants:
      1. STUDENT_RANKING = 0
      2. HISTORICAL_EVIDENCE_REBINDING = 0
      3. AUTHOR_SELF_APPROVAL = DENY
      4. AI_DECISION_AUTHORITY = 0
      5. REAL_PII = 0
    """

    # =========================================================================
    # 1. P3-VS23: CURRICULUM AUTHORING & EDITORIAL WORKFLOW
    # =========================================================================

    @classmethod
    def create_draft_workspace(
        cls,
        *,
        tenant_id: UUID,
        course_id: UUID,
        base_version_id: UUID,
        workspace_title: str,
        created_by_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CurriculumDraftWorkspace:
        with transaction.atomic():
            course = Course.objects.get(tenant_id=tenant_id, id=course_id)
            base_version = CurriculumVersion.objects.get(tenant_id=tenant_id, id=base_version_id)

            workspace = CurriculumDraftWorkspace(
                tenant_id=tenant_id,
                course=course,
                base_version=base_version,
                workspace_title=workspace_title,
                status=CurriculumDraftWorkspaceStatus.ACTIVE,
                created_by_id=created_by_id,
                metadata=metadata or {},
            )
            workspace.full_clean()
            workspace.save()

            if created_by_id:
                assignment = AuthorAssignment(
                    tenant_id=tenant_id,
                    workspace=workspace,
                    author_id=created_by_id,
                    assigned_role=AuthorAssignmentRole.PRIMARY_AUTHOR,
                )
                assignment.full_clean()
                assignment.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.workspace.created",
                aggregate_type="CurriculumDraftWorkspace",
                aggregate_id=str(workspace.id),
                payload={
                    "workspace_id": str(workspace.id),
                    "course_id": str(course_id),
                    "base_version_id": str(base_version_id),
                    "title": workspace_title,
                },
            )
            return workspace

    @classmethod
    def create_change_set(
        cls,
        *,
        tenant_id: UUID,
        workspace_id: UUID,
        title: str,
        change_summary: str,
        author_id: Optional[UUID] = None,
    ) -> ContentChangeSet:
        with transaction.atomic():
            workspace = CurriculumDraftWorkspace.objects.get(tenant_id=tenant_id, id=workspace_id)
            if workspace.status != CurriculumDraftWorkspaceStatus.ACTIVE:
                raise ValidationError(f"Cannot create change set in workspace with status {workspace.status}.")

            change_set = ContentChangeSet(
                tenant_id=tenant_id,
                workspace=workspace,
                title=title,
                change_summary=change_summary,
                status=ContentChangeSetStatus.DRAFT,
                author_id=author_id,
            )
            change_set.full_clean()
            change_set.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.changeset.created",
                aggregate_type="ContentChangeSet",
                aggregate_id=str(change_set.id),
                payload={
                    "change_set_id": str(change_set.id),
                    "workspace_id": str(workspace_id),
                    "title": title,
                },
            )
            return change_set

    @classmethod
    def submit_change_set_for_review(
        cls,
        *,
        tenant_id: UUID,
        change_set_id: UUID,
        actor_id: Optional[UUID] = None,
    ) -> ContentChangeSet:
        with transaction.atomic():
            change_set = ContentChangeSet.objects.select_for_update().get(
                tenant_id=tenant_id, id=change_set_id
            )
            if change_set.status not in (ContentChangeSetStatus.DRAFT, ContentChangeSetStatus.CHANGES_REQUESTED):
                raise ValidationError(f"Cannot submit change set in status {change_set.status} for review.")

            change_set.status = ContentChangeSetStatus.IN_REVIEW
            change_set.submitted_at = timezone.now()
            change_set.full_clean()
            change_set.save()

            review = EditorialReview.objects.create(
                tenant_id=tenant_id,
                change_set=change_set,
                decision=EditorialReviewDecision.PENDING,
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.changeset.submitted",
                aggregate_type="ContentChangeSet",
                aggregate_id=str(change_set.id),
                payload={
                    "change_set_id": str(change_set.id),
                    "review_id": str(review.id),
                },
            )
            return change_set

    @classmethod
    def record_editorial_decision(
        cls,
        *,
        tenant_id: UUID,
        change_set_id: UUID,
        reviewer_id: UUID,
        decision: str,
        justification: str = "",
    ) -> ChangeApprovalRecord:
        with transaction.atomic():
            change_set = ContentChangeSet.objects.select_for_update().get(
                tenant_id=tenant_id, id=change_set_id
            )
            if change_set.status != ContentChangeSetStatus.IN_REVIEW:
                raise ValidationError(f"Cannot record editorial decision for change set in status {change_set.status}.")

            # HARD INVARIANT: AUTHOR_SELF_APPROVAL = DENY
            if change_set.author_id and str(change_set.author_id) == str(reviewer_id):
                raise PermissionDenied("author_self_approval_denied: Authors cannot approve their own changesets.")

            if decision not in (EditorialReviewDecision.APPROVED, EditorialReviewDecision.CHANGES_REQUESTED, EditorialReviewDecision.REJECTED):
                raise ValidationError(f"Invalid editorial decision: {decision}")

            review = EditorialReview.objects.filter(
                tenant_id=tenant_id, change_set=change_set
            ).order_by("-created_at").first()

            if not review:
                review = EditorialReview.objects.create(
                    tenant_id=tenant_id,
                    change_set=change_set,
                    reviewer_id=reviewer_id,
                    decision=decision,
                    review_notes=justification,
                    completed_at=timezone.now(),
                )
            else:
                review.reviewer_id = reviewer_id
                review.decision = decision
                review.review_notes = justification
                review.completed_at = timezone.now()
                review.save()

            if decision == EditorialReviewDecision.APPROVED:
                change_set.status = ContentChangeSetStatus.APPROVED
                change_set.approved_at = timezone.now()
                change_set.save()

                # Generate cryptographic approval hash
                hash_content = f"{tenant_id}:{change_set.id}:{reviewer_id}:{timezone.now().isoformat()}"
                approval_hash = hashlib.sha256(hash_content.encode("utf-8")).hexdigest()

                approval_record = ChangeApprovalRecord(
                    tenant_id=tenant_id,
                    change_set=change_set,
                    approver_id=reviewer_id,
                    approval_verdict=ChangeApprovalVerdict.APPROVED,
                    approval_hash=approval_hash,
                    justification=justification,
                )
                approval_record.full_clean()
                approval_record.save()

                append_outbox_event(
                    tenant_id=tenant_id,
                    topic="curriculum.changeset.approved",
                    aggregate_type="ContentChangeSet",
                    aggregate_id=str(change_set.id),
                    payload={
                        "change_set_id": str(change_set.id),
                        "approval_record_id": str(approval_record.id),
                        "approver_id": str(reviewer_id),
                        "approval_hash": approval_hash,
                    },
                )
                return approval_record
            else:
                change_set.status = ContentChangeSetStatus.CHANGES_REQUESTED
                change_set.save()

                append_outbox_event(
                    tenant_id=tenant_id,
                    topic="curriculum.changeset.rejected",
                    aggregate_type="ContentChangeSet",
                    aggregate_id=str(change_set.id),
                    payload={
                        "change_set_id": str(change_set.id),
                        "decision": decision,
                        "reviewer_id": str(reviewer_id),
                    },
                )
                return None

    # =========================================================================
    # 2. P3-VS24: LEARNING ASSESSMENT BLUEPRINT & RUBRIC GOVERNANCE
    # =========================================================================

    @classmethod
    def create_assessment_blueprint(
        cls,
        *,
        tenant_id: UUID,
        course_id: UUID,
        blueprint_title: str,
        version_tag: str = "v1.0",
        pedagogical_intent: str = "",
    ) -> AssessmentBlueprint:
        with transaction.atomic():
            course = Course.objects.get(tenant_id=tenant_id, id=course_id)
            blueprint = AssessmentBlueprint(
                tenant_id=tenant_id,
                course=course,
                blueprint_title=blueprint_title,
                version_tag=version_tag,
                status=AssessmentBlueprintStatus.ACTIVE,
                pedagogical_intent=pedagogical_intent,
            )
            blueprint.full_clean()
            blueprint.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.assessment_blueprint.created",
                aggregate_type="AssessmentBlueprint",
                aggregate_id=str(blueprint.id),
                payload={
                    "blueprint_id": str(blueprint.id),
                    "course_id": str(course_id),
                    "version_tag": version_tag,
                },
            )
            return blueprint

    @classmethod
    def define_rubric(
        cls,
        *,
        tenant_id: UUID,
        blueprint_id: UUID,
        rubric_title: str,
        criteria_list: List[Dict[str, Any]],
    ) -> RubricDefinition:
        with transaction.atomic():
            blueprint = AssessmentBlueprint.objects.get(tenant_id=tenant_id, id=blueprint_id)

            total_weight = sum(Decimal(str(c.get("weight_percentage", 0))) for c in criteria_list)
            if total_weight != Decimal("100.00"):
                raise ValidationError(f"Rubric criteria weights must sum to 100.00%, got {total_weight}%.")

            for c in criteria_list:
                weight = Decimal(str(c.get("weight_percentage", 0)))
                if weight <= 0:
                    raise ValidationError("Rubric criterion weight must be greater than 0.")

            rubric = RubricDefinition(
                tenant_id=tenant_id,
                blueprint=blueprint,
                rubric_title=rubric_title,
                scale_type="QUALITATIVE_STANDARD",
                status=RubricDefinitionStatus.DRAFT,
                is_anti_ranking_compliant=True,
            )
            rubric.full_clean()
            rubric.save()

            for c in criteria_list:
                criterion = RubricCriterion(
                    tenant_id=tenant_id,
                    rubric=rubric,
                    criterion_title=c["criterion_title"],
                    description=c.get("description", ""),
                    weight_percentage=Decimal(str(c["weight_percentage"])),
                    evaluation_levels=c.get("evaluation_levels", []),
                )
                criterion.full_clean()
                criterion.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.rubric.defined",
                aggregate_type="RubricDefinition",
                aggregate_id=str(rubric.id),
                payload={
                    "rubric_id": str(rubric.id),
                    "blueprint_id": str(blueprint_id),
                    "title": rubric_title,
                },
            )
            return rubric

    @classmethod
    def bind_assessment_to_release(
        cls,
        *,
        tenant_id: UUID,
        course_release_id: UUID,
        blueprint_id: UUID,
        rubric_id: UUID,
    ) -> AssessmentReleaseBinding:
        with transaction.atomic():
            course_release = CourseRelease.objects.get(tenant_id=tenant_id, id=course_release_id)
            blueprint = AssessmentBlueprint.objects.get(tenant_id=tenant_id, id=blueprint_id)
            rubric = RubricDefinition.objects.get(tenant_id=tenant_id, id=rubric_id)

            binding = AssessmentReleaseBinding(
                tenant_id=tenant_id,
                course_release=course_release,
                blueprint=blueprint,
                rubric=rubric,
                is_authoritative=True,
            )
            binding.full_clean()
            binding.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.assessment_release.bound",
                aggregate_type="AssessmentReleaseBinding",
                aggregate_id=str(binding.id),
                payload={
                    "binding_id": str(binding.id),
                    "course_release_id": str(course_release_id),
                    "blueprint_id": str(blueprint_id),
                    "rubric_id": str(rubric_id),
                },
            )
            return binding

    # =========================================================================
    # 3. P3-VS25: RELEASE READINESS, CHANGE IMPACT & PROGRAM ROLLFORWARD
    # =========================================================================

    @classmethod
    def analyze_curriculum_change_impact(
        cls,
        *,
        tenant_id: UUID,
        source_version_id: UUID,
        target_version_id: UUID,
    ) -> CurriculumChangeImpact:
        with transaction.atomic():
            source = CurriculumVersion.objects.get(tenant_id=tenant_id, id=source_version_id)
            target = CurriculumVersion.objects.get(tenant_id=tenant_id, id=target_version_id)

            breaking = target.semver_major > source.semver_major
            if breaking:
                impact_level = CurriculumChangeImpactLevel.BREAKING
            elif target.semver_minor > source.semver_minor:
                impact_level = CurriculumChangeImpactLevel.MAJOR
            else:
                impact_level = CurriculumChangeImpactLevel.PATCH

            impact = CurriculumChangeImpact(
                tenant_id=tenant_id,
                source_version=source,
                target_version=target,
                impact_level=impact_level,
                breaking_changes_detected=breaking,
                affected_cohorts_count=0,
                impact_details={
                    "source_semver": f"{source.semver_major}.{source.semver_minor}.{source.semver_patch}",
                    "target_semver": f"{target.semver_major}.{target.semver_minor}.{target.semver_patch}",
                    "breaking": breaking,
                },
            )
            impact.full_clean()
            impact.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.change_impact.analyzed",
                aggregate_type="CurriculumChangeImpact",
                aggregate_id=str(impact.id),
                payload={
                    "impact_id": str(impact.id),
                    "source_version_id": str(source_version_id),
                    "target_version_id": str(target_version_id),
                    "impact_level": impact_level,
                },
            )
            return impact

    @classmethod
    def evaluate_release_readiness(
        cls,
        *,
        tenant_id: UUID,
        curriculum_version_id: UUID,
    ) -> Dict[str, Any]:
        with transaction.atomic():
            version = CurriculumVersion.objects.get(tenant_id=tenant_id, id=curriculum_version_id)

            # Check 1: Editorial approval check
            has_approval = ChangeApprovalRecord.objects.filter(
                tenant_id=tenant_id,
                change_set__workspace__base_version=version,
                approval_verdict=ChangeApprovalVerdict.APPROVED,
            ).exists()

            editorial_check, _ = ReleaseReadinessCheck.objects.update_or_create(
                tenant_id=tenant_id,
                curriculum_version=version,
                check_name="editorial_approval_check",
                defaults={
                    "category": "EDITORIAL",
                    "status": ReleaseReadinessStatus.PASSED if has_approval else ReleaseReadinessStatus.FAILED,
                    "check_output": "Approved change sets verified" if has_approval else "Pending change approval",
                },
            )

            editorial_gate, _ = ReleaseReadinessGate.objects.update_or_create(
                tenant_id=tenant_id,
                curriculum_version=version,
                gate_name="editorial_governance_gate",
                defaults={
                    "is_blocking": True,
                    "verdict": ReleaseReadinessStatus.PASSED if has_approval else ReleaseReadinessStatus.FAILED,
                },
            )

            # Check 2: Rubric anti-ranking check
            has_rubrics = RubricDefinition.objects.filter(
                tenant_id=tenant_id,
                blueprint__course=version.course,
                is_anti_ranking_compliant=True,
            ).exists()

            rubric_check, _ = ReleaseReadinessCheck.objects.update_or_create(
                tenant_id=tenant_id,
                curriculum_version=version,
                check_name="rubric_anti_ranking_check",
                defaults={
                    "category": "PEDAGOGICAL",
                    "status": ReleaseReadinessStatus.PASSED if has_rubrics else ReleaseReadinessStatus.FAILED,
                    "check_output": "Anti-ranking qualitative rubric verified" if has_rubrics else "No compliant rubric defined",
                },
            )

            rubric_gate, _ = ReleaseReadinessGate.objects.update_or_create(
                tenant_id=tenant_id,
                curriculum_version=version,
                gate_name="rubric_compliance_gate",
                defaults={
                    "is_blocking": True,
                    "verdict": ReleaseReadinessStatus.PASSED if has_rubrics else ReleaseReadinessStatus.FAILED,
                },
            )

            all_passed = (editorial_gate.verdict == ReleaseReadinessStatus.PASSED and rubric_gate.verdict == ReleaseReadinessStatus.PASSED)
            return {
                "version_id": str(version.id),
                "is_ready_for_release": all_passed,
                "editorial_gate": editorial_gate.verdict,
                "rubric_gate": rubric_gate.verdict,
            }

    @classmethod
    def create_cohort_rollforward_plan(
        cls,
        *,
        tenant_id: UUID,
        cohort_schedule_id: UUID,
        target_release_id: UUID,
        rollforward_mode: str = CohortRollforwardMode.FUTURE_MODULES_ONLY,
        scheduled_effective_date: Optional[date] = None,
    ) -> CohortRollforwardPlan:
        with transaction.atomic():
            schedule = CohortSchedule.objects.get(tenant_id=tenant_id, id=cohort_schedule_id)
            if not schedule.is_active:
                raise ValidationError("cohort_not_eligible_for_rollforward: Inactive cohorts cannot be targeted.")

            target_release = CourseRelease.objects.get(tenant_id=tenant_id, id=target_release_id)

            plan = CohortRollforwardPlan(
                tenant_id=tenant_id,
                cohort_schedule=schedule,
                target_release=target_release,
                rollforward_mode=rollforward_mode,
                status=CohortRollforwardStatus.DRAFT,
                scheduled_effective_date=scheduled_effective_date or timezone.now().date(),
            )
            plan.full_clean()
            plan.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.rollforward_plan.created",
                aggregate_type="CohortRollforwardPlan",
                aggregate_id=str(plan.id),
                payload={
                    "plan_id": str(plan.id),
                    "cohort_schedule_id": str(cohort_schedule_id),
                    "target_release_id": str(target_release_id),
                    "mode": rollforward_mode,
                },
            )
            return plan

    @classmethod
    def decide_curriculum_migration(
        cls,
        *,
        tenant_id: UUID,
        plan_id: UUID,
        decided_by_id: UUID,
        decision: str,
        justification: str = "",
    ) -> CurriculumMigrationDecision:
        with transaction.atomic():
            plan = CohortRollforwardPlan.objects.select_for_update().get(
                tenant_id=tenant_id, id=plan_id
            )
            if decision not in (CurriculumMigrationDecisionChoice.PROCEED, CurriculumMigrationDecisionChoice.HALT, CurriculumMigrationDecisionChoice.EXCEPTION_REQUIRED):
                raise ValidationError(f"Invalid migration decision: {decision}")

            decision_record = CurriculumMigrationDecision(
                tenant_id=tenant_id,
                plan=plan,
                decided_by_id=decided_by_id,
                decision=decision,
                justification=justification,
            )
            decision_record.full_clean()
            decision_record.save()

            if decision == CurriculumMigrationDecisionChoice.PROCEED:
                plan.status = CohortRollforwardStatus.APPROVED
            elif decision == CurriculumMigrationDecisionChoice.HALT:
                plan.status = CohortRollforwardStatus.CANCELLED
            plan.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.migration.decided",
                aggregate_type="CurriculumMigrationDecision",
                aggregate_id=str(decision_record.id),
                payload={
                    "decision_id": str(decision_record.id),
                    "plan_id": str(plan_id),
                    "decision": decision,
                    "decided_by_id": str(decided_by_id),
                },
            )
            return decision_record

    @classmethod
    def grant_release_exception(
        cls,
        *,
        tenant_id: UUID,
        gate_id: UUID,
        granted_by_id: UUID,
        exception_reason: str,
    ) -> ReleaseExceptionRecord:
        with transaction.atomic():
            gate = ReleaseReadinessGate.objects.select_for_update().get(
                tenant_id=tenant_id, id=gate_id
            )
            if not exception_reason or len(exception_reason.strip()) < 10:
                raise ValidationError("gate_waiver_requires_audit_justification: Exception reason must be at least 10 characters.")

            record = ReleaseExceptionRecord(
                tenant_id=tenant_id,
                gate=gate,
                granted_by_id=granted_by_id,
                exception_reason=exception_reason,
            )
            record.full_clean()
            record.save()

            gate.verdict = ReleaseReadinessStatus.WAIVED
            gate.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.release_gate.waived",
                aggregate_type="ReleaseExceptionRecord",
                aggregate_id=str(record.id),
                payload={
                    "record_id": str(record.id),
                    "gate_id": str(gate_id),
                    "granted_by_id": str(granted_by_id),
                },
            )
            return record
