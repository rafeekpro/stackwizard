#!/usr/bin/env node

/**
 * Test to verify timezone fixes in statistics and export endpoints
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testTimezoneEndpoints() {
  log('🧪 Testing Timezone Fixes', 'blue');
  log('=' . repeat(50), 'blue');
  
  const projectName = `test-timezone-${Date.now()}`;
  const projectDir = path.join(process.cwd(), projectName);
  
  try {
    // 1. Generate test project
    log('Generating test project...', 'yellow');
    const answers = [
      projectName,
      '', // Material UI (default)
      '', // db name
      '', // db user  
      '', // db password
      '', // db port
      '', // frontend port
      '', // backend port
    ];
    
    execSync(`echo "${answers.join('\\n')}" | node src/index.js`, {
      cwd: process.cwd(),
      encoding: 'utf8'
    });
    
    // 2. Start services
    log('Starting Docker services...', 'yellow');
    execSync('docker compose up -d', { cwd: projectDir });
    
    // 3. Wait for services
    log('Waiting for services to be ready...', 'yellow');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    // 4. Initialize database
    log('Initializing database...', 'yellow');
    execSync('docker compose exec backend python -m app.db.init_db', { cwd: projectDir });
    
    // 5. Test login
    log('Testing login...', 'blue');
    const loginResponse = execSync(`curl -s -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin@example.com&password=changeme123"`, { encoding: 'utf8' });
    
    const loginData = JSON.parse(loginResponse);
    const token = loginData.access_token;
    
    if (!token) {
      throw new Error('Failed to get auth token');
    }
    log('✅ Login successful', 'green');
    
    // 6. Test statistics endpoint
    log('Testing /api/v1/users/me/statistics...', 'blue');
    const statsResponse = execSync(`curl -s -X GET http://localhost:8000/api/v1/users/me/statistics \
      -H "Authorization: Bearer ${token}"`, { encoding: 'utf8' });
    
    const stats = JSON.parse(statsResponse);
    if (stats.account_age_days !== undefined && stats.total_items !== undefined) {
      log('✅ Statistics endpoint works with timezone fix!', 'green');
      log(`   Account age: ${stats.account_age_days} days`, 'green');
      log(`   Total items: ${stats.total_items}`, 'green');
    } else if (stats.detail) {
      throw new Error(`Statistics endpoint failed: ${stats.detail}`);
    }
    
    // 7. Test export endpoint
    log('Testing /api/v1/users/me/export...', 'blue');
    const exportResponse = execSync(`curl -s -X GET http://localhost:8000/api/v1/users/me/export \
      -H "Authorization: Bearer ${token}"`, { encoding: 'utf8' });
    
    const exportData = JSON.parse(exportResponse);
    if (exportData.export_date && exportData.user) {
      log('✅ Export endpoint works with timezone fix!', 'green');
      log(`   Export date: ${exportData.export_date}`, 'green');
      log(`   User email: ${exportData.user.email}`, 'green');
    } else if (exportData.detail) {
      throw new Error(`Export endpoint failed: ${exportData.detail}`);
    }
    
    log('\n' + '='.repeat(50), 'green');
    log('✅ ALL TIMEZONE TESTS PASSED!', 'green');
    log('='.repeat(50), 'green');
    
  } catch (error) {
    log('\n' + '='.repeat(50), 'red');
    log('❌ TIMEZONE TEST FAILED', 'red');
    log(error.message, 'red');
    log('='.repeat(50), 'red');
    process.exit(1);
  } finally {
    // Cleanup
    log('\nCleaning up...', 'yellow');
    try {
      execSync('docker compose down -v', { cwd: projectDir });
      fs.rmSync(projectDir, { recursive: true, force: true });
    } catch (e) {
      // Ignore cleanup errors
    }
  }
}

// Run test
testTimezoneEndpoints();