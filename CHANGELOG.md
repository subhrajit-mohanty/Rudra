# Changelog

All notable changes to Rudra will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-04-23

### Security

- Bump backend Python dependencies to patched versions flagged by
  `pip-audit` (ten CVEs resolved across `pymongo`, `python-jose`,
  `python-multipart` and `starlette`). `fastapi` goes from 0.109.2 to
  0.129.0, which pulls `starlette>=0.47` and closes CVE-2024-47874 and
  CVE-2025-54121. `python-jose` goes from 3.3.0 to 3.5.0, which allows
  the newer `pyasn1` 0.6.x line that closes CVE-2026-30922.
- Enforce tenant ownership on every realm scoped endpoint. Sixteen routes
  (session revocation, role assignment and removal, user impersonation,
  organization and invitation management, SAML and OIDC identity providers,
  client deletion, webhook creation, listing and deletion) previously
  required only authentication; an authenticated admin could act on any
  other admin's realm. A new `_get_owned_tenant` helper centralizes the
  check and `_check_feature` now routes through it.
- Stop shipping default credentials and a well known `SECRET_KEY` in
  `docker-compose.yml`. Every secret is now read from a local `.env` file
  that is git ignored. The backend fails fast on boot if any required
  variable is missing so an insecure default cannot be deployed by
  accident.
- Expand `.gitignore` to cover `.env`, Python build artefacts, Node
  modules, IDE folders and macOS metadata. Add `.dockerignore` for the
  backend and frontend build contexts so `.env` files and local caches
  cannot leak into images.

### Added

- `.env.example` documenting every required environment variable with
  safe placeholders and inline guidance on how to generate a real
  `SECRET_KEY`.
- `HEALTHCHECK` directives in both backend and frontend Dockerfiles plus
  a compose level healthcheck for the frontend container.
- `frontend/package-lock.json` so `npm ci` produces reproducible builds.
- Seventeen dashboard screenshots under `assets/screenshots/` covering
  sign in, register, empty and populated dashboards, plan picker,
  project configuration and detail, every project tab (Users,
  Applications, SSO, Organizations, Roles, Webhooks, Settings), the
  Coupons list, the create coupon modal, and the global dashboard
  after a Pro project has been fully seeded. Linked from the README, a
  new `docs/screenshots.md` tour page and a new Screenshots section in
  `docs/docs.html`.
- First pytest suite under `tests/`, split into `tests/unit/` (pure
  function coverage for password hashing, JWT handling, the `_required`
  env helper and Pydantic request models) and `tests/integration/`
  (FastAPI TestClient against real MongoDB with Keycloak mocked,
  covering the health surface, the register and login flow, and tenant
  isolation regression tests that prove a second admin cannot access
  another admin's realm).
- CI jobs `Unit Tests` and `Integration Tests` (the latter with a
  `mongo:7` GitHub Actions service container) that must pass before a
  PR into `main` can be merged, plus a `Dependency Security Audit` job
  that runs `pip-audit` and `npm audit`.
- Top level `permissions: contents: read` and a `concurrency:` group
  on the CI workflow so the default `GITHUB_TOKEN` is read only and
  rapid pushes cancel in flight runs.
- `CHANGELOG.md`.

### Changed

- Backend Dockerfile now runs uvicorn as a dedicated non root `rudra`
  system user instead of root.
- Frontend Dockerfile switched from `npm install` to `npm ci` to pin
  against the committed lockfile.
- README quick start now instructs contributors to copy `.env.example`
  to `.env` before running `docker compose up`, and the service
  credentials table references the real environment variable names
  rather than the removed `admin / admin` defaults.

### Removed

- Dropped the obsolete top level `version: '3.9'` key from
  `docker-compose.yml`. Docker Compose V2 ignores it and prints a
  deprecation warning on every invocation when it is present.

## [1.0.1] - 2026-02-10

### Changed

- Bumped package version to 1.0.1.
- Refreshed the project banner SVG rendered at the top of the README.

### Added

- New SVG banner asset (`assets/banner.svg`) referenced from the README.

## [1.0.0] - 2026-02-10

Initial public release of Rudra, an open source managed authentication
platform built on Keycloak.

### Added

- FastAPI backend exposing 50+ endpoints covering authentication,
  tenants (Keycloak realms), users, sessions, organizations, invitations,
  roles, identity providers (OIDC and SAML), clients, webhooks, coupons
  and analytics.
- React plus Vite dashboard for managing projects, users, organizations,
  roles, webhooks, SSO and coupons, served by nginx in production.
- Python SDK (`rudra_sdk`) and JavaScript SDK (`@rudra/sdk`) with
  matching resource namespaces for projects, users, organizations,
  roles, SSO, webhooks, coupons and analytics.
- Six service Docker Compose stack (Postgres, MongoDB, Redis, Keycloak,
  backend, frontend) with healthchecks on the data stores and Keycloak.
- Plan tiers (Free, Pro, Business, Enterprise) with per plan feature
  gating for SAML connections, organizations, webhooks, analytics,
  impersonation, bot protection, password breach detection and
  disposable email blocking.
- GitHub Actions CI covering ruff lint, Python syntax validation,
  frontend build, Docker image build and SDK import checks for both
  Python and JavaScript.
- Light themed standalone documentation (`docs.html`) and contribution
  guide (`CONTRIBUTING.md`).
- MIT license.

[Unreleased]: https://github.com/rudra-auth/rudra/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/rudra-auth/rudra/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/rudra-auth/rudra/compare/v1.0...v1.0.1
[1.0.0]: https://github.com/rudra-auth/rudra/releases/tag/v1.0
