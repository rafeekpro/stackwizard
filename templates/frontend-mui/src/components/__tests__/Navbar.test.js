import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navbar from '../Navbar';
import { useAuth } from '../../contexts/AuthContext';

// Mock the useAuth hook
jest.mock('../../contexts/AuthContext', () => ({
  ...jest.requireActual('../../contexts/AuthContext'),
  useAuth: jest.fn(),
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Navbar Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Unauthenticated User', () => {
    beforeEach(() => {
      useAuth.mockReturnValue({
        user: null,
        logout: jest.fn(),
      });
    });

    test('shows public navigation items', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // Check for public pages using tab links
      const tabs = screen.getByRole('tablist');
      expect(within(tabs).getByText('Home')).toBeInTheDocument();
      expect(within(tabs).getByText('About')).toBeInTheDocument();
      
      // Should not show authenticated pages
      expect(within(tabs).queryByText('Users')).not.toBeInTheDocument();
      expect(within(tabs).queryByText('Items')).not.toBeInTheDocument();
      expect(within(tabs).queryByText('My Account')).not.toBeInTheDocument();
    });

    test('shows Sign In and Sign Up buttons', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // Check for auth buttons
      const signInButtons = screen.getAllByText('Sign In');
      const signUpButtons = screen.getAllByText('Sign Up');
      
      // Should have at least one of each
      expect(signInButtons.length).toBeGreaterThan(0);
      expect(signUpButtons.length).toBeGreaterThan(0);
      
      // Should not show logout
      expect(screen.queryByText('Logout')).not.toBeInTheDocument();
    });

    test('Sign In button navigates to login page', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const signInButton = screen.getAllByText('Sign In')[0];
      fireEvent.click(signInButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    test('Sign Up button navigates to register page', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const signUpButton = screen.getAllByText('Sign Up')[0];
      fireEvent.click(signUpButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/register');
    });
  });

  describe('Authenticated User', () => {
    const mockLogout = jest.fn();
    
    beforeEach(() => {
      useAuth.mockReturnValue({
        user: { id: 1, email: 'test@example.com' },
        logout: mockLogout,
      });
    });

    test('shows authenticated navigation items', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // Check for all authenticated pages
      const tabs = screen.getByRole('tablist');
      expect(within(tabs).getByText('Home')).toBeInTheDocument();
      expect(within(tabs).getByText('About')).toBeInTheDocument();
      expect(within(tabs).getByText('Users')).toBeInTheDocument();
      expect(within(tabs).getByText('Items')).toBeInTheDocument();
      expect(within(tabs).getByText('My Account')).toBeInTheDocument();
    });

    test('shows Logout button', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // Check for logout button
      const logoutButtons = screen.getAllByText('Logout');
      expect(logoutButtons.length).toBeGreaterThan(0);
      
      // Should not show sign in/sign up
      expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
      expect(screen.queryByText('Sign Up')).not.toBeInTheDocument();
    });

    test('Logout button calls logout function', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const logoutButton = screen.getAllByText('Logout')[0];
      fireEvent.click(logoutButton);
      
      expect(mockLogout).toHaveBeenCalled();
    });

    test('My Account link navigates to my-account page', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const tabs = screen.getByRole('tablist');
      const myAccountTab = within(tabs).getByText('My Account');
      
      // The tab itself is a link
      expect(myAccountTab.closest('a')).toHaveAttribute('href', '/my-account');
    });
  });

  describe('Navigation Structure', () => {
    test('renders AppBar with correct structure', () => {
      useAuth.mockReturnValue({
        user: null,
        logout: jest.fn(),
      });
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // Check for AppBar components
      expect(screen.getByRole('banner')).toBeInTheDocument(); // AppBar has banner role
      expect(screen.getByRole('tablist')).toBeInTheDocument(); // Tabs component
    });
  });
});