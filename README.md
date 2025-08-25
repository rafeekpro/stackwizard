# 🧙‍♂️ StackWizard CLI

> **Create production-ready full-stack applications in seconds!**

[![npm version](https://img.shields.io/npm/v/@rafeekpro/stackwizard.svg?style=flat-square)](https://www.npmjs.com/package/@rafeekpro/stackwizard)
[![npm downloads](https://img.shields.io/npm/dm/@rafeekpro/stackwizard.svg?style=flat-square)](https://www.npmjs.com/package/@rafeekpro/stackwizard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-16%2B-brightgreen?style=flat-square)](https://nodejs.org)
[![GitHub Stars](https://img.shields.io/github/stars/rafeekpro/stackwizard?style=flat-square)](https://github.com/rafeekpro/stackwizard/stargazers)

**StackWizard** is a powerful CLI tool that generates complete, production-ready full-stack applications with a single command. Get a fully configured project with **FastAPI** backend, **React** frontend, **PostgreSQL** database, and **Docker Compose** orchestration - all following industry best practices.

## ✨ Features

### Core Stack
- 🚀 **FastAPI Backend** - Modern Python web API with async support, JWT authentication, and 100% type hints
- ⚛️ **React Frontend** - Choose between Material-UI or Tailwind CSS for your UI
- 🐘 **PostgreSQL Database** - Production-ready database with Alembic migrations
- 🐳 **Docker Compose** - Complete containerized development environment with health checks

### Security & Architecture
- 🔐 **Authentication System** - JWT-based auth with secure password hashing & refresh tokens
- 🛡️ **Security Middleware** - Rate limiting, CSRF protection, security headers
- 🏗️ **Service Layer Architecture** - Clean separation with Service/Repository patterns
- 📚 **API Documentation** - Auto-generated Swagger/OpenAPI documentation

### Developer Experience
- 🧪 **Comprehensive Testing** - Cypress E2E tests, unit tests, Docker validation
- 🎭 **Visual Testing** - Watch Cypress tests run in real-time
- 🛠️ **Pre-Push Validation** - Automatic Docker & dependency verification
- 📊 **Test Orchestration** - Makefile & custom orchestrator for test management
- 🎯 **Best Practices** - Clean architecture, type safety, and production-ready configuration

## 🚀 Quick Start

### From GitHub (Current Method)

Clone and run directly:

```bash
# Clone the repository
git clone https://github.com/rafeekpro/stackwizard.git
cd stackwizard
npm install

# Run the generator
npm start
# or
node src/index.js
```

### NPM Installation ✅

Install from NPM registry:

```bash
# Global installation
npm install -g @rafeekpro/stackwizard

# Or use npx directly
npx @rafeekpro/stackwizard my-awesome-app
```

### GitHub Packages (Alternative)

Install from GitHub Packages registry:

```bash
# Configure npm to use GitHub registry for @rafeekpro scope
npm config set @rafeekpro:registry https://npm.pkg.github.com

# Install globally
npm install -g @rafeekpro/stackwizard
```

> **Note**: Both NPM and GitHub Packages are now live with version 1.0.0!

## 📋 Usage

### Interactive Mode (Recommended)

Simply run the command and follow the interactive prompts:

```bash
# From cloned repository
npm start

# Or after global installation
stackwizard

# Or use npx directly (no installation needed!)
npx @rafeekpro/stackwizard
```

You'll be asked to configure:
- 📝 Project name
- 🎨 UI library (Material-UI or Tailwind CSS)
- 🗄️ Database configuration
- 🔌 Port settings
- ✅ Additional features (Git initialization, dependency installation)

### Command Line Mode

Skip the prompts with command-line options:

```bash
node src/index.js --name my-app --ui mui --skip-git
```

#### Available Options

```
Options:
  -V, --version     Output version number
  -n, --name <name> Project name
  -u, --ui <ui>     UI library (mui or tailwind)
  -s, --skip-git    Skip git initialization
  -i, --install     Install dependencies after creation
  -q, --quick       Quick mode - use all defaults
  -h, --help        Display help
```

### Quick Mode

Generate a project with all defaults in seconds:

```bash
node src/index.js --quick --name my-app
```

## 🏗️ Generated Project Structure

```
your-project/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration & security
│   │   ├── crud/        # Database operations
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── main.py      # Application entry point
│   ├── alembic/         # Database migrations
│   ├── tests/           # Backend tests
│   └── Dockerfile       # Production-ready Dockerfile
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API service layer
│   │   └── App.js       # Main application component
│   ├── public/          # Static assets
│   └── Dockerfile       # Production-ready Dockerfile
├── database/            # Database initialization
├── docker-compose.yml   # Docker orchestration
├── .env                 # Environment configuration
└── README.md           # Project documentation
```

## 🎯 What You Get

### Backend (FastAPI)
- ✅ RESTful API with async/await support
- ✅ SQLAlchemy ORM with Alembic migrations
- ✅ JWT authentication & authorization
- ✅ Request validation with Pydantic
- ✅ CORS configuration
- ✅ Health check endpoints
- ✅ Comprehensive error handling
- ✅ 100% type hints for better IDE support

### Frontend (React)
- ✅ Modern React with Hooks
- ✅ React Router for navigation
- ✅ Axios with request/response interceptors
- ✅ Authentication context & protected routes
- ✅ Responsive design
- ✅ Material-UI or Tailwind CSS styling
- ✅ Environment-based configuration

### Database (PostgreSQL)
- ✅ PostgreSQL 15 with optimal settings
- ✅ Database migrations with Alembic
- ✅ Connection pooling
- ✅ Automated backup support
- ✅ Health monitoring

### DevOps (Docker)
- ✅ Multi-stage Dockerfiles for optimal image size
- ✅ Docker Compose with health checks
- ✅ Hot-reload for development
- ✅ Production-ready configuration
- ✅ Optional Redis & Nginx services

## 🚀 Running Your Generated Project

After generation, start your full-stack application with:

```bash
cd your-project
docker-compose up -d
```

Your application will be available at:
- 🌐 **Frontend**: http://localhost:3000
- 🚀 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

## 🛠️ Development Workflow

### Complete Development Environment (New!)
Full-featured development environment with hot-reload, database management, and debugging tools:

```bash
# Navigate to dev environment
cd dev-environment

# Setup environment
cp .env.example .env

# Start all services (PostgreSQL, Redis, FastAPI, React, Adminer, MailHog)
make start
# or
./scripts/dev.sh start

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Database Admin: http://localhost:8080
# Email Testing: http://localhost:8025

# Database management
make db-reset     # Reset to clean state with SQL files
make db-backup    # Create backup
make db-restore   # Restore from backup
make db-seed      # Load test data

# Development commands
make logs         # View all logs
make shell        # Backend shell
make shell-db     # PostgreSQL shell
make test         # Run all tests
```

### Without Docker

**Backend Development:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend Development:**
```bash
cd frontend
npm install
npm start
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🧪 Testing & Validation

### Kedro Test Pipeline (New!)
Advanced test orchestration with visual pipeline monitoring:

```bash
# Run specific test suites
npm run test:kedro:package    # Test npm package integrity
npm run test:kedro:structure  # Test project structure generation
npm run test:kedro:docker     # Test Docker configuration
npm run test:kedro:e2e        # Run end-to-end tests
npm run test:kedro:all        # Run complete test suite

# Database testing with SQL files
npm run test:kedro:db         # Initialize test database from SQL
npm run test:kedro:db:cleanup # Clean up test database
npm run test:kedro:db:full    # Full database test cycle

# Visual pipeline monitoring
kedro viz run                  # Open at http://127.0.0.1:4141/
```

### Visual Testing with Cypress
Watch your tests run in real-time:

```bash
# Install Cypress
make cypress-install

# Test MUI template visually
make cypress-mui

# Test Tailwind template visually
make cypress-tailwind
```

### Pre-Push Validation
Ensure everything works before pushing to GitHub:

```bash
# Full validation (recommended)
npm run validate:full

# Quick validation
npm run validate:quick

# Install git hooks for automatic validation
npm run install-hooks
```

### Test Orchestration
Run comprehensive tests with a single command:

```bash
# Using Makefile
make test-all        # Run all tests
make pre-commit      # Pre-commit checks
make docker-build-test  # Test Docker builds

# Using orchestrator
npm run test:orchestrate       # Smart mode
npm run test:orchestrate:full  # Full test suite
```

## 📁 Project Structure

```
project-generator-cli/
├── src/                        # Generator source code
│   └── index.js               # Main CLI application
├── templates/                  # Project templates
│   ├── common/                # Shared templates
│   │   ├── backend/          # FastAPI backend template
│   │   ├── database/         # PostgreSQL initialization
│   │   └── docker-compose.yml # Docker orchestration
│   ├── frontend-mui/          # Material UI template
│   └── frontend-tailwind/     # Tailwind CSS template
├── kedro-pipeline/            # Test orchestration (NEW!)
│   ├── src/                  # Pipeline implementation
│   │   └── stackwizard_pipeline/
│   │       ├── nodes/        # Test functions
│   │       └── pipelines/    # Test workflows
│   ├── data/                 # Test data and results
│   │   └── 01_raw/sql/      # SQL initialization files
│   │       ├── schema/      # Database schema
│   │       ├── seed/        # Development data
│   │       └── test/        # Test data
│   └── conf/                 # Pipeline configuration
├── dev-environment/           # Development environment (NEW!)
│   ├── backend/              # FastAPI development
│   ├── frontend/             # React development
│   ├── database/             # Database management
│   ├── scripts/              # Helper scripts
│   │   └── dev.sh           # Development CLI
│   ├── docker-compose.yml    # Service orchestration
│   └── Makefile             # Quick commands
└── test/                      # Legacy test files

```

## 📦 System Requirements

- Node.js 16.0.0 or higher
- npm 7.0.0 or higher
- Docker & Docker Compose (for running generated projects)
- Python 3.11+ (for local backend development)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and request features via [GitHub Issues](https://github.com/rafeekpro/stackwizard/issues)
- Submit pull requests with improvements
- Share feedback and suggestions

## 📄 License

MIT © [Rafał Łagowski](https://github.com/rafeekpro)

## 👨‍💻 Author

**Rafał Łagowski** - Full-Stack Developer
- GitHub: [@rafeekpro](https://github.com/rafeekpro)
- NPM: [@rafeekpro](https://www.npmjs.com/~rafeekpro)

## 🙏 Technologies Used

This project leverages modern, production-ready technologies:
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework
- [React](https://reactjs.org/) - Component-based UI library
- [PostgreSQL](https://www.postgresql.org/) - Enterprise-grade database
- [Docker](https://www.docker.com/) - Container orchestration
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
- [Material-UI](https://mui.com/) - React component library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## 📚 Documentation

- **[TESTING.md](./TESTING.md)** - Complete testing guide with Kedro pipelines
- **[SCRIPTS.md](./SCRIPTS.md)** - NPM scripts reference
- **[CLAUDE.md](./CLAUDE.md)** - Development guidelines for AI assistants
- **[dev-environment/README.md](./dev-environment/README.md)** - Development environment setup

## 📞 Contact & Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rafeekpro/stackwizard/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/rafeekpro/stackwizard/discussions)
- 📦 **NPM Package**: [@rafeekpro/stackwizard](https://www.npmjs.com/package/@rafeekpro/stackwizard)
- 📦 **GitHub Package**: [@rafeekpro/stackwizard](https://github.com/users/rafeekpro/packages/npm/package/stackwizard)
- 👤 **Developer**: [Rafał Łagowski](https://github.com/rafeekpro)

---

<p align="center">
  <strong>Created with ❤️ by <a href="https://github.com/rafeekpro">Rafał Łagowski</a></strong><br>
  <em>Full-Stack Developer | Open Source Contributor</em><br><br>
  <a href="https://www.npmjs.com/package/@rafeekpro/stackwizard">NPM</a> • 
  <a href="https://github.com/rafeekpro/stackwizard">GitHub</a> • 
  <a href="https://github.com/rafeekpro">Profile</a>
</p>

