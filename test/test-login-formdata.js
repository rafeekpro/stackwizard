#!/usr/bin/env node

/**
 * Test that login endpoint works with form-data format
 * This test verifies that the frontend sends data in the correct format
 * that the backend OAuth2PasswordRequestForm expects
 */

import fs from 'fs-extra';
import { execSync } from 'child_process';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import axios from 'axios';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

const TEST_PROJECT_NAME = 'test-login-formdata';
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

  const expectFile = join(testOutputDir, 'generate-login-test.exp');
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
    
    // Wait for backend to be ready
    let retries = 30;
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
    
    // Wait a bit more for database initialization
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    return true;
  } catch (err) {
    console.log(error('❌ Failed to start services:'), err.message);
    return false;
  }
}

/**
 * Test login with form-data
 */
async function testLoginFormData() {
  console.log(info('\n🔐 Testing login with form-data format...'));
  console.log('─'.repeat(60));
  
  const testResults = {
    jsonLogin: false,
    formDataLogin: false,
    adminLogin: false,
    tokenReceived: false,
    userDataReceived: false
  };
  
  try {
    // Test 1: Try JSON login (should fail with 422)
    console.log(info('\n1️⃣ Testing JSON format (should fail)...'));
    try {
      const jsonResponse = await axios.post(`${API_URL}/api/v1/auth/login`, {
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
        testResults.jsonLogin = true;
      } else {
        console.log(error('❌ Unexpected error:'), err.response?.status || err.message);
      }
    }
    
    // Test 2: Try form-data login (should succeed)
    console.log(info('\n2️⃣ Testing form-data format (should succeed)...'));
    try {
      const params = new URLSearchParams();
      params.append('username', 'admin@example.com');
      params.append('password', 'admin123');
      
      const formDataResponse = await axios.post(`${API_URL}/api/v1/auth/login`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      if (formDataResponse.status === 200) {
        console.log(success('✅ Form-data login successful!'));
        testResults.formDataLogin = true;
        
        // Check response structure
        const data = formDataResponse.data;
        if (data.access_token) {
          console.log(success('✅ Access token received'));
          testResults.tokenReceived = true;
        }
        
        // Test 3: Use token to get user info
        console.log(info('\n3️⃣ Testing token authentication...'));
        try {
          const verifyResponse = await axios.get(`${API_URL}/api/v1/auth/verify-token`, {
            headers: {
              'Authorization': `Bearer ${data.access_token}`
            }
          });
          
          if (verifyResponse.status === 200 && verifyResponse.data.email) {
            console.log(success('✅ Token verified, user data received'));
            console.log(info('   User:', verifyResponse.data.email));
            testResults.userDataReceived = true;
            
            if (verifyResponse.data.is_superuser) {
              console.log(success('✅ Admin user confirmed'));
              testResults.adminLogin = true;
            }
          }
        } catch (err) {
          console.log(error('❌ Token verification failed:'), err.message);
        }
      }
    } catch (err) {
      console.log(error('❌ Form-data login failed:'), err.response?.status || err.message);
      if (err.response?.data) {
        console.log(error('   Error details:'), err.response.data);
      }
    }
    
    // Test 4: Test with wrong credentials
    console.log(info('\n4️⃣ Testing with invalid credentials...'));
    try {
      const params = new URLSearchParams();
      params.append('username', 'wrong@example.com');
      params.append('password', 'wrongpass');
      
      await axios.post(`${API_URL}/api/v1/auth/login`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      console.log(error('❌ Invalid login succeeded (should have failed)'));
    } catch (err) {
      if (err.response && err.response.status === 401) {
        console.log(success('✅ Invalid credentials correctly rejected with 401'));
      } else {
        console.log(error('❌ Unexpected error:'), err.response?.status || err.message);
      }
    }
    
  } catch (err) {
    console.log(error('❌ Test failed:'), err.message);
  }
  
  return testResults;
}

/**
 * Test frontend login implementation
 */
async function testFrontendLogin() {
  console.log(info('\n🌐 Testing frontend login implementation...'));
  console.log('─'.repeat(60));
  
  // Check that AuthContext uses form-data
  const muiAuthPath = join(TEST_DIR, 'frontend', 'src', 'contexts', 'AuthContext.js');
  
  if (fs.existsSync(muiAuthPath)) {
    const content = fs.readFileSync(muiAuthPath, 'utf-8');
    
    // Check for URLSearchParams (form-data)
    if (content.includes('URLSearchParams') && 
        content.includes("'Content-Type': 'application/x-www-form-urlencoded'")) {
      console.log(success('✅ Frontend correctly uses form-data for login'));
      return true;
    } else {
      console.log(error('❌ Frontend not using form-data format'));
      return false;
    }
  } else {
    console.log(warning('⚠️  Frontend not found in generated project'));
    return false;
  }
}

/**
 * Main test function
 */
async function runTests() {
  console.log(chalk.bold.cyan('\n🔐 Login Form-Data Test\n'));
  console.log('═'.repeat(60));
  
  let testPassed = true;
  
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
    
    // Run login tests
    const testResults = await testLoginFormData();
    
    // Check frontend implementation
    const frontendCorrect = await testFrontendLogin();
    
    // Evaluate results
    const allTestsPassed = 
      testResults.formDataLogin &&
      testResults.tokenReceived &&
      testResults.userDataReceived &&
      testResults.adminLogin &&
      frontendCorrect;
    
    if (!allTestsPassed) {
      testPassed = false;
    }
    
    // Final report
    console.log('\n' + chalk.bold('Test Summary:'));
    console.log('═'.repeat(60));
    console.log(testResults.jsonLogin ? success('✅') : error('❌'), 'JSON format rejected (422)');
    console.log(testResults.formDataLogin ? success('✅') : error('❌'), 'Form-data login successful');
    console.log(testResults.tokenReceived ? success('✅') : error('❌'), 'Access token received');
    console.log(testResults.userDataReceived ? success('✅') : error('❌'), 'User data retrieved');
    console.log(testResults.adminLogin ? success('✅') : error('❌'), 'Admin user verified');
    console.log(frontendCorrect ? success('✅') : error('❌'), 'Frontend uses correct format');
    
  } catch (err) {
    console.log(error('\n❌ Test suite failed:'), err.message);
    testPassed = false;
  } finally {
    // Clean up
    console.log(info('\n🧹 Cleaning up...'));
    await cleanup();
  }
  
  if (testPassed) {
    console.log(success('\n✅ All login tests passed!'));
    console.log(success('Login with admin@example.com / admin123 works correctly.'));
    process.exit(0);
  } else {
    console.log(error('\n❌ Login tests failed!'));
    console.log(error('The login endpoint is not working correctly.'));
    process.exit(1);
  }
}

// Run the tests
runTests().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});