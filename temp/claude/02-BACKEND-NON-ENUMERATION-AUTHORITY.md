# Backend non-enumeration authority

Source excerpts are from the authoritative Task80B implementation evidence (`backend/modules/learning/views.py` and `backend/tests/test_learning_api.py`).

```python
try:
    parsed_course_id = UUID(course_id)
except (ValueError, AttributeError):
    return Response({"code": "not_found"}, status=404)
course = Course.objects.filter(
    id=parsed_course_id,
    tenant_id=_tenant_id(request),
    state=PublicationState.PUBLISHED,
).first()
if course is None:
    return Response({"code": "not_found"}, status=404)
```

```python
def test_hidden_parent_and_unknown_parent_have_identical_not_found(learner):
    ...
    responses = [client.get(... draft), client.get(... archived)]
    responses.append(client.get(... uuid4()))
    responses.append(client.get(".../not-a-uuid/lessons/"))
    assert [(r.status_code, r.json()) for r in responses] == [
        (404, {"code": "not_found"}),
        (404, {"code": "not_found"}),
        (404, {"code": "not_found"}),
        (404, {"code": "not_found"}),
    ]
```

```python
def test_tenant_authority_is_not_overridden_by_request_values(learner):
    ...
    response = client.get(".../courses/?tenant_id={other.id}")
    assert [item["id"] for item in response.json()["results"]] == [str(local_course.id)]
    cross_tenant = client.get(f".../courses/{other_course.id}/lessons/")
    assert (cross_tenant.status_code, cross_tenant.json()) == (404, {"code": "not_found"})
```

These tests cover malformed UUID, unknown UUID, draft, archived, and cross-tenant parents with indistinguishable not-found status/body. The backend does not disclose which condition occurred; the frontend must preserve that boundary.
