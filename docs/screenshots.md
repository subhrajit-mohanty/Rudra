# Product tour

A walkthrough of the Rudra dashboard captured against a clean
`docker compose up` against commit on `dev`. Every shot is 1440x900.

## 1. Sign in

![Login page](../assets/screenshots/01-login.png)

The dashboard is a React SPA served by nginx on port 3000. Unauthenticated
traffic is redirected to `/login`.

## 2. Create an admin account

![Register page](../assets/screenshots/02-register.png)

Registration hits `POST /api/auth/register` on the FastAPI backend, which
hashes the password with PBKDF2-SHA256 (260k iterations) before persisting
the record in MongoDB, then returns a 24 hour JWT.

## 3. Empty dashboard

![Empty dashboard](../assets/screenshots/03-dashboard-empty.png)

Immediately after sign up there are no projects, users, applications or
organizations. The activity feed records the account creation event.

## 4. Pick a plan

![Plan picker](../assets/screenshots/04-plans.png)

Projects are plan scoped. The free tier caps users, projects and
organizations; the Pro, Business and Enterprise tiers unlock SAML,
webhooks, analytics, impersonation and breach detection. Plan data comes
from `GET /api/plans`.

## 5. Configure the project

![Project form](../assets/screenshots/05-project-form.png)

Pick a human name and a realm identifier (used as the Keycloak realm
slug). A coupon code can be attached here to apply a discount on the base
plan.

## 6. Project detail

![Project detail](../assets/screenshots/06-project-detail.png)

`POST /api/tenants` creates the Keycloak realm and the Mongo tenant row
in a single transaction. The project detail page surfaces eight tabs
(Overview, Users, Applications, SSO, Organizations, Roles, Webhooks,
Settings), live user and login counts from Keycloak events, and the
direct Keycloak URL for the realm.

## 7. Populated dashboard

![Populated dashboard](../assets/screenshots/07-dashboard-populated.png)

Back on the global dashboard the stats roll up across every project the
admin owns. Plan distribution, per project headcount and recent activity
are computed by the backend from MongoDB and Keycloak admin events.

## 8. Users tab

![Project users](../assets/screenshots/08-project-users.png)

Search, inspect, assign roles, revoke sessions and delete end users.
Each row comes directly from the Keycloak user store for the realm, so
the dashboard is always the source of truth rather than a cached copy.

## 9. Applications tab

![Project applications](../assets/screenshots/09-project-applications.png)

Register OIDC and SAML applications (Keycloak clients) that will
authenticate against this realm. The table shows client id, protocol,
public flag and quick delete.

## 10. SSO tab

![Project SSO](../assets/screenshots/10-project-sso.png)

Add social (Google, GitHub, Facebook), generic OIDC or SAML identity
providers. SAML is gated behind the Business plan; the free and Pro
tiers ship the OIDC path only.

## 11. Organizations tab

![Project organizations](../assets/screenshots/11-project-organizations.png)

B2B organizations with domain based auto join, members and
invitations. Each organization is backed by a Keycloak group so
permissions flow through the realm's RBAC model.

## 12. Roles tab

![Project roles](../assets/screenshots/12-project-roles.png)

Custom RBAC roles, mapped into the user's JWT tokens on login. Pair
these with your application's authorization layer.

## 13. Webhooks tab

![Project webhooks](../assets/screenshots/13-project-webhooks.png)

Register endpoints to receive real time events (`user.created`,
`user.deleted`, `organization.created` and so on). Each delivery is
logged with status code and response body so failures can be retried
or debugged.

## 14. Settings tab

![Project settings](../assets/screenshots/14-project-settings.png)

Per project toggles for the authentication stack: password auth,
social login, magic links, MFA, disposable email blocking, password
breach detection and bot protection. Branding lives below this block.

## 15. Coupons list

![Coupons list](../assets/screenshots/15-coupons-list.png)

All active coupons with code, discount, description, plan scope,
redemption count, limit and status. Toggling a coupon from active to
disabled is a one click action; redemption history is one click away.

## 16. Create coupon modal

![Create coupon modal](../assets/screenshots/16-coupon-create-modal.png)

Create a coupon with percent discount, redemption cap, plan scope and
expiry. The code is normalized to uppercase before it hits the API.

## 17. Dashboard after seeding a Pro project

![Dashboard populated with a Pro project](../assets/screenshots/17-dashboard-pro-project.png)

Once a Pro project has users, applications, organizations, roles,
webhooks and coupons attached, the dashboard rolls everything up: plan
distribution, total users and applications, and a detailed activity
feed across every project the admin owns.
