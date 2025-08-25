/// <reference types="cypress" />

describe('MUI Template - Dashboard & CRUD', () => {
  beforeEach(() => {
    // Login as admin
    cy.visit('/login');
    cy.get('input[name="email"]').type(Cypress.env('adminEmail'));
    cy.get('input[name="password"]').type(Cypress.env('adminPassword'));
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });

  describe('Dashboard', () => {
    it('should display dashboard cards', () => {
      cy.get('.MuiCard-root').should('have.length.at.least', 3);
      
      // Check for specific cards
      cy.contains('Total Users').should('be.visible');
      cy.contains('Total Items').should('be.visible');
      cy.contains('System Status').should('be.visible');
    });

    it('should have working navigation menu', () => {
      cy.contains('Users').should('be.visible');
      cy.contains('Items').should('be.visible');
      cy.contains('My Account').should('be.visible');
    });
  });

  describe('Users Management', () => {
    beforeEach(() => {
      cy.contains('Users').click();
      cy.url().should('include', '/users');
    });

    it('should display users table', () => {
      // Check for MUI DataGrid or Table
      cy.get('.MuiTable-root, .MuiDataGrid-root').should('be.visible');
      
      // Check for table headers
      cy.contains('Email').should('be.visible');
      cy.contains('Username').should('be.visible');
      cy.contains('Actions').should('be.visible');
    });

    it('should open create user dialog', () => {
      cy.contains('button', 'Add User').click();
      
      // Check dialog opened
      cy.get('.MuiDialog-root').should('be.visible');
      cy.contains('Create New User').should('be.visible');
    });

    it('should create a new user', () => {
      const uniqueEmail = `newuser_${Date.now()}@test.com`;
      
      cy.contains('button', 'Add User').click();
      
      // Fill form in dialog
      cy.get('.MuiDialog-root input[name="email"]').type(uniqueEmail);
      cy.get('.MuiDialog-root input[name="username"]').type('newuser');
      cy.get('.MuiDialog-root input[name="full_name"]').type('New User');
      cy.get('.MuiDialog-root input[name="password"]').type('NewUser123!');
      
      // Submit
      cy.get('.MuiDialog-root button').contains('Create').click();
      
      // Check user appears in table
      cy.contains(uniqueEmail).should('be.visible');
    });

    it('should edit a user', () => {
      // Click edit on first non-admin user
      cy.get('[data-testid="edit-button"]').first().click();
      
      // Dialog should open
      cy.get('.MuiDialog-root').should('be.visible');
      cy.contains('Edit User').should('be.visible');
      
      // Change name
      cy.get('.MuiDialog-root input[name="full_name"]').clear().type('Updated Name');
      
      // Save
      cy.get('.MuiDialog-root button').contains('Save').click();
      
      // Check update reflected
      cy.contains('Updated Name').should('be.visible');
    });

    it('should delete a user', () => {
      // Count initial users
      let initialCount;
      cy.get('tbody tr, .MuiDataGrid-row').then($rows => {
        initialCount = $rows.length;
      });
      
      // Click delete on first non-admin user
      cy.get('[data-testid="delete-button"]').first().click();
      
      // Confirm deletion
      cy.contains('button', 'Confirm').click();
      
      // Check user count decreased
      cy.get('tbody tr, .MuiDataGrid-row').should('have.length.lessThan', initialCount);
    });
  });

  describe('Items Management', () => {
    beforeEach(() => {
      cy.contains('Items').click();
      cy.url().should('include', '/items');
    });

    it('should display items list', () => {
      cy.get('.MuiCard-root, .MuiTable-root').should('be.visible');
    });

    it('should create a new item', () => {
      const itemName = `Test Item ${Date.now()}`;
      
      cy.contains('button', 'Add Item').click();
      
      // Fill form
      cy.get('input[name="name"]').type(itemName);
      cy.get('textarea[name="description"]').type('Test item description');
      cy.get('input[name="price"]').type('99.99');
      
      // Submit
      cy.contains('button', 'Create').click();
      
      // Check item appears
      cy.contains(itemName).should('be.visible');
    });

    it('should display item details', () => {
      // Click on first item
      cy.get('.MuiCard-root, tbody tr').first().click();
      
      // Should show details
      cy.contains('Description').should('be.visible');
      cy.contains('Price').should('be.visible');
    });
  });

  describe('My Account', () => {
    beforeEach(() => {
      cy.contains('My Account').click();
      cy.url().should('include', '/my-account');
    });

    it('should display account tabs', () => {
      // Check for MUI Tabs
      cy.get('.MuiTabs-root').should('be.visible');
      
      cy.contains('Profile').should('be.visible');
      cy.contains('Password').should('be.visible');
      cy.contains('Statistics').should('be.visible');
    });

    it('should update profile', () => {
      cy.contains('Profile').click();
      
      // Update name
      cy.get('input[name="full_name"]').clear().type('Updated Admin Name');
      
      // Save
      cy.contains('button', 'Save').click();
      
      // Check success message
      cy.contains('successfully').should('be.visible');
    });

    it('should show statistics', () => {
      cy.contains('Statistics').click();
      
      // Check statistics display
      cy.contains('Total Items').should('be.visible');
      cy.contains('Account Created').should('be.visible');
      cy.contains('Last Login').should('be.visible');
    });

    it('should have Material UI components', () => {
      // Check for MUI components
      cy.get('.MuiTabs-root').should('exist');
      cy.get('.MuiTab-root').should('have.length', 3);
      cy.get('.MuiTextField-root').should('exist');
      cy.get('.MuiButton-root').should('exist');
    });
  });
});