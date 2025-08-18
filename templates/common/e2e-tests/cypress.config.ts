import { defineConfig } from 'cypress';
import createBundler from '@bahmutov/cypress-esbuild-preprocessor';
import { addCucumberPreprocessorPlugin } from '@badeball/cypress-cucumber-preprocessor';
import { createEsbuildPlugin } from '@badeball/cypress-cucumber-preprocessor/esbuild';

export default defineConfig({
  e2e: {
    async setupNodeEvents(on, config) {
      // Cucumber preprocessor
      await addCucumberPreprocessorPlugin(on, config);
      
      // Esbuild bundler
      on(
        'file:preprocessor',
        createBundler({
          plugins: [createEsbuildPlugin(config)],
        })
      );

      // Task for database operations
      on('task', {
        // Database cleanup task
        async resetDb() {
          // Add database reset logic here
          console.log('Database reset');
          return null;
        },
        
        // Seed test data
        async seedTestData(data) {
          // Add seeding logic here
          console.log('Seeding test data:', data);
          return null;
        },
        
        // Custom logging
        log(message) {
          console.log(message);
          return null;
        },
      });

      // Load environment-specific config
      const environmentName = config.env.environment || 'local';
      const environmentFilename = `./cypress/config/${environmentName}.json`;
      
      try {
        const settings = require(environmentFilename);
        config.baseUrl = settings.baseUrl;
        config.env = { ...config.env, ...settings.env };
      } catch (e) {
        console.log(`No config file found for environment: ${environmentName}`);
      }

      return config;
    },
    
    // Base configuration
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    
    // Timeouts
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    
    // Test isolation
    testIsolation: true,
    
    // Retries
    retries: {
      runMode: 2,
      openMode: 0
    },
    
    // Folders
    specPattern: 'cypress/e2e/**/*.feature',
    supportFile: 'cypress/support/e2e.ts',
    downloadsFolder: 'cypress/downloads',
    videosFolder: 'cypress/videos',
    screenshotsFolder: 'cypress/screenshots',
    
    // Environment variables
    env: {
      apiUrl: 'http://localhost:8000',
      coverage: false,
      TAGS: '',
      
      // Test users
      adminEmail: 'admin@example.com',
      adminPassword: 'Admin123!',
      testUserEmail: 'testuser@example.com',
      testUserPassword: 'TestUser123!',
    },
    
    // Exclude test files
    excludeSpecPattern: [
      '*.hot-update.js',
      '**/__snapshots__/*',
      '**/__image_snapshots__/*',
    ],
  },
  
  // Component testing config (if needed)
  component: {
    devServer: {
      framework: 'react',
      bundler: 'webpack',
    },
    specPattern: 'cypress/component/**/*.cy.{js,jsx,ts,tsx}',
  },
});