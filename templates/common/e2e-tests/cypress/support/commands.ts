/// <reference types="cypress" />

// Authentication commands
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-cy=email-input]').type(email);
    cy.get('[data-cy=password-input]').type(password);
    cy.get('[data-cy=login-button]').click();
    cy.url().should('not.include', '/login');
  });
});

Cypress.Commands.add('loginAsAdmin', () => {
  cy.login(Cypress.env('adminEmail'), Cypress.env('adminPassword'));
});

Cypress.Commands.add('loginAsUser', () => {
  cy.login(Cypress.env('testUserEmail'), Cypress.env('testUserPassword'));
});

Cypress.Commands.add('logout', () => {
  cy.get('[data-cy=logout-button]').click();
});

// API commands
Cypress.Commands.add('apiLogin', (email: string, password: string) => {
  return cy.request('POST', `${Cypress.env('apiUrl')}/api/v1/auth/login`, {
    email,
    password,
  }).then((response) => {
    window.localStorage.setItem('authToken', response.body.access_token);
    return response.body;
  });
});

Cypress.Commands.add('apiRequest', (method: string, url: string, body?: any) => {
  const token = window.localStorage.getItem('authToken');
  return cy.request({
    method,
    url: `${Cypress.env('apiUrl')}${url}`,
    body,
    headers: {
      Authorization: token ? `Bearer ${token}` : undefined,
    },
  });
});

// User management commands
Cypress.Commands.add('createUser', (userData: {
  email: string;
  username?: string;
  password?: string;
  role?: string;
}) => {
  const defaultData = {
    username: userData.email.split('@')[0],
    password: 'TestPass123!',
    role: 'user',
    ...userData,
  };

  return cy.apiRequest('POST', '/api/v1/admin/users', defaultData);
});

Cypress.Commands.add('deleteUser', (email: string) => {
  return cy.apiRequest('GET', `/api/v1/admin/users?email=${email}`)
    .then((response) => {
      if (response.body.length > 0) {
        const userId = response.body[0].id;
        return cy.apiRequest('DELETE', `/api/v1/admin/users/${userId}`);
      }
    });
});

// Database commands
Cypress.Commands.add('resetDatabase', () => {
  cy.task('resetDb');
});

Cypress.Commands.add('seedTestData', (data?: any) => {
  cy.task('seedTestData', data);
});

// File upload commands
Cypress.Commands.add('uploadFile', (fileName: string, selector: string) => {
  cy.fixture(fileName).then((fileContent) => {
    cy.get(selector).attachFile({
      fileContent: fileContent.toString(),
      fileName,
      mimeType: 'application/octet-stream',
    });
  });
});

// Assertion helpers
Cypress.Commands.add('shouldBeVisible', (selector: string) => {
  cy.get(selector).should('be.visible');
});

Cypress.Commands.add('shouldContainText', (selector: string, text: string) => {
  cy.get(selector).should('contain', text);
});

Cypress.Commands.add('shouldHaveValue', (selector: string, value: string) => {
  cy.get(selector).should('have.value', value);
});

// Wait helpers
Cypress.Commands.add('waitForElement', (selector: string, timeout = 10000) => {
  cy.get(selector, { timeout }).should('exist');
});

Cypress.Commands.add('waitForApi', (alias: string) => {
  cy.intercept('**').as(alias);
  cy.wait(`@${alias}`);
});

// Local storage commands
Cypress.Commands.add('saveLocalStorage', () => {
  Object.keys(localStorage).forEach((key) => {
    cy.window().then((window) => {
      cy.wrap(window.localStorage.getItem(key)).as(`localStorage_${key}`);
    });
  });
});

Cypress.Commands.add('restoreLocalStorage', () => {
  Object.keys(localStorage).forEach((key) => {
    cy.get(`@localStorage_${key}`).then((value) => {
      cy.window().then((window) => {
        window.localStorage.setItem(key, value as string);
      });
    });
  });
});

// Cookie commands
Cypress.Commands.add('preserveCookies', () => {
  Cypress.Cookies.preserveOnce('session', 'authToken');
});

// Accessibility commands
Cypress.Commands.add('checkA11y', (context?: string, options?: any) => {
  // This would integrate with cypress-axe for accessibility testing
  // cy.injectAxe();
  // cy.checkA11y(context, options);
});

// Screenshot commands
Cypress.Commands.add('takeNamedScreenshot', (name: string) => {
  cy.screenshot(name, { capture: 'fullPage' });
});

// Custom wait until command
Cypress.Commands.add('waitUntil', (predicate: () => boolean, options = {}) => {
  const defaultOptions = {
    timeout: 10000,
    interval: 100,
    ...options,
  };

  const start = Date.now();
  
  const checkCondition = () => {
    if (predicate()) {
      return true;
    }
    
    if (Date.now() - start > defaultOptions.timeout) {
      throw new Error('Timeout waiting for condition');
    }
    
    cy.wait(defaultOptions.interval);
    return checkCondition();
  };
  
  return cy.wrap(null).then(checkCondition);
});

// TypeScript declarations
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      loginAsAdmin(): Chainable<void>;
      loginAsUser(): Chainable<void>;
      logout(): Chainable<void>;
      apiLogin(email: string, password: string): Chainable<any>;
      apiRequest(method: string, url: string, body?: any): Chainable<any>;
      createUser(userData: any): Chainable<any>;
      deleteUser(email: string): Chainable<any>;
      resetDatabase(): Chainable<void>;
      seedTestData(data?: any): Chainable<void>;
      uploadFile(fileName: string, selector: string): Chainable<void>;
      shouldBeVisible(selector: string): Chainable<void>;
      shouldContainText(selector: string, text: string): Chainable<void>;
      shouldHaveValue(selector: string, value: string): Chainable<void>;
      waitForElement(selector: string, timeout?: number): Chainable<void>;
      waitForApi(alias: string): Chainable<void>;
      saveLocalStorage(): Chainable<void>;
      restoreLocalStorage(): Chainable<void>;
      preserveCookies(): Chainable<void>;
      checkA11y(context?: string, options?: any): Chainable<void>;
      takeNamedScreenshot(name: string): Chainable<void>;
      waitUntil(predicate: () => boolean, options?: any): Chainable<void>;
    }
  }
}

export {};