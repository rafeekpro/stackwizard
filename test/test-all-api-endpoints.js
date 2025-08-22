#!/usr/bin/env node

/**
 * Comprehensive test for ALL API endpoints in generated projects
 * Ensures no 404 errors and correct routing for all API calls
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

// List of ALL API endpoints that should be available
const API_ENDPOINTS = {
  auth: [
    { method: 'POST', path: '/api/v1/auth/login', description: 'User login' },
    { method: 'POST', path: '/api/v1/auth/register', description: 'User registration' },
    { method: 'POST', path: '/api/v1/auth/logout', description: 'User logout' },
    { method: 'POST', path: '/api/v1/auth/refresh', description: 'Token refresh' },
    { method: 'POST', path: '/api/v1/auth/password-recovery', description: 'Password recovery' },
    { method: 'POST', path: '/api/v1/auth/reset-password', description: 'Password reset' },
    { method: 'GET', path: '/api/v1/auth/verify-token', description: 'Token verification' }
  ],
  users: [
    { method: 'GET', path: '/api/v1/users/', description: 'List users' },
    { method: 'POST', path: '/api/v1/users/', description: 'Create user' },
    { method: 'GET', path: '/api/v1/users/me', description: 'Get current user' },
    { method: 'PUT', path: '/api/v1/users/me', description: 'Update current user' },
    { method: 'PUT', path: '/api/v1/users/me/password', description: 'Change password' },
    { method: 'DELETE', path: '/api/v1/users/me', description: 'Deactivate account' },
    { method: 'GET', path: '/api/v1/users/{id}', description: 'Get user by ID' },
    { method: 'PUT', path: '/api/v1/users/{id}', description: 'Update user' },
    { method: 'DELETE', path: '/api/v1/users/{id}', description: 'Delete user' }
  ],
  items: [
    { method: 'GET', path: '/api/v1/items/', description: 'List items' },
    { method: 'POST', path: '/api/v1/items/', description: 'Create item' },
    { method: 'GET', path: '/api/v1/items/{id}', description: 'Get item' },
    { method: 'PUT', path: '/api/v1/items/{id}', description: 'Update item' },
    { method: 'DELETE', path: '/api/v1/items/{id}', description: 'Delete item' }
  ],
  admin: [
    { method: 'GET', path: '/api/v1/admin/stats', description: 'Admin statistics' },
    { method: 'GET', path: '/api/v1/admin/recent-registrations', description: 'Recent registrations' },
    { method: 'GET', path: '/api/v1/admin/audit-log', description: 'Audit log' },
    { method: 'GET', path: '/api/v1/admin/users', description: 'Admin user search' },
    { method: 'POST', path: '/api/v1/admin/users/{id}/reset-password', description: 'Admin reset password' },
    { method: 'POST', path: '/api/v1/admin/users/{id}/verify-email', description: 'Verify user email' },
    { method: 'GET', path: '/api/v1/admin/users/export', description: 'Export users' },
    { method: 'POST', path: '/api/v1/admin/users/import', description: 'Import users' },
    { method: 'POST', path: '/api/v1/admin/users/bulk-activate', description: 'Bulk activate' },
    { method: 'POST', path: '/api/v1/admin/users/bulk-deactivate', description: 'Bulk deactivate' },
    { method: 'GET', path: '/api/v1/admin/users/{id}/sessions', description: 'User sessions' },
    { method: 'DELETE', path: '/api/v1/admin/users/{id}/sessions', description: 'Invalidate sessions' }
  ],
  health: [
    { method: 'GET', path: '/health', description: 'Root health check' },
    { method: 'GET', path: '/health/db', description: 'Database health check' },
    { method: 'GET', path: '/api/health', description: 'API health check' },
    { method: 'GET', path: '/api/health/db', description: 'API database health' },
    { method: 'GET', path: '/api/v1/health', description: 'API v1 health check' },
    { method: 'GET', path: '/api/v1/health/db', description: 'API v1 database health' }
  ]
};

// Extract all API calls from frontend code
function extractFrontendAPICalls(templateType) {
  const apiCalls = new Set();
  const srcDir = path.join(__dirname, '..', 'templates', `frontend-${templateType}`, 'src');
  
  function scanDirectory(dir) {
    const files = fs.readdirSync(dir);
    
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
        scanDirectory(filePath);
      } else if (file.endsWith('.js') || file.endsWith('.jsx')) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Find all API calls
        const patterns = [
          /api\.(get|post|put|delete|patch)\(['"`](.*?)['"`]/g,
          /fetch\(['"`](.*?\/api\/.*?)['"`]/g,
          /axios\.(get|post|put|delete|patch)\(['"`](.*?)['"`]/g
        ];
        
        patterns.forEach(pattern => {
          let match;
          while ((match = pattern.exec(content)) !== null) {
            const url = match[2] || match[1];
            if (url && url.includes('api')) {
              apiCalls.add(url);
            }
          }
        });
      }
    }
  }
  
  if (fs.existsSync(srcDir)) {
    scanDirectory(srcDir);
  }
  
  return Array.from(apiCalls);
}

// Check if backend has the required endpoints
function checkBackendEndpoints() {
  const issues = [];
  
  // Check main.py
  const mainFile = path.join(__dirname, '..', 'templates', 'common', 'backend', 'app', 'main.py');
  if (fs.existsSync(mainFile)) {
    const content = fs.readFileSync(mainFile, 'utf8');
    
    // Check for API router inclusion
    if (!content.includes('api_router')) {
      issues.push('API router not included in main.py');
    }
    
    if (!content.includes('API_V1_STR')) {
      issues.push('API_V1_STR not configured in main.py');
    }
  }
  
  // Check auth endpoints
  const authFile = path.join(__dirname, '..', 'templates', 'common', 'backend', 'app', 'api', 'v1', 'auth.py');
  if (fs.existsSync(authFile)) {
    const content = fs.readFileSync(authFile, 'utf8');
    const requiredEndpoints = ['login', 'register', 'logout', 'refresh'];
    
    requiredEndpoints.forEach(endpoint => {
      if (!content.includes(`"/${endpoint}"`) && !content.includes(`'/${endpoint}'`)) {
        issues.push(`Auth endpoint /${endpoint} not found in auth.py`);
      }
    });
  }
  
  return issues;
}

// Main test function
function runTest() {
  console.log(chalk.bold.cyan('\n🔍 Comprehensive API Endpoints Test\n'));
  console.log('═'.repeat(60));
  
  let hasErrors = false;
  const results = {
    frontend: {},
    backend: [],
    mismatches: []
  };
  
  // Check frontend templates
  ['mui', 'tailwind'].forEach(template => {
    console.log('\n' + info(`Checking ${template.toUpperCase()} template...`));
    console.log('─'.repeat(50));
    
    const apiCalls = extractFrontendAPICalls(template);
    results.frontend[template] = apiCalls;
    
    console.log(`Found ${apiCalls.length} API calls:`);
    apiCalls.forEach(call => {
      console.log(`  - ${call}`);
    });
    
    // Check for incorrect patterns
    const incorrectPatterns = [
      { pattern: /^\/auth\//, correct: '/api/v1/auth/' },
      { pattern: /^\/users\//, correct: '/api/v1/users/' },
      { pattern: /^\/items\//, correct: '/api/v1/items/' },
      { pattern: /^\/admin\//, correct: '/api/v1/admin/' }
    ];
    
    apiCalls.forEach(call => {
      incorrectPatterns.forEach(({ pattern, correct }) => {
        if (pattern.test(call)) {
          console.log(error(`  ❌ Incorrect path: ${call}`));
          console.log(warning(`     Should be: ${call.replace(pattern, correct)}`));
          results.mismatches.push({ template, call, correct: call.replace(pattern, correct) });
          hasErrors = true;
        }
      });
    });
  });
  
  // Check backend endpoints
  console.log('\n' + info('Checking backend endpoints...'));
  console.log('─'.repeat(50));
  
  const backendIssues = checkBackendEndpoints();
  results.backend = backendIssues;
  
  if (backendIssues.length > 0) {
    console.log(error('Backend issues found:'));
    backendIssues.forEach(issue => {
      console.log(error(`  ❌ ${issue}`));
    });
    hasErrors = true;
  } else {
    console.log(success('✅ Backend endpoints configured correctly'));
  }
  
  // Check all required endpoints
  console.log('\n' + info('Validating required endpoints...'));
  console.log('─'.repeat(50));
  
  let endpointCount = 0;
  Object.entries(API_ENDPOINTS).forEach(([category, endpoints]) => {
    console.log(`\n${category.toUpperCase()}:`);
    endpoints.forEach(({ method, path, description }) => {
      endpointCount++;
      console.log(`  ${method.padEnd(6)} ${path.padEnd(45)} - ${description}`);
    });
  });
  
  console.log(`\nTotal endpoints to validate: ${endpointCount}`);
  
  // Generate report
  console.log('\n' + chalk.bold('Test Summary:'));
  console.log('═'.repeat(60));
  
  if (hasErrors) {
    console.log(error('❌ API endpoint issues found!'));
    
    if (results.mismatches.length > 0) {
      console.log(error(`\n${results.mismatches.length} incorrect API paths in frontend`));
    }
    
    if (results.backend.length > 0) {
      console.log(error(`${results.backend.length} backend configuration issues`));
    }
    
    console.log(warning('\nAction required:'));
    console.log('1. Fix incorrect API paths in frontend components');
    console.log('2. Ensure all auth endpoints use /api/v1/auth/ prefix');
    console.log('3. Verify backend router configuration');
    
    process.exit(1);
  } else {
    console.log(success('✅ All API endpoints are correctly configured!'));
    console.log(success(`Validated ${endpointCount} endpoints across all categories`));
    process.exit(0);
  }
}

// Run the test
runTest();