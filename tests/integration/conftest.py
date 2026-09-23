"""Integration test fixtures.

Integration tests exercise the FastAPI app end to end against a real
MongoDB, with Keycloak calls mocked. Running a real Keycloak in CI
would add roughly two minutes of boot per job and the tests here do not
assert on Keycloak behaviour, only on our handlers and persistence.
"""
from __future__ import annotations

import os
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def _mongo_available():
    """Check once per session that MongoDB answers a ping.

    Locally the suite skips when MongoDB is not running so `pytest tests/`
    stays usable without services. In CI (`CI=true`, which GitHub Actions
    sets) an unreachable database is an infrastructure failure, so the
    suite fails instead of going green with every test skipped.
    """
    from config import MONGODB_URL
    from pymongo import MongoClient

    mongo = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    try:
        mongo.admin.command("ping")
    except Exception as e:
        reason = f"MongoDB not reachable at {MONGODB_URL}: {e}"
        if os.environ.get("CI", "").lower() in ("1", "true", "yes"):
            pytest.fail(reason, pytrace=False)
        pytest.skip(reason)
    finally:
        mongo.close()


@pytest.fixture(autouse=True)
def _clear_mongo(_mongo_available):
    """Drop the test database before and after each test to keep them isolated."""
    from config import MONGODB_DB, MONGODB_URL
    from pymongo import MongoClient

    mongo = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    mongo.drop_database(MONGODB_DB)
    try:
        yield
    finally:
        mongo.drop_database(MONGODB_DB)
        mongo.close()


@pytest.fixture(autouse=True)
def _mock_keycloak(monkeypatch):
    """Replace every Keycloak admin call with an async mock.

    Return values match the shapes real Keycloak would produce so the
    handlers under test do not break on unexpected Nones.
    """
    import keycloak_client

    kc = keycloak_client.kc

    monkeypatch.setattr(kc, "_get_token", AsyncMock(return_value="mock-admin-token"))
    monkeypatch.setattr(kc, "update_realm", AsyncMock())
    monkeypatch.setattr(
        kc,
        "create_realm",
        AsyncMock(return_value={"realm": "test-realm", "status": "created"}),
    )
    monkeypatch.setattr(kc, "delete_realm", AsyncMock())
    monkeypatch.setattr(kc, "get_realm", AsyncMock(return_value={"realm": "test-realm"}))
    monkeypatch.setattr(kc, "count_users", AsyncMock(return_value=0))
    monkeypatch.setattr(kc, "list_users", AsyncMock(return_value=[]))
    monkeypatch.setattr(kc, "list_clients", AsyncMock(return_value=[]))
    monkeypatch.setattr(kc, "list_idps", AsyncMock(return_value=[]))
    monkeypatch.setattr(kc, "list_roles", AsyncMock(return_value=[]))
    monkeypatch.setattr(kc, "get_events", AsyncMock(return_value=[]))


@pytest.fixture
def client():
    """A TestClient that runs the FastAPI lifespan (connects to Mongo)."""
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def authed_client(client):
    """Register a fresh admin and return (client, token, email)."""
    email = "alice@example.com"
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": "s3cret-pw", "name": "Alice"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, token, email
