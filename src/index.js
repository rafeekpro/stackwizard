#!/usr/bin/env node

import { program } from 'commander';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');

program
  .version('1.0.0')
  .description('🧙‍♂️ StackWizard - Magical full-stack project generator with FastAPI, React, and PostgreSQL')
  .action(async () => {
    console.log(chalk.cyan.bold('\n🧙‍♂️ StackWizard - Full-Stack Project Generator\n'));
    
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'projectName',
        message: 'What is your project name?',
        default: 'my-fullstack-app',
        validate: (input) => {
          if (/^[a-z0-9-]+$/.test(input)) return true;
          return 'Project name should contain only lowercase letters, numbers, and hyphens';
        }
      },
      {
        type: 'list',
        name: 'uiLibrary',
        message: 'Choose your UI library for React frontend:',
        choices: [
          { name: '🎨 Material UI', value: 'mui' },
          { name: '🎯 Tailwind CSS', value: 'tailwind' }
        ]
      },
      {
        type: 'input',
        name: 'dbName',
        message: 'Database name:',
        default: (answers) => answers.projectName.replace(/-/g, '_')
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
        default: 'postgres'
      },
      {
        type: 'input',
        name: 'apiPort',
        message: 'Backend API port:',
        default: '8000'
      },
      {
        type: 'input',
        name: 'frontendPort',
        message: 'Frontend port:',
        default: '3000'
      }
    ]);

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

      spinner.succeed(chalk.green('✅ Project created successfully!'));

      console.log('\n' + chalk.cyan.bold('Next steps:'));
      console.log(chalk.white(`  1. cd ${answers.projectName}`));
      console.log(chalk.white('  2. docker-compose up -d'));
      console.log(chalk.white(`  3. Open http://localhost:${answers.frontendPort}\n`));

    } catch (error) {
      spinner.fail(chalk.red('Failed to create project'));
      console.error(error);
      process.exit(1);
    }
  });

program.parse(process.argv);