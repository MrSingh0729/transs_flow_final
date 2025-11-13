import api from './index';

// Login user and store tokens
export const login = async (credentials) => {
  const response = await api.post('/api/auth/token/', credentials);
  const { access, refresh } = response.data;
  localStorage.setItem('token', access);
  localStorage.setItem('refreshToken', refresh);
  return response;
};

// Refresh token
export const refreshToken = (refresh) => api.post('/api/auth/token/refresh/', { refresh });

// Get user profile
export const getUserProfile = () => api.get('/api/auth/profile/');

// Logout
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
};
