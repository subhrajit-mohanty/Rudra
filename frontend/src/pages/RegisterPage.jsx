import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '', company: '' });
  const [error, setError] = useState('');
  const { register } = useAuth();
  const nav = useNavigate();
  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try { await register(form.email, form.password, form.name, form.company); nav('/dashboard'); }
    catch (err) { setError(err.message); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div style={{textAlign:'center',marginBottom:16}}><img src="/logo.png" alt="Rudra" style={{height:56, width:'auto'}} /></div>
        <p className="subtitle">Create your account</p>
        {error && <div style={{background:'rgba(248,113,113,0.1)',border:'1px solid rgba(248,113,113,0.3)',borderRadius:6,padding:'10px 14px',marginBottom:16,color:'var(--danger)',fontSize:14}}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group"><label>Full Name</label><input type="text" value={form.name} onChange={e=>set('name',e.target.value)} required/></div>
          <div className="form-group"><label>Email</label><input type="email" value={form.email} onChange={e=>set('email',e.target.value)} required/></div>
          <div className="form-group"><label>Company</label><input type="text" value={form.company} onChange={e=>set('company',e.target.value)} placeholder="Optional"/></div>
          <div className="form-group"><label>Password</label><input type="password" value={form.password} onChange={e=>set('password',e.target.value)} required minLength={8}/></div>
          <button type="submit" className="btn btn-primary w-full" style={{justifyContent:'center'}}>Create Account</button>
        </form>
        <p className="footer">Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  );
}
