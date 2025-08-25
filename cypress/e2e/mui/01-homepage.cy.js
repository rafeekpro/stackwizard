/// <reference types="cypress" />

describe('MUI Template - Homepage', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should load the homepage successfully', () => {
    cy.contains('Welcome to Your Full-Stack Application').should('be.visible');
  });

  it('should display health status indicators', () => {
    // Wait for health checks to complete
    cy.wait(2000);
    
    // Check API status
    cy.get('[data-testid="api-status"]').should('exist');
    
    // Check Database status
    cy.get('[data-testid="db-status"]').should('exist');
  });

  it('should have working navigation', () => {
    // Check navbar exists
    cy.get('header').should('be.visible');
    
    // Check navigation items
    cy.contains('Home').should('be.visible');
    cy.contains('About').should('be.visible');
    cy.contains('Sign In').should('be.visible');
    cy.contains('Sign Up').should('be.visible');
  });

  it('should navigate to About page', () => {
    cy.contains('About').click();
    cy.url().should('include', '/about');
    cy.contains('About This Application').should('be.visible');
  });

  it('should have Material UI styling', () => {
    // Check for MUI AppBar
    cy.get('.MuiAppBar-root').should('exist');
    
    // Check for MUI buttons
    cy.get('.MuiButton-root').should('exist');
    
    // Check navbar has blue background
    cy.get('.MuiAppBar-root')
      .should('have.css', 'background-color')
      .and('include', 'rgb(25, 118, 210)'); // MUI blue color
  });

  it('should be responsive', () => {
    // Desktop view
    cy.viewport(1920, 1080);
    cy.get('.MuiContainer-root').should('be.visible');
    
    // Tablet view
    cy.viewport(768, 1024);
    cy.get('.MuiContainer-root').should('be.visible');
    
    // Mobile view
    cy.viewport(375, 667);
    cy.get('[aria-label="menu"]').should('be.visible'); // Mobile menu icon
  });
});