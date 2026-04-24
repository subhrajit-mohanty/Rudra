# Rudra Roadmap

This is the living product roadmap for Rudra, organised into four release milestones. Every bullet below is a real GitHub issue with acceptance criteria, technical approach, dependencies, and references — pick up any one and ship.

The current released version is **1.1.0** (April 2026). This roadmap covers four quarterly releases beyond that.

## How to read this document

* Four milestones, each mapped to a semver release and a calendar target.
* Each milestone is grouped by tier so contributors can pick work that matches their interest: foundation plumbing, auth primitives, AI-native features, enterprise, developer experience, polish.
* Every feature has a short identifier (e.g. `A-1`, `FND-10`) and a matching GitHub issue with full detail.
* Effort markers: **S** under a week, **M** one to three weeks, **L** over a month, **XL** over a quarter.
* Priority markers: **P0** (ship first), **P1** (early), **P2** (later), **P3** (defer if tight).

## Where to look first

* Browse by milestone: [Milestones](https://github.com/subhrajit-mohanty/Rudra/milestones).
* Filter by tier: [tier:foundation](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Afoundation), [tier:auth](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Aauth), [tier:ai-native](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Aai-native), [tier:enterprise](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Aenterprise), [tier:devex](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Adevex), [tier:novel](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Anovel), [tier:polish](https://github.com/subhrajit-mohanty/Rudra/labels/tier%3Apolish).
* Filter by priority: [priority:p0-critical](https://github.com/subhrajit-mohanty/Rudra/labels/priority%3Ap0-critical), [priority:p1-high](https://github.com/subhrajit-mohanty/Rudra/labels/priority%3Ap1-high).
* Good first issues: effort `S` items tagged with `priority:p2-medium` or lower are the easiest starting points.

---

## v1.2.0 — Foundation and first-hour wins

**Target:** 2026-07-15 · **Milestone:** [v1.2.0](https://github.com/subhrajit-mohanty/Rudra/milestone/1)

**Theme:** every feature the product advertises actually works, observability is live, and the complaints a developer voices in their first hour are gone.

### Security and trust (7 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| FND-10 | [Reconcile pyproject.toml with backend/requirements.txt](https://github.com/subhrajit-mohanty/Rudra/issues/4) | S | P0 |
| FND-3 | [Enforce per-tenant api_rate_limit using Redis](https://github.com/subhrajit-mohanty/Rudra/issues/5) | S | P0 |
| FND-5 | [Wire MFA toggle through to Keycloak required-actions](https://github.com/subhrajit-mohanty/Rudra/issues/6) | S | P0 |
| FND-6 | [Implement password breach detection via HIBP](https://github.com/subhrajit-mohanty/Rudra/issues/7) | S | P0 |
| FND-7 | [Implement bot protection via Cloudflare Turnstile](https://github.com/subhrajit-mohanty/Rudra/issues/8) | S | P0 |
| FND-8 | [HMAC-SHA256 signatures for webhook deliveries](https://github.com/subhrajit-mohanty/Rudra/issues/9) | S | P0 |
| FND-9 | [Migrate remaining 25 endpoints to _get_owned_tenant helper](https://github.com/subhrajit-mohanty/Rudra/issues/10) | S | P1 |

### Scale and ops hygiene (4 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| FND-1 | [Cache Keycloak admin token in Redis](https://github.com/subhrajit-mohanty/Rudra/issues/11) | S | P0 |
| FND-2 | [Share a single httpx.AsyncClient with connection pooling](https://github.com/subhrajit-mohanty/Rudra/issues/12) | S | P0 |
| FND-11 | [Real /api/health that checks Mongo, Keycloak, Redis](https://github.com/subhrajit-mohanty/Rudra/issues/13) | S | P1 |
| FND-4 | [Background queue for webhook delivery with retries and DLQ](https://github.com/subhrajit-mohanty/Rudra/issues/14) | M | P1 |
| FND-12 | [Prometheus metrics and OpenTelemetry tracing](https://github.com/subhrajit-mohanty/Rudra/issues/15) | M | P1 |

### Developer first-hour (3 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| D-5 | [Publish auto-generated OpenAPI spec and versioned releases](https://github.com/subhrajit-mohanty/Rudra/issues/16) | S | P1 |
| D-6 | [Webhook replay in dashboard and local tunnel in CLI](https://github.com/subhrajit-mohanty/Rudra/issues/17) | S | P2 |
| P-1 | [In-dashboard email template editor with live preview](https://github.com/subhrajit-mohanty/Rudra/issues/18) | S | P2 |

---

## v1.3.0 — Hosted components and enterprise unlock

**Target:** 2026-10-15 · **Milestone:** [v1.3.0](https://github.com/subhrajit-mohanty/Rudra/milestone/2)

**Theme:** drop-in React components turn a three-day integration into thirty minutes. First F500 RFPs close. Modern auth primitives (passkeys, step-up, account linking, OTP, MFA recovery) all ship.

### Modern auth primitives (6 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| A-1 | [Passkeys / WebAuthn support](https://github.com/subhrajit-mohanty/Rudra/issues/19) | M | P1 |
| A-3 | [Account linking across password, social and passkeys](https://github.com/subhrajit-mohanty/Rudra/issues/20) | M | P1 |
| A-4 | [Step-up authentication for sensitive operations](https://github.com/subhrajit-mohanty/Rudra/issues/21) | S | P1 |
| A-8 | [Email OTP and SMS OTP as alternatives to magic links](https://github.com/subhrajit-mohanty/Rudra/issues/22) | S | P1 |
| A-11 | [MFA recovery flows (backup codes, recovery email, admin unlock)](https://github.com/subhrajit-mohanty/Rudra/issues/23) | S | P1 |
| A-12 | [Service account tokens for CI/CD and server-to-server](https://github.com/subhrajit-mohanty/Rudra/issues/24) | S | P2 |

### Integration friction (3 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| A-2 | [Hosted UI components (<SignIn />, <UserButton />, ...)](https://github.com/subhrajit-mohanty/Rudra/issues/25) | XL | P1 |
| A-10 | [Framework SDKs (rudra-fastapi, rudra-django, rudra-nextjs, rudra-express)](https://github.com/subhrajit-mohanty/Rudra/issues/26) | M | P2 |
| D-1 | [rudra CLI for login, resource management, logs, webhook tunnel](https://github.com/subhrajit-mohanty/Rudra/issues/27) | M | P2 |

### Enterprise unlock (5 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| C-1 | [SCIM 2.0 provisioning endpoint](https://github.com/subhrajit-mohanty/Rudra/issues/28) | M | P1 |
| C-2 | [Organization-level SSO (per-org IdP routing by email domain)](https://github.com/subhrajit-mohanty/Rudra/issues/29) | M | P1 |
| C-4 | [Audit log streaming to S3, Datadog, Splunk, OCSF](https://github.com/subhrajit-mohanty/Rudra/issues/30) | M | P1 |
| C-5 | [Immutable tamper-evident audit logs (hash-chained)](https://github.com/subhrajit-mohanty/Rudra/issues/31) | S | P2 |
| C-10 | [IP allowlisting and geo-fencing per tenant](https://github.com/subhrajit-mohanty/Rudra/issues/32) | S | P2 |

### Rollout machinery (2 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| E-5 | [Per-tenant feature flags](https://github.com/subhrajit-mohanty/Rudra/issues/33) | S | P1 |
| C-9 | [GDPR data subject access requests (export and deletion)](https://github.com/subhrajit-mohanty/Rudra/issues/34) | S | P2 |

---

## v2.0.0 — AI-native differentiation

**Target:** 2027-01-15 · **Milestone:** [v2.0.0](https://github.com/subhrajit-mohanty/Rudra/milestone/3)

**Theme:** plant the 2026 flag that no open-source auth product has planted yet. Agent identity, MCP OAuth, policy assistant, explainable risk. The pitch moves from "open-source Clerk" to "first auth platform built for the agent era."

### Authorization foundation (2 items, build first in the quarter)

| ID | Title | Effort | Priority |
|---|---|---|---|
| A-7 | [Fine-grained authorization (ReBAC) with POST /api/check](https://github.com/subhrajit-mohanty/Rudra/issues/35) | L | P0 |
| A-5 | [Adaptive risk-based authentication](https://github.com/subhrajit-mohanty/Rudra/issues/36) | M | P0 |

### Agent primitives (5 items, on top of A-7)

| ID | Title | Effort | Priority |
|---|---|---|---|
| B-1 | [Agents as first-class principals](https://github.com/subhrajit-mohanty/Rudra/issues/37) | M | P0 |
| B-2 | [OAuth 2.0 authorization server for MCP servers](https://github.com/subhrajit-mohanty/Rudra/issues/38) | L | P1 |
| B-3 | [Human-in-the-loop approval workflows](https://github.com/subhrajit-mohanty/Rudra/issues/39) | M | P1 |
| B-4 | [Per-tool scoped tokens with minute-level expiry](https://github.com/subhrajit-mohanty/Rudra/issues/40) | M | P1 |
| B-5 | [Agent audit log with intent capture](https://github.com/subhrajit-mohanty/Rudra/issues/41) | S | P2 |

### AI features (3 items, on top of ReBAC and adaptive auth)

| ID | Title | Effort | Priority |
|---|---|---|---|
| B-6 | [AI policy assistant — natural language to ReBAC](https://github.com/subhrajit-mohanty/Rudra/issues/42) | M | P2 |
| B-7 | [Natural-language audit log queries](https://github.com/subhrajit-mohanty/Rudra/issues/43) | M | P2 |
| B-8 | [Explainable risk score UI](https://github.com/subhrajit-mohanty/Rudra/issues/44) | S | P2 |

### Platform polish (4 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| A-6 | [Custom domains per tenant](https://github.com/subhrajit-mohanty/Rudra/issues/45) | L | P1 |
| D-2 | [Terraform provider and Helm chart](https://github.com/subhrajit-mohanty/Rudra/issues/46) | M | P2 |
| D-7 | [Auth flow playground in the dashboard](https://github.com/subhrajit-mohanty/Rudra/issues/47) | M | P2 |
| D-8 | [Self-service diagnostic dump](https://github.com/subhrajit-mohanty/Rudra/issues/48) | S | P3 |

---

## v2.1.0 — Compliance, commercial, scale

**Target:** 2027-04-15 · **Milestone:** [v2.1.0](https://github.com/subhrajit-mohanty/Rudra/milestone/4)

**Theme:** move from "startups love it" to "enterprises standardise on it." Compliance packs, BYOK, data residency start, Stripe billing, additional language SDKs, migration tools, a11y and i18n.

### Compliance (3 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| C-7 | [Customer-managed encryption keys (BYOK) for PII](https://github.com/subhrajit-mohanty/Rudra/issues/49) | M | P1 |
| C-8 | [Compliance pack (SOC 2 / GDPR / HIPAA preset)](https://github.com/subhrajit-mohanty/Rudra/issues/50) | M | P1 |
| C-6 | [Data residency in US / EU / APAC (start)](https://github.com/subhrajit-mohanty/Rudra/issues/51) | XL | P1 |

### Commercial (4 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| E-4 | [Stripe-backed metered billing for plans and MAU](https://github.com/subhrajit-mohanty/Rudra/issues/52) | M | P1 |
| E-3 | [Consent ledger with user-facing receipts](https://github.com/subhrajit-mohanty/Rudra/issues/53) | M | P2 |
| C-3 | [Organization hierarchies (parent / child orgs)](https://github.com/subhrajit-mohanty/Rudra/issues/54) | M | P2 |
| C-11 | [Organization-scoped API keys](https://github.com/subhrajit-mohanty/Rudra/issues/55) | M | P2 |
| C-12 | [Dark web monitoring for tenant user credentials](https://github.com/subhrajit-mohanty/Rudra/issues/56) | S | P2 |

### Scale and developer breadth (5 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| D-4 | [Additional SDKs: Go, Java, Ruby, .NET, PHP](https://github.com/subhrajit-mohanty/Rudra/issues/57) | L | P1 |
| D-3 | [Migration tools from Auth0, Clerk, Firebase](https://github.com/subhrajit-mohanty/Rudra/issues/58) | L | P2 |
| D-9 | [Visual workflow builder for auth flows](https://github.com/subhrajit-mohanty/Rudra/issues/59) | L | P3 |
| P-6 | [Read replicas and per-tenant Mongo sharding](https://github.com/subhrajit-mohanty/Rudra/issues/60) | L | P2 |
| P-7 | [Backup and restore workflows](https://github.com/subhrajit-mohanty/Rudra/issues/61) | M | P2 |

### Accessibility, i18n, real-time (3 items)

| ID | Title | Effort | Priority |
|---|---|---|---|
| P-9 | [WCAG 2.1 AA audit and fixes for hosted UI](https://github.com/subhrajit-mohanty/Rudra/issues/62) | M | P2 |
| P-10 | [i18n harness and first non-English locale](https://github.com/subhrajit-mohanty/Rudra/issues/63) | M | P2 |
| P-5 | [Real-time dashboard updates via WebSockets](https://github.com/subhrajit-mohanty/Rudra/issues/64) | S | P3 |

---

## Explicitly deferred

A few ideas considered but deliberately held back:

* **Cross-tenant identity portability (BYO-Identity).** Beautiful network-effect idea. Requires product-market fit first; revisit in year two.
* **Continuous authentication (behavioural biometrics).** High false-positive risk without dedicated ML. Wait for stronger data infrastructure.
* **GraphQL API alongside REST.** OpenAPI gives most of the benefit. Two surfaces to maintain for unclear payoff.
* **China / Russia data residency regions.** Different regulatory animal; covered by acknowledging the issue, deferred on scope.
* **Full SOC 2 Type II audit certification.** The compliance pack (C-8) prepares the tenant; the actual audit is a customer-side exercise for now.

## Working with the roadmap

**For maintainers:**
* Add a feature to an existing milestone before adding a new milestone.
* Keep milestones date-bound and under a quarter of real work.
* Close an issue only when its Acceptance Criteria all tick. No "done enough" closures.

**For contributors:**
* Pick any unassigned issue; comment "I'd like to take this" and a maintainer will assign it.
* Ship on a `dev` branch. Never push directly to `master`; the repo's CI only runs on PRs into `master`.
* The full validation procedure and contribution guidelines live in [CONTRIBUTING.md](CONTRIBUTING.md).

## Setting up a Projects v2 board (optional)

The roadmap above is fully navigable via milestones and labels without a Projects v2 board. If you want a kanban-style view, create one manually (one-time setup, approximately 5 minutes):

1. Go to https://github.com/users/subhrajit-mohanty/projects and click **New project** → **Board**.
2. Name: "Rudra Roadmap".
3. Add fields: `Quarter` (single select: v1.2.0, v1.3.0, v2.0.0, v2.1.0), `Tier` (from the tier labels), `Priority` (P0–P3), `Effort` (S/M/L/XL).
4. Add existing issues: **+ Add item** → filter `is:issue milestone:v1.2.0` and bulk add. Repeat per milestone.
5. Create views: Kanban by Status, Roadmap by Quarter, Table all-in.
6. Done.

If Projects v2 CLI scope becomes useful, `gh auth refresh -s project` opens a browser and grants the scope; a future issue can automate board creation via `gh project create`.
