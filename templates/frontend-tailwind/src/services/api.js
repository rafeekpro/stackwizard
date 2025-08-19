import axios from 'axios';

// Get API URL from environment or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Export setup function for testing
export const setupInterceptors = () => {
  // This function is primarily for testing purposes
  // Interceptors are set up automatically when the module loads
};

export default api;

// API functions
export const checkHealth = async (endpoint = '') => {
  const response = await api.get(`/api/health${endpoint}`);
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get('/api/v1/users/');
  return response.data;
};

export const getUser = async (userId) => {
  const response = await api.get(`/api/v1/users/${userId}`);
  return response.data;
};

export const createUser = async (userData) => {
  // Users should be created through the registration endpoint
  const registrationData = {
    email: userData.email,
    password: userData.password || 'TempPass123!',  // Provide a default if not specified
    full_name: userData.full_name || userData.username || 'New User'
  };
  
  // Only add username if it's not empty
  if (userData.username && userData.username.trim()) {
    registrationData.username = userData.username;
  }
  
  try {
    const response = await api.post('/api/v1/auth/register', registrationData);
    return response.data.user;  // Return just the user object
  } catch (error) {
    // If registration fails, throw more detailed error
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (typeof detail === 'string') {
        throw new Error(detail);
      } else if (Array.isArray(detail)) {
        const messages = detail.map(d => d.msg || d.message || 'Validation error').join(', ');
        throw new Error(messages);
      }
    }
    throw error;
  }
};

export const updateUser = async (userId, userData) => {
  const response = await api.put(`/api/v1/users/${userId}`, userData);
  return response.data;
};

export const deleteUser = async (userId) => {
  const response = await api.delete(`/api/v1/users/${userId}`);
  return response.data;
};

export const getItems = async () => {
  const response = await api.get('/api/v1/items/');
  return response.data;
};

export const getItem = async (itemId) => {
  const response = await api.get(`/api/v1/items/${itemId}`);
  return response.data;
};

export const createItem = async (itemData) => {
  const response = await api.post('/api/v1/items/', itemData);
  return response.data;
};

export const updateItem = async (itemId, itemData) => {
  const response = await api.put(`/api/v1/items/${itemId}`, itemData);
  return response.data;
};

export const deleteItem = async (itemId) => {
  const response = await api.delete(`/api/v1/items/${itemId}`);
  return response.data;
};