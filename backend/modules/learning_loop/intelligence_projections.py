"""
Wave 5.7 Phase 3: Intelligence Read Projection Service.

Orchestrates read model compilation across domain services, enforcing role boundaries and tenant scoping.
"""
from typing import Any, Optional
from modules.platform_tenant.models import Tenant, TenantMembership
from modules.learning_loop.models import LearnerProfile
from .intelligence_services import (
    SkillGraphService,
    MentorInsightGenerator,
    ParentTranslationService,
)
from .intelligence_serializers import (
    LearnerSkillGraphReadModelSerializer,
    MentorIntelligenceDossierReadModelSerializer,
    ParentInsightReadModelSerializer,
    UnifiedIntelligenceProjectionSerializer,
)


class IntelligenceReadProjectionService:
    """
    Assembles sanitized read projections conforming to the Intelligence Read Contract.
    """

    @classmethod
    def get_learner_skill_graph_projection(cls, tenant: Tenant, learner: LearnerProfile) -> dict[str, Any]:
        data = SkillGraphService.get_skills_for_learner(tenant, learner)
        serializer = LearnerSkillGraphReadModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @classmethod
    def get_mentor_dossier_projection(cls, tenant: Tenant, learner: LearnerProfile) -> dict[str, Any]:
        data = MentorInsightGenerator.generate_mentor_dossier(tenant, learner)
        serializer = MentorIntelligenceDossierReadModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @classmethod
    def get_parent_insight_projection(cls, tenant: Tenant, learner: LearnerProfile) -> dict[str, Any]:
        data = ParentTranslationService.generate_parent_insight(tenant, learner)
        serializer = ParentInsightReadModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @classmethod
    def get_role_scoped_projection(
        cls,
        tenant: Tenant,
        user: Any,
        learner: LearnerProfile,
        user_role: str,
    ) -> dict[str, Any]:
        """
        Compiles a role-filtered projection ensuring strict privacy and role boundaries.
        - LEARNER: Skill Graph + Reflections (Own)
        - MENTOR: Skill Graph + Mentor Dossier (Socratic Prompts, Friction Signals)
        - GUARDIAN: Parent Insight (Jargon-free Growth Language)
        """
        payload: dict[str, Any] = {}

        if user_role in (TenantMembership.Role.LEARNER, TenantMembership.Role.MENTOR, TenantMembership.Role.ADMIN, TenantMembership.Role.OWNER):
            payload["skill_graph"] = cls.get_learner_skill_graph_projection(tenant, learner)

        if user_role in (TenantMembership.Role.MENTOR, TenantMembership.Role.ADMIN, TenantMembership.Role.OWNER):
            payload["mentor_dossier"] = cls.get_mentor_dossier_projection(tenant, learner)

        if user_role in (TenantMembership.Role.GUARDIAN, TenantMembership.Role.ADMIN, TenantMembership.Role.OWNER):
            payload["parent_insight"] = cls.get_parent_insight_projection(tenant, learner)

        serializer = UnifiedIntelligenceProjectionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
