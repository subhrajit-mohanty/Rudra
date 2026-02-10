import os

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_EXTERNAL_URL = os.getenv("KEYCLOAK_EXTERNAL_URL", "http://localhost:8080")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:admin_password@localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "rudra")
REDIS_URL = os.getenv("REDIS_URL", "redis://:redis_password@localhost:6379/0")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

DISPOSABLE_EMAIL_DOMAINS = [
    "mailinator.com","tempmail.com","throwaway.email","guerrillamail.com",
    "sharklasers.com","guerrillamailblock.com","grr.la","yopmail.com",
    "10minutemail.com","trashmail.com","fakeinbox.com","maildrop.cc",
]

PLANS = {
    "free": {
        "name": "Free", "price": 0,
        "max_users": 10000, "max_admins": 1, "max_realms": 1,
        "saml_connections": 0, "mfa_level": "basic",
        "custom_branding": True, "oidc_sso": True,
        "social_login": True, "magic_links": False,
        "organizations": False, "max_orgs": 0,
        "webhooks": False, "max_webhooks": 0,
        "analytics": False, "user_impersonation": False,
        "session_management": True, "device_tracking": False,
        "disposable_email_blocking": False,
        "custom_roles": False, "max_roles": 2,
        "bot_protection": False, "password_breach_detection": False,
        "priority_support": False, "premium_support": False,
        "api_rate_limit": 100,
    },
    "pro": {
        "name": "Pro", "price": 25,
        "max_users": 100000, "max_admins": 3, "max_realms": 5,
        "saml_connections": 0, "mfa_level": "advanced",
        "custom_branding": True, "oidc_sso": True,
        "social_login": True, "magic_links": True,
        "organizations": True, "max_orgs": 50,
        "webhooks": True, "max_webhooks": 3,
        "analytics": True, "user_impersonation": True,
        "session_management": True, "device_tracking": True,
        "disposable_email_blocking": True,
        "custom_roles": True, "max_roles": 20,
        "bot_protection": True, "password_breach_detection": True,
        "priority_support": True, "premium_support": False,
        "api_rate_limit": 1000,
    },
    "business": {
        "name": "Business", "price": 99,
        "max_users": 500000, "max_admins": 10, "max_realms": -1,
        "saml_connections": 3, "mfa_level": "advanced",
        "custom_branding": True, "oidc_sso": True,
        "social_login": True, "magic_links": True,
        "organizations": True, "max_orgs": -1,
        "webhooks": True, "max_webhooks": 10,
        "analytics": True, "user_impersonation": True,
        "session_management": True, "device_tracking": True,
        "disposable_email_blocking": True,
        "custom_roles": True, "max_roles": -1,
        "bot_protection": True, "password_breach_detection": True,
        "priority_support": True, "premium_support": True,
        "api_rate_limit": 5000,
    },
    "enterprise": {
        "name": "Enterprise", "price": 499,
        "max_users": -1, "max_admins": -1, "max_realms": -1,
        "saml_connections": -1, "mfa_level": "full",
        "custom_branding": True, "oidc_sso": True,
        "social_login": True, "magic_links": True,
        "organizations": True, "max_orgs": -1,
        "webhooks": True, "max_webhooks": -1,
        "analytics": True, "user_impersonation": True,
        "session_management": True, "device_tracking": True,
        "disposable_email_blocking": True,
        "custom_roles": True, "max_roles": -1,
        "bot_protection": True, "password_breach_detection": True,
        "priority_support": True, "premium_support": True,
        "api_rate_limit": -1,
    },
}
