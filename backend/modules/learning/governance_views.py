import uuid
from uuid import UUID
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.learning.enterprise_governance_service import EnterpriseGovernanceService
from modules.learning.models import (
    StaffAccessAssignment,
    PrivilegedPermissionGrant,
    AccessReviewCampaign,
    DataRetentionPolicy,
    LegalHold,
    ReadinessControl,
    ReadinessEvidence,
    ReadinessAssessmentRun,
    ReadinessFinding,
    PilotReadinessGate,
)
from modules.learning.governance_serializers import (
    StaffAccessAssignmentSerializer,
    PrivilegedPermissionGrantSerializer,
    AccessReviewCampaignSerializer,
    AccessReviewDecisionSerializer,
    DataRetentionPolicySerializer,
    LegalHoldSerializer,
    ReadinessControlSerializer,
    ReadinessEvidenceSerializer,
    ReadinessAssessmentRunSerializer,
    ReadinessFindingSerializer,
    ReadinessExceptionSerializer,
    PilotReadinessGateSerializer,
)


def _extract_tenant(request: Request) -> UUID:
    tenant = getattr(request, "tenant", None)
    if tenant and hasattr(tenant, "id"):
        return tenant.id
    tenant_id_header = request.headers.get("X-Tenant-Id")
    if tenant_id_header:
        return UUID(tenant_id_header)
    raise PermissionDenied("tenant_required: No tenant context provided.")


def _check_anti_ranking_query(request: Request):
    params = getattr(request, "query_params", None)
    if params is None:
        params = getattr(request, "GET", {})
    for param in params:
        if any(forbidden in param.lower() for forbidden in ["rank", "leaderboard", "percentile", "score_rank", "peer_comparison"]):
            raise ValidationError("ranking_queries_prohibited: Anti-ranking policy active. Competitive scoring queries are prohibited.")


class BaseGovernanceView(APIView):
    authentication_classes = []
    permission_classes = []


# -----------------------------------------------------------------------------
# P3-VS26: DELEGATED ADMINISTRATION & ACCESS GOVERNANCE VIEWS
# -----------------------------------------------------------------------------

