#!/usr/bin/env node

/**
 * Pre-Push Validator
 * COMPREHENSIVE validation before pushing to GitHub
 * This will CATCH ALL Docker/dependency issues
 */

import { execSync, exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PrePushValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.testDir = path.join('/tmp', `validator-test-${Date.now()}`);
  }

  log(message, type = 'info') {
    const colors = {
      error: chalk.red,
      success: chalk.green,
      warning: chalk.yellow,
      info: chalk.blue
    };
    console.log(colors[type](message));
  }

  async cleanup() {
    try {
      // Stop any running containers
      await execAsync(`cd ${this.testDir} && docker-compose down -v 2>/dev/null || true`).catch(() => {});
      // Remove test directory
      await fs.remove(this.testDir);
    } catch (e) {
      // Ignore cleanup errors
    }
  }

  async validateNpmPackage() {
    const spinner = ora('Validating npm package contents...').start();
    
    try {
      // Check what files will be included
      const output = execSync('npm pack --dry-run 2>&1', { encoding: 'utf8' });
      
      // Critical files that MUST be included
      const criticalFiles = [
        'templates/frontend-mui/package-lock.json',
        'templates/frontend-tailwind/package-lock.json',
        'templates/frontend-mui/Dockerfile',
        'templates/frontend-tailwind/Dockerfile',
        'templates/common/docker-compose.yml'
      ];
      
      for (const file of criticalFiles) {
        if (!output.includes(file)) {
          this.errors.push(`Missing critical file in npm package: ${file}`);
          spinner.fail(chalk.red(`Missing: ${file}`));
          return false;
        }
      }
      
      spinner.succeed(chalk.green('NPM package validation passed'));
      return true;
    } catch (error) {
      spinner.fail(chalk.red('NPM package validation failed'));
      this.errors.push(`NPM package error: ${error.message}`);
      return false;
    }
  }

  async generateTestProject(uiType = 'mui') {
    const spinner = ora(`Generating test project with ${uiType.toUpperCase()}...`).start();
    
    try {
      await fs.ensureDir(this.testDir);
      
      // Copy templates directly (bypass CLI issues)
      const templatesDir = path.join(__dirname, 'templates');
      const projectName = 'validator-test';
      
      // Copy backend
      await fs.copy(
        path.join(templatesDir, 'common', 'backend'),
        path.join(this.testDir, 'backend')
      );
      
      // Copy frontend
      const frontendTemplate = uiType === 'mui' ? 'frontend-mui' : 'frontend-tailwind';
      await fs.copy(
        path.join(templatesDir, frontendTemplate),
        path.join(this.testDir, 'frontend')
      );
      
      // Copy docker-compose
      await fs.copy(
        path.join(templatesDir, 'common', 'docker-compose.yml'),
        path.join(this.testDir, 'docker-compose.yml')
      );
      
      // Copy and update .env
      const envContent = await fs.readFile(
        path.join(templatesDir, 'common', '.env.example'),
        'utf8'
      );
      const updatedEnv = envContent
        .replace(/{{PROJECT_NAME}}/g, projectName)
        .replace(/{{DB_NAME}}/g, 'test_db')
        .replace(/{{DB_USER}}/g, 'test_user')
        .replace(/{{DB_PASSWORD}}/g, 'test_pass')
        .replace(/{{API_PORT}}/g, '8000')
        .replace(/{{FRONTEND_PORT}}/g, '3000');
      
      await fs.writeFile(path.join(this.testDir, '.env'), updatedEnv);
      
      spinner.succeed(chalk.green(`Test project generated with ${uiType.toUpperCase()}`));
      return true;
    } catch (error) {
      spinner.fail(chalk.red('Project generation failed'));
      this.errors.push(`Generation error: ${error.message}`);
      return false;
    }
  }

  async validateDockerBuild(service) {
    const spinner = ora(`Building Docker image for ${service}...`).start();
    
    try {
      const servicePath = path.join(this.testDir, service);
      
      // Build the Docker image
      const buildOutput = execSync(
        `docker build -t validator-${service} ${servicePath} 2>&1`,
        { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
      );
      
      // Check for npm errors
      if (buildOutput.includes("Module not found") || 
          buildOutput.includes("Can't resolve")) {
        const errorMatch = buildOutput.match(/Module not found.*|Can't resolve.*/g);
        if (errorMatch) {
          spinner.fail(chalk.red(`Dependencies missing in ${service}`));
          this.errors.push(`Docker build error in ${service}: ${errorMatch[0]}`);
          return false;
        }
      }
      
      spinner.succeed(chalk.green(`Docker build successful for ${service}`));
      return true;
    } catch (error) {
      spinner.fail(chalk.red(`Docker build failed for ${service}`));
      this.errors.push(`Docker build error: ${error.message}`);
      return false;
    }
  }

  async validateDockerRun(service) {
    const spinner = ora(`Running Docker container for ${service}...`).start();
    
    try {
      const containerName = `validator-${service}-container`;
      const port = service === 'frontend' ? '3002:3000' : '8002:8000';
      
      // Stop any existing container
      execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      
      // Run the container
      execSync(
        `docker run -d --name ${containerName} -p ${port} validator-${service}`,
        { stdio: 'pipe' }
      );
      
      // Wait for container to start
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      // Check logs for errors
      const logs = execSync(`docker logs ${containerName} 2>&1`, { encoding: 'utf8' });
      
      // Check for compilation/runtime errors
      const errorPatterns = [
        /Module not found.*@mui/i,
        /Module not found.*@headlessui/i,
        /Can't resolve '@mui\/material'/i,
        /Can't resolve '@heroicons/i,
        /ERROR in \./i,
        /Failed to compile/i,
        /npm ERR!/i
      ];
      
      for (const pattern of errorPatterns) {
        if (pattern.test(logs)) {
          const match = logs.match(pattern);
          spinner.fail(chalk.red(`Runtime error in ${service}: ${match[0]}`));
          this.errors.push(`Runtime error in ${service}: ${match[0]}`);
          
          // Clean up
          execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
          execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
          return false;
        }
      }
      
      // Check for successful compilation (frontend only)
      if (service === 'frontend' && !logs.includes('Compiled successfully')) {
        spinner.fail(chalk.red(`Frontend did not compile successfully`));
        this.errors.push('Frontend compilation failed');
        
        // Print relevant logs
        console.log(chalk.yellow('\nRelevant logs:'));
        console.log(logs.split('\n').slice(-30).join('\n'));
        
        // Clean up
        execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
        execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
        return false;
      }
      
      // Clean up
      execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      
      spinner.succeed(chalk.green(`Docker runtime validation passed for ${service}`));
      return true;
    } catch (error) {
      spinner.fail(chalk.red(`Docker runtime validation failed for ${service}`));
      this.errors.push(`Runtime error: ${error.message}`);
      return false;
    }
  }

  async validateDockerCompose() {
    const spinner = ora('Validating docker-compose configuration...').start();
    
    try {
      // Validate docker-compose syntax
      execSync(`cd ${this.testDir} && docker-compose config`, { stdio: 'pipe' });
      
      spinner.succeed(chalk.green('Docker-compose validation passed'));
      return true;
    } catch (error) {
      spinner.fail(chalk.red('Docker-compose validation failed'));
      this.errors.push(`Docker-compose error: ${error.message}`);
      return false;
    }
  }

  async runFullValidation() {
    console.log(chalk.bold.blue('\n🔍 Pre-Push Validator\n'));
    console.log(chalk.gray('This will ensure EVERYTHING works before pushing to GitHub\n'));
    
    let allPassed = true;
    
    // 1. Validate NPM package
    if (!await this.validateNpmPackage()) {
      allPassed = false;
    }
    
    // 2. Run REAL Docker Runtime Test (if available)
    console.log(chalk.blue('\n🐳 Running Docker Runtime Test...\n'));
    try {
      execSync('npm run test:docker-runtime', { stdio: 'inherit' });
      console.log(chalk.green('✅ Docker runtime test passed'));
    } catch (error) {
      console.log(chalk.red('❌ Docker runtime test failed'));
      console.log(chalk.yellow('This test would have caught the "@mui/material" error!'));
      allPassed = false;
      return false; // Stop immediately if Docker test fails
    }
    
    // 2. Test MUI template
    console.log(chalk.blue('\n📦 Testing Material UI Template\n'));
    if (await this.generateTestProject('mui')) {
      if (!await this.validateDockerBuild('frontend')) allPassed = false;
      if (!await this.validateDockerBuild('backend')) allPassed = false;
      if (!await this.validateDockerCompose()) allPassed = false;
      
      // Run containers and check for errors
      if (allPassed) {
        if (!await this.validateDockerRun('frontend')) allPassed = false;
      }
    } else {
      allPassed = false;
    }
    
    // Clean up
    await this.cleanup();
    
    // 3. Test Tailwind template
    console.log(chalk.blue('\n🎨 Testing Tailwind CSS Template\n'));
    if (await this.generateTestProject('tailwind')) {
      if (!await this.validateDockerBuild('frontend')) allPassed = false;
      if (!await this.validateDockerBuild('backend')) allPassed = false;
      if (!await this.validateDockerCompose()) allPassed = false;
      
      // Run containers and check for errors
      if (allPassed) {
        if (!await this.validateDockerRun('frontend')) allPassed = false;
      }
    } else {
      allPassed = false;
    }
    
    // Clean up
    await this.cleanup();
    
    // Print summary
    console.log(chalk.bold.blue('\n📊 Validation Summary\n'));
    console.log(chalk.gray('═'.repeat(50)));
    
    if (this.errors.length > 0) {
      console.log(chalk.red('\n❌ Errors found:\n'));
      this.errors.forEach(error => {
        console.log(chalk.red(`  • ${error}`));
      });
    }
    
    if (this.warnings.length > 0) {
      console.log(chalk.yellow('\n⚠️  Warnings:\n'));
      this.warnings.forEach(warning => {
        console.log(chalk.yellow(`  • ${warning}`));
      });
    }
    
    console.log(chalk.gray('═'.repeat(50)));
    
    if (allPassed && this.errors.length === 0) {
      console.log(chalk.green.bold('\n✅ All validations passed! Safe to push to GitHub.\n'));
      return true;
    } else {
      console.log(chalk.red.bold('\n❌ Validation failed! DO NOT push to GitHub.\n'));
      console.log(chalk.yellow('Fix the errors above and run validation again.\n'));
      return false;
    }
  }

  async quickValidation() {
    console.log(chalk.bold.blue('\n⚡ Quick Validation (NPM package only)\n'));
    
    const passed = await this.validateNpmPackage();
    
    if (passed) {
      console.log(chalk.green.bold('\n✅ Quick validation passed!\n'));
    } else {
      console.log(chalk.red.bold('\n❌ Quick validation failed!\n'));
      this.errors.forEach(error => {
        console.log(chalk.red(`  • ${error}`));
      });
    }
    
    return passed;
  }
}

// CLI
const validator = new PrePushValidator();
const mode = process.argv[2] || 'full';

async function run() {
  try {
    let success;
    
    if (mode === 'quick') {
      success = await validator.quickValidation();
    } else {
      success = await validator.runFullValidation();
    }
    
    process.exit(success ? 0 : 1);
  } catch (error) {
    console.error(chalk.red('\n💥 Unexpected error:'), error);
    await validator.cleanup();
    process.exit(1);
  }
}

// Handle interruption
process.on('SIGINT', async () => {
  console.log(chalk.yellow('\n\nInterrupted. Cleaning up...'));
  await validator.cleanup();
  process.exit(1);
});

run();