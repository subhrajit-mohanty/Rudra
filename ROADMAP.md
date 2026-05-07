# Rudra Roadmap

This is the living product roadmap for Rudra, focused on a single-quarter release cadence. The next release (v1.2.0) is ambitious but scoped to roughly twelve weeks of work for a small team. Everything else lives in the [Backlog](#backlog) until v1.2.0 ships.

The current released version is **1.1.0** (April 2026). The next target is **1.2.0** by mid-July 2026.

## How to read this document

* One quarterly milestone. Twenty four issues, each fully scoped with acceptance criteria, technical approach, dependencies, and references.
* Beyond v1.2.0, items are in the [backlog](#backlog), grouped by tier so they can be promoted into v1.3.0 when the next quarter opens.
* Effort markers: **S** under a week, **M** one to three weeks, **L** over a month, **XL** over a quarter.
* Priority markers: **P0** ship first, **P1** ship early, **P2** ship later in the milestone, **P3** defer if tight.

## Where to look first

* Browse the milestone: [v1.2.0](https://github.com/subhrajit-mohanty/Rudra/milestone/1).
* Filter by tier: [tier:foundation](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Afoundation), [tier:auth](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Aauth), [tier:ai-native](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Aai-native), [tier:enterprise](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Aenterprise), [tier:devex](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Adevex), [tier:novel](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Anovel), [tier:polish](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Apolish).
* Filter by priority: [priority:p0-critical](https://github.com/subhrajit-mohanty/Rudra/labels/priority%3Ap0-critical), [priority:p1-high](https://github.com/subhrajit-mohanty/Rudra/labels/priority%3Ap1-high).
* Backlog (no milestone): [issues with no milestone](https://github.com/subhrajit-mohanty/Rudra/issues?q=is%3Aissue+is%3Aopen+no%3Amilestone).
* Good first issues: effort `S` items tagged `priority:p2-medium` or lower.

---

## v1.2.0 - Production-ready quarter

**Target:** 2026-07-15 · **Milestone:** [v1.2.0](https://github.com/subhrajit-mohanty/Rudra/milestone/1) · **Scope:** 24 issues

**Theme:** every feature the product advertises actually works, ops can observe and operate the system, modern auth ships (passkeys, step-up, OTP, MFA recovery, account-protection), and developer first-hour friction is gone. Anything that does not directly serve those goals lives in the backlog until v1.2.0 lands.

### Foundation: trust repair and ops hygiene (12 items)

These twelve items remove the gap between what Rudra advertises and what Rudra does. Without them, every other feature rests on sand.

| ID | Title | Effort | Priority |
|---|---|---|---|
| FND-10 | [Reconcile pyproject.toml with backend/requirements.txt](https://github.com/subhrajit-mohanty/Rudra/issues/4) | S | P0 |
| FND-3 | [Enforce per-tenant api_rate_limit using Redis](https://github.com/subhrajit-mohanty/Rudra/issues/5) | S | P0 |
| FND-5 | [Wire MFA toggle through to Keycloak required-actions](https://github.com/subhrajit-mohanty/Rudra/issues/6) | S | P0 |
| FND-6 | [Implement password breach detection via HIBP](https://github.com/subhrajit-mohanty/Rudra/issues/7) | S | P0 |
| FND-7 | [Implement bot protection via Cloudflare Turnstile](https://github.com/subhrajit-mohanty/Rudra/issues/8) | S | P0 |
| FND-8 | [HMAC-SHA256 signatures for webhook deliveries](https://github.com/subhrajit-mohanty/Rudra/issues/9) | S | P0 |
| FND-9 | [Migrate remaining 25 endpoints to _get_owned_tenant helper](https://github.com/subhrajit-mohanty/Rudra/issues/10) | S | P1 |
| FND-1 | [Cache Keycloak admin token in Redis](https://github.com/subhrajit-mohanty/Rudra/issues/11) | S | P0 |
| FND-2 | [Share a single httpx.AsyncClient with connection pooling](https://github.com/subhrajit-mohanty/Rudra/issues/12) | S | P0 |
| FND-11 | [Real /api/health that checks Mongo, Keycloak, Redis](https://github.com/subhrajit-mohanty/Rudra/issues/13) | S | P1 |
| FND-4 | [Background queue for webhook delivery with retries and DLQ](https://github.com/subhrajit-mohanty/Rudra/issues/14) | M | P1 |
| FND-12 | [Prometheus metrics and OpenTelemetry tracing](https://github.com/subhrajit-mohanty/Rudra/issues/15) | M | P1 |

### Modern auth that evaluators look for in the first hour (5 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| A-1 | [Passkeys / WebAuthn support](https://github.com/subhrajit-mohanty/Rudra/issues/19) | M | P1 |
| A-4 | [Step-up authentication for sensitive operations](https://github.com/subhrajit-mohanty/Rudra/issues/21) | S | P1 |
| A-8 | [Email OTP and SMS OTP as alternatives to magic links](https://github.com/subhrajit-mohanty/Rudra/issues/22) | S | P1 |
| A-11 | [MFA recovery flows (backup codes, recovery email, admin unlock)](https://github.com/subhrajit-mohanty/Rudra/issues/23) | S | P1 |
| C-9 | [GDPR data subject access requests (export and deletion)](https://github.com/subhrajit-mohanty/Rudra/issues/34) | S | P2 |

### Quality of life and rollout safety (4 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| D-5 | [Publish auto-generated OpenAPI spec and versioned releases](https://github.com/subhrajit-mohanty/Rudra/issues/16) | S | P1 |
| D-6 | [Webhook replay in dashboard and local tunnel in CLI](https://github.com/subhrajit-mohanty/Rudra/issues/17) | S | P2 |
| P-1 | [In-dashboard email template editor with live preview](https://github.com/subhrajit-mohanty/Rudra/issues/18) | S | P2 |
| E-5 | [Per-tenant feature flags](https://github.com/subhrajit-mohanty/Rudra/issues/33) | S | P1 |

### Stretch goals (3 items, ship if quarter has slack)

| ID | Title | Effort | Priority |
|---|---|---|---|
| A-12 | [Service account tokens for CI/CD and server-to-server](https://github.com/subhrajit-mohanty/Rudra/issues/24) | S | P2 |
| C-5 | [Immutable tamper-evident audit logs (hash-chained)](https://github.com/subhrajit-mohanty/Rudra/issues/31) | S | P2 |
| D-1 | [rudra CLI for login, resource management, logs, webhook tunnel](https://github.com/subhrajit-mohanty/Rudra/issues/27) | M | P2 |

---

## Backlog

Thirty eight fully scoped issues, parked until v1.2.0 ships. Each is ready to be picked up the moment the next quarter opens. Listed by tier so contributors can browse to the area they want to work on.

### Modern auth and B2B identity

| ID | Title | Effort |
|---|---|---|
| A-2 | [Hosted UI components (`<SignIn />`, `<UserButton />`, ...)](https://github.com/subhrajit-mohanty/Rudra/issues/25) | XL |
| A-3 | [Account linking across password, social and passkeys](https://github.com/subhrajit-mohanty/Rudra/issues/20) | M |
| A-5 | [Adaptive risk-based authentication](https://github.com/subhrajit-mohanty/Rudra/issues/36) | M |
| A-6 | [Custom domains per tenant](https://github.com/subhrajit-mohanty/Rudra/issues/45) | L |
| A-7 | [Fine-grained authorization (ReBAC) with POST /api/check](https://github.com/subhrajit-mohanty/Rudra/issues/35) | L |
| A-10 | [Framework SDKs (rudra-fastapi, rudra-django, rudra-nextjs, rudra-express)](https://github.com/subhrajit-mohanty/Rudra/issues/26) | M |

### AI-native auth

| ID | Title | Effort |
|---|---|---|
| B-1 | [Agents as first-class principals](https://github.com/subhrajit-mohanty/Rudra/issues/37) | M |
| B-2 | [OAuth 2.0 authorization server for MCP servers](https://github.com/subhrajit-mohanty/Rudra/issues/38) | L |
| B-3 | [Human-in-the-loop approval workflows](https://github.com/subhrajit-mohanty/Rudra/issues/39) | M |
| B-4 | [Per-tool scoped tokens with minute-level expiry](https://github.com/subhrajit-mohanty/Rudra/issues/40) | M |
| B-5 | [Agent audit log with intent capture](https://github.com/subhrajit-mohanty/Rudra/issues/41) | S |
| B-6 | [AI policy assistant - natural language to ReBAC](https://github.com/subhrajit-mohanty/Rudra/issues/42) | M |
| B-7 | [Natural-language audit log queries](https://github.com/subhrajit-mohanty/Rudra/issues/43) | M |
| B-8 | [Explainable risk score UI](https://github.com/subhrajit-mohanty/Rudra/issues/44) | S |

### Enterprise and compliance

| ID | Title | Effort |
|---|---|---|
| C-1 | [SCIM 2.0 provisioning endpoint](https://github.com/subhrajit-mohanty/Rudra/issues/28) | M |
| C-2 | [Organization-level SSO](https://github.com/subhrajit-mohanty/Rudra/issues/29) | M |
| C-3 | [Organization hierarchies (parent / child orgs)](https://github.com/subhrajit-mohanty/Rudra/issues/54) | M |
| C-4 | [Audit log streaming to S3, Datadog, Splunk, OCSF](https://github.com/subhrajit-mohanty/Rudra/issues/30) | M |
| C-6 | [Data residency in US / EU / APAC (start)](https://github.com/subhrajit-mohanty/Rudra/issues/51) | XL |
| C-7 | [Customer-managed encryption keys (BYOK)](https://github.com/subhrajit-mohanty/Rudra/issues/49) | M |
| C-8 | [Compliance pack (SOC 2 / GDPR / HIPAA preset)](https://github.com/subhrajit-mohanty/Rudra/issues/50) | M |
| C-10 | [IP allowlisting and geo-fencing per tenant](https://github.com/subhrajit-mohanty/Rudra/issues/32) | S |
| C-11 | [Organization-scoped API keys](https://github.com/subhrajit-mohanty/Rudra/issues/55) | M |
| C-12 | [Dark web monitoring for tenant user credentials](https://github.com/subhrajit-mohanty/Rudra/issues/56) | S |

### Developer experience

| ID | Title | Effort |
|---|---|---|
| D-2 | [Terraform provider and Helm chart](https://github.com/subhrajit-mohanty/Rudra/issues/46) | M |
| D-3 | [Migration tools from Auth0, Clerk, Firebase](https://github.com/subhrajit-mohanty/Rudra/issues/58) | L |
| D-4 | [Additional SDKs: Go, Java, Ruby, .NET, PHP](https://github.com/subhrajit-mohanty/Rudra/issues/57) | L |
| D-7 | [Auth flow playground in the dashboard](https://github.com/subhrajit-mohanty/Rudra/issues/47) | M |
| D-8 | [Self-service diagnostic dump](https://github.com/subhrajit-mohanty/Rudra/issues/48) | S |
| D-9 | [Visual workflow builder for auth flows](https://github.com/subhrajit-mohanty/Rudra/issues/59) | L |

### Commercial and novel

| ID | Title | Effort |
|---|---|---|
| E-3 | [Consent ledger with user-facing receipts](https://github.com/subhrajit-mohanty/Rudra/issues/53) | M |
| E-4 | [Stripe-backed metered billing for plans and MAU](https://github.com/subhrajit-mohanty/Rudra/issues/52) | M |

### Polish and scale

| ID | Title | Effort |
|---|---|---|
| P-5 | [Real-time dashboard updates via WebSockets](https://github.com/subhrajit-mohanty/Rudra/issues/64) | S |
| P-6 | [Read replicas and per-tenant Mongo sharding](https://github.com/subhrajit-mohanty/Rudra/issues/60) | L |
| P-7 | [Backup and restore workflows](https://github.com/subhrajit-mohanty/Rudra/issues/61) | M |
| P-9 | [WCAG 2.1 AA audit and fixes for hosted UI](https://github.com/subhrajit-mohanty/Rudra/issues/62) | M |
| P-10 | [i18n harness and first non-English locale](https://github.com/subhrajit-mohanty/Rudra/issues/63) | M |

### Documentation

| ID | Title | Effort |
|---|---|---|
| #3 | [docs: auto-stamp the release version into the published docs](https://github.com/subhrajit-mohanty/Rudra/issues/3) | S |

---

## Explicitly deferred

These ideas were considered and held back deliberately. They do not have issues filed; promote them by writing one.

* **Cross-tenant identity portability (BYO-Identity).** Beautiful network-effect idea. Requires product-market fit first; revisit in year two.
* **Continuous authentication (behavioural biometrics).** High false-positive risk without dedicated ML. Wait for stronger data infrastructure.
* **GraphQL API alongside REST.** OpenAPI gives most of the benefit. Two surfaces to maintain for unclear payoff.

## Working with the roadmap

**For maintainers:**
* Add a feature to v1.2.0 only if it directly advances the quarterly theme. Otherwise file in the backlog.
* Promote a backlog item to the next milestone (v1.3.0) only after v1.2.0 ships.
* Close an issue only when its Acceptance Criteria all tick. No "done enough" closures.

**For contributors:**
* Pick any unassigned issue; comment "I'd like to take this" and a maintainer will assign it.
* Ship on a `dev` branch. Never push directly to `master`; the repo's CI only runs on PRs into `master`.
* The full validation procedure and contribution guidelines live in [CONTRIBUTING.md](CONTRIBUTING.md).
