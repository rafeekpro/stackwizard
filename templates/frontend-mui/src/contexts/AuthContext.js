import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/v1/auth/login', {
        username: email, // Backend expects 'username' field
        password
      });

      const { access_token, user: userData } = response.data;

      // Store token and user in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      // Update state
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      // Handle different error formats from FastAPI
      let errorMessage = 'Login failed';
      if (error.response?.data?.detail) {
        // detail can be a string or an array of validation errors
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          // Validation errors array
          errorMessage = error.response.data.detail.map(err => err.msg || err.message).join(', ');
        } else if (typeof error.response.data.detail === 'object') {
          // Single validation error object
          errorMessage = error.response.data.detail.msg || error.response.data.detail.message || 'Validation error';
        }
      }
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/v1/auth/register', userData);

      const { access_token, user: newUser } = response.data;

      // Store token and user in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(newUser));

      // Update state
      setUser(newUser);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      console.error('Registration failed:', error);
      // Handle different error formats from FastAPI
      let errorMessage = 'Registration failed';
      if (error.response?.data?.detail) {
        // detail can be a string or an array of validation errors
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          // Validation errors array
          errorMessage = error.response.data.detail.map(err => err.msg || err.message).join(', ');
        } else if (typeof error.response.data.detail === 'object') {
          // Single validation error object
          errorMessage = error.response.data.detail.msg || error.response.data.detail.message || 'Validation error';
        }
      }
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Clear state
    setUser(null);
    setIsAuthenticated(false);

    // Optional: Call logout endpoint
    if (api && api.post) {
      api.post('/api/v1/auth/logout').catch(() => {
        // Ignore logout errors
      });
    }
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    register,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};