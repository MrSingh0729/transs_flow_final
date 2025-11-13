import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
 
const AuthContext = createContext();
 
export const useAuth = () => {
  return useContext(AuthContext);
};
 
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
 
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);
 
  const fetchUser = async () => {
    try {
      const response = await axios.get('/accounts/api/user/');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };
 
  const login = async (username, password) => {
    try {
      const response = await axios.post('/ipqc/api/auth/token/', {
        username,
        password
      });
      
      const { access, refresh } = response.data;
      localStorage.setItem('token', access);
      localStorage.setItem('refreshToken', refresh);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      // Fetch user details
      const userResponse = await axios.get('/accounts/api/user/');
      setUser(userResponse.data);
      
      toast.success('Login successful!');
      return true;
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Invalid credentials');
      return false;
    }
  };
 
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    toast.info('Logged out successfully');
  };
 
  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      const response = await axios.post('/ipqc/api/auth/token/refresh/', {
        refresh: refreshToken
      });
      
      const { access } = response.data;
      localStorage.setItem('token', access);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      return access;
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      return null;
    }
  };
 
  const value = {
    user,
    login,
    logout,
    loading,
    refreshToken
  };
 
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};