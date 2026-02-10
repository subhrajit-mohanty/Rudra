import json
import logging
import secrets
from contextlib import asynccontextmanager
from typing import List, Optional

import httpx
from auth import create_access_token, get_current_admin, hash_password, verify_password
from config import CORS_ORIGINS, DISPOSABLE_EMAIL_DOMAINS, KEYCLOAK_EXTERNAL_URL, PLANS
from database import db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from keycloak_client import kc
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await db.connect()
        # Disable SSL requirement on Keycloak master realm for local dev
        try:
            await kc.update_realm("master", {"sslRequired": "none"})
            logger.info("Keycloak master realm SSL requirement disabled")
        except Exception as e:
            logger.warning(f"Could not update master realm SSL: {e}")
        logger.info("Backend started successfully")
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        raise
    yield
    await db.disconnect()

app = FastAPI(title="Rudra API", description="Clerk-like Auth Platform powered by Keycloak", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ── Helpers ──
def _plan(tenant): return PLANS.get(tenant.get("plan", "free"), PLANS["free"])

async def _check_feature(realm, feature):
    t = await db.get_tenant(realm)
    if not t: raise HTTPException(404, "Tenant not found")
    pc = _plan(t)
    if not pc.get(feature): raise HTTPException(403, f"Feature '{feature}' requires plan upgrade")
    return t, pc

async def _fire_webhooks(realm_name, event_type, data):
    """Deliver webhooks like Clerk does"""
    webhooks = await db.list_webhooks(realm_name)
    for wh in webhooks:
        if not wh.get("enabled"): continue
        if event_type not in wh.get("events", []): continue
        payload = {"type": event_type, "data": data}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(wh["url"], json=payload, headers={"X-Webhook-Secret": wh.get("secret","")})
                await db.log_webhook_delivery(str(wh["_id"]), event_type, r.status_code, r.text[:500])
        except Exception as e:
            await db.log_webhook_delivery(str(wh["_id"]), event_type, 0, str(e)[:500])

# ═══ Models ═══
class RegisterM(BaseModel):
    email: str; password: str; name: str; company: str = ""
class LoginM(BaseModel):
    email: str; password: str
class TenantCreateM(BaseModel):
    name: str; realm_name: str; plan: str = "free"; coupon_code: str = ""
class TenantUpdateM(BaseModel):
    plan: Optional[str] = None; display_name: Optional[str] = None
class AuthSettingsM(BaseModel):
    password_auth: Optional[bool] = None; social_login: Optional[bool] = None
    magic_links: Optional[bool] = None; mfa_enabled: Optional[bool] = None
    mfa_methods: Optional[List[str]] = None
    disposable_email_blocking: Optional[bool] = None
    password_breach_detection: Optional[bool] = None
    bot_protection: Optional[bool] = None
class BrandingM(BaseModel):
    logo_url: Optional[str] = None; primary_color: Optional[str] = None; background_color: Optional[str] = None
class ClientCreateM(BaseModel):
    client_id: str; redirect_uris: List[str] = ["http://localhost:*"]; protocol: str = "openid-connect"
class UserCreateM(BaseModel):
    username: str; email: str; password: str; first_name: str = ""; last_name: str = ""
    metadata: Optional[dict] = None
class UserUpdateM(BaseModel):
    first_name: Optional[str] = None; last_name: Optional[str] = None
    email: Optional[str] = None; enabled: Optional[bool] = None
    metadata: Optional[dict] = None
class OrgCreateM(BaseModel):
    name: str; slug: str; allowed_email_domains: List[str] = []
class OrgMemberM(BaseModel):
    user_id: str; role: str = "member"
class InvitationCreateM(BaseModel):
    email: str; org_slug: Optional[str] = None; role: str = "member"
class IdpCreateM(BaseModel):
    alias: str; provider_type: str = "google"; client_id: str; client_secret: str
    authorization_url: str = ""; token_url: str = ""
class SamlIdpCreateM(BaseModel):
    alias: str; entity_id: str; sso_url: str; signing_certificate: str = ""
class RoleCreateM(BaseModel):
    name: str; description: str = ""
class WebhookCreateM(BaseModel):
    url: str; events: List[str]
class CouponCreateM(BaseModel):
    code: str; discount_pct: int = Field(ge=1, le=100); description: str = ""
    max_redemptions: int = -1; valid_plans: List[str] = []
    duration_days: int = 0
class CouponValidateM(BaseModel):
    code: str; plan: str = ""

# ═══ AUTH ═══
@app.post("/api/auth/register")
async def register(d: RegisterM):
    if await db.get_admin_by_email(d.email): raise HTTPException(400, "Email already registered")
    await db.create_admin(d.email, hash_password(d.password), d.name, d.company)
    token = create_access_token({"sub": d.email, "name": d.name})
    await db.log_activity(d.email, "register", "Account created")
    return {"token": token, "email": d.email, "name": d.name}

@app.post("/api/auth/login")
async def login(d: LoginM):
    a = await db.get_admin_by_email(d.email)
    if not a or not verify_password(d.password, a["password"]): raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": a["email"], "name": a["name"]})
    return {"token": token, "email": a["email"], "name": a["name"]}

@app.get("/api/auth/me")
async def get_me(admin=Depends(get_current_admin)):
    a = await db.get_admin_by_email(admin["email"])
    return {"email": a["email"], "name": a["name"], "company": a.get("company", "")}

# ═══ PLANS ═══
@app.get("/api/plans")
async def get_plans(): return PLANS

# ═══ TENANTS ═══
@app.post("/api/tenants")
async def create_tenant(d: TenantCreateM, admin=Depends(get_current_admin)):
    pc = PLANS.get(d.plan)
    if not pc: raise HTTPException(400, f"Invalid plan: {d.plan}")
    cnt = await db.count_tenants(admin["email"])
    if pc["max_realms"] != -1 and cnt >= pc["max_realms"]:
        raise HTTPException(403, f"Plan limit: max {pc['max_realms']} projects")
    # Coupon validation
    discount_pct = 0
    coupon_code = ""
    if d.coupon_code:
        coupon, err = await db.validate_coupon(d.coupon_code, d.plan)
        if err: raise HTTPException(400, f"Coupon error: {err}")
        discount_pct = coupon["discount_pct"]
        coupon_code = coupon["code"]
    try: await kc.create_realm(d.realm_name, d.name, d.plan)
    except ValueError as e: raise HTTPException(409, str(e))
    except Exception as e: raise HTTPException(500, f"Failed: {e}")
    await db.create_tenant(d.name, d.realm_name, d.plan, admin["email"], coupon_code, discount_pct)
    if coupon_code:
        await db.redeem_coupon(coupon_code, admin["email"], d.realm_name)
    await db.log_activity(admin["email"], "create_tenant",
        f"Created '{d.name}'" + (f" with coupon {coupon_code} ({discount_pct}% off)" if coupon_code else ""), d.realm_name)
    await db.track_event(d.realm_name, "project.created", {"plan": d.plan, "coupon": coupon_code})
    return {"status": "created", "realm_name": d.realm_name,
            "coupon_applied": coupon_code, "discount_pct": discount_pct}

@app.get("/api/tenants")
async def list_tenants(admin=Depends(get_current_admin)):
    tenants = await db.list_tenants(admin["email"])
    result = []
    for t in tenants:
        try:
            uc = await kc.count_users(t["realm_name"])
            cls = await kc.list_clients(t["realm_name"])
            idps = await kc.list_idps(t["realm_name"])
        except Exception: uc, cls, idps = 0, [], []
        oc = await db.count_orgs(t["realm_name"])
        result.append({"id": str(t["_id"]), "name": t["name"], "realm_name": t["realm_name"],
            "plan": t["plan"], "owner_email": t["owner_email"], "created_at": t.get("created_at"),
            "user_count": uc, "client_count": len(cls), "idp_count": len(idps), "org_count": oc,
            "auth_settings": t.get("auth_settings", {}), "branding": t.get("branding", {}),
            "applied_coupon": t.get("applied_coupon", ""), "discount_pct": t.get("discount_pct", 0)})
    return result

@app.get("/api/tenants/{realm}")
async def get_tenant(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    try:
        uc = await kc.count_users(realm); cls = await kc.list_clients(realm)
        idps = await kc.list_idps(realm); roles = await kc.list_roles(realm)
    except Exception: uc, cls, idps, roles = 0, [], [], []
    oc = await db.count_orgs(realm)
    wc = len(await db.list_webhooks(realm))
    pc = _plan(t)
    skip_roles = {"uma_authorization","offline_access",f"default-roles-{realm}"}
    custom_roles = [r for r in roles if r.get("name") not in skip_roles and not r.get("name","").startswith("uma_")]
    return {"id": str(t["_id"]), "name": t["name"], "realm_name": t["realm_name"], "plan": t["plan"],
        "plan_config": pc, "owner_email": t["owner_email"], "created_at": t.get("created_at"),
        "user_count": uc, "client_count": len(cls), "idp_count": len(idps), "org_count": oc,
        "role_count": len(custom_roles), "webhook_count": wc,
        "auth_settings": t.get("auth_settings", {}), "branding": t.get("branding", {}),
        "keycloak_url": f"{KEYCLOAK_EXTERNAL_URL}/realms/{realm}"}

@app.put("/api/tenants/{realm}")
async def update_tenant(realm: str, d: TenantUpdateM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    updates = {}
    if d.plan and d.plan in PLANS: updates["plan"] = d.plan
    if d.display_name: updates["name"] = d.display_name
    if updates:
        await db.update_tenant(realm, updates)
        await db.log_activity(admin["email"], "update_tenant", json.dumps(updates), realm)
    return {"status": "updated"}

@app.delete("/api/tenants/{realm}")
async def delete_tenant(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    try: await kc.delete_realm(realm)
    except Exception: pass
    await db.delete_tenant(realm)
    await db.log_activity(admin["email"], "delete_tenant", f"Deleted '{realm}'")
    return {"status": "deleted"}

# ═══ AUTH SETTINGS (Clerk: Instance settings) ═══
@app.put("/api/tenants/{realm}/auth-settings")
async def update_auth_settings(realm: str, d: AuthSettingsM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    settings = t.get("auth_settings", {})
    for k, v in d.dict(exclude_none=True).items(): settings[k] = v
    await db.update_tenant(realm, {"auth_settings": settings})
    # Apply to Keycloak
    kc_updates = {}
    if d.mfa_enabled is not None:
        kc_updates["otpPolicyType"] = "totp" if d.mfa_enabled else ""
    await db.log_activity(admin["email"], "update_auth_settings", json.dumps(settings), realm)
    return {"status": "updated", "auth_settings": settings}

# ═══ BRANDING (Clerk: customization) ═══
@app.put("/api/tenants/{realm}/branding")
async def update_branding(realm: str, d: BrandingM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    branding = t.get("branding", {})
    for k, v in d.dict(exclude_none=True).items(): branding[k] = v
    await db.update_tenant(realm, {"branding": branding})
    return {"status": "updated", "branding": branding}

# ═══ USERS ═══
@app.post("/api/tenants/{realm}/users")
async def create_user(realm: str, d: UserCreateM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    pc = _plan(t)
    # Disposable email check
    if t.get("auth_settings",{}).get("disposable_email_blocking"):
        domain = d.email.split("@")[-1].lower()
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            raise HTTPException(400, f"Disposable email domain '{domain}' is blocked")
    uc = await kc.count_users(realm)
    if pc["max_users"] != -1 and uc >= pc["max_users"]:
        raise HTTPException(403, f"User limit ({pc['max_users']}) reached")
    attrs = d.metadata if d.metadata else {}
    try: result = await kc.create_user(realm, d.username, d.email, d.password, d.first_name, d.last_name, attrs)
    except ValueError as e: raise HTTPException(409, str(e))
    await db.log_activity(admin["email"], "create_user", f"Created '{d.username}'", realm)
    await db.track_event(realm, "user.created", {"username": d.username, "email": d.email})
    await _fire_webhooks(realm, "user.created", {"username": d.username, "email": d.email, "user_id": result.get("user_id")})
    return result

@app.get("/api/tenants/{realm}/users")
async def list_users(realm: str, search: str = None, first: int = 0, max: int = 50, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    users = await kc.list_users(realm, first, max, search)
    return [{"id": u.get("id"), "username": u.get("username"), "email": u.get("email"),
             "firstName": u.get("firstName",""), "lastName": u.get("lastName",""),
             "enabled": u.get("enabled"), "emailVerified": u.get("emailVerified"),
             "createdTimestamp": u.get("createdTimestamp"), "attributes": u.get("attributes",{})} for u in users]

@app.get("/api/tenants/{realm}/users/{uid}")
async def get_user(realm: str, uid: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    u = await kc.get_user(realm, uid)
    sessions = await kc.get_user_sessions(realm, uid)
    roles = await kc.get_user_roles(realm, uid)
    return {"id": u.get("id"), "username": u.get("username"), "email": u.get("email"),
            "firstName": u.get("firstName",""), "lastName": u.get("lastName",""),
            "enabled": u.get("enabled"), "emailVerified": u.get("emailVerified"),
            "createdTimestamp": u.get("createdTimestamp"), "attributes": u.get("attributes",{}),
            "sessions": [{"id": s.get("id"), "ipAddress": s.get("ipAddress"),
                          "lastAccess": s.get("lastAccess"), "start": s.get("start"),
                          "clients": s.get("clients",{})} for s in sessions],
            "roles": [{"id": r.get("id"), "name": r.get("name")} for r in roles]}

@app.put("/api/tenants/{realm}/users/{uid}")
async def update_user(realm: str, uid: str, d: UserUpdateM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    updates = {}
    if d.first_name is not None: updates["firstName"] = d.first_name
    if d.last_name is not None: updates["lastName"] = d.last_name
    if d.email is not None: updates["email"] = d.email
    if d.enabled is not None: updates["enabled"] = d.enabled
    if d.metadata is not None: updates["attributes"] = d.metadata
    await kc.update_user(realm, uid, updates)
    await _fire_webhooks(realm, "user.updated", {"user_id": uid, "updates": updates})
    return {"status": "updated"}

@app.delete("/api/tenants/{realm}/users/{uid}")
async def delete_user(realm: str, uid: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    await kc.delete_user(realm, uid)
    await db.log_activity(admin["email"], "delete_user", f"Deleted user {uid}", realm)
    await _fire_webhooks(realm, "user.deleted", {"user_id": uid})
    return {"status": "deleted"}

# ═══ SESSIONS (Clerk: session management) ═══
@app.get("/api/tenants/{realm}/users/{uid}/sessions")
async def get_sessions(realm: str, uid: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    return await kc.get_user_sessions(realm, uid)

@app.delete("/api/tenants/{realm}/users/{uid}/sessions")
async def revoke_sessions(realm: str, uid: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    await kc.revoke_user_sessions(realm, uid)
    await _fire_webhooks(realm, "session.revoked", {"user_id": uid})
    return {"status": "all sessions revoked"}

@app.delete("/api/tenants/{realm}/sessions/{sid}")
async def revoke_session(realm: str, sid: str, admin=Depends(get_current_admin)):
    await kc.delete_session(realm, sid)
    return {"status": "session revoked"}

# ═══ IMPERSONATION (Clerk Pro) ═══
@app.post("/api/tenants/{realm}/users/{uid}/impersonate")
async def impersonate(realm: str, uid: str, admin=Depends(get_current_admin)):
    await _check_feature(realm, "user_impersonation")
    r = await kc.impersonate_user(realm, uid)
    await db.log_activity(admin["email"], "impersonate_user", f"Impersonated {uid}", realm)
    return r

# ═══ ROLES (Clerk RBAC) ═══
@app.post("/api/tenants/{realm}/roles")
async def create_role(realm: str, d: RoleCreateM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    r = await kc.create_role(realm, d.name, d.description)
    await db.log_activity(admin["email"], "create_role", f"Created role '{d.name}'", realm)
    return r

@app.get("/api/tenants/{realm}/roles")
async def list_roles(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    roles = await kc.list_roles(realm)
    skip = {"uma_authorization","offline_access",f"default-roles-{realm}"}
    return [{"id": r.get("id"), "name": r.get("name"), "description": r.get("description",""),
             "composite": r.get("composite",False)}
            for r in roles if r.get("name") not in skip and not r.get("name","").startswith("uma_")]

@app.delete("/api/tenants/{realm}/roles/{role_name}")
async def delete_role(realm: str, role_name: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    await kc.delete_role(realm, role_name)
    return {"status": "deleted"}

@app.post("/api/tenants/{realm}/users/{uid}/roles/{role_name}")
async def assign_user_role(realm: str, uid: str, role_name: str, admin=Depends(get_current_admin)):
    role = await kc.get_role(realm, role_name)
    if not role: raise HTTPException(404, "Role not found")
    await kc.assign_role(realm, uid, role["id"], role["name"])
    return {"status": "assigned"}

@app.delete("/api/tenants/{realm}/users/{uid}/roles/{role_name}")
async def remove_user_role(realm: str, uid: str, role_name: str, admin=Depends(get_current_admin)):
    role = await kc.get_role(realm, role_name)
    if not role: raise HTTPException(404, "Role not found")
    await kc.remove_role(realm, uid, role["id"], role["name"])
    return {"status": "removed"}

# ═══ ORGANIZATIONS (Clerk B2B) ═══
@app.post("/api/tenants/{realm}/organizations")
async def create_org(realm: str, d: OrgCreateM, admin=Depends(get_current_admin)):
    t, pc = await _check_feature(realm, "organizations")
    oc = await db.count_orgs(realm)
    if pc["max_orgs"] != -1 and oc >= pc["max_orgs"]:
        raise HTTPException(403, f"Org limit ({pc['max_orgs']}) reached")
    try: await kc.create_group(realm, d.slug, {"display_name": [d.name]})
    except Exception: pass
    await db.create_org(realm, d.name, d.slug, admin["email"])
    if d.allowed_email_domains:
        await db.update_org(realm, d.slug, {"allowed_email_domains": d.allowed_email_domains})
    await db.log_activity(admin["email"], "create_org", f"Created org '{d.name}'", realm)
    await db.track_event(realm, "organization.created", {"name": d.name, "slug": d.slug})
    await _fire_webhooks(realm, "organization.created", {"name": d.name, "slug": d.slug})
    return {"status": "created", "slug": d.slug}

@app.get("/api/tenants/{realm}/organizations")
async def list_orgs(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    orgs = await db.list_orgs(realm)
    return [{"id": str(o["_id"]), "name": o["name"], "slug": o["slug"],
             "member_count": len(o.get("members",[])), "allowed_email_domains": o.get("allowed_email_domains",[]),
             "created_at": o.get("created_at")} for o in orgs]

@app.get("/api/tenants/{realm}/organizations/{slug}")
async def get_org(realm: str, slug: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    o = await db.get_org(realm, slug)
    if not o: raise HTTPException(404, "Organization not found")
    return {"id": str(o["_id"]), "name": o["name"], "slug": o["slug"],
            "members": o.get("members",[]), "allowed_email_domains": o.get("allowed_email_domains",[]),
            "created_at": o.get("created_at")}

@app.post("/api/tenants/{realm}/organizations/{slug}/members")
async def add_org_member(realm: str, slug: str, d: OrgMemberM, admin=Depends(get_current_admin)):
    await db.add_org_member(realm, slug, d.user_id, d.role)
    await _fire_webhooks(realm, "organizationMembership.created", {"org": slug, "user_id": d.user_id, "role": d.role})
    return {"status": "added"}

@app.delete("/api/tenants/{realm}/organizations/{slug}/members/{uid}")
async def remove_org_member(realm: str, slug: str, uid: str, admin=Depends(get_current_admin)):
    await db.remove_org_member(realm, slug, uid)
    return {"status": "removed"}

@app.delete("/api/tenants/{realm}/organizations/{slug}")
async def delete_org(realm: str, slug: str, admin=Depends(get_current_admin)):
    await db.delete_org(realm, slug)
    return {"status": "deleted"}

# ═══ INVITATIONS (Clerk feature) ═══
@app.post("/api/tenants/{realm}/invitations")
async def create_invitation(realm: str, d: InvitationCreateM, admin=Depends(get_current_admin)):
    inv_id = await db.create_invitation(realm, d.email, d.org_slug, d.role, admin["email"])
    await db.log_activity(admin["email"], "create_invitation", f"Invited {d.email}", realm)
    await _fire_webhooks(realm, "invitation.created", {"email": d.email, "org_slug": d.org_slug})
    return {"status": "created", "id": inv_id}

@app.get("/api/tenants/{realm}/invitations")
async def list_invitations(realm: str, org_slug: str = None, admin=Depends(get_current_admin)):
    invs = await db.list_invitations(realm, org_slug)
    return [{"id": str(i["_id"]), "email": i["email"], "org_slug": i.get("org_slug"),
             "role": i["role"], "status": i["status"], "invited_by": i.get("invited_by",""),
             "created_at": i.get("created_at"), "expires_at": i.get("expires_at")} for i in invs]

# ═══ IDENTITY PROVIDERS (Clerk: Social + Enterprise SSO) ═══
@app.post("/api/tenants/{realm}/idp/oidc")
async def create_oidc_idp(realm: str, d: IdpCreateM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    providers = {"google": "google", "github": "github", "facebook": "facebook", "oidc": "oidc"}
    pid = providers.get(d.provider_type, "oidc")
    config = {"clientId": d.client_id, "clientSecret": d.client_secret}
    if pid == "oidc":
        config["authorizationUrl"] = d.authorization_url
        config["tokenUrl"] = d.token_url
    r = await kc.create_idp(realm, d.alias, pid, config)
    await db.log_activity(admin["email"], "create_idp", f"Added {d.provider_type}", realm)
    await db.track_event(realm, "sso.configured", {"provider": d.provider_type})
    return r

@app.post("/api/tenants/{realm}/idp/saml")
async def create_saml_idp(realm: str, d: SamlIdpCreateM, admin=Depends(get_current_admin)):
    t, pc = await _check_feature(realm, "saml_connections")
    if pc["saml_connections"] == 0: raise HTTPException(403, "SAML requires Business plan")
    idps = await kc.list_idps(realm)
    saml_count = len([i for i in idps if i.get("providerId") == "saml"])
    if pc["saml_connections"] != -1 and saml_count >= pc["saml_connections"]:
        raise HTTPException(403, "SAML connection limit reached")
    config = {"singleSignOnServiceUrl": d.sso_url, "entityId": d.entity_id,
              "nameIDPolicyFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"}
    if d.signing_certificate: config["signingCertificate"] = d.signing_certificate
    r = await kc.create_idp(realm, d.alias, "saml", config)
    await db.log_activity(admin["email"], "create_saml_idp", f"Added SAML '{d.alias}'", realm)
    return r

@app.get("/api/tenants/{realm}/idp")
async def list_idps(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    idps = await kc.list_idps(realm)
    return [{"alias": i.get("alias"), "providerId": i.get("providerId"),
             "enabled": i.get("enabled"), "displayName": i.get("displayName","")} for i in idps]

@app.delete("/api/tenants/{realm}/idp/{alias}")
async def delete_idp(realm: str, alias: str, admin=Depends(get_current_admin)):
    await kc.delete_idp(realm, alias)
    return {"status": "deleted"}

# ═══ CLIENTS (Applications) ═══
@app.post("/api/tenants/{realm}/clients")
async def create_client(realm: str, d: ClientCreateM, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    r = await kc.create_client(realm, d.client_id, d.redirect_uris, d.protocol)
    await db.log_activity(admin["email"], "create_client", f"Created '{d.client_id}'", realm)
    return r

@app.get("/api/tenants/{realm}/clients")
async def list_clients(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    cls = await kc.list_clients(realm)
    return [{"id": c.get("id"), "clientId": c.get("clientId"), "protocol": c.get("protocol"),
             "enabled": c.get("enabled"), "redirectUris": c.get("redirectUris",[]),
             "publicClient": c.get("publicClient")} for c in cls]

@app.delete("/api/tenants/{realm}/clients/{cid}")
async def delete_client(realm: str, cid: str, admin=Depends(get_current_admin)):
    await kc.delete_client(realm, cid)
    return {"status": "deleted"}

# ═══ WEBHOOKS (Clerk webhooks system) ═══
@app.post("/api/tenants/{realm}/webhooks")
async def create_webhook(realm: str, d: WebhookCreateM, admin=Depends(get_current_admin)):
    t, pc = await _check_feature(realm, "webhooks")
    wc = len(await db.list_webhooks(realm))
    if pc["max_webhooks"] != -1 and wc >= pc["max_webhooks"]:
        raise HTTPException(403, f"Webhook limit ({pc['max_webhooks']}) reached")
    secret = secrets.token_hex(32)
    wid = await db.create_webhook(realm, d.url, d.events, secret)
    await db.log_activity(admin["email"], "create_webhook", f"Added webhook to {d.url}", realm)
    return {"id": wid, "secret": secret, "status": "created"}

@app.get("/api/tenants/{realm}/webhooks")
async def list_webhooks(realm: str, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    whs = await db.list_webhooks(realm)
    return [{"id": str(w["_id"]), "url": w["url"], "events": w["events"],
             "enabled": w["enabled"], "created_at": w.get("created_at")} for w in whs]

@app.get("/api/tenants/{realm}/webhooks/{wid}/logs")
async def get_webhook_logs(realm: str, wid: str, admin=Depends(get_current_admin)):
    logs = await db.get_webhook_logs(wid)
    return [{"event": entry["event"], "status_code": entry["status_code"],
             "response_body": entry.get("response_body",""), "created_at": entry.get("created_at")} for entry in logs]

@app.delete("/api/tenants/{realm}/webhooks/{wid}")
async def delete_webhook(realm: str, wid: str, admin=Depends(get_current_admin)):
    await db.delete_webhook(wid)
    return {"status": "deleted"}

# ═══ ANALYTICS (Clerk dashboard analytics) ═══
@app.get("/api/tenants/{realm}/analytics")
async def get_analytics(realm: str, days: int = 30, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    summary = await db.get_analytics_summary(realm, days)
    user_signups = await db.get_daily_counts(realm, "user.created", days)
    try:
        login_events = await kc.get_events(realm, "LOGIN", 500)
        login_count = len(login_events)
        failed_logins = await kc.get_events(realm, "LOGIN_ERROR", 500)
        failed_count = len(failed_logins)
    except Exception: login_count, failed_count = 0, 0
    return {"summary": summary, "user_signups_daily": user_signups,
            "login_count": login_count, "failed_login_count": failed_count,
            "total_users": await kc.count_users(realm),
            "total_orgs": await db.count_orgs(realm)}

@app.get("/api/tenants/{realm}/events")
async def get_events(realm: str, event_type: str = None, max: int = 50, admin=Depends(get_current_admin)):
    t = await db.get_tenant(realm)
    if not t or t["owner_email"] != admin["email"]: raise HTTPException(404)
    return await kc.get_events(realm, event_type, max)

# ═══ DASHBOARD ═══
@app.get("/api/dashboard")
async def dashboard(admin=Depends(get_current_admin)):
    tenants = await db.list_tenants(admin["email"])
    total_users, total_clients, plan_dist = 0, 0, {}
    for t in tenants:
        try:
            total_users += await kc.count_users(t["realm_name"])
            total_clients += len(await kc.list_clients(t["realm_name"]))
        except Exception: pass
        p = t.get("plan","free")
        plan_dist[p] = plan_dist.get(p,0) + 1
    total_orgs = sum([await db.count_orgs(t["realm_name"]) for t in tenants])
    activity = await db.get_recent_activity(admin["email"], 15)
    recent = [{"action": a["action"], "details": a["details"],
               "realm_name": a.get("realm_name",""),
               "timestamp": a["timestamp"].isoformat() if a.get("timestamp") else ""} for a in activity]
    return {"total_tenants": len(tenants), "total_users": total_users,
            "total_clients": total_clients, "total_orgs": total_orgs,
            "plan_distribution": plan_dist, "recent_activity": recent}

# ═══ COUPONS ═══
@app.post("/api/coupons")
async def create_coupon(d: CouponCreateM, admin=Depends(get_current_admin)):
    existing = await db.get_coupon(d.code)
    if existing: raise HTTPException(409, f"Coupon '{d.code.upper()}' already exists")
    expires = None
    if d.duration_days > 0:
        from datetime import datetime, timedelta
        expires = datetime.utcnow() + timedelta(days=d.duration_days)
    cid = await db.create_coupon(d.code, d.discount_pct, d.description,
        d.max_redemptions, d.valid_plans or [], expires, admin["email"])
    await db.log_activity(admin["email"], "create_coupon", f"Created coupon {d.code.upper()} ({d.discount_pct}% off)")
    return {"id": cid, "code": d.code.upper(), "discount_pct": d.discount_pct}

@app.get("/api/coupons")
async def list_coupons(admin=Depends(get_current_admin)):
    coupons = await db.list_coupons(admin["email"])
    result = []
    for c in coupons:
        result.append({"code": c["code"], "discount_pct": c["discount_pct"],
            "description": c.get("description",""), "max_redemptions": c["max_redemptions"],
            "times_redeemed": c["times_redeemed"], "valid_plans": c.get("valid_plans",[]),
            "enabled": c["enabled"], "expires_at": c.get("expires_at"),
            "created_at": c.get("created_at")})
    return result

@app.post("/api/coupons/validate")
async def validate_coupon(d: CouponValidateM, admin=Depends(get_current_admin)):
    coupon, err = await db.validate_coupon(d.code, d.plan)
    if err: return {"valid": False, "error": err}
    return {"valid": True, "code": coupon["code"], "discount_pct": coupon["discount_pct"],
            "description": coupon.get("description","")}

@app.get("/api/coupons/{code}/redemptions")
async def get_redemptions(code: str, admin=Depends(get_current_admin)):
    reds = await db.get_coupon_redemptions(code)
    return [{"redeemed_by": r["redeemed_by"], "realm_name": r["realm_name"],
             "redeemed_at": r.get("redeemed_at")} for r in reds]

@app.put("/api/coupons/{code}/toggle")
async def toggle_coupon(code: str, admin=Depends(get_current_admin)):
    c = await db.get_coupon(code)
    if not c: raise HTTPException(404, "Coupon not found")
    new_state = not c.get("enabled", True)
    await db.update_coupon(code, {"enabled": new_state})
    return {"code": code.upper(), "enabled": new_state}

@app.delete("/api/coupons/{code}")
async def delete_coupon(code: str, admin=Depends(get_current_admin)):
    await db.delete_coupon(code)
    await db.log_activity(admin["email"], "delete_coupon", f"Deleted coupon {code.upper()}")
    return {"status": "deleted"}

@app.get("/api/health")
async def health(): return {"status": "ok", "version": "1.0.0"}
