import datetime
import uuid
from typing import Any, Tuple
from django.db import transaction
from django.utils import timezone

from .models import (
    BadgeDefinition,
    StudentBadgeAward,
    StudentProgressionProfile,
)


class GamificationEngine:
    """
    Event-driven gamification and progression evaluation engine.
    Strictly Zero-PII, tenant-bounded, idempotent, with optimistic locking and UTC Midnight day boundary.
    """

    DEFAULT_BADGES = [
        {
            "badge_code": "FIRST_LESSON",
            "badge_level": 1,
            "title": "نخستین گام یادگیری",
            "description": "تکمیل موفقیت‌آمیز اولین درس",
            "threshold": 1,
            "is_repeatable": False,
        },
        {
            "badge_code": "STREAK_3_DAYS",
            "badge_level": 1,
            "title": "پشتکار ۳ روزه",
            "description": "استمرار در فعالیت آموزشی برای ۳ روز پیاپی",
            "threshold": 3,
            "is_repeatable": False,
        },
        {
            "badge_code": "STREAK_7_DAYS",
            "badge_level": 1,
            "title": "مشعل یادگیری",
            "description": "استمرار در فعالیت آموزشی برای ۷ روز پیاپی",
            "threshold": 7,
            "is_repeatable": False,
        },
        {
            "badge_code": "SUBMISSION_STAR",
            "badge_level": 1,
            "title": "تلاشگر برتر",
            "description": "بررسی و تایید اولین تکلیف ارسالی",
            "threshold": 1,
            "is_repeatable": False,
        },
    ]

    @classmethod
    def ensure_default_badges(cls) -> None:
        """Bootstraps default badge catalog idempotently."""
        for b in cls.DEFAULT_BADGES:
            BadgeDefinition.objects.get_or_create(
                badge_code=b["badge_code"],
                badge_level=b["badge_level"],
                defaults={
                    "title": b["title"],
                    "description": b["description"],
                    "threshold": b["threshold"],
                    "is_repeatable": b["is_repeatable"],
                },
            )

    @classmethod
    def normalize_utc_date(cls, dt: datetime.datetime | None = None) -> datetime.date:
        """
        Calculates UTC date boundary strictly from UTC Midnight.
        Avoids any browser or local server timezone drift.
        """
        if dt is None:
            dt = timezone.now()
        if timezone.is_aware(dt):
            dt = dt.astimezone(datetime.timezone.utc)
        return dt.date()

    @classmethod
    def handle_learning_event(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        event_type: str,
        event_id: uuid.UUID,
        occurred_at: datetime.datetime | None = None,
    ) -> Tuple[StudentProgressionProfile, list[StudentBadgeAward]]:
        """
        Processes authoritative learning event (e.g. lesson_completed, submission_reviewed).
        Updates student progression profile using optimistic locking and evaluates badge awards idempotently.
        """
        cls.ensure_default_badges()

        today_utc = cls.normalize_utc_date(occurred_at)

        # Retry loop for optimistic locking
        for attempt in range(5):
            with transaction.atomic():
                profile, created = StudentProgressionProfile.objects.select_for_update().get_or_create(
                    tenant_id=tenant_id,
                    student_id=student_id,
                    defaults={
                        "current_streak_days": 1,
                        "longest_streak_days": 1,
                        "last_qualifying_date": today_utc,
                        "total_xp": 10,
                        "completed_lessons_count": 1 if event_type == "lesson_completed" else 0,
                        "reviewed_submissions_count": 1 if event_type == "submission_reviewed" else 0,
                        "version": 1,
                    },
                )

                if not created:
                    # Check streak progression
                    last_date = profile.last_qualifying_date
                    if last_date is None:
                        profile.current_streak_days = 1
                        profile.last_qualifying_date = today_utc
                    elif last_date == today_utc:
                        # Same day: deduplication per day rule
                        pass
                    elif last_date == today_utc - datetime.timedelta(days=1):
                        # Consecutive day
                        profile.current_streak_days += 1
                        profile.last_qualifying_date = today_utc
                    else:
                        # Streak broken
                        profile.current_streak_days = 1
                        profile.last_qualifying_date = today_utc

                    if profile.current_streak_days > profile.longest_streak_days:
                        profile.longest_streak_days = profile.current_streak_days

                    # Update event specific counters
                    if event_type == "lesson_completed":
                        profile.completed_lessons_count += 1
                        profile.total_xp += 20
                    elif event_type == "submission_reviewed":
                        profile.reviewed_submissions_count += 1
                        profile.total_xp += 30

                    profile.level = max(1, (profile.total_xp // 100) + 1)
                    profile.version += 1
                    profile.save()

                # Evaluate Badges
                awarded_badges: list[StudentBadgeAward] = []

                # Badge 1: FIRST_LESSON
                if profile.completed_lessons_count >= 1:
                    award = cls._grant_badge_if_eligible(
                        tenant_id=tenant_id,
                        student_id=student_id,
                        badge_code="FIRST_LESSON",
                        badge_level=1,
                        source_event_id=event_id,
                    )
                    if award:
                        awarded_badges.append(award)

                # Badge 2: STREAK_3_DAYS
                if profile.current_streak_days >= 3 or profile.longest_streak_days >= 3:
                    award = cls._grant_badge_if_eligible(
                        tenant_id=tenant_id,
                        student_id=student_id,
                        badge_code="STREAK_3_DAYS",
                        badge_level=1,
                        source_event_id=event_id,
                    )
                    if award:
                        awarded_badges.append(award)

                # Badge 3: STREAK_7_DAYS
                if profile.current_streak_days >= 7 or profile.longest_streak_days >= 7:
                    award = cls._grant_badge_if_eligible(
                        tenant_id=tenant_id,
                        student_id=student_id,
                        badge_code="STREAK_7_DAYS",
                        badge_level=1,
                        source_event_id=event_id,
                    )
                    if award:
                        awarded_badges.append(award)

                # Badge 4: SUBMISSION_STAR
                if profile.reviewed_submissions_count >= 1:
                    award = cls._grant_badge_if_eligible(
                        tenant_id=tenant_id,
                        student_id=student_id,
                        badge_code="SUBMISSION_STAR",
                        badge_level=1,
                        source_event_id=event_id,
                    )
                    if award:
                        awarded_badges.append(award)

                return profile, awarded_badges

        raise RuntimeError("Optimistic locking conflict in GamificationEngine")

    @classmethod
    def _grant_badge_if_eligible(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        badge_code: str,
        badge_level: int,
        source_event_id: uuid.UUID | None = None,
    ) -> StudentBadgeAward | None:
        """Idempotently grants badge if not already awarded."""
        badge_def = BadgeDefinition.objects.filter(
            badge_code=badge_code, badge_level=badge_level
        ).first()
        if not badge_def:
            return None

        # Check existing award
        existing = StudentBadgeAward.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
            badge_code=badge_code,
            badge_level=badge_level,
        ).first()
        if existing:
            return None

        idemp_key = f"{tenant_id}:{student_id}:{badge_code}:{badge_level}"
        award, _ = StudentBadgeAward.objects.get_or_create(
            tenant_id=tenant_id,
            student_id=student_id,
            badge=badge_def,
            badge_code=badge_code,
            badge_level=badge_level,
            defaults={
                "source_event_id": source_event_id,
                "idempotency_key": idemp_key,
            },
        )
        return award
