import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import Modal from '../components/Modal';
import { Users, AppWindow, Shield, Building2, Webhook, Settings, BarChart3, Key, UserCog, Trash2, Eye, LogOut, UserPlus, Plus } from 'lucide-react';

const TABS = [
  { id:'overview', label:'Overview', icon:<BarChart3 size={15}/> },
  { id:'users', label:'Users', icon:<Users size={15}/> },
  { id:'clients', label:'Applications', icon:<AppWindow size={15}/> },
  { id:'sso', label:'SSO', icon:<Key size={15}/> },
  { id:'orgs', label:'Organizations', icon:<Building2 size={15}/> },
  { id:'roles', label:'Roles', icon:<Shield size={15}/> },
  { id:'webhooks', label:'Webhooks', icon:<Webhook size={15}/> },
  { id:'settings', label:'Settings', icon:<Settings size={15}/> },
];

export default function ProjectDetailPage() {
  const { realm } = useParams();
  const nav = useNavigate();
  const [tenant, setTenant] = useState(null);
  const [tab, setTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [clients, setClients] = useState([]);
  const [idps, setIdps] = useState([]);
  const [orgs, setOrgs] = useState([]);
  const [roles, setRoles] = useState([]);
  const [webhooks, setWebhooks] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    try { const t = await api.get(`/tenants/${realm}`); setTenant(t); } catch { nav('/projects'); }
  }, [realm, nav]);

  const loadTab = useCallback(async () => {
    try {
      if (tab === 'users') setUsers(await api.get(`/tenants/${realm}/users${search?`?search=${search}`:''}`));
      if (tab === 'clients') setClients(await api.get(`/tenants/${realm}/clients`));
      if (tab === 'sso') setIdps(await api.get(`/tenants/${realm}/idp`));
      if (tab === 'orgs') { setOrgs(await api.get(`/tenants/${realm}/organizations`)); setInvitations(await api.get(`/tenants/${realm}/invitations`)); }
      if (tab === 'roles') setRoles(await api.get(`/tenants/${realm}/roles`));
      if (tab === 'webhooks') setWebhooks(await api.get(`/tenants/${realm}/webhooks`));
      if (tab === 'overview') { try { setAnalytics(await api.get(`/tenants/${realm}/analytics`)); } catch {} }
    } catch(e) { console.error(e); }
  }, [realm, tab, search]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { if(tenant) loadTab(); }, [tenant, loadTab]);

  const sf = (k, v) => setForm(p => ({...p, [k]: v}));
  const closeModal = () => { setModal(null); setForm({}); setError(''); };

  const exec = async (fn) => { setError(''); try { await fn(); closeModal(); load(); loadTab(); } catch(e) { setError(e.message); } };

  if (!tenant) return <div className="text-muted" style={{padding:40}}>Loading...</div>;
  const pc = tenant.plan_config || {};

  // ── User Detail View ──
  const viewUser = async (uid) => {
    const u = await api.get(`/tenants/${realm}/users/${uid}`);
    setSelectedUser(u);
    setModal('user-detail');
  };

  return (
    <div>
      <div className="breadcrumb"><a href="/projects">Projects</a><span>/</span>{tenant.name}</div>
      <div className="page-header">
        <div><h1>{tenant.name}</h1><p className="text-sm text-muted" style={{fontFamily:'var(--font-mono)'}}>{realm}</p></div>
        <div className="flex gap-2 items-center">
          <span className={`badge badge-${tenant.plan}`}>{tenant.plan}</span>
        </div>
      </div>

      <div className="tabs">
        {TABS.map(t => <div key={t.id} className={`tab ${tab===t.id?'active':''}`} onClick={() => setTab(t.id)}>{t.icon} {t.label}</div>)}
      </div>

      {/* ═══ OVERVIEW ═══ */}
      {tab === 'overview' && (
        <>
          <div className="stat-grid">
            <div className="stat-card"><div className="label">Users</div><div className="value" style={{color:'#5b5bf0'}}>{tenant.user_count}</div><div className="text-sm text-muted">{pc.max_users===-1?'Unlimited':`Limit: ${pc.max_users?.toLocaleString()}`}</div></div>
            <div className="stat-card"><div className="label">Applications</div><div className="value" style={{color:'#34d399'}}>{tenant.client_count}</div></div>
            <div className="stat-card"><div className="label">SSO Providers</div><div className="value" style={{color:'#fbbf24'}}>{tenant.idp_count}</div></div>
            <div className="stat-card"><div className="label">Organizations</div><div className="value" style={{color:'#f87171'}}>{tenant.org_count}</div></div>
            <div className="stat-card"><div className="label">Roles</div><div className="value" style={{color:'#60a5fa'}}>{tenant.role_count}</div></div>
            <div className="stat-card"><div className="label">Webhooks</div><div className="value" style={{color:'#a78bfa'}}>{tenant.webhook_count}</div></div>
          </div>
          {analytics && (
            <div className="section">
              <h3><BarChart3 size={18}/> Analytics</h3>
              <div className="grid-2">
                <div><div className="text-sm text-muted">Logins (recent)</div><div style={{fontSize:24,fontWeight:700,fontFamily:'var(--font-mono)'}}>{analytics.login_count}</div></div>
                <div><div className="text-sm text-muted">Failed Logins</div><div style={{fontSize:24,fontWeight:700,fontFamily:'var(--font-mono)',color:'var(--danger)'}}>{analytics.failed_login_count}</div></div>
              </div>
              {analytics.user_signups_daily?.length > 0 && (
                <div className="mt-4">
                  <div className="text-sm text-muted mb-4">User Signups (last 30 days)</div>
                  <div className="flex gap-2" style={{alignItems:'flex-end',height:80}}>
                    {analytics.user_signups_daily.map((d, i) => (
                      <div key={i} title={`${d._id}: ${d.count}`} style={{flex:1,background:'var(--accent)',borderRadius:2,minHeight:4,height:`${Math.max(10,d.count*20)}px`,maxHeight:80}}/>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <div className="section">
            <h3>Quick Links</h3>
            <div className="text-sm"><strong>Keycloak URL:</strong> <a href={tenant.keycloak_url} target="_blank" rel="noreferrer" style={{fontFamily:'var(--font-mono)'}}>{tenant.keycloak_url}</a></div>
          </div>
        </>
      )}

      {/* ═══ USERS ═══ */}
      {tab === 'users' && (
        <>
          <div className="flex items-center justify-between mb-4">
            <input type="text" placeholder="Search users..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key==='Enter'&&loadTab()} style={{maxWidth:300}}/>
            <button className="btn btn-primary btn-sm" onClick={() => setModal('add-user')}><UserPlus size={14}/> Add User</button>
          </div>
          <div className="table-wrap"><table><thead><tr><th>Username</th><th>Email</th><th>Name</th><th>Status</th><th>Actions</th></tr></thead><tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td style={{fontFamily:'var(--font-mono)',fontSize:13}}>{u.username}</td>
                <td>{u.email}</td>
                <td>{u.firstName} {u.lastName}</td>
                <td><span className={`badge ${u.enabled?'badge-success':'badge-danger'}`}>{u.enabled?'Active':'Disabled'}</span></td>
                <td>
                  <div className="flex gap-2">
                    <button className="btn-icon" title="View" onClick={() => viewUser(u.id)}><Eye size={14}/></button>
                    {pc.user_impersonation && <button className="btn-icon" title="Impersonate" onClick={() => exec(() => api.post(`/tenants/${realm}/users/${u.id}/impersonate`))}><UserCog size={14}/></button>}
                    <button className="btn-icon" title="Revoke Sessions" onClick={() => exec(() => api.del(`/tenants/${realm}/users/${u.id}/sessions`))}><LogOut size={14}/></button>
                    <button className="btn-icon" style={{color:'var(--danger)'}} title="Delete" onClick={() => exec(() => api.del(`/tenants/${realm}/users/${u.id}`))}><Trash2 size={14}/></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody></table></div>
          {users.length === 0 && <div className="empty-state"><h3>No users</h3><p>Create your first user or let users sign up</p></div>}
        </>
      )}

      {/* ═══ APPLICATIONS ═══ */}
      {tab === 'clients' && (
        <>
          <div className="flex justify-between mb-4">
            <div/><button className="btn btn-primary btn-sm" onClick={() => { setForm({protocol:'openid-connect'}); setModal('add-client'); }}><Plus size={14}/> Add Application</button>
          </div>
          <div className="table-wrap"><table><thead><tr><th>Client ID</th><th>Protocol</th><th>Public</th><th>Actions</th></tr></thead><tbody>
            {clients.map(c => (
              <tr key={c.id}><td style={{fontFamily:'var(--font-mono)',fontSize:13}}>{c.clientId}</td><td><span className="badge badge-info">{c.protocol}</span></td>
                <td>{c.publicClient?'Yes':'No'}</td><td><button className="btn-icon" style={{color:'var(--danger)'}} onClick={() => exec(() => api.del(`/tenants/${realm}/clients/${c.id}`))}><Trash2 size={14}/></button></td></tr>
            ))}
          </tbody></table></div>
        </>
      )}

      {/* ═══ SSO ═══ */}
      {tab === 'sso' && (
        <>
          <div className="flex justify-between mb-4">
            <div/>
            <div className="flex gap-2">
              <button className="btn btn-primary btn-sm" onClick={() => { setForm({provider_type:'google'}); setModal('add-oidc'); }}>+ OIDC Provider</button>
              <button className="btn btn-secondary btn-sm" onClick={() => { if(pc.saml_connections===0) { setError('SAML requires Business plan'); return; } setModal('add-saml'); }}>+ SAML Provider</button>
            </div>
          </div>
          {error && <div style={{background:'rgba(248,113,113,0.1)',border:'1px solid rgba(248,113,113,0.3)',borderRadius:6,padding:'10px 14px',marginBottom:16,color:'var(--danger)',fontSize:14}}>{error}</div>}
          <div className="table-wrap"><table><thead><tr><th>Alias</th><th>Type</th><th>Status</th><th>Actions</th></tr></thead><tbody>
            {idps.map(i => (
              <tr key={i.alias}><td style={{fontFamily:'var(--font-mono)'}}>{i.alias}</td><td><span className={`badge ${i.providerId==='saml'?'badge-warning':'badge-info'}`}>{i.providerId}</span></td>
                <td><span className={`badge ${i.enabled?'badge-success':'badge-danger'}`}>{i.enabled?'Active':'Disabled'}</span></td>
                <td><button className="btn-icon" style={{color:'var(--danger)'}} onClick={() => exec(() => api.del(`/tenants/${realm}/idp/${i.alias}`))}><Trash2 size={14}/></button></td></tr>
            ))}
          </tbody></table></div>
        </>
      )}

      {/* ═══ ORGANIZATIONS ═══ */}
      {tab === 'orgs' && (
        <>
          {!pc.organizations ? (
            <div className="empty-state"><h3>Organizations require Pro plan</h3><p>Upgrade to enable B2B multi-tenant features</p></div>
          ) : (
            <>
              <div className="flex justify-between mb-4"><div/>
                <div className="flex gap-2">
                  <button className="btn btn-primary btn-sm" onClick={() => setModal('add-org')}><Building2 size={14}/> New Organization</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => setModal('add-invite')}><UserPlus size={14}/> Invite</button>
                </div>
              </div>
              <div className="tenant-grid">
                {orgs.map(o => (
                  <div className="card" key={o.slug} style={{cursor:'default'}}>
                    <div className="flex items-center justify-between"><h3 style={{fontSize:16}}>{o.name}</h3>
                      <button className="btn-icon" style={{color:'var(--danger)'}} onClick={() => exec(() => api.del(`/tenants/${realm}/organizations/${o.slug}`))}><Trash2 size={14}/></button></div>
                    <div className="text-sm text-muted" style={{fontFamily:'var(--font-mono)'}}>{o.slug}</div>
                    <div className="mt-2 text-sm"><strong>{o.member_count}</strong> members</div>
                    {o.allowed_email_domains?.length > 0 && <div className="mt-2 text-sm text-muted">Auto-join: {o.allowed_email_domains.join(', ')}</div>}
                  </div>
                ))}
              </div>
              {invitations.length > 0 && (
                <div className="section mt-4">
                  <h3>Pending Invitations</h3>
                  <div className="table-wrap"><table><thead><tr><th>Email</th><th>Org</th><th>Role</th><th>Status</th></tr></thead><tbody>
                    {invitations.map((inv, i) => (
                      <tr key={i}><td>{inv.email}</td><td>{inv.org_slug||'—'}</td><td><span className="badge badge-info">{inv.role}</span></td><td><span className={`badge badge-${inv.status==='pending'?'warning':'success'}`}>{inv.status}</span></td></tr>
                    ))}
                  </tbody></table></div>
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* ═══ ROLES ═══ */}
      {tab === 'roles' && (
        <>
          <div className="flex justify-between mb-4"><div/><button className="btn btn-primary btn-sm" onClick={() => setModal('add-role')}><Shield size={14}/> New Role</button></div>
          <div className="table-wrap"><table><thead><tr><th>Name</th><th>Description</th><th>Actions</th></tr></thead><tbody>
            {roles.map(r => (
              <tr key={r.id}><td style={{fontFamily:'var(--font-mono)'}}>{r.name}</td><td className="text-muted">{r.description||'—'}</td>
                <td><button className="btn-icon" style={{color:'var(--danger)'}} onClick={() => exec(() => api.del(`/tenants/${realm}/roles/${r.name}`))}><Trash2 size={14}/></button></td></tr>
            ))}
          </tbody></table></div>
        </>
      )}

      {/* ═══ WEBHOOKS ═══ */}
      {tab === 'webhooks' && (
        <>
          {!pc.webhooks ? (
            <div className="empty-state"><h3>Webhooks require Pro plan</h3><p>Upgrade to receive real-time event notifications</p></div>
          ) : (
            <>
              <div className="flex justify-between mb-4"><div/><button className="btn btn-primary btn-sm" onClick={() => { setForm({events:[]}); setModal('add-webhook'); }}><Webhook size={14}/> Add Endpoint</button></div>
              {webhooks.map(w => (
                <div className="section" key={w.id}>
                  <div className="flex items-center justify-between">
                    <div><div style={{fontFamily:'var(--font-mono)',fontSize:13}}>{w.url}</div><div className="text-sm text-muted mt-2">Events: {w.events.map(e => <span className="event-tag" key={e}>{e}</span>)}</div></div>
                    <button className="btn btn-danger btn-sm" onClick={() => exec(() => api.del(`/tenants/${realm}/webhooks/${w.id}`))}><Trash2 size={14}/></button>
                  </div>
                </div>
              ))}
              {webhooks.length === 0 && <div className="empty-state"><h3>No webhooks</h3><p>Add an endpoint to receive event notifications</p></div>}
            </>
          )}
        </>
      )}

      {/* ═══ SETTINGS ═══ */}
      {tab === 'settings' && (
        <>
          <div className="section">
            <h3><Settings size={18}/> Authentication Settings</h3>
            {[
              { key: 'password_auth', label: 'Password Authentication', desc: 'Allow email/password sign-in' },
              { key: 'social_login', label: 'Social Login', desc: 'Enable Google, GitHub, etc.' },
              { key: 'magic_links', label: 'Magic Links', desc: 'Passwordless email login (Pro+)', gate: 'magic_links' },
              { key: 'mfa_enabled', label: 'Multi-Factor Authentication', desc: 'Require MFA for all users' },
              { key: 'disposable_email_blocking', label: 'Block Disposable Emails', desc: 'Reject temporary email domains (Pro+)', gate: 'disposable_email_blocking' },
              { key: 'password_breach_detection', label: 'Password Breach Detection', desc: 'Check passwords against known breaches (Pro+)', gate: 'password_breach_detection' },
              { key: 'bot_protection', label: 'Bot Protection', desc: 'Rate limiting & CAPTCHA (Pro+)', gate: 'bot_protection' },
            ].map(s => {
              const val = tenant.auth_settings?.[s.key] ?? false;
              const locked = s.gate && !pc[s.gate];
              return (
                <div className="toggle-row" key={s.key}>
                  <div><div className="toggle-label">{s.label} {locked && <span className="badge badge-pro" style={{marginLeft:6,fontSize:10}}>Pro</span>}</div><div className="toggle-desc">{s.desc}</div></div>
                  <div className={`toggle ${val?'on':''} ${locked?'':''}`.trim()} style={locked?{opacity:0.4,cursor:'not-allowed'}:{}} onClick={() => {
                    if(locked) return;
                    api.put(`/tenants/${realm}/auth-settings`, { [s.key]: !val }).then(load);
                  }}/>
                </div>
              );
            })}
          </div>

          <div className="section">
            <h3>Branding</h3>
            <div className="grid-2">
              <div className="form-group"><label>Primary Color</label>
                <div className="flex gap-2 items-center">
                  <input type="color" value={tenant.branding?.primary_color || '#5b5bf0'} onChange={e => api.put(`/tenants/${realm}/branding`, { primary_color: e.target.value }).then(load)} style={{width:40,height:36,padding:2}}/>
                  <input type="text" value={tenant.branding?.primary_color || '#5b5bf0'} readOnly style={{fontFamily:'var(--font-mono)'}}/>
                </div>
              </div>
              <div className="form-group"><label>Logo URL</label>
                <input type="url" placeholder="https://..." defaultValue={tenant.branding?.logo_url||''} onBlur={e => api.put(`/tenants/${realm}/branding`, { logo_url: e.target.value }).then(load)}/>
              </div>
            </div>
          </div>

          <div className="section">
            <h3>Plan & Billing</h3>
            <div className="flex items-center gap-4 mb-4">
              <div><div className="text-sm text-muted">Current Plan</div><span className={`badge badge-${tenant.plan}`} style={{fontSize:16,padding:'6px 16px'}}>{tenant.plan}</span></div>
              <div><div className="text-sm text-muted">Price</div><div style={{fontSize:20,fontWeight:700,fontFamily:'var(--font-mono)'}}>${pc.price}/mo</div></div>
            </div>
            <div className="flex gap-2">
              {['free','pro','business','enterprise'].filter(p => p !== tenant.plan).map(p => (
                <button key={p} className="btn btn-secondary btn-sm" onClick={() => exec(() => api.put(`/tenants/${realm}`, { plan: p }))}>
                  {['free','pro','business','enterprise'].indexOf(p) > ['free','pro','business','enterprise'].indexOf(tenant.plan) ? 'Upgrade' : 'Downgrade'} to {p}
                </button>
              ))}
            </div>
          </div>

          <div className="section" style={{borderColor:'var(--danger)'}}>
            <h3 style={{color:'var(--danger)'}}>Danger Zone</h3>
            <p className="text-sm text-muted mb-4">Permanently delete this project and all associated data.</p>
            <button className="btn btn-danger" onClick={() => { if(window.confirm(`Delete "${tenant.name}"? This cannot be undone.`)) exec(() => api.del(`/tenants/${realm}`).then(() => nav('/projects'))); }}>
              <Trash2 size={14}/> Delete Project
            </button>
          </div>
        </>
      )}

      {/* ═══ MODALS ═══ */}
      <Modal open={modal==='add-user'} onClose={closeModal} title="Add User">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Username</label><input type="text" value={form.username||''} onChange={e=>sf('username',e.target.value)}/></div>
        <div className="form-group"><label>Email</label><input type="email" value={form.email||''} onChange={e=>sf('email',e.target.value)}/></div>
        <div className="grid-2">
          <div className="form-group"><label>First Name</label><input type="text" value={form.first_name||''} onChange={e=>sf('first_name',e.target.value)}/></div>
          <div className="form-group"><label>Last Name</label><input type="text" value={form.last_name||''} onChange={e=>sf('last_name',e.target.value)}/></div>
        </div>
        <div className="form-group"><label>Password</label><input type="password" value={form.password||''} onChange={e=>sf('password',e.target.value)}/></div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/users`, form))}>Create User</button></div>
      </Modal>

      <Modal open={modal==='add-client'} onClose={closeModal} title="Add Application">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Client ID</label><input type="text" value={form.client_id||''} onChange={e=>sf('client_id',e.target.value)} placeholder="my-web-app"/></div>
        <div className="form-group"><label>Protocol</label><select value={form.protocol||'openid-connect'} onChange={e=>sf('protocol',e.target.value)}>
          <option value="openid-connect">OpenID Connect</option><option value="saml">SAML</option></select></div>
        <div className="form-group"><label>Redirect URIs</label><input type="text" value={form.redirect_uris||'http://localhost:*'} onChange={e=>sf('redirect_uris',e.target.value)} placeholder="comma-separated"/></div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/clients`, {...form, redirect_uris: (form.redirect_uris||'').split(',').map(u=>u.trim())}))}>Create</button></div>
      </Modal>

      <Modal open={modal==='add-oidc'} onClose={closeModal} title="Add OIDC Provider">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Provider</label><select value={form.provider_type||'google'} onChange={e=>sf('provider_type',e.target.value)}>
          <option value="google">Google</option><option value="github">GitHub</option><option value="facebook">Facebook</option><option value="oidc">Custom OIDC</option></select></div>
        <div className="form-group"><label>Alias</label><input type="text" value={form.alias||''} onChange={e=>sf('alias',e.target.value)} placeholder="google-login"/></div>
        <div className="form-group"><label>Client ID</label><input type="text" value={form.client_id||''} onChange={e=>sf('client_id',e.target.value)}/></div>
        <div className="form-group"><label>Client Secret</label><input type="password" value={form.client_secret||''} onChange={e=>sf('client_secret',e.target.value)}/></div>
        {form.provider_type==='oidc' && <>
          <div className="form-group"><label>Authorization URL</label><input type="url" value={form.authorization_url||''} onChange={e=>sf('authorization_url',e.target.value)}/></div>
          <div className="form-group"><label>Token URL</label><input type="url" value={form.token_url||''} onChange={e=>sf('token_url',e.target.value)}/></div>
        </>}
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/idp/oidc`, form))}>Add Provider</button></div>
      </Modal>

      <Modal open={modal==='add-saml'} onClose={closeModal} title="Add SAML Provider">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Alias</label><input type="text" value={form.alias||''} onChange={e=>sf('alias',e.target.value)} placeholder="okta-saml"/></div>
        <div className="form-group"><label>Entity ID</label><input type="text" value={form.entity_id||''} onChange={e=>sf('entity_id',e.target.value)}/></div>
        <div className="form-group"><label>SSO URL</label><input type="url" value={form.sso_url||''} onChange={e=>sf('sso_url',e.target.value)}/></div>
        <div className="form-group"><label>Signing Certificate (optional)</label><textarea rows={3} value={form.signing_certificate||''} onChange={e=>sf('signing_certificate',e.target.value)}/></div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/idp/saml`, form))}>Add SAML</button></div>
      </Modal>

      <Modal open={modal==='add-org'} onClose={closeModal} title="Create Organization">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Name</label><input type="text" value={form.name||''} onChange={e => { sf('name',e.target.value); sf('slug', e.target.value.toLowerCase().replace(/[^a-z0-9]/g,'-')); }}/></div>
        <div className="form-group"><label>Slug</label><input type="text" value={form.slug||''} onChange={e=>sf('slug',e.target.value)} style={{fontFamily:'var(--font-mono)'}}/></div>
        <div className="form-group"><label>Auto-join Email Domains (comma separated)</label><input type="text" value={form.domains||''} onChange={e=>sf('domains',e.target.value)} placeholder="company.com, subsidiary.com"/></div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/organizations`, { name: form.name, slug: form.slug, allowed_email_domains: (form.domains||'').split(',').map(d=>d.trim()).filter(Boolean) }))}>Create</button></div>
      </Modal>

      <Modal open={modal==='add-invite'} onClose={closeModal} title="Send Invitation">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Email</label><input type="email" value={form.email||''} onChange={e=>sf('email',e.target.value)}/></div>
        <div className="form-group"><label>Organization (optional)</label><select value={form.org_slug||''} onChange={e=>sf('org_slug',e.target.value)}>
          <option value="">No specific org</option>{orgs.map(o => <option key={o.slug} value={o.slug}>{o.name}</option>)}</select></div>
        <div className="form-group"><label>Role</label><select value={form.role||'member'} onChange={e=>sf('role',e.target.value)}>
          <option value="member">Member</option><option value="admin">Admin</option></select></div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/invitations`, form))}>Send Invitation</button></div>
      </Modal>

      <Modal open={modal==='add-role'} onClose={closeModal} title="Create Role">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Role Name</label><input type="text" value={form.name||''} onChange={e=>sf('name',e.target.value)} placeholder="editor"/></div>
        <div className="form-group"><label>Description</label><input type="text" value={form.description||''} onChange={e=>sf('description',e.target.value)}/></div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/roles`, form))}>Create Role</button></div>
      </Modal>

      <Modal open={modal==='add-webhook'} onClose={closeModal} title="Add Webhook Endpoint">
        {error && <div style={{color:'var(--danger)',marginBottom:12,fontSize:13}}>{error}</div>}
        <div className="form-group"><label>Endpoint URL</label><input type="url" value={form.url||''} onChange={e=>sf('url',e.target.value)} placeholder="https://your-app.com/webhooks"/></div>
        <div className="form-group"><label>Events</label>
          <div style={{display:'flex',flexWrap:'wrap',gap:6}}>
            {['user.created','user.updated','user.deleted','organization.created','organizationMembership.created','session.revoked','invitation.created'].map(ev => {
              const sel = (form.events||[]).includes(ev);
              return <div key={ev} className={`event-tag ${sel?'':'text-muted'}`} style={{cursor:'pointer',opacity:sel?1:0.5,border: sel?'1px solid var(--accent)':'1px solid var(--border)'}}
                onClick={() => sf('events', sel ? (form.events||[]).filter(e=>e!==ev) : [...(form.events||[]), ev])}>{ev}</div>;
            })}
          </div>
        </div>
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={() => exec(() => api.post(`/tenants/${realm}/webhooks`, form))}>Create Webhook</button></div>
      </Modal>

      <Modal open={modal==='user-detail'} onClose={() => { setModal(null); setSelectedUser(null); }} title="User Details">
        {selectedUser && (
          <>
            <div className="grid-2 mb-4">
              <div><div className="text-sm text-muted">Username</div><div style={{fontFamily:'var(--font-mono)'}}>{selectedUser.username}</div></div>
              <div><div className="text-sm text-muted">Email</div><div>{selectedUser.email}</div></div>
              <div><div className="text-sm text-muted">Name</div><div>{selectedUser.firstName} {selectedUser.lastName}</div></div>
              <div><div className="text-sm text-muted">Status</div><span className={`badge ${selectedUser.enabled?'badge-success':'badge-danger'}`}>{selectedUser.enabled?'Active':'Disabled'}</span></div>
            </div>
            {selectedUser.roles?.length > 0 && (
              <div className="mb-4"><div className="text-sm text-muted mb-4">Roles</div>
                <div className="flex gap-2">{selectedUser.roles.map(r => <span className="badge badge-info" key={r.id}>{r.name}</span>)}</div></div>
            )}
            {selectedUser.sessions?.length > 0 && (
              <div><div className="text-sm text-muted mb-4">Active Sessions ({selectedUser.sessions.length})</div>
                {selectedUser.sessions.map(s => (
                  <div key={s.id} className="card mb-4" style={{padding:12}}>
                    <div className="flex items-center justify-between">
                      <div><div className="text-sm">IP: <strong>{s.ipAddress}</strong></div>
                        <div className="text-sm text-muted">Started: {s.start ? new Date(s.start).toLocaleString() : '—'}</div></div>
                      <button className="btn btn-danger btn-sm" onClick={() => { api.del(`/tenants/${realm}/sessions/${s.id}`).then(() => viewUser(selectedUser.id)); }}>Revoke</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </Modal>
    </div>
  );
}
