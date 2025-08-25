#!/usr/bin/env node

/**
 * Local Test Orchestrator
 * Alternative to Airflow for test orchestration
 * Run before pushing to ensure all tests pass
 */

import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs-extra';
import path from 'path';

const execAsync = promisify(exec);

class TestOrchestrator {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
  }

  // Test definitions with dependencies
  tests = {
    'lint': {
      name: 'Code Linting',
      command: 'npm run lint',
      critical: true,
      dependencies: []
    },
    'format': {
      name: 'Code Formatting',
      command: 'npm run format:check',
      critical: true,
      dependencies: []
    },
    'package': {
      name: 'NPM Package Integrity',
      command: 'npm run test:package',
      critical: true,
      dependencies: ['lint', 'format']
    },
    'structure': {
      name: 'Project Structure',
      command: 'npm run test:structure',
      critical: true,
      dependencies: ['package']
    },
    'unit': {
      name: 'Unit Tests',
      command: 'npm test',
      critical: false,
      dependencies: ['lint']
    },
    'docker-build': {
      name: 'Docker Build',
      command: 'cd templates/frontend-mui && docker build -t test-mui . > /dev/null 2>&1',
      critical: false,
      dependencies: ['package'],
      condition: () => this.hasDockerChanges()
    },
    'docker-compose': {
      name: 'Docker Compose Integration',
      command: 'npm run test:docker',
      critical: false,
      dependencies: ['docker-build'],
      condition: () => this.hasDockerChanges(),
      timeout: 300000
    },
    'generated-project': {
      name: 'Generated Project Test',
      command: async () => await this.testGeneratedProject(),
      critical: false,
      dependencies: ['structure'],
      condition: () => this.hasTemplateChanges()
    }
  };

  async hasDockerChanges() {
    try {
      const { stdout } = await execAsync('git diff --name-only HEAD~1 HEAD');
      return stdout.includes('Dockerfile') || stdout.includes('docker-compose');
    } catch {
      return true; // If can't determine, run the test
    }
  }

  async hasTemplateChanges() {
    try {
      const { stdout } = await execAsync('git diff --name-only HEAD~1 HEAD');
      return stdout.includes('templates/');
    } catch {
      return true;
    }
  }

  async testGeneratedProject() {
    const testDir = path.join(process.cwd(), '..', 'test-orchestrator-project');
    
    try {
      // Clean up if exists
      await fs.remove(testDir);
      
      // Generate project
      const input = 'test-orchestrator-project\n\ntest_db\ntest_user\ntest_pass\n8000\n3000\n';
      await execAsync(`echo "${input}" | npm start`);
      
      // Check if project was created
      if (!await fs.pathExists(testDir)) {
        throw new Error('Project generation failed');
      }
      
      // Test docker-compose
      await execAsync(`cd ${testDir} && docker-compose config`);
      
      // Clean up
      await fs.remove(testDir);
      
      return { success: true };
    } catch (error) {
      await fs.remove(testDir).catch(() => {});
      throw error;
    }
  }

  async runTest(testId) {
    const test = this.tests[testId];
    const spinner = ora(`Running ${test.name}...`).start();
    
    const result = {
      id: testId,
      name: test.name,
      status: 'pending',
      duration: 0,
      error: null
    };
    
    const startTime = Date.now();
    
    try {
      // Check condition if exists
      if (test.condition && !(await test.condition())) {
        spinner.info(`${test.name} - Skipped (condition not met)`);
        result.status = 'skipped';
        this.results.push(result);
        return result;
      }
      
      // Run command
      if (typeof test.command === 'function') {
        await test.command();
      } else {
        const options = test.timeout ? { timeout: test.timeout } : {};
        await execAsync(test.command, options);
      }
      
      result.status = 'passed';
      result.duration = Date.now() - startTime;
      spinner.succeed(chalk.green(`${test.name} - Passed (${result.duration}ms)`));
      
    } catch (error) {
      result.status = 'failed';
      result.duration = Date.now() - startTime;
      result.error = error.message;
      
      if (test.critical) {
        spinner.fail(chalk.red(`${test.name} - Failed (Critical)`));
        throw error;
      } else {
        spinner.warn(chalk.yellow(`${test.name} - Failed (Non-critical)`));
      }
    }
    
    this.results.push(result);
    return result;
  }

  async runParallel(testIds) {
    console.log(chalk.blue(`\nRunning ${testIds.length} tests in parallel...\n`));
    
    const promises = testIds.map(id => this.runTest(id));
    const results = await Promise.allSettled(promises);
    
    return results.map(r => r.status === 'fulfilled' ? r.value : r.reason);
  }

  async runSequential(testIds) {
    console.log(chalk.blue(`\nRunning ${testIds.length} tests sequentially...\n`));
    
    const results = [];
    for (const id of testIds) {
      const result = await this.runTest(id);
      results.push(result);
      
      if (result.status === 'failed' && this.tests[id].critical) {
        break;
      }
    }
    
    return results;
  }

  async orchestrate(mode = 'smart') {
    console.log(chalk.bold.blue('🎭 Test Orchestrator Started\n'));
    console.log(chalk.gray(`Mode: ${mode}`));
    console.log(chalk.gray(`Time: ${new Date().toLocaleString()}\n`));
    
    try {
      if (mode === 'quick') {
        // Quick mode - only critical tests
        await this.runParallel(['lint', 'format']);
        await this.runSequential(['package', 'structure']);
        
      } else if (mode === 'full') {
        // Full mode - all tests
        await this.runParallel(['lint', 'format']);
        await this.runSequential(['package', 'structure']);
        await this.runParallel(['unit', 'docker-build']);
        await this.runSequential(['docker-compose', 'generated-project']);
        
      } else {
        // Smart mode - based on changes
        await this.runParallel(['lint', 'format']);
        await this.runSequential(['package', 'structure']);
        
        if (await this.hasDockerChanges()) {
          await this.runSequential(['docker-build', 'docker-compose']);
        }
        
        if (await this.hasTemplateChanges()) {
          await this.runTest('generated-project');
        }
      }
      
      this.printSummary();
      
    } catch (error) {
      console.error(chalk.red('\n❌ Orchestration failed:'), error.message);
      this.printSummary();
      process.exit(1);
    }
  }

  printSummary() {
    const duration = Date.now() - this.startTime;
    const passed = this.results.filter(r => r.status === 'passed').length;
    const failed = this.results.filter(r => r.status === 'failed').length;
    const skipped = this.results.filter(r => r.status === 'skipped').length;
    
    console.log(chalk.bold.blue('\n📊 Test Summary\n'));
    console.log(chalk.gray('═'.repeat(50)));
    
    this.results.forEach(result => {
      const icon = {
        passed: '✅',
        failed: '❌',
        skipped: '⏭️',
        pending: '⏳'
      }[result.status];
      
      const color = {
        passed: chalk.green,
        failed: chalk.red,
        skipped: chalk.gray,
        pending: chalk.yellow
      }[result.status];
      
      console.log(`${icon} ${color(result.name.padEnd(30))} ${result.duration}ms`);
      
      if (result.error) {
        console.log(chalk.red(`   └─ ${result.error}`));
      }
    });
    
    console.log(chalk.gray('═'.repeat(50)));
    console.log(chalk.bold(`Total: ${passed} passed, ${failed} failed, ${skipped} skipped`));
    console.log(chalk.bold(`Duration: ${(duration / 1000).toFixed(2)}s`));
    
    if (failed === 0) {
      console.log(chalk.green.bold('\n✅ All tests passed! Ready to push.\n'));
    } else {
      console.log(chalk.red.bold('\n❌ Some tests failed. Please fix before pushing.\n'));
    }
  }

  // GitHub Actions comparison
  async compareWithCI() {
    console.log(chalk.blue('\n🔄 Comparing with GitHub Actions...\n'));
    
    try {
      const { stdout } = await execAsync('gh pr checks --json');
      const checks = JSON.parse(stdout);
      
      console.log('GitHub Actions status:');
      checks.forEach(check => {
        const icon = check.conclusion === 'success' ? '✅' : '❌';
        console.log(`${icon} ${check.name}`);
      });
    } catch {
      console.log(chalk.yellow('No PR found or GitHub CLI not configured'));
    }
  }
}

// CLI Interface
const orchestrator = new TestOrchestrator();
const mode = process.argv[2] || 'smart';

const validModes = ['quick', 'smart', 'full'];
if (!validModes.includes(mode)) {
  console.log(chalk.red(`Invalid mode: ${mode}`));
  console.log(chalk.yellow(`Valid modes: ${validModes.join(', ')}`));
  process.exit(1);
}

// Run orchestration
orchestrator.orchestrate(mode).then(() => {
  if (process.argv.includes('--compare-ci')) {
    orchestrator.compareWithCI();
  }
});