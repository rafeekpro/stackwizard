import axios from 'axios';

// Use relative URLs to leverage the proxy in package.json
const API_BASE_URL = '';

const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
});

// Token storage
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
export const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
};
export const clearTokens = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// Auth functions
export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email); // OAuth2 expects 'username' field
  formData.append('password', password);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    
    const data = await response.json();
    const { access_token, refresh_token } = data;
    setTokens(access_token, refresh_token);
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const register = async (email, password, fullName) => {
  const response = await axios.post(`${API_BASE_URL}/api/v1/auth/register`, {
    email,
    password,
    full_name: fullName,
  }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

export const logout = () => {
  clearTokens();
  window.location.href = '/';
};

export const isAuthenticated = () => {
  return !!getToken();
};

export const getCurrentUser = async () => {
  const token = getToken();
  if (!token) {
    throw new Error('No token found');
  }
  
  const response = await axios.get(`${API_BASE_URL}/api/v1/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.data;
};