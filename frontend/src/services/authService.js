import apiClient from './apiService';

export const authService = {
  signup: async ({ email, password, role = 'end_user' }) => {
    const res = await apiClient.post('/auth/simple/register', { email, password, role });
    return res.data;
  },
  login: async ({ email, password }) => {
    const res = await apiClient.post('/auth/simple/login', { email, password });
    const data = res.data;
    if (data?.access_token) {
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_role', data.role || 'end_user');
      localStorage.setItem('auth_user_id', data.user_id || '');
    }
    return data;
  },
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_role');
    localStorage.removeItem('auth_user_id');
  },
  getRole: () => localStorage.getItem('auth_role') || 'guest',
  isLoggedIn: () => !!localStorage.getItem('auth_token')
};

export default authService;


