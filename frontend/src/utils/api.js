const BASE = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE}${path}`, { ...options, headers });
  } catch (e) {
    throw new Error('Network error — is the backend running?');
  }

  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }

  let data;
  const text = await res.text();
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(res.ok ? text : `Server error (${res.status}): ${text.substring(0, 100)}`);
  }

  if (!res.ok) throw new Error(data.detail || data.message || JSON.stringify(data));
  return data;
}

const api = {
  get: (p) => request(p),
  post: (p, d) => request(p, { method: 'POST', body: JSON.stringify(d) }),
  put: (p, d) => request(p, { method: 'PUT', body: JSON.stringify(d) }),
  del: (p) => request(p, { method: 'DELETE' }),
};

export default api;
