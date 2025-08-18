// Import commands
import './commands';

// Import third-party commands
import 'cypress-file-upload';
import 'cypress-wait-until';
import 'cypress-real-events';
import '@cypress/grep';

// Global before each hook
beforeEach(() => {
  // Clear cookies and local storage before each test
  cy.clearCookies();
  cy.clearLocalStorage();
  
  // Set default viewport
  cy.viewport(1280, 720);
  
  // Intercept common API calls
  cy.intercept('GET', '**/api/health', { statusCode: 200, body: { status: 'healthy' } }).as('healthCheck');
  cy.intercept('POST', '**/api/v1/auth/login').as('loginRequest');
  cy.intercept('POST', '**/api/v1/auth/register').as('registerRequest');
  cy.intercept('GET', '**/api/v1/users/me').as('getCurrentUser');
});

// Global after each hook
afterEach(() => {
  // Take screenshot on failure
  if (Cypress.currentTest.state === 'failed') {
    const testName = Cypress.currentTest.title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    cy.screenshot(`failed_${testName}`);
  }
});

// Handle uncaught exceptions
Cypress.on('uncaught:exception', (err, runnable) => {
  // Log the error but don't fail the test
  console.error('Uncaught exception:', err);
  
  // Return false to prevent the test from failing
  // In production, you might want to be more selective about which errors to ignore
  if (err.message.includes('ResizeObserver loop limit exceeded')) {
    return false;
  }
  
  // Let other errors fail the test
  return true;
});

// Custom error messages
Cypress.on('fail', (error, runnable) => {
  // Add more context to error messages
  if (error.message.includes('Timed out')) {
    error.message = `${error.message}\n\nConsider increasing the timeout or checking if the element exists`;
  }
  
  throw error;
});

// Add custom chai assertions
chai.Assertion.addMethod('inViewport', function () {
  const subject = this._obj;
  const bottom = Cypress.$(cy.state('window')).height();
  const rect = subject[0].getBoundingClientRect();
  
  this.assert(
    rect.top < bottom && rect.bottom > 0,
    'expected #{this} to be in viewport',
    'expected #{this} not to be in viewport',
    this._obj
  );
});

// Global test configuration
before(() => {
  // Perform global setup
  cy.log('Starting test suite');
  
  // Check if API is healthy
  cy.request({
    url: `${Cypress.env('apiUrl')}/api/health`,
    failOnStatusCode: false,
  }).then((response) => {
    if (response.status !== 200) {
      throw new Error('API is not healthy. Please ensure the backend is running.');
    }
  });
});

after(() => {
  // Perform global cleanup
  cy.log('Test suite completed');
});