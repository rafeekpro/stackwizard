#!/usr/bin/env node

/**
 * Test to verify Docker containers have all required npm dependencies
 * This test generates projects and verifies all npm packages are properly installed
 */

import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.dirname(__dirname);

const TEST_PROJECT_NAME = 'test-docker-deps';
const TEST_DIR = path.join(projectRoot, '..', '..', TEST_PROJECT_NAME);

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

async function cleanup() {
  if (fs.existsSync(TEST_DIR)) {
    log(`Cleaning up test directory: ${TEST_DIR}`, 'yellow');
    try {
      // Stop any running containers
      execSync(`cd ${TEST_DIR} && docker compose down -v 2>/dev/null || true`, { stdio: 'pipe' });
    } catch (e) {
      // Ignore errors during cleanup
    }
    await fs.remove(TEST_DIR);
  }
}

async function generateProject(uiLibrary) {
  log(`\n=== Testing ${uiLibrary.toUpperCase()} Template ===`, 'blue');
  
  // Clean up before generating
  await cleanup();
  
  log(`Generating project with ${uiLibrary}...`, 'blue');
  
  // Create input file with proper selections
  const inputFile = path.join(projectRoot, 'test-input.txt');
  let inputContent;
  
  if (uiLibrary === 'mui') {
    // For MUI: project name, Enter (select first option), db config, ports
    inputContent = `${TEST_PROJECT_NAME}\n\ntest_db\ntest_user\ntest_password\n8000\n3000\n`;
  } else {
    // For Tailwind: project name, Arrow Down + Enter, db config, ports
    inputContent = `${TEST_PROJECT_NAME}\n\x1B[B\ntest_db\ntest_user\ntest_password\n8000\n3000\n`;
  }
  
  fs.writeFileSync(inputFile, inputContent);
  
  try {
    // Generate project in parent of parent directory
    const parentDir = path.join(projectRoot, '..', '..');
    execSync(`cd ${parentDir} && cat ${inputFile} | node ${projectRoot}/src/index.js`, {
      stdio: 'pipe'
    });
  } catch (e) {
    // Some versions might exit with non-zero for pipe closure
    if (!fs.existsSync(TEST_DIR)) {
      console.error('Generation error:', e.message);
      throw new Error(`Project generation failed - directory not created: ${TEST_DIR}`);
    }
  } finally {
    // Clean up input file
    if (fs.existsSync(inputFile)) {
      fs.unlinkSync(inputFile);
    }
  }
  
  if (!fs.existsSync(TEST_DIR)) {
    throw new Error(`Project generation failed - directory not created: ${TEST_DIR}`);
  }
  
  log('Project generated successfully', 'green');
}

async function verifyDockerDependencies(uiLibrary) {
  log('\nBuilding Docker containers...', 'blue');
  
  try {
    // Build the frontend container
    execSync(`cd ${TEST_DIR} && docker compose build frontend`, {
      stdio: 'inherit'
    });
    
    log('Docker build successful', 'green');
    
    // Start the frontend container
    log('\nStarting frontend container...', 'blue');
    execSync(`cd ${TEST_DIR} && docker compose up -d frontend`, {
      stdio: 'inherit'
    });
    
    // Wait for container to start
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check if container is running
    const containerStatus = execSync(`cd ${TEST_DIR} && docker compose ps frontend --format json`, {
      encoding: 'utf8'
    });
    
    if (!containerStatus.includes('running')) {
      throw new Error('Frontend container is not running');
    }
    
    log('Frontend container started successfully', 'green');
    
    // Check container logs for dependency errors
    log('\nChecking for dependency errors...', 'blue');
    const logs = execSync(`cd ${TEST_DIR} && docker compose logs frontend 2>&1`, {
      encoding: 'utf8'
    });
    
    // Check for common dependency error patterns
    const errorPatterns = [
      /Module not found.*@mui\/material/i,
      /Module not found.*@mui\/icons-material/i,
      /Module not found.*@headlessui\/react/i,
      /Module not found.*@heroicons\/react/i,
      /Cannot find module/i,
      /Module build failed/i,
      /npm ERR!/i,
      /ERROR in \./i
    ];
    
    const foundErrors = [];
    for (const pattern of errorPatterns) {
      if (pattern.test(logs)) {
        const matches = logs.match(new RegExp(pattern.source, 'gim'));
        if (matches) {
          foundErrors.push(...matches);
        }
      }
    }
    
    if (foundErrors.length > 0) {
      log('\n❌ Dependency errors found:', 'red');
      foundErrors.forEach(error => log(`  - ${error}`, 'red'));
      
      // Print relevant log section
      log('\nRelevant logs:', 'yellow');
      const relevantLogs = logs.split('\n')
        .filter(line => errorPatterns.some(p => p.test(line)))
        .slice(0, 20)
        .join('\n');
      console.log(relevantLogs);
      
      throw new Error(`Found ${foundErrors.length} dependency errors in ${uiLibrary} template`);
    }
    
    log('✅ No dependency errors found', 'green');
    
    // Additional check: verify key dependencies are installed
    log('\nVerifying key dependencies are installed...', 'blue');
    
    const keyDependencies = uiLibrary === 'mui' 
      ? ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled']
      : ['@headlessui/react', '@heroicons/react', 'tailwindcss'];
    
    for (const dep of keyDependencies) {
      const checkCmd = `docker compose exec -T frontend sh -c "ls node_modules/${dep.replace('/', '/').replace('@', '')} 2>/dev/null || echo 'NOT_FOUND'"`;
      try {
        const result = execSync(`cd ${TEST_DIR} && ${checkCmd}`, {
          encoding: 'utf8',
          stdio: 'pipe'
        });
        
        if (result.includes('NOT_FOUND')) {
          throw new Error(`Dependency ${dep} is not installed in container`);
        }
        log(`  ✓ ${dep} is installed`, 'green');
      } catch (e) {
        log(`  ✗ ${dep} is NOT installed`, 'red');
        throw new Error(`Dependency ${dep} is not installed in container`);
      }
    }
    
    log(`\n✅ All key dependencies verified for ${uiLibrary} template`, 'green');
    
  } finally {
    // Clean up containers
    log('\nStopping containers...', 'yellow');
    execSync(`cd ${TEST_DIR} && docker compose down -v`, {
      stdio: 'pipe'
    });
  }
}

async function runTests() {
  log('=== Docker Dependencies Test ===', 'blue');
  log('This test verifies that all npm dependencies are properly installed in Docker containers', 'blue');
  
  try {
    // Test MUI template
    await generateProject('mui');
    await verifyDockerDependencies('mui');
    
    // Test Tailwind template
    await generateProject('tailwind');
    await verifyDockerDependencies('tailwind');
    
    log('\n✅ All Docker dependency tests passed!', 'green');
    process.exit(0);
  } catch (error) {
    log(`\n❌ Test failed: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  } finally {
    await cleanup();
  }
}

// Run tests
runTests().catch(error => {
  log(`\n❌ Unexpected error: ${error.message}`, 'red');
  console.error(error);
  cleanup().then(() => process.exit(1));
});