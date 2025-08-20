import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Box, CircularProgress } from '@mui/material';

const PrivateRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        data-testid="loading-spinner"
      >
        <CircularProgress />
      </Box>
    );
  }

  // Check if user is not authenticated
  if (!isAuthenticated) {
    // Redirect to login page while preserving the attempted location
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check admin requirements
  if (requireAdmin && !user?.is_superuser) {
    return <Navigate to="/unauthorized" replace />;
  }

  // User is authenticated (and admin if required), render the protected component
  return children;
};

export default PrivateRoute;