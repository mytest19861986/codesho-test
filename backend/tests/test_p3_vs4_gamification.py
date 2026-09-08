import datetime
import uuid
import pytest
from django.utils import timezone

from modules.learning.gamification import GamificationEngine
from modules.learning.models import (
    BadgeDefinition,
    StudentBadgeAward,
    StudentProgressionProfile,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_gamification_utc_boundary_and_streak_progression():
    tenant = Tenant.objects.create(name="T1", slug=f"t1-{uuid.uuid4().hex[:6]}")
    student_id = uuid.uuid4()

    # Day 1: 2026-09-01 23:59:00 UTC
    dt_day1 = datetime.datetime(2026, 9, 1, 23, 59, 0, tzinfo=datetime.timezone.utc)
    ev_day1 = uuid.uuid4()

    with tenant_atomic(tenant.id):
        profile, badges = GamificationEngine.handle_learning_event(
            tenant_id=tenant.id,
            student_id=student_id,
            event_type="lesson_completed",
            event_id=ev_day1,
            occurred_at=dt_day1,
        )
        assert profile.current_streak_days == 1
        assert profile.longest_streak_days == 1
        assert profile.completed_lessons_count == 1
        assert any(b.badge_code == "FIRST_LESSON" for b in badges)

    # Day 2: 2026-09-02 00:01:00 UTC (Crosses UTC Midnight boundary)
    dt_day2 = datetime.datetime(2026, 9, 2, 0, 1, 0, tzinfo=datetime.timezone.utc)
    ev_day2 = uuid.uuid4()

    with tenant_atomic(tenant.id):
        profile2, _ = GamificationEngine.handle_learning_event(
            tenant_id=tenant.id,
            student_id=student_id,
            event_type="lesson_completed",
            event_id=ev_day2,
            occurred_at=dt_day2,
        )
        assert profile2.current_streak_days == 2
        assert profile2.longest_streak_days == 2
        assert profile2.completed_lessons_count == 2

    # Same Day event: 2026-09-02 14:00:00 UTC (Deduplication per day)
    dt_day2_later = datetime.datetime(2026, 9, 2, 14, 0, 0, tzinfo=datetime.timezone.utc)
    ev_day2_later = uuid.uuid4()

    with tenant_atomic(tenant.id):
        profile2_dedup, _ = GamificationEngine.handle_learning_event(
            tenant_id=tenant.id,
            student_id=student_id,
            event_type="submission_reviewed",
            event_id=ev_day2_later,
            occurred_at=dt_day2_later,
        )
        # Streak must not increase on the same day!
        assert profile2_dedup.current_streak_days == 2
        assert profile2_dedup.reviewed_submissions_count == 1

    # Day 3: 2026-09-03 10:00:00 UTC (Day 3 consecutive -> STREAK_3_DAYS award)
    dt_day3 = datetime.datetime(2026, 9, 3, 10, 0, 0, tzinfo=datetime.timezone.utc)
    ev_day3 = uuid.uuid4()

    with tenant_atomic(tenant.id):
        profile3, badges3 = GamificationEngine.handle_learning_event(
            tenant_id=tenant.id,
            student_id=student_id,
            event_type="lesson_completed",
            event_id=ev_day3,
            occurred_at=dt_day3,
        )
        assert profile3.current_streak_days == 3
        assert profile3.longest_streak_days == 3
        assert any(b.badge_code == "STREAK_3_DAYS" for b in badges3)


@pytest.mark.django_db(transaction=True)
def test_gamification_idempotency_and_zero_duplicate_awards():
    tenant = Tenant.objects.create(name="T2", slug=f"t2-{uuid.uuid4().hex[:6]}")
    student_id = uuid.uuid4()
    fixed_event_id = uuid.uuid4()
    fixed_dt = datetime.datetime(2026, 9, 5, 12, 0, 0, tzinfo=datetime.timezone.utc)

    with tenant_atomic(tenant.id):
        # 1. Initial event trigger
        GamificationEngine.handle_learning_event(
            tenant_id=tenant.id,
            student_id=student_id,
            event_type="lesson_completed",
            event_id=fixed_event_id,
            occurred_at=fixed_dt,
        )

        # 2. Replay 3 times (Mandatory Commander check)
        for _ in range(3):
            GamificationEngine.handle_learning_event(
                tenant_id=tenant.id,
                student_id=student_id,
                event_type="lesson_completed",
                event_id=fixed_event_id,
                occurred_at=fixed_dt,
            )

        # Assert total FIRST_LESSON badge awards for this student == 1
        award_count = StudentBadgeAward.objects.filter(
            tenant=tenant,
            student_id=student_id,
            badge_code="FIRST_LESSON",
        ).count()
        assert award_count == 1

        # Profile count for student == 1
        assert StudentProgressionProfile.objects.filter(tenant=tenant, student_id=student_id).count() == 1
