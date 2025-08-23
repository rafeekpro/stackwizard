#!/usr/bin/env node

/**
 * Test to verify that all critical template files are included in the npm package
 * This test prevents the issue where .npmignore excludes essential files
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.join(__dirname, '..');

// Critical files that MUST be included in the npm package
const CRITICAL_FILES = [
  // Essential template files
  'templates/common/.env.example',
  'templates/common/docker-compose.yml',
  'templates/common/PROJECT_README.md',
  
  // Backend directory and key files
  'templates/common/backend/Dockerfile',
  'templates/common/backend/requirements.txt',
  'templates/common/backend/app/main.py',
  'templates/common/backend/alembic.ini',
  
  // Database files
  'templates/common/database/init.sql',
  
  // Frontend templates
  'templates/frontend-mui/package.json',
  'templates/frontend-mui/src/App.js',
  'templates/frontend-mui/public/index.html',
  'templates/frontend-tailwind/package.json',
  'templates/frontend-tailwind/src/App.js',
  'templates/frontend-tailwind/public/index.html',
  
  // GitHub Actions (optional but good to have)
  'templates/common/.github/workflows/test-backend-integration.yml',
  
  // Main generator file
  'src/index.js',
];

// Patterns that should NOT be included (but templates/* are exceptions)
const EXCLUDED_PATTERNS = [
  { pattern: '.env.local', excludeTemplates: false },
  { pattern: '.env.development', excludeTemplates: false },
  { pattern: '.env.production', excludeTemplates: false },
  { pattern: 'node_modules', excludeTemplates: false },
  { pattern: 'test/', excludeTemplates: false },
  { pattern: 'coverage/', excludeTemplates: false },
  { pattern: '.git/', excludeTemplates: true }, // .git directory itself, but not .github or .gitignore in templates
];

function runTest() {
  console.log('🔍 Testing npm package file inclusion...\n');
  
  let hasErrors = false;
  const errors = [];
  const warnings = [];
  
  try {
    // Get list of files that will be included in npm package
    const npmPackOutput = execSync('npm pack --dry-run --json', {
      cwd: projectRoot,
      encoding: 'utf8',
    });
    
    // Parse the JSON output
    const packData = JSON.parse(npmPackOutput);
    const includedFiles = packData[0].files.map(f => f.path);
    
    console.log(`📦 Package will include ${includedFiles.length} files\n`);
    
    // Check that all critical files are included
    console.log('Checking critical files...');
    for (const file of CRITICAL_FILES) {
      if (!includedFiles.includes(file)) {
        hasErrors = true;
        errors.push(`❌ MISSING: ${file}`);
      } else {
        console.log(`✅ Found: ${file}`);
      }
    }
    
    // Check that excluded patterns are NOT included (with template exceptions)
    console.log('\nChecking excluded patterns...');
    for (const exclusion of EXCLUDED_PATTERNS) {
      const { pattern, excludeTemplates } = exclusion;
      const matchingFiles = includedFiles.filter(f => {
        // Check if file matches the pattern
        if (!f.includes(pattern)) return false;
        // If it's in templates and we don't exclude templates, it's OK
        if (f.startsWith('templates/') && !excludeTemplates) return false;
        // Special case: .github is OK in templates, .git/ is not
        if (pattern === '.git/' && f.includes('.github')) return false;
        return true;
      });
      
      if (matchingFiles.length > 0) {
        hasErrors = true;
        matchingFiles.forEach(f => {
          errors.push(`❌ SHOULD NOT INCLUDE: ${f} (matches pattern: ${pattern})`);
        });
      } else {
        console.log(`✅ Correctly handled pattern: ${pattern}`);
      }
    }
    
    // Check for .env.example specifically (it should be included)
    const envExampleFiles = includedFiles.filter(f => f.includes('.env.example'));
    if (envExampleFiles.length === 0) {
      hasErrors = true;
      errors.push('❌ CRITICAL: No .env.example files found in package!');
    } else {
      console.log(`✅ Found ${envExampleFiles.length} .env.example file(s)`);
    }
    
    // Check that backend directory is included
    const backendFiles = includedFiles.filter(f => f.includes('templates/common/backend/'));
    if (backendFiles.length < 10) {
      hasErrors = true;
      errors.push(`❌ CRITICAL: Only ${backendFiles.length} backend files found (expected many more)`);
    } else {
      console.log(`✅ Found ${backendFiles.length} backend files`);
    }
    
    // Check file sizes to ensure files aren't empty
    console.log('\nChecking file sizes...');
    const packageSize = packData[0].size;
    const unpackedSize = packData[0].unpackedSize;
    
    if (packageSize < 100000) { // Less than 100KB is suspicious
      warnings.push(`⚠️  Package size is very small: ${(packageSize / 1024).toFixed(2)} KB`);
    } else {
      console.log(`✅ Package size: ${(packageSize / 1024).toFixed(2)} KB`);
    }
    
    if (unpackedSize < 500000) { // Less than 500KB unpacked is suspicious
      warnings.push(`⚠️  Unpacked size is very small: ${(unpackedSize / 1024).toFixed(2)} KB`);
    } else {
      console.log(`✅ Unpacked size: ${(unpackedSize / 1024 / 1024).toFixed(2)} MB`);
    }
    
    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));
    
    if (errors.length > 0) {
      console.log('\n❌ ERRORS:');
      errors.forEach(err => console.log(`  ${err}`));
    }
    
    if (warnings.length > 0) {
      console.log('\n⚠️  WARNINGS:');
      warnings.forEach(warn => console.log(`  ${warn}`));
    }
    
    if (hasErrors) {
      console.log('\n❌ TEST FAILED: Critical files are missing from npm package!');
      console.log('Check your .npmignore file and ensure it has proper exclusions.');
      process.exit(1);
    } else {
      console.log('\n✅ TEST PASSED: All critical files are included in npm package!');
      process.exit(0);
    }
    
  } catch (error) {
    console.error('❌ Error running test:', error.message);
    if (error.stderr) {
      console.error('stderr:', error.stderr.toString());
    }
    process.exit(1);
  }
}

// Run the test
runTest();