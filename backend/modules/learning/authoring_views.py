from uuid import UUID
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.learning.curriculum_authoring_service import CurriculumAuthoringService
from modules.learning.models import (
    CurriculumDraftWorkspace,
    ContentChangeSet,
    EditorialReview,
    ReviewComment,
    AssessmentBlueprint,
    RubricDefinition,
    AssessmentReleaseBinding,
    ReleaseReadinessGate,
    CohortRollforwardPlan,
    ReleaseExceptionRecord,
)
from modules.learning.authoring_serializers import (
    CurriculumDraftWorkspaceSerializer,
    ContentChangeSetSerializer,
    EditorialReviewSerializer,
    ReviewCommentSerializer,
    AssessmentBlueprintSerializer,
    RubricDefinitionSerializer,
    AssessmentReleaseBindingSerializer,
    ReleaseReadinessGateSerializer,
    CohortRollforwardPlanSerializer,
    ReleaseExceptionRecordSerializer,
)


from rest_framework.permissions import AllowAny


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


class BaseAuthoringView(APIView):
    authentication_classes = []
    permission_classes = []


class CurriculumDraftWorkspaceView(BaseAuthoringView):
    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        workspaces = CurriculumDraftWorkspace.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:50]
        return Response(CurriculumDraftWorkspaceSerializer(workspaces, many=True).data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _extract_tenant(request)
        # Role check: Learners cannot create authoring workspaces
        role = getattr(request, "user_role", None) or request.headers.get("X-User-Role")
        if role == "LEARNER":
            return Response({"detail": "unauthorized_role: Learners cannot author curriculum."}, status=403)

        data = request.data
        try:
            workspace = CurriculumAuthoringService.create_draft_workspace(
                tenant_id=tenant_id,
                course_id=UUID(data["course_id"]),
                base_version_id=UUID(data["base_version_id"]),
                workspace_title=data.get("workspace_title", ""),
                created_by_id=UUID(data["created_by_id"]) if data.get("created_by_id") else None,
                metadata=data.get("metadata", {}),
            )
            return Response(CurriculumDraftWorkspaceSerializer(workspace).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class ContentChangeSetView(BaseAuthoringView):
    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        change_sets = ContentChangeSet.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:50]
        return Response(ContentChangeSetSerializer(change_sets, many=True).data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _extract_tenant(request)
        role = getattr(request, "user_role", None) or request.headers.get("X-User-Role")
        if role == "LEARNER":
            return Response({"detail": "unauthorized_role: Learners cannot create content change sets."}, status=403)

        data = request.data
        try:
            change_set = CurriculumAuthoringService.create_change_set(
                tenant_id=tenant_id,
                workspace_id=UUID(data["workspace_id"]),
                title=data.get("title", ""),
                change_summary=data.get("change_summary", ""),
                author_id=UUID(data["author_id"]) if data.get("author_id") else None,
            )
            return Response(ContentChangeSetSerializer(change_set).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class SubmitChangeSetView(BaseAuthoringView):
    def post(self, request: Request, pk: str) -> Response:
        tenant_id = _extract_tenant(request)
        try:
            change_set = CurriculumAuthoringService.submit_change_set_for_review(
                tenant_id=tenant_id,
                change_set_id=UUID(pk),
            )
            return Response(ContentChangeSetSerializer(change_set).data, status=200)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class EditorialDecisionView(BaseAuthoringView):
    def post(self, request: Request, pk: str) -> Response:
        tenant_id = _extract_tenant(request)
        data = request.data
        try:
            record = CurriculumAuthoringService.record_editorial_decision(
                tenant_id=tenant_id,
                change_set_id=UUID(pk),
                reviewer_id=UUID(data["reviewer_id"]),
                decision=data.get("decision", "APPROVED"),
                justification=data.get("justification", ""),
            )
            return Response(
                {"status": "recorded", "approval_record_id": str(record.id) if record else None},
                status=200
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"code": "author_self_approval_denied", "detail": str(e)}, status=403)


class AssessmentBlueprintView(BaseAuthoringView):
    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        blueprints = AssessmentBlueprint.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:50]
        return Response(AssessmentBlueprintSerializer(blueprints, many=True).data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _extract_tenant(request)
        data = request.data
        try:
            bp = CurriculumAuthoringService.create_assessment_blueprint(
                tenant_id=tenant_id,
                course_id=UUID(data["course_id"]),
                blueprint_title=data.get("blueprint_title", ""),
                version_tag=data.get("version_tag", "v1.0"),
                pedagogical_intent=data.get("pedagogical_intent", ""),
            )
            return Response(AssessmentBlueprintSerializer(bp).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class RubricDefinitionView(BaseAuthoringView):
    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        rubrics = RubricDefinition.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:50]
        return Response(RubricDefinitionSerializer(rubrics, many=True).data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _extract_tenant(request)
        data = request.data
        try:
            rubric = CurriculumAuthoringService.define_rubric(
                tenant_id=tenant_id,
                blueprint_id=UUID(data["blueprint_id"]),
                rubric_title=data.get("rubric_title", ""),
                criteria_list=data.get("criteria", []),
            )
            return Response(RubricDefinitionSerializer(rubric).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class AssessmentReleaseBindingView(BaseAuthoringView):
    def post(self, request: Request) -> Response:
        tenant_id = _extract_tenant(request)
        data = request.data
        try:
            binding = CurriculumAuthoringService.bind_assessment_to_release(
                tenant_id=tenant_id,
                course_release_id=UUID(data["course_release_id"]),
                blueprint_id=UUID(data["blueprint_id"]),
                rubric_id=UUID(data["rubric_id"]),
            )
            return Response(AssessmentReleaseBindingSerializer(binding).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class ReleaseReadinessEvaluateView(BaseAuthoringView):
    def post(self, request: Request, version_id: str) -> Response:
        tenant_id = _extract_tenant(request)
        role = getattr(request, "user_role", None) or request.headers.get("X-User-Role")
        if role == "LEARNER":
            return Response({"detail": "unauthorized_role: Learners cannot evaluate release readiness."}, status=403)

        try:
            summary = CurriculumAuthoringService.evaluate_release_readiness(
                tenant_id=tenant_id,
                curriculum_version_id=UUID(version_id),
            )
            return Response(summary, status=200)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class ReleaseExceptionGrantView(BaseAuthoringView):
    def post(self, request: Request, gate_id: str) -> Response:
        tenant_id = _extract_tenant(request)
        data = request.data
        try:
            record = CurriculumAuthoringService.grant_release_exception(
                tenant_id=tenant_id,
                gate_id=UUID(gate_id),
                granted_by_id=UUID(data["granted_by_id"]),
                exception_reason=data.get("exception_reason", ""),
            )
            return Response(ReleaseExceptionRecordSerializer(record).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class CohortRollforwardPlanView(BaseAuthoringView):
    def get(self, request: Request) -> Response:
        _check_anti_ranking_query(request)
        tenant_id = _extract_tenant(request)
        plans = CohortRollforwardPlan.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:50]
        return Response(CohortRollforwardPlanSerializer(plans, many=True).data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _extract_tenant(request)
        data = request.data
        try:
            plan = CurriculumAuthoringService.create_cohort_rollforward_plan(
                tenant_id=tenant_id,
                cohort_schedule_id=UUID(data["cohort_schedule_id"]),
                target_release_id=UUID(data["target_release_id"]),
                rollforward_mode=data.get("rollforward_mode", "FUTURE_MODULES_ONLY"),
            )
            return Response(CohortRollforwardPlanSerializer(plan).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
