#!/usr/bin/env node

/**
 * API Endpoint Mapping Verification Test
 * Checks that all frontend API calls have corresponding backend endpoints
 */

import fs from 'fs-extra';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import { dirname, join, relative } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

// Frontend API calls to verify
const FRONTEND_ENDPOINTS = [
  // Auth endpoints
  { path: '/api/v1/auth/login', method: 'POST', source: 'AuthContext' },
  { path: '/api/v1/auth/register', method: 'POST', source: 'AuthContext' },
  { path: '/api/v1/auth/logout', method: 'POST', source: 'AuthContext' },
  { path: '/api/v1/auth/refresh', method: 'POST', source: 'auth service' },
  
  // User endpoints
  { path: '/api/v1/users/me', method: 'GET', source: 'auth service' },
  { path: '/api/v1/users/', method: 'GET', source: 'api service' },
  { path: '/api/v1/users/{id}', method: 'GET', source: 'api service' },
  { path: '/api/v1/users/{id}', method: 'PUT', source: 'api service' },
  { path: '/api/v1/users/{id}', method: 'DELETE', source: 'api service' },
  
  // Admin endpoints
  { path: '/api/v1/admin/stats', method: 'GET', source: 'AdminDashboard' },
  { path: '/api/v1/admin/recent-registrations', method: 'GET', source: 'AdminDashboard' },
  { path: '/api/v1/admin/audit-log', method: 'GET', source: 'AdminDashboard' },
  
  // Items endpoints
  { path: '/api/v1/items/', method: 'GET', source: 'api service' },
  { path: '/api/v1/items/{id}', method: 'GET', source: 'api service' },
  { path: '/api/v1/items/', method: 'POST', source: 'api service' },
  { path: '/api/v1/items/{id}', method: 'PUT', source: 'api service' },
  { path: '/api/v1/items/{id}', method: 'DELETE', source: 'api service' },
  
  // Health endpoints
  { path: '/health', method: 'GET', source: 'health check' },
  { path: '/health/db', method: 'GET', source: 'health check' },
  { path: '/api/health', method: 'GET', source: 'health check' },
  { path: '/api/health/db', method: 'GET', source: 'health check' }
];

/**
 * Extract API calls from frontend source
 */
