#!/usr/bin/env node

/**
 * Test for React Router issues:
 * - Deprecation warnings
 * - Missing routes
 * - Console errors
 */

import fs from 'fs-extra';
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

const TEST_PROJECT_NAME = 'test-router-issues';
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
        // Ignore cleanup errors
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
function generateProject(uiLibrary = 'mui') {
  console.log(info('\n📦 Generating test project with ' + uiLibrary + '...'));
  
  const testOutputDir = join(__dirname, '..', 'test-output');
  fs.ensureDirSync(testOutputDir);
  
  const expectScript = `#!/usr/bin/expect -f
set timeout 60
spawn node ${join(__dirname, '..', 'src', 'index.js')}

expect "What is your project name?" { send "${TEST_PROJECT_NAME}\\r" }
expect "Choose your UI library" { 
  ${uiLibrary === 'tailwind' ? 'send "\\033\\[B\\r"' : 'send "\\r"'}
}
expect "Database name:" { send "\\r" }
expect "Database user:" { send "\\r" }
expect "Database password:" { send "password\\r" }
expect "Backend API port:" { send "\\r" }
expect "Frontend port:" { send "\\r" }
expect "Select additional features:" { send "\\r" }
expect eof
exit 0
`;

  const expectFile = join(testOutputDir, 'generate-router-test.exp');
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
 * Check for React Router v7 future flags
 */
function checkReactRouterConfig() {
  console.log(info('\n🔍 Checking React Router configuration...'));
  
  const appJsPath = join(TEST_DIR, 'frontend', 'src', 'App.js');
  
  if (!fs.existsSync(appJsPath)) {
    console.log(error('❌ App.js not found!'));
    return false;
  }
  
  const content = fs.readFileSync(appJsPath, 'utf-8');
  
  // Check for future flags
  const hasFutureFlags = content.includes('v7_startTransition') || 
                         content.includes('v7_relativeSplatPath');
  
  if (!hasFutureFlags) {
    console.log(warning('⚠️  React Router v7 future flags not configured'));
    console.log(warning('   This will cause deprecation warnings'));
    return false;
  }
  
  console.log(success('✅ React Router v7 future flags configured'));
  return true;
}

/**
 * Check for missing routes
 */
function checkRoutes() {
  console.log(info('\n🔍 Checking route definitions...'));
  
  const appJsPath = join(TEST_DIR, 'frontend', 'src', 'App.js');
  const content = fs.readFileSync(appJsPath, 'utf-8');
  
  const requiredRoutes = [
    '/login',
    '/register',
    '/dashboard',
    '/users',
    '/items',
    '/about',
    '/unauthorized'
  ];
  
  const missingRoutes = [];
  
  for (const route of requiredRoutes) {
    // Check if route is defined in various formats
    const routeRegex = new RegExp(`path=["'\`]${route}["'\`]|"${route}"|'${route}'|\`${route}\``);
    if (!routeRegex.test(content)) {
      missingRoutes.push(route);
    }
  }
  
  if (missingRoutes.length > 0) {
    console.log(error('❌ Missing routes:'), missingRoutes.join(', '));
    return false;
  }
  
  console.log(success('✅ All required routes defined'));
  return true;
}

/**
 * Test with Puppeteer for console warnings
 */
async function testBrowserWarnings() {
  console.log(info('\n🌐 Testing for browser warnings and errors...'));
  
  let browser;
  const issues = {
    deprecationWarnings: [],
    consoleErrors: [],
    missingRoutes: []
  };
  
  try {
    // Start services
    console.log(info('🐳 Starting Docker services...'));
    execSync('docker compose up -d', {
      cwd: TEST_DIR,
      stdio: 'inherit'
    });
    
    // Wait for services
    await new Promise(resolve => setTimeout(resolve, 15000));
    
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Capture console messages
    page.on('console', msg => {
      const text = msg.text();
      
      // Check for React Router deprecation warnings
      if (text.includes('React Router Future Flag Warning')) {
        issues.deprecationWarnings.push(text);
        console.log(warning('⚠️  Deprecation warning detected:'), text.substring(0, 100) + '...');
      }
      
      // Check for missing route warnings
      if (text.includes('No routes matched location')) {
        const match = text.match(/No routes matched location "([^"]+)"/);
        if (match) {
          issues.missingRoutes.push(match[1]);
          console.log(error('❌ Missing route:'), match[1]);
        }
      }
      
      // Check for console errors
      if (msg.type() === 'error') {
        issues.consoleErrors.push(text);
        console.log(error('❌ Console error:'), text.substring(0, 100) + '...');
      }
    });
    
    // Navigate to app
    console.log(info('📍 Navigating to application...'));
    await page.goto(FRONTEND_URL, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Try to navigate to login
    console.log(info('📍 Navigating to login...'));
    await page.goto(`${FRONTEND_URL}/login`, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Try to navigate to unauthorized (this will likely fail)
    console.log(info('📍 Testing unauthorized route...'));
    await page.goto(`${FRONTEND_URL}/unauthorized`, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    }).catch(() => {
    }).catch((err) => {
      console.log(warning('⚠️  /unauthorized route not accessible'));
      console.log(warning('Error details:'), err && err.message ? err.message : err);
    });
    
    // Wait for any async warnings
    await new Promise(resolve => setTimeout(resolve, 3000));
    
  } catch (err) {
    console.log(error('❌ Browser test failed:'), err.message);
  } finally {
    if (browser) {
      await browser.close();
    }
    
    // Stop services
    try {
      execSync('docker compose down', {
        cwd: TEST_DIR,
        stdio: 'ignore'
      });
    } catch (e) {
      // Ignore
    }
  }
  
  return issues;
}

/**
 * Main test function
 */
async function runTests() {
  console.log(chalk.bold.cyan('\n🔍 React Router Issues Test\n'));
  console.log('═'.repeat(60));
  
  let allTestsPassed = true;
  const results = {
    mui: { configOk: false, routesOk: false, browserIssues: null },
    tailwind: { configOk: false, routesOk: false, browserIssues: null }
  };
  
  try {
    // Test both UI libraries
    for (const uiLibrary of ['mui', 'tailwind']) {
      console.log(chalk.bold(`\n\n📦 Testing ${uiLibrary.toUpperCase()} Template`));
      console.log('─'.repeat(60));
      
      // Clean up any previous test
      await cleanup();
      
      // Generate project
      generateProject(uiLibrary);
      
      // Verify project exists
      if (!fs.existsSync(TEST_DIR)) {
        throw new Error(`Project generation failed for ${uiLibrary}`);
      }
      
      // Check React Router configuration
      results[uiLibrary].configOk = checkReactRouterConfig();
      if (!results[uiLibrary].configOk) {
        allTestsPassed = false;
      }
      
      // Check routes
      results[uiLibrary].routesOk = checkRoutes();
      if (!results[uiLibrary].routesOk) {
        allTestsPassed = false;
      }
      
      // Test in browser
      results[uiLibrary].browserIssues = await testBrowserWarnings();
      if (results[uiLibrary].browserIssues.deprecationWarnings.length > 0 ||
          results[uiLibrary].browserIssues.missingRoutes.length > 0 ||
          results[uiLibrary].browserIssues.consoleErrors.length > 0) {
        allTestsPassed = false;
      }
      
      // Clean up
      await cleanup();
    }
    
    // Final report
    console.log('\n' + chalk.bold('Test Summary:'));
    console.log('═'.repeat(60));
    
    for (const [lib, result] of Object.entries(results)) {
      console.log(chalk.bold(`\n${lib.toUpperCase()} Template:`));
      console.log(result.configOk ? success('✅') : error('❌'), 'React Router v7 future flags');
      console.log(result.routesOk ? success('✅') : error('❌'), 'All routes defined');
      
      if (result.browserIssues) {
        const depWarnings = result.browserIssues.deprecationWarnings.length;
        const missingRoutes = result.browserIssues.missingRoutes.length;
        const consoleErrors = result.browserIssues.consoleErrors.length;
        
        console.log(depWarnings === 0 ? success('✅') : error('❌'), 
                   `Deprecation warnings: ${depWarnings}`);
        console.log(missingRoutes === 0 ? success('✅') : error('❌'), 
                   `Missing routes: ${missingRoutes}`);
        console.log(consoleErrors === 0 ? success('✅') : error('❌'), 
                   `Console errors: ${consoleErrors}`);
      }
    }
    
  } catch (err) {
    console.log(error('\n❌ Test suite failed:'), err.message);
    allTestsPassed = false;
  } finally {
    // Final cleanup
    await cleanup();
  }
  
  if (allTestsPassed) {
    console.log(success('\n✅ All tests passed!'));
    process.exit(0);
  } else {
    console.log(error('\n❌ Tests failed! React Router issues detected.'));
    console.log(error('The templates need to be updated with:'));
    console.log(error('1. React Router v7 future flags'));
    console.log(error('2. Missing /unauthorized route'));
    process.exit(1);
  }
}

// Check for puppeteer
if (!process.env.CI) {
  (async () => {
    try {
      await import('puppeteer');
    } catch (e) {
      console.log(warning('\n⚠️  Installing puppeteer for test...'));
      execSync('npm install --no-save puppeteer', { stdio: 'inherit' });
    }
  })();
}

// Run the tests
runTests().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});