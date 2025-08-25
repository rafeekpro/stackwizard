/// <reference types="cypress" />

describe('MUI Template - Authentication', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Registration', () => {
    it('should navigate to registration page', () => {
      cy.contains('Sign Up').click();
      cy.url().should('include', '/register');
      cy.contains('Create Account').should('be.visible');
    });

    it('should register a new user', () => {
      const uniqueEmail = `user_${Date.now()}@test.com`;
      
      cy.contains('Sign Up').click();
      
      // Fill registration form
      cy.get('input[name="email"]').type(uniqueEmail);
      cy.get('input[name="username"]').type('testuser');
      cy.get('input[name="full_name"]').type('Test User');
      cy.get('input[name="password"]').type('Test123!@#');
      cy.get('input[name="confirmPassword"]').type('Test123!@#');
      
      // Submit form
      cy.get('button[type="submit"]').click();
      
      // Should redirect to login or dashboard
      cy.url().should('not.include', '/register');
    });

    it('should show validation errors', () => {
      cy.contains('Sign Up').click();
      
      // Try to submit empty form
      cy.get('button[type="submit"]').click();
      
      // Should show required field errors
      cy.contains('required').should('be.visible');
    });

    it('should validate password match', () => {
      cy.contains('Sign Up').click();
      
      cy.get('input[name="password"]').type('Test123!@#');
      cy.get('input[name="confirmPassword"]').type('Different123!@#');
      
      cy.get('button[type="submit"]').click();
      
      // Should show password mismatch error
      cy.contains('Passwords do not match').should('be.visible');
    });
  });

  describe('Login', () => {
    it('should navigate to login page', () => {
      cy.contains('Sign In').click();
      cy.url().should('include', '/login');
      cy.contains('Sign In').should('be.visible');
    });

    it('should login with admin credentials', () => {
      cy.contains('Sign In').click();
      
      // Fill login form
      cy.get('input[name="email"]').type(Cypress.env('adminEmail'));
      cy.get('input[name="password"]').type(Cypress.env('adminPassword'));
      
      // Submit form
      cy.get('button[type="submit"]').click();
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard');
      
      // Navigation should update
      cy.contains('Logout').should('be.visible');
      cy.contains('Sign In').should('not.exist');
    });

    it('should show error for invalid credentials', () => {
      cy.contains('Sign In').click();
      
      cy.get('input[name="email"]').type('invalid@example.com');
      cy.get('input[name="password"]').type('wrongpassword');
      
      cy.get('button[type="submit"]').click();
      
      // Should show error message
      cy.contains('Invalid').should('be.visible');
    });

    it('should have Material UI form styling', () => {
      cy.contains('Sign In').click();
      
      // Check for MUI TextField
      cy.get('.MuiTextField-root').should('exist');
      
      // Check for MUI Button
      cy.get('.MuiButton-containedPrimary').should('exist');
      
      // Check for MUI Paper (form container)
      cy.get('.MuiPaper-root').should('exist');
    });
  });

  describe('Logout', () => {
    beforeEach(() => {
      // Login first
      cy.contains('Sign In').click();
      cy.get('input[name="email"]').type(Cypress.env('adminEmail'));
      cy.get('input[name="password"]').type(Cypress.env('adminPassword'));
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });

    it('should logout successfully', () => {
      cy.contains('Logout').click();
      
      // Should redirect to home
      cy.url().should('eq', Cypress.config('baseUrl') + '/');
      
      // Navigation should update
      cy.contains('Sign In').should('be.visible');
      cy.contains('Logout').should('not.exist');
    });
  });
});