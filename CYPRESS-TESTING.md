# 🎭 Cypress Visual Testing Guide

## Overview
See your application being tested in real-time with Cypress! Watch as it clicks buttons, fills forms, and navigates through your app.

## 🚀 Quick Start

### 1. Install Cypress (one time)
```bash
make cypress-install
```

### 2. Test with Visual Mode (SEE the tests running!)

#### Test MUI Template
```bash
make cypress-mui
```
This will:
1. Generate a test project with MUI
2. Start Docker containers
3. Open Cypress Test Runner
4. You can SEE tests running in browser!

#### Test Tailwind Template
```bash
make cypress-tailwind
```

## 📺 Visual Testing Features

### What You'll See:
- 🖱️ **Mouse movements** - Watch Cypress click buttons
- ⌨️ **Form filling** - See text being typed
- 📱 **Responsive testing** - Watch viewport changes
- 📸 **Screenshots** - Automatic on failures
- 🎥 **Videos** - Record test runs
- ⏱️ **Real-time execution** - Step by step

## 🎯 Available Commands

### Interactive Mode (Visual)
```bash
# Open Cypress Test Runner
make cypress-open

# Test MUI with visual feedback
make cypress-mui

# Test Tailwind with visual feedback
make cypress-tailwind

# Watch mode with live reload
make cypress-watch
```

### Headless Mode (CI/CD)
```bash
# Run all tests headless
make cypress-both

# Run specific template headless
make cypress-test-mui-headless
make cypress-test-tailwind-headless
```

## 🧪 Test Coverage

### MUI Template Tests
1. **Homepage** (`01-homepage.cy.js`)
   - Navigation
   - Health status
   - Material UI components
   - Responsive design

2. **Authentication** (`02-authentication.cy.js`)
   - Registration flow
   - Login/Logout
   - Form validation
   - Error handling

3. **Dashboard & CRUD** (`03-dashboard.cy.js`)
   - User management
   - Item management
   - My Account features
   - Data tables

### Tailwind Template Tests
1. **Homepage** (`01-homepage.cy.js`)
   - Tailwind styling
   - Headless UI components
   - Responsive breakpoints

## 🎬 Running Tests Step by Step

### 1. Start Fresh Test Environment
```bash
# Clean any existing test projects
rm -rf ../test-cypress-*

# Generate and test MUI
make cypress-mui
```

### 2. In Cypress Test Runner
1. Click on a test file (e.g., `01-homepage.cy.js`)
2. Watch the browser open
3. See each test step execute
4. Green ✅ = Pass, Red ❌ = Fail

### 3. Debug Failed Tests
- Click on failed test step
- See exact error
- Check screenshots
- View DOM snapshot
- Time travel through test steps

## 🖼️ Screenshots & Videos

### Automatic Screenshots
```javascript
// On test failure
cy.screenshot('failure-screenshot');

// Manual screenshot
cy.takeNamedScreenshot('login-form');
```

### Video Recording
```bash
# Record videos of test runs
make cypress-record
```

Videos saved in: `cypress/videos/`
Screenshots in: `cypress/screenshots/`

## 🔍 Visual Debugging

### Time Travel
- Hover over test steps
- See app state at each point
- Click to pin a snapshot

### DOM Snapshots
- Inspect elements
- Check computed styles
- View network requests

### Console Logs
- See application console
- Debug JavaScript errors
- Check API calls

## 🎨 Testing Different Viewports

### Desktop
```javascript
cy.viewport(1920, 1080);
```

### Tablet
```javascript
cy.viewport(768, 1024);
```

### Mobile
```javascript
cy.viewport(375, 667);
```

## 📝 Writing New Tests

### Basic Test Structure
```javascript
describe('Feature Name', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should do something', () => {
    // Your test here
    cy.contains('Button Text').click();
    cy.url().should('include', '/expected-path');
  });
});
```

### Custom Commands
```javascript
// Login quickly
cy.login('admin@example.com', 'admin123');

// Check MUI components
cy.checkMuiComponents();

// Check Tailwind classes
cy.checkTailwindClasses();
```

## 🚦 CI/CD Integration

### GitHub Actions
```yaml
- name: Run Cypress tests
  run: |
    docker-compose up -d
    npm run cypress:run
    docker-compose down
```

### Parallel Testing
```bash
# Run both templates in parallel
make -j2 cypress-test-mui-headless cypress-test-tailwind-headless
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Cypress won't open
```bash
# Reinstall Cypress
rm -rf node_modules
npm install
npx cypress install
```

#### 2. Tests timing out
```javascript
// Increase timeout
cy.get('element', { timeout: 10000 });
```

#### 3. Container not ready
```bash
# Wait longer before tests
sleep 20  # Instead of sleep 15
```

## 💡 Pro Tips

### 1. Use data-testid
```html
<button data-testid="submit-button">Submit</button>
```
```javascript
cy.get('[data-testid="submit-button"]').click();
```

### 2. Wait for API
```javascript
cy.waitForApi();  // Custom command
```

### 3. Visual Regression Testing
```bash
# Take baseline screenshots
cy.screenshot('baseline/homepage');

# Compare in future runs
cy.screenshot('current/homepage');
```

### 4. Debug Mode
```javascript
// Pause test execution
cy.pause();

// Debug specific element
cy.get('.element').debug();
```

## 🎯 Best Practices

1. **Keep tests independent** - Each test should run alone
2. **Use beforeEach** - Reset state before each test
3. **Avoid cy.wait()** - Use assertions instead
4. **Test user journeys** - Not just individual elements
5. **Name tests clearly** - Describe what they test

## 📊 View Test Results

### In Terminal
```bash
  ✓ should load homepage (2.1s)
  ✓ should login successfully (3.5s)
  ✓ should create new item (1.8s)
  
  3 passing (7.4s)
```

### In Cypress Dashboard
- Test duration
- Success rate
- Failure screenshots
- Performance metrics

## 🔄 Continuous Testing

### Watch Mode
```bash
# Auto-run tests on file changes
make cypress-watch
```

### Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
make cypress-both
```

---

## 🎬 Example Test Run

```bash
# 1. Start the visual test
$ make cypress-mui

# 2. Output you'll see:
🟡 Starting MUI template for Cypress testing...
🟡 Generating MUI test project...
✅ MUI project generated!
🔵 Waiting for services to start...
✅ Services started! Opening Cypress...

# 3. Cypress opens - click on test file
# 4. Watch the magic happen! 🎭
```

Enjoy watching your tests run! 🚀