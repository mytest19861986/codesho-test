import uuid
from rest_framework import serializers

from modules.learning.models import (
    StaffAccessAssignment,
    DelegatedAdminScope,
    PrivilegedPermissionGrant,
    AccessReviewCampaign,
    AccessReviewDecision,
    PrivilegedActionAudit,
    DataRetentionPolicy,
    RetentionPolicyVersion,
    LegalHold,
    LegalHoldScope,
    RetentionEvaluation,
    DataDispositionRecord,
    DispositionAuditLog,
    ReadinessControl,
    ReadinessEvidence,
    ReadinessAssessmentRun,
    ReadinessFinding,
    ReadinessException,
    PilotReadinessGate,
    ControlAttestationAudit,
)


class StaffAccessAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAccessAssignment
        fields = [
            "id",
            "tenant",
            "user_id",
            "role_name",
            "scope_type",
            "assigned_by_id",
            "is_active",
            "valid_from",
            "valid_until",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class DelegatedAdminScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DelegatedAdminScope
        fields = [
            "id",
            "tenant",
            "assignment",
            "scope_resource_type",
            "scope_resource_id",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class PrivilegedPermissionGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivilegedPermissionGrant
        fields = [
            "id",
            "tenant",
            "user_id",
            "permission_code",
            "justification",
            "granted_by_id",
            "second_approver_id",
            "status",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class AccessReviewCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessReviewCampaign
        fields = [
            "id",
            "tenant",
            "title",
            "campaign_period",
            "status",
            "deadline",
            "created_by_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class AccessReviewDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessReviewDecision
        fields = [
            "id",
            "tenant",
            "campaign",
            "assignment",
            "reviewer_id",
            "decision",
            "notes",
            "decided_at",
        ]
        read_only_fields = ["id", "tenant", "decided_at"]


class PrivilegedActionAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivilegedActionAudit
        fields = [
            "id",
            "tenant",
            "actor_id",
            "action_type",
            "target_resource",
            "ip_address",
            "details",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataRetentionPolicy
        fields = [
            "id",
            "tenant",
            "data_category",
            "retention_period_days",
            "disposition_action",
            "is_active",
            "created_by_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class RetentionPolicyVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetentionPolicyVersion
        fields = [
            "id",
            "tenant",
            "policy",
            "version_number",
            "retention_period_days",
            "disposition_action",
            "reason_for_change",
            "changed_by_id",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class LegalHoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalHold
        fields = [
            "id",
            "tenant",
            "title",
            "legal_case_reference",
            "reason",
            "status",
            "placed_by_id",
            "released_by_id",
            "placed_at",
            "released_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "placed_at", "created_at", "updated_at"]


class LegalHoldScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalHoldScope
        fields = [
            "id",
            "tenant",
            "legal_hold",
            "target_data_category",
            "target_entity_id",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class RetentionEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetentionEvaluation
        fields = [
            "id",
            "tenant",
            "policy",
            "target_entity_type",
            "target_entity_id",
            "is_eligible_for_disposition",
            "blocked_by_legal_hold",
            "evaluation_reason",
            "evaluated_at",
        ]
        read_only_fields = ["id", "tenant", "evaluated_at"]


class DataDispositionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDispositionRecord
        fields = [
            "id",
            "tenant",
            "target_entity_type",
            "target_entity_id",
            "action_applied",
            "records_affected_count",
            "executed_by_id",
            "disposition_hash",
            "executed_at",
        ]
        read_only_fields = ["id", "tenant", "executed_at"]


class DispositionAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispositionAuditLog
        fields = [
            "id",
            "tenant",
            "disposition_record",
            "action_type",
            "verification_status",
            "logged_at",
        ]
        read_only_fields = ["id", "tenant", "logged_at"]


class ReadinessControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadinessControl
        fields = [
            "id",
            "tenant",
            "control_code",
            "category",
            "description",
            "is_blocking_for_pilot",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class ReadinessEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadinessEvidence
        fields = [
            "id",
            "tenant",
            "control",
            "evidence_name",
            "evidence_type",
            "sha256_digest",
            "artifact_uri",
            "status",
            "submitted_by_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class ReadinessAssessmentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadinessAssessmentRun
        fields = [
            "id",
            "tenant",
            "run_code",
            "evaluation_scope",
            "overall_status",
            "executed_by_id",
            "summary",
            "started_at",
            "completed_at",
        ]
        read_only_fields = ["id", "tenant", "started_at"]


class ReadinessFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadinessFinding
        fields = [
            "id",
            "tenant",
            "assessment_run",
            "control",
            "severity",
            "finding_summary",
            "remediation_plan",
            "is_resolved",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class ReadinessExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadinessException
        fields = [
            "id",
            "tenant",
            "finding",
            "justification",
            "approved_by_id",
            "valid_until",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class PilotReadinessGateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilotReadinessGate
        fields = [
            "id",
            "tenant",
            "assessment_run",
            "gate_verdict",
            "advisory_notes",
            "blocking_findings_count",
            "has_automated_deploy_authority",
            "evaluated_at",
        ]
        read_only_fields = ["id", "tenant", "has_automated_deploy_authority", "evaluated_at"]


class ControlAttestationAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlAttestationAudit
        fields = [
            "id",
            "tenant",
            "gate",
            "attested_by_id",
            "attestation_role",
            "signature_digest",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "signature_digest", "created_at"]
