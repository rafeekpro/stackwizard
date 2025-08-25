#!/usr/bin/env node

/**
 * REAL TEST that will ACTUALLY catch Docker dependency issues
 * This test:
 * 1. Generates a REAL project using the CLI
 * 2. Builds REAL Docker image
 * 3. Runs container and checks for REAL errors
 */

import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import chalk from 'chalk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const cliPath = path.join(path.dirname(__dirname), 'src', 'index.js');

class RealDockerDepsTest {
  constructor() {
    this.testDir = path.join('/tmp', `real-docker-test-${Date.now()}`);
    this.projectName = 'test-deps-project';
    this.errors = [];
  }

  async cleanup() {
    try {
      // Stop any running containers
      execSync(`docker stop $(docker ps -q --filter "name=${this.projectName}") 2>/dev/null || true`, {
        stdio: 'pipe'
      });
      // Remove test directory
      await fs.remove(this.testDir);
    } catch (e) {
      // Ignore
    }
  }

  async generateRealProject(uiType = 'mui') {
    console.log(chalk.blue(`\n📦 Generating REAL project with ${uiType.toUpperCase()}...`));
    
    await fs.ensureDir(this.testDir);
    
    // Create expect script to automate CLI
    const expectScript = `#!/usr/bin/expect -f
set timeout 30
spawn node ${cliPath}
expect "What is your project name?"
send "${this.projectName}\\r"
expect "Choose your UI library"
${uiType === 'mui' ? 'send "\\r"' : 'send "\\033\\[B\\r"'}
expect "Database name:"
send "testdb\\r"
expect "Database user:"
send "testuser\\r"
expect "Database password:"
send "testpass\\r"
expect "API port:"
send "8888\\r"
expect "Frontend port:"
send "3888\\r"
expect "Select additional features:"
send "\\r"
expect eof`;

    const expectFile = path.join(this.testDir, 'generate.exp');
    await fs.writeFile(expectFile, expectScript);
    await fs.chmod(expectFile, '755');
    
    // Run generation
    try {
      execSync(`cd ${this.testDir} && ${expectFile}`, {
        stdio: 'pipe',
        encoding: 'utf8'
      });
      console.log(chalk.green('✅ Project generated'));
      return true;
    } catch (error) {
      console.log(chalk.red('❌ Failed to generate project'));
      this.errors.push(`Generation failed: ${error.message}`);
      return false;
    }
  }

  async testDockerBuild() {
    console.log(chalk.blue('\n🐳 Building Docker image from GENERATED project...'));
    
    const projectPath = path.join(this.testDir, this.projectName);
    const frontendPath = path.join(projectPath, 'frontend');
    
    if (!fs.existsSync(frontendPath)) {
      console.log(chalk.red('❌ Frontend directory not found'));
      this.errors.push('Frontend directory missing');
      return false;
    }
    
    try {
      // Build Docker image
      console.log(chalk.yellow('Building frontend Docker image...'));
      const buildOutput = execSync(
        `cd ${frontendPath} && docker build -t ${this.projectName}-frontend . 2>&1`,
        { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
      );
      
      // Check for dependency errors in build
      if (buildOutput.includes('ERROR: Failed to install')) {
        console.log(chalk.red('❌ Docker build failed - missing dependencies'));
        console.log(buildOutput);
        this.errors.push('Docker build failed with dependency errors');
        return false;
      }
      
      console.log(chalk.green('✅ Docker image built'));
      return true;
    } catch (error) {
      console.log(chalk.red('❌ Docker build failed'));
      console.log(error.stdout || error.message);
      this.errors.push(`Docker build failed: ${error.message}`);
      return false;
    }
  }

  async testDockerRun() {
    console.log(chalk.blue('\n🚀 Running Docker container...'));
    
    const containerName = `${this.projectName}-test`;
    
    try {
      // Stop any existing container
      execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      
      // Run container
      execSync(`docker run -d --name ${containerName} -p 3888:3000 ${this.projectName}-frontend`, {
        stdio: 'pipe'
      });
      
      console.log(chalk.yellow('Waiting for container to start...'));
      await new Promise(resolve => setTimeout(resolve, 15000));
      
      // Check logs for errors
      const logs = execSync(`docker logs ${containerName} 2>&1`, {
        encoding: 'utf8',
        maxBuffer: 10 * 1024 * 1024
      });
      
      // Check for dependency errors
      const errorPatterns = [
        /Module not found.*@mui\/material/i,
        /Module not found.*@mui\/icons-material/i,
        /Can't resolve '@mui\/material'/i,
        /Module not found.*@headlessui\/react/i,
        /Module not found.*@heroicons\/react/i,
        /Can't resolve.*tailwindcss/i
      ];
      
      for (const pattern of errorPatterns) {
        if (pattern.test(logs)) {
          const match = logs.match(pattern);
          console.log(chalk.red(`\n❌ DEPENDENCY ERROR FOUND: ${match[0]}`));
          this.errors.push(`Runtime error: ${match[0]}`);
          
          // Show relevant logs
          console.log(chalk.yellow('\nContainer logs:'));
          console.log(logs.split('\n').slice(-30).join('\n'));
          
          // Cleanup
          execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
          execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
          return false;
        }
      }
      
      // Check for successful compilation
      if (!logs.includes('Compiled successfully') && !logs.includes('webpack compiled')) {
        console.log(chalk.red('❌ Frontend did not compile successfully'));
        this.errors.push('Frontend compilation failed');
        
        // Cleanup
        execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
        execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
        return false;
      }
      
      // Cleanup
      execSync(`docker stop ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      execSync(`docker rm ${containerName} 2>/dev/null || true`, { stdio: 'pipe' });
      
      console.log(chalk.green('✅ Container runs without dependency errors'));
      return true;
    } catch (error) {
      console.log(chalk.red('❌ Failed to run container'));
      this.errors.push(`Container run failed: ${error.message}`);
      return false;
    }
  }

  async runFullTest(uiType = 'mui') {
    console.log(chalk.bold.blue(`\n🧪 REAL Docker Dependency Test - ${uiType.toUpperCase()}\n`));
    
    let success = true;
    
    try {
      // Generate real project
      if (!await this.generateRealProject(uiType)) {
        return false;
      }
      
      // Build Docker image
      if (!await this.testDockerBuild()) {
        return false;
      }
      
      // Run and test container
      if (!await this.testDockerRun()) {
        return false;
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
      console.log(chalk.green('Docker dependencies are properly installed.'));
    } else {
      console.log(chalk.red.bold(`❌ FOUND ${this.errors.length} ERRORS:`));
      this.errors.forEach((error, i) => {
        console.log(chalk.red(`\n${i + 1}. ${error}`));
      });
    }
    
    console.log(chalk.gray('\n' + '═'.repeat(50)));
  }
}

// Run the test
async function main() {
  const tester = new RealDockerDepsTest();
  
  // Test both templates
  const muiSuccess = await tester.runFullTest('mui');
  
  // Reset for second test
  tester.errors = [];
  const tailwindSuccess = await tester.runFullTest('tailwind');
  
  // Print summary
  tester.printSummary();
  
  // Exit with appropriate code
  if (!muiSuccess || !tailwindSuccess) {
    console.log(chalk.red.bold('\n❌ REAL Docker dependency test FAILED!'));
    process.exit(1);
  }
  
  console.log(chalk.green.bold('\n✅ REAL Docker dependency test PASSED!\n'));
  process.exit(0);
}

main().catch(error => {
  console.error(chalk.red('Fatal error:'), error);
  process.exit(1);
});