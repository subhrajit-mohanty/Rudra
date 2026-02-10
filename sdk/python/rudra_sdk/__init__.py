"""
Rudra Python SDK
================

Connect your Python application to Rudra Auth Platform.

Usage:
    from rudra_sdk import RudraClient

    client = RudraClient("http://localhost:8000", email="admin@example.com", password="secret")

    # Create a user
    user = client.users.create("my-realm", username="jane", email="jane@co.com", password="pass123")

    # List organizations
    orgs = client.organizations.list("my-realm")
"""

from typing import Any, List, Optional

import requests


class RudraAPIError(Exception):
    """Raised when the Rudra API returns an error."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


class _BaseResource:
    def __init__(self, client: "RudraClient"):
        self._client = client

    def _request(self, method: str, path: str, **kwargs) -> Any:
        return self._client._request(method, path, **kwargs)


class AuthResource(_BaseResource):
    """Authentication operations."""

    def register(self, email: str, password: str, name: str, company: str = "") -> dict:
        """Register a new platform admin account."""
        return self._request("POST", "/auth/register", json={
            "email": email, "password": password, "name": name, "company": company
        })

    def login(self, email: str, password: str) -> dict:
        """Login and obtain a JWT token."""
        return self._request("POST", "/auth/login", json={
            "email": email, "password": password
        })

    def me(self) -> dict:
        """Get current admin profile."""
        return self._request("GET", "/auth/me")


class ProjectResource(_BaseResource):
    """Project (tenant/realm) management."""

    def create(self, name: str, realm_name: str, plan: str = "free", coupon_code: str = "") -> dict:
        """Create a new project with optional coupon."""
        payload = {"name": name, "realm_name": realm_name, "plan": plan}
        if coupon_code:
            payload["coupon_code"] = coupon_code
        return self._request("POST", "/tenants", json=payload)

    def list(self) -> List[dict]:
        """List all projects owned by current admin."""
        return self._request("GET", "/tenants")

    def get(self, realm: str) -> dict:
        """Get project details."""
        return self._request("GET", f"/tenants/{realm}")

    def update(self, realm: str, plan: str = None, display_name: str = None) -> dict:
        """Update project plan or name."""
        payload = {}
        if plan: payload["plan"] = plan
        if display_name: payload["display_name"] = display_name
        return self._request("PUT", f"/tenants/{realm}", json=payload)

    def delete(self, realm: str) -> dict:
        """Delete a project and its Keycloak realm."""
        return self._request("DELETE", f"/tenants/{realm}")

    def update_auth_settings(self, realm: str, **settings) -> dict:
        """Update authentication settings (mfa_enabled, bot_protection, etc.)."""
        return self._request("PUT", f"/tenants/{realm}/auth-settings", json=settings)

    def update_branding(self, realm: str, **branding) -> dict:
        """Update branding (primary_color, logo_url, etc.)."""
        return self._request("PUT", f"/tenants/{realm}/branding", json=branding)


class UserResource(_BaseResource):
    """User management within a project."""

    def create(self, realm: str, username: str, email: str, password: str,
               first_name: str = "", last_name: str = "", metadata: dict = None) -> dict:
        """Create a new user in the realm."""
        payload = {"username": username, "email": email, "password": password,
                   "first_name": first_name, "last_name": last_name}
        if metadata: payload["metadata"] = metadata
        return self._request("POST", f"/tenants/{realm}/users", json=payload)

    def list(self, realm: str, search: str = None, first: int = 0, max: int = 50) -> List[dict]:
        """List users with optional search."""
        params = {"first": first, "max": max}
        if search: params["search"] = search
        return self._request("GET", f"/tenants/{realm}/users", params=params)

    def get(self, realm: str, user_id: str) -> dict:
        """Get user detail with sessions and roles."""
        return self._request("GET", f"/tenants/{realm}/users/{user_id}")

    def update(self, realm: str, user_id: str, **updates) -> dict:
        """Update user fields (first_name, last_name, email, enabled, metadata)."""
        return self._request("PUT", f"/tenants/{realm}/users/{user_id}", json=updates)

    def delete(self, realm: str, user_id: str) -> dict:
        """Delete a user."""
        return self._request("DELETE", f"/tenants/{realm}/users/{user_id}")

    def impersonate(self, realm: str, user_id: str) -> dict:
        """Impersonate a user (Pro+ plan)."""
        return self._request("POST", f"/tenants/{realm}/users/{user_id}/impersonate")


class SessionResource(_BaseResource):
    """Session management."""

    def list(self, realm: str, user_id: str) -> List[dict]:
        """List active sessions for a user."""
        return self._request("GET", f"/tenants/{realm}/users/{user_id}/sessions")

    def revoke_all(self, realm: str, user_id: str) -> dict:
        """Revoke all sessions for a user."""
        return self._request("DELETE", f"/tenants/{realm}/users/{user_id}/sessions")

    def revoke(self, realm: str, session_id: str) -> dict:
        """Revoke a specific session."""
        return self._request("DELETE", f"/tenants/{realm}/sessions/{session_id}")


class OrganizationResource(_BaseResource):
    """B2B organization management (Pro+ plan)."""

    def create(self, realm: str, name: str, slug: str, allowed_email_domains: List[str] = None) -> dict:
        """Create an organization."""
        payload = {"name": name, "slug": slug}
        if allowed_email_domains: payload["allowed_email_domains"] = allowed_email_domains
        return self._request("POST", f"/tenants/{realm}/organizations", json=payload)

    def list(self, realm: str) -> List[dict]:
        """List all organizations in a realm."""
        return self._request("GET", f"/tenants/{realm}/organizations")

    def add_member(self, realm: str, slug: str, user_id: str, role: str = "member") -> dict:
        """Add a member to an organization."""
        return self._request("POST", f"/tenants/{realm}/organizations/{slug}/members",
                             json={"user_id": user_id, "role": role})

    def remove_member(self, realm: str, slug: str, user_id: str) -> dict:
        """Remove a member from an organization."""
        return self._request("DELETE", f"/tenants/{realm}/organizations/{slug}/members/{user_id}")

    def delete(self, realm: str, slug: str) -> dict:
        """Delete an organization."""
        return self._request("DELETE", f"/tenants/{realm}/organizations/{slug}")

    def invite(self, realm: str, email: str, org_slug: str = None, role: str = "member") -> dict:
        """Send an invitation."""
        return self._request("POST", f"/tenants/{realm}/invitations",
                             json={"email": email, "org_slug": org_slug, "role": role})

    def list_invitations(self, realm: str) -> List[dict]:
        """List pending invitations."""
        return self._request("GET", f"/tenants/{realm}/invitations")


class RoleResource(_BaseResource):
    """RBAC role management."""

    def create(self, realm: str, name: str, description: str = "") -> dict:
        """Create a custom role."""
        return self._request("POST", f"/tenants/{realm}/roles",
                             json={"name": name, "description": description})

    def list(self, realm: str) -> List[dict]:
        """List all roles in a realm."""
        return self._request("GET", f"/tenants/{realm}/roles")

    def assign(self, realm: str, user_id: str, role_name: str) -> dict:
        """Assign a role to a user."""
        return self._request("POST", f"/tenants/{realm}/users/{user_id}/roles/{role_name}")

    def remove(self, realm: str, user_id: str, role_name: str) -> dict:
        """Remove a role from a user."""
        return self._request("DELETE", f"/tenants/{realm}/users/{user_id}/roles/{role_name}")

    def delete(self, realm: str, role_name: str) -> dict:
        """Delete a role."""
        return self._request("DELETE", f"/tenants/{realm}/roles/{role_name}")


class SSOResource(_BaseResource):
    """SSO / Identity Provider management."""

    def add_oidc(self, realm: str, alias: str, client_id: str, client_secret: str,
                 provider_type: str = "google", authorization_url: str = "",
                 token_url: str = "") -> dict:
        """Add an OIDC identity provider (Google, GitHub, etc.)."""
        return self._request("POST", f"/tenants/{realm}/idp/oidc", json={
            "alias": alias, "provider_type": provider_type,
            "client_id": client_id, "client_secret": client_secret,
            "authorization_url": authorization_url, "token_url": token_url
        })

    def add_saml(self, realm: str, alias: str, entity_id: str, sso_url: str,
                 signing_certificate: str = "") -> dict:
        """Add a SAML identity provider (Business+ plan)."""
        return self._request("POST", f"/tenants/{realm}/idp/saml", json={
            "alias": alias, "entity_id": entity_id, "sso_url": sso_url,
            "signing_certificate": signing_certificate
        })

    def list(self, realm: str) -> List[dict]:
        """List identity providers."""
        return self._request("GET", f"/tenants/{realm}/idp")

    def delete(self, realm: str, alias: str) -> dict:
        """Delete an identity provider."""
        return self._request("DELETE", f"/tenants/{realm}/idp/{alias}")


class ClientResource(_BaseResource):
    """OIDC/SAML application (client) management."""

    def create(self, realm: str, client_id: str, redirect_uris: List[str] = None,
               protocol: str = "openid-connect") -> dict:
        """Register an OIDC/SAML client application."""
        return self._request("POST", f"/tenants/{realm}/clients", json={
            "client_id": client_id,
            "redirect_uris": redirect_uris or ["http://localhost:*"],
            "protocol": protocol
        })

    def list(self, realm: str) -> List[dict]:
        """List registered client applications."""
        return self._request("GET", f"/tenants/{realm}/clients")

    def delete(self, realm: str, kc_id: str) -> dict:
        """Delete a client application."""
        return self._request("DELETE", f"/tenants/{realm}/clients/{kc_id}")


class WebhookResource(_BaseResource):
    """Webhook management (Pro+ plan)."""

    def create(self, realm: str, url: str, events: List[str]) -> dict:
        """Create a webhook endpoint."""
        return self._request("POST", f"/tenants/{realm}/webhooks",
                             json={"url": url, "events": events})

    def list(self, realm: str) -> List[dict]:
        """List webhook endpoints."""
        return self._request("GET", f"/tenants/{realm}/webhooks")

    def logs(self, realm: str, webhook_id: str) -> List[dict]:
        """Get delivery logs for a webhook."""
        return self._request("GET", f"/tenants/{realm}/webhooks/{webhook_id}/logs")

    def delete(self, realm: str, webhook_id: str) -> dict:
        """Delete a webhook endpoint."""
        return self._request("DELETE", f"/tenants/{realm}/webhooks/{webhook_id}")


class CouponResource(_BaseResource):
    """Coupon/discount management."""

    def create(self, code: str, discount_pct: int, description: str = "",
               max_redemptions: int = -1, valid_plans: List[str] = None,
               duration_days: int = 0) -> dict:
        """Create a coupon."""
        return self._request("POST", "/coupons", json={
            "code": code, "discount_pct": discount_pct, "description": description,
            "max_redemptions": max_redemptions, "valid_plans": valid_plans or [],
            "duration_days": duration_days
        })

    def list(self) -> List[dict]:
        """List all coupons."""
        return self._request("GET", "/coupons")

    def validate(self, code: str, plan: str = "") -> dict:
        """Validate a coupon code."""
        return self._request("POST", "/coupons/validate", json={"code": code, "plan": plan})

    def redemptions(self, code: str) -> List[dict]:
        """Get redemption history for a coupon."""
        return self._request("GET", f"/coupons/{code}/redemptions")

    def toggle(self, code: str) -> dict:
        """Enable/disable a coupon."""
        return self._request("PUT", f"/coupons/{code}/toggle")

    def delete(self, code: str) -> dict:
        """Delete a coupon."""
        return self._request("DELETE", f"/coupons/{code}")


class AnalyticsResource(_BaseResource):
    """Analytics and event data (Pro+ plan)."""

    def summary(self, realm: str, days: int = 30) -> dict:
        """Get analytics summary: signups, logins, daily trends."""
        return self._request("GET", f"/tenants/{realm}/analytics", params={"days": days})

    def events(self, realm: str, event_type: str = None, max: int = 50) -> List[dict]:
        """Get raw Keycloak events."""
        params = {"max": max}
        if event_type: params["event_type"] = event_type
        return self._request("GET", f"/tenants/{realm}/events", params=params)

    def dashboard(self) -> dict:
        """Get platform-wide dashboard overview."""
        return self._request("GET", "/dashboard")


class RudraClient:
    """
    Rudra SDK Client.

    Args:
        base_url: Rudra API base URL (e.g. "http://localhost:8000")
        email: Admin email for authentication
        password: Admin password
        token: Pre-existing JWT token (skip login)

    Example:
        client = RudraClient("http://localhost:8000", email="admin@co.com", password="secret")
        projects = client.projects.list()
    """

    def __init__(self, base_url: str, email: str = None, password: str = None, token: str = None):
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._session = requests.Session()

        # Auto-login if credentials provided
        if email and password and not token:
            self.login(email, password)

        # Initialize resource managers
        self.auth = AuthResource(self)
        self.projects = ProjectResource(self)
        self.users = UserResource(self)
        self.sessions = SessionResource(self)
        self.organizations = OrganizationResource(self)
        self.roles = RoleResource(self)
        self.sso = SSOResource(self)
        self.clients = ClientResource(self)
        self.webhooks = WebhookResource(self)
        self.coupons = CouponResource(self)
        self.analytics = AnalyticsResource(self)

    def login(self, email: str, password: str) -> dict:
        """Authenticate and store the JWT token."""
        resp = self._request("POST", "/auth/login", json={
            "email": email, "password": password
        })
        self._token = resp.get("token")
        return resp

    @property
    def token(self) -> Optional[str]:
        return self._token

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}/api{path}"
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json"
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        resp = self._session.request(method, url, headers=headers, **kwargs)

        try:
            data = resp.json()
        except ValueError:
            if not resp.ok:
                raise RudraAPIError(resp.status_code, resp.text[:200])
            return resp.text

        if not resp.ok:
            detail = data.get("detail", str(data)) if isinstance(data, dict) else str(data)
            raise RudraAPIError(resp.status_code, detail)

        return data

    def health(self) -> dict:
        """Check API health."""
        return self._request("GET", "/health")

    def plans(self) -> dict:
        """Get available plans with features."""
        return self._request("GET", "/plans")
