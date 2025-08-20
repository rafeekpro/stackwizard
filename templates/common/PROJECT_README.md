# {{PROJECT_NAME}}

Full-stack application built with **FastAPI**, **React** ({{UI_LIBRARY}}), and **PostgreSQL**.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
# Clone the repository (if applicable)
git clone <your-repo-url>
cd {{PROJECT_NAME}}

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access the Application

- 🌐 **Frontend**: http://localhost:{{FRONTEND_PORT}}
- 🚀 **Backend API**: http://localhost:{{API_PORT}}
- 📚 **API Documentation**: http://localhost:{{API_PORT}}/docs
- 🔧 **Alternative API Docs**: http://localhost:{{API_PORT}}/redoc

## 📁 Project Structure

```
{{PROJECT_NAME}}/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── v1/         # API version 1
│   │   ├── core/           # Core configuration & security
│   │   ├── crud/           # CRUD operations
│   │   ├── db/             # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   └── main.py         # FastAPI application entry
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service layer
│   │   ├── context/        # React Context providers
│   │   ├── hooks/          # Custom React hooks
│   │   ├── utils/          # Utility functions
│   │   └── App.js          # Main App component
│   ├── public/             # Static files
│   ├── package.json        # Node dependencies
│   └── Dockerfile
├── database/               # Database initialization
│   └── init.sql           # Initial database setup
├── nginx/                  # Nginx configuration (optional)
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Development

### Backend Development

#### Local Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port {{API_PORT}}
```

#### Database Migrations (Alembic)

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Development

#### Local Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

#### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

### Database Management

#### Access PostgreSQL
```bash
# Via Docker
docker-compose exec db psql -U {{DB_USER}} -d {{DB_NAME}}

# Direct connection
psql -h localhost -p 5432 -U {{DB_USER}} -d {{DB_NAME}}
```

#### Common Database Commands
```sql
-- List all tables
\dt

-- Describe table structure
\d table_name

-- View all users
SELECT * FROM users;

-- Check database size
SELECT pg_database_size('{{DB_NAME}}');
```

#### Backup & Restore
```bash
# Backup database
docker-compose exec db pg_dump -U {{DB_USER}} {{DB_NAME}} > backup.sql

# Restore database
docker-compose exec -T db psql -U {{DB_USER}} {{DB_NAME}} < backup.sql
```

## 🔑 Authentication & Security

### Default Credentials
- **Admin Email**: admin@example.com
- **Admin Password**: ChangeMeNow123!

⚠️ **Important**: Change these credentials immediately after first login!

### JWT Authentication
The API uses JWT tokens for authentication:
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Tokens are stored in httpOnly cookies (frontend)

### API Authentication
```bash
# Login
curl -X POST http://localhost:{{API_PORT}}/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "ChangeMeNow123!"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:{{API_PORT}}/api/v1/users/me
```

## 🧪 Testing

### Backend Tests
```bash
# Run in Docker
docker-compose exec backend pytest

# Run locally
cd backend && pytest

# With coverage
pytest --cov=app --cov-report=term-missing
```

### Frontend Tests
```bash
# Run in Docker
docker-compose exec frontend npm test

# Run locally
cd frontend && npm test

# With coverage
npm test -- --coverage --watchAll=false
```

### Integration Tests
```bash
# Run full test suite
./scripts/run-tests.sh

# Test specific service
docker-compose run --rm backend pytest tests/integration/
```

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks
- Backend: http://localhost:{{API_PORT}}/health
- Frontend: http://localhost:{{FRONTEND_PORT}}/
- Database: `docker-compose exec db pg_isready`

## 🚀 Deployment

### Production Checklist
- [ ] Change all default passwords
- [ ] Update SECRET_KEY in .env
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure email service
- [ ] Set up backup strategy
- [ ] Configure monitoring
- [ ] Review security settings
- [ ] Optimize Docker images

### Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
See `.env.example` for all available configuration options.

Key variables to configure for production:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRET_KEY` - Generate a secure random key
- `DATABASE_URL` - Production database
- `BACKEND_CORS_ORIGINS` - Allowed origins
- Email configuration (SMTP settings)

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :{{API_PORT}}
lsof -i :{{FRONTEND_PORT}}

# Kill process
kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### Clear Docker Resources
```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: Deletes data)
docker-compose down -v

# Clean Docker system
docker system prune -a
```

#### Reset Database
```bash
# Drop and recreate database
docker-compose exec db psql -U postgres -c "DROP DATABASE {{DB_NAME}};"
docker-compose exec db psql -U postgres -c "CREATE DATABASE {{DB_NAME}};"

# Run migrations
docker-compose exec backend alembic upgrade head
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:{{API_PORT}}/docs
- **ReDoc**: http://localhost:{{API_PORT}}/redoc

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/password-recovery` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password

#### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/` - List users (admin)
- `GET /api/v1/users/{id}` - Get user by ID (admin)
- `POST /api/v1/users/` - Create user (admin)
- `PUT /api/v1/users/{id}` - Update user (admin)
- `DELETE /api/v1/users/{id}` - Delete user (admin)

#### Health
- `GET /health` - Application health check
- `GET /health/db` - Database health check

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write tests for new features
- Update documentation
- Use conventional commits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [StackWizard CLI](https://github.com/rafeekpro/stackwizard)

---

Generated with ❤️ by [StackWizard](https://github.com/rafeekpro/stackwizard)