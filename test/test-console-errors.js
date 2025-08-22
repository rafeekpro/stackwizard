#!/usr/bin/env node

/**
 * Test to detect console errors in generated projects
 * This ensures that generated projects run without runtime errors
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_PROJECT_NAME = 'test-console-errors';
const TEST_PROJECT_PATH = path.join(process.cwd(), TEST_PROJECT_NAME);

// Colors for output
const error = chalk.red;
const success = chalk.green;
const warning = chalk.yellow;
const info = chalk.blue;

async function cleanup() {
  if (await fs.pathExists(TEST_PROJECT_PATH)) {
    await fs.remove(TEST_PROJECT_PATH);
  }
  
  // Stop any running Docker containers
  try {
    await execAsync(`cd ${TEST_PROJECT_PATH} && docker-compose down`, { 
      cwd: TEST_PROJECT_PATH 
    }).catch(() => {});
  } catch (e) {
    // Ignore errors during cleanup
  }
}

async function generateProject(uiLibrary = 'mui') {
  const spinner = ora('Generating test project...').start();
  
  try {
    await cleanup();
    
    // Generate project using stackwizard
    const command = `node ${path.join(__dirname, '..', 'src', 'index.js')} --quick --name ${TEST_PROJECT_NAME} --ui ${uiLibrary} --skip-git`;
    await execAsync(command, { 
      cwd: process.cwd(),
      env: { ...process.env, CI: 'true' }
    });
    
    spinner.succeed('Test project generated');
    return true;
  } catch (error) {
    spinner.fail('Failed to generate project');
    console.error(error);
    return false;
  }
}

async function startServices(projectPath) {
  const spinner = ora('Starting Docker services...').start();
  
  try {
    // Start Docker Compose services
    await execAsync('docker-compose up -d', { 
      cwd: projectPath,
      env: { ...process.env }
    });
    
    // Wait for services to be ready
    spinner.text = 'Waiting for services to be ready...';
    await new Promise(resolve => setTimeout(resolve, 15000)); // Wait 15 seconds
    
    spinner.succeed('Services started');
    return true;
  } catch (error) {
    spinner.fail('Failed to start services');
    console.error(error);
    return false;
  }
}

async function checkConsoleErrors(projectPath, uiType) {
  const spinner = ora(`Checking for console errors in ${uiType} template...`).start();
  
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Collect console messages
    const consoleMessages = [];
    const consoleErrors = [];
    const networkErrors = [];
    
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      
      // Skip React DevTools message and deprecation warnings
      if (text.includes('Download the React DevTools')) return;
      if (text.includes('deprecation') || text.includes('Future Flag Warning')) return;
      
      consoleMessages.push({ type, text });
      
      if (type === 'error') {
        consoleErrors.push(text);
      }
    });
    
    // Track network errors
    page.on('requestfailed', request => {
      const failure = request.failure();
      const url = request.url();
      
      // Ignore some expected failures
      if (url.includes('favicon.ico')) return;
      if (url.includes('chrome-extension://')) return;
      
      networkErrors.push({
        url,
        error: failure ? failure.errorText : 'Unknown error'
      });
    });
    
    // Track 404 responses
    page.on('response', response => {
      const status = response.status();
      const url = response.url();
      
      if (status === 404) {
        networkErrors.push({
          url,
          error: `404 Not Found`
        });
      }
    });
    
    // Navigate to the application
    spinner.text = 'Loading application...';
    try {
      await page.goto('http://localhost:3000', { 
        waitUntil: 'networkidle2',
        timeout: 30000 
      });
    } catch (navError) {
      spinner.fail(`Failed to load application: ${navError.message}`);
      await browser.close();
      return { success: false, errors: [navError.message], networkErrors: [] };
    }
    
    // Wait a bit for any async operations
    await page.waitForTimeout(3000);
    
    await browser.close();
    
    const hasErrors = consoleErrors.length > 0 || networkErrors.length > 0;
    
    if (hasErrors) {
      spinner.fail(`${uiType}: ${consoleErrors.length} console errors, ${networkErrors.length} network errors found`);
    } else {
      spinner.succeed(`${uiType}: No console or network errors found`);
    }
    
    return {
      success: !hasErrors,
      consoleErrors,
      networkErrors,
      totalMessages: consoleMessages.length
    };
    
  } catch (error) {
    spinner.fail(`Failed to check console errors: ${error.message}`);
    return { 
      success: false, 
      consoleErrors: [], 
      networkErrors: [],
      error: error.message 
    };
  }
}

function printErrors(result, templateName) {
  if (!result.success) {
    console.log('\n' + chalk.bold(`${templateName} Errors:`));
    console.log('─'.repeat(80));
    
    if (result.consoleErrors && result.consoleErrors.length > 0) {
      console.log(chalk.bold.red('\n❌ Console Errors:'));
      result.consoleErrors.forEach((err, i) => {
        console.log(`  ${i + 1}. ${error(err)}`);
      });
    }
    
    if (result.networkErrors && result.networkErrors.length > 0) {
      console.log(chalk.bold.red('\n❌ Network/404 Errors:'));
      result.networkErrors.forEach((err, i) => {
        console.log(`  ${i + 1}. ${error(err.url)}`);
        console.log(`     ${chalk.gray(err.error)}`);
      });
    }
    
    if (result.error) {
      console.log(chalk.bold.red('\n❌ Test Error:'));
      console.log(`  ${error(result.error)}`);
    }
    
    console.log('─'.repeat(80));
  }
}

async function testUILibrary(uiLibrary) {
  console.log('\n' + info(`Testing ${uiLibrary.toUpperCase()} template...`));
  console.log('═'.repeat(80));
  
  // Generate project
  if (!await generateProject(uiLibrary)) {
    return { success: false, error: 'Failed to generate project' };
  }
  
  // Start services
  if (!await startServices(TEST_PROJECT_PATH)) {
    await cleanup();
    return { success: false, error: 'Failed to start services' };
  }
  
  // Check for console errors
  const result = await checkConsoleErrors(TEST_PROJECT_PATH, uiLibrary.toUpperCase());
  
  // Clean up
  await cleanup();
  
  return result;
}

async function main() {
  console.log(chalk.bold.cyan('\n🔍 Console Error Detection Test\n'));
  console.log('This test ensures generated projects run without console errors.\n');
  
  // Check if Docker is running
  try {
    await execAsync('docker info');
  } catch (e) {
    console.error(error('❌ Docker is not running. Please start Docker and try again.'));
    process.exit(1);
  }
  
  // Check if puppeteer is installed
  try {
    await import('puppeteer');
  } catch (e) {
    console.log(warning('⚠️  Puppeteer not installed. Installing...'));
    await execAsync('npm install puppeteer');
  }
  
  const results = {
    mui: null,
    tailwind: null
  };
  
  try {
    // Test MUI template
    results.mui = await testUILibrary('mui');
    
    // Test Tailwind template  
    results.tailwind = await testUILibrary('tailwind');
    
    // Summary
    console.log('\n' + chalk.bold('Test Summary:'));
    console.log('═'.repeat(80));
    
    // MUI Results
    if (results.mui.success) {
      console.log(`Material UI Template: ${success('✅ PASSED - No errors')}`);
    } else {
      console.log(`Material UI Template: ${error('❌ FAILED')}`);
      printErrors(results.mui, 'Material UI');
    }
    
    // Tailwind Results
    if (results.tailwind.success) {
      console.log(`Tailwind CSS Template: ${success('✅ PASSED - No errors')}`);
    } else {
      console.log(`Tailwind CSS Template: ${error('❌ FAILED')}`);
      printErrors(results.tailwind, 'Tailwind CSS');
    }
    
    if (results.mui.success && results.tailwind.success) {
      console.log('\n' + success.bold('✨ All templates run without console errors!'));
      process.exit(0);
    } else {
      console.log('\n' + error.bold('❌ Some templates have runtime errors that need to be fixed.'));
      console.log(warning('\nTo fix these issues:'));
      console.log('1. Check API endpoint paths in frontend code');
      console.log('2. Ensure backend routes match frontend expectations');
      console.log('3. Fix any undefined variables or missing imports');
      console.log('4. Run this test again to verify the fixes');
      process.exit(1);
    }
  } catch (error) {
    console.error(error('Test failed with error:'), error);
    await cleanup();
    process.exit(1);
  }
}

// Run the test
main().catch(console.error);