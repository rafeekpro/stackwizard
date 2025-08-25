/// <reference types="cypress" />

describe('Tailwind Template - Homepage', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should load the homepage successfully', () => {
    cy.contains('Welcome to Your Full-Stack Application').should('be.visible');
  });

  it('should have Tailwind CSS styling', () => {
    // Check for Tailwind classes
    cy.get('[class*="bg-"]').should('exist');
    cy.get('[class*="text-"]').should('exist');
    cy.get('[class*="flex"]').should('exist');
    
    // Check navbar has dark background
    cy.get('nav')
      .should('have.class', 'bg-gray-800')
      .or('have.class', 'bg-gray-900');
  });

  it('should have working navigation', () => {
    // Check navbar exists
    cy.get('nav').should('be.visible');
    
    // Check navigation items
    cy.contains('Home').should('be.visible');
    cy.contains('About').should('be.visible');
    cy.contains('Sign In').should('be.visible');
    cy.contains('Sign Up').should('be.visible');
  });

  it('should display health status with Tailwind badges', () => {
    cy.wait(2000);
    
    // Check for Tailwind styled badges
    cy.get('[class*="rounded-full"]').should('exist');
    cy.get('[class*="px-"]').should('exist');
    cy.get('[class*="py-"]').should('exist');
  });

  it('should be responsive with Tailwind breakpoints', () => {
    // Desktop view
    cy.viewport(1920, 1080);
    cy.get('[class*="container"]').should('be.visible');
    cy.get('[class*="lg:"]').should('exist');
    
    // Tablet view
    cy.viewport(768, 1024);
    cy.get('[class*="md:"]').should('exist');
    
    // Mobile view
    cy.viewport(375, 667);
    cy.get('[class*="sm:"]').should('exist');
    // Mobile menu button
    cy.get('button[aria-label*="menu"], button[class*="mobile-menu"]').should('be.visible');
  });

  it('should have Headless UI components', () => {
    // Mobile view to see menu
    cy.viewport(375, 667);
    
    // Click mobile menu button
    cy.get('button').first().click();
    
    // Check for Headless UI transitions
    cy.get('[class*="transition"]').should('exist');
  });

  it('should navigate to About page', () => {
    cy.contains('About').click();
    cy.url().should('include', '/about');
    cy.contains('About This Application').should('be.visible');
    
    // Check for Tailwind card styling
    cy.get('[class*="shadow"]').should('exist');
    cy.get('[class*="rounded"]').should('exist');
  });
});