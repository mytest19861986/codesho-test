from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone

from modules.platform_tenant.models import GuardianAccessGrant
from .models import (
    LearningPortfolio,
    AchievementArtifact,
    StudentJourneyTimeline,
    PortfolioModerationAction,
    PortfolioVisibility,
    PortfolioModerationStatus,
    ArtifactType,
    ModerationActionType,
)


class PortfolioService:
    """
    P3-VS12 Service Layer: Learning Portfolio, Achievement Artifacts, and Student Journey Narrative.
    Strictly enforces:
    - Zero Bare UUIDs & Fail-closed multi-tenant boundary checks
    - Showcase Consent Guard: No Consent = No Showcase (Visibility = TENANT_PUBLIC strictly requires APPROVED + public_consent_active)
    - Append-only audit logging of moderation & consent actions
    - Guardian access lifecycle management (PENDING -> ACTIVE -> REVOKED)
    - Zero PII in timeline narrative metadata
    """

    @classmethod
    def create_or_get_portfolio(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        headline: str,
        summary_narrative: str = "",
    ) -> LearningPortfolio:
        """
        Creates or retrieves a student's learning portfolio with default fail-closed security:
        visibility=PRIVATE, moderation_status=PENDING.
        """
        if len(headline.strip()) < 5:
            raise ValidationError("Headline must be at least 5 characters.")

        with transaction.atomic():
            portfolio, created = LearningPortfolio.objects.get_or_create(
                tenant_id=tenant_id,
                student_id=student_id,
                defaults={
                    "headline": headline.strip(),
                    "summary_narrative": summary_narrative.strip(),
                    "visibility": PortfolioVisibility.PRIVATE,
                    "moderation_status": PortfolioModerationStatus.PENDING,
                    "public_consent_active": False,
                },
            )
            return portfolio

    @classmethod
    def update_visibility(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        target_visibility: str,
    ) -> LearningPortfolio:
        """
        Updates portfolio visibility respecting child privacy state machine.
        Transitioning to TENANT_PUBLIC requires APPROVED moderation status AND active consent.
        Transitioning away from TENANT_PUBLIC instantly revokes public consent.
        """
        with transaction.atomic():
            portfolio = LearningPortfolio.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=portfolio_id,
                student_id=student_id,
            )

            if target_visibility == PortfolioVisibility.TENANT_PUBLIC:
                if portfolio.moderation_status != PortfolioModerationStatus.APPROVED or not portfolio.public_consent_active:
                    raise ValidationError("Cannot publish to showcase without APPROVED moderation and active consent.")
            elif portfolio.visibility == PortfolioVisibility.TENANT_PUBLIC and target_visibility != PortfolioVisibility.TENANT_PUBLIC:
                # Instant retraction
                portfolio.public_consent_active = False
                portfolio.public_consent_at = None
                PortfolioModerationAction.objects.create(
                    tenant_id=tenant_id,
                    target_portfolio=portfolio,
                    actor_id=student_id,
                    action_type=ModerationActionType.CONSENT_REVOKE,
                    reason="Student retracted public showcase consent",
                )

            portfolio.visibility = target_visibility
            portfolio.save()
            return portfolio

    @classmethod
    def grant_showcase_consent(
        cls,
        tenant_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        consenting_user_id: uuid.UUID,
    ) -> LearningPortfolio:
        """
        Grants explicit consent to showcase the student portfolio.
        Records an append-only audit event in PortfolioModerationAction.
        """
        with transaction.atomic():
            portfolio = LearningPortfolio.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=portfolio_id,
            )
            portfolio.public_consent_active = True
            portfolio.public_consent_by = consenting_user_id
            portfolio.public_consent_at = timezone.now()
            portfolio.save()

            PortfolioModerationAction.objects.create(
                tenant_id=tenant_id,
                target_portfolio=portfolio,
                actor_id=consenting_user_id,
                action_type=ModerationActionType.CONSENT_GRANT,
                reason="Showcase consent granted",
            )
            return portfolio

    @classmethod
    def revoke_showcase_consent(
        cls,
        tenant_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        revoking_user_id: uuid.UUID,
        reason: str = "Consent revoked",
    ) -> LearningPortfolio:
        """
        Instantly revokes consent and demotes visibility away from TENANT_PUBLIC if active.
        """
        with transaction.atomic():
            portfolio = LearningPortfolio.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=portfolio_id,
            )
            portfolio.public_consent_active = False
            portfolio.public_consent_by = None
            portfolio.public_consent_at = None
            if portfolio.visibility == PortfolioVisibility.TENANT_PUBLIC:
                portfolio.visibility = PortfolioVisibility.GUARDIAN_SHARED
            portfolio.save()

            PortfolioModerationAction.objects.create(
                tenant_id=tenant_id,
                target_portfolio=portfolio,
                actor_id=revoking_user_id,
                action_type=ModerationActionType.CONSENT_REVOKE,
                reason=reason,
            )
            return portfolio

    @classmethod
    def moderate_portfolio(
        cls,
        tenant_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        moderator_id: uuid.UUID,
        action: str,
        reason: str = "",
    ) -> LearningPortfolio:
        """
        Moderates a portfolio (APPROVE, FLAG, UNFLAG, REMOVE, RESTORE).
        Author self-approval is strictly forbidden (403 Forbidden).
        """
        with transaction.atomic():
            portfolio = LearningPortfolio.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=portfolio_id,
            )
            if str(portfolio.student_id) == str(moderator_id) and action == ModerationActionType.APPROVE:
                raise PermissionDenied("Author cannot self-approve their own learning portfolio.")

            if action == ModerationActionType.APPROVE:
                portfolio.moderation_status = PortfolioModerationStatus.APPROVED
            elif action == ModerationActionType.FLAG:
                portfolio.moderation_status = PortfolioModerationStatus.FLAGGED
                if portfolio.visibility == PortfolioVisibility.TENANT_PUBLIC:
                    portfolio.visibility = PortfolioVisibility.GUARDIAN_SHARED
            elif action == ModerationActionType.UNFLAG:
                portfolio.moderation_status = PortfolioModerationStatus.APPROVED
            elif action == ModerationActionType.REMOVE:
                portfolio.moderation_status = PortfolioModerationStatus.REMOVED
                portfolio.visibility = PortfolioVisibility.PRIVATE
            elif action == ModerationActionType.RESTORE:
                portfolio.moderation_status = PortfolioModerationStatus.PENDING
            else:
                raise ValidationError(f"Invalid moderation action: {action}")

            portfolio.save()

            PortfolioModerationAction.objects.create(
                tenant_id=tenant_id,
                target_portfolio=portfolio,
                actor_id=moderator_id,
                action_type=action,
                reason=reason,
            )
            return portfolio

    @classmethod
    def attach_achievement_artifact(
        cls,
        tenant_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        artifact_type: str,
        title: str,
        reflection_notes: str = "",
        mentor_user_id: Optional[uuid.UUID] = None,
        source_submission_id: Optional[uuid.UUID] = None,
        source_certificate_id: Optional[uuid.UUID] = None,
        is_featured: bool = False,
    ) -> AchievementArtifact:
        """
        Attaches a verified achievement artifact to a student portfolio.
        Enforces evidence source rules: CAPSTONE_SUBMISSION must link to submission,
        CERTIFICATE must link to certificate.
        """
        with transaction.atomic():
            portfolio = LearningPortfolio.objects.filter(id=portfolio_id).first()
            if not portfolio or str(portfolio.tenant_id) != str(tenant_id):
                raise ValidationError("Cross-tenant artifact attachment blocked: portfolio does not belong to specified tenant.")

            if source_submission_id:
                from modules.learning.models import Submission
                sub = Submission.objects.filter(id=source_submission_id).first()
                if not sub or str(sub.tenant_id) != str(tenant_id):
                    raise ValidationError("Cross-tenant or non-existent source submission link rejected.")

            if source_certificate_id:
                from modules.learning.models import CourseCertificate
                cert = CourseCertificate.objects.filter(id=source_certificate_id).first()
                if not cert or str(cert.tenant_id) != str(tenant_id):
                    raise ValidationError("Cross-tenant or non-existent source certificate link rejected.")

            artifact = AchievementArtifact(
                tenant_id=tenant_id,
                portfolio=portfolio,
                artifact_type=artifact_type,
                title=title.strip(),
                reflection_notes=reflection_notes.strip(),
                mentor_user_id=mentor_user_id,
                source_submission_id=source_submission_id,
                source_certificate_id=source_certificate_id,
                is_featured=is_featured,
                moderation_status=PortfolioModerationStatus.PENDING,
            )
            artifact.full_clean()
            artifact.save()

            if is_featured:
                portfolio.featured_artifact_count = portfolio.artifacts.filter(is_featured=True).count()
                portfolio.save()

            return artifact

    @classmethod
    def endorse_artifact(
        cls,
        tenant_id: uuid.UUID,
        artifact_id: uuid.UUID,
        mentor_user_id: uuid.UUID,
        endorsement_text: str,
    ) -> AchievementArtifact:
        """
        Allows a mentor to endorse an achievement artifact.
        """
        if len(endorsement_text.strip()) < 5:
            raise ValidationError("Endorsement text must be at least 5 characters.")

        with transaction.atomic():
            artifact = AchievementArtifact.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=artifact_id,
            )
            artifact.mentor_endorsement = endorsement_text.strip()
            artifact.mentor_user_id = mentor_user_id
            artifact.save()
            return artifact

    @classmethod
    def log_journey_milestone(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        event_key: str,
        event_title: str,
        narrative_description: str,
        milestone_date,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StudentJourneyTimeline:
        """
        Logs an educational journey milestone. Strictly rejects PII in metadata.
        """
        if metadata is None:
            metadata = {}

        milestone = StudentJourneyTimeline(
            tenant_id=tenant_id,
            student_id=student_id,
            event_key=event_key.strip(),
            event_title=event_title.strip(),
            narrative_description=narrative_description.strip(),
            milestone_date=milestone_date,
            metadata=metadata,
        )
        milestone.full_clean()
        milestone.save()
        return milestone

    @classmethod
    def request_guardian_access(
        cls,
        tenant_id: uuid.UUID,
        guardian_user_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> GuardianAccessGrant:
        """
        Requests guardian access grant for a student in status PENDING.
        """
        with transaction.atomic():
            grant, created = GuardianAccessGrant.objects.get_or_create(
                tenant_id=tenant_id,
                guardian_user_id=guardian_user_id,
                student_id=student_id,
                status=GuardianAccessGrant.Status.PENDING,
            )
            return grant

    @classmethod
    def decide_guardian_access(
        cls,
        tenant_id: uuid.UUID,
        grant_id: uuid.UUID,
        approve: bool,
    ) -> GuardianAccessGrant:
        """
        Approves or denies guardian access.
        Sets decided_at on activation.
        """
        with transaction.atomic():
            grant = GuardianAccessGrant.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=grant_id,
            )
            now = timezone.now()
            if approve:
                grant.status = GuardianAccessGrant.Status.ACTIVE
                grant.decided_at = now
            else:
                grant.status = GuardianAccessGrant.Status.REVOKED
                grant.decided_at = now
                grant.revoked_at = now
            grant.save()
            return grant

    @classmethod
    def revoke_guardian_access(
        cls,
        tenant_id: uuid.UUID,
        grant_id: uuid.UUID,
    ) -> GuardianAccessGrant:
        """
        Revokes an active guardian access grant.
        Preserves decided_at for minor privacy audit trail, sets revoked_at.
        """
        with transaction.atomic():
            grant = GuardianAccessGrant.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=grant_id,
            )
            grant.status = GuardianAccessGrant.Status.REVOKED
            grant.revoked_at = timezone.now()
            grant.save()
            return grant
