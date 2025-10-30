import importlib
import os
import sys

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUME_SELECTOR_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("RESUME_SELECTOR_EMBEDDER", "stub")
    module_name = "backend.app"
    if module_name in sys.modules:
        del sys.modules[module_name]
    app_module = importlib.import_module(module_name)
    importlib.reload(app_module)
    app = app_module.app
    app.testing = True
    yield app.test_client()


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {"ok": True}


def test_create_job_flow(client):
    payload = {
        "title": "ML Engineer",
        "description": "Looking for Python, PyTorch, and Docker skills",
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "job_id" in data
    job_id = data["job_id"]
    assert isinstance(job_id, int)

    ranking_resp = client.get(f"/rankings?job_id={job_id}&k=5&epsilon=0.0")
    assert ranking_resp.status_code == 200
    ranking_data = ranking_resp.get_json()
    assert ranking_data["job_id"] == job_id
    assert "candidates" in ranking_data
    assert isinstance(ranking_data["weights"], list)
