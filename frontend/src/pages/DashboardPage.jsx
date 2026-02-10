import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { FolderKey, Users, AppWindow, Building2 } from 'lucide-react';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const nav = useNavigate();
  useEffect(() => { api.get('/dashboard').then(setData).catch(console.error); }, []);
  if (!data) return <div className="text-muted" style={{padding:40}}>Loading...</div>;
  const stats = [
    { label: 'Projects', value: data.total_tenants, icon: <FolderKey size={20}/>, color: '#5b5bf0' },
    { label: 'Total Users', value: data.total_users, icon: <Users size={20}/>, color: '#34d399' },
    { label: 'Applications', value: data.total_clients, icon: <AppWindow size={20}/>, color: '#fbbf24' },
    { label: 'Organizations', value: data.total_orgs, icon: <Building2 size={20}/>, color: '#f87171' },
  ];
  return (
    <div>
      <div className="page-header"><div><h1>Dashboard</h1><p>Overview of your Rudra platform</p></div>
        <button className="btn btn-primary" onClick={() => nav('/projects/new')}>+ New Project</button>
      </div>
      <div className="stat-grid">
        {stats.map(s => (
          <div className="stat-card" key={s.label}>
            <div className="flex items-center justify-between mb-4">
              <div className="label">{s.label}</div>
              <div style={{color:s.color}}>{s.icon}</div>
            </div>
            <div className="value" style={{color:s.color}}>{s.value.toLocaleString()}</div>
          </div>
        ))}
      </div>
      {data.plan_distribution && Object.keys(data.plan_distribution).length > 0 && (
        <div className="section">
          <h3>Plan Distribution</h3>
          <div className="flex gap-4">
            {Object.entries(data.plan_distribution).map(([k,v]) => (
              <div key={k} className="flex items-center gap-2">
                <span className={`badge badge-${k}`}>{k}</span>
                <span style={{fontFamily:'var(--font-mono)',fontWeight:700}}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="section">
        <h3>Recent Activity</h3>
        {data.recent_activity?.length === 0 && <div className="text-muted text-sm">No recent activity</div>}
        {data.recent_activity?.map((a, i) => (
          <div className="activity-item" key={i}>
            <div className="activity-dot"/>
            <div>
              <div className="activity-text"><strong>{a.action}</strong> {a.details && `— ${a.details}`}</div>
              <div className="activity-time">{a.realm_name && `${a.realm_name} · `}{a.timestamp ? new Date(a.timestamp).toLocaleString() : ''}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
