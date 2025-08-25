#!/usr/bin/env node

/**
 * REAL Docker Runtime Test
 * This test ACTUALLY runs Docker containers and checks for dependency errors
 * It will CATCH the "@mui/material not found" errors
 */

import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import chalk from 'chalk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.dirname(__dirname);

class DockerRuntimeTest {
  constructor() {
    this.testDir = path.join('/tmp', `docker-runtime-test-${Date.now()}`);
    this.errors = [];
  }

  async cleanup() {
    try {
      if (fs.existsSync(this.testDir)) {
        // Stop containers
        execSync(`cd ${this.testDir} && docker compose down -v 2>/dev/null || true`, { 
          stdio: 'pipe' 
        });
        // Remove directory
        await fs.remove(this.testDir);
      }
    } catch (e) {
      // Ignore cleanup errors
    }
  }

  async setupTestProject(template = 'mui') {
    console.log(chalk.blue(`\n📦 Setting up ${template.toUpperCase()} test project...`));
    
    await fs.ensureDir(this.testDir);
    
    // Copy templates
    const frontendTemplate = template === 'mui' ? 'frontend-mui' : 'frontend-tailwind';
    
    // Copy backend
    await fs.copy(
      path.join(projectRoot, 'templates', 'common', 'backend'),
      path.join(this.testDir, 'backend')
    );
    
    // Copy frontend
    await fs.copy(
      path.join(projectRoot, 'templates', frontendTemplate),
      path.join(this.testDir, 'frontend')
    );
    
    // Copy docker-compose
    await fs.copy(
      path.join(projectRoot, 'templates', 'common', 'docker-compose.yml'),
      path.join(this.testDir, 'docker-compose.yml')
    );
    
    // Create .env
    const envContent = `
PROJECT_NAME=test-project
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_pass
DB_HOST=database
DB_PORT=5432
API_PORT=8000
FRONTEND_PORT=3000
JWT_SECRET=test-secret-key-123
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
    `.trim();
    
    await fs.writeFile(path.join(this.testDir, '.env'), envContent);
    
    console.log(chalk.green('✅ Test project created'));
  }

  async buildDockerImages() {
    console.log(chalk.blue('\n🐳 Building Docker images...'));
    
    try {
      // Build frontend
      console.log(chalk.yellow('Building frontend...'));
      const frontendBuild = execSync(
        `cd ${this.testDir} && docker compose build frontend 2>&1`,
        { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024 }
      );
      
      // Check for build errors
      if (frontendBuild.includes('ERROR') || frontendBuild.includes('error')) {
        console.log(chalk.red('Frontend build output:'));
        console.log(frontendBuild);
      }
      
      // Build backend
      console.log(chalk.yellow('Building backend...'));
      execSync(
        `cd ${this.testDir} && docker compose build backend 2>&1`,
        { encoding: 'utf8', stdio: 'pipe' }
      );
      
      console.log(chalk.green('✅ Docker images built'));
      return true;
    } catch (error) {
      console.log(chalk.red('❌ Docker build failed:'));
      console.log(error.message);
      this.errors.push(`Docker build failed: ${error.message}`);
      return false;
    }
  }

  async startContainers() {
    console.log(chalk.blue('\n🚀 Starting Docker containers...'));
    
    try {
      // Start containers
      execSync(
        `cd ${this.testDir} && docker compose up -d`,
        { stdio: 'pipe' }
      );
      
      console.log(chalk.yellow('Waiting for containers to start...'));
      await new Promise(resolve => setTimeout(resolve, 20000)); // Wait 20 seconds
      
      console.log(chalk.green('✅ Containers started'));
      return true;
    } catch (error) {
      console.log(chalk.red('❌ Failed to start containers:'));
      console.log(error.message);
      this.errors.push(`Container start failed: ${error.message}`);
      return false;
    }
  }

