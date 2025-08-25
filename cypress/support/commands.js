// ***********************************************
// Custom Cypress Commands
// ***********************************************

// Login command
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login');
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
  cy.url().should('not.include', '/login');
});

// Logout command
Cypress.Commands.add('logout', () => {
  cy.contains('Logout').click();
  cy.url().should('eq', Cypress.config('baseUrl') + '/');
});

// Wait for API to be ready
Cypress.Commands.add('waitForApi', () => {
  cy.request({
    url: `${Cypress.env('apiUrl')}/health`,
    retryOnStatusCodeFailure: true,
    retryOnNetworkFailure: true,
    timeout: 30000
  }).its('status').should('eq', 200);
});

// Create a test user via API
Cypress.Commands.add('createTestUser', (userData) => {
  const user = {
    email: userData.email || `test_${Date.now()}@example.com`,
    username: userData.username || 'testuser',
    full_name: userData.full_name || 'Test User',
    password: userData.password || 'Test123!@#',
    ...userData
  };
  
  cy.request('POST', `${Cypress.env('apiUrl')}/api/v1/users/`, user);
  return cy.wrap(user);
});

// Check element visibility with retry
Cypress.Commands.add('shouldBeVisible', (selector, options = {}) => {
  const { timeout = 10000 } = options;
  cy.get(selector, { timeout }).should('be.visible');
});

// Check MUI components
Cypress.Commands.add('checkMuiComponents', () => {
  cy.get('.MuiAppBar-root').should('exist');
  cy.get('.MuiButton-root').should('exist');
  cy.get('.MuiContainer-root').should('exist');
});

// Check Tailwind classes
Cypress.Commands.add('checkTailwindClasses', () => {
  cy.get('[class*="bg-"]').should('exist');
  cy.get('[class*="text-"]').should('exist');
  cy.get('[class*="flex"]').should('exist');
  cy.get('[class*="rounded"]').should('exist');
});

// Take named screenshot
Cypress.Commands.add('takeNamedScreenshot', (name) => {
  cy.screenshot(name, {
    capture: 'viewport',
    overwrite: true
  });
});

// Wait for loading to complete
Cypress.Commands.add('waitForLoading', () => {
  cy.get('[class*="loading"], [class*="spinner"], .MuiCircularProgress-root', { timeout: 100 })
    .should('not.exist');
});