class StaffAccessAssignmentView(BaseGovernanceView):
    """List or create delegated staff access assignments."""

    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        assignments = StaffAccessAssignment.objects.filter(tenant_id=tenant_id).order_by("-created_at")
        serializer = StaffAccessAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        assigned_by_id = UUID(str(data.get("assigned_by_id", uuid.uuid4())))
        user_id = UUID(str(data["user_id"]))
        role_name = data["role_name"]
        scope_type = data.get("scope_type", "TENANT_WIDE")
        valid_until = data.get("valid_until")
        scopes = data.get("scopes")

        assignment = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=tenant_id,
            user_id=user_id,
            role_name=role_name,
            assigned_by_id=assigned_by_id,
            scope_type=scope_type,
            valid_until=valid_until,
            scopes=scopes,
        )
        serializer = StaffAccessAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PrivilegedPermissionGrantView(BaseGovernanceView):
    """List or grant dual-custody privileged permissions."""

    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        grants = PrivilegedPermissionGrant.objects.filter(tenant_id=tenant_id).order_by("-created_at")
        serializer = PrivilegedPermissionGrantSerializer(grants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        user_id = UUID(str(data["user_id"]))
        permission_code = data["permission_code"]
        justification = data["justification"]
        granted_by_id = UUID(str(data["granted_by_id"]))
        expires_at = data["expires_at"]
        second_approver_id = UUID(str(data["second_approver_id"])) if data.get("second_approver_id") else None

        grant = EnterpriseGovernanceService.grant_privileged_permission(
            tenant_id=tenant_id,
            user_id=user_id,
            permission_code=permission_code,
            justification=justification,
            granted_by_id=granted_by_id,
            expires_at=expires_at,
            second_approver_id=second_approver_id,
        )
        serializer = PrivilegedPermissionGrantSerializer(grant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccessReviewCampaignView(BaseGovernanceView):
    """Launch or view access review campaigns."""

    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        campaigns = AccessReviewCampaign.objects.filter(tenant_id=tenant_id).order_by("-created_at")
        serializer = AccessReviewCampaignSerializer(campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        campaign = EnterpriseGovernanceService.launch_access_review_campaign(
            tenant_id=tenant_id,
            title=data["title"],
            campaign_period=data["campaign_period"],
            deadline=data["deadline"],
            created_by_id=UUID(str(data.get("created_by_id", uuid.uuid4()))),
        )
        serializer = AccessReviewCampaignSerializer(campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccessReviewDecisionView(BaseGovernanceView):
    """Record authoritative access review decision."""

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        decision = EnterpriseGovernanceService.record_access_review_decision(
            tenant_id=tenant_id,
            campaign_id=UUID(str(data["campaign_id"])),
            assignment_id=UUID(str(data["assignment_id"])),
            reviewer_id=UUID(str(data.get("reviewer_id", uuid.uuid4()))),
            decision=data["decision"],
            notes=data.get("notes", ""),
        )
        serializer = AccessReviewDecisionSerializer(decision)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -----------------------------------------------------------------------------
# P3-VS27: DATA LIFECYCLE & RETENTION GOVERNANCE VIEWS
# -----------------------------------------------------------------------------

class DataRetentionPolicyView(BaseGovernanceView):
    """List or configure category-specific retention policies."""

    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        policies = DataRetentionPolicy.objects.filter(tenant_id=tenant_id).order_by("-created_at")
        serializer = DataRetentionPolicySerializer(policies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        policy = EnterpriseGovernanceService.create_retention_policy(
            tenant_id=tenant_id,
            data_category=data["data_category"],
            retention_period_days=int(data["retention_period_days"]),
            disposition_action=data.get("disposition_action", "ANONYMIZE"),
            created_by_id=UUID(str(data.get("created_by_id", uuid.uuid4()))),
            reason=data.get("reason", "Policy baseline"),
        )
        serializer = DataRetentionPolicySerializer(policy)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LegalHoldView(BaseGovernanceView):
    """Place or inspect immutable legal holds."""

    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        holds = LegalHold.objects.filter(tenant_id=tenant_id).order_by("-placed_at")
        serializer = LegalHoldSerializer(holds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        hold = EnterpriseGovernanceService.place_legal_hold(
            tenant_id=tenant_id,
            title=data["title"],
            legal_case_reference=data["legal_case_reference"],
            reason=data["reason"],
            placed_by_id=UUID(str(data.get("placed_by_id", uuid.uuid4()))),
            scopes=data.get("scopes"),
        )
        serializer = LegalHoldSerializer(hold)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -----------------------------------------------------------------------------
# P3-VS28: ENTERPRISE CONTROL EVIDENCE & PILOT READINESS VIEWS
# -----------------------------------------------------------------------------

class ReadinessControlView(BaseGovernanceView):
    """List or register enterprise readiness controls."""

    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        controls = ReadinessControl.objects.filter(tenant_id=tenant_id).order_by("control_code")
        serializer = ReadinessControlSerializer(controls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        control = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=tenant_id,
            control_code=data["control_code"],
            category=data["category"],
            description=data["description"],
            is_blocking_for_pilot=data.get("is_blocking_for_pilot", True),
        )
        serializer = ReadinessControlSerializer(control)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReadinessEvidenceSubmitView(BaseGovernanceView):
    """Submit cryptographic evidence for an enterprise readiness control."""

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        evidence = EnterpriseGovernanceService.submit_readiness_evidence(
            tenant_id=tenant_id,
            control_id=UUID(str(data["control_id"])),
            evidence_name=data["evidence_name"],
            evidence_type=data["evidence_type"],
            raw_content=data["raw_content"].encode("utf-8"),
            artifact_uri=data["artifact_uri"],
            submitted_by_id=UUID(str(data.get("submitted_by_id", uuid.uuid4()))),
        )
        serializer = ReadinessEvidenceSerializer(evidence)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PilotReadinessAssessmentRunView(BaseGovernanceView):
    """Execute readiness assessment run."""

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=tenant_id,
            run_code=data["run_code"],
            evaluation_scope=data["evaluation_scope"],
            executed_by_id=UUID(str(data.get("executed_by_id", uuid.uuid4()))),
            summary=data.get("summary", "Automated readiness evaluation"),
        )
        serializer = ReadinessAssessmentRunSerializer(run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PilotReadinessGateEvaluationView(BaseGovernanceView):
    """Evaluate advisory pilot readiness gate with human attestation."""

    def post(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        data = request.data
        gate = EnterpriseGovernanceService.evaluate_pilot_readiness_gate(
            tenant_id=tenant_id,
            assessment_run_id=UUID(str(data["assessment_run_id"])),
            attested_by_id=UUID(str(data.get("attested_by_id", uuid.uuid4()))),
            attestation_role=data.get("attestation_role", "CHIEF_INFORMATION_SECURITY_OFFICER"),
            human_summary=data.get("human_summary", "Independent pilot readiness advisory assessment verified."),
        )
        serializer = PilotReadinessGateSerializer(gate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
