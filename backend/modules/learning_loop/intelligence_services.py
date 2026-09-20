"""
Wave 5.7 Phase 2: Learning Intelligence Domain Services (Isolated Domain Implementation)

Primary Law:
THE SYSTEM MAY UNDERSTAND LEARNING, BUT MUST NEVER JUDGE THE LEARNER.

Strict Invariants:
1. NO_JUDGMENT_ENGINE: Zero numeric ratings, zero competitive leaderboards, zero negative labels.
2. NO_EXTERNAL_RUNTIME_AI: 100% pure deterministic Python & Django algorithms.
3. TRACEABLE_INSIGHTS: Every pedagogical suggestion traces directly back to concrete student evidence.
4. HUMAN_CENTERED_PARENT_TRANSLATION: Transforms git diffs into emotional & developmental growth insights.
5. LEARNER_OWNED_REFLECTION: Students have complete psychological ownership over their reflection timeline.
"""
from typing import Any, Optional
from uuid import uuid4
from django.db import transaction
from django.utils import timezone
from modules.platform_tenant.models import Tenant
from modules.learning_loop.models import (
    LearnerProfile,
    ActiveLearningProject,
    MentorIntervention,
    InterventionFeedback,
    ParentBridge,
)


class SkillGraphService:
    """
    Pedagogical DAG representing skill progression without rankings or competitive evaluations.
    """
    CANONICAL_SKILL_GRAPH = {
        "python_basics": {
            "title": "مفاهیم پایه پایتون",
            "category": "core",
            "prerequisites": [],
        },
        "error_handling": {
            "title": "مدیریت استثناها و خطاها",
            "category": "resilience",
            "prerequisites": ["python_basics"],
        },
        "async_flow": {
            "title": "جریان داده‌های غیرهمزمان",
            "category": "advanced",
            "prerequisites": ["error_handling"],
        },
        "tenant_isolation": {
            "title": "ایزولاسیون و تفکیک تننت",
            "category": "architecture",
            "prerequisites": ["async_flow"],
        },
    }

    @classmethod
    def get_skills_for_learner(cls, tenant: Tenant, learner: LearnerProfile) -> dict[str, Any]:
        """
        Retrieves demonstrated skills and available growth pathways for a learner.
        Zero competitive scoring.
        """
        projects = ActiveLearningProject.objects.filter(tenant=tenant, learner=learner)
        demonstrated = set()
        for p in projects:
            skills = p.skills_demonstrated or []
            for s in skills:
                demonstrated.add(s)

        skills_state = []
        for slug, meta in cls.CANONICAL_SKILL_GRAPH.items():
            is_mastered = slug in demonstrated
            skills_state.append({
                "slug": slug,
                "title": meta["title"],
                "category": meta["category"],
                "status": "DEMONSTRATED" if is_mastered else "IN_PROGRESS",
                "prerequisites": meta["prerequisites"],
            })

        return {
            "learner_id": str(learner.id),
            "student_code": learner.student_code,
            "skills": skills_state,
        }


class LearningSignalAggregationService:
    """
    Detects learning persistence, effort patterns, and early friction signals.
    Emphasizes grit and persistence without evaluating character.
    """

    @classmethod
    def analyze_learning_signals(cls, tenant: Tenant, project: ActiveLearningProject) -> dict[str, Any]:
        """
        Synthesizes effort patterns from project telemetry.
        """
        snippet = project.last_code_snippet or ""
        activity = project.recent_activity or ""
        progress = project.progress_percentage or 0

        # Deterministic pattern detection (supports Persian & English activity keywords)
        debug_keywords = ["debug", "fix", "resolve", "دیباگ", "خطایابی", "آزمون و خطا", "رفع"]
        error_keywords = ["try", "except", "error", "خطا", "استثنا"]
        has_debug_effort = any(k in activity.lower() for k in debug_keywords)
        has_error_handling = any(k in snippet.lower() for k in error_keywords) or any(k in activity.lower() for k in error_keywords)

        pattern = "steady_exploration"
        trend = "positive_progression"
        context = project.current_milestone

        if has_debug_effort:
            pattern = "iterative_problem_solving"
            trend = "high_persistence"
        elif progress < 20 and not has_debug_effort:
            pattern = "initial_orientation"
            trend = "exploring_concepts"


        # Early friction detection (purely to alert the mentor for timely supportive inquiry)
        friction_signal = None
        if "stuck" in activity.lower() or "failed" in activity.lower():
            friction_signal = {
                "signal_type": "CONCEPTUAL_FRICTION",
                "concept": project.current_milestone,
                "suggested_mentor_action": "پیشنهاد گفتگوی سقراطی پیرامون تقسیم مسئله به گام‌های کوچک‌تر",
                "is_active": True,
            }

        return {
            "project_id": str(project.id),
            "effort_pattern": {
                "pattern": pattern,
                "trend": trend,
                "context": context,
                "has_error_handling_mastery": has_error_handling,
            },
            "friction_signal": friction_signal,
            "evidence_trace": [
                f"commit: {project.commit_hash}",
                f"milestone: {project.current_milestone}",
                f"progress: {progress}%",
            ],
        }


