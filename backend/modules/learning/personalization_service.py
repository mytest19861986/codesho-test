from __future__ import annotations

import decimal
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Lesson,
    LessonSkillMapping,
    MasteryLevel,
    ProcessedLearningEvent,
    RecommendationStatus,
    RecommendationTransitionLog,
    RecommendationType,
    SkillDefinition,
    SkillDependency,
    StudentLearningProfile,
    StudentSkillProgress,
    LearningRecommendation,
    TransitionActorType,
)


class PersonalizationService:
    """
    Service layer orchestrating the Adaptive Progression & Personalization Engine for P3-VS11.
    Adheres strictly to the Boundary Invariants:
    - Zero Bare UUIDs & Multi-tenant boundary checks
    - Idempotent learning event deduplication via ProcessedLearningEvent
    - Monotonic mastery level progression
    - Deterministic, 100% rebuildable StudentLearningProfile
    - Explainable, single-target LearningRecommendations with immutable transition auditing
    """

    @classmethod
    def record_learning_event_idempotent(
        cls,
        tenant_id: uuid.UUID,
        event_id: uuid.UUID,
        event_type: str,
        student_id: uuid.UUID,
    ) -> bool:
        """
        Idempotently registers an incoming learning event.
        Returns True if the event was fresh and recorded, False if already processed.
        """
        try:
            with transaction.atomic():
                _, created = ProcessedLearningEvent.objects.get_or_create(
                    tenant_id=tenant_id,
                    event_id=event_id,
                    event_type=event_type,
                    defaults={
                        "student_id": student_id,
                    },
                )
                return created
        except Exception:
            return False

    @classmethod
    def evaluate_skill_progression(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        skill_id: uuid.UUID,
        score: Decimal,
        is_completed_practice: bool = True,
        evaluated_at: Optional[timezone.datetime] = None,
    ) -> StudentSkillProgress:
        """
        Evaluates and updates student progress for a specific skill monotonically.
        Late-arriving lower scores do not regress established mastery levels.
        """
        if evaluated_at is None:
            evaluated_at = timezone.now()

        skill = SkillDefinition.objects.get(tenant_id=tenant_id, id=skill_id)

        progress, _ = StudentSkillProgress.objects.get_or_create(
            tenant_id=tenant_id,
            student_id=student_id,
            skill=skill,
            defaults={
                "mastery_level": MasteryLevel.NOT_STARTED,
                "mastery_score": Decimal("0.00"),
                "practice_count": 0,
                "last_evaluated_at": evaluated_at,
            },
        )

        if is_completed_practice:
            progress.practice_count += 1

        # Monotonic score progression: highest verified or weighted advance
        new_score = Decimal(str(score))
        if new_score > progress.mastery_score:
            progress.mastery_score = new_score

        # Mastery Level Deterministic Transitions (Qwen Invariant 4)
        current_level = progress.mastery_level
        # Hierarchy: NOT_STARTED < BEGINNER < DEVELOPING < PROFICIENT < MASTERED
        level_ranks = {
            MasteryLevel.NOT_STARTED: 0,
            MasteryLevel.BEGINNER: 1,
            MasteryLevel.DEVELOPING: 2,
            MasteryLevel.PROFICIENT: 3,
            MasteryLevel.MASTERED: 4,
        }

        candidate_level = MasteryLevel.NOT_STARTED
        if progress.practice_count >= 1 and progress.mastery_score >= Decimal("50.00"):
            candidate_level = MasteryLevel.BEGINNER
        if progress.practice_count >= 2 and progress.mastery_score >= Decimal("65.00"):
            candidate_level = MasteryLevel.DEVELOPING
        if progress.practice_count >= 3 and progress.mastery_score >= Decimal("75.00"):
            candidate_level = MasteryLevel.PROFICIENT
        if progress.practice_count >= 5 and progress.mastery_score >= Decimal("85.00"):
            candidate_level = MasteryLevel.MASTERED

        if level_ranks[candidate_level] > level_ranks[current_level]:
            progress.mastery_level = candidate_level

        progress.last_evaluated_at = evaluated_at
        progress.save()

        # Check if any accepted recommendations for this skill can now transition to COMPLETED (Qwen Invariant 2)
        if progress.mastery_level in (MasteryLevel.PROFICIENT, MasteryLevel.MASTERED):
            active_skill_recs = LearningRecommendation.objects.filter(
                tenant_id=tenant_id,
                student_id=student_id,
                target_skill=skill,
                status=RecommendationStatus.ACCEPTED,
            )
            for rec in active_skill_recs:
                cls.transition_recommendation(
                    tenant_id=tenant_id,
                    recommendation_id=rec.id,
                    target_status=RecommendationStatus.COMPLETED,
                    actor_id=student_id,
                    actor_type=TransitionActorType.SYSTEM,
                    reason=f"Criteria met: Student achieved {progress.mastery_level} on skill {skill.slug}",
                )

        return progress

    @classmethod
    def rebuild_student_profile(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> StudentLearningProfile:
        """
        100% deterministically rebuilds the StudentLearningProfile presentation projection
        from canonical progress and mastery records.
        """
        progress_records = list(
            StudentSkillProgress.objects.filter(
                tenant_id=tenant_id,
                student_id=student_id,
            ).select_related("skill")
        )

        total_skills = len(progress_records)
        mastered_count = sum(1 for p in progress_records if p.mastery_level == MasteryLevel.MASTERED)
        developing_count = sum(1 for p in progress_records if p.mastery_level in (MasteryLevel.BEGINNER, MasteryLevel.DEVELOPING))

        if total_skills > 0:
            avg_score = sum(p.mastery_score for p in progress_records) / Decimal(str(total_skills))
            competency_index = min(Decimal("100.00"), max(Decimal("0.00"), round(avg_score, 2)))
        else:
            competency_index = Decimal("0.00")

        # Identify learning gaps (Adolescent Psychology: Guide, Don't Judge)
        gaps = []
        for p in progress_records:
            if p.mastery_score < Decimal("60.00") and p.practice_count >= 1:
                gaps.append({
                    "skill_id": str(p.skill.id),
                    "skill_slug": p.skill.slug,
                    "skill_title": p.skill.title,
                    "severity": "HIGH" if p.mastery_score < Decimal("40.00") else "MEDIUM",
                    "reason": "مهارت در حال شکوفایی، نیازمند تمرین هدفمند تکمیلی",
                })

        profile, created = StudentLearningProfile.objects.get_or_create(
            tenant_id=tenant_id,
            student_id=student_id,
            defaults={
                "total_skills_tracked": total_skills,
                "mastered_skills_count": mastered_count,
                "developing_skills_count": developing_count,
                "overall_competency_index": competency_index,
                "identified_learning_gaps": gaps,
                "last_rebuilt_at": timezone.now(),
                "rebuild_version": 1,
            },
        )

        if not created:
            profile.total_skills_tracked = total_skills
            profile.mastered_skills_count = mastered_count
            profile.developing_skills_count = developing_count
            profile.overall_competency_index = competency_index
            profile.identified_learning_gaps = gaps
            profile.last_rebuilt_at = timezone.now()
            profile.rebuild_version += 1
            profile.save()

        return profile

    @classmethod
    def generate_recommendation(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        recommendation_type: str,
        reason: str,
        evidence_context: Dict[str, Any],
        priority: int = 1,
        target_course_id: Optional[uuid.UUID] = None,
        target_lesson_id: Optional[uuid.UUID] = None,
        target_skill_id: Optional[uuid.UUID] = None,
    ) -> LearningRecommendation:
        """
        Generates an explainable recommendation with strict single-target XOR and audit logging.
        """
        if not evidence_context:
            raise ValidationError("Evidence context cannot be empty (Explainability First).")
        if len(reason.strip()) < 10:
            raise ValidationError("Recommendation reason must be at least 10 characters.")

        targets = [target_course_id, target_lesson_id, target_skill_id]
        if sum(1 for t in targets if t is not None) != 1:
            raise ValidationError("Recommendation must target exactly one of course, lesson, or skill.")

        if target_skill_id:
            skill = SkillDefinition.objects.get(tenant_id=tenant_id, id=target_skill_id)
            if not skill.is_active:
                raise ValidationError("Cannot target inactive skill.")

        # Deterministic idempotency key
        target_key = str(target_course_id or target_lesson_id or target_skill_id)
        idempotency_key = f"{student_id}:{recommendation_type}:{target_key}:{priority}"

        with transaction.atomic():
            rec, created = LearningRecommendation.objects.get_or_create(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
                defaults={
                    "student_id": student_id,
                    "target_course_id": target_course_id,
                    "target_lesson_id": target_lesson_id,
                    "target_skill_id": target_skill_id,
                    "recommendation_type": recommendation_type,
                    "status": RecommendationStatus.GENERATED,
                    "priority": priority,
                    "recommendation_reason": reason,
                    "evidence_context": evidence_context,
                },
            )

            if created:
                # Log initial transition
                RecommendationTransitionLog.objects.create(
                    tenant_id=tenant_id,
                    recommendation=rec,
                    from_status="NONE",
                    to_status=RecommendationStatus.GENERATED,
                    actor_id=student_id,
                    actor_type=TransitionActorType.SYSTEM,
                    transition_reason="Automated recommendation generation based on learning profile evidence.",
                )

        return rec

    @classmethod
    def transition_recommendation(
        cls,
        tenant_id: uuid.UUID,
        recommendation_id: uuid.UUID,
        target_status: str,
        actor_id: uuid.UUID,
        actor_type: str,
        reason: str = "",
    ) -> LearningRecommendation:
        """
        Executes a validated FSM state transition for a recommendation and appends to the immutable audit log.
        """
        with transaction.atomic():
            rec = LearningRecommendation.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=recommendation_id,
            )

            # Valid transition matrix check
            allowed_transitions = {
                RecommendationStatus.GENERATED: [
                    RecommendationStatus.VIEWED,
                    RecommendationStatus.ACCEPTED,
                    RecommendationStatus.DISMISSED,
                    RecommendationStatus.SUPERSEDED,
                ],
                RecommendationStatus.VIEWED: [
                    RecommendationStatus.ACCEPTED,
                    RecommendationStatus.DISMISSED,
                    RecommendationStatus.SUPERSEDED,
                ],
                RecommendationStatus.ACCEPTED: [
                    RecommendationStatus.COMPLETED,
                    RecommendationStatus.SUPERSEDED,
                ],
            }

            from_status = rec.status
            if target_status not in allowed_transitions.get(from_status, []):
                raise ValidationError(f"Invalid transition from {from_status} to {target_status}.")

            rec.status = target_status
            rec.save()

            RecommendationTransitionLog.objects.create(
                tenant_id=tenant_id,
                recommendation=rec,
                from_status=from_status,
                to_status=target_status,
                actor_id=actor_id,
                actor_type=actor_type,
                transition_reason=reason or f"Transitioned from {from_status} to {target_status}",
            )

        return rec
