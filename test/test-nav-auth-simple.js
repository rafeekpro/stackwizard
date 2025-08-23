#!/usr/bin/env node

/**
 * Simplified Navigation Auth Test - MUI Only
 * This is a quick test to verify the navigation menu issue
 */

import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_DIR = path.join(__dirname, '..', 'test-output');
const PROJECT_NAME = 'test-nav-simple';

// Use fixed high ports to avoid conflicts
const BACKEND_PORT = 18765;
const FRONTEND_PORT = 13765;
const DB_PORT = 15765;

async function cleanup() {
  console.log('Cleaning up...');
  const projectPath = path.join(TEST_DIR, PROJECT_NAME);
  if (fs.existsSync(projectPath)) {
    try {
      execSync('docker compose down -v', { 
        cwd: projectPath, 
        stdio: 'ignore' 
      });
    } catch (error) {
      // Ignore
    }
  }
  await fs.remove(TEST_DIR);
}

async function runTest() {
  console.log('🧪 Simple Navigation Auth Test - MUI\n');
  
  try {
    // Clean up first
    await cleanup();
    
    // Create test directory
    await fs.ensureDir(TEST_DIR);
    
    // Generate project
    console.log('1️⃣ Generating project...');
    execSync(`node ${path.join(__dirname, '..', 'src', 'index.js')} --name ${PROJECT_NAME} --ui mui --quick`, {
      cwd: TEST_DIR,
      stdio: 'inherit'
    });
    
    const projectPath = path.join(TEST_DIR, PROJECT_NAME);
    
    // Update ports in docker-compose.yml
    console.log('2️⃣ Updating ports...');
    const dockerComposePath = path.join(projectPath, 'docker-compose.yml');
    let dockerComposeContent = fs.readFileSync(dockerComposePath, 'utf8');
    dockerComposeContent = dockerComposeContent
      .replace(/- "8000:8000"/g, `- "${BACKEND_PORT}:8000"`)
      .replace(/- "3000:3000"/g, `- "${FRONTEND_PORT}:3000"`)
      .replace(/- "5432:5432"/g, `- "${DB_PORT}:5432"`);
    fs.writeFileSync(dockerComposePath, dockerComposeContent);
    
    // Start services
    console.log('3️⃣ Starting Docker services...');
    execSync('docker compose up -d --build', { 
      cwd: projectPath,
      stdio: 'inherit'
    });
    
    // Wait for services
    console.log('4️⃣ Waiting for services to be ready...');
    for (let i = 0; i < 60; i++) {
      try {
        const healthCheck = execSync(`curl -s http://localhost:${BACKEND_PORT}/health`, {
          encoding: 'utf8'
        });
        const health = JSON.parse(healthCheck);
        if (health.api === 'healthy' && health.database === 'healthy') {
          console.log('✅ Services are ready');
          break;
        }
      } catch (error) {
        // Not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Test with Puppeteer
    console.log('5️⃣ Testing navigation menu...');
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    
    // Go to app
    await page.goto(`http://localhost:${FRONTEND_PORT}`, { waitUntil: 'networkidle0' });
    
    // Check navigation before login
    console.log('\n📍 BEFORE LOGIN:');
    let navItems = await page.evaluate(() => {
      const items = [];
      document.querySelectorAll('nav button, nav a').forEach(el => {
        const text = el.textContent.trim();
        if (text) items.push(text);
      });
      return items;
    });
    console.log('Navigation items:', navItems);
    
    // Go to login
    await page.goto(`http://localhost:${FRONTEND_PORT}/login`, { waitUntil: 'networkidle0' });
    
    // Login
    await page.type('input[name="email"]', 'admin@example.com');
    await page.type('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    
    // Check URL
    const currentUrl = page.url();
    console.log('\n📍 AFTER LOGIN:');
    console.log('Current URL:', currentUrl);
    
    // Check navigation after login
    navItems = await page.evaluate(() => {
      const items = [];
      document.querySelectorAll('nav button, nav a').forEach(el => {
        const text = el.textContent.trim();
        if (text) items.push(text);
      });
      return items;
    });
    console.log('Navigation items:', navItems);
    
    // Check if user is stored in localStorage
    const localStorage = await page.evaluate(() => {
      return {
        token: window.localStorage.getItem('token'),
        user: window.localStorage.getItem('user')
      };
    });
    console.log('\n📍 LOCAL STORAGE:');
    console.log('Has token:', !!localStorage.token);
    console.log('Has user:', !!localStorage.user);
    if (localStorage.user) {
      console.log('User data:', JSON.parse(localStorage.user));
    }
    
    // Check AuthContext state
    const authState = await page.evaluate(() => {
      // Try to access React DevTools if available
      const reactFiber = document.querySelector('#root')._reactRootContainer?._internalRoot?.current;
      if (reactFiber) {
        // Traverse to find AuthContext
        let node = reactFiber;
        while (node) {
          if (node.memoizedProps?.value?.user) {
            return {
              user: node.memoizedProps.value.user,
              isAuthenticated: node.memoizedProps.value.isAuthenticated
            };
          }
          node = node.child || node.sibling;
        }
      }
      return null;
    });
    console.log('\n📍 AUTH CONTEXT STATE:');
    console.log('Auth state:', authState);
    
    await browser.close();
    
    // Stop services
    console.log('\n6️⃣ Stopping services...');
    execSync('docker compose down', { 
      cwd: projectPath,
      stdio: 'ignore'
    });
    
    // Analyze results
    console.log('\n' + '='.repeat(50));
    console.log('🔍 ISSUE ANALYSIS:');
    
    const hasSignInAfterLogin = navItems.includes('Sign In');
    const hasSignUpAfterLogin = navItems.includes('Sign Up');
    const hasUsersAfterLogin = navItems.includes('Users');
    const hasItemsAfterLogin = navItems.includes('Items');
    const hasLogoutAfterLogin = navItems.includes('Logout');
    
    if (hasSignInAfterLogin || hasSignUpAfterLogin) {
      console.log('❌ PROBLEM: Sign In/Sign Up buttons still visible after login');
    }
    if (!hasUsersAfterLogin || !hasItemsAfterLogin) {
      console.log('❌ PROBLEM: Users/Items menu items not visible after login');
    }
    if (!hasLogoutAfterLogin) {
      console.log('❌ PROBLEM: Logout button not visible after login');
    }
    
    if (hasSignInAfterLogin || hasSignUpAfterLogin || !hasUsersAfterLogin || !hasItemsAfterLogin || !hasLogoutAfterLogin) {
      console.log('\n⚠️ The navigation menu is NOT updating correctly after login');
      console.log('This confirms the issue reported by the user.');
    } else {
      console.log('\n✅ Navigation menu is updating correctly');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await cleanup();
  }
}

// Run the test
runTest();