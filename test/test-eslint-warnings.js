#!/usr/bin/env node

/**
 * Test to detect ESLint warnings in generated projects
 * This ensures that generated code is clean and follows best practices
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_PROJECT_NAME = 'test-eslint-project';
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
}

async function generateProject(uiLibrary = 'mui') {
  const spinner = ora('Generating test project...').start();
  
  try {
    // Clean up any existing test project
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

async function runESLintCheck(projectPath, projectType) {
  const spinner = ora(`Running ESLint check for ${projectType}...`).start();
  
  try {
    const frontendPath = path.join(projectPath, 'frontend');
    
    // Check if frontend directory exists
    if (!await fs.pathExists(frontendPath)) {
      spinner.fail(`Frontend directory not found: ${frontendPath}`);
      return { success: false, warnings: [], errors: [] };
    }
    
    // Install dependencies first (needed for ESLint to work properly)
    spinner.text = 'Installing frontend dependencies...';
    await execAsync('npm install --silent', { cwd: frontendPath });
    
    // Run build which includes ESLint check
    spinner.text = `Running build with ESLint check for ${projectType}...`;
    const buildResult = await execAsync('CI=true npm run build 2>&1', { 
      cwd: frontendPath,
      maxBuffer: 1024 * 1024 * 10, // 10MB buffer for large outputs
      env: { ...process.env, CI: 'true' }
    }).catch(e => ({ 
      stdout: e.stdout || '', 
      stderr: e.stderr || '', 
      code: e.code,
      failed: true 
    }));
    
    const output = buildResult.stdout + buildResult.stderr;
    
    // Check for ESLint warnings/errors in build output
    const warningMatches = output.match(/Line \d+:\d+:/g) || [];
    const errorMatches = output.match(/Error:/g) || [];
    const compiledWithWarnings = output.includes('Compiled with warnings');
    const failedToCompile = output.includes('Failed to compile');
    
    let totalWarnings = 0;
    let totalErrors = 0;
    const issues = [];
    
    if (compiledWithWarnings || warningMatches.length > 0) {
      // Extract warning details from output
      const lines = output.split('\n');
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.includes('Line ') && line.includes(':')) {
          const match = line.match(/Line (\d+):(\d+):\s+(.+)/);
          if (match) {
            totalWarnings++;
            issues.push({
              severity: 'warning',
              message: line.trim()
            });
          }
        }
      }
    }
    
    if (failedToCompile || buildResult.failed) {
      totalErrors = 1;
      issues.push({
        severity: 'error',
        message: 'Build failed - check console output'
      });
    }
    
    if (totalErrors > 0) {
      spinner.fail(`${projectType}: ${totalErrors} errors found`);
    } else if (totalWarnings > 0) {
      spinner.warn(`${projectType}: ${totalWarnings} warnings found`);
    } else {
      spinner.succeed(`${projectType}: No ESLint issues found`);
    }
    
    return {
      success: totalErrors === 0 && totalWarnings === 0,
      warnings: totalWarnings,
      errors: totalErrors,
      issues
    };
  } catch (error) {
    spinner.fail(`Failed to run ESLint check: ${error.message}`);
    console.error(error);
    return { success: false, warnings: 0, errors: 0, issues: [] };
  }
}

function printIssues(issues) {
  if (issues.length === 0) return;
  
  console.log('\n' + chalk.bold('ESLint Issues Found:'));
  console.log('─'.repeat(80));
  
  for (const issue of issues) {
    const icon = issue.severity === 'error' ? '❌' : '⚠️';
    const color = issue.severity === 'error' ? error : warning;
    
    console.log(
      `${icon} ${color(issue.file)}:${issue.line}:${issue.column} - ${issue.message} (${chalk.gray(issue.rule)})`
    );
  }
  
  console.log('─'.repeat(80));
}

async function testUILibrary(uiLibrary) {
  console.log('\n' + info(`Testing ${uiLibrary.toUpperCase()} template...`));
  console.log('═'.repeat(80));
  
  // Generate project
  if (!await generateProject(uiLibrary)) {
    return false;
  }
  
  // Run ESLint check
  const result = await runESLintCheck(TEST_PROJECT_PATH, uiLibrary.toUpperCase());
  
  // Print issues if any
  if (result.issues && result.issues.length > 0) {
    printIssues(result.issues);
  }
  
  // Clean up
  await cleanup();
  
  return result.success;
}

async function main() {
  console.log(chalk.bold.cyan('\n🔍 ESLint Warning Detection Test\n'));
  console.log('This test ensures generated projects have no ESLint warnings or errors.\n');
  
  const results = {
    mui: false,
    tailwind: false
  };
  
  try {
    // Test MUI template
    results.mui = await testUILibrary('mui');
    
    // Test Tailwind template
    results.tailwind = await testUILibrary('tailwind');
    
    // Summary
    console.log('\n' + chalk.bold('Test Summary:'));
    console.log('═'.repeat(80));
    
    const muiStatus = results.mui ? success('✅ PASSED') : error('❌ FAILED');
    const tailwindStatus = results.tailwind ? success('✅ PASSED') : error('❌ FAILED');
    
    console.log(`Material UI Template: ${muiStatus}`);
    console.log(`Tailwind CSS Template: ${tailwindStatus}`);
    
    if (results.mui && results.tailwind) {
      console.log('\n' + success.bold('✨ All templates passed ESLint checks!'));
      process.exit(0);
    } else {
      console.log('\n' + error.bold('❌ Some templates have ESLint issues that need to be fixed.'));
      console.log(warning('\nTo fix these issues:'));
      console.log('1. Update the template files in templates/frontend-mui or templates/frontend-tailwind');
      console.log('2. Fix the reported ESLint warnings and errors');
      console.log('3. Run this test again to verify the fixes');
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