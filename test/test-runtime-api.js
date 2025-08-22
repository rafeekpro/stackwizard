#!/usr/bin/env node

/**
 * Runtime API test for generated projects
 * Tests actual API calls in a running Docker environment
 */

import fs from 'fs-extra';
import path from 'path';
import { execSync } from 'child_process';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

const TEST_PROJECT_NAME = 'test-runtime-api';
const TEST_DIR = path.join(__dirname, '..', 'test-output', TEST_PROJECT_NAME);

// API test cases
const API_TESTS = [
  {
    name: 'Health Check',
    method: 'GET',
    endpoint: '/health',
    expectedStatus: 200,
    requiresAuth: false
  },
  {
    name: 'Database Health',
    method: 'GET',
    endpoint: '/health/db',
    expectedStatus: 200,
    requiresAuth: false
  },
  {
    name: 'API Health',
    method: 'GET',
    endpoint: '/api/health',
    expectedStatus: 200,
    requiresAuth: false
  },
  {
    name: 'API Database Health',
    method: 'GET',
    endpoint: '/api/health/db',
    expectedStatus: 200,
    requiresAuth: false
  },
  {
    name: 'Login Endpoint Exists',
    method: 'POST',
    endpoint: '/api/v1/auth/login',
    expectedStatus: 422, // Will get validation error without data
    requiresAuth: false
  },
  {
    name: 'Register Endpoint Exists',
    method: 'POST',
    endpoint: '/api/v1/auth/register',
    expectedStatus: 422,
    requiresAuth: false
  },
  {
    name: 'Admin Login',
    method: 'POST',
    endpoint: '/api/v1/auth/login',
    data: {
      username: 'admin@example.com',
      password: 'Admin123!'
    },
    contentType: 'application/x-www-form-urlencoded',
    expectedStatus: 200,
    requiresAuth: false,
    saveToken: true
  },
  {
    name: 'Get Current User',
    method: 'GET',
    endpoint: '/api/v1/users/me',
    expectedStatus: 200,
    requiresAuth: true
  },
  {
    name: 'List Users',
    method: 'GET',
    endpoint: '/api/v1/users/',
    expectedStatus: 200,
    requiresAuth: true
  },
  {
    name: 'List Items',
    method: 'GET',
    endpoint: '/api/v1/items/',
    expectedStatus: 200,
    requiresAuth: true
  },
  {
    name: 'Admin Stats',
    method: 'GET',
    endpoint: '/api/v1/admin/stats',
    expectedStatus: 200,
    requiresAuth: true
  },
  {
    name: 'Logout',
    method: 'POST',
    endpoint: '/api/v1/auth/logout',
    expectedStatus: 200,
    requiresAuth: true
  }
];

// Clean up function
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

// Generate test project
function generateProject() {
  console.log(info('\n📦 Generating test project...'));
  
  const testOutputDir = path.join(__dirname, '..', 'test-output');
  fs.ensureDirSync(testOutputDir);
  
  // Create expect script
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

  const expectFile = path.join(testOutputDir, 'generate-runtime-test.exp');
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

// Start Docker services
async function startDockerServices() {
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
        await axios.get('http://localhost:8000/health', { timeout: 1000 });
        console.log(success('✅ Backend is ready'));
        break;
      } catch (err) {
        retries--;
        if (retries === 0) {
          throw new Error('Backend failed to start');
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    // Give database time to initialize
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    return true;
  } catch (err) {
    console.log(error('❌ Failed to start Docker services:'), err.message);
    return false;
  }
}

// Run API tests
async function runAPITests() {
  console.log(info('\n🧪 Running API tests...'));
  console.log('─'.repeat(60));
  
  const results = [];
  let token = null;
  let hasErrors = false;
  
  for (const test of API_TESTS) {
    try {
      const config = {
        method: test.method,
        url: `http://localhost:8000${test.endpoint}`,
        validateStatus: () => true // Don't throw on any status
      };
      
      // Add auth header if required
      if (test.requiresAuth && token) {
        config.headers = {
          Authorization: `Bearer ${token}`
        };
      }
      
      // Add data if provided
      if (test.data) {
        if (test.contentType === 'application/x-www-form-urlencoded') {
          const params = new URLSearchParams();
          Object.entries(test.data).forEach(([key, value]) => {
            params.append(key, value);
          });
          config.data = params;
          config.headers = {
            ...config.headers,
            'Content-Type': 'application/x-www-form-urlencoded'
          };
        } else {
          config.data = test.data;
        }
      }
      
      const response = await axios(config);
      
      const testPassed = response.status === test.expectedStatus;
      
      if (testPassed) {
        console.log(success(`✅ ${test.name}: ${test.method} ${test.endpoint} - Status ${response.status}`));
        
        // Save token if this is login
        if (test.saveToken && response.data?.access_token) {
          token = response.data.access_token;
          console.log(info('   Token saved for authenticated requests'));
        }
      } else {
        console.log(error(`❌ ${test.name}: ${test.method} ${test.endpoint}`));
        console.log(error(`   Expected status ${test.expectedStatus}, got ${response.status}`));
        hasErrors = true;
      }
      
      results.push({
        name: test.name,
        endpoint: test.endpoint,
        method: test.method,
        passed: testPassed,
        status: response.status,
        expected: test.expectedStatus
      });
      
    } catch (err) {
      console.log(error(`❌ ${test.name}: ${test.method} ${test.endpoint}`));
      console.log(error(`   Error: ${err.message}`));
      hasErrors = true;
      
      results.push({
        name: test.name,
        endpoint: test.endpoint,
        method: test.method,
        passed: false,
        error: err.message
      });
    }
  }
  
  return { results, hasErrors };
}

// Main test function
async function runTest() {
  console.log(chalk.bold.cyan('\n🚀 Runtime API Test\n'));
  console.log('═'.repeat(60));
  
  let testPassed = true;
  
  try {
    // Clean up any previous test
    await cleanup();
    
    // Generate project
    generateProject();
    
    // Verify project structure
    if (!fs.existsSync(TEST_DIR)) {
      throw new Error('Project generation failed - directory not created');
    }
    
    // Start Docker services
    const servicesStarted = await startDockerServices();
    if (!servicesStarted) {
      throw new Error('Failed to start Docker services');
    }
    
    // Run API tests
    const { hasErrors } = await runAPITests();
    if (hasErrors) {
      testPassed = false;
    }
    
  } catch (err) {
    console.log(error('\n❌ Test failed:'), err.message);
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
    console.log(success('✅ All runtime API tests passed!'));
    console.log(success('All endpoints are accessible and working correctly.'));
    process.exit(0);
  } else {
    console.log(error('❌ Runtime API tests failed!'));
    console.log(error('Some endpoints returned unexpected responses or errors.'));
    process.exit(1);
  }
}

// Run the test
runTest().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});