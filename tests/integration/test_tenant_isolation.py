"""Regression tests for the tenant ownership enforcement we just added.

These tests spin up two admins, have one create a tenant, then verify
the other admin sees a 404 on every realm scoped endpoint. If any of
these start returning 200, the ownership check on that endpoint has
been lost.
"""


def _register(client, email):
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": "pw", "name": email.split("@")[0]},
    )
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_other_admin_cannot_read_tenant(client):
    alice_token = _register(client, "alice@example.com")
    bob_token = _register(client, "bob@example.com")

    create = client.post(
        "/api/tenants",
        json={"name": "Alice App", "realm_name": "alice-app", "plan": "free"},
        headers=_auth(alice_token),
    )
    assert create.status_code == 200

    hers = client.get("/api/tenants/alice-app", headers=_auth(alice_token))
    assert hers.status_code == 200

    his = client.get("/api/tenants/alice-app", headers=_auth(bob_token))
    assert his.status_code == 404, "Bob must not be able to read Alice's tenant"


def test_other_admin_cannot_delete_tenant(client):
    alice_token = _register(client, "alice@example.com")
    bob_token = _register(client, "bob@example.com")

    client.post(
        "/api/tenants",
        json={"name": "Alice App", "realm_name": "alice-app", "plan": "free"},
        headers=_auth(alice_token),
    )

    his_delete = client.delete("/api/tenants/alice-app", headers=_auth(bob_token))
    assert his_delete.status_code == 404

    # Alice's tenant should still be there.
    still_there = client.get("/api/tenants/alice-app", headers=_auth(alice_token))
    assert still_there.status_code == 200


def test_other_admin_cannot_revoke_session(client):
    alice_token = _register(client, "alice@example.com")
    bob_token = _register(client, "bob@example.com")

    client.post(
        "/api/tenants",
        json={"name": "Alice App", "realm_name": "alice-app", "plan": "free"},
        headers=_auth(alice_token),
    )

    r = client.delete(
        "/api/tenants/alice-app/sessions/some-session-id",
        headers=_auth(bob_token),
    )
    assert r.status_code == 404


def test_other_admin_cannot_create_invitation(client):
    alice_token = _register(client, "alice@example.com")
    bob_token = _register(client, "bob@example.com")

    client.post(
        "/api/tenants",
        json={"name": "Alice App", "realm_name": "alice-app", "plan": "free"},
        headers=_auth(alice_token),
    )

    r = client.post(
        "/api/tenants/alice-app/invitations",
        json={"email": "new@example.com", "role": "member"},
        headers=_auth(bob_token),
    )
    assert r.status_code == 404


def test_other_admin_cannot_assign_role(client):
    alice_token = _register(client, "alice@example.com")
    bob_token = _register(client, "bob@example.com")

    client.post(
        "/api/tenants",
        json={"name": "Alice App", "realm_name": "alice-app", "plan": "free"},
        headers=_auth(alice_token),
    )

    r = client.post(
        "/api/tenants/alice-app/users/some-user-id/roles/admin",
        headers=_auth(bob_token),
    )
    assert r.status_code == 404
