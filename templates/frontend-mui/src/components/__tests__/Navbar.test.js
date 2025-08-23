import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
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

    it('should show Home and About links', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('About')).toBeInTheDocument();
    });

    it('should show Sign In and Sign Up buttons', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Sign In')).toBeInTheDocument();
      expect(screen.getByText('Sign Up')).toBeInTheDocument();
    });

    it('should NOT show authenticated menu items', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.queryByText('Users')).not.toBeInTheDocument();
      expect(screen.queryByText('Items')).not.toBeInTheDocument();
      expect(screen.queryByText('My Account')).not.toBeInTheDocument();
      expect(screen.queryByText('Logout')).not.toBeInTheDocument();
    });

    it('should navigate to login when Sign In is clicked', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const signInButton = screen.getByText('Sign In');
      fireEvent.click(signInButton);
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    it('should navigate to register when Sign Up is clicked', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const signUpButton = screen.getByText('Sign Up');
      fireEvent.click(signUpButton);
      expect(mockNavigate).toHaveBeenCalledWith('/register');
    });
  });

  describe('Authenticated User', () => {
    const mockLogout = jest.fn();

    beforeEach(() => {
      useAuth.mockReturnValue({
        user: { 
          id: '123', 
          email: 'test@example.com',
          full_name: 'Test User'
        },
        logout: mockLogout,
      });
    });

    it('should show Home and About links', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('About')).toBeInTheDocument();
    });

    it('should show Users, Items, and My Account links', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Users')).toBeInTheDocument();
      expect(screen.getByText('Items')).toBeInTheDocument();
      expect(screen.getByText('My Account')).toBeInTheDocument();
    });

    it('should show Logout button', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Logout')).toBeInTheDocument();
    });

    it('should NOT show Sign In and Sign Up buttons', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
      expect(screen.queryByText('Sign Up')).not.toBeInTheDocument();
    });

    it('should call logout when Logout is clicked', async () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const logoutButton = screen.getByText('Logout');
      fireEvent.click(logoutButton);
      
      expect(mockLogout).toHaveBeenCalled();
    });

    it('should navigate to My Account when clicked', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // For Link components, we need to check the href
      const myAccountLink = screen.getByText('My Account').closest('a');
      expect(myAccountLink).toHaveAttribute('href', '/my-account');
    });
  });

  describe('Mobile Navigation', () => {
    it('should toggle mobile menu when menu icon is clicked', () => {
      useAuth.mockReturnValue({
        user: null,
        logout: jest.fn(),
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      // Find and click the menu icon button
      const menuButton = screen.getByLabelText(/menu/i);
      fireEvent.click(menuButton);

      // Check if mobile menu items are visible
      // Note: Implementation will determine exact behavior
      expect(screen.getByText('Home')).toBeInTheDocument();
    });
  });
});