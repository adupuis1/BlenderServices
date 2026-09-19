import uuid

import pytest
from fastapi.testclient import TestClient

from common.deps import current_caller
from app.main import app
from app.models import Project, ProjectStatus
from common import storage
from common.auth import Caller
from common.db import get_session

OWNER = Caller(id=uuid.uuid4(), username="owner", is_superuser=False)
STRANGER = Caller(id=uuid.uuid4(), username="stranger", is_superuser=False)


@pytest.fixture
def uploaded(monkeypatch):
    """Whether storage.exists() reports the file as uploaded."""
    state = {"yes": True}
    monkeypatch.setattr(storage, "exists", lambda key: state["yes"])
    monkeypatch.setattr(storage, "upload_url",
                        lambda key, expires=900: f"http://minio.test/{key}")
    return state


@pytest.fixture
def as_user():
    who = {"caller": OWNER}
    app.dependency_overrides[current_caller] = lambda: who["caller"]
    yield who
    app.dependency_overrides.pop(current_caller, None)


@pytest.fixture
def client(session, uploaded, as_user):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.pop(get_session, None)


def create(client, name="cube"):
    r = client.post("/api/v1/projects", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


def test_create_returns_pending_project_and_upload_url(client):
    body = create(client)
    assert body["project"]["status"] == "pending_upload"
    assert body["upload_url"].startswith("http://minio.test/projects/")


def test_empty_name_is_rejected(client):
    assert client.post("/api/v1/projects", json={"name": ""}).status_code == 422


def test_list_shows_only_your_projects(client, as_user):
    create(client, "mine")
    as_user["caller"] = STRANGER
    assert client.get("/api/v1/projects").json() == []


def test_someone_elses_project_is_404_not_403(client, as_user):
    pid = create(client)["project"]["id"]
    as_user["caller"] = STRANGER
    for method, path in [("get", ""), ("patch", ""), ("delete", ""), ("post", "/complete")]:
        kwargs = {"json": {"name": "x"}} if method == "patch" else {}
        r = getattr(client, method)(f"/api/v1/projects/{pid}{path}", **kwargs)
        assert r.status_code == 404, (method, path, r.status_code)


def test_patch_renames_and_ignores_status(client):
    pid = create(client)["project"]["id"]
    r = client.patch(f"/api/v1/projects/{pid}", json={"name": "renamed", "status": "ready"})
    assert r.status_code == 200
    assert r.json()["name"] == "renamed"
    assert r.json()["status"] == "pending_upload"


def test_complete_checks_the_upload_then_moves_to_scanning(client, uploaded):
    pid = create(client)["project"]["id"]
    uploaded["yes"] = False
    assert client.post(f"/api/v1/projects/{pid}/complete").status_code == 400
    uploaded["yes"] = True
    r = client.post(f"/api/v1/projects/{pid}/complete")
    assert r.status_code == 200 and r.json()["status"] == "scanning"
    assert client.post(f"/api/v1/projects/{pid}/complete").status_code == 409


def test_delete_is_refused_while_scanning(client, session):
    pid = create(client)["project"]["id"]
    project = session.get(Project, uuid.UUID(pid))
    project.status = ProjectStatus.SCANNING
    session.add(project)
    session.commit()
    assert client.delete(f"/api/v1/projects/{pid}").status_code == 409


def test_delete_removes_the_project(client):
    pid = create(client)["project"]["id"]
    assert client.delete(f"/api/v1/projects/{pid}").status_code == 204
    assert client.get(f"/api/v1/projects/{pid}").status_code == 404


def test_no_token_is_401(session, uploaded):
    app.dependency_overrides[get_session] = lambda: session
    try:
        assert TestClient(app).get("/api/v1/projects").status_code == 401
    finally:
        app.dependency_overrides.pop(get_session, None)