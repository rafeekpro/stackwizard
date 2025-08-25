# Cypress Visual Testing 🎭

## Overview

StackWizard includes comprehensive Cypress E2E tests that you can watch run in real-time. See tests clicking buttons, filling forms, and navigating through your application.

## Installation

```bash
# Install Cypress and dependencies
make cypress-install

# Or manually
npm install
npx cypress install
```

## Visual Testing Mode

### Test MUI Template

```bash
make cypress-mui
```

This command:
1. Generates a test project with Material UI
2. Starts Docker containers
3. Opens Cypress Test Runner
4. You can watch tests run in the browser!

### Test Tailwind Template

```bash
make cypress-tailwind
```

## What You'll See

- 🖱️ **Mouse movements** - Watch Cypress click buttons
- ⌨️ **Form filling** - See text being typed in real-time
- 📱 **Responsive testing** - Watch viewport changes
- 📸 **Screenshots** - Automatic capture on failures
- 🎥 **Videos** - Record entire test runs

## Test Coverage

### MUI Template Tests

#### 1. Homepage (`01-homepage.cy.js`)
- Navigation menu functionality
- Health status indicators
- Material UI component presence
- Responsive design testing

#### 2. Authentication (`02-authentication.cy.js`)
- User registration flow
- Login/logout functionality
- Form validation
- Error handling

#### 3. Dashboard & CRUD (`03-dashboard.cy.js`)
- User management (create, read, update, delete)
- Item management
- My Account features
- Data table interactions

### Tailwind Template Tests

#### 1. Homepage (`01-homepage.cy.js`)
- Tailwind CSS styling verification
- Headless UI component testing
- Responsive breakpoint testing

## Running Tests

### Interactive Mode (Visual)

```bash
# Open Cypress Test Runner
make cypress-open

# Watch mode with live reload
make cypress-watch
```

### Headless Mode (CI/CD)

```bash
# Run all tests without UI
make cypress-both

# Test specific template
make cypress-test-mui-headless
make cypress-test-tailwind-headless
```

## Writing Custom Tests

### Basic Test Structure

```javascript
describe('Feature Name', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should perform an action', () => {
    cy.contains('Button Text').click();
    cy.url().should('include', '/expected-path');
    cy.contains('Success Message').should('be.visible');
  });
});
```

### Using Custom Commands

```javascript
// Quick login
cy.login('admin@example.com', 'admin123');

// Check MUI components exist
cy.checkMuiComponents();

// Check Tailwind classes
cy.checkTailwindClasses();

// Wait for API to be ready
cy.waitForApi();

// Take named screenshot
cy.takeNamedScreenshot('dashboard-view');
```

## Debugging Failed Tests

### Time Travel
- Hover over test steps in the command log
- See application state at each point
- Click to pin a specific snapshot

### DOM Snapshots
- Inspect any element
- Check computed CSS styles
- View network requests

### Screenshots & Videos
- Automatic screenshots on failure
- Full video recording of test runs
- Located in `cypress/screenshots/` and `cypress/videos/`

## Best Practices

### 1. Use Data Test IDs

```html
<!-- In your React component -->
<button data-testid="submit-button">Submit</button>
```

```javascript
// In your test
cy.get('[data-testid="submit-button"]').click();
```

### 2. Avoid Hard Waits

```javascript
// ❌ Bad
cy.wait(5000);

// ✅ Good
cy.contains('Loading...').should('not.exist');
cy.get('[data-testid="content"]').should('be.visible');
```

### 3. Keep Tests Independent

```javascript
describe('User Management', () => {
  beforeEach(() => {
    // Reset to clean state
    cy.task('db:seed');
    cy.login('admin@example.com', 'admin123');
  });

  it('should create user', () => {
    // Test logic
  });

  it('should edit user', () => {
    // This test doesn't depend on previous test
  });
});
```

## Configuration

### cypress.config.js

```javascript
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
  },
  env: {
    apiUrl: 'http://localhost:8000',
    template: 'mui', // or 'tailwind'
  }
});
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Cypress Tests
  run: |
    docker-compose up -d
    npx wait-on http://localhost:3000
    npm run cypress:run
    docker-compose down
```

### Parallel Testing

```bash
# Run both templates in parallel
make -j2 cypress-test-mui-headless cypress-test-tailwind-headless
```

## Troubleshooting

### Cypress Won't Open

```bash
# Reinstall Cypress binary
npx cypress install --force
```

### Tests Timing Out

```javascript
// Increase timeout in specific test
cy.get('element', { timeout: 20000 });

// Or globally in cypress.config.js
defaultCommandTimeout: 20000
```

### Container Not Ready

```bash
# Wait longer before starting tests
sleep 30  # Instead of default 15
```

---

[Back to Wiki Home](Home)