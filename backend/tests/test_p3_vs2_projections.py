from uuid import uuid4

import pytest

from modules.learning.events import LearningDomainEvents
from modules.learning.models import (
    Assignment,
    AssignmentState,
    AssignmentSubmissionMetrics,
    Course,
    CourseProgressAggregate,
    Lesson,
    Module,
    Progress,
    ProgressState,
    PublicationState,
    RoleActivityFeed,
    Submission,
    SubmissionState,
)
from modules.learning.projections import ProjectionApplier
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_course_progress_projection_and_dedup():
    tenant = Tenant.objects.create(name="Projections Tenant")
    course = Course.objects.create(
        tenant=tenant,
        code="CS101",
        title="Python Mastery",
        state=PublicationState.PUBLISHED,
    )
    module = Module.objects.create(
        tenant=tenant,
        course=course,
        code="MOD1",
        title="Intro",
        position=1,
    )
    lesson = Lesson.objects.create(
        tenant=tenant,
        course=course,
        module=module,
        code="LES1",
        title="Setup",
        position=1,
        state=PublicationState.PUBLISHED,
    )

    student_id = uuid4()
    progress = Progress.objects.create(
        tenant=tenant,
        student_id=student_id,
        lesson=lesson,
        state=ProgressState.COMPLETED,
    )

    event = LearningDomainEvents.lesson_completed(
        tenant_id=tenant.id,
        progress_id=progress.id,
        student_id=student_id,
        course_id=course.id,
        lesson_id=lesson.id,
    )

    # 1. First application
    applied = ProjectionApplier.apply_event(event)
    assert applied is True

    # Check CourseProgressAggregate
    agg = CourseProgressAggregate.objects.get(tenant=tenant, student_id=student_id, course=course)
    assert agg.total_lessons == 1
    assert agg.completed_lessons == 1
    assert agg.progress_percentage == 100
    assert agg.last_event_id == event.event_id

    # Check Student & Parent Activity Feed
    student_feed = RoleActivityFeed.objects.filter(
        tenant=tenant,
        target_role=RoleActivityFeed.ActivityRole.STUDENT,
        source_event_id=event.event_id,
    )
    assert student_feed.count() == 1

    parent_feed = RoleActivityFeed.objects.filter(
        tenant=tenant,
        target_role=RoleActivityFeed.ActivityRole.PARENT,
        source_event_id=event.event_id,
    )
    assert parent_feed.count() == 1

    # 2. Duplicate Application (Dedup Gate)
    duplicate_applied = ProjectionApplier.apply_event(event)
    assert duplicate_applied is False
    assert CourseProgressAggregate.objects.filter(tenant=tenant, student_id=student_id).count() == 1
    assert (
        RoleActivityFeed.objects.filter(tenant=tenant, source_event_id=event.event_id).count() == 2
    )


