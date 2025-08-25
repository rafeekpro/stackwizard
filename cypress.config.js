import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    
    setupNodeEvents(on, config) {
      // Setup different configs for different templates
      const template = config.env.template || 'mui';
      
      if (template === 'tailwind') {
        config.specPattern = 'cypress/e2e/tailwind/**/*.cy.js';
      } else {
        config.specPattern = 'cypress/e2e/mui/**/*.cy.js';
      }
      
      return config;
    },
  },
  
  env: {
    apiUrl: 'http://localhost:8000',
    template: 'mui',
    adminEmail: 'admin@example.com',
    adminPassword: 'admin123',
    testUserEmail: 'test@example.com',
    testUserPassword: 'test123'
  }
});