function extractFrontendAPICalls(template) {
  console.log(info(`\n📂 Analyzing ${template} template...`));
  
  const templatePath = join(__dirname, '..', 'templates', template, 'src');
  const apiCalls = [];
  
  // Patterns to search for
  const patterns = [
    /api\.(get|post|put|delete|patch)\(['"`]([^'"`]+)['"`]/g,
    /axios\.(get|post|put|delete|patch)\(['"`]([^'"`]+)['"`]/g,
    /fetch\(['"`]([^'"`]+)['"`]/g
  ];
  
  // Recursively search all JS/JSX files
  function searchFiles(dir) {
    const files = fs.readdirSync(dir);
    
    for (const file of files) {
      const filePath = join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
        searchFiles(filePath);
      } else if (file.endsWith('.js') || file.endsWith('.jsx')) {
        const content = fs.readFileSync(filePath, 'utf-8');
        
        for (const pattern of patterns) {
          let match;
          while ((match = pattern.exec(content)) !== null) {
            const method = match[1] || 'GET';
            const endpoint = match[2] || match[1];
            
            if (endpoint && !endpoint.startsWith('http') && !endpoint.startsWith('$')) {
              apiCalls.push({
                method: method.toUpperCase(),
                endpoint: endpoint,
                file: relative(templatePath, filePath)
              });
            }
          }
        }
      }
    }
  }
  
  searchFiles(templatePath);
  return apiCalls;
}

/**
 * Extract backend endpoints
 */
function extractBackendEndpoints() {
  console.log(info('\n📂 Analyzing backend endpoints...'));
  
  const backendPath = join(__dirname, '..', 'templates', 'common', 'backend');
  const endpoints = [];
  
  // Search for router definitions
  const routerPattern = /@(app|router)\.(get|post|put|delete|patch)\(['"`]([^'"`]+)['"`]/g;
  
  function searchPythonFiles(dir) {
    const files = fs.readdirSync(dir);
    
    for (const file of files) {
      const filePath = join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory() && !file.startsWith('.') && file !== '__pycache__') {
        searchPythonFiles(filePath);
      } else if (file.endsWith('.py')) {
        const content = fs.readFileSync(filePath, 'utf-8');
        
        // Extract router prefix if exists
        const prefixMatch = content.match(/router\s*=\s*APIRouter\([^)]*prefix\s*=\s*['"`]([^'"`]+)['"`]/);
        const prefix = prefixMatch ? prefixMatch[1] : '';
        
        let match;
        const localRouterPattern = /@(app|router)\.(get|post|put|delete|patch)\(['"`]([^'"`]+)['"`]/g;
        while ((match = localRouterPattern.exec(content)) !== null) {
          const method = match[2].toUpperCase();
          const path = match[3];
          
          // Combine with prefix if it's a router
          const fullPath = match[1] === 'router' && prefix ? prefix + path : path;
          
          endpoints.push({
            method: method,
            path: fullPath,
            file: relative(backendPath, filePath)
          });
        }
      }
    }
  }
  
  searchPythonFiles(backendPath);
  
  // Add API v1 prefix to router endpoints
  const apiV1Endpoints = endpoints.map(ep => {
    if (ep.file.includes('api/v1') && !ep.path.startsWith('/api/v1')) {
      return { ...ep, path: '/api/v1' + ep.path };
    }
    return ep;
  });
  
  return apiV1Endpoints;
}

/**
 * Compare frontend and backend endpoints
 */
function compareEndpoints() {
  console.log(info('\n🔍 Verifying endpoint mappings...'));
  console.log('─'.repeat(60));
  
  // Extract endpoints from both templates
  const muiCalls = extractFrontendAPICalls('frontend-mui');
  const tailwindCalls = extractFrontendAPICalls('frontend-tailwind');
  const backendEndpoints = extractBackendEndpoints();
  
  // Combine frontend calls
  const allFrontendCalls = [...muiCalls, ...tailwindCalls];
  
  // Normalize and deduplicate
  const uniqueFrontendEndpoints = Array.from(new Set(
    allFrontendCalls.map(call => `${call.method} ${call.endpoint}`)
  )).map(str => {
    const [method, ...pathParts] = str.split(' ');
    return { method, path: pathParts.join(' ') };
  });
  
  // Check each expected endpoint
  const results = [];
  let hasErrors = false;
  
  console.log(chalk.bold('\n📋 Expected Frontend Endpoints:'));
  console.log('─'.repeat(60));
  
  for (const expected of FRONTEND_ENDPOINTS) {
    // Check if backend has this endpoint
    const backendMatch = backendEndpoints.find(be => {
      const pathMatch = be.path === expected.path || 
                       be.path.replace(/{[^}]+}/g, '{id}') === expected.path.replace(/{[^}]+}/g, '{id}');
      return pathMatch && be.method === expected.method;
    });
    
    if (backendMatch) {
      console.log(success(`✅ ${expected.method} ${expected.path} - Found in ${backendMatch.file}`));
      results.push({ ...expected, status: 'found', backend: backendMatch.file });
    } else {
      console.log(error(`❌ ${expected.method} ${expected.path} - NOT FOUND in backend`));
      results.push({ ...expected, status: 'missing' });
      hasErrors = true;
    }
  }
  
  // Find unexpected frontend calls
  console.log(chalk.bold('\n🔎 Additional Frontend API Calls Found:'));
  console.log('─'.repeat(60));
  
  for (const call of uniqueFrontendEndpoints) {
    const isExpected = FRONTEND_ENDPOINTS.some(
      e => e.path === call.path && e.method === call.method
    );
    
    if (!isExpected && !call.path.includes('localhost') && !call.path.includes('ENV')) {
      console.log(warning(`⚠️  ${call.method} ${call.path} - Unexpected API call`));
      
      // Check if backend has it
      const backendMatch = backendEndpoints.find(be => {
        const pathMatch = be.path === call.path || 
                         be.path.replace(/{[^}]+}/g, '*') === call.path.replace(/\/\d+/g, '/*');
        return pathMatch && be.method === call.method;
      });
      
      if (!backendMatch) {
        console.log(error(`   └─ NOT FOUND in backend!`));
        hasErrors = true;
      }
    }
  }
  
  // List all backend endpoints for reference
  console.log(chalk.bold('\n📚 Available Backend Endpoints:'));
  console.log('─'.repeat(60));
  
  const groupedEndpoints = {};
  for (const ep of backendEndpoints) {
    const group = ep.path.split('/')[2] || 'root';
    if (!groupedEndpoints[group]) {
      groupedEndpoints[group] = [];
    }
    groupedEndpoints[group].push(ep);
  }
  
  for (const [group, endpoints] of Object.entries(groupedEndpoints)) {
    console.log(chalk.cyan(`\n${group}:`));
    for (const ep of endpoints) {
      console.log(`  ${ep.method.padEnd(6)} ${ep.path}`);
    }
  }
  
  return { results, hasErrors };
}

/**
 * Main test function
 */
function runTest() {
  console.log(chalk.bold.cyan('\n🔗 API Endpoint Mapping Verification\n'));
  console.log('═'.repeat(60));
  
  try {
    const { hasErrors } = compareEndpoints();
    
    // Final report
    console.log('\n' + chalk.bold('Verification Summary:'));
    console.log('═'.repeat(60));
    
    if (!hasErrors) {
      console.log(success('✅ All frontend API calls have matching backend endpoints!'));
      console.log(success('The application should work correctly.'));
      process.exit(0);
    } else {
      console.log(error('❌ Some frontend API calls are missing backend endpoints!'));
      console.log(error('This will cause 404 errors in the application.'));
      console.log(warning('\n⚠️  To fix: Ensure all frontend API paths match backend routes'));
      process.exit(1);
    }
    
  } catch (err) {
    console.log(error('\n❌ Verification failed:'), err.message);
    console.log(err.stack);
    process.exit(1);
  }
}

// Run the test
runTest();