  async checkForErrors() {
    console.log(chalk.blue('\n🔍 Checking for runtime errors...'));
    
    try {
      // Get logs
      const logs = execSync(
        `cd ${this.testDir} && docker compose logs frontend 2>&1`,
        { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
      );
      
      // CRITICAL: Check for dependency errors
      const errorPatterns = [
        /Module not found.*@mui\/material/gi,
        /Module not found.*@mui\/icons-material/gi,
        /Can't resolve '@mui\/material'/gi,
        /Module not found.*@headlessui\/react/gi,
        /Module not found.*@heroicons\/react/gi,
        /Can't resolve '@headlessui\/react'/gi,
        /Can't resolve '@heroicons\/react'/gi,
        /Failed to compile/gi,
        /ERROR in \./gi,
        /npm ERR!/gi
      ];
      
      let foundErrors = false;
      
      for (const pattern of errorPatterns) {
        const matches = logs.match(pattern);
        if (matches) {
          foundErrors = true;
          console.log(chalk.red(`\n❌ DEPENDENCY ERROR FOUND:`));
          matches.forEach(match => {
            console.log(chalk.red(`   ${match}`));
            this.errors.push(match);
          });
        }
      }
      
      // Check for successful compilation
      if (!logs.includes('Compiled successfully') && !logs.includes('webpack compiled')) {
        console.log(chalk.red('\n❌ Frontend did not compile successfully'));
        
        // Show last 30 lines of logs
        const lastLines = logs.split('\n').slice(-30).join('\n');
        console.log(chalk.yellow('\nLast 30 lines of logs:'));
        console.log(lastLines);
        
        this.errors.push('Frontend compilation failed');
        foundErrors = true;
      }
      
      if (!foundErrors) {
        console.log(chalk.green('✅ No dependency errors found'));
        console.log(chalk.green('✅ Frontend compiled successfully'));
      }
      
      return !foundErrors;
    } catch (error) {
      console.log(chalk.red('❌ Error checking logs:'));
      console.log(error.message);
      this.errors.push(`Log check failed: ${error.message}`);
      return false;
    }
  }

  async testEndpoint() {
    console.log(chalk.blue('\n🌐 Testing frontend endpoint...'));
    
    try {
      // Try to access frontend
      execSync('curl -f http://localhost:3000 2>/dev/null', { 
        encoding: 'utf8',
        stdio: 'pipe' 
      });
      
      console.log(chalk.green('✅ Frontend is accessible'));
      return true;
    } catch (error) {
      console.log(chalk.red('❌ Frontend is not accessible'));
      this.errors.push('Frontend endpoint not accessible');
      return false;
    }
  }

  async runFullTest(template = 'mui') {
    console.log(chalk.bold.blue(`\n🧪 Docker Runtime Test - ${template.toUpperCase()}\n`));
    console.log(chalk.gray('This test will ACTUALLY run Docker and check for errors\n'));
    
    let success = true;
    
    try {
      // Setup
      await this.setupTestProject(template);
      
      // Build
      if (!await this.buildDockerImages()) {
        success = false;
      }
      
      // Start
      if (success && !await this.startContainers()) {
        success = false;
      }
      
      // Check errors
      if (success && !await this.checkForErrors()) {
        success = false;
      }
      
      // Test endpoint
      if (success && !await this.testEndpoint()) {
        success = false;
      }
      
    } catch (error) {
      console.log(chalk.red('\n💥 Unexpected error:'));
      console.log(error);
      success = false;
      this.errors.push(`Unexpected: ${error.message}`);
    } finally {
      await this.cleanup();
    }
    
    return success;
  }

  printSummary() {
    console.log(chalk.bold.blue('\n📊 Test Summary\n'));
    console.log(chalk.gray('═'.repeat(50)));
    
    if (this.errors.length === 0) {
      console.log(chalk.green.bold('✅ ALL TESTS PASSED!'));
      console.log(chalk.green('No Docker dependency issues found.'));
    } else {
      console.log(chalk.red.bold(`❌ FOUND ${this.errors.length} ERRORS:`));
      this.errors.forEach((error, i) => {
        console.log(chalk.red(`\n${i + 1}. ${error}`));
      });
      
      console.log(chalk.yellow('\n🔧 HOW TO FIX:'));
      console.log(chalk.yellow('1. Check that package-lock.json exists in templates'));
      console.log(chalk.yellow('2. Verify all dependencies in package.json'));
      console.log(chalk.yellow('3. Run: cd templates/frontend-mui && npm install'));
      console.log(chalk.yellow('4. Test locally: docker build -t test .'));
    }
    
    console.log(chalk.gray('\n' + '═'.repeat(50)));
  }
}

// Run the test
async function main() {
  const tester = new DockerRuntimeTest();
  
  // Test both templates
  const muiSuccess = await tester.runFullTest('mui');
  const tailwindSuccess = await tester.runFullTest('tailwind');
  
  // Print summary
  tester.printSummary();
  
  // Exit with appropriate code
  if (!muiSuccess || !tailwindSuccess) {
    console.log(chalk.red.bold('\n❌ Docker runtime test FAILED!'));
    console.log(chalk.red('This would have caught the "@mui/material" error!\n'));
    process.exit(1);
  }
  
  console.log(chalk.green.bold('\n✅ Docker runtime test PASSED!\n'));
  process.exit(0);
}

// Handle cleanup on exit
process.on('SIGINT', async () => {
  console.log(chalk.yellow('\n\nCleaning up...'));
  const tester = new DockerRuntimeTest();
  await tester.cleanup();
  process.exit(1);
});

main().catch(error => {
  console.error(chalk.red('Fatal error:'), error);
  process.exit(1);
});