# 🧪 E2E Tests with Cypress & Cucumber

Comprehensive end-to-end testing suite using Cypress with Cucumber (BDD) for the StackWizard application.

## 🚀 Features

- **BDD Testing**: Write tests in Gherkin syntax for better readability
- **Page Object Pattern**: Maintainable test structure
- **Custom Commands**: Reusable Cypress commands
- **Multi-environment Support**: Test against local, staging, or production
- **Parallel Execution**: Run tests in parallel for faster feedback
- **Comprehensive Coverage**: Authentication, user management, admin features
- **Visual Testing**: Screenshot comparisons and visual regression
- **Accessibility Testing**: Built-in a11y checks
- **API Testing**: Direct API testing capabilities

## 📦 Installation

```bash
# Navigate to e2e-tests directory
cd e2e-tests

# Install dependencies
npm install

# Verify Cypress installation
npx cypress verify
```

## 🏃 Running Tests

### Interactive Mode (Cypress GUI)
```bash
npm run cy:open
```

### Headless Mode
```bash
npm run cy:run
```

### Run Specific Features
```bash
# Authentication tests only
npm run test:auth

# User management tests
npm run test:users

# Admin tests
npm run test:admin
```

### Run by Tags
```bash
# Smoke tests only
npm run test:smoke

# Regression tests
npm run test:regression

# Custom tags
npm run cy:run:tag @critical
```

### Different Browsers
```bash
npm run cy:run:chrome
npm run cy:run:firefox
npm run cy:run:edge
```

### Different Environments
```bash
# Local environment (default)
npm run cy:run

# Staging environment
CYPRESS_environment=staging npm run cy:run

# Production environment
CYPRESS_environment=production npm run cy:run
```

## 🏗️ Project Structure

```
cypress/
├── e2e/
│   ├── features/           # Cucumber feature files
│   │   ├── authentication/
│   │   │   ├── login.feature
│   │   │   ├── registration.feature
│   │   │   └── password-reset.feature
│   │   ├── users/
│   │   │   └── user-profile.feature
│   │   └── admin/
│   │       └── user-management.feature
│   └── step-definitions/   # Step implementations
│       ├── authentication.steps.ts
│       ├── users.steps.ts
│       └── admin.steps.ts
├── support/
│   ├── page-objects/       # Page Object Models
│   │   ├── LoginPage.ts
│   │   ├── RegistrationPage.ts
│   │   └── DashboardPage.ts
│   ├── commands.ts         # Custom Cypress commands
│   └── e2e.ts              # Support file
├── fixtures/               # Test data
│   └── users.json
├── config/                 # Environment configs
│   ├── local.json
│   └── staging.json
└── reports/               # Test reports
```

## 🏷️ Tags

Use tags to organize and filter tests:

- `@smoke` - Critical path tests
- `@regression` - Full regression suite
- `@authentication` - Auth-related tests
- `@users` - User management tests
- `@admin` - Admin functionality tests
- `@negative` - Negative test cases
- `@security` - Security-related tests
- `@accessibility` - A11y tests
- `@performance` - Performance tests

## 📝 Writing Tests

### Feature File Example
```gherkin
@authentication @smoke
Feature: User Login
  As a user
  I want to login
  So that I can access the application

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be logged in successfully
```

### Step Definition Example
```typescript
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor';

Given('I am on the login page', () => {
  cy.visit('/login');
});

When('I enter valid credentials', () => {
  cy.get('#email').type('user@example.com');
  cy.get('#password').type('Password123!');
});
```

### Page Object Example
```typescript
export default class LoginPage {
  visit(): void {
    cy.visit('/login');
  }

  login(email: string, password: string): void {
    cy.get('#email').type(email);
    cy.get('#password').type(password);
    cy.get('button[type="submit"]').click();
  }
}
```

## 🔧 Custom Commands

### Authentication
```javascript
// Login with credentials
cy.login('email@example.com', 'password');

// Login as admin
cy.loginAsAdmin();

// Login via API
cy.apiLogin('email@example.com', 'password');
```

### User Management
```javascript
// Create a test user
cy.createUser({ email: 'test@example.com' });

// Delete a user
cy.deleteUser('test@example.com');
```

### Database
```javascript
// Reset database to clean state
cy.resetDatabase();

// Seed test data
cy.seedTestData();
```

## 📊 Reports

### Generate HTML Report
```bash
npm run report:generate
```

Reports are generated in:
- `cypress/reports/cucumber-html/` - HTML reports
- `cypress/reports/cucumber-json/` - JSON reports
- `cypress/screenshots/` - Screenshots
- `cypress/videos/` - Test videos

## 🐳 Docker Support

Run tests in Docker:

```bash
# Build test image
docker build -t e2e-tests .

# Run tests
docker run --network="host" e2e-tests

# Run with custom command
docker run --network="host" e2e-tests npm run test:smoke
```

## 🔍 Debugging

### Debug Mode
```bash
# Run with debug output
DEBUG=cypress:* npm run cy:run
```

### Pause Test Execution
```javascript
// Add debugger statement
debugger;

// Or use Cypress pause
cy.pause();
```

### Take Screenshots
```javascript
// Take named screenshot
cy.screenshot('before-action');

// Full page screenshot
cy.screenshot('full-page', { capture: 'fullPage' });
```

## ⚙️ Configuration

### Environment Variables
```bash
# API URL
CYPRESS_apiUrl=http://localhost:8000

# Test credentials
CYPRESS_adminEmail=admin@example.com
CYPRESS_adminPassword=Admin123!

# Feature flags
CYPRESS_coverage=true
```

### cypress.config.ts
```typescript
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
  },
});
```

## 🚦 CI/CD Integration

### GitHub Actions
```yaml
- name: Run E2E Tests
  run: |
    npm ci
    npm run cy:run:record
  env:
    CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}
```

### Jenkins
```groovy
stage('E2E Tests') {
  steps {
    sh 'npm ci'
    sh 'npm run cy:run'
  }
}
```

## 📈 Best Practices

1. **Keep tests independent** - Each test should be able to run in isolation
2. **Use Page Objects** - Encapsulate page logic in page objects
3. **Use meaningful selectors** - Prefer data-cy attributes
4. **Clean test data** - Reset state before/after tests
5. **Use tags wisely** - Organize tests with appropriate tags
6. **Write descriptive scenarios** - Make tests readable for non-technical stakeholders
7. **Avoid hard-coded waits** - Use Cypress's built-in retry-ability
8. **Test happy paths first** - Then add edge cases
9. **Keep step definitions simple** - Complex logic belongs in page objects
10. **Version control test data** - Keep fixtures in sync with code

## 🆘 Troubleshooting

### Common Issues

**Tests failing locally but passing in CI**
- Check environment differences
- Verify test data state
- Review timing/race conditions

**Element not found errors**
- Increase timeout: `cy.get('.element', { timeout: 10000 })`
- Check if element is in viewport
- Verify selectors are correct

**Flaky tests**
- Add explicit waits for API calls
- Use cy.intercept() to control network requests
- Check for animation completion

## 📚 Resources

- [Cypress Documentation](https://docs.cypress.io)
- [Cucumber Documentation](https://cucumber.io/docs/cucumber/)
- [Cypress Cucumber Preprocessor](https://github.com/badeball/cypress-cucumber-preprocessor)
- [Best Practices](https://docs.cypress.io/guides/references/best-practices)