import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LayoutDashboard, FolderKey, LogOut, Ticket } from 'lucide-react';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const items = [
    { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18}/> },
    { path: '/projects', label: 'Projects', icon: <FolderKey size={18}/> },
    { path: '/coupons', label: 'Coupons', icon: <Ticket size={18}/> },
  ];
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo" onClick={() => nav('/dashboard')} style={{cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', paddingBottom:20}}>
          <img src="/logo.png" alt="Rudra" style={{height:44, width:'auto', objectFit:'contain'}} />
        </div>
        <nav className="sidebar-nav">
          <div className="nav-section">Platform</div>
          {items.map(i => (
            <div key={i.path} className={`nav-item ${loc.pathname.startsWith(i.path)?'active':''}`} onClick={() => nav(i.path)}>
              {i.icon}{i.label}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <strong>{user?.name || user?.email}</strong>
            <span>{user?.email}</span>
          </div>
          <div style={{marginTop:10}}>
            <button className="btn btn-secondary btn-sm w-full" onClick={() => { logout(); nav('/login'); }}>
              <LogOut size={14}/> Sign Out
            </button>
          </div>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
