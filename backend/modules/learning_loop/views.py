from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .permissions import (
    IsTenantMember,
    IsTenantMentor,
    IsTenantGuardian,
    IsTenantLearner,
    IsInternalQualifiedUser,
)
from .services import LearningLoopDomainService
from .serializers import (
    SharedLearningStateAggregateSerializer,
    UpdateInterventionStatusInputSerializer,
    AddFeedbackInputSerializer,
    SaveParentBriefingInputSerializer,
    SendParentEncouragementInputSerializer,
    SubmitEvidenceInputSerializer,
    FeedbackItemSerializer,
    MentorInterventionSerializer,
    ParentBridgeSerializer,
    ActiveProjectSerializer,
)


@extend_schema(
    summary="Get aggregated learning loop state",
    description="Returns cross-role learning loop state scoped to authenticated tenant and user context.",
    responses={200: SharedLearningStateAggregateSerializer},
)
@api_view(["GET"])
@permission_classes([IsTenantMember])
def learning_loop_state_view(request):
    data = LearningLoopDomainService.get_aggregate_state_for_user(
        tenant=request.tenant, user=request.user
    )
    if not data:
        return Response({"detail": "No active learning loop found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = SharedLearningStateAggregateSerializer(data)
    return Response(serializer.data)


@extend_schema(
    summary="Update mentor intervention status",
    request=UpdateInterventionStatusInputSerializer,
    responses={200: MentorInterventionSerializer},
)
@api_view(["POST"])
@permission_classes([IsTenantMentor, IsInternalQualifiedUser])
def update_intervention_status_view(request, intervention_id):
    serializer = UpdateInterventionStatusInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    intervention = LearningLoopDomainService.update_intervention_status(
        tenant=request.tenant,
        intervention_id=intervention_id,
        new_status=serializer.validated_data["status"],
        actor_user=request.user,
    )
    return Response(MentorInterventionSerializer(intervention).data)


@extend_schema(
    summary="Add pedagogical feedback to intervention",
    request=AddFeedbackInputSerializer,
    responses={201: FeedbackItemSerializer},
)
@api_view(["POST"])
@permission_classes([IsTenantMember, IsInternalQualifiedUser])
def add_intervention_feedback_view(request, intervention_id):
    serializer = AddFeedbackInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    sender_role = "MENTOR" if request.tenant_membership.role == "mentor" else "STUDENT"
    feedback = LearningLoopDomainService.add_feedback(
        tenant=request.tenant,
        intervention_id=intervention_id,
        sender_user=request.user,
        sender_role=sender_role,
        action_type=serializer.validated_data["action_type"],
        text=serializer.validated_data["text"],
    )
    return Response(FeedbackItemSerializer(feedback).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Update parent briefing from mentor",
    request=SaveParentBriefingInputSerializer,
    responses={200: ParentBridgeSerializer},
)
@api_view(["POST"])
@permission_classes([IsTenantMentor, IsInternalQualifiedUser])
def update_parent_briefing_view(request, learner_id):
    serializer = SaveParentBriefingInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    bridge = LearningLoopDomainService.update_parent_briefing(
        tenant=request.tenant,
        learner_id=learner_id,
        briefing_text=serializer.validated_data["last_briefing"],
        mentor_user=request.user,
    )
    return Response(ParentBridgeSerializer(bridge).data)


@extend_schema(
    summary="Send parent encouragement praise ribbon",
    request=SendParentEncouragementInputSerializer,
    responses={200: ParentBridgeSerializer},
)
@api_view(["POST"])
@permission_classes([IsTenantGuardian, IsInternalQualifiedUser])
def send_parent_encouragement_view(request, learner_id):
    serializer = SendParentEncouragementInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    bridge = LearningLoopDomainService.send_parent_encouragement(
        tenant=request.tenant,
        learner_id=learner_id,
        message=serializer.validated_data["message"],
        guardian_user=request.user,
    )
    return Response(ParentBridgeSerializer(bridge).data)


@extend_schema(
    summary="Submit learning evidence from learner",
    request=SubmitEvidenceInputSerializer,
    responses={200: ActiveProjectSerializer},
)
@api_view(["POST"])
@permission_classes([IsTenantLearner, IsInternalQualifiedUser])
def submit_evidence_view(request, project_id):
    serializer = SubmitEvidenceInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    project = LearningLoopDomainService.submit_learning_evidence(
        tenant=request.tenant,
        project_id=project_id,
        learner_user=request.user,
        repo_branch=serializer.validated_data["repo_branch"],
        commit_hash=serializer.validated_data["commit_hash"],
        current_milestone=serializer.validated_data["current_milestone"],
        recent_activity=serializer.validated_data["recent_activity"],
        last_code_snippet=serializer.validated_data.get("last_code_snippet", ""),
        progress_percentage=serializer.validated_data.get("progress_percentage"),
    )
    return Response(ActiveProjectSerializer(project).data)
