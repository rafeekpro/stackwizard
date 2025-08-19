import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import ItemsPage from './pages/ItemsPage';
import AboutPage from './pages/AboutPage';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <AuthProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute>
                  <DashboardPage />
                </PrivateRoute>
              } 
            />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/items" element={<ItemsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route 
              path="/admin" 
              element={
                <PrivateRoute requireAdmin={true}>
                  <AdminDashboard />
                </PrivateRoute>
              } 
            />
          </Routes>
        </Box>
      </Box>
    </AuthProvider>
  );
}

export default App;