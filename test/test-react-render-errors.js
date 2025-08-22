#!/usr/bin/env node

/**
 * React Render Error Detection Test
 * Detects React errors when trying to render objects as children
 * Tests error handling in authentication flows
 */

import fs from 'fs-extra';
import path from 'path';
import { execSync } from 'child_process';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

const TEST_PROJECT_NAME = 'test-react-errors';
const TEST_DIR = join(__dirname, '..', 'test-output', TEST_PROJECT_NAME);
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

  const expectFile = join(testOutputDir, 'generate-react-test.exp');
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
    
    // Wait for services to start
    await new Promise(resolve => setTimeout(resolve, 15000));
    
    return true;
  } catch (err) {
    console.log(error('❌ Failed to start services:'), err.message);
    return false;
  }
}

/**
 * Test React render errors
 */
async function testReactRenderErrors() {
  console.log(info('\n🧪 Testing React render error handling...'));
  console.log('─'.repeat(60));
  
  let browser;
  const errors = [];
  const consoleErrors = [];
  
  try {
    // Launch browser with proper args for CI
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    const page = await browser.newPage();
    
    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        consoleErrors.push(text);
        
        // Check for React render errors
        if (text.includes('Objects are not valid as a React child')) {
          errors.push({
            type: 'REACT_RENDER_ERROR',
            message: text,
            severity: 'critical'
          });
          console.log(error('❌ React render error detected:'), text.substring(0, 100) + '...');
        }
        
        // Check for other React errors
        if (text.includes('Cannot read properties') || text.includes('undefined')) {
          errors.push({
            type: 'RUNTIME_ERROR',
            message: text,
            severity: 'high'
          });
          console.log(error('❌ Runtime error detected:'), text.substring(0, 100) + '...');
        }
      }
    });
    
    // Capture page errors
    page.on('pageerror', err => {
      errors.push({
        type: 'PAGE_ERROR',
        message: err.message,
        severity: 'critical'
      });
      console.log(error('❌ Page error:'), err.message);
    });
    
    // Test 1: Navigate to login page
    console.log(info('\n📍 Testing login page...'));
    await page.goto(`${FRONTEND_URL}/login`, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Test 2: Try login with invalid credentials to trigger error
    console.log(info('🔐 Testing error handling with invalid login...'));
    
    // Fill form with invalid data
    await page.type('input[name="email"], input[type="email"]', 'invalid@test.com');
    await page.type('input[name="password"], input[type="password"]', 'wrong');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for error to appear
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check if error is displayed properly (not as object)
    const errorElement = await page.$('[role="alert"], .alert, .error');
    if (errorElement) {
      const errorText = await page.evaluate(el => el.textContent, errorElement);
      console.log(info('📝 Error message displayed:'), errorText);
      
      // Check if error contains object notation
      if (errorText.includes('[object Object]') || errorText.includes('{')) {
        errors.push({
          type: 'ERROR_DISPLAY',
          message: 'Error displayed as object instead of text',
          severity: 'high'
        });
        console.log(error('❌ Error displayed as object!'));
      } else {
        console.log(success('✅ Error displayed correctly as text'));
      }
    }
    
    // Test 3: Navigate to register page
    console.log(info('\n📍 Testing register page...'));
    await page.goto(`${FRONTEND_URL}/register`, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Test 4: Try registration with invalid data
    console.log(info('📝 Testing registration error handling...'));
    
    // Submit empty form to trigger validation
    const registerButton = await page.$('button[type="submit"]');
    if (registerButton) {
      await registerButton.click();
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Test 5: Test dashboard (if accessible)
    console.log(info('\n📍 Testing dashboard...'));
    await page.goto(`${FRONTEND_URL}/`, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Wait and check for any delayed errors
    await new Promise(resolve => setTimeout(resolve, 3000));
    
  } catch (err) {
    console.log(error('❌ Test failed:'), err.message);
    errors.push({
      type: 'TEST_FAILURE',
      message: err.message,
      severity: 'critical'
    });
  } finally {
    if (browser) {
      await browser.close();
    }
  }
  
  return { errors, consoleErrors };
}

/**
 * Validate frontend error handling code
 */
function validateErrorHandling() {
  console.log(info('\n🔍 Validating error handling in source code...'));
  console.log('─'.repeat(60));
  
  const issues = [];
  const templates = ['frontend-mui', 'frontend-tailwind'];
  
  for (const template of templates) {
    const authContextPath = join(__dirname, '..', 'templates', template, 'src', 'contexts', 'AuthContext.js');
    
    if (fs.existsSync(authContextPath)) {
      const content = fs.readFileSync(authContextPath, 'utf-8');
      
      // Check for direct object rendering
      if (content.includes('error.response?.data?.detail ||') && 
          !content.includes('typeof error.response.data.detail')) {
        issues.push({
          file: `${template}/AuthContext.js`,
          issue: 'Missing type checking for error.response.data.detail',
          line: content.split('\n').findIndex(line => line.includes('error.response?.data?.detail ||')) + 1
        });
        console.log(warning(`⚠️  ${template}: Missing error type checking`));
      } else {
        console.log(success(`✅ ${template}: Error handling looks good`));
      }
      
      // Check for proper error extraction
      if (!content.includes('Array.isArray') || !content.includes('.map(')) {
        console.log(warning(`⚠️  ${template}: May not handle array errors properly`));
      }
    }
  }
  
  return issues;
}

/**
 * Main test function
 */
async function runTests() {
  console.log(chalk.bold.cyan('\n🎭 React Render Error Detection Test\n'));
  console.log('═'.repeat(60));
  
  let testPassed = true;
  const allErrors = [];
  
  try {
    // Clean up any previous test
    await cleanup();
    
    // Generate project
    generateProject();
    
    // Verify project exists
    if (!fs.existsSync(TEST_DIR)) {
      throw new Error('Project generation failed');
    }
    
    // Start services
    const servicesStarted = await startServices();
    if (!servicesStarted) {
      throw new Error('Failed to start Docker services');
    }
    
    // Run React render error tests
    const { errors, consoleErrors } = await testReactRenderErrors();
    allErrors.push(...errors);
    
    if (errors.length > 0) {
      testPassed = false;
      console.log(error(`\n❌ Found ${errors.length} React errors!`));
      errors.forEach(err => {
        console.log(error(`  - ${err.type}: ${err.message.substring(0, 100)}...`));
      });
    }
    
    // Validate source code
    const codeIssues = validateErrorHandling();
    if (codeIssues.length > 0) {
      testPassed = false;
      console.log(error(`\n❌ Found ${codeIssues.length} code issues!`));
    }
    
  } catch (err) {
    console.log(error('\n❌ Test suite failed:'), err.message);
    testPassed = false;
  } finally {
    // Clean up
    console.log(info('\n🧹 Cleaning up...'));
    await cleanup();
  }
  
  // Final report
  console.log('\n' + chalk.bold('Test Summary:'));
  console.log('═'.repeat(60));
  
  if (testPassed) {
    console.log(success('✅ No React render errors detected!'));
    console.log(success('Error handling is working correctly.'));
    process.exit(0);
  } else {
    console.log(error('❌ React render errors detected!'));
    console.log(error('Objects are being rendered as React children.'));
    console.log(warning('\nTo fix:'));
    console.log('1. Ensure all error messages are strings, not objects');
    console.log('2. Add type checking for error.response?.data?.detail');
    console.log('3. Handle array and object error formats from FastAPI');
    process.exit(1);
  }
}

// Check if puppeteer is installed (only install if not in CI)
if (!process.env.CI) {
  try {
    require.resolve('puppeteer');
  } catch (e) {
    console.log(warning('\n⚠️  Puppeteer not installed. Installing for test...'));
    execSync('npm install --no-save puppeteer', { stdio: 'inherit' });
  }
}

// Run the tests
runTests().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});