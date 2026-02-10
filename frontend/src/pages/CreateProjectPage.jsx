import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Check, Ticket } from 'lucide-react';

export default function CreateProjectPage() {
  const [plans, setPlans] = useState({});
  const [selectedPlan, setSelectedPlan] = useState('free');
  const [name, setName] = useState('');
  const [realm, setRealm] = useState('');
  const [couponCode, setCouponCode] = useState('');
  const [couponResult, setCouponResult] = useState(null);
  const [couponChecking, setCouponChecking] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const nav = useNavigate();

  useEffect(() => { api.get('/plans').then(setPlans).catch(console.error); }, []);
  const handleNameChange = (v) => { setName(v); setRealm(v.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-')); };

  const validateCoupon = useCallback(async (code) => {
    if (!code || code.length < 2) { setCouponResult(null); return; }
    setCouponChecking(true);
    try {
      const r = await api.post('/coupons/validate', { code, plan: selectedPlan });
      setCouponResult(r);
    } catch { setCouponResult({ valid: false, error: 'Validation failed' }); }
    setCouponChecking(false);
  }, [selectedPlan]);

  useEffect(() => {
    const t = setTimeout(() => { if (couponCode) validateCoupon(couponCode); }, 500);
    return () => clearTimeout(t);
  }, [couponCode, validateCoupon]);

  const handleCreate = async (e) => {
    e.preventDefault(); setError('');
    try {
      const payload = { name, realm_name: realm, plan: selectedPlan };
      if (couponResult?.valid) payload.coupon_code = couponCode;
      await api.post('/tenants', payload);
      nav(`/projects/${realm}`);
    } catch (err) { setError(err.message); }
  };

  const planPrice = plans[selectedPlan]?.price || 0;
  const discount = couponResult?.valid ? couponResult.discount_pct : 0;
  const finalPrice = Math.max(0, planPrice - (planPrice * discount / 100));

  const features = [
    { key: 'max_users', label: 'Users', fmt: v => v === -1 ? 'Unlimited' : v.toLocaleString() },
    { key: 'max_realms', label: 'Projects', fmt: v => v === -1 ? 'Unlimited' : v },
    { key: 'organizations', label: 'Organizations', fmt: v => v ? 'Yes' : 'No' },
    { key: 'saml_connections', label: 'SAML SSO', fmt: v => v === -1 ? 'Unlimited' : v === 0 ? 'No' : `${v} connections` },
    { key: 'webhooks', label: 'Webhooks', fmt: v => v ? 'Yes' : 'No' },
    { key: 'analytics', label: 'Analytics', fmt: v => v ? 'Yes' : 'No' },
    { key: 'user_impersonation', label: 'Impersonation', fmt: v => v ? 'Yes' : 'No' },
    { key: 'password_breach_detection', label: 'Breach Detection', fmt: v => v ? 'Yes' : 'No' },
    { key: 'bot_protection', label: 'Bot Protection', fmt: v => v ? 'Yes' : 'No' },
  ];

  return (
    <div>
      <div className="breadcrumb"><a href="/projects">Projects</a><span>/</span>New</div>
      <div className="page-header"><div><h1>Create Project</h1><p>{step === 1 ? 'Choose a plan' : 'Configure your project'}</p></div></div>

      {step === 1 && (
        <>
          <div className="plan-grid">
            {Object.entries(plans).map(([k, p]) => (
              <div key={k} className={`plan-card ${selectedPlan===k?'selected':''}`} onClick={() => setSelectedPlan(k)} style={{position:'relative'}}>
                {selectedPlan===k && <Check size={20} style={{color:'var(--accent)',position:'absolute',top:12,right:12}}/>}
                <h3>{p.name}</h3>
                <div className="price">{p.price === 0 ? 'Free' : `$${p.price}`}{p.price > 0 && <span>/mo</span>}</div>
                {features.map(f => (
                  <div className="feature" key={f.key}>{f.label}: <strong>{f.fmt(p[f.key])}</strong></div>
                ))}
              </div>
            ))}
          </div>
          <button className="btn btn-primary" onClick={() => setStep(2)}>Continue with {plans[selectedPlan]?.name || selectedPlan}</button>
        </>
      )}

      {step === 2 && (
        <div style={{display:'grid', gridTemplateColumns:'1fr 340px', gap:24, alignItems:'start'}}>
          <div className="card">
            {error && <div style={{background:'rgba(248,113,113,0.1)',border:'1px solid rgba(248,113,113,0.3)',borderRadius:6,padding:'10px 14px',marginBottom:16,color:'var(--danger)',fontSize:14}}>{error}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-group"><label>Project Name</label><input type="text" value={name} onChange={e => handleNameChange(e.target.value)} required placeholder="My SaaS App"/></div>
              <div className="form-group"><label>Realm Identifier</label><input type="text" value={realm} onChange={e => setRealm(e.target.value)} required placeholder="my-saas-app"/>
                <div className="text-sm text-muted mt-2">Auth URL: auth.rudra.io/realms/{realm || '...'}</div></div>
              <div className="form-group"><label>Plan</label><div className="flex items-center gap-2"><span className={`badge badge-${selectedPlan}`}>{plans[selectedPlan]?.name}</span>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setStep(1)}>Change</button></div></div>

              {/* Coupon Code Section */}
              <div className="form-group" style={{borderTop:'1px solid var(--border)', paddingTop:18, marginTop:8}}>
                <label><Ticket size={14} style={{marginRight:6,verticalAlign:'middle'}}/>Have a coupon code?</label>
                <div className="flex gap-2 items-center">
                  <input type="text" value={couponCode} onChange={e => setCouponCode(e.target.value.toUpperCase())}
                    placeholder="Enter code" style={{fontFamily:'var(--font-mono)', textTransform:'uppercase', maxWidth:240}}/>
                  {couponChecking && <span className="text-sm text-muted">Checking...</span>}
                </div>
                {couponResult && (
                  <div style={{marginTop:8, padding:'10px 14px', borderRadius:6,
                    background: couponResult.valid ? 'rgba(52,211,153,0.1)' : 'rgba(248,113,113,0.1)',
                    border: `1px solid ${couponResult.valid ? 'rgba(52,211,153,0.3)' : 'rgba(248,113,113,0.3)'}`,
                    color: couponResult.valid ? 'var(--success)' : 'var(--danger)', fontSize:14}}>
                    {couponResult.valid
                      ? <>✓ <strong>{couponResult.discount_pct}% off</strong> applied! {couponResult.description && `— ${couponResult.description}`}</>
                      : <>✗ {couponResult.error}</>}
                  </div>
                )}
              </div>

              <div className="modal-actions" style={{justifyContent:'flex-start'}}>
                <button type="submit" className="btn btn-primary">Create Project</button>
                <button type="button" className="btn btn-secondary" onClick={() => nav('/projects')}>Cancel</button>
              </div>
            </form>
          </div>

          {/* Order Summary Sidebar */}
          <div className="card" style={{position:'sticky', top:32}}>
            <h3 style={{fontSize:15, marginBottom:16}}>Order Summary</h3>
            <div style={{display:'flex', justifyContent:'space-between', marginBottom:8}}>
              <span className="text-muted">Plan</span>
              <span className={`badge badge-${selectedPlan}`}>{plans[selectedPlan]?.name}</span>
            </div>
            <div style={{display:'flex', justifyContent:'space-between', marginBottom:8}}>
              <span className="text-muted">Base Price</span>
              <span style={{fontFamily:'var(--font-mono)', fontWeight:600}}>{planPrice === 0 ? 'Free' : `$${planPrice}/mo`}</span>
            </div>
            {discount > 0 && (
              <div style={{display:'flex', justifyContent:'space-between', marginBottom:8, color:'var(--success)'}}>
                <span>Coupon ({couponResult.code})</span>
                <span style={{fontFamily:'var(--font-mono)', fontWeight:600}}>-{discount}%</span>
              </div>
            )}
            <div style={{borderTop:'1px solid var(--border)', paddingTop:12, marginTop:12, display:'flex', justifyContent:'space-between'}}>
              <span style={{fontWeight:700}}>Total</span>
              <span style={{fontFamily:'var(--font-mono)', fontWeight:700, fontSize:20, color: discount > 0 ? 'var(--success)' : 'var(--text-primary)'}}>
                {finalPrice === 0 ? 'Free' : `$${finalPrice.toFixed(0)}/mo`}
              </span>
            </div>
            {discount > 0 && planPrice > 0 && (
              <div className="text-sm" style={{textAlign:'right', marginTop:4, color:'var(--success)'}}>
                You save ${(planPrice - finalPrice).toFixed(0)}/mo
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
