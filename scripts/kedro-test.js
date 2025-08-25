#!/usr/bin/env node
/**
 * Kedro pipeline wrapper for npm integration
 */
import { execSync } from 'child_process';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const KEDRO_DIR = path.join(__dirname, '..', 'kedro-pipeline');

/**
 * Check if Kedro and dependencies are installed
 */
function checkKedroInstalled() {
  try {
    // Check if kedro command is available (pipx installed)
    execSync('kedro --version', { stdio: 'ignore' });
    return true;
  } catch {
    console.log(chalk.yellow('⚠️  Kedro not installed. Please install with:'));
    console.log(chalk.gray('pipx install kedro'));
    console.log(chalk.gray('pipx inject kedro kedro-datasets kedro-viz'));
    return false;
  }
}

/**
 * Run Kedro pipeline
 */
function runPipeline(pipelineName = 'validation', options = {}) {
  if (!checkKedroInstalled()) {
    process.exit(1);
  }

  const args = process.argv.slice(2);
  let pipeline = 'validation';
  
  // Parse arguments
  if (args.includes('--quick')) {
    pipeline = 'quick';
  } else if (args.includes('--release')) {
    pipeline = 'release';
  }
  
  const skipDocker = args.includes('--skip-docker');
  const uiType = args.find(arg => arg.startsWith('--ui='))?.split('=')[1] || 'all';
  
  console.log(chalk.cyan('\n🚀 Running StackWizard Kedro Pipeline'));
  console.log(chalk.gray(`Pipeline: ${pipeline}`));
  console.log(chalk.gray(`UI Type: ${uiType}`));
  console.log(chalk.gray(`Skip Docker: ${skipDocker}`));
  console.log(chalk.gray('-'.repeat(60)));
  
  try {
    const cmd = [
      'python3',
      path.join(KEDRO_DIR, 'run_pipeline.py'),
      pipeline,
      skipDocker ? '--skip-docker' : '',
      `--ui=${uiType}`
    ].filter(Boolean).join(' ');
    
    execSync(cmd, { 
      stdio: 'inherit',
      cwd: KEDRO_DIR
    });
    
    console.log(chalk.green('\n✅ Pipeline completed successfully'));
    process.exit(0);
  } catch (error) {
    console.error(chalk.red('\n❌ Pipeline failed'));
    process.exit(1);
  }
}

// Run the pipeline
runPipeline();