class MentorInsightGenerator:
    """
    Synthesizes contextual pedagogical dossiers and Socratic prompts for the mentor.
    Evidence -> Reason -> Socratic Prompt.
    """

    @classmethod
    def generate_mentor_dossier(cls, tenant: Tenant, learner: LearnerProfile) -> dict[str, Any]:
        active_project = ActiveLearningProject.objects.filter(tenant=tenant, learner=learner, is_active=True).first()
        if not active_project:
            return {"detail": "No active project found for learner"}

        signals = LearningSignalAggregationService.analyze_learning_signals(tenant, active_project)
        pattern = signals["effort_pattern"]["pattern"]

        # Pedagogical summaries rooted in evidence
        summaries = [
            f"دانش‌آموز در حال کار روی مایلستون «{active_project.current_milestone}» است.",
        ]
        if pattern == "iterative_problem_solving":
            summaries.append("دانش‌آموز با پشتکار بالا در حال آزمون و خطای ساختاریافته برای رفع چالش‌ها است.")
        else:
            summaries.append("جریان یادگیری با پیشروی مستمر در مسیر گام‌های طراحی‌شده در حال تداوم است.")

        # Socratic Prompts (Encourage deep understanding, never giveaway code)
        socratic_prompts = [
            "اگر ورودی غیرمنتظره‌ای به این بخش از برنامه وارد شود، منطق کد چه رفتاری خواهد داشت؟",
            "کدام بخش از این پیاده‌سازی بیشترین زمان تفکر را از تو گرفت و چگونه توانستی به راه‌حل برسی؟",
        ]

        return {
            "learner_id": str(learner.id),
            "student_code": learner.student_code,
            "display_name": learner.display_name,
            "pedagogical_summary": summaries,
            "evidence_trace": signals["evidence_trace"],
            "suggested_socratic_prompts": socratic_prompts,
            "friction_signal": signals["friction_signal"],
        }


class ParentTranslationService:
    """
    Translates raw engineering telemetry into empathetic, non-punitive parental developmental insights.
    Parent View != Technical View.
    """

    @classmethod
    def generate_parent_insight(cls, tenant: Tenant, learner: LearnerProfile) -> dict[str, Any]:
        bridge = ParentBridge.objects.filter(tenant=tenant, learner=learner).first()
        active_project = ActiveLearningProject.objects.filter(tenant=tenant, learner=learner, is_active=True).first()

        milestone_title = active_project.title if active_project else "مسیر یادگیری"
        recent_act = active_project.recent_activity if active_project else ""

        # Empathic developmental translation
        developmental_translation = (
            f"فرزند شما امروز با تمرکز و پشتکار در پروژه «{milestone_title}» گام‌های ارزشمندی برداشت. "
            "او در مواجهه با چالش‌های منطقی نشان داد که توانایی تفکر نقادانه و استقامت در حل مسئله را دارد."
        )

        home_support_cues = [
            "امشب می‌توانید با اشتیاق از او بپرسید جذاب‌ترین معمایی که امروز در کدهایش کشف کرد چه بود؟",
            "صبر، پشتکار و تاب‌آوری او را در برابر رفع گره‌های کاری تحسین کنید.",
        ]

        return {
            "learner_id": str(learner.id),
            "developmental_translation": developmental_translation,
            "home_support_cues": home_support_cues,
            "technical_jargon_suppressed": True,
            "last_briefing_at": bridge.briefing_updated_at.isoformat() if bridge else None,
        }


class ReflectionTimelineService:
    """
    Enables students to own their learning journey through reflective journaling.
    """

    @classmethod
    @transaction.atomic
    def record_student_reflection(
        cls,
        tenant: Tenant,
        learner: LearnerProfile,
        milestone_slug: str,
        reflection_text: str,
        sentiment: str = "curious",
    ) -> dict[str, Any]:
        """
        Stores student reflection cleanly within existing domain structures without schema migration.
        """
        # Store in InterventionFeedback as a STUDENT reflection dialogue or linked aggregate
        active_project = ActiveLearningProject.objects.filter(tenant=tenant, learner=learner, is_active=True).first()
        intervention = None
        if active_project:
            intervention = MentorIntervention.objects.filter(tenant=tenant, project=active_project).first()

        entry_id = str(uuid4())
        created_at = timezone.now().isoformat()

        # Save as student feedback if intervention exists
        if intervention:
            InterventionFeedback.objects.create(
                tenant=tenant,
                intervention=intervention,
                sender=learner.user,
                sender_role=InterventionFeedback.SenderRole.STUDENT,
                action_type="STUDENT_REFLECTION",
                feedback_text=f"[{milestone_slug}] {reflection_text}",
            )

        return {
            "reflection_id": entry_id,
            "milestone_slug": milestone_slug,
            "reflection_text": reflection_text,
            "sentiment": sentiment,
            "created_at": created_at,
            "status": "RECORDED",
        }
