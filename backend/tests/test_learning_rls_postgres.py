from uuid import uuid4

import pytest
from django.db import IntegrityError, ProgrammingError, connection, transaction
from psycopg.errors import ForeignKeyViolation, InsufficientPrivilege

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
    course = course_factory(first, "python")
    lesson_factory(first, course, "intro", 1)
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
        cursor.execute("SELECT course_id FROM learning_lesson")
        assert cursor.fetchall() == [(first_course.id,)]
    runtime_connection.rollback()

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM learning_course")
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT count(*) FROM learning_lesson")
        assert cursor.fetchone()[0] == 0


@pytest.mark.django_db(transaction=True)
def test_runtime_cannot_insert_cross_tenant_course_or_lesson(runtime_connection):
    first = Tenant.objects.create(slug=f"learn-{uuid4()}", name="First")
    second = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Second")
    first_course = course_factory(first, "first")

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises(InsufficientPrivilege):
            cursor.execute(
                "INSERT INTO learning_course "
                "(id, tenant_id, code, title, state, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, 'draft', now(), now())",
                [uuid4(), second.id, "forbidden", "Forbidden"],
            )
    runtime_connection.rollback()

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises(InsufficientPrivilege):
            cursor.execute(
                "INSERT INTO learning_lesson "
                "(id, tenant_id, course_id, code, title, position, state, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, 2, 'draft', now(), now())",
                [uuid4(), second.id, first_course.id, "forbidden", "Forbidden"],
            )
    runtime_connection.rollback()


@pytest.mark.django_db(transaction=True)
def test_database_rejects_cross_tenant_lesson_course_reference(runtime_connection):
    first = Tenant.objects.create(slug=f"learn-{uuid4()}", name="First")
    second = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Second")
    second_course = course_factory(second, "second")

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


@pytest.mark.django_db(transaction=True)
def test_runtime_cannot_reassign_learning_tenant_ownership(runtime_connection):
    first = Tenant.objects.create(slug=f"learn-{uuid4()}", name="First")
    second = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Second")
    first_course = course_factory(first, "first")
    first_lesson = lesson_factory(first, first_course, "intro", 1)

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises(InsufficientPrivilege):
            cursor.execute(
                "UPDATE learning_course SET tenant_id = %s WHERE id = %s",
                [second.id, first_course.id],
            )
    runtime_connection.rollback()

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.id)])
        with pytest.raises(InsufficientPrivilege):
            cursor.execute(
                "UPDATE learning_lesson SET tenant_id = %s WHERE id = %s",
                [second.id, first_lesson.id],
            )
    runtime_connection.rollback()


@pytest.mark.django_db(transaction=True)
def test_database_guards_immutable_learning_keys():
    require_postgres()
    tenant = Tenant.objects.create(slug=f"learn-{uuid4()}", name="Tenant")
    course = course_factory(tenant, "python")
    lesson = lesson_factory(tenant, course, "intro", 1)

    with tenant_atomic(tenant.id):
        with pytest.raises(ProgrammingError), transaction.atomic():
            Course.objects.filter(pk=course.pk).update(code="changed")
        with pytest.raises(ProgrammingError), transaction.atomic():
            Lesson.objects.filter(pk=lesson.pk).update(code="changed")
        with pytest.raises(ProgrammingError), transaction.atomic():
            Lesson.objects.filter(pk=lesson.pk).update(position=2)


@pytest.mark.django_db(transaction=True)
def test_force_rls_and_runtime_role_contract_for_learning_tables(runtime_connection):
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
        cursor.execute(
            "SELECT tableowner FROM pg_tables WHERE schemaname = current_schema() "
            "AND tablename IN ('learning_course', 'learning_lesson') ORDER BY tablename"
        )
        assert cursor.fetchall() == [("codesho_migrator",), ("codesho_migrator",)]

    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = current_user")
        assert cursor.fetchone()[0] is False
        for table in ("learning_course", "learning_lesson"):
            cursor.execute("SELECT has_table_privilege(current_user, %s, 'TRUNCATE')", [table])
            assert cursor.fetchone()[0] is False
            with pytest.raises(InsufficientPrivilege):
                cursor.execute(f"TRUNCATE TABLE {table}")
            runtime_connection.rollback()
