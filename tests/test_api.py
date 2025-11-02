from fastapi.testclient import TestClient

from app.logger_utils import mask_pii
from app.main import app

client = TestClient(app)


def test_validation_problem_details_on_large_limit():
    r = client.get("/notes?limit=10000")
    assert r.status_code == 422
    assert r.headers.get("content-type").startswith("application/problem+json")
    body = r.json()
    # required fields
    for f in ["type", "title", "status", "detail", "instance", "correlation_id"]:
        assert f in body


def test_create_and_list_notes_with_pagination_and_no_body_leak():
    # create
    r = client.post(
        "/notes", json={"title": "Hello", "body": "Secret text", "tags": ["t1", "t2"]}
    )
    assert r.status_code == 200
    rid = r.headers.get("x-request-id")
    assert rid is not None

    # list
    r2 = client.get("/notes?limit=10&offset=0")
    assert r2.status_code == 200
    data = r2.json()
    assert "items" in data and isinstance(data["items"], list)
    # ensure body is NOT present in list items
    assert "body" not in data["items"][0]
    assert r2.headers.get("x-request-id")


def test_mask_pii():
    obj = {"password": "qwerty", "token": "abcd", "body": "PRIVATE", "ok": True}
    masked = mask_pii(obj)
    assert (
        masked["password"] == "***"
        and masked["token"] == "***"
        and masked["body"] == "***"
    )
    assert masked["ok"] is True
