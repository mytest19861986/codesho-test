from uuid import uuid4

import pytest
from django.db import IntegrityError, connection, transaction
from psycopg.errors import ForeignKeyViolation, InsufficientPrivilege, RaiseException

from modules.learning.models import Course, Lesson
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant

pytest_plugins = ("tests.test_passcode_change_challenge_postgres",)


def require_postgres() -> None:
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific learning RLS contract")


def course_factory(tenant: Tenant, code: str) -> Course:
    with tenant_atomic(tenant.id):
        return Course.objects.create(tenant=tenant, code=code, title=code.title())


def lesson_factory(tenant: Tenant, course: Course, code: str, position: int) -> Lesson:
    with tenant_atomic(tenant.id):
        return Lesson.objects.create(
            tenant=tenant,
            course=course,
            code=code,
            title=code.title(),
            position=position,
        )


@pytest.mark.django_db(transaction=True)
def test_learning_rls_fails_closed_without_tenant_context(runtime_connection):
    first = Tenant.objects.create(slug=f"learn-{uuid4()}", name="First")
    course_factory(first, "python")
    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM learning_course")
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT count(*) FROM learning_lesson")
        assert cursor.fetchone()[0] == 0


@pytest.mark.django_db(transaction=True)
def test_learning_rls_isolates_tenants_and_connection_reuse(runtime_connection):
    first = Tenant.objects.create(slug=f"learn-{uuid4()}", name="First")
    second = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Second")
    first_course = course_factory(first, "first")
    second_course = course_factory(second, "second")
    lesson_factory(first, first_course, "intro", 1)
    lesson_factory(second, second_course, "intro", 1)

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        cursor.execute("SELECT code FROM learning_course ORDER BY code")
        assert cursor.fetchall() == [("first",)]
        cursor.execute("SELECT code FROM learning_lesson ORDER BY code")
        assert cursor.fetchall() == [("intro",)]
    runtime_connection.rollback()

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM learning_course")
        assert cursor.fetchone()[0] == 0


@pytest.mark.django_db(transaction=True)
def test_runtime_cannot_insert_or_reassign_cross_tenant_rows(runtime_connection):
    first = Tenant.objects.create(slug=f"learn-{uuid4()}", name="First")
    second = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Second")
    first_course = course_factory(first, "first")
    second_course = course_factory(second, "second")

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises(InsufficientPrivilege):
            cursor.execute(
                "INSERT INTO learning_course (id, tenant_id, code, title, state, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, 'draft', now(), now())",
                [uuid4(), second.id, "forbidden", "Forbidden"],
            )
    runtime_connection.rollback()

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises((ForeignKeyViolation, IntegrityError)):
            cursor.execute(
                "INSERT INTO learning_lesson "
                "(id, tenant_id, course_id, code, title, position, state, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, 1, 'draft', now(), now())",
                [uuid4(), first.id, second_course.id, "cross", "Cross"],
            )
    runtime_connection.rollback()

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises(InsufficientPrivilege):
            cursor.execute(
                "UPDATE learning_course SET tenant_id = %s WHERE id = %s",
                [second.id, first_course.id],
            )
    runtime_connection.rollback()


@pytest.mark.django_db(transaction=True)
def test_database_guards_immutable_learning_keys():
    require_postgres()
    tenant = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Tenant")
    course = course_factory(tenant, "python")
    lesson = lesson_factory(tenant, course, "intro", 1)

    with tenant_atomic(tenant.id):
        with pytest.raises((RaiseException, IntegrityError)), transaction.atomic():
            Course.objects.filter(pk=course.pk).update(code="changed")
        with pytest.raises((RaiseException, IntegrityError)), transaction.atomic():
            Lesson.objects.filter(pk=lesson.pk).update(position=2)


@pytest.mark.django_db(transaction=True)
def test_force_rls_is_enabled_for_learning_tables():
    require_postgres()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT relname, relrowsecurity, relforcerowsecurity "
            "FROM pg_class WHERE relname IN ('learning_course', 'learning_lesson') "
            "ORDER BY relname"
        )
        assert cursor.fetchall() == [
            ("learning_course", True, True),
            ("learning_lesson", True, True),
        ]
