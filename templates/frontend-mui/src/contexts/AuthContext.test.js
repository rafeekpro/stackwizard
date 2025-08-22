import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import { api } from '../services/api';

// Mock the API module
jest.mock('../services/api');

// Test component that uses the auth context
const TestComponent = () => {
  const { user, isAuthenticated, login, logout, register } = useAuth();
  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>
      <div data-testid="user-email">{user?.email || 'no-user'}</div>
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={() => logout()}>Logout</button>
      <button onClick={() => register({ email: 'new@example.com', password: 'password' })}>Register</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('should provide initial unauthenticated state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated');
    expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
  });

  it('should handle successful login', async () => {
    const mockResponse = {
      data: {
        access_token: 'test-token',
        token_type: 'Bearer',
        user: {
          id: '123',
          email: 'test@example.com',
          full_name: 'Test User'
        }
      }
    };

    api.post.mockResolvedValueOnce(mockResponse);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    
    await act(async () => {
      loginButton.click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });

    expect(localStorage.getItem('token')).toBe('test-token');
    // Check that URLSearchParams was used for form-data
    expect(api.post).toHaveBeenCalledTimes(1);
    const [[url, data, config]] = api.post.mock.calls;
    expect(url).toBe('/api/v1/auth/login');
    expect(data).toBeInstanceOf(URLSearchParams);
    expect(data.get('username')).toBe('test@example.com');
    expect(data.get('password')).toBe('password');
    expect(config.headers['Content-Type']).toBe('application/x-www-form-urlencoded');
  });

  it('should handle login failure', async () => {
    const mockError = new Error('Invalid credentials');
    api.post.mockRejectedValueOnce(mockError);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    
    await act(async () => {
      loginButton.click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
    });

    expect(localStorage.getItem('token')).toBeNull();
  });

  it('should handle logout', async () => {
    // Mock the logout API call
    api.post.mockResolvedValueOnce({ data: {} });
    
    // Set initial authenticated state
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user', JSON.stringify({
      id: '123',
      email: 'test@example.com'
    }));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Should load authenticated state from localStorage
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
    });

    const logoutButton = screen.getByText('Logout');
    
    await act(async () => {
      logoutButton.click();
    });

    expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated');
    expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('should handle successful registration', async () => {
    const mockResponse = {
      data: {
        access_token: 'new-token',
        token_type: 'Bearer',
        user: {
          id: '456',
          email: 'new@example.com',
          full_name: 'New User'
        }
      }
    };

    api.post.mockResolvedValueOnce(mockResponse);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const registerButton = screen.getByText('Register');
    
    await act(async () => {
      registerButton.click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('new@example.com');
    });

    expect(localStorage.getItem('token')).toBe('new-token');
    expect(api.post).toHaveBeenCalledWith('/api/v1/auth/register', {
      email: 'new@example.com',
      password: 'password'
    });
  });

  it('should load authenticated state from localStorage on mount', async () => {
    const userData = {
      id: '789',
      email: 'stored@example.com',
      full_name: 'Stored User'
    };

    localStorage.setItem('token', 'stored-token');
    localStorage.setItem('user', JSON.stringify(userData));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('stored@example.com');
    });
  });

  it('should throw error when useAuth is used outside AuthProvider', () => {
    // Suppress console.error for this test
    const originalError = console.error;
    console.error = jest.fn();

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    console.error = originalError;
  });
});