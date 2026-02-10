/**
 * Rudra JavaScript SDK
 * ====================
 *
 * Connect your JavaScript/Node.js application to Rudra Auth Platform.
 *
 * Usage:
 *   import { RudraClient } from '@rudra/sdk';
 *   const client = new RudraClient('http://localhost:8000');
 *   await client.login('admin@example.com', 'password');
 *   const users = await client.users.list('my-realm');
 */

class RudraAPIError extends Error {
  constructor(statusCode, detail) {
    super(`[${statusCode}] ${detail}`);
    this.name = 'RudraAPIError';
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

class BaseResource {
  constructor(client) { this._client = client; }
  _request(method, path, opts) { return this._client._request(method, path, opts); }
}

class AuthResource extends BaseResource {
  register(email, password, name, company = '') {
    return this._request('POST', '/auth/register', { body: { email, password, name, company } });
  }
  login(email, password) {
    return this._request('POST', '/auth/login', { body: { email, password } });
  }
  me() { return this._request('GET', '/auth/me'); }
}

class ProjectResource extends BaseResource {
  create(name, realmName, plan = 'free', couponCode = '') {
    const body = { name, realm_name: realmName, plan };
    if (couponCode) body.coupon_code = couponCode;
    return this._request('POST', '/tenants', { body });
  }
  list() { return this._request('GET', '/tenants'); }
  get(realm) { return this._request('GET', `/tenants/${realm}`); }
  update(realm, updates) { return this._request('PUT', `/tenants/${realm}`, { body: updates }); }
  delete(realm) { return this._request('DELETE', `/tenants/${realm}`); }
  updateAuthSettings(realm, settings) {
    return this._request('PUT', `/tenants/${realm}/auth-settings`, { body: settings });
  }
  updateBranding(realm, branding) {
    return this._request('PUT', `/tenants/${realm}/branding`, { body: branding });
  }
}

class UserResource extends BaseResource {
  create(realm, { username, email, password, firstName = '', lastName = '', metadata = null }) {
    const body = { username, email, password, first_name: firstName, last_name: lastName };
    if (metadata) body.metadata = metadata;
    return this._request('POST', `/tenants/${realm}/users`, { body });
  }
  list(realm, { search, first = 0, max = 50 } = {}) {
    const params = { first, max };
    if (search) params.search = search;
    return this._request('GET', `/tenants/${realm}/users`, { params });
  }
  get(realm, userId) { return this._request('GET', `/tenants/${realm}/users/${userId}`); }
  update(realm, userId, updates) {
    return this._request('PUT', `/tenants/${realm}/users/${userId}`, { body: updates });
  }
  delete(realm, userId) { return this._request('DELETE', `/tenants/${realm}/users/${userId}`); }
  impersonate(realm, userId) {
    return this._request('POST', `/tenants/${realm}/users/${userId}/impersonate`);
  }
}

class SessionResource extends BaseResource {
  list(realm, userId) { return this._request('GET', `/tenants/${realm}/users/${userId}/sessions`); }
  revokeAll(realm, userId) { return this._request('DELETE', `/tenants/${realm}/users/${userId}/sessions`); }
  revoke(realm, sessionId) { return this._request('DELETE', `/tenants/${realm}/sessions/${sessionId}`); }
}

class OrganizationResource extends BaseResource {
  create(realm, { name, slug, allowedEmailDomains = [] }) {
    return this._request('POST', `/tenants/${realm}/organizations`, {
      body: { name, slug, allowed_email_domains: allowedEmailDomains }
    });
  }
  list(realm) { return this._request('GET', `/tenants/${realm}/organizations`); }
  addMember(realm, slug, userId, role = 'member') {
    return this._request('POST', `/tenants/${realm}/organizations/${slug}/members`, {
      body: { user_id: userId, role }
    });
  }
  removeMember(realm, slug, userId) {
    return this._request('DELETE', `/tenants/${realm}/organizations/${slug}/members/${userId}`);
  }
  delete(realm, slug) { return this._request('DELETE', `/tenants/${realm}/organizations/${slug}`); }
  invite(realm, email, orgSlug = null, role = 'member') {
    return this._request('POST', `/tenants/${realm}/invitations`, {
      body: { email, org_slug: orgSlug, role }
    });
  }
  listInvitations(realm) { return this._request('GET', `/tenants/${realm}/invitations`); }
}

class RoleResource extends BaseResource {
  create(realm, name, description = '') {
    return this._request('POST', `/tenants/${realm}/roles`, { body: { name, description } });
  }
  list(realm) { return this._request('GET', `/tenants/${realm}/roles`); }
  assign(realm, userId, roleName) {
    return this._request('POST', `/tenants/${realm}/users/${userId}/roles/${roleName}`);
  }
  remove(realm, userId, roleName) {
    return this._request('DELETE', `/tenants/${realm}/users/${userId}/roles/${roleName}`);
  }
  delete(realm, roleName) { return this._request('DELETE', `/tenants/${realm}/roles/${roleName}`); }
}

class SSOResource extends BaseResource {
  addOIDC(realm, { alias, providerType = 'google', clientId, clientSecret, authorizationUrl = '', tokenUrl = '' }) {
    return this._request('POST', `/tenants/${realm}/idp/oidc`, {
      body: { alias, provider_type: providerType, client_id: clientId, client_secret: clientSecret,
              authorization_url: authorizationUrl, token_url: tokenUrl }
    });
  }
  addSAML(realm, { alias, entityId, ssoUrl, signingCertificate = '' }) {
    return this._request('POST', `/tenants/${realm}/idp/saml`, {
      body: { alias, entity_id: entityId, sso_url: ssoUrl, signing_certificate: signingCertificate }
    });
  }
  list(realm) { return this._request('GET', `/tenants/${realm}/idp`); }
  delete(realm, alias) { return this._request('DELETE', `/tenants/${realm}/idp/${alias}`); }
}

class ClientResource extends BaseResource {
  create(realm, clientId, redirectUris = ['http://localhost:*'], protocol = 'openid-connect') {
    return this._request('POST', `/tenants/${realm}/clients`, {
      body: { client_id: clientId, redirect_uris: redirectUris, protocol }
    });
  }
  list(realm) { return this._request('GET', `/tenants/${realm}/clients`); }
  delete(realm, kcId) { return this._request('DELETE', `/tenants/${realm}/clients/${kcId}`); }
}

class WebhookResource extends BaseResource {
  create(realm, url, events) {
    return this._request('POST', `/tenants/${realm}/webhooks`, { body: { url, events } });
  }
  list(realm) { return this._request('GET', `/tenants/${realm}/webhooks`); }
  logs(realm, webhookId) { return this._request('GET', `/tenants/${realm}/webhooks/${webhookId}/logs`); }
  delete(realm, webhookId) { return this._request('DELETE', `/tenants/${realm}/webhooks/${webhookId}`); }
}

class CouponResource extends BaseResource {
  create({ code, discountPct, description = '', maxRedemptions = -1, validPlans = [], durationDays = 0 }) {
    return this._request('POST', '/coupons', {
      body: { code, discount_pct: discountPct, description, max_redemptions: maxRedemptions,
              valid_plans: validPlans, duration_days: durationDays }
    });
  }
  list() { return this._request('GET', '/coupons'); }
  validate(code, plan = '') { return this._request('POST', '/coupons/validate', { body: { code, plan } }); }
  redemptions(code) { return this._request('GET', `/coupons/${code}/redemptions`); }
  toggle(code) { return this._request('PUT', `/coupons/${code}/toggle`); }
  delete(code) { return this._request('DELETE', `/coupons/${code}`); }
}

class AnalyticsResource extends BaseResource {
  summary(realm, days = 30) { return this._request('GET', `/tenants/${realm}/analytics`, { params: { days } }); }
  events(realm, { eventType, max = 50 } = {}) {
    const params = { max };
    if (eventType) params.event_type = eventType;
    return this._request('GET', `/tenants/${realm}/events`, { params });
  }
  dashboard() { return this._request('GET', '/dashboard'); }
}


class RudraClient {
  /**
   * @param {string} baseUrl - Rudra API URL (e.g. "http://localhost:8000")
   * @param {object} opts
   * @param {string} [opts.token] - Pre-existing JWT token
   */
  constructor(baseUrl, opts = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this._token = opts.token || null;

    this.auth = new AuthResource(this);
    this.projects = new ProjectResource(this);
    this.users = new UserResource(this);
    this.sessions = new SessionResource(this);
    this.organizations = new OrganizationResource(this);
    this.roles = new RoleResource(this);
    this.sso = new SSOResource(this);
    this.clients = new ClientResource(this);
    this.webhooks = new WebhookResource(this);
    this.coupons = new CouponResource(this);
    this.analytics = new AnalyticsResource(this);
  }

  async login(email, password) {
    const resp = await this._request('POST', '/auth/login', { body: { email, password } });
    this._token = resp.token;
    return resp;
  }

  get token() { return this._token; }

  async _request(method, path, { body, params } = {}) {
    let url = `${this.baseUrl}/api${path}`;
    if (params) {
      const qs = new URLSearchParams(params).toString();
      if (qs) url += `?${qs}`;
    }

    const headers = { 'Content-Type': 'application/json' };
    if (this._token) headers['Authorization'] = `Bearer ${this._token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(url, opts);
    const text = await res.text();

    let data;
    try { data = JSON.parse(text); } catch {
      if (!res.ok) throw new RudraAPIError(res.status, text.substring(0, 200));
      return text;
    }

    if (!res.ok) {
      const detail = data.detail || data.message || JSON.stringify(data);
      throw new RudraAPIError(res.status, detail);
    }
    return data;
  }

  health() { return this._request('GET', '/health'); }
  plans() { return this._request('GET', '/plans'); }
}

export { RudraClient, RudraAPIError };
