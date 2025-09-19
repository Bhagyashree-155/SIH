import apiClient from './apiService';

export const authService = {
  signup: async ({ username, email, password, role = 'end_user' }) => {
    const res = await apiClient.post('/auth/simple/register', { username, email, password, role });
    return res.data;
  },
  login: async ({ email, password }) => {
    const res = await apiClient.post('/auth/simple/login', { email, password });
    const data = res.data;
    if (data?.access_token) {
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_role', data.role || 'end_user');
      localStorage.setItem('auth_user_id', data.user_id || '');
      // Persist email for navbar display
      const userEmail = data.email || email || '';
      if (userEmail) {
        try { localStorage.setItem('auth_email', userEmail); } catch {}
      }
      const username = data.username || '';
      if (username) {
        try { localStorage.setItem('auth_username', username); } catch {}
      }
      try { window.dispatchEvent(new Event('auth-changed')); } catch {}
    }
    return data;
  },
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_role');
    localStorage.removeItem('auth_user_id');
    try { localStorage.removeItem('auth_email'); } catch {}
    try { localStorage.removeItem('auth_username'); } catch {}
    try { window.dispatchEvent(new Event('auth-changed')); } catch {}
  },
  getRole: () => localStorage.getItem('auth_role') || 'guest',
  isLoggedIn: () => !!localStorage.getItem('auth_token'),
  getEmail: () => localStorage.getItem('auth_email') || '',
  getUsername: () => localStorage.getItem('auth_username') || ''
};

export default authService;


