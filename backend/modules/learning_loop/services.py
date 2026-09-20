from typing import Any
from django.db import transaction
from django.utils import timezone
from modules.platform_tenant.models import Tenant
from .models import (
    LearnerProfile,
    ActiveLearningProject,
    MentorIntervention,
    InterventionFeedback,
    ParentBridge,
)


class LearningLoopDomainService:
    """
    Core Domain Service coordinating educational state transitions within Tenant boundaries.
    """

    @staticmethod
    def get_aggregate_state_for_user(tenant: Tenant, user: Any) -> dict[str, Any]:
        """
        Retrieves the bounded learning state for a learner, or for a mentor/guardian
        associated with their active learner.
        """
        # Resolve learner profile
        learner = (
            LearnerProfile.objects.filter(tenant=tenant, user=user).first()
            or LearnerProfile.objects.filter(tenant=tenant, assigned_mentor=user).first()
            or LearnerProfile.objects.filter(tenant=tenant, guardian=user).first()
            or LearnerProfile.objects.filter(tenant=tenant).first()
        )

        if not learner:
            # Return empty or unseeded structure
            return {}

        active_project = (
            ActiveLearningProject.objects.filter(
                tenant=tenant, learner=learner, is_active=True
            ).first()
            or ActiveLearningProject.objects.filter(tenant=tenant, learner=learner).first()
        )

        mentor_intervention = None
        if active_project:
            mentor_intervention = (
                MentorIntervention.objects.filter(
                    tenant=tenant, project=active_project
                )
                .prefetch_related("feedbacks")
                .first()
            )

        parent_bridge = getattr(learner, "parent_bridge", None)
        if parent_bridge is None:
            parent_bridge = ParentBridge.objects.filter(tenant=tenant, learner=learner).first()

        return {
            "student": learner,
            "active_project": active_project,
            "mentor_intervention": mentor_intervention,
            "parent_bridge": parent_bridge,
        }

    @staticmethod
    @transaction.atomic
    def update_intervention_status(
        tenant: Tenant,
        intervention_id: str,
        new_status: str,
        actor_user: Any,
    ) -> MentorIntervention:
        intervention = MentorIntervention.objects.select_for_update().get(
            id=intervention_id, tenant=tenant
        )
        intervention.status = new_status
        intervention.save(update_fields=["status", "updated_at"])
        return intervention

    @staticmethod
    @transaction.atomic
    def add_feedback(
        tenant: Tenant,
        intervention_id: str,
        sender_user: Any,
        sender_role: str,
        action_type: str,
        text: str,
    ) -> InterventionFeedback:
        intervention = MentorIntervention.objects.get(id=intervention_id, tenant=tenant)
        feedback = InterventionFeedback.objects.create(
            tenant=tenant,
            intervention=intervention,
            sender=sender_user,
            sender_role=sender_role,
            action_type=action_type,
            feedback_text=text,
        )
        return feedback

    @staticmethod
    @transaction.atomic
    def update_parent_briefing(
        tenant: Tenant,
        learner_id: str,
        briefing_text: str,
        mentor_user: Any,
    ) -> ParentBridge:
        learner = LearnerProfile.objects.get(id=learner_id, tenant=tenant)
        bridge, _ = ParentBridge.objects.select_for_update().get_or_create(
            tenant=tenant,
            learner=learner,
            defaults={"last_briefing": briefing_text},
        )
        bridge.last_briefing = briefing_text
        bridge.save(update_fields=["last_briefing", "briefing_updated_at"])
        return bridge

    @staticmethod
    @transaction.atomic
    def send_parent_encouragement(
        tenant: Tenant,
        learner_id: str,
        message: str,
        guardian_user: Any,
    ) -> ParentBridge:
        learner = LearnerProfile.objects.get(id=learner_id, tenant=tenant)
        bridge, _ = ParentBridge.objects.select_for_update().get_or_create(
            tenant=tenant,
            learner=learner,
            defaults={
                "last_briefing": "گزارش وضعیت یادگیری",
                "parent_encouragement_sent": True,
                "parent_encouragement_message": message,
                "encouragement_updated_at": timezone.now(),
            },
        )
        bridge.parent_encouragement_sent = True
        bridge.parent_encouragement_message = message
        bridge.encouragement_updated_at = timezone.now()
        bridge.save(
            update_fields=[
                "parent_encouragement_sent",
                "parent_encouragement_message",
                "encouragement_updated_at",
            ]
        )
        return bridge

    @staticmethod
    @transaction.atomic
    def submit_learning_evidence(
        tenant: Tenant,
        project_id: str,
        learner_user: Any,
        repo_branch: str,
        commit_hash: str,
        current_milestone: str,
        recent_activity: str,
        last_code_snippet: str = "",
        progress_percentage: int = None,
    ) -> ActiveLearningProject:
        project = ActiveLearningProject.objects.select_for_update().get(
            id=project_id, tenant=tenant, learner__user=learner_user
        )
        project.repo_branch = repo_branch
        project.commit_hash = commit_hash
        project.current_milestone = current_milestone
        project.recent_activity = recent_activity
        if last_code_snippet:
            project.last_code_snippet = last_code_snippet
        if progress_percentage is not None:
            project.progress_percentage = progress_percentage
        project.save(
            update_fields=[
                "repo_branch",
                "commit_hash",
                "current_milestone",
                "recent_activity",
                "last_code_snippet",
                "progress_percentage",
                "updated_at",
            ]
        )
        return project
