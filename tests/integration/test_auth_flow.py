"""Register, login, and token based authentication flow."""


def test_register_returns_token(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "bob@example.com", "password": "pw", "name": "Bob"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "bob@example.com"
    assert body["name"] == "Bob"
    assert body["token"]


def test_register_rejects_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "pw", "name": "D"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 200

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 400


def test_login_succeeds_with_correct_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "password": "right-pw", "name": "Carol"},
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "right-pw"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == "carol@example.com"


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "dan@example.com", "password": "right-pw", "name": "Dan"},
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "dan@example.com", "password": "WRONG"},
    )
    assert r.status_code == 401


def test_login_rejects_unknown_email(client):
    r = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "anything"},
    )
    assert r.status_code == 401


def test_me_returns_current_admin(authed_client):
    client, _token, email = authed_client
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == email


def test_me_rejects_missing_bearer(client):
    r = client.get("/api/auth/me")
    assert r.status_code in (401, 403)
