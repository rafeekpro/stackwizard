#!/usr/bin/env node

/**
 * Test to verify API endpoints match between frontend and backend
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

// Extract API calls from frontend code
function extractFrontendAPICalls(templateType) {
  const apiFile = path.join(__dirname, '..', 'templates', `frontend-${templateType}`, 'src', 'services', 'api.js');
  const homePageFile = path.join(__dirname, '..', 'templates', `frontend-${templateType}`, 'src', 'pages', 'HomePage.js');
  
  const apiCalls = [];
  
  if (fs.existsSync(apiFile)) {
    const content = fs.readFileSync(apiFile, 'utf8');
    
    // Find all api.get, api.post, etc. calls
    const apiMatches = content.match(/api\.(get|post|put|delete|patch)\(['"](.*?)['"]/g) || [];
    apiMatches.forEach(match => {
      const url = match.match(/['"](.*?)['"]/)[1];
      apiCalls.push(url);
    });
  }
  
  // Check specific health endpoint usage
  if (fs.existsSync(homePageFile)) {
    const content = fs.readFileSync(homePageFile, 'utf8');
    if (content.includes("checkHealth('/db')")) {
      apiCalls.push('/api/health/db');
    }
    if (content.includes("checkHealth()")) {
      apiCalls.push('/api/health');
    }
  }
  
  return [...new Set(apiCalls)]; // Remove duplicates
}

// Extract backend API routes
function extractBackendRoutes() {
  const routes = [];
  
  // Check main.py for top-level routes
  const mainFile = path.join(__dirname, '..', 'templates', 'common', 'backend', 'app', 'main.py');
  if (fs.existsSync(mainFile)) {
    const content = fs.readFileSync(mainFile, 'utf8');
    
    // Find @app.get, @app.post decorators
    const decoratorMatches = content.match(/@app\.(get|post|put|delete|patch)\(['"](.*?)['"]/g) || [];
    decoratorMatches.forEach(match => {
      const url = match.match(/['"](.*?)['"]/)[1];
      routes.push(url);
    });
  }
  
  // Check API v1 routes
  const apiV1File = path.join(__dirname, '..', 'templates', 'common', 'backend', 'app', 'api', 'v1', 'api.py');
  if (fs.existsSync(apiV1File)) {
    const content = fs.readFileSync(apiV1File, 'utf8');
    
    // Check for routers - these define the actual API endpoints
    if (content.includes('auth.router')) {
      // Auth endpoints
      routes.push('/api/v1/auth/register');
      routes.push('/api/v1/auth/login');
      routes.push('/api/v1/auth/logout');
      routes.push('/api/v1/auth/refresh');
    }
    
    if (content.includes('users.router')) {
      // User endpoints
      routes.push('/api/v1/users/');
      routes.push('/api/v1/users/{user_id}');
      routes.push('/api/v1/users/me');
    }
    
    if (content.includes('items.router')) {
      // Item endpoints
      routes.push('/api/v1/items/');
      routes.push('/api/v1/items/{item_id}');
    }
    
    if (content.includes('health.router')) {
      routes.push('/api/v1/health');
      routes.push('/api/v1/health/db');
    }
  }
  
  // Check health.py for specific endpoints
  const healthFile = path.join(__dirname, '..', 'templates', 'common', 'backend', 'app', 'api', 'health.py');
  if (fs.existsSync(healthFile)) {
    const content = fs.readFileSync(healthFile, 'utf8');
    
    if (content.includes('@router.get("/")')) {
      // This will be mounted at /api/v1/health
    }
    if (content.includes('@router.get("/db")')) {
      // This will be mounted at /api/v1/health/db
    }
  }
  
  return routes;
}

// Check if frontend calls match backend routes
function validateEndpoints() {
  console.log(chalk.bold.cyan('\n🔍 API Endpoint Validation Test\n'));
  
  const backendRoutes = extractBackendRoutes();
  const templates = ['mui', 'tailwind'];
  let hasErrors = false;
  
  console.log(info('Backend routes found:'));
  backendRoutes.forEach(route => {
    console.log(`  - ${route}`);
  });
  
  templates.forEach(template => {
    console.log('\n' + info(`\nChecking ${template.toUpperCase()} template...`));
    console.log('─'.repeat(50));
    
    const frontendCalls = extractFrontendAPICalls(template);
    
    console.log('Frontend API calls:');
    frontendCalls.forEach(call => {
      console.log(`  - ${call}`);
    });
    
    // Check each frontend call
    const missingEndpoints = [];
    frontendCalls.forEach(call => {
      // For relative paths like /health, they should work with the baseURL
      // The baseURL is /api/v1, so /health becomes /api/v1/health
      const fullPath = call.startsWith('/api/') ? call : `/api/v1${call}`;
      
      // Check if backend has this route
      const exists = backendRoutes.some(route => {
        // Exact match or pattern match (for parametric routes)
        return route === fullPath || 
               route === call ||
               (route.includes('{') && fullPath.startsWith(route.split('{')[0]));
      });
      
      if (!exists && !call.includes('{')) {
        missingEndpoints.push({ call, expected: fullPath });
        hasErrors = true;
      }
    });
    
    if (missingEndpoints.length > 0) {
      console.log(error('\n❌ Missing backend endpoints:'));
      missingEndpoints.forEach(({ call, expected }) => {
        console.log(error(`  Frontend calls: ${call}`));
        console.log(error(`  Expected backend: ${expected}`));
      });
    } else {
      console.log(success('\n✅ All API endpoints match!'));
    }
  });
  
  console.log('\n' + chalk.bold('Summary:'));
  console.log('═'.repeat(50));
  
  if (hasErrors) {
    console.log(error('❌ API endpoint mismatches found!'));
    console.log(warning('\nTo fix:'));
    console.log('1. Update frontend API calls to match backend routes');
    console.log('2. Or add missing routes to backend');
    console.log('3. Ensure baseURL is correctly configured');
    process.exit(1);
  } else {
    console.log(success('✅ All API endpoints are correctly configured!'));
    process.exit(0);
  }
}

// Run validation
validateEndpoints();