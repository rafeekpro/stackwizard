#!/usr/bin/env node

import { program } from 'commander';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';
import {
  ErrorCodes,
  StackWizardError,
  Logger,
  ErrorHandler,
  Validators,
  checkSystemRequirements,
  cleanup,
} from './errors.js';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read version from package.json
const packageJsonPath = path.join(__dirname, '..', 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const VERSION = packageJson.version;

const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');

// ASCII Art Banner
const banner = chalk.cyan(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🧙‍♂️  StackWizard - Full-Stack Project Generator       ║
║                                                           ║
║     FastAPI + React + PostgreSQL + Docker                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`);

program
  .version(VERSION)
  .description(
    '🧙‍♂️ StackWizard - Magical full-stack project generator with FastAPI, React, and PostgreSQL'
  )
  .option('-n, --name <name>', 'Project name')
  .option('-u, --ui <ui>', 'UI library (mui or tailwind)')
  .option('-s, --skip-git', 'Skip git initialization')
  .option('-i, --install', 'Install dependencies after creation')
  .option('-q, --quick', 'Quick mode - use all defaults')
  .option('-d, --debug', 'Enable debug mode with detailed logging')
  .option('--check-requirements', 'Check system requirements and exit')
  .action(async (options) => {
    // Initialize logger and error handler
    const logger = new Logger(options.debug);
    const errorHandler = new ErrorHandler(logger);

    logger.debug('StackWizard started', { options, version: VERSION });

    // Check system requirements if requested
    if (options.checkRequirements) {
      console.log(chalk.cyan('\n🔍 Checking system requirements...\n'));
      try {
        const requirements = await checkSystemRequirements(logger);

        console.log(chalk.green.bold('System Requirements Check:\n'));
        for (const info of Object.values(requirements)) {
          const status = info.installed
            ? chalk.green('✓ Installed')
            : info.optional
              ? chalk.yellow('✗ Not installed (optional)')
              : chalk.red('✗ Not installed (required)');
          let output = `  ${info.name}: ${status}`;
          if (info.installed && info.version) {
            output += chalk.gray(` (v${info.version})`);
            if (info.command) {
              output += chalk.gray(` [${info.command}]`);
            }
          }
          console.log(output);
        }

        const hasRequired = Object.values(requirements)
          .filter((r) => !r.optional)
          .every((r) => r.installed);

        if (hasRequired) {
          console.log(
            chalk.green('\n✅ All required dependencies are installed!')
          );
        } else {
          console.log(
            chalk.red('\n❌ Some required dependencies are missing.')
          );
        }

        process.exit(0);
      } catch (error) {
        await errorHandler.handle(error);
        process.exit(1);
      }
    }

    try {
      // Check required system dependencies
      logger.info('Checking system requirements...');
      await checkSystemRequirements(logger);
    } catch (error) {
      await errorHandler.handle(error);
      process.exit(1);
    }
    console.log(banner);

    // Quick mode - use all defaults
    if (options.quick) {
      options.name = options.name || 'my-fullstack-app';
      options.ui = options.ui || 'mui';
      options.skipGit = true;
      options.install = false;
    }

    // Build prompts based on what's not provided via CLI options
    const prompts = [];

    if (!options.name && !options.quick) {
      prompts.push({
        type: 'input',
        name: 'projectName',
        message: 'What is your project name?',
        default: 'my-fullstack-app',
        validate: Validators.projectName,
      });
    }

    if (!options.ui) {
      prompts.push({
        type: 'list',
        name: 'uiLibrary',
        message: 'Choose your UI library for React frontend:',
        choices: [
          { name: '🎨 Material UI', value: 'mui' },
          { name: '🎯 Tailwind CSS', value: 'tailwind' },
        ],
      });
    }

    // Add database configuration prompts (skip in quick mode)
    if (!options.quick) {
      prompts.push(
        {
          type: 'input',
          name: 'dbName',
          message: 'Database name:',
          default: (answers) =>
            (answers.projectName || options.name || 'my_app').replace(
              /-/g,
              '_'
            ),
        },
        {
          type: 'input',
          name: 'dbUser',
          message: 'Database user:',
          default: 'postgres',
        },
        {
          type: 'password',
          name: 'dbPassword',
          message: 'Database password:',
          default: 'postgres',
          mask: '*',
        },
        {
          type: 'input',
          name: 'apiPort',
          message: 'Backend API port:',
          default: '8000',
          validate: Validators.port,
        },
        {
          type: 'input',
          name: 'frontendPort',
          message: 'Frontend port:',
          default: '3000',
          validate: Validators.port,
        }
      );
    }

    // Ask about additional features only if in interactive mode and not quick mode
    if (
      !options.quick &&
      (prompts.length > 0 || !options.skipGit === undefined)
    ) {
      prompts.push({
        type: 'checkbox',
        name: 'features',
        message: 'Select additional features:',
        choices: [
          {
            name: '📦 Initialize Git repository',
            value: 'git',
            checked: !options.skipGit,
          },
          {
            name: '🔧 Install dependencies',
            value: 'install',
            checked: options.install,
          },
          { name: '📝 Generate .gitignore', value: 'gitignore', checked: true },
          {
            name: '🚀 Add GitHub Actions CI/CD',
            value: 'github-actions',
            checked: false,
          },
        ],
      });
    }

    const answers = await inquirer.prompt(prompts);

    // Merge CLI options with answers
    if (options.name) answers.projectName = options.name;
    if (options.ui) answers.uiLibrary = options.ui;

    // Set defaults for quick mode
    if (options.quick) {
      answers.projectName =
        answers.projectName || options.name || 'my-fullstack-app';
      answers.uiLibrary = answers.uiLibrary || options.ui || 'mui';
      answers.dbName = answers.dbName || answers.projectName.replace(/-/g, '_');
      answers.dbUser = answers.dbUser || 'postgres';
      answers.dbPassword = answers.dbPassword || 'postgres';
      answers.apiPort = answers.apiPort || '8000';
      answers.frontendPort = answers.frontendPort || '3000';
      answers.features = ['gitignore'];
    }

    const projectPath = path.join(process.cwd(), answers.projectName);

    if (fs.existsSync(projectPath)) {
      const error = new StackWizardError(
        ErrorCodes.DIR_EXISTS,
        `Directory ${answers.projectName} already exists`,
        { projectName: answers.projectName, path: projectPath }
      );

      const recovered = await errorHandler.handle(error, {
        projectName: answers.projectName,
        details: `Path: ${projectPath}`,
      });

      if (!recovered) {
        process.exit(1);
      }

      // If recovery suggested, exit gracefully
      process.exit(0);
    }

    const spinner = ora('Creating project structure...').start();
    let projectCreated = false;

    try {
      logger.debug('Creating project directory', { path: projectPath });
      fs.ensureDirSync(projectPath);
      projectCreated = true;

      spinner.text = 'Copying backend template...';
      const backendSrc = path.join(TEMPLATES_DIR, 'common', 'backend');
      const backendDest = path.join(projectPath, 'backend');

      if (!fs.existsSync(backendSrc)) {
        throw new StackWizardError(
          ErrorCodes.TEMPLATE_NOT_FOUND,
          'Backend template not found',
          { path: backendSrc }
        );
      }

      logger.debug('Copying backend template', {
        from: backendSrc,
        to: backendDest,
      });
      await fs.copy(backendSrc, backendDest);

      spinner.text = 'Setting up database configuration...';
      const dbSrc = path.join(TEMPLATES_DIR, 'common', 'database');
      const dbDest = path.join(projectPath, 'database');
      await fs.copy(dbSrc, dbDest);

      spinner.text = 'Copying frontend template...';
      const frontendTemplate =
        answers.uiLibrary === 'mui' ? 'frontend-mui' : 'frontend-tailwind';
      const frontendSrc = path.join(TEMPLATES_DIR, frontendTemplate);
      const frontendDest = path.join(projectPath, 'frontend');

      if (!fs.existsSync(frontendSrc)) {
        throw new StackWizardError(
          ErrorCodes.TEMPLATE_NOT_FOUND,
          `Frontend template '${frontendTemplate}' not found`,
          { path: frontendSrc, template: frontendTemplate }
        );
      }

      logger.debug('Copying frontend template', {
        template: frontendTemplate,
        from: frontendSrc,
        to: frontendDest,
      });
      await fs.copy(frontendSrc, frontendDest);

      spinner.text = 'Creating Docker Compose configuration...';
      const dockerComposeSrc = path.join(
        TEMPLATES_DIR,
        'common',
        'docker-compose.yml'
      );
      const dockerComposeDest = path.join(projectPath, 'docker-compose.yml');
      let dockerComposeContent = await fs.readFile(dockerComposeSrc, 'utf-8');

      dockerComposeContent = dockerComposeContent
        .replace(/{{PROJECT_NAME}}/g, answers.projectName)
        .replace(/{{DB_NAME}}/g, answers.dbName)
        .replace(/{{DB_USER}}/g, answers.dbUser)
        .replace(/{{DB_PASSWORD}}/g, answers.dbPassword)
        .replace(/{{API_PORT}}/g, answers.apiPort)
        .replace(/{{FRONTEND_PORT}}/g, answers.frontendPort);

      await fs.writeFile(dockerComposeDest, dockerComposeContent);

      spinner.text = 'Creating environment configuration...';
      const envExampleSrc = path.join(TEMPLATES_DIR, 'common', '.env.example');
      const envExampleDest = path.join(projectPath, '.env.example');
      const envDest = path.join(projectPath, '.env');

      let envContent = await fs.readFile(envExampleSrc, 'utf-8');
      envContent = envContent
        .replace(/{{PROJECT_NAME}}/g, answers.projectName)
        .replace(/{{DB_NAME}}/g, answers.dbName)
        .replace(/{{DB_USER}}/g, answers.dbUser)
        .replace(/{{DB_PASSWORD}}/g, answers.dbPassword)
        .replace(/{{API_PORT}}/g, answers.apiPort)
        .replace(/{{FRONTEND_PORT}}/g, answers.frontendPort);

      await fs.writeFile(envExampleDest, envContent);
      await fs.writeFile(envDest, envContent);

      spinner.text = 'Setting up GitHub Actions workflows...';
      const githubSrc = path.join(TEMPLATES_DIR, 'common', '.github');
      const githubDest = path.join(projectPath, '.github');
      if (await fs.pathExists(githubSrc)) {
        await fs.copy(githubSrc, githubDest);
      }

      // Create uploads directory for backend
      spinner.text = 'Creating uploads directory...';
      const uploadsDir = path.join(projectPath, 'uploads');
      await fs.ensureDir(uploadsDir);
      await fs.writeFile(path.join(uploadsDir, '.gitkeep'), '');

      spinner.text = 'Updating package.json configurations...';
      const packageJsonPath = path.join(frontendDest, 'package.json');
      if (fs.existsSync(packageJsonPath)) {
        const packageJson = await fs.readJson(packageJsonPath);
        packageJson.name = answers.projectName;
        // Keep proxy as backend:8000 for container communication
        // packageJson.proxy is already set correctly in template
        await fs.writeJson(packageJsonPath, packageJson, { spaces: 2 });
      }

      // Create .gitignore if requested
      if (answers.features && answers.features.includes('gitignore')) {
        spinner.text = 'Creating .gitignore...';
        const gitignoreContent = `# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.env
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Docker
.dockerignore

# Database
*.db
*.sqlite3
postgres-data/

# Logs
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/
coverage/
`;
        await fs.writeFile(
          path.join(projectPath, '.gitignore'),
          gitignoreContent
        );
      }

      spinner.text = 'Creating project README...';
      const readmeSrc = path.join(TEMPLATES_DIR, 'common', 'PROJECT_README.md');
      const readmeDest = path.join(projectPath, 'README.md');

      let readmeContent = await fs.readFile(readmeSrc, 'utf-8');
      readmeContent = readmeContent
        .replace(/{{PROJECT_NAME}}/g, answers.projectName)
        .replace(/{{DB_NAME}}/g, answers.dbName)
        .replace(/{{DB_USER}}/g, answers.dbUser)
        .replace(/{{DB_PASSWORD}}/g, answers.dbPassword)
        .replace(/{{API_PORT}}/g, answers.apiPort)
        .replace(/{{FRONTEND_PORT}}/g, answers.frontendPort)
        .replace(
          /{{UI_LIBRARY}}/g,
          answers.uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS'
        );

      await fs.writeFile(readmeDest, readmeContent);

      // Initialize Git repository if requested
      if (answers.features && answers.features.includes('git')) {
        spinner.text = 'Initializing Git repository...';
        try {
          logger.debug('Initializing Git repository');
          await execAsync('git init', { cwd: projectPath });
          await execAsync('git add .', { cwd: projectPath });
          await execAsync(
            'git commit -m "Initial commit from StackWizard 🧙‍♂️"',
            { cwd: projectPath }
          );
          spinner.text = 'Git repository initialized';
          logger.info('Git repository initialized successfully');
        } catch (gitError) {
          const error = new StackWizardError(
            ErrorCodes.GIT_NOT_INSTALLED,
            'Git initialization failed',
            { error: gitError.message }
          );

          await errorHandler.handle(error, {
            projectName: answers.projectName,
            skipFeatures: [],
          });

          spinner.warn(
            chalk.yellow('Git initialization skipped (continuing without Git)')
          );
        }
      }

      // Install dependencies if requested
      if (answers.features && answers.features.includes('install')) {
        spinner.text = 'Installing backend dependencies...';
        try {
          logger.debug('Installing backend dependencies');
          await execAsync(
            'pip3 install -r requirements.txt || pip install -r requirements.txt',
            {
              cwd: path.join(projectPath, 'backend'),
              timeout: 120000, // 2 minute timeout
            }
          );
          logger.info('Backend dependencies installed successfully');
        } catch (pipError) {
          const error = new StackWizardError(
            ErrorCodes.PIP_INSTALL_FAILED,
            'Backend dependencies installation failed',
            { error: pipError.message }
          );

          await errorHandler.handle(error, {
            projectName: answers.projectName,
            skipFeatures: [],
          });

          spinner.warn(
            chalk.yellow(
              'Backend dependencies installation skipped (install manually later)'
            )
          );
        }

        spinner.text = 'Installing frontend dependencies...';
        try {
          logger.debug('Installing frontend dependencies');
          await execAsync('npm install', {
            cwd: path.join(projectPath, 'frontend'),
            timeout: 180000, // 3 minute timeout
          });
          logger.info('Frontend dependencies installed successfully');
        } catch (npmError) {
          const error = new StackWizardError(
            ErrorCodes.NPM_INSTALL_FAILED,
            'Frontend dependencies installation failed',
            { error: npmError.message }
          );

          await errorHandler.handle(error, {
            projectName: answers.projectName,
            skipFeatures: [],
          });

          spinner.warn(
            chalk.yellow(
              'Frontend dependencies installation skipped (install manually later)'
            )
          );
        }
      }

      spinner.succeed(chalk.green.bold('✅ Project created successfully!'));

      // Display project summary
      console.log('\n' + chalk.cyan('📋 Project Summary:'));
      console.log(chalk.white(`  • Name: ${chalk.bold(answers.projectName)}`));
      console.log(
        chalk.white(
          `  • UI Library: ${chalk.bold(answers.uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS')}`
        )
      );
      console.log(chalk.white(`  • Database: ${chalk.bold('PostgreSQL')}`));
      console.log(
        chalk.white(`  • Backend Port: ${chalk.bold(answers.apiPort)}`)
      );
      console.log(
        chalk.white(`  • Frontend Port: ${chalk.bold(answers.frontendPort)}`)
      );

      if (answers.features && answers.features.length > 0) {
        console.log(
          chalk.white(
            `  • Features: ${chalk.bold(answers.features.join(', '))}`
          )
        );
      }

      console.log('\n' + chalk.cyan.bold('🚀 Next steps:'));
      console.log(
        chalk.white(
          `  ${chalk.gray('$')} cd ${chalk.green(answers.projectName)}`
        )
      );
      console.log(chalk.white(`  ${chalk.gray('$')} docker-compose up -d`));
      console.log(
        chalk.white(
          `  ${chalk.gray('$')} Open ${chalk.blue(`http://localhost:${answers.frontendPort}`)}\n`
        )
      );

      console.log(chalk.cyan('📚 Documentation:'));
      console.log(
        chalk.white(
          `  • API Docs: ${chalk.blue(`http://localhost:${answers.apiPort}/docs`)}`
        )
      );
      console.log(
        chalk.white(
          `  • README: ${chalk.gray(`${answers.projectName}/README.md`)}\n`
        )
      );

      console.log(chalk.green.bold('Happy coding! 🎉'));

      // Log success
      logger.info('Project created successfully', {
        projectName: answers.projectName,
        uiLibrary: answers.uiLibrary,
        features: answers.features,
      });

      if (logger.debugMode) {
        console.log(chalk.gray(`\nDebug log saved to: ${logger.getLogPath()}`));
      }
    } catch (error) {
      spinner.fail(chalk.red('Failed to create project'));

      // Handle the error with our error handler
      const handled = await errorHandler.handle(error, {
        projectName: answers.projectName,
        projectPath,
        stage: 'project_creation',
      });

      // Clean up if project was partially created
      if (projectCreated && !handled) {
        await cleanup(projectPath, logger);
      }

      // Generate error report if in debug mode
      if (logger.debugMode) {
        errorHandler.generateErrorReport();
      }

      process.exit(1);
    }
  });

program.parse(process.argv);