@pytest.mark.django_db(transaction=True)
def test_submission_metrics_and_mentor_feed():
    tenant = Tenant.objects.create(name="Mentor Metrics Tenant")
    course = Course.objects.create(tenant=tenant, code="C2", title="Course 2")
    module = Module.objects.create(
        tenant=tenant, course=course, code="M2", title="Mod 2", position=1
    )
    lesson = Lesson.objects.create(
        tenant=tenant, course=course, module=module, code="L2", title="Les 2", position=1
    )
    assignment = Assignment.objects.create(
        tenant=tenant,
        lesson=lesson,
        code="A1",
        title="Assignment 1",
        state=AssignmentState.PUBLISHED,
    )

    student_id = uuid4()
    submission = Submission.objects.create(
        tenant=tenant,
        assignment=assignment,
        student_id=student_id,
        content="My Solution",
        state=SubmissionState.SUBMITTED,
    )

    event = LearningDomainEvents.submission_received(
        tenant_id=tenant.id,
        submission_id=submission.id,
        student_id=student_id,
        assignment_id=assignment.id,
    )

    # First application
    applied = ProjectionApplier.apply_event(event)
    assert applied is True

    # Verify metrics aggregate
    metrics = AssignmentSubmissionMetrics.objects.get(tenant=tenant, assignment=assignment)
    assert metrics.submitted_count == 1
    assert metrics.under_review_count == 0
    assert metrics.reviewed_count == 0

    # Verify mentor activity feed
    mentor_feed = RoleActivityFeed.objects.filter(
        tenant=tenant,
        target_role=RoleActivityFeed.ActivityRole.MENTOR,
        source_event_id=event.event_id,
    )
    assert mentor_feed.count() == 1

    # Duplicate application check
    dup = ProjectionApplier.apply_event(event)
    assert dup is False
    assert (
        AssignmentSubmissionMetrics.objects.filter(tenant=tenant, assignment=assignment).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_gate_a_projection_integrity_and_dead_letter():
    tenant = Tenant.objects.create(name="Gate A Tenant", slug=f"gate-a-{uuid4().hex[:8]}")
    from modules.learning.events import DomainEvent
    from modules.learning.models import ProjectionDeadLetterEvent, ProjectionWatermark
    from django.utils import timezone
    import datetime

    now = timezone.now()
    event_id = uuid4()

    # 1. Unrecognized event type should go to Dead-Letter Queue
    unknown_event = DomainEvent(
        event_id=event_id,
        event_type="unknown.event.type",
        tenant_id=tenant.id,
        aggregate_id=uuid4(),
        payload={"foo": "bar", "user_id": str(uuid4())},
    )
    unknown_event.occurred_at = now

    applied = ProjectionApplier.apply_event(unknown_event)
    assert applied is False

    dlq = ProjectionDeadLetterEvent.objects.filter(tenant=tenant, event_id=event_id).first()
    assert dlq is not None
    assert dlq.event_type == "unknown.event.type"
    assert "Unknown event type" in dlq.reason

    # 2. Watermark advances on valid event
    course = Course.objects.create(tenant=tenant, code="C_GATE", title="Gate Course")
    module = Module.objects.create(tenant=tenant, course=course, code="M_GATE", title="M", position=1)
    lesson = Lesson.objects.create(tenant=tenant, course=course, module=module, code="L_GATE", title="L", position=1)
    student_id = uuid4()
    progress = Progress.objects.create(tenant=tenant, student_id=student_id, lesson=lesson, state=ProgressState.COMPLETED)

    valid_event = LearningDomainEvents.lesson_completed(
        tenant_id=tenant.id,
        progress_id=progress.id,
        student_id=student_id,
        course_id=course.id,
        lesson_id=lesson.id,
    )
    valid_event.occurred_at = now + datetime.timedelta(seconds=10)

    applied_valid = ProjectionApplier.apply_event(valid_event)
    assert applied_valid is True

    wm = ProjectionWatermark.objects.get(tenant=tenant, projection_name="learning_projections")
    assert wm.last_event_id == valid_event.event_id

    # 3. Older event arriving after watermark should be deduplicated
    older_event = LearningDomainEvents.lesson_completed(
        tenant_id=tenant.id,
        progress_id=progress.id,
        student_id=student_id,
        course_id=course.id,
        lesson_id=lesson.id,
    )
    older_event.occurred_at = now - datetime.timedelta(seconds=60)

    applied_older = ProjectionApplier.apply_event(older_event)
    assert applied_older is False


@pytest.mark.django_db(transaction=True)
def test_gate_b_cross_tenant_projection_isolation():
    tenant_a = Tenant.objects.create(name="Tenant A", slug=f"tenant-a-{uuid4().hex[:8]}")
    tenant_b = Tenant.objects.create(name="Tenant B", slug=f"tenant-b-{uuid4().hex[:8]}")

    course_a = Course.objects.create(tenant=tenant_a, code="CA", title="Course A")
    module_a = Module.objects.create(tenant=tenant_a, course=course_a, code="MA", title="Mod A", position=1)
    lesson_a = Lesson.objects.create(tenant=tenant_a, course=course_a, module=module_a, code="LA", title="Les A", position=1)
    student_a = uuid4()
    progress_a = Progress.objects.create(tenant=tenant_a, student_id=student_a, lesson=lesson_a, state=ProgressState.COMPLETED)

    event_a = LearningDomainEvents.lesson_completed(
        tenant_id=tenant_a.id,
        progress_id=progress_a.id,
        student_id=student_a,
        course_id=course_a.id,
        lesson_id=lesson_a.id,
    )

    ProjectionApplier.apply_event(event_a)

    # Verify projections exist for Tenant A
    assert CourseProgressAggregate.objects.filter(tenant=tenant_a).count() == 1
    assert RoleActivityFeed.objects.filter(tenant=tenant_a).count() == 2

    # Verify zero leak / 0 rows exposed to Tenant B
    assert CourseProgressAggregate.objects.filter(tenant=tenant_b).count() == 0
    assert RoleActivityFeed.objects.filter(tenant=tenant_b).count() == 0
