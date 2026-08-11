from __future__ import annotations

from uuid import uuid4

import pytest
from django.test import Client

from modules.identity.models import User
from modules.learning.models import Course, Lesson, PublicationState
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@pytest.fixture
def learner(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug="catalog-a", name="Catalog A")
    user = User.objects.create_user(username="catalog-learner", email="catalog@example.com")
    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant, user=user, role=TenantMembership.Role.LEARNER
        )
    client = Client()
    client.force_login(user)
    session = client.session
    session["session_auth_epoch"] = user.session_auth_epoch
    session.save()
    return tenant, client


def create_course(tenant: Tenant, code: str, state: str = PublicationState.PUBLISHED) -> Course:
    with tenant_atomic(tenant.id):
        return Course.objects.create(tenant=tenant, code=code, title=code.title(), state=state)


def create_lesson(
    tenant: Tenant,
    course: Course,
    code: str,
    position: int,
    state: str = PublicationState.PUBLISHED,
) -> Lesson:
    with tenant_atomic(tenant.id):
        return Lesson.objects.create(
            tenant=tenant,
            course=course,
            code=code,
            title=code.title(),
            position=position,
            state=state,
        )


@pytest.mark.django_db(transaction=True)
def test_courses_publish_minimize_and_order(learner):
    tenant, client = learner
    create_course(tenant, "zeta")
    create_course(tenant, "alpha")
    create_course(tenant, "draft", PublicationState.DRAFT)
    create_course(tenant, "archived", PublicationState.ARCHIVED)

    response = client.get("/api/v1/learning/courses/", HTTP_HOST="catalog-a.localhost")

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "id": str(Course.objects.get(code="alpha").id),
                "code": "alpha",
                "title": "Alpha",
                "state": "published",
            },
            {
                "id": str(Course.objects.get(code="zeta").id),
                "code": "zeta",
                "title": "Zeta",
                "state": "published",
            },
        ]
    }
    assert set(response.json()["results"][0]) == {"id", "code", "title", "state"}


@pytest.mark.django_db(transaction=True)
def test_lessons_publish_minimize_and_order(learner):
    tenant, client = learner
    course = create_course(tenant, "python")
    create_lesson(tenant, course, "later", 2)
    create_lesson(tenant, course, "first", 1)
    create_lesson(tenant, course, "draft", 3, PublicationState.DRAFT)
    create_lesson(tenant, course, "archived", 4, PublicationState.ARCHIVED)

    response = client.get(
        f"/api/v1/learning/courses/{course.id}/lessons/", HTTP_HOST="catalog-a.localhost"
    )

    assert response.status_code == 200
    assert [(row["code"], row["position"]) for row in response.json()["results"]] == [
        ("first", 1),
        ("later", 2),
    ]
    assert set(response.json()["results"][0]) == {"id", "code", "title", "position", "state"}


@pytest.mark.django_db(transaction=True)
def test_hidden_parent_and_unknown_parent_have_identical_not_found(learner):
    tenant, client = learner
    draft = create_course(tenant, "draft-parent", PublicationState.DRAFT)
    archived = create_course(tenant, "archived-parent", PublicationState.ARCHIVED)
    expected = {"code": "not_found"}
    responses = [
        client.get(
            f"/api/v1/learning/courses/{course.id}/lessons/", HTTP_HOST="catalog-a.localhost"
        )
        for course in (draft, archived)
    ]
    responses.append(
        client.get(f"/api/v1/learning/courses/{uuid4()}/lessons/", HTTP_HOST="catalog-a.localhost")
    )
    responses.append(
        client.get("/api/v1/learning/courses/not-a-uuid/lessons/", HTTP_HOST="catalog-a.localhost")
    )
    assert [(response.status_code, response.json()) for response in responses] == [
        (404, expected),
        (404, expected),
        (404, expected),
        (404, expected),
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "query",
    [
        "?page=0",
        "?page=-1",
        "?page=abc",
        "?page_size=0",
        "?page_size=-1",
        "?page_size=101",
        "?page_size=abc",
    ],
)
def test_invalid_pagination_is_compact_and_not_normalized(learner, query):
    _, client = learner
    response = client.get(f"/api/v1/learning/courses/{query}", HTTP_HOST="catalog-a.localhost")
    assert response.status_code == 400
    assert response.json() == {"code": "invalid_pagination"}


@pytest.mark.django_db(transaction=True)
def test_pagination_has_bounded_results_and_no_metadata(learner):
    tenant, client = learner
    for index in range(25):
        create_course(tenant, f"course-{index:02d}")
    first = client.get("/api/v1/learning/courses/", HTTP_HOST="catalog-a.localhost")
    page = client.get(
        "/api/v1/learning/courses/?page=2&page_size=20", HTTP_HOST="catalog-a.localhost"
    )
    empty = client.get(
        "/api/v1/learning/courses/?page=3&page_size=20", HTTP_HOST="catalog-a.localhost"
    )
    assert len(first.json()["results"]) == 20
    assert len(page.json()["results"]) == 5
    assert empty.json() == {"results": []}
    assert set(first.json()) == {"results"}


@pytest.mark.django_db(transaction=True)
def test_unauthenticated_and_inactive_membership_fail_closed(learner):
    tenant, _ = learner
    anonymous = Client()
    response = anonymous.get("/api/v1/learning/courses/", HTTP_HOST="catalog-a.localhost")
    assert response.status_code == 401
    User.objects.filter(username="catalog-learner").update(is_active=False)
    inactive = Client()
    inactive.force_login(User.objects.get(username="catalog-learner"))
    response = inactive.get("/api/v1/learning/courses/", HTTP_HOST="catalog-a.localhost")
    assert response.status_code in {401, 403}
    assert not Course.objects.filter(tenant=tenant).exists()
