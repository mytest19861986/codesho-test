from decimal import Decimal
from rest_framework import serializers

from modules.learning.models import (
    CurriculumDraftWorkspace,
    ContentChangeSet,
    EditorialReview,
    ReviewComment,
    ReviewResolution,
    AuthorAssignment,
    ChangeApprovalRecord,
    AssessmentBlueprint,
    LearningObjectiveMapping,
    RubricDefinition,
    RubricCriterion,
    AssessmentReleaseBinding,
    RubricReviewRecord,
    CurriculumChangeImpact,
    ReleaseReadinessCheck,
    ReleaseReadinessGate,
    CohortRollforwardPlan,
    CurriculumMigrationDecision,
    ReleaseExceptionRecord,
    PROHIBITED_PII_KEYS_20_22,
    PII_REGEX_20_22,
)


def _check_pii_string(val: str, field_name: str) -> None:
    if val and PII_REGEX_20_22.search(val):
        raise serializers.ValidationError({field_name: f"PII detected in {field_name}."})


def _check_pii_dict(val: dict, field_name: str) -> None:
    if isinstance(val, dict):
        bad_keys = set(val.keys()) & PROHIBITED_PII_KEYS_20_22
        if bad_keys:
            raise serializers.ValidationError({field_name: f"Prohibited PII keys: {bad_keys}"})


class CurriculumDraftWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumDraftWorkspace
        fields = [
            "id", "tenant", "course", "base_version", "workspace_title",
            "status", "created_by_id", "metadata", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_workspace_title(self, value):
        _check_pii_string(value, "workspace_title")
        return value

    def validate_metadata(self, value):
        _check_pii_dict(value, "metadata")
        return value


class ContentChangeSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentChangeSet
        fields = [
            "id", "tenant", "workspace", "title", "change_summary",
            "status", "author_id", "submitted_at", "approved_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "submitted_at", "approved_at", "created_at", "updated_at"]

    def validate_title(self, value):
        _check_pii_string(value, "title")
        return value

    def validate_change_summary(self, value):
        _check_pii_string(value, "change_summary")
        return value


class EditorialReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorialReview
        fields = [
            "id", "tenant", "change_set", "reviewer_id", "decision",
            "review_notes", "completed_at", "created_at"
        ]
        read_only_fields = ["id", "completed_at", "created_at"]

    def validate_review_notes(self, value):
        _check_pii_string(value, "review_notes")
        return value


class ReviewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = [
            "id", "tenant", "review", "author_id", "comment_text",
            "target_entity", "target_entity_id", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def validate_comment_text(self, value):
        _check_pii_string(value, "comment_text")
        return value


class AssessmentBlueprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentBlueprint
        fields = [
            "id", "tenant", "course", "blueprint_title", "version_tag",
            "status", "pedagogical_intent", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_blueprint_title(self, value):
        _check_pii_string(value, "blueprint_title")
        return value


class RubricCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricCriterion
        fields = [
            "id", "tenant", "rubric", "criterion_title", "description",
            "weight_percentage", "evaluation_levels", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class RubricDefinitionSerializer(serializers.ModelSerializer):
    criteria = RubricCriterionSerializer(many=True, read_only=True)

    class Meta:
        model = RubricDefinition
        fields = [
            "id", "tenant", "blueprint", "rubric_title", "scale_type",
            "status", "is_anti_ranking_compliant", "criteria", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "is_anti_ranking_compliant", "created_at", "updated_at"]

    def validate(self, attrs):
        # Strict anti-ranking enforcement
        if not attrs.get("is_anti_ranking_compliant", True):
            raise serializers.ValidationError({"is_anti_ranking_compliant": "Anti-ranking policy violation."})
        return attrs


class AssessmentReleaseBindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentReleaseBinding
        fields = [
            "id", "tenant", "course_release", "blueprint", "rubric",
            "is_authoritative", "bound_at"
        ]
        read_only_fields = ["id", "bound_at"]


class ReleaseReadinessGateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseReadinessGate
        fields = [
            "id", "tenant", "curriculum_version", "gate_name",
            "is_blocking", "verdict", "evaluated_at"
        ]
        read_only_fields = ["id", "evaluated_at"]


class CohortRollforwardPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CohortRollforwardPlan
        fields = [
            "id", "tenant", "cohort_schedule", "target_release",
            "rollforward_mode", "status", "scheduled_effective_date",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReleaseExceptionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseExceptionRecord
        fields = [
            "id", "tenant", "gate", "granted_by_id", "exception_reason", "granted_at"
        ]
        read_only_fields = ["id", "granted_at"]

    def validate_exception_reason(self, value):
        _check_pii_string(value, "exception_reason")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Exception reason must be at least 10 characters.")
        return value
