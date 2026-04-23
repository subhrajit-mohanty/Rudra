"""Smoke tests that exercise the unauthenticated surface of the API."""


def test_health_returns_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_plans_are_public(client):
    r = client.get("/api/plans")
    assert r.status_code == 200
    plans = r.json()
    for tier in ["free", "pro", "business", "enterprise"]:
        assert tier in plans, f"{tier} plan missing from /api/plans"


def test_protected_endpoint_requires_auth(client):
    r = client.get("/api/dashboard")
    # HTTPBearer returns 403 when the Authorization header is absent, which
    # is a FastAPI default. Either 401 or 403 is an acceptable refusal.
    assert r.status_code in (401, 403)
