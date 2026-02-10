import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Plus } from 'lucide-react';

export default function ProjectsPage() {
  const [tenants, setTenants] = useState([]);
  const nav = useNavigate();
  useEffect(() => { api.get('/tenants').then(setTenants).catch(console.error); }, []);
  return (
    <div>
      <div className="page-header"><div><h1>Projects</h1><p>Manage your authentication projects</p></div>
        <button className="btn btn-primary" onClick={() => nav('/projects/new')}><Plus size={16}/>New Project</button>
      </div>
      {tenants.length === 0 ? (
        <div className="empty-state"><h3>No projects yet</h3><p>Create your first project to get started</p>
          <button className="btn btn-primary mt-4" onClick={() => nav('/projects/new')}>Create Project</button></div>
      ) : (
        <div className="tenant-grid">
          {tenants.map(t => (
            <div className="tenant-card" key={t.realm_name} onClick={() => nav(`/projects/${t.realm_name}`)}>
              <div className="flex items-center justify-between">
                <h3>{t.name}</h3>
                <div className="flex gap-2 items-center">
                  {t.applied_coupon && <span className="badge badge-success" title={`${t.discount_pct}% off`}>🎟 {t.discount_pct}% off</span>}
                  <span className={`badge badge-${t.plan}`}>{t.plan}</span>
                </div>
              </div>
              <div className="realm">{t.realm_name}</div>
              <div className="stats">
                <div className="mini-stat"><div className="num">{t.user_count}</div><div className="lbl">Users</div></div>
                <div className="mini-stat"><div className="num">{t.client_count}</div><div className="lbl">Apps</div></div>
                <div className="mini-stat"><div className="num">{t.idp_count}</div><div className="lbl">SSO</div></div>
                <div className="mini-stat"><div className="num">{t.org_count}</div><div className="lbl">Orgs</div></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
