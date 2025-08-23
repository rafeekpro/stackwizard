#!/usr/bin/env node

/**
 * Test: Navigation Menu Authentication State
 * 
 * This test verifies that the navigation menu correctly updates
 * after user authentication in both MUI and Tailwind templates.
 * 
 * Critical Test Requirements:
 * 1. Before login: Should show Home, About, Sign In, Sign Up
 * 2. After login: Should show Home, About, Users, Items, My Account, Logout
 * 3. Should NOT show Sign In/Sign Up after login
 * 4. Should work in both MUI and Tailwind templates
 */

import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_DIR = path.join(__dirname, '..', 'test-output');
const PROJECT_NAME = 'test-nav-auth';

// Generate random ports to avoid conflicts
const BACKEND_PORT = 18000 + Math.floor(Math.random() * 1000);
const FRONTEND_PORT = 13000 + Math.floor(Math.random() * 1000);
const DB_PORT = 15432 + Math.floor(Math.random() * 1000);

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logStep(step) {
  console.log(`\n${colors.cyan}▶ ${step}${colors.reset}`);
}

function logSuccess(message) {
  console.log(`${colors.green}✓ ${message}${colors.reset}`);
}

function logError(message) {
  console.log(`${colors.red}✗ ${message}${colors.reset}`);
}

async function cleanup() {
  logStep('Cleaning up test environment...');
  
  // Stop and remove Docker containers
  const projectPath = path.join(TEST_DIR, PROJECT_NAME);
  if (fs.existsSync(projectPath)) {
    try {
      execSync('docker compose down -v', { 
        cwd: projectPath, 
        stdio: 'ignore' 
      });
    } catch (error) {
      // Ignore errors during cleanup
    }
  }
  
  // Remove test directory
  await fs.remove(TEST_DIR);
  logSuccess('Cleanup completed');
}

async function generateProject(uiLibrary) {
  logStep(`Generating project with ${uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS'}...`);
  
  const projectPath = path.join(TEST_DIR, PROJECT_NAME);
  
  // Remove existing project if it exists
  if (fs.existsSync(projectPath)) {
    await fs.remove(projectPath);
  }
  
  // Ensure test directory exists
  await fs.ensureDir(TEST_DIR);
  
  // Generate project using the CLI with quick mode and custom ports
  const command = `node ${path.join(__dirname, '..', 'src', 'index.js')} --name ${PROJECT_NAME} --ui ${uiLibrary} --quick`;
  
  try {
    execSync(command, {
      cwd: TEST_DIR,
      stdio: 'inherit'
    });
    logSuccess(`Project generated with ${uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS'}`);
    
    // Update docker-compose.yml with custom ports to avoid conflicts
    const dockerComposePath = path.join(projectPath, 'docker-compose.yml');
    let dockerComposeContent = fs.readFileSync(dockerComposePath, 'utf8');
    dockerComposeContent = dockerComposeContent
      .replace(/- "8000:8000"/g, `- "${BACKEND_PORT}:8000"`)
      .replace(/- "3000:3000"/g, `- "${FRONTEND_PORT}:3000"`)
      .replace(/- "5432:5432"/g, `- "${DB_PORT}:5432"`);
    fs.writeFileSync(dockerComposePath, dockerComposeContent);
    
    logSuccess(`Updated ports - Backend: ${BACKEND_PORT}, Frontend: ${FRONTEND_PORT}, DB: ${DB_PORT}`);
  } catch (error) {
    logError(`Failed to generate project: ${error.message}`);
    throw error;
  }
  
  return projectPath;
}

async function startServices(projectPath) {
  logStep('Starting Docker services...');
  
  try {
    // Build and start services
    execSync('docker compose up -d --build', { 
      cwd: projectPath,
      stdio: 'inherit'
    });
    
    logSuccess('Docker services started');
    
    // Wait for services to be ready
    log('Waiting for services to be ready...');
    await waitForServices(projectPath);
    
  } catch (error) {
    logError(`Failed to start services: ${error.message}`);
    throw error;
  }
}

async function waitForServices(projectPath, maxAttempts = 60) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      // Check if backend is responding
      const healthCheck = execSync(`curl -s http://localhost:${BACKEND_PORT}/health`, {
        encoding: 'utf8'
      });
      
      const health = JSON.parse(healthCheck);
      if (health.api === 'healthy' && health.database === 'healthy') {
        logSuccess('Backend services are ready');
        
        // Check if frontend is responding
        execSync(`curl -s http://localhost:${FRONTEND_PORT}`, {
          encoding: 'utf8'
        });
        logSuccess('Frontend service is ready');
        return;
      }
    } catch (error) {
      // Services not ready yet
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error('Services did not become ready in time');
}

async function testNavigationAuth(projectPath, uiLibrary) {
  logStep(`Testing navigation authentication state (${uiLibrary})...`);
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1280, height: 800 });
    
    // Navigate to the application
    log('Navigating to application...');
    await page.goto(`http://localhost:${FRONTEND_PORT}`, { waitUntil: 'networkidle0' });
    
    // Test 1: Check navigation items BEFORE login
    log('Checking navigation items before login...');
    const beforeLoginItems = await getNavigationItems(page, uiLibrary);
    
    // Verify expected items before login
    const expectedBeforeLogin = ['Home', 'About'];
    const unexpectedBeforeLogin = ['Users', 'Items', 'My Account', 'Logout'];
    
    for (const item of expectedBeforeLogin) {
      if (!beforeLoginItems.includes(item)) {
        throw new Error(`Expected navigation item "${item}" not found before login`);
      }
    }
    
    for (const item of unexpectedBeforeLogin) {
      if (beforeLoginItems.includes(item)) {
        throw new Error(`Unexpected navigation item "${item}" found before login`);
      }
    }
    
    // Check for Sign In and Sign Up buttons
    const hasSignInButton = await checkForAuthButton(page, 'Sign In', uiLibrary);
    const hasSignUpButton = await checkForAuthButton(page, 'Sign Up', uiLibrary);
    
    if (!hasSignInButton) {
      throw new Error('Sign In button not found before login');
    }
    if (!hasSignUpButton) {
      throw new Error('Sign Up button not found before login');
    }
    
    logSuccess('Navigation items correct before login');
    
    // Navigate to login page
    log('Navigating to login page...');
    await page.goto(`http://localhost:${FRONTEND_PORT}/login`, { waitUntil: 'networkidle0' });
    
    // Login with test credentials
    log('Logging in...');
    await page.type('input[name="email"]', 'admin@example.com');
    await page.type('input[name="password"]', 'admin123');
    
    // Submit login form
    await page.click('button[type="submit"]');
    
    // Wait for navigation to dashboard
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    
    // Verify we're on the dashboard
    const currentUrl = page.url();
    if (!currentUrl.includes('/dashboard')) {
      throw new Error(`Expected to be redirected to dashboard, but on: ${currentUrl}`);
    }
    
    logSuccess('Successfully logged in and redirected to dashboard');
    
    // Test 2: Check navigation items AFTER login
    log('Checking navigation items after login...');
    const afterLoginItems = await getNavigationItems(page, uiLibrary);
    
    // Verify expected items after login
    const expectedAfterLogin = ['Home', 'About', 'Users', 'Items'];
    const unexpectedAfterLogin = ['Sign In', 'Sign Up'];
    
    for (const item of expectedAfterLogin) {
      if (!afterLoginItems.includes(item)) {
        throw new Error(`Expected navigation item "${item}" not found after login. Found: ${afterLoginItems.join(', ')}`);
      }
    }
    
    // Check for My Account (MUI) or account-related items
    if (uiLibrary === 'mui' && !afterLoginItems.includes('My Account')) {
      throw new Error('Expected "My Account" navigation item not found after login');
    }
    
    // Check that Sign In/Sign Up are NOT present
    const hasSignInAfterLogin = await checkForAuthButton(page, 'Sign In', uiLibrary);
    const hasSignUpAfterLogin = await checkForAuthButton(page, 'Sign Up', uiLibrary);
    
    if (hasSignInAfterLogin) {
      throw new Error('Sign In button should not be visible after login');
    }
    if (hasSignUpAfterLogin) {
      throw new Error('Sign Up button should not be visible after login');
    }
    
    // Check for Logout button
    const hasLogoutButton = await checkForAuthButton(page, 'Logout', uiLibrary);
    if (!hasLogoutButton) {
      throw new Error('Logout button not found after login');
    }
    
    logSuccess('Navigation items correct after login');
    
    // Test 3: Test logout functionality
    log('Testing logout...');
    await clickLogoutButton(page, uiLibrary);
    
    // Wait for navigation
    await page.waitForTimeout(2000);
    
    // Check navigation items after logout
    const afterLogoutItems = await getNavigationItems(page, uiLibrary);
    
    // Should be back to unauthenticated state
    for (const item of expectedBeforeLogin) {
      if (!afterLogoutItems.includes(item)) {
        throw new Error(`Expected navigation item "${item}" not found after logout`);
      }
    }
    
    for (const item of unexpectedBeforeLogin) {
      if (afterLogoutItems.includes(item)) {
        throw new Error(`Unexpected navigation item "${item}" found after logout`);
      }
    }
    
    logSuccess('Navigation items correct after logout');
    
    logSuccess(`✅ All navigation authentication tests passed for ${uiLibrary}`);
    
  } finally {
    await browser.close();
  }
}

async function getNavigationItems(page, uiLibrary) {
  if (uiLibrary === 'mui') {
    // For MUI, get navigation items from the AppBar
    return await page.evaluate(() => {
      const items = [];
      // Desktop menu items
      const buttons = document.querySelectorAll('nav button, nav a');
      buttons.forEach(button => {
        const text = button.textContent.trim();
        if (text && !items.includes(text)) {
          items.push(text);
        }
      });
      return items;
    });
  } else {
    // For Tailwind, get navigation items from the nav links
    return await page.evaluate(() => {
      const items = [];
      const links = document.querySelectorAll('nav a');
      links.forEach(link => {
        const text = link.textContent.trim();
        if (text && !items.includes(text)) {
          items.push(text);
        }
      });
      return items;
    });
  }
}

async function checkForAuthButton(page, buttonText, uiLibrary) {
  return await page.evaluate((text) => {
    const buttons = document.querySelectorAll('button, a');
    for (const button of buttons) {
      if (button.textContent.trim() === text) {
        return true;
      }
    }
    return false;
  }, buttonText);
}

async function clickLogoutButton(page, uiLibrary) {
  await page.evaluate(() => {
    const buttons = document.querySelectorAll('button');
    for (const button of buttons) {
      if (button.textContent.trim() === 'Logout') {
        button.click();
        return;
      }
    }
  });
}

async function runTests() {
  console.log(`\n${colors.bright}${colors.blue}========================================${colors.reset}`);
  console.log(`${colors.bright}${colors.blue}  Navigation Authentication State Test  ${colors.reset}`);
  console.log(`${colors.bright}${colors.blue}========================================${colors.reset}\n`);
  
  let exitCode = 0;
  
  try {
    // Test both UI libraries
    for (const uiLibrary of ['mui', 'tailwind']) {
      console.log(`\n${colors.bright}${colors.cyan}Testing ${uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS'} Template${colors.reset}`);
      console.log(`${colors.cyan}${'='.repeat(40)}${colors.reset}`);
      
      // Clean up from previous test
      await cleanup();
      
      // Generate project
      const projectPath = await generateProject(uiLibrary);
      
      // Start services
      await startServices(projectPath);
      
      // Run navigation auth tests
      await testNavigationAuth(projectPath, uiLibrary);
      
      // Stop services
      logStep('Stopping services...');
      execSync('docker compose down', { 
        cwd: projectPath,
        stdio: 'ignore'
      });
    }
    
    console.log(`\n${colors.bright}${colors.green}✅ ALL NAVIGATION AUTHENTICATION TESTS PASSED!${colors.reset}\n`);
    
  } catch (error) {
    console.error(`\n${colors.bright}${colors.red}❌ TEST FAILED: ${error.message}${colors.reset}\n`);
    if (error.stack) {
      console.error(colors.red + error.stack + colors.reset);
    }
    exitCode = 1;
  } finally {
    // Final cleanup
    await cleanup();
  }
  
  process.exit(exitCode);
}

// Handle process termination
process.on('SIGINT', async () => {
  console.log('\n\nReceived SIGINT, cleaning up...');
  await cleanup();
  process.exit(1);
});

process.on('SIGTERM', async () => {
  console.log('\n\nReceived SIGTERM, cleaning up...');
  await cleanup();
  process.exit(1);
});

// Run the tests
runTests();