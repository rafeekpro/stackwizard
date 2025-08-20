# 🧙‍♂️ StackWizard CLI

> **Create production-ready full-stack applications in seconds!**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-16%2B-brightgreen?style=flat-square)](https://nodejs.org)
[![GitHub Stars](https://img.shields.io/github/stars/rafeekpro/stackwizard?style=flat-square)](https://github.com/rafeekpro/stackwizard/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/rafeekpro/stackwizard?style=flat-square)](https://github.com/rafeekpro/stackwizard/issues)

**StackWizard** is a powerful CLI tool that generates complete, production-ready full-stack applications with a single command. Get a fully configured project with **FastAPI** backend, **React** frontend, **PostgreSQL** database, and **Docker Compose** orchestration - all following industry best practices.

## ✨ Features

- 🚀 **FastAPI Backend** - Modern Python web API with async support, JWT authentication, and 100% type hints
- ⚛️ **React Frontend** - Choose between Material-UI or Tailwind CSS for your UI
- 🐘 **PostgreSQL Database** - Production-ready database with Alembic migrations
- 🐳 **Docker Compose** - Complete containerized development environment with health checks
- 🔐 **Authentication System** - JWT-based auth with secure password hashing
- 📚 **API Documentation** - Auto-generated Swagger/OpenAPI documentation
- 🧪 **Testing Setup** - Pre-configured test suites for both backend and frontend
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

### NPM Installation (Ready for Publishing)

Once published to NPM, you'll be able to install with:

```bash
# Global installation
npm install -g @rafeekpro/stackwizard

# Or use npx directly
npx @rafeekpro/stackwizard my-awesome-app
```

## 📋 Usage

### Interactive Mode (Recommended)

Simply run the command and follow the interactive prompts:

```bash
# From cloned repository
npm start

# Or after global installation (when published)
stackwizard
# OR with npx directly
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

## 📦 System Requirements

- Node.js 16.0.0 or higher
- npm 7.0.0 or higher
- Docker & Docker Compose (for running generated projects)
- Python 3.11+ (for local backend development)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/rafeekpro/stackwizard/blob/main/CONTRIBUTING.md) for details.

## 📄 License

MIT © [StackWizard Team](https://github.com/rafeekpro/stackwizard)

## 🙏 Acknowledgments

Built with love using:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library for building user interfaces
- [PostgreSQL](https://www.postgresql.org/) - Advanced open-source database
- [Docker](https://www.docker.com/) - Containerization platform

## 📞 Support

- 📧 **Email**: support@stackwizard.dev  
- 🐛 **Issues**: [GitHub Issues](https://github.com/rafeekpro/stackwizard/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/rafeekpro/stackwizard/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rafeekpro/stackwizard/discussions)
- 📦 **NPM Package**: [@rafeekpro/stackwizard](https://www.npmjs.com/package/@rafeekpro/stackwizard) *(Publishing Soon)*

---

<p align="center">
  Made with ❤️ by the <a href="https://github.com/rafeekpro">StackWizard Team</a>
</p>

