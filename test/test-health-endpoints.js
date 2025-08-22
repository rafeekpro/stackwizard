#!/usr/bin/env node

/**
 * Comprehensive test for health endpoints in generated projects
 * This test ensures that health endpoints are properly configured and accessible
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

const TEST_PROJECT_NAME = 'test-health-endpoints';
const TEST_DIR = path.join(__dirname, '..', 'test-output', TEST_PROJECT_NAME);

// Clean up function
async function cleanup() {
  try {
    // Stop Docker containers if running
    if (fs.existsSync(TEST_DIR)) {
      try {
        execSync('docker compose down -v', { 
          cwd: TEST_DIR,
          stdio: 'ignore'
        });
      } catch (e) {
        // Ignore errors
      }
      
      // Remove test directory
      await fs.remove(TEST_DIR);
    }
  } catch (err) {
    console.log(warning('Warning: Cleanup encountered issues:'), err.message);
  }
}

// Generate test project
function generateProject() {
  console.log(info('\n📦 Generating test project...'));
  
  // Ensure test output directory exists
  const testOutputDir = path.join(__dirname, '..', 'test-output');
  fs.ensureDirSync(testOutputDir);
  
  // Create expect script for automated responses
  const expectScript = `#!/usr/bin/expect -f
set timeout 60
spawn node ${path.join(__dirname, '..', 'src', 'index.js')}

# Wait for project name prompt
expect {
  "What is your project name?" {
    send "${TEST_PROJECT_NAME}\\r"
  }
  timeout {
    puts "Timeout waiting for project name prompt"
    exit 1
  }
}

# Choose UI library (default Material UI)
expect {
  "Choose your UI library" {
    send "\\r"
  }
  timeout {
    puts "Timeout waiting for UI library prompt"
    exit 1
  }
}

# Database name
expect {
  "Database name:" {
    send "\\r"
  }
  timeout {
    puts "Timeout waiting for database name prompt"
    exit 1
  }
}

# Database user
expect {
  "Database user:" {
    send "\\r"
  }
  timeout {
    puts "Timeout waiting for database user prompt"
    exit 1
  }
}

# Database password
expect {
  "Database password:" {
    send "password\\r"
  }
  timeout {
    puts "Timeout waiting for database password prompt"
    exit 1
  }
}

# Backend API port
expect {
  "Backend API port:" {
    send "\\r"
  }
  timeout {
    puts "Timeout waiting for backend port prompt"
    exit 1
  }
}

# Frontend port
expect {
  "Frontend port:" {
    send "\\r"
  }
  timeout {
    puts "Timeout waiting for frontend port prompt"
    exit 1
  }
}

# Additional features
expect {
  "Select additional features:" {
    send "\\r"
  }
  timeout {
    puts "Timeout waiting for features prompt"
    exit 1
  }
}

# Wait for completion
expect {
  "Project created successfully" {
    puts "\\nProject generation completed successfully"
  }
  "Successfully created your full-stack project" {
    puts "\\nProject generation completed successfully"
  }
  timeout {
    puts "\\nProject generation may have completed"
  }
  eof {
    puts "\\nProcess ended"
  }
}

exit 0
`;

  const expectFile = path.join(testOutputDir, 'generate-health-test.exp');
  fs.writeFileSync(expectFile, expectScript);
  fs.chmodSync(expectFile, '755');
  
  try {
    execSync(expectFile, {
      cwd: testOutputDir,
      stdio: 'inherit'
    });
    
    console.log(success('✅ Project generated successfully'));
  } catch (err) {
    console.log(warning('⚠️  Generation script ended, checking if project was created...'));
  } finally {
    // Clean up expect script
    fs.removeSync(expectFile);
  }
}

// Test health endpoints
async function testHealthEndpoints() {
  console.log(info('\n🔍 Testing health endpoints...'));
  
  const backendUrl = 'http://localhost:8000';
  const endpoints = [
    { path: '/health', name: 'Root health' },
    { path: '/health/db', name: 'Database health' },
    { path: '/api/health', name: 'API health' },
    { path: '/api/health/db', name: 'API database health' },
    { path: '/api/v1/health', name: 'API v1 health' },
    { path: '/api/v1/health/db', name: 'API v1 database health' }
  ];
  
  const results = [];
  let hasErrors = false;
  
  for (const endpoint of endpoints) {
    try {
      const response = await axios.get(`${backendUrl}${endpoint.path}`, {
        timeout: 5000
      });
      
      if (response.status === 200) {
        results.push({
          endpoint: endpoint.path,
          name: endpoint.name,
          status: 'success',
          data: response.data
        });
        console.log(success(`  ✅ ${endpoint.name}: ${endpoint.path}`));
      } else {
        results.push({
          endpoint: endpoint.path,
          name: endpoint.name,
          status: 'error',
          error: `Status ${response.status}`
        });
        console.log(error(`  ❌ ${endpoint.name}: ${endpoint.path} - Status ${response.status}`));
        hasErrors = true;
      }
    } catch (err) {
      results.push({
        endpoint: endpoint.path,
        name: endpoint.name,
        status: 'error',
        error: err.message
      });
      console.log(error(`  ❌ ${endpoint.name}: ${endpoint.path} - ${err.message}`));
      hasErrors = true;
    }
  }
  
  // Test database connectivity
  console.log(info('\n🗄️  Testing database connectivity...'));
  const dbEndpoints = ['/health/db', '/api/health/db', '/api/v1/health/db'];
  
  for (const endpoint of dbEndpoints) {
    const result = results.find(r => r.endpoint === endpoint);
    if (result && result.status === 'success') {
      if (result.data.database === 'connected') {
        console.log(success(`  ✅ Database connected via ${endpoint}`));
      } else {
        console.log(warning(`  ⚠️  Database disconnected via ${endpoint}`));
        hasErrors = true;
      }
    }
  }
  
  return { results, hasErrors };
}

// Test frontend API calls
async function testFrontendIntegration() {
  console.log(info('\n🌐 Testing frontend API integration...'));
  
  // Check if frontend correctly calls health endpoints
  const frontendApiFile = path.join(TEST_DIR, 'frontend', 'src', 'services', 'api.js');
  
  if (fs.existsSync(frontendApiFile)) {
    const content = fs.readFileSync(frontendApiFile, 'utf8');
    
    // Check for correct health endpoint configuration
    if (content.includes('/api/health')) {
      console.log(success('  ✅ Frontend uses correct health endpoint'));
    } else {
      console.log(error('  ❌ Frontend uses incorrect health endpoint'));
      return false;
    }
    
    // Check for environment variable usage
    if (content.includes('process.env.REACT_APP_API_URL')) {
      console.log(success('  ✅ Frontend uses environment variable for API URL'));
    } else {
      console.log(warning('  ⚠️  Frontend hardcodes API URL'));
    }
  } else {
    console.log(error('  ❌ Frontend API file not found'));
    return false;
  }
  
  return true;
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

// Main test function
async function runTest() {
  console.log(chalk.bold.cyan('\n🧪 Health Endpoints Comprehensive Test\n'));
  console.log('═'.repeat(50));
  
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
    
    // Test health endpoints
    const { hasErrors } = await testHealthEndpoints();
    if (hasErrors) {
      testPassed = false;
    }
    
    // Test frontend integration
    const frontendOk = await testFrontendIntegration();
    if (!frontendOk) {
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
  console.log('═'.repeat(50));
  
  if (testPassed) {
    console.log(success('✅ All health endpoint tests passed!'));
    console.log(success('Health endpoints are properly configured and accessible.'));
    process.exit(0);
  } else {
    console.log(error('❌ Health endpoint tests failed!'));
    console.log(error('Please fix the issues and run the test again.'));
    process.exit(1);
  }
}

// Run the test
runTest().catch(err => {
  console.error(error('Fatal error:'), err);
  cleanup().then(() => process.exit(1));
});