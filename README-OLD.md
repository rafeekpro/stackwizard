# 🧙‍♂️ StackWizard CLI

> Magical full-stack project generator with FastAPI, React, PostgreSQL, and Docker

[![npm version](https://img.shields.io/npm/v/stackwizard-cli.svg)](https://www.npmjs.com/package/stackwizard-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Create production-ready full-stack applications with a single command! StackWizard generates a complete project structure with FastAPI backend, React frontend (Material-UI or Tailwind CSS), PostgreSQL database, and Docker Compose configuration.

## ✨ Features

- **🚀 FastAPI Backend** - Modern Python web API with async support
- **⚛️ React Frontend** - Choice of Material-UI or Tailwind CSS
- **🐘 PostgreSQL Database** - Production-ready database with migrations
- **🐳 Docker Compose** - Complete containerized development environment
- **🔐 Authentication** - JWT-based auth system built-in
- **📚 API Documentation** - Auto-generated Swagger/OpenAPI docs
- **🧪 Testing** - Pre-configured test suites for both backend and frontend
- **🎨 UI Libraries** - Choose between Material-UI or Tailwind CSS

## 📦 Installation

### Using npx (recommended)

No installation needed! Just run:

```bash
npx stackwizard-cli
```

### Global Installation

```bash
npm install -g stackwizard-cli
```

Then run:

```bash
stackwizard
```

## 🚀 Quick Start

### Interactive Mode (Recommended)

```bash
npx stackwizard-cli
```

Follow the interactive prompts to configure your project:
- Project name
- UI library (Material-UI or Tailwind CSS)
- Database configuration
- Port settings
- Additional features (Git, dependencies installation, etc.)

### Command Line Mode

```bash
npx stackwizard-cli --name my-app --ui mui
```

### Available Options

```bash
Options:
  -V, --version     output the version number
  -n, --name <name> project name
  -u, --ui <ui>     UI library (mui or tailwind)
  -s, --skip-git    skip git initialization
  -i, --install     install dependencies after creation
  -h, --help        display help for command
```

## 📁 Generated Project Structure

```
your-project/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration
│   │   ├── crud/        # Database operations
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── main.py      # Application entry point
│   ├── tests/           # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── context/     # React context
│   │   └── App.js       # Main app component
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── database/            # Database initialization
│   └── init.sql
├── docker-compose.yml   # Container orchestration
├── .env                 # Environment variables
└── README.md           # Project documentation
```

## 🎯 Features in Generated Projects

### Backend (FastAPI)
- ✅ RESTful API with async/await
- ✅ SQLAlchemy ORM with Alembic migrations
- ✅ JWT authentication
- ✅ CORS configuration
- ✅ Pydantic validation
- ✅ Auto-generated API documentation
- ✅ Health check endpoints
- ✅ 100% test coverage setup

### Frontend (React)
- ✅ Modern React with hooks
- ✅ React Router for navigation
- ✅ Axios for API calls with interceptors
- ✅ Authentication context
- ✅ Protected routes
- ✅ Responsive design
- ✅ Material-UI or Tailwind CSS styling

### Database (PostgreSQL)
- ✅ PostgreSQL 15
- ✅ Database migrations
- ✅ Connection pooling
- ✅ Automated initialization

### DevOps (Docker)
- ✅ Multi-stage Dockerfiles
- ✅ Docker Compose for local development
- ✅ Hot-reload for development
- ✅ Environment variable configuration

## 🛠️ Development Workflow

After generating your project:

### 1. Start with Docker Compose

```bash
cd your-project
docker-compose up -d
```

This starts:
- Backend API at http://localhost:8000
- Frontend at http://localhost:3000
- PostgreSQL database at localhost:5432
- API docs at http://localhost:8000/docs

### 2. Development without Docker

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Environment Variables

Generated projects include a `.env` file with:

```env
# Database
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Backend
API_PORT=8000
SECRET_KEY=your-secret-key

# Frontend
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:8000
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing Python web framework
- React team for the fantastic frontend library
- Docker for containerization
- All contributors and users of StackWizard

## 📞 Support

- 📧 Email: support@stackwizard.dev
- 🐛 Issues: [GitHub Issues](https://github.com/rafeekpro/stackwizard/issues)
- 📖 Docs: [Documentation](https://github.com/rafeekpro/stackwizard/wiki)

---

Made with ❤️ by the StackWizard Team

**Happy coding! 🎉**