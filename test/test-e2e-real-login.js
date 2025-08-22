#!/usr/bin/env node

/**
 * End-to-End test that actually generates a project and tests login
 * This test verifies that the generated project can handle login correctly
 */

import fs from 'fs-extra';
import { execSync } from 'child_process';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import axios from 'axios';
import puppeteer from 'puppeteer';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

const TEST_PROJECT_NAME = 'test-e2e-login';
const TEST_DIR = join(__dirname, '..', 'test-output', TEST_PROJECT_NAME);
const API_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:3000';

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
  
  const testOutputDir = join(__dirname, '..', 'test-output');
  fs.ensureDirSync(testOutputDir);
  
  const expectScript = `#!/usr/bin/expect -f
set timeout 60
spawn node ${join(__dirname, '..', 'src', 'index.js')}

expect "What is your project name?" { send "${TEST_PROJECT_NAME}\\r" }
expect "Choose your UI library" { send "\\r" }
expect "Database name:" { send "\\r" }
expect "Database user:" { send "\\r" }
expect "Database password:" { send "password\\r" }
expect "Backend API port:" { send "\\r" }
expect "Frontend port:" { send "\\r" }
expect "Select additional features:" { send "\\r" }
expect eof
exit 0
`;

  const expectFile = join(testOutputDir, 'generate-e2e-test.exp');
  fs.writeFileSync(expectFile, expectScript);
  fs.chmodSync(expectFile, '755');
  
  try {
    execSync(expectFile, {
      cwd: testOutputDir,
      stdio: 'inherit'
    });
    console.log(success('✅ Project generated successfully'));
  } catch (err) {
    console.log(warning('⚠️  Generation ended'));
  } finally {
    fs.removeSync(expectFile);
  }
}

/**
 * Verify AuthContext implementation
 */
function verifyAuthContextImplementation() {
  console.log(info('\n🔍 Verifying AuthContext implementation...'));
  
  const authContextPath = join(TEST_DIR, 'frontend', 'src', 'contexts', 'AuthContext.js');
  
  if (!fs.existsSync(authContextPath)) {
    console.log(error('❌ AuthContext.js not found!'));
    return false;
  }
  
  const content = fs.readFileSync(authContextPath, 'utf-8');
  
  // Check for URLSearchParams (correct implementation)
  if (content.includes('URLSearchParams') && 
      content.includes("'Content-Type': 'application/x-www-form-urlencoded'")) {
    console.log(success('✅ AuthContext correctly uses URLSearchParams for form-data'));
    return true;
  } else {
    console.log(error('❌ AuthContext is NOT using URLSearchParams!'));
    console.log(warning('   It appears to be sending JSON instead of form-data'));
    
    // Show what's actually there
    const loginMatch = content.match(/const login = async[\s\S]*?^  \}/m);
    if (loginMatch) {
      console.log(info('\nActual login implementation:'));
      console.log(loginMatch[0].substring(0, 300) + '...');
    }
    return false;
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
    
    // Wait for backend to be ready
    let retries = 60;
    while (retries > 0) {
      try {
        const response = await axios.get(`${API_URL}/health`);
        if (response.status === 200) {
          console.log(success('✅ Backend is ready'));
          break;
        }
      } catch (e) {
        // Service not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
      retries--;
    }
    
    if (retries === 0) {
      throw new Error('Backend did not become ready in time');
    }
    
    // Wait for frontend
    retries = 30;
    while (retries > 0) {
      try {
        const response = await axios.get(FRONTEND_URL);
        if (response.status === 200) {
          console.log(success('✅ Frontend is ready'));
          break;
        }
      } catch (e) {
        // Service not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
      retries--;
    }
    
    // Wait a bit more for database initialization
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    return true;
  } catch (err) {
    console.log(error('❌ Failed to start services:'), err.message);
    return false;
  }
}

/**
 * Test login via API
 */
async function testLoginAPI() {
  console.log(info('\n🔐 Testing login via API...'));
  console.log('─'.repeat(60));
  
  const results = {
    jsonFails: false,
    formDataWorks: false,
    tokenReceived: false
  };
  
  // Test 1: JSON should fail with 422
  console.log(info('\n1️⃣ Testing JSON format (should fail with 422)...'));
  try {
    await axios.post(`${API_URL}/api/v1/auth/login`, {
      username: 'admin@example.com',
      password: 'admin123'
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    console.log(error('❌ JSON login succeeded (should have failed)'));
  } catch (err) {
    if (err.response && err.response.status === 422) {
      console.log(success('✅ JSON format correctly rejected with 422'));
      results.jsonFails = true;
    } else {
      console.log(error('❌ Unexpected error:'), err.response?.status || err.message);
    }
  }
  
  // Test 2: Form-data should work
  console.log(info('\n2️⃣ Testing form-data format (should succeed)...'));
  try {
    const params = new URLSearchParams();
    params.append('username', 'admin@example.com');
    params.append('password', 'admin123');
    
    const response = await axios.post(`${API_URL}/api/v1/auth/login`, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    if (response.status === 200) {
      console.log(success('✅ Form-data login successful!'));
      results.formDataWorks = true;
      
      if (response.data.access_token) {
        console.log(success('✅ Access token received'));
        results.tokenReceived = true;
      }
    }
  } catch (err) {
    console.log(error('❌ Form-data login failed:'), err.response?.status || err.message);
    if (err.response?.data) {
      console.log(error('   Error details:'), err.response.data);
    }
  }
  
  return results;
}

/**
 * Test login via browser
 */
async function testLoginBrowser() {
  console.log(info('\n🌐 Testing login via browser...'));
  console.log('─'.repeat(60));
  
  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Capture console logs
    const consoleLogs = [];
    page.on('console', msg => {
      const text = msg.text();
      consoleLogs.push({ type: msg.type(), text });
      if (msg.type() === 'error') {
        console.log(error('   Browser console error:'), text.substring(0, 100));
      }
    });
    
    // Navigate to login page
    console.log(info('📍 Navigating to login page...'));
    await page.goto(`${FRONTEND_URL}/login`, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Fill login form
    console.log(info('📝 Filling login form...'));
    await page.type('input[name="email"], input[type="email"]', 'admin@example.com');
    await page.type('input[name="email"], input[type="email"]', ADMIN_EMAIL);
    await page.type('input[name="password"], input[type="password"]', ADMIN_PASSWORD);
    
    // Submit form
    console.log(info('🚀 Submitting login...'));
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {})
    ]);
    
    // Wait a bit for any errors
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check for 422 error in console
    const has422Error = consoleLogs.some(log => 
      log.text.includes('422') || log.text.includes('Unprocessable Entity')
    );
    
    if (has422Error) {
      console.log(error('❌ Login failed with 422 error!'));
      console.log(error('   The frontend is still sending JSON instead of form-data'));
      return false;
    }
    
    // Check if we're on dashboard (successful login)
    const currentUrl = page.url();
    if (currentUrl.includes('/dashboard') || currentUrl === `${FRONTEND_URL}/`) {
      console.log(success('✅ Login successful! Redirected to dashboard'));
      return true;
    } else {
      console.log(warning('⚠️  Still on login page, checking for errors...'));
      
      // Check for error messages
      const errorElement = await page.$('[role="alert"], .alert-error, .error');
      if (errorElement) {
        const errorText = await page.evaluate(el => el.textContent, errorElement);
        console.log(error('❌ Login error displayed:'), errorText);
      }
      
      return false;
    }
    
  } catch (err) {
    console.log(error('❌ Browser test failed:'), err.message);
    return false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

/**
 * Main test function
 */
async function runTests() {
  console.log(chalk.bold.cyan('\n🔐 End-to-End Login Test\n'));
  console.log('═'.repeat(60));
  
  let allTestsPassed = true;
  
  try {
    // Clean up any previous test
    await cleanup();
    
    // Generate project
    generateProject();
    
    // Verify project exists
    if (!fs.existsSync(TEST_DIR)) {
      throw new Error('Project generation failed');
    }
    
    // Verify AuthContext implementation
    const authContextCorrect = verifyAuthContextImplementation();
    if (!authContextCorrect) {
      allTestsPassed = false;
      console.log(error('\n⚠️  AuthContext needs to be fixed!'));
    }
    
    // Start services
    const servicesStarted = await startServices();
    if (!servicesStarted) {
      throw new Error('Failed to start Docker services');
    }
    
    // Test API login
    const apiResults = await testLoginAPI();
    if (!apiResults.formDataWorks) {
      allTestsPassed = false;
    }
    
    // Test browser login
    const browserSuccess = await testLoginBrowser();
    if (!browserSuccess) {
      allTestsPassed = false;
    }
    
    // Final report
    console.log('\n' + chalk.bold('Test Summary:'));
    console.log('═'.repeat(60));
    console.log(authContextCorrect ? success('✅') : error('❌'), 'AuthContext uses URLSearchParams');
    console.log(apiResults.jsonFails ? success('✅') : error('❌'), 'API rejects JSON (422)');
    console.log(apiResults.formDataWorks ? success('✅') : error('❌'), 'API accepts form-data');
    console.log(apiResults.tokenReceived ? success('✅') : error('❌'), 'Token received from API');
    console.log(browserSuccess ? success('✅') : error('❌'), 'Browser login works');
    
  } catch (err) {
    console.log(error('\n❌ Test suite failed:'), err.message);
    allTestsPassed = false;
  } finally {
    // Clean up
    console.log(info('\n🧹 Cleaning up...'));
    await cleanup();
  }
  
  if (allTestsPassed) {
    console.log(success('\n✅ All tests passed! Login works correctly.'));
    process.exit(0);
  } else {
    console.log(error('\n❌ Tests failed! Login is not working correctly.'));
    console.log(error('The generated project still sends JSON instead of form-data.'));
    process.exit(1);
  }
}

// Check for puppeteer
if (!process.env.CI) {
  try {
    require.resolve('puppeteer');
  } catch (e) {
    console.log(warning('\n⚠️  Installing puppeteer for test...'));
    execSync('npm install --no-save puppeteer', { stdio: 'inherit' });
  }
}

// Run the tests
runTests().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});