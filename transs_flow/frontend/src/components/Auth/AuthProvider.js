import React, { createContext, useState, useEffect } from 'react';
import { SecureStorage } from '../../plugins/secure-storage';
import api from '../../api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = await SecureStorage.get('token');
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        try {
          const response = await api.get('/accounts/me/');
          setUser(response.data);
        } catch {
          setUser(null);
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (employee_id, password) => {
    const response = await api.post('/accounts/api/token/', { employee_id, password });
    const { access, refresh } = response.data;
    await SecureStorage.set({ key: 'token', value: access });
    await SecureStorage.set({ key: 'refreshToken', value: refresh });
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
    setUser(await api.get('/accounts/me/').then(res => res.data));
  };

  const logout = async () => {
    await SecureStorage.clear();
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
