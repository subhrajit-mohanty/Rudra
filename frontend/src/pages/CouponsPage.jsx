import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import Modal from '../components/Modal';
import { Ticket, Plus, Trash2, Eye, ToggleLeft, ToggleRight } from 'lucide-react';

export default function CouponsPage() {
  const [coupons, setCoupons] = useState([]);
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState('');
  const [redemptions, setRedemptions] = useState([]);
  const [viewCode, setViewCode] = useState('');

  const load = () => api.get('/coupons').then(setCoupons).catch(console.error);
  useEffect(() => { load(); }, []);

  const sf = (k, v) => setForm(p => ({ ...p, [k]: v }));
  const closeModal = () => { setModal(null); setForm({}); setError(''); };

  const createCoupon = async () => {
    setError('');
    try {
      await api.post('/coupons', {
        code: form.code || '',
        discount_pct: parseInt(form.discount_pct) || 10,
        description: form.description || '',
        max_redemptions: parseInt(form.max_redemptions) || -1,
        valid_plans: (form.valid_plans || '').split(',').map(s => s.trim()).filter(Boolean),
        duration_days: parseInt(form.duration_days) || 0,
      });
      closeModal();
      load();
    } catch (e) { setError(e.message); }
  };

  const toggleCoupon = async (code) => {
    await api.put(`/coupons/${code}/toggle`);
    load();
  };

  const deleteCoupon = async (code) => {
    if (!window.confirm(`Delete coupon "${code}"?`)) return;
    await api.del(`/coupons/${code}`);
    load();
  };

  const viewRedemptions = async (code) => {
    setViewCode(code);
    const r = await api.get(`/coupons/${code}/redemptions`);
    setRedemptions(r);
    setModal('redemptions');
  };

  return (
    <div>
      <div className="page-header">
        <div><h1><Ticket size={24} style={{ marginRight: 8, verticalAlign: 'middle' }} />Coupons</h1>
          <p>Create discount coupons for organizations and customers</p></div>
        <button className="btn btn-primary" onClick={() => setModal('create')}><Plus size={16} /> New Coupon</button>
      </div>

      {coupons.length === 0 ? (
        <div className="empty-state">
          <Ticket size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
          <h3>No coupons yet</h3>
          <p>Create coupons to offer discounts to your customers during project creation</p>
          <button className="btn btn-primary mt-4" onClick={() => setModal('create')}>Create First Coupon</button>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Code</th><th>Discount</th><th>Description</th><th>Plans</th><th>Redeemed</th><th>Limit</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {coupons.map(c => (
                <tr key={c.code}>
                  <td><span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 14, background: 'var(--accent-light)', padding: '4px 10px', borderRadius: 4 }}>{c.code}</span></td>
                  <td><span style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--success)' }}>{c.discount_pct}%</span></td>
                  <td className="text-muted">{c.description || '—'}</td>
                  <td>{c.valid_plans?.length > 0 ? c.valid_plans.map(p => <span key={p} className={`badge badge-${p}`} style={{ marginRight: 4 }}>{p}</span>) : <span className="text-muted">All</span>}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{c.times_redeemed}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{c.max_redemptions === -1 ? '∞' : c.max_redemptions}</td>
                  <td><span className={`badge ${c.enabled ? 'badge-success' : 'badge-danger'}`}>{c.enabled ? 'Active' : 'Disabled'}</span></td>
                  <td>
                    <div className="flex gap-2">
                      <button className="btn-icon" title="View Redemptions" onClick={() => viewRedemptions(c.code)}><Eye size={14} /></button>
                      <button className="btn-icon" title={c.enabled ? 'Disable' : 'Enable'} onClick={() => toggleCoupon(c.code)}>
                        {c.enabled ? <ToggleRight size={14} style={{ color: 'var(--success)' }} /> : <ToggleLeft size={14} />}
                      </button>
                      <button className="btn-icon" style={{ color: 'var(--danger)' }} title="Delete" onClick={() => deleteCoupon(c.code)}><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Coupon Modal */}
      <Modal open={modal === 'create'} onClose={closeModal} title="Create Coupon">
        {error && <div style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.3)', borderRadius: 6, padding: '10px 14px', marginBottom: 16, color: 'var(--danger)', fontSize: 14 }}>{error}</div>}
        <div className="form-group">
          <label>Coupon Code</label>
          <input type="text" value={form.code || ''} onChange={e => sf('code', e.target.value.toUpperCase())} placeholder="WELCOME50" style={{ fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }} />
        </div>
        <div className="grid-2">
          <div className="form-group">
            <label>Discount %</label>
            <input type="number" min="1" max="100" value={form.discount_pct || ''} onChange={e => sf('discount_pct', e.target.value)} placeholder="25" />
          </div>
          <div className="form-group">
            <label>Max Redemptions</label>
            <input type="number" min="-1" value={form.max_redemptions || ''} onChange={e => sf('max_redemptions', e.target.value)} placeholder="-1 for unlimited" />
          </div>
        </div>
        <div className="form-group">
          <label>Description</label>
          <input type="text" value={form.description || ''} onChange={e => sf('description', e.target.value)} placeholder="Welcome discount for new organizations" />
        </div>
        <div className="form-group">
          <label>Valid Plans (comma separated, empty = all)</label>
          <input type="text" value={form.valid_plans || ''} onChange={e => sf('valid_plans', e.target.value)} placeholder="pro, business, enterprise" />
        </div>
        <div className="form-group">
          <label>Expires In (days, 0 = never)</label>
          <input type="number" min="0" value={form.duration_days || ''} onChange={e => sf('duration_days', e.target.value)} placeholder="0" />
        </div>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={closeModal}>Cancel</button>
          <button className="btn btn-primary" onClick={createCoupon}>Create Coupon</button>
        </div>
      </Modal>

      {/* Redemptions Modal */}
      <Modal open={modal === 'redemptions'} onClose={closeModal} title={`Redemptions — ${viewCode}`}>
        {redemptions.length === 0 ? (
          <div className="text-muted" style={{ textAlign: 'center', padding: 20 }}>No redemptions yet</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>User</th><th>Project</th><th>Date</th></tr></thead>
              <tbody>
                {redemptions.map((r, i) => (
                  <tr key={i}>
                    <td>{r.redeemed_by}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 13 }}>{r.realm_name}</td>
                    <td className="text-muted">{r.redeemed_at ? new Date(r.redeemed_at).toLocaleString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="modal-actions"><button className="btn btn-secondary" onClick={closeModal}>Close</button></div>
      </Modal>
    </div>
  );
}
