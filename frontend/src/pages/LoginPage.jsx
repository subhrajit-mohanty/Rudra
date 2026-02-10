import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const nav = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try { await login(email, password); nav('/dashboard'); }
    catch (err) { setError(err.message); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div style={{textAlign:'center',marginBottom:16}}><img src="/logo.png" alt="Rudra" style={{height:56, width:'auto'}} /></div>
        <p className="subtitle">Sign in to your account</p>
        {error && <div style={{background:'rgba(248,113,113,0.1)',border:'1px solid rgba(248,113,113,0.3)',borderRadius:6,padding:'10px 14px',marginBottom:16,color:'var(--danger)',fontSize:14}}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group"><label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/></div>
          <div className="form-group"><label>Password</label><input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></div>
          <button type="submit" className="btn btn-primary w-full" style={{justifyContent:'center'}}>Sign In</button>
        </form>
        <p className="footer">Don't have an account? <Link to="/register">Create one</Link></p>
      </div>
    </div>
  );
}
