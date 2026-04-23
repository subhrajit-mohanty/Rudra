<div align="center">

<img src="assets/banner.svg" alt="Rudra — Open-source managed authentication platform" width="800" />

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](docker-compose.yml)
[![Python SDK](https://img.shields.io/badge/SDK-Python-3776AB.svg)](sdk/python/)
[![JS SDK](https://img.shields.io/badge/SDK-JavaScript-F7DF1E.svg)](sdk/javascript/)

[Quick Start](#quick-start) · [Documentation](https://rudra-auth.github.io/rudra/) · [SDK](#sdk) · [Contributing](CONTRIBUTING.md)

</div>

---

## Quick Start

```bash
cp .env.example .env
# edit .env and replace every change_me_* placeholder with a real secret
docker compose up --build
```

The backend refuses to boot if `SECRET_KEY` or any other required variable
in `.env` is missing, so fill the file in before starting the stack.

| Service     | URL                       | Credentials                                   |
|-------------|---------------------------|-----------------------------------------------|
| Dashboard   | http://localhost:3000     | Register new account on the login page        |
| API Docs    | http://localhost:8000/docs| Bearer token from `/api/auth/login`           |
| Keycloak    | http://localhost:8080     | `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`  |

## Screenshots

### Onboarding

| | |
|---|---|
| ![Login](assets/screenshots/01-login.png) | ![Register](assets/screenshots/02-register.png) |
| Sign in page | Create an admin account |
| ![Empty dashboard](assets/screenshots/03-dashboard-empty.png) | ![Plan picker](assets/screenshots/04-plans.png) |
| Dashboard after first sign in | Pick a plan for a new project |
| ![Project form](assets/screenshots/05-project-form.png) | ![Project detail](assets/screenshots/06-project-detail.png) |
| Name a project and attach a coupon | Project overview with live counts |

### Inside a project

| | |
|---|---|
| ![Users tab](assets/screenshots/08-project-users.png) | ![Applications tab](assets/screenshots/09-project-applications.png) |
| Manage end users across the realm | Register OIDC and SAML applications |
| ![SSO tab](assets/screenshots/10-project-sso.png) | ![Organizations tab](assets/screenshots/11-project-organizations.png) |
| Add OIDC or SAML identity providers | B2B organizations with domain auto join |
| ![Roles tab](assets/screenshots/12-project-roles.png) | ![Webhooks tab](assets/screenshots/13-project-webhooks.png) |
| RBAC roles mapped into JWT tokens | Event delivery endpoints with subscriptions |
| ![Settings tab](assets/screenshots/14-project-settings.png) | ![Dashboard populated](assets/screenshots/17-dashboard-pro-project.png) |
| Auth stack toggles and branding | Global dashboard once a Pro project is seeded |

### Coupons

| | |
|---|---|
| ![Coupons list](assets/screenshots/15-coupons-list.png) | ![Create coupon modal](assets/screenshots/16-coupon-create-modal.png) |
| Active coupons with redemption counts | Create a new coupon with plan scope and expiry |

See [docs/screenshots.md](docs/screenshots.md) for the full tour with captions.

## Features

- **Email/Password, Social Login, Magic Links, MFA** — Full auth stack per project
- **Enterprise SSO** — OIDC + SAML identity providers
- **B2B Organizations** — Multi-tenant orgs with roles, invitations, domain auto-join
- **RBAC** — Custom roles assigned to users, reflected in JWT tokens
- **Webhooks** — Real-time events (user.created, org.created, etc.) with delivery logs
- **Coupons** — Discount codes with plan restrictions, usage limits, expiry tracking
- **Analytics** — User signup trends, login tracking, activity audit log
- **Session Management** — View, revoke sessions, user impersonation
- **Bot Protection, Breach Detection, Disposable Email Blocking** — Security features
- **Multi-tier Plans** — Free / Pro / Business / Enterprise with feature gating

## Architecture

```
React (3000) → FastAPI (8000) → Keycloak (8080)
                    ↓
          MongoDB (27017) + Postgres (5432) + Redis (6379)
```

## SDK

Rudra ships with official SDKs for Python and JavaScript.

### Python

```bash
cd sdk/python && pip install -e .
```

```python
from rudra_sdk import RudraClient

client = RudraClient("http://localhost:8000",
    email="admin@example.com", password="secret")

# Create project with coupon
client.projects.create("My App", "my-app", plan="pro", coupon_code="WELCOME50")

# Manage users
client.users.create("my-app", username="jane", email="jane@co.com", password="pass123")
users = client.users.list("my-app", search="jane")

# Organizations, roles, webhooks, SSO...
client.organizations.create("my-app", name="Acme", slug="acme")
client.roles.create("my-app", name="editor")
client.webhooks.create("my-app", url="https://app.com/hook", events=["user.created"])
client.sso.add_oidc("my-app", alias="google", client_id="...", client_secret="...")
```

### JavaScript

```bash
npm install @rudra/sdk  # or import from sdk/javascript/
```

```javascript
import { RudraClient } from '@rudra/sdk';

const client = new RudraClient('http://localhost:8000');
await client.login('admin@example.com', 'secret');

await client.projects.create('My App', 'my-app', 'pro');
await client.users.create('my-app', { username: 'jane', email: 'jane@co.com', password: 'pass123' });
await client.organizations.create('my-app', { name: 'Acme', slug: 'acme' });
```

See full SDK docs: [Python](sdk/python/README.md) | [JavaScript](sdk/javascript/README.md)

## Plans

| | Free | Pro $25 | Business $99 | Enterprise $499 |
|---|---|---|---|---|
| Users | 10K | 100K | 500K | Unlimited |
| Projects | 1 | 5 | Unlimited | Unlimited |
| Organizations | — | 50 | Unlimited | Unlimited |
| SAML SSO | — | — | 3 | Unlimited |
| Webhooks | — | 3 | 10 | Unlimited |
| Analytics | — | ✓ | ✓ | ✓ |
| Impersonation | — | ✓ | ✓ | ✓ |
| Bot Protection | — | ✓ | ✓ | ✓ |
| Coupons | ✓ | ✓ | ✓ | ✓ |

## Project Structure

```
rudra/
├── backend/              # FastAPI (50+ endpoints)
├── frontend/             # React + Vite dashboard
├── sdk/
│   ├── python/           # rudra Python package
│   └── javascript/       # @rudra/sdk npm package
├── docker-compose.yml    # 6-service stack
├── docs.html             # Full documentation (open in browser)
├── LICENSE               # MIT
├── CONTRIBUTING.md       # Contribution guide
└── README.md
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) — free for personal and commercial use.
