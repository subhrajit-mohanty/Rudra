import logging

import httpx
from config import KEYCLOAK_ADMIN_PASSWORD, KEYCLOAK_ADMIN_USER, KEYCLOAK_URL

logger = logging.getLogger(__name__)

class KeycloakAdmin:
    def __init__(self):
        self.base_url = KEYCLOAK_URL

    async def _get_token(self):
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/realms/master/protocol/openid-connect/token",
                data={"grant_type": "password", "client_id": "admin-cli",
                      "username": KEYCLOAK_ADMIN_USER, "password": KEYCLOAK_ADMIN_PASSWORD})
            r.raise_for_status()
            return r.json()["access_token"]

    async def _h(self):
        return {"Authorization": f"Bearer {await self._get_token()}", "Content-Type": "application/json"}

    # ── Realms ──
    async def create_realm(self, name, display, plan):
        h = await self._h()
        cfg = {"realm": name, "enabled": True, "displayName": display,
               "sslRequired": "none", "registrationAllowed": True,
               "loginWithEmailAllowed": True, "resetPasswordAllowed": True,
               "bruteForceProtected": True, "permanentLockout": False,
               "maxFailureWaitSeconds": 900, "failureFactor": 5,
               "eventsEnabled": True, "eventsExpiration": 2592000,
               "adminEventsEnabled": True, "adminEventsDetailsEnabled": True,
               "attributes": {"plan": plan}}
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms", json=cfg, headers=h)
            if r.status_code == 409: raise ValueError(f"Realm '{name}' already exists")
            r.raise_for_status()
            return {"realm": name, "status": "created"}

    async def get_realm(self, name):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{name}", headers=await self._h())
            r.raise_for_status()
            return r.json()

    async def delete_realm(self, name):
        async with httpx.AsyncClient() as c:
            r = await c.delete(f"{self.base_url}/admin/realms/{name}", headers=await self._h())
            r.raise_for_status()

    async def update_realm(self, name, updates):
        async with httpx.AsyncClient() as c:
            r = await c.put(f"{self.base_url}/admin/realms/{name}", json=updates, headers=await self._h())
            r.raise_for_status()

    # ── Clients ──
    async def create_client(self, realm, client_id, redirect_uris, protocol="openid-connect"):
        cfg = {"clientId": client_id, "enabled": True, "protocol": protocol,
               "publicClient": True, "redirectUris": redirect_uris, "webOrigins": ["*"],
               "standardFlowEnabled": True, "directAccessGrantsEnabled": True}
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms/{realm}/clients", json=cfg, headers=await self._h())
            r.raise_for_status()
            loc = r.headers.get("Location", "")
            return {"client_id": client_id, "kc_id": loc.split("/")[-1] if loc else None}

    async def list_clients(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/clients", headers=await self._h())
            r.raise_for_status()
            skip = {"account","realm-management","admin-cli","broker","security-admin-console","account-console"}
            return [x for x in r.json() if x.get("clientId") not in skip]

    async def delete_client(self, realm, kc_id):
        async with httpx.AsyncClient() as c:
            await c.delete(f"{self.base_url}/admin/realms/{realm}/clients/{kc_id}", headers=await self._h())

    # ── Users ──
    async def create_user(self, realm, username, email, password, first_name="", last_name="", attributes=None):
        cfg = {"username": username, "email": email, "firstName": first_name, "lastName": last_name,
               "enabled": True, "emailVerified": True, "attributes": attributes or {},
               "credentials": [{"type": "password", "value": password, "temporary": False}]}
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms/{realm}/users", json=cfg, headers=await self._h())
            if r.status_code == 409: raise ValueError(f"User '{username}' already exists")
            r.raise_for_status()
            loc = r.headers.get("Location", "")
            return {"username": username, "user_id": loc.split("/")[-1] if loc else None}

    async def list_users(self, realm, first=0, max_results=100, search=None):
        params = {"first": first, "max": max_results}
        if search: params["search"] = search
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/users", params=params, headers=await self._h())
            r.raise_for_status()
            return r.json()

    async def get_user(self, realm, user_id):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/users/{user_id}", headers=await self._h())
            r.raise_for_status()
            return r.json()

    async def update_user(self, realm, user_id, updates):
        async with httpx.AsyncClient() as c:
            r = await c.put(f"{self.base_url}/admin/realms/{realm}/users/{user_id}", json=updates, headers=await self._h())
            r.raise_for_status()

    async def count_users(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/users/count", headers=await self._h())
            r.raise_for_status()
            return r.json()

    async def delete_user(self, realm, user_id):
        async with httpx.AsyncClient() as c:
            await c.delete(f"{self.base_url}/admin/realms/{realm}/users/{user_id}", headers=await self._h())

    # ── User Sessions (Clerk: session management) ──
    async def get_user_sessions(self, realm, user_id):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/sessions", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    async def revoke_user_sessions(self, realm, user_id):
        async with httpx.AsyncClient() as c:
            await c.post(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/logout", headers=await self._h())

    async def delete_session(self, realm, session_id):
        async with httpx.AsyncClient() as c:
            await c.delete(f"{self.base_url}/admin/realms/{realm}/sessions/{session_id}", headers=await self._h())

    # ── User Impersonation (Clerk Pro feature) ──
    async def impersonate_user(self, realm, user_id):
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/impersonation", json={}, headers=await self._h())
            return r.json() if r.status_code == 200 else {"error": "Impersonation failed"}

    # ── User Role Mapping ──
    async def get_user_roles(self, realm, user_id):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    async def assign_role(self, realm, user_id, role_id, role_name):
        async with httpx.AsyncClient() as c:
            await c.post(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm",
                json=[{"id": role_id, "name": role_name}], headers=await self._h())

    async def remove_role(self, realm, user_id, role_id, role_name):
        async with httpx.AsyncClient() as c:
            await c.request("DELETE", f"{self.base_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm",
                json=[{"id": role_id, "name": role_name}], headers=await self._h())

    # ── Groups (for Organizations) ──
    async def create_group(self, realm, name, attributes=None):
        cfg = {"name": name, "attributes": attributes or {}}
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms/{realm}/groups", json=cfg, headers=await self._h())
            r.raise_for_status()
            loc = r.headers.get("Location", "")
            return {"name": name, "id": loc.split("/")[-1] if loc else None}

    async def list_groups(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/groups", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    async def add_user_to_group(self, realm, user_id, group_id):
        async with httpx.AsyncClient() as c:
            await c.put(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/groups/{group_id}", headers=await self._h())

    async def remove_user_from_group(self, realm, user_id, group_id):
        async with httpx.AsyncClient() as c:
            await c.delete(f"{self.base_url}/admin/realms/{realm}/users/{user_id}/groups/{group_id}", headers=await self._h())

    async def get_group_members(self, realm, group_id):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/groups/{group_id}/members", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    # ── Roles ──
    async def create_role(self, realm, name, description=""):
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms/{realm}/roles",
                json={"name": name, "description": description}, headers=await self._h())
            r.raise_for_status()
            return {"role": name}

    async def list_roles(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/roles", headers=await self._h())
            r.raise_for_status()
            return r.json()

    async def get_role(self, realm, role_name):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/roles/{role_name}", headers=await self._h())
            return r.json() if r.status_code == 200 else None

    async def delete_role(self, realm, role_name):
        async with httpx.AsyncClient() as c:
            await c.delete(f"{self.base_url}/admin/realms/{realm}/roles/{role_name}", headers=await self._h())

    # ── Identity Providers ──
    async def create_idp(self, realm, alias, provider_id, config):
        cfg = {"alias": alias, "providerId": provider_id, "enabled": True,
               "storeToken": True, "trustEmail": True,
               "firstBrokerLoginFlowAlias": "first broker login", "config": config}
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base_url}/admin/realms/{realm}/identity-provider/instances",
                json=cfg, headers=await self._h())
            r.raise_for_status()
            return {"alias": alias}

    async def list_idps(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/identity-provider/instances", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    async def delete_idp(self, realm, alias):
        async with httpx.AsyncClient() as c:
            await c.delete(f"{self.base_url}/admin/realms/{realm}/identity-provider/instances/{alias}", headers=await self._h())

    # ── Events (Clerk: analytics) ──
    async def get_events(self, realm, event_type=None, max_results=100):
        params = {"max": max_results}
        if event_type: params["type"] = event_type
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/events", params=params, headers=await self._h())
            return r.json() if r.status_code == 200 else []

    async def get_admin_events(self, realm, max_results=50):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/admin-events",
                params={"max": max_results}, headers=await self._h())
            return r.json() if r.status_code == 200 else []

    # ── Session Stats ──
    async def get_client_session_stats(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/client-session-stats", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    # ── Authentication Flows (MFA config) ──
    async def get_auth_flows(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/authentication/flows", headers=await self._h())
            return r.json() if r.status_code == 200 else []

    async def get_required_actions(self, realm):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base_url}/admin/realms/{realm}/authentication/required-actions", headers=await self._h())
            return r.json() if r.status_code == 200 else []

kc = KeycloakAdmin()
