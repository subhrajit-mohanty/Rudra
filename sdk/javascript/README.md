# @rudra/sdk

Official JavaScript SDK for [Rudra](https://github.com/rudra-auth/rudra) — managed auth platform powered by Keycloak.

## Install

```bash
npm install @rudra/sdk
```

## Quick Start

```javascript
import { RudraClient } from '@rudra/sdk';

const client = new RudraClient('http://localhost:8000');
await client.login('admin@example.com', 'your-password');

// Create a project with coupon
const project = await client.projects.create('My App', 'my-app', 'pro', 'WELCOME50');

// Create a user
const user = await client.users.create('my-app', {
  username: 'janedoe',
  email: 'jane@example.com',
  password: 'securepass123',
  firstName: 'Jane',
  lastName: 'Doe',
});

// List users
const users = await client.users.list('my-app', { search: 'jane' });

// Organizations
const org = await client.organizations.create('my-app', {
  name: 'Acme Corp',
  slug: 'acme-corp',
  allowedEmailDomains: ['acme.com'],
});

// SSO
await client.sso.addOIDC('my-app', {
  alias: 'google',
  providerType: 'google',
  clientId: 'GOOGLE_ID',
  clientSecret: 'GOOGLE_SECRET',
});

// Webhooks
const wh = await client.webhooks.create('my-app',
  'https://my-app.com/webhooks',
  ['user.created', 'organization.created']
);
console.log('Secret:', wh.secret);

// Roles
await client.roles.create('my-app', 'editor', 'Can edit content');
await client.roles.assign('my-app', user.user_id, 'editor');

// Coupons
await client.coupons.create({
  code: 'STARTUP30',
  discountPct: 30,
  maxRedemptions: 100,
  validPlans: ['pro', 'business'],
});

// Analytics
const stats = await client.analytics.summary('my-app');
console.log(`Users: ${stats.total_users}, Logins: ${stats.login_count}`);
```

## Error Handling

```javascript
import { RudraClient, RudraAPIError } from '@rudra/sdk';

try {
  await client.users.create('my-app', { username: 'existing', ... });
} catch (e) {
  if (e instanceof RudraAPIError) {
    console.log(`Error ${e.statusCode}: ${e.detail}`);
  }
}
```

## Resources

| Resource | Methods |
|---|---|
| `client.auth` | `register()`, `login()`, `me()` |
| `client.projects` | `create()`, `list()`, `get()`, `update()`, `delete()`, `updateAuthSettings()`, `updateBranding()` |
| `client.users` | `create()`, `list()`, `get()`, `update()`, `delete()`, `impersonate()` |
| `client.sessions` | `list()`, `revokeAll()`, `revoke()` |
| `client.organizations` | `create()`, `list()`, `addMember()`, `removeMember()`, `delete()`, `invite()`, `listInvitations()` |
| `client.roles` | `create()`, `list()`, `assign()`, `remove()`, `delete()` |
| `client.sso` | `addOIDC()`, `addSAML()`, `list()`, `delete()` |
| `client.clients` | `create()`, `list()`, `delete()` |
| `client.webhooks` | `create()`, `list()`, `logs()`, `delete()` |
| `client.coupons` | `create()`, `list()`, `validate()`, `redemptions()`, `toggle()`, `delete()` |
| `client.analytics` | `summary()`, `events()`, `dashboard()` |

## License

MIT
