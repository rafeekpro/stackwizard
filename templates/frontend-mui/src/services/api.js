import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const checkHealth = async (endpoint = '') => {
  const response = await api.get(`/api/health${endpoint}`);
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get('/api/users');
  return response.data;
};

export const getUser = async (userId) => {
  const response = await api.get(`/api/users/${userId}`);
  return response.data;
};

export const createUser = async (userData) => {
  const response = await api.post('/api/users', userData);
  return response.data;
};

export const updateUser = async (userId, userData) => {
  const response = await api.put(`/api/users/${userId}`, userData);
  return response.data;
};

export const deleteUser = async (userId) => {
  const response = await api.delete(`/api/users/${userId}`);
  return response.data;
};

export const getItems = async () => {
  const response = await api.get('/api/items');
  return response.data;
};

export const getItem = async (itemId) => {
  const response = await api.get(`/api/items/${itemId}`);
  return response.data;
};

export const createItem = async (itemData) => {
  const response = await api.post('/api/items', itemData);
  return response.data;
};

export const updateItem = async (itemId, itemData) => {
  const response = await api.put(`/api/items/${itemId}`, itemData);
  return response.data;
};

export const deleteItem = async (itemId) => {
  const response = await api.delete(`/api/items/${itemId}`);
  return response.data;
};

export default api;