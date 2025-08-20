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

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
  .version('1.1.0')
  .description('🧙‍♂️ StackWizard - Magical full-stack project generator with FastAPI, React, and PostgreSQL')
  .option('-n, --name <name>', 'Project name')
  .option('-u, --ui <ui>', 'UI library (mui or tailwind)')
  .option('-s, --skip-git', 'Skip git initialization')
  .option('-i, --install', 'Install dependencies after creation')
  .option('-q, --quick', 'Quick mode - use all defaults')
  .action(async (options) => {
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
        validate: (input) => {
          if (/^[a-z0-9-]+$/.test(input)) return true;
          return 'Project name should contain only lowercase letters, numbers, and hyphens';
        }
      });
    }
    
    if (!options.ui) {
      prompts.push({
        type: 'list',
        name: 'uiLibrary',
        message: 'Choose your UI library for React frontend:',
        choices: [
          { name: '🎨 Material UI', value: 'mui' },
          { name: '🎯 Tailwind CSS', value: 'tailwind' }
        ]
      });
    }
    
    // Add database configuration prompts (skip in quick mode)
    if (!options.quick) {
      prompts.push(
      {
        type: 'input',
        name: 'dbName',
        message: 'Database name:',
        default: (answers) => (answers.projectName || options.name || 'my_app').replace(/-/g, '_')
      },
      {
        type: 'input',
        name: 'dbUser',
        message: 'Database user:',
        default: 'postgres'
      },
      {
        type: 'password',
        name: 'dbPassword',
        message: 'Database password:',
        default: 'postgres',
        mask: '*'
      },
      {
        type: 'input',
        name: 'apiPort',
        message: 'Backend API port:',
        default: '8000',
        validate: (input) => {
          const port = parseInt(input);
          if (port > 0 && port < 65536) return true;
          return 'Please enter a valid port number (1-65535)';
        }
      },
      {
        type: 'input',
        name: 'frontendPort',
        message: 'Frontend port:',
        default: '3000',
        validate: (input) => {
          const port = parseInt(input);
          if (port > 0 && port < 65536) return true;
          return 'Please enter a valid port number (1-65535)';
        }
      }
      );
    }
    
    // Ask about additional features only if in interactive mode and not quick mode
    if (!options.quick && (prompts.length > 0 || !options.skipGit === undefined)) {
      prompts.push({
        type: 'checkbox',
        name: 'features',
        message: 'Select additional features:',
        choices: [
          { name: '📦 Initialize Git repository', value: 'git', checked: !options.skipGit },
          { name: '🔧 Install dependencies', value: 'install', checked: options.install },
          { name: '📝 Generate .gitignore', value: 'gitignore', checked: true },
          { name: '🚀 Add GitHub Actions CI/CD', value: 'github-actions', checked: false }
        ]
      });
    }
    
    const answers = await inquirer.prompt(prompts);
    
    // Merge CLI options with answers
    if (options.name) answers.projectName = options.name;
    if (options.ui) answers.uiLibrary = options.ui;
    
    // Set defaults for quick mode
    if (options.quick) {
      answers.projectName = answers.projectName || options.name || 'my-fullstack-app';
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
      console.log(chalk.red(`\n❌ Directory ${answers.projectName} already exists!`));
      process.exit(1);
    }

    const spinner = ora('Creating project structure...').start();

    try {
      fs.ensureDirSync(projectPath);
      
      spinner.text = 'Copying backend template...';
      const backendSrc = path.join(TEMPLATES_DIR, 'common', 'backend');
      const backendDest = path.join(projectPath, 'backend');
      await fs.copy(backendSrc, backendDest);

      spinner.text = 'Setting up database configuration...';
      const dbSrc = path.join(TEMPLATES_DIR, 'common', 'database');
      const dbDest = path.join(projectPath, 'database');
      await fs.copy(dbSrc, dbDest);

      spinner.text = 'Copying frontend template...';
      const frontendTemplate = answers.uiLibrary === 'mui' ? 'frontend-mui' : 'frontend-tailwind';
      const frontendSrc = path.join(TEMPLATES_DIR, frontendTemplate);
      const frontendDest = path.join(projectPath, 'frontend');
      await fs.copy(frontendSrc, frontendDest);

      spinner.text = 'Creating Docker Compose configuration...';
      const dockerComposeSrc = path.join(TEMPLATES_DIR, 'common', 'docker-compose.yml');
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
        .replace(/{{DB_NAME}}/g, answers.dbName)
        .replace(/{{DB_USER}}/g, answers.dbUser)
        .replace(/{{DB_PASSWORD}}/g, answers.dbPassword)
        .replace(/{{API_PORT}}/g, answers.apiPort)
        .replace(/{{FRONTEND_PORT}}/g, answers.frontendPort);
      
      await fs.writeFile(envExampleDest, envContent);
      await fs.writeFile(envDest, envContent);

      spinner.text = 'Updating package.json configurations...';
      const packageJsonPath = path.join(frontendDest, 'package.json');
      if (fs.existsSync(packageJsonPath)) {
        const packageJson = await fs.readJson(packageJsonPath);
        packageJson.name = answers.projectName;
        packageJson.proxy = `http://localhost:${answers.apiPort}`;
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
        await fs.writeFile(path.join(projectPath, '.gitignore'), gitignoreContent);
      }
      
      spinner.text = 'Creating README...';
      const readmeContent = `# ${answers.projectName}

Full-stack application with FastAPI backend, React frontend (${answers.uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS'}), and PostgreSQL database.

## 🚀 Quick Start

1. Make sure Docker and Docker Compose are installed
2. Run the application:
   \`\`\`bash
   docker-compose up -d
   \`\`\`

## 📁 Project Structure

\`\`\`
${answers.projectName}/
├── backend/          # FastAPI backend
├── frontend/         # React frontend with ${answers.uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS'}
├── database/         # PostgreSQL initialization scripts
├── docker-compose.yml
└── .env             # Environment variables
\`\`\`

## 🔗 Access Points

- Frontend: http://localhost:${answers.frontendPort}
- Backend API: http://localhost:${answers.apiPort}
- API Documentation: http://localhost:${answers.apiPort}/docs

## 🛠️ Development

### Backend
\`\`\`bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port ${answers.apiPort}
\`\`\`

### Frontend
\`\`\`bash
cd frontend
npm install
npm start
\`\`\`

### Database
PostgreSQL is running in Docker container on port 5432.

## 📝 Environment Variables

Check \`.env.example\` for all available configuration options.
`;
      await fs.writeFile(path.join(projectPath, 'README.md'), readmeContent);

      // Initialize Git repository if requested
      if (answers.features && answers.features.includes('git')) {
        spinner.text = 'Initializing Git repository...';
        try {
          await execAsync('git init', { cwd: projectPath });
          await execAsync('git add .', { cwd: projectPath });
          await execAsync('git commit -m "Initial commit from StackWizard 🧙‍♂️"', { cwd: projectPath });
          spinner.text = 'Git repository initialized';
        } catch (gitError) {
          spinner.warn(chalk.yellow('Git initialization failed (git might not be installed)'));
        }
      }
      
      // Install dependencies if requested
      if (answers.features && answers.features.includes('install')) {
        spinner.text = 'Installing backend dependencies...';
        try {
          await execAsync('pip install -r requirements.txt', { cwd: path.join(projectPath, 'backend') });
        } catch (e) {
          spinner.warn(chalk.yellow('Backend dependencies installation skipped (Python/pip not available)'));
        }
        
        spinner.text = 'Installing frontend dependencies...';
        try {
          await execAsync('npm install', { cwd: path.join(projectPath, 'frontend') });
        } catch (e) {
          spinner.warn(chalk.yellow('Frontend dependencies installation skipped'));
        }
      }
      
      spinner.succeed(chalk.green.bold('✅ Project created successfully!'));
      
      // Display project summary
      console.log('\n' + chalk.cyan('📋 Project Summary:'));
      console.log(chalk.white(`  • Name: ${chalk.bold(answers.projectName)}`));
      console.log(chalk.white(`  • UI Library: ${chalk.bold(answers.uiLibrary === 'mui' ? 'Material UI' : 'Tailwind CSS')}`));
      console.log(chalk.white(`  • Database: ${chalk.bold('PostgreSQL')}`));
      console.log(chalk.white(`  • Backend Port: ${chalk.bold(answers.apiPort)}`));
      console.log(chalk.white(`  • Frontend Port: ${chalk.bold(answers.frontendPort)}`));
      
      if (answers.features && answers.features.length > 0) {
        console.log(chalk.white(`  • Features: ${chalk.bold(answers.features.join(', '))}`));
      }

      console.log('\n' + chalk.cyan.bold('🚀 Next steps:'));
      console.log(chalk.white(`  ${chalk.gray('$')} cd ${chalk.green(answers.projectName)}`));
      console.log(chalk.white(`  ${chalk.gray('$')} docker-compose up -d`));
      console.log(chalk.white(`  ${chalk.gray('$')} Open ${chalk.blue(`http://localhost:${answers.frontendPort}`)}\n`));
      
      console.log(chalk.cyan('📚 Documentation:'));
      console.log(chalk.white(`  • API Docs: ${chalk.blue(`http://localhost:${answers.apiPort}/docs`)}`));
      console.log(chalk.white(`  • README: ${chalk.gray(`${answers.projectName}/README.md`)}\n`));
      
      console.log(chalk.green.bold('Happy coding! 🎉'));

    } catch (error) {
      spinner.fail(chalk.red('Failed to create project'));
      console.error(error);
      process.exit(1);
    }
  });

program.parse(process.argv);