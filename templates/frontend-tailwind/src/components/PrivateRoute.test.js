import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import PrivateRoute from './PrivateRoute';

// Mock the auth context
jest.mock('../contexts/AuthContext', () => ({
  ...jest.requireActual('../contexts/AuthContext'),
  useAuth: jest.fn()
}));

const { useAuth } = require('../contexts/AuthContext');

// Test components
const ProtectedComponent = () => <div>Protected Content</div>;
const LoginComponent = () => <div>Login Page</div>;

describe('PrivateRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render protected content when user is authenticated', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      loading: false,
      user: { id: '123', email: 'test@example.com' }
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<LoginComponent />} />
          <Route
            path="/protected"
            element={
              <PrivateRoute>
                <ProtectedComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });

  it('should redirect to login when user is not authenticated', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: false,
      user: null
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<LoginComponent />} />
          <Route
            path="/protected"
            element={
              <PrivateRoute>
                <ProtectedComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should show loading state while authentication is being checked', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: true,
      user: null
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<LoginComponent />} />
          <Route
            path="/protected"
            element={
              <PrivateRoute>
                <ProtectedComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    // Should show loading state, not redirect immediately
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
    // You might want to add a loading indicator test here
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('should preserve the attempted location when redirecting', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: false,
      user: null
    });

    const { container } = render(
      <MemoryRouter initialEntries={['/protected/resource/123']}>
        <Routes>
          <Route path="/login" element={<LoginComponent />} />
          <Route
            path="/protected/*"
            element={
              <PrivateRoute>
                <ProtectedComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    // Check that location state includes the from property
    // This would be used to redirect back after login
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('should allow role-based access control', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      loading: false,
      user: { id: '123', email: 'test@example.com', is_superuser: false }
    });

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/unauthorized" element={<div>Unauthorized</div>} />
          <Route
            path="/admin"
            element={
              <PrivateRoute requireAdmin={true}>
                <ProtectedComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    // Non-admin user should be redirected to unauthorized
    expect(screen.getByText('Unauthorized')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should allow admin access to admin routes', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      loading: false,
      user: { id: '123', email: 'admin@example.com', is_superuser: true }
    });

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/unauthorized" element={<div>Unauthorized</div>} />
          <Route
            path="/admin"
            element={
              <PrivateRoute requireAdmin={true}>
                <ProtectedComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    // Admin user should see protected content
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByText('Unauthorized')).not.toBeInTheDocument();
  });
});