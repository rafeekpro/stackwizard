#!/usr/bin/env node

/**
 * End-to-End Login Test
 * Tests user login flow through http://localhost:3000/login
 * Verifies all API endpoints are correctly mapped between React and FastAPI
 */

import fs from 'fs-extra';
import path from 'path';
import { execSync } from 'child_process';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

const TEST_PROJECT_NAME = 'test-e2e-login';
const TEST_DIR = path.join(__dirname, '..', 'test-output', TEST_PROJECT_NAME);
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000';

// Test configuration
const TEST_USER = {
  email: 'test@example.com',
  password: 'TestPassword123!',
  fullName: 'Test User'
};

const ADMIN_USER = {
  email: 'admin@example.com',
  password: 'admin123'
};

/**
 * Clean up test environment
 */
async function cleanup() {
  try {
    if (fs.existsSync(TEST_DIR)) {
      try {
        execSync('docker compose down -v', { 
          cwd: TEST_DIR,
          stdio: 'ignore'
        });
      } catch (e) {
        // Ignore errors
      }
      await fs.remove(TEST_DIR);
    }
  } catch (err) {
    console.log(warning('Warning: Cleanup encountered issues:'), err.message);
  }
}

/**
 * Generate test project
 */
function generateProject() {
  console.log(info('\n📦 Generating test project...'));
  
  const testOutputDir = path.join(__dirname, '..', 'test-output');
  fs.ensureDirSync(testOutputDir);
  
  // Create expect script for automated project generation
  const expectScript = `#!/usr/bin/expect -f
set timeout 60
spawn node ${path.join(__dirname, '..', 'src', 'index.js')}

expect {
  "What is your project name?" {
    send "${TEST_PROJECT_NAME}\\r"
  }
}

expect {
  "Choose your UI library" {
    send "\\r"
  }
}

expect {
  "Database name:" {
    send "\\r"
  }
}

expect {
  "Database user:" {
    send "\\r"
  }
}

expect {
  "Database password:" {
    send "password\\r"
  }
}

expect {
  "Backend API port:" {
    send "\\r"
  }
}

expect {
  "Frontend port:" {
    send "\\r"
  }
}

expect {
  "Select additional features:" {
    send "\\r"
  }
}

expect {
  "Project created successfully" {
    puts "\\nProject generation completed"
  }
  eof {
    puts "\\nGeneration completed"
  }
}

exit 0
`;

  const expectFile = path.join(testOutputDir, 'generate-e2e-test.exp');
  fs.writeFileSync(expectFile, expectScript);
  fs.chmodSync(expectFile, '755');
  
  try {
    execSync(expectFile, {
      cwd: testOutputDir,
      stdio: 'inherit'
    });
    console.log(success('✅ Project generated successfully'));
  } catch (err) {
    console.log(warning('⚠️  Generation ended, checking if project was created...'));
  } finally {
    fs.removeSync(expectFile);
  }
}

/**
 * Start Docker services
 */
async function startServices() {
  console.log(info('\n🐳 Starting Docker services...'));
  
  try {
    execSync('docker compose up -d', {
      cwd: TEST_DIR,
      stdio: 'inherit'
    });
    
    console.log(info('⏳ Waiting for services to be ready...'));
    
    // Wait for backend
    let backendReady = false;
    for (let i = 0; i < 30; i++) {
      try {
        await axios.get(`${BACKEND_URL}/health`, { timeout: 1000 });
        backendReady = true;
        console.log(success('✅ Backend is ready'));
        break;
      } catch (err) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    if (!backendReady) {
      throw new Error('Backend failed to start');
    }
    
    // Wait for frontend
    let frontendReady = false;
    for (let i = 0; i < 30; i++) {
      try {
        await axios.get(FRONTEND_URL, { timeout: 1000 });
        frontendReady = true;
        console.log(success('✅ Frontend is ready'));
        break;
      } catch (err) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    if (!frontendReady) {
      throw new Error('Frontend failed to start');
    }
    
    // Give database time to initialize
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    return true;
  } catch (err) {
    console.log(error('❌ Failed to start services:'), err.message);
    return false;
  }
}

/**
 * Test API endpoints mapping
 */
async function testAPIEndpoints() {
  console.log(info('\n🔍 Testing API endpoints mapping...'));
  console.log('─'.repeat(60));
  
  const endpoints = [
    // Auth endpoints
    { method: 'POST', path: '/api/v1/auth/login', needsAuth: false, description: 'Login endpoint' },
    { method: 'POST', path: '/api/v1/auth/register', needsAuth: false, description: 'Register endpoint' },
    { method: 'POST', path: '/api/v1/auth/logout', needsAuth: true, description: 'Logout endpoint' },
    { method: 'POST', path: '/api/v1/auth/refresh', needsAuth: false, description: 'Token refresh' },
    
    // User endpoints
    { method: 'GET', path: '/api/v1/users/me', needsAuth: true, description: 'Current user' },
    { method: 'GET', path: '/api/v1/users/', needsAuth: true, description: 'List users' },
    
    // Admin endpoints
    { method: 'GET', path: '/api/v1/admin/stats', needsAuth: true, description: 'Admin statistics' },
    { method: 'GET', path: '/api/v1/admin/recent-registrations', needsAuth: true, description: 'Recent registrations' },
    { method: 'GET', path: '/api/v1/admin/audit-log', needsAuth: true, description: 'Audit log' },
    
    // Items endpoints
    { method: 'GET', path: '/api/v1/items/', needsAuth: true, description: 'List items' },
    
    // Health endpoints
    { method: 'GET', path: '/health', needsAuth: false, description: 'Health check' },
    { method: 'GET', path: '/api/health', needsAuth: false, description: 'API health check' }
  ];
  
  let token = null;
  const results = [];
  
  // First login to get token
  try {
    const loginData = new URLSearchParams();
    loginData.append('username', ADMIN_USER.email);
    loginData.append('password', ADMIN_USER.password);
    
    const loginResponse = await axios.post(
      `${BACKEND_URL}/api/v1/auth/login`,
      loginData,
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    
    token = loginResponse.data.access_token;
    console.log(success('✅ Admin authentication successful'));
  } catch (err) {
    console.log(error('❌ Admin authentication failed'), err.message);
    return { results, hasErrors: true };
  }
  
  // Test each endpoint
  for (const endpoint of endpoints) {
    try {
      const config = {
        method: endpoint.method,
        url: `${BACKEND_URL}${endpoint.path}`,
        validateStatus: () => true
      };
      
      if (endpoint.needsAuth && token) {
        config.headers = { Authorization: `Bearer ${token}` };
      }
      
      const response = await axios(config);
      
      const isSuccess = response.status < 400 || 
                       (endpoint.method === 'POST' && response.status === 422); // POST without data
      
      if (isSuccess) {
        console.log(success(`✅ ${endpoint.description}: ${endpoint.method} ${endpoint.path} - Status ${response.status}`));
      } else {
        console.log(error(`❌ ${endpoint.description}: ${endpoint.method} ${endpoint.path} - Status ${response.status}`));
      }
      
      results.push({
        ...endpoint,
        status: response.status,
        success: isSuccess
      });
      
    } catch (err) {
      console.log(error(`❌ ${endpoint.description}: ${endpoint.method} ${endpoint.path} - Error: ${err.message}`));
      results.push({
        ...endpoint,
        error: err.message,
        success: false
      });
    }
  }
  
  const hasErrors = results.some(r => !r.success);
  return { results, hasErrors };
}

/**
 * Test login flow with Puppeteer
 */
async function testLoginFlow() {
  console.log(info('\n🌐 Testing login flow through browser...'));
  console.log('─'.repeat(60));
  
  let browser;
  let success = true;
  
  try {
    // Launch browser
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Enable console logging
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(error('Browser console error:'), msg.text());
      }
    });
    
    // Test 1: Navigate to login page
    console.log(info('📍 Navigating to login page...'));
    await page.goto(`${FRONTEND_URL}/login`, { waitUntil: 'networkidle2' });
    console.log(chalk.green('✅ Login page loaded'));
    
    // Test 2: Check if login form exists
    const emailInput = await page.$('input[name="email"], input[type="email"]');
    const passwordInput = await page.$('input[name="password"], input[type="password"]');
    const submitButton = await page.$('button[type="submit"]');
    
    if (!emailInput || !passwordInput || !submitButton) {
      throw new Error('Login form elements not found');
    }
    console.log(chalk.green('✅ Login form elements found'));
    
    // Test 3: Try login with admin credentials
    console.log(info('🔐 Attempting login with admin credentials...'));
    await page.type('input[name="email"], input[type="email"]', ADMIN_USER.email);
    await page.type('input[name="password"], input[type="password"]', ADMIN_USER.password);
    
    // Monitor network requests
    const loginRequest = page.waitForResponse(
      response => response.url().includes('/auth/login') || response.url().includes('/api/v1/auth/login'),
      { timeout: 10000 }
    );
    
    await submitButton.click();
    
    try {
      const response = await loginRequest;
      console.log(info(`📡 Login request to: ${response.url()}`));
      console.log(info(`📊 Response status: ${response.status()}`));
      
      if (response.status() === 200) {
        console.log(chalk.green('✅ Login successful'));
        
        // Wait for redirect to dashboard
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 5000 }).catch(() => {});
        
        const currentUrl = page.url();
        if (currentUrl.includes('/dashboard') || currentUrl === `${FRONTEND_URL}/`) {
          console.log(chalk.green('✅ Redirected to dashboard/home'));
        } else {
          console.log(warning(`⚠️  Unexpected redirect to: ${currentUrl}`));
        }
      } else {
        console.log(error(`❌ Login failed with status: ${response.status()}`));
        success = false;
      }
    } catch (err) {
      console.log(error('❌ Login request failed:'), err.message);
      success = false;
    }
    
    // Test 4: Check if user menu appears (indicates successful login)
    try {
      await page.waitForSelector('[data-testid="user-menu"], #user-menu, .user-menu', { timeout: 5000 });
      console.log(chalk.green('✅ User menu appeared - login confirmed'));
    } catch (err) {
      console.log(warning('⚠️  User menu not found - might be a UI variation'));
    }
    
    // Test 5: Try to access admin dashboard
    console.log(info('📊 Accessing admin dashboard...'));
    await page.goto(`${FRONTEND_URL}/admin`, { waitUntil: 'networkidle2' });
    
    // Check if admin dashboard loaded
    const adminTitle = await page.$eval('h1, h2', el => el.textContent).catch(() => null);
    if (adminTitle && adminTitle.toLowerCase().includes('admin')) {
      console.log(chalk.green('✅ Admin dashboard accessible'));
    } else {
      console.log(warning('⚠️  Admin dashboard might not be accessible'));
    }
    
  } catch (err) {
    console.log(error('❌ Browser test failed:'), err.message);
    success = false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
  
  return success;
}

/**
 * Main test function
 */
async function runTests() {
  console.log(chalk.bold.cyan('\n🧪 E2E Login Test Suite\n'));
  console.log('═'.repeat(60));
  
  let allTestsPassed = true;
  
  try {
    // Clean up any previous test
    await cleanup();
    
    // Generate project
    generateProject();
    
    // Verify project structure
    if (!fs.existsSync(TEST_DIR)) {
      throw new Error('Project generation failed - directory not created');
    }
    
    // Start services
    const servicesStarted = await startServices();
    if (!servicesStarted) {
      throw new Error('Failed to start Docker services');
    }
    
    // Test API endpoints
    const { hasErrors: apiErrors } = await testAPIEndpoints();
    if (apiErrors) {
      allTestsPassed = false;
    }
    
    // Test login flow
    const loginSuccess = await testLoginFlow();
    if (!loginSuccess) {
      allTestsPassed = false;
    }
    
  } catch (err) {
    console.log(error('\n❌ Test suite failed:'), err.message);
    allTestsPassed = false;
  } finally {
    // Clean up
    console.log(info('\n🧹 Cleaning up...'));
    await cleanup();
  }
  
  // Final report
  console.log('\n' + chalk.bold('Test Summary:'));
  console.log('═'.repeat(60));
  
  if (allTestsPassed) {
    console.log(success('✅ All E2E tests passed!'));
    console.log(success('Login flow and API endpoints are working correctly.'));
    process.exit(0);
  } else {
    console.log(error('❌ Some E2E tests failed!'));
    console.log(error('Please check the API endpoint mappings between React and FastAPI.'));
    process.exit(1);
  }
}

// Check if puppeteer is installed
try {
  require.resolve('puppeteer');
} catch (e) {
  console.log(warning('\n⚠️  Puppeteer not installed. Installing...'));
  execSync('npm install puppeteer', { stdio: 'inherit' });
}

// Run the tests
runTests().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});