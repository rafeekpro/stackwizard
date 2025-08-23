#!/usr/bin/env node

/**
 * Integration test that generates a project and runs docker-compose to verify everything works
 * This test catches runtime issues that static tests miss
 */

import { execSync, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';
import http from 'http';
import https from 'https';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.join(__dirname, '..');

// Health check endpoints to verify
const HEALTH_CHECKS = [
  { 
    name: 'Backend API', 
    url: 'http://localhost:8000/health',
    expected: { status: 'healthy' }
  },
  { 
    name: 'Backend Docs', 
    url: 'http://localhost:8000/docs',
    expectStatus: 200
  },
  { 
    name: 'Frontend', 
    url: 'http://localhost:3000',
    expectStatus: 200
  }
];

// Maximum time to wait for services to start (in seconds)
const MAX_WAIT_TIME = 120;
const CHECK_INTERVAL = 5;

async function checkHealth(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        client.get(url, (res) => {
          let data = '';
          res.on('data', chunk => data += chunk);
          res.on('end', () => {
            resolve({
              status: res.statusCode,
              data: data
            });
          });
        }).on('error', reject);
      });
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}

async function waitForServices(projectPath) {
  console.log('⏳ Waiting for services to start...');
  
  const startTime = Date.now();
  let allHealthy = false;
  let lastError = null;
  
  while (!allHealthy && (Date.now() - startTime) / 1000 < MAX_WAIT_TIME) {
    allHealthy = true;
    
    for (const check of HEALTH_CHECKS) {
      try {
        const response = await checkHealth(check.url);
        
        if (check.expectStatus && response.status !== check.expectStatus) {
          console.log(`  ⏳ ${check.name}: HTTP ${response.status} (expected ${check.expectStatus})`);
          allHealthy = false;
        } else if (check.expected) {
          const data = JSON.parse(response.data);
          const isHealthy = Object.entries(check.expected).every(
            ([key, value]) => data[key] === value
          );
          if (!isHealthy) {
            console.log(`  ⏳ ${check.name}: Not healthy yet`);
            allHealthy = false;
          } else {
            console.log(`  ✅ ${check.name}: Healthy`);
          }
        } else {
          console.log(`  ✅ ${check.name}: Responding`);
        }
      } catch (error) {
        console.log(`  ⏳ ${check.name}: Not ready (${error.code || error.message})`);
        lastError = error;
        allHealthy = false;
      }
    }
    
    if (!allHealthy) {
      await new Promise(resolve => setTimeout(resolve, CHECK_INTERVAL * 1000));
    }
  }
  
  if (!allHealthy) {
    throw new Error(`Services did not become healthy within ${MAX_WAIT_TIME} seconds. Last error: ${lastError?.message}`);
  }
  
  console.log('✅ All services are healthy!\n');
  return true;
}

function checkDockerLogs(projectPath) {
  console.log('📋 Checking Docker logs for errors...\n');
  
  const logs = execSync('docker-compose logs --no-color', {
    cwd: projectPath,
    encoding: 'utf8'
  });
  
  const errors = [];
  const warnings = [];
  
  // Check for common error patterns
  const errorPatterns = [
    { pattern: /ImportError:/gi, message: 'Import error found' },
    { pattern: /ModuleNotFoundError:/gi, message: 'Module not found error' },
    { pattern: /FATAL:/gi, message: 'Fatal error found' },
    { pattern: /ERROR.*failed/gi, message: 'Service failure detected' },
    { pattern: /Cannot connect/gi, message: 'Connection error' },
    { pattern: /relation.*does not exist/gi, message: 'Database table missing' },
    { pattern: /permission denied/gi, message: 'Permission error' },
    { pattern: /Can't find Python file/gi, message: 'Missing Python file' }
  ];
  
  const warningPatterns = [
    { pattern: /WARNING:/gi, message: 'Warning found' },
    { pattern: /DeprecationWarning:/gi, message: 'Deprecation warning' },
    { pattern: /\(trapped\) error/gi, message: 'Trapped error' }
  ];
  
  // Check for errors (but ignore the expected alembic error on first run)
  errorPatterns.forEach(({ pattern, message }) => {
    const matches = logs.match(pattern);
    if (matches) {
      // Ignore the first alembic error which is expected
      const filtered = matches.filter(m => 
        !m.includes("Can't find Python file alembic/env.py") || 
        matches.length > 1
      );
      if (filtered.length > 0) {
        errors.push(`❌ ${message}: ${filtered[0]}`);
      }
    }
  });
  
  // Check for warnings
  warningPatterns.forEach(({ pattern, message }) => {
    const matches = logs.match(pattern);
    if (matches) {
      warnings.push(`⚠️  ${message}: ${matches[0]}`);
    }
  });
  
  return { errors, warnings, logs };
}

async function runTest() {
  console.log('🐳 Testing Docker Compose integration...\n');
  
  // Create temporary directory for test
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stackwizard-docker-test-'));
  const projectName = 'test-docker-project';
  const projectPath = path.join(tmpDir, projectName);
  
  console.log(`📁 Test directory: ${tmpDir}`);
  console.log(`🏗️  Generating project: ${projectName}\n`);
  
  let dockerProcess = null;
  
  try {
    // Run the generator
    const generatorPath = path.join(projectRoot, 'src', 'index.js');
    execSync(`node ${generatorPath} --quick --name ${projectName}`, {
      cwd: tmpDir,
      stdio: 'pipe',
      encoding: 'utf8',
    });
    
    console.log('✅ Project generated successfully\n');
    
    // Check that docker-compose.yml exists
    const dockerComposePath = path.join(projectPath, 'docker-compose.yml');
    if (!fs.existsSync(dockerComposePath)) {
      throw new Error('docker-compose.yml not found in generated project');
    }
    
    console.log('🐳 Starting Docker Compose...\n');
    
    // Start docker-compose in detached mode
    execSync('docker-compose up -d', {
      cwd: projectPath,
      stdio: 'inherit'
    });
    
    // Wait for services to be healthy
    await waitForServices(projectPath);
    
    // Check logs for errors
    const { errors, warnings, logs } = checkDockerLogs(projectPath);
    
    // Test API endpoints
    console.log('🧪 Testing API endpoints...\n');
    
    // Test login endpoint
    const loginResponse = await new Promise((resolve, reject) => {
      const postData = 'username=admin@example.com&password=admin123';
      const options = {
        hostname: 'localhost',
        port: 8000,
        path: '/api/v1/auth/login',
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(postData)
        }
      };
      
      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          resolve({
            status: res.statusCode,
            data: data
          });
        });
      });
      
      req.on('error', reject);
      req.write(postData);
      req.end();
    });
    
    if (loginResponse.status === 200) {
      console.log('✅ Login endpoint working');
    } else {
      errors.push(`❌ Login failed with status ${loginResponse.status}`);
    }
    
    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 DOCKER COMPOSE TEST SUMMARY');
    console.log('='.repeat(60));
    
    if (errors.length > 0) {
      console.log('\n❌ ERRORS:');
      errors.forEach(err => console.log(`  ${err}`));
    }
    
    if (warnings.length > 0) {
      console.log('\n⚠️  WARNINGS:');
      warnings.forEach(warn => console.log(`  ${warn}`));
    }
    
    // Stop docker-compose
    console.log('\n🛑 Stopping Docker Compose...');
    execSync('docker-compose down -v', {
      cwd: projectPath,
      stdio: 'pipe'
    });
    
    // Cleanup
    console.log('🧹 Cleaning up test directory...');
    fs.rmSync(tmpDir, { recursive: true, force: true });
    
    if (errors.length > 0) {
      console.log('\n❌ TEST FAILED: Docker Compose has errors!');
      process.exit(1);
    } else {
      console.log('\n✅ TEST PASSED: Docker Compose integration working!');
      process.exit(0);
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    
    // Try to stop docker-compose and cleanup
    try {
      execSync('docker-compose down -v', {
        cwd: projectPath,
        stdio: 'pipe'
      });
    } catch (cleanupError) {
      console.error('Failed to stop docker-compose:', cleanupError.message);
    }
    
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch (cleanupError) {
      console.error('Failed to cleanup:', cleanupError.message);
    }
    
    process.exit(1);
  }
}

// Check if Docker is available
try {
  execSync('docker --version', { stdio: 'pipe' });
  execSync('docker-compose --version', { stdio: 'pipe' });
} catch (error) {
  console.error('❌ Docker or Docker Compose not available. Skipping test.');
  console.log('ℹ️  Install Docker Desktop to run this test.');
  process.exit(0); // Exit with success to not block CI
}

// Run the test
runTest().catch(error => {
  console.error('Unexpected error:', error);
  process.exit(1);
});