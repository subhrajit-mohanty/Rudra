import asyncio
import logging
from datetime import datetime, timedelta

from config import MONGODB_DB, MONGODB_URL
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        for attempt in range(10):
            try:
                self.client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
                # Force a connection test
                await self.client.admin.command('ping')
                self.db = self.client[MONGODB_DB]
                await self._create_indexes()
                logger.info("Connected to MongoDB")
                return
            except Exception as e:
                logger.warning(f"MongoDB connection attempt {attempt+1}/10 failed: {e}")
                if attempt < 9:
                    await asyncio.sleep(3)
                else:
                    raise RuntimeError(f"Could not connect to MongoDB after 10 attempts: {e}")

    async def _create_indexes(self):
        await self.db.admins.create_index("email", unique=True)
        await self.db.tenants.create_index("realm_name", unique=True)
        await self.db.tenants.create_index("owner_email")
        await self.db.organizations.create_index([("realm_name", 1), ("slug", 1)], unique=True)
        await self.db.invitations.create_index([("realm_name", 1), ("email", 1)])
        await self.db.webhooks.create_index([("realm_name", 1)])
        await self.db.webhook_logs.create_index([("webhook_id", 1), ("created_at", -1)])
        await self.db.analytics_events.create_index([("realm_name", 1), ("event_type", 1), ("timestamp", -1)])
        await self.db.activity_log.create_index([("owner_email", 1), ("timestamp", -1)])
        await self.db.coupons.create_index("code", unique=True)
        await self.db.coupon_redemptions.create_index([("coupon_code", 1), ("redeemed_by", 1)])

    async def disconnect(self):
        if self.client: self.client.close()

    # ── Admin ──
    async def create_admin(self, email, hashed_password, name, company=""):
        doc = {"email": email, "password": hashed_password, "name": name, "company": company, "created_at": datetime.utcnow()}
        r = await self.db.admins.insert_one(doc)
        return str(r.inserted_id)

    async def get_admin_by_email(self, email):
        return await self.db.admins.find_one({"email": email})

    # ── Tenants ──
    async def create_tenant(self, name, realm_name, plan, owner_email, coupon_code="", discount_pct=0):
        doc = {"name": name, "realm_name": realm_name, "plan": plan, "owner_email": owner_email,
               "applied_coupon": coupon_code, "discount_pct": discount_pct,
               "auth_settings": {"password_auth": True, "social_login": True, "magic_links": False,
                                 "mfa_enabled": False, "mfa_methods": ["totp"],
                                 "disposable_email_blocking": False, "password_breach_detection": False,
                                 "bot_protection": False, "allowed_domains": [], "blocked_domains": []},
               "branding": {"logo_url": "", "primary_color": "#10a0a0", "background_color": "#f4f8f8"},
               "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        r = await self.db.tenants.insert_one(doc)
        return str(r.inserted_id)

    async def get_tenant(self, realm_name):
        return await self.db.tenants.find_one({"realm_name": realm_name})

    async def list_tenants(self, owner_email):
        return await self.db.tenants.find({"owner_email": owner_email}).to_list(100)

    async def update_tenant(self, realm_name, updates):
        updates["updated_at"] = datetime.utcnow()
        await self.db.tenants.update_one({"realm_name": realm_name}, {"$set": updates})

    async def delete_tenant(self, realm_name):
        await self.db.tenants.delete_one({"realm_name": realm_name})
        await self.db.organizations.delete_many({"realm_name": realm_name})
        await self.db.invitations.delete_many({"realm_name": realm_name})
        await self.db.webhooks.delete_many({"realm_name": realm_name})
        await self.db.analytics_events.delete_many({"realm_name": realm_name})

    async def count_tenants(self, owner_email):
        return await self.db.tenants.count_documents({"owner_email": owner_email})

    # ── Organizations (Clerk B2B feature) ──
    async def create_org(self, realm_name, name, slug, created_by):
        doc = {"realm_name": realm_name, "name": name, "slug": slug, "created_by": created_by,
               "members": [{"user_id": created_by, "role": "admin", "joined_at": datetime.utcnow()}],
               "allowed_email_domains": [], "max_members": -1,
               "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        r = await self.db.organizations.insert_one(doc)
        return str(r.inserted_id)

    async def list_orgs(self, realm_name):
        return await self.db.organizations.find({"realm_name": realm_name}).to_list(500)

    async def get_org(self, realm_name, slug):
        return await self.db.organizations.find_one({"realm_name": realm_name, "slug": slug})

    async def update_org(self, realm_name, slug, updates):
        updates["updated_at"] = datetime.utcnow()
        await self.db.organizations.update_one({"realm_name": realm_name, "slug": slug}, {"$set": updates})

    async def delete_org(self, realm_name, slug):
        await self.db.organizations.delete_one({"realm_name": realm_name, "slug": slug})

    async def add_org_member(self, realm_name, slug, user_id, role="member"):
        await self.db.organizations.update_one(
            {"realm_name": realm_name, "slug": slug},
            {"$push": {"members": {"user_id": user_id, "role": role, "joined_at": datetime.utcnow()}}})

    async def remove_org_member(self, realm_name, slug, user_id):
        await self.db.organizations.update_one(
            {"realm_name": realm_name, "slug": slug},
            {"$pull": {"members": {"user_id": user_id}}})

    async def count_orgs(self, realm_name):
        return await self.db.organizations.count_documents({"realm_name": realm_name})

    # ── Invitations ──
    async def create_invitation(self, realm_name, email, org_slug=None, role="member", invited_by=""):
        doc = {"realm_name": realm_name, "email": email, "org_slug": org_slug, "role": role,
               "invited_by": invited_by, "status": "pending", "created_at": datetime.utcnow(),
               "expires_at": datetime.utcnow() + timedelta(days=7)}
        r = await self.db.invitations.insert_one(doc)
        return str(r.inserted_id)

    async def list_invitations(self, realm_name, org_slug=None):
        q = {"realm_name": realm_name}
        if org_slug: q["org_slug"] = org_slug
        return await self.db.invitations.find(q).to_list(500)

    async def update_invitation(self, inv_id, status):
        from bson import ObjectId
        await self.db.invitations.update_one({"_id": ObjectId(inv_id)}, {"$set": {"status": status}})

    # ── Webhooks ──
    async def create_webhook(self, realm_name, url, events, secret):
        doc = {"realm_name": realm_name, "url": url, "events": events, "secret": secret,
               "enabled": True, "created_at": datetime.utcnow()}
        r = await self.db.webhooks.insert_one(doc)
        return str(r.inserted_id)

    async def list_webhooks(self, realm_name):
        return await self.db.webhooks.find({"realm_name": realm_name}).to_list(50)

    async def delete_webhook(self, webhook_id):
        from bson import ObjectId
        await self.db.webhooks.delete_one({"_id": ObjectId(webhook_id)})

    async def log_webhook_delivery(self, webhook_id, event, status_code, response_body=""):
        doc = {"webhook_id": webhook_id, "event": event, "status_code": status_code,
               "response_body": response_body[:1000], "created_at": datetime.utcnow()}
        await self.db.webhook_logs.insert_one(doc)

    async def get_webhook_logs(self, webhook_id, limit=20):
        return await self.db.webhook_logs.find({"webhook_id": webhook_id}).sort("created_at", -1).limit(limit).to_list(limit)

    # ── Analytics Events ──
    async def track_event(self, realm_name, event_type, metadata=None):
        doc = {"realm_name": realm_name, "event_type": event_type,
               "metadata": metadata or {}, "timestamp": datetime.utcnow()}
        await self.db.analytics_events.insert_one(doc)

    async def get_analytics(self, realm_name, event_type=None, days=30):
        q = {"realm_name": realm_name, "timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}}
        if event_type: q["event_type"] = event_type
        return await self.db.analytics_events.find(q).sort("timestamp", -1).to_list(1000)

    async def get_analytics_summary(self, realm_name, days=30):
        since = datetime.utcnow() - timedelta(days=days)
        pipeline = [
            {"$match": {"realm_name": realm_name, "timestamp": {"$gte": since}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        ]
        cursor = self.db.analytics_events.aggregate(pipeline)
        result = {}
        async for doc in cursor:
            result[doc["_id"]] = doc["count"]
        return result

    async def get_daily_counts(self, realm_name, event_type, days=30):
        since = datetime.utcnow() - timedelta(days=days)
        pipeline = [
            {"$match": {"realm_name": realm_name, "event_type": event_type, "timestamp": {"$gte": since}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        cursor = self.db.analytics_events.aggregate(pipeline)
        return await cursor.to_list(60)

    # ── Activity Log ──
    async def log_activity(self, owner_email, action, details="", realm_name=""):
        doc = {"owner_email": owner_email, "action": action, "details": details,
               "realm_name": realm_name, "timestamp": datetime.utcnow()}
        await self.db.activity_log.insert_one(doc)

    async def get_recent_activity(self, owner_email, limit=20):
        return await self.db.activity_log.find({"owner_email": owner_email}).sort("timestamp", -1).limit(limit).to_list(limit)

    # ── Coupons ──
    async def create_coupon(self, code, discount_pct, description="", max_redemptions=-1,
                            valid_plans=None, expires_at=None, created_by=""):
        doc = {"code": code.upper().strip(), "discount_pct": min(max(discount_pct, 1), 100),
               "description": description, "max_redemptions": max_redemptions,
               "times_redeemed": 0, "valid_plans": valid_plans or [],
               "expires_at": expires_at, "enabled": True,
               "created_by": created_by, "created_at": datetime.utcnow()}
        r = await self.db.coupons.insert_one(doc)
        return str(r.inserted_id)

    async def list_coupons(self, created_by=None):
        q = {"created_by": created_by} if created_by else {}
        return await self.db.coupons.find(q).sort("created_at", -1).to_list(200)

    async def get_coupon(self, code):
        return await self.db.coupons.find_one({"code": code.upper().strip()})

    async def validate_coupon(self, code, plan=""):
        c = await self.get_coupon(code)
        if not c: return None, "Coupon not found"
        if not c.get("enabled"): return None, "Coupon is disabled"
        if c.get("expires_at") and c["expires_at"] < datetime.utcnow():
            return None, "Coupon has expired"
        if c["max_redemptions"] != -1 and c["times_redeemed"] >= c["max_redemptions"]:
            return None, "Coupon redemption limit reached"
        if c.get("valid_plans") and plan and plan not in c["valid_plans"]:
            return None, f"Coupon not valid for '{plan}' plan"
        return c, None

    async def redeem_coupon(self, code, redeemed_by, realm_name):
        code = code.upper().strip()
        await self.db.coupons.update_one({"code": code}, {"$inc": {"times_redeemed": 1}})
        await self.db.coupon_redemptions.insert_one({
            "coupon_code": code, "redeemed_by": redeemed_by,
            "realm_name": realm_name, "redeemed_at": datetime.utcnow()})

    async def get_coupon_redemptions(self, code=None, limit=100):
        q = {"coupon_code": code.upper().strip()} if code else {}
        return await self.db.coupon_redemptions.find(q).sort("redeemed_at", -1).to_list(limit)

    async def update_coupon(self, code, updates):
        await self.db.coupons.update_one({"code": code.upper().strip()}, {"$set": updates})

    async def delete_coupon(self, code):
        await self.db.coupons.delete_one({"code": code.upper().strip()})

db = Database()
