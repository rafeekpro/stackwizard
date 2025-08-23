#!/usr/bin/env node

/**
 * Integration test to verify that the generator creates all required files and folders
 * This test actually runs the generator and checks the output
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.join(__dirname, '..');

// Required directories that must exist in generated project
const REQUIRED_DIRECTORIES = [
  'backend',
  'backend/app',
  'backend/app/api',
  'backend/app/core',
  'backend/app/crud',
  'backend/app/db',
  'backend/app/models',
  'backend/app/schemas',
  'backend/app/services',
  'backend/alembic',
  'backend/tests',
  'database',
  'frontend',
  'frontend/src',
  'frontend/src/components',
  'frontend/src/contexts',
  'frontend/src/pages',
  'frontend/src/services',
  'frontend/public',
  'uploads',
  '.github',
  '.github/workflows',
];

// Required files that must exist in generated project
const REQUIRED_FILES = [
  '.env',
  '.env.example',
  'docker-compose.yml',
  'README.md',
  '.gitignore',
  'backend/requirements.txt',
  'backend/Dockerfile',
  'backend/app/main.py',
  'backend/alembic.ini',
  'database/init.sql',
  'frontend/package.json',
  'frontend/src/App.js',
  'frontend/public/index.html',
];

function runTest() {
  console.log('🧪 Testing project generation structure...\n');
  
  // Create temporary directory for test
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stackwizard-test-'));
  const projectName = 'test-structure-project';
  const projectPath = path.join(tmpDir, projectName);
  
  console.log(`📁 Test directory: ${tmpDir}`);
  console.log(`🏗️  Generating project: ${projectName}\n`);
  
  let hasErrors = false;
  const errors = [];
  
  try {
    // Run the generator with quick mode to use defaults
    const generatorPath = path.join(projectRoot, 'src', 'index.js');
    execSync(`node ${generatorPath} --quick --name ${projectName}`, {
      cwd: tmpDir,
      stdio: 'pipe', // Suppress output
      encoding: 'utf8',
    });
    
    console.log('✅ Project generated successfully\n');
    
    // Check that project directory was created
    if (!fs.existsSync(projectPath)) {
      console.error(`❌ Project directory not created at ${projectPath}`);
      process.exit(1);
    }
    
    // Check required directories
    console.log('Checking required directories...');
    for (const dir of REQUIRED_DIRECTORIES) {
      const dirPath = path.join(projectPath, dir);
      if (!fs.existsSync(dirPath)) {
        hasErrors = true;
        errors.push(`❌ Missing directory: ${dir}`);
      } else if (!fs.statSync(dirPath).isDirectory()) {
        hasErrors = true;
        errors.push(`❌ Not a directory: ${dir}`);
      } else {
        console.log(`✅ Found directory: ${dir}`);
      }
    }
    
    // Check required files
    console.log('\nChecking required files...');
    for (const file of REQUIRED_FILES) {
      const filePath = path.join(projectPath, file);
      if (!fs.existsSync(filePath)) {
        hasErrors = true;
        errors.push(`❌ Missing file: ${file}`);
      } else if (!fs.statSync(filePath).isFile()) {
        hasErrors = true;
        errors.push(`❌ Not a file: ${file}`);
      } else {
        const size = fs.statSync(filePath).size;
        if (size === 0) {
          errors.push(`⚠️  File is empty: ${file}`);
        } else {
          console.log(`✅ Found file: ${file} (${size} bytes)`);
        }
      }
    }
    
    // Additional checks for critical file contents
    console.log('\nChecking file contents...');
    
    // Check that .env.example has placeholders replaced
    const envExamplePath = path.join(projectPath, '.env.example');
    const envContent = fs.readFileSync(envExamplePath, 'utf8');
    if (envContent.includes('{{PROJECT_NAME}}')) {
      hasErrors = true;
      errors.push('❌ .env.example still contains unreplaced placeholders');
    } else {
      console.log('✅ .env.example placeholders replaced correctly');
    }
    
    // Check docker-compose.yml
    const dockerComposePath = path.join(projectPath, 'docker-compose.yml');
    const dockerContent = fs.readFileSync(dockerComposePath, 'utf8');
    if (dockerContent.includes('{{')) {
      hasErrors = true;
      errors.push('❌ docker-compose.yml still contains unreplaced placeholders');
    } else {
      console.log('✅ docker-compose.yml placeholders replaced correctly');
    }
    
    // Check that both frontend variants work
    const packageJsonPath = path.join(projectPath, 'frontend', 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      if (packageJson.name === projectName) {
        console.log('✅ Frontend package.json configured correctly');
      } else {
        errors.push('⚠️  Frontend package.json name not updated');
      }
    }
    
    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));
    
    if (errors.length > 0) {
      console.log('\n Issues found:');
      errors.forEach(err => console.log(`  ${err}`));
    }
    
    // Cleanup
    console.log(`\n🧹 Cleaning up test directory...`);
    fs.rmSync(tmpDir, { recursive: true, force: true });
    
    if (hasErrors) {
      console.log('\n❌ TEST FAILED: Generated project is missing critical components!');
      process.exit(1);
    } else {
      console.log('\n✅ TEST PASSED: Generated project has correct structure!');
      process.exit(0);
    }
    
  } catch (error) {
    console.error('❌ Error during test:', error.message);
    
    // Cleanup on error
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch (cleanupError) {
      console.error('Failed to cleanup:', cleanupError.message);
    }
    
    process.exit(1);
  }
}

// Run the test
runTest();