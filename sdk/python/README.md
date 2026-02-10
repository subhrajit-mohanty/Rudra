# Rudra Python SDK

Official Python SDK for [Rudra](https://github.com/rudra-auth/rudra) — managed auth platform powered by Keycloak.

## Install

```bash
pip install rudra
# or from source
cd sdk/python && pip install -e .
```

## Quick Start

```python
from rudra_sdk import RudraClient

# Connect to Rudra
client = RudraClient(
    "http://localhost:8000",
    email="admin@example.com",
    password="your-password"
)

# Create a project
project = client.projects.create(
    name="My SaaS App",
    realm_name="my-saas-app",
    plan="pro",
    coupon_code="WELCOME50"  # optional
)

# Create users
user = client.users.create("my-saas-app",
    username="janedoe",
    email="jane@example.com",
    password="securepass123",
    first_name="Jane",
    last_name="Doe"
)

# List users with search
users = client.users.list("my-saas-app", search="jane")

# Create an organization
org = client.organizations.create("my-saas-app",
    name="Acme Corp",
    slug="acme-corp",
    allowed_email_domains=["acme.com"]
)

# Add SSO provider
client.sso.add_oidc("my-saas-app",
    alias="google",
    provider_type="google",
    client_id="GOOGLE_CLIENT_ID",
    client_secret="GOOGLE_SECRET"
)

# Create roles and assign
client.roles.create("my-saas-app", name="editor", description="Can edit content")
client.roles.assign("my-saas-app", user_id="user-uuid", role_name="editor")

# Set up webhooks
webhook = client.webhooks.create("my-saas-app",
    url="https://my-app.com/webhooks",
    events=["user.created", "user.deleted", "organization.created"]
)
print(f"Webhook secret: {webhook['secret']}")

# Create coupons
client.coupons.create(
    code="STARTUP30",
    discount_pct=30,
    description="Startup discount",
    max_redemptions=100,
    valid_plans=["pro", "business"]
)

# Analytics
stats = client.analytics.summary("my-saas-app", days=30)
print(f"Total users: {stats['total_users']}")
print(f"Logins (30d): {stats['login_count']}")
```

## API Reference

### Resources

| Resource | Methods |
|---|---|
| `client.auth` | `register()`, `login()`, `me()` |
| `client.projects` | `create()`, `list()`, `get()`, `update()`, `delete()`, `update_auth_settings()`, `update_branding()` |
| `client.users` | `create()`, `list()`, `get()`, `update()`, `delete()`, `impersonate()` |
| `client.sessions` | `list()`, `revoke_all()`, `revoke()` |
| `client.organizations` | `create()`, `list()`, `add_member()`, `remove_member()`, `delete()`, `invite()`, `list_invitations()` |
| `client.roles` | `create()`, `list()`, `assign()`, `remove()`, `delete()` |
| `client.sso` | `add_oidc()`, `add_saml()`, `list()`, `delete()` |
| `client.clients` | `create()`, `list()`, `delete()` |
| `client.webhooks` | `create()`, `list()`, `logs()`, `delete()` |
| `client.coupons` | `create()`, `list()`, `validate()`, `redemptions()`, `toggle()`, `delete()` |
| `client.analytics` | `summary()`, `events()`, `dashboard()` |

### Error Handling

```python
from rudra_sdk import RudraClient, RudraAPIError

try:
    client.users.create("my-realm", username="existing", ...)
except RudraAPIError as e:
    print(f"Error {e.status_code}: {e.detail}")
```

## License

MIT
