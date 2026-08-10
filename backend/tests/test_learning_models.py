from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from modules.learning.models import Course, Lesson, PublicationState
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db
def test_learning_field_bounds_and_states_are_pinned():
    assert Course._meta.get_field("code").max_length == 64
    assert Course._meta.get_field("title").max_length == 160
    assert Lesson._meta.get_field("code").max_length == 64
    assert Lesson._meta.get_field("title").max_length == 160
    assert set(PublicationState.values) == {"draft", "published", "archived"}


@pytest.mark.django_db
def test_course_code_is_unique_per_tenant():
    tenant = Tenant.objects.create(slug="learning-a", name="Learning A")
    with tenant_atomic(tenant.id):
        Course.objects.create(tenant=tenant, code="python", title="Python")
        with pytest.raises(IntegrityError), transaction.atomic():
            Course.objects.create(tenant=tenant, code="python", title="Duplicate")


@pytest.mark.django_db
def test_lesson_code_and_position_are_unique_per_course():
    tenant = Tenant.objects.create(slug="learning-b", name="Learning B")
    with tenant_atomic(tenant.id):
        course = Course.objects.create(tenant=tenant, code="web", title="Web")
        Lesson.objects.create(
            tenant=tenant,
            course=course,
            code="intro",
            title="Intro",
            position=1,
        )
        with pytest.raises(IntegrityError), transaction.atomic():
            Lesson.objects.create(
                tenant=tenant,
                course=course,
                code="intro",
                title="Duplicate",
                position=2,
            )
        with pytest.raises(IntegrityError), transaction.atomic():
            Lesson.objects.create(
                tenant=tenant,
                course=course,
                code="other",
                title="Other",
                position=1,
            )


@pytest.mark.django_db
def test_lesson_position_must_be_positive():
    tenant = Tenant.objects.create(slug="learning-c", name="Learning C")
    with tenant_atomic(tenant.id):
        course = Course.objects.create(tenant=tenant, code="css", title="CSS")
        with pytest.raises(IntegrityError), transaction.atomic():
            Lesson.objects.create(
                tenant=tenant,
                course=course,
                code="zero",
                title="Zero",
                position=0,
            )


@pytest.mark.django_db
def test_stable_codes_and_lesson_position_are_guarded_from_model_mutation():
    tenant = Tenant.objects.create(slug="learning-d", name="Learning D")
    with tenant_atomic(tenant.id):
        course = Course.objects.create(tenant=tenant, code="js", title="JavaScript")
        lesson = Lesson.objects.create(
            tenant=tenant,
            course=course,
            code="dom",
            title="DOM",
            position=1,
        )

        course.code = "changed"
        with pytest.raises(ValidationError):
            course.save()

        lesson.code = "changed"
        with pytest.raises(ValidationError):
            lesson.save()

        lesson.refresh_from_db()
        lesson.position = 2
        with pytest.raises(ValidationError):
            lesson.save()


@pytest.mark.django_db
def test_primary_keys_are_guarded_from_model_mutation():
    tenant = Tenant.objects.create(slug="learning-id", name="Learning ID")
    with tenant_atomic(tenant.id):
        course = Course.objects.create(tenant=tenant, code="ids", title="IDs")
        lesson = Lesson.objects.create(
            tenant=tenant,
            course=course,
            code="stable-id",
            title="Stable ID",
            position=1,
        )
        original_course_id = course.id
        original_lesson_id = lesson.id

        course.id = uuid4()
        with pytest.raises(ValidationError):
            course.save()
        assert Course.objects.filter(pk=original_course_id).exists()

        lesson.id = uuid4()
        with pytest.raises(ValidationError):
            lesson.save()
        assert Lesson.objects.filter(pk=original_lesson_id).exists()


def test_learning_app_does_not_define_learner_or_progress_models():
    from modules import learning
    from modules.learning import models as learning_models

    assert learning is not None
    assert not hasattr(learning_models, "ClassCohort")
    assert not hasattr(learning_models, "ClassMembership")
    assert not hasattr(learning_models, "LessonProgress")
