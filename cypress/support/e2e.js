// ***********************************************************
// This file is processed and loaded automatically before test files.
// ***********************************************************

// Import commands.js
import './commands'

// Handle uncaught exceptions
Cypress.on('uncaught:exception', (err, runnable) => {
  // Return false to prevent the test from failing
  // on uncaught exceptions from the application
  if (err.message.includes('ResizeObserver')) {
    return false;
  }
  if (err.message.includes('Network request failed')) {
    return false;
  }
  // Let other errors fail the test
  return true;
});