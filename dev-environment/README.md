# 🚀 StackWizard Development Environment

Complete development environment for StackWizard full-stack application with FastAPI, React, PostgreSQL, Redis, and development tools.

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Make (optional, for Makefile commands)

## 🎯 Quick Start

### 1. Clone and Setup

```bash
# Copy environment variables
cp .env.example .env

# Start all services
make start
# or
./scripts/dev.sh start
```

### 2. Access Services

After starting, services are available at:

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 🗄️ **Database Admin (Adminer)**: http://localhost:8080
- 📧 **Email Testing (MailHog)**: http://localhost:8025

## 🛠️ Development Workflow

### Daily Development

```bash
# Start services
make start

# Watch logs
make logs

# Open backend shell
make shell

# Open database shell
make shell-db
```

### Database Management

```bash
# Reset database to initial state
make db-reset

# Create backup
make db-backup

# Restore from latest backup
make db-restore

# Run migrations
make db-migrate

# Seed with test data
make db-seed
```

### Testing

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run E2E tests
make test-e2e
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check
```

## 📁 Project Structure

```
dev-environment/
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   ├── tests/            # Backend tests
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json      # Node dependencies
├── database/             # Database files
│   ├── init/             # Initialization scripts
│   └── backup/           # Database backups
├── scripts/              # Helper scripts
│   └── dev.sh           # Main development script
├── docker-compose.yml    # Service orchestration
├── Makefile             # Development commands
└── .env                 # Environment variables
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file to configure:

```bash
# Database
POSTGRES_USER=stackwizard
POSTGRES_PASSWORD=stackwizard123
POSTGRES_DB=stackwizard_dev

# Ports
API_PORT=8000
FRONTEND_PORT=3000
DB_PORT=5432
REDIS_PORT=6379
ADMINER_PORT=8080
MAILHOG_UI_PORT=8025
```

### VS Code Setup

The project includes VS Code configurations:

1. **Debugging**: Press `F5` to start debugging
2. **Tasks**: Use `Ctrl+Shift+B` to run build tasks
3. **Extensions**: Install recommended extensions

## 🐳 Docker Services

### Service Commands

```bash
# View all containers
docker-compose ps

# Restart specific service
docker-compose restart backend

# View service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
```

### Container Details

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| postgres | postgres:15-alpine | 5432 | PostgreSQL database |
| redis | redis:7-alpine | 6379 | Cache & sessions |
| backend | custom | 8000 | FastAPI application |
| frontend | custom | 3000 | React application |
| adminer | adminer:latest | 8080 | Database UI |
| mailhog | mailhog/mailhog | 8025 | Email testing |

## 🔄 Database Migration Workflow

### Creating Migrations

```bash
# Generate migration from models
docker-compose exec backend alembic revision --autogenerate -m "Add user table"

# Create empty migration
docker-compose exec backend alembic revision -m "Custom migration"
```

### Applying Migrations

```bash
# Upgrade to latest
make db-migrate

# Upgrade to specific revision
docker-compose exec backend alembic upgrade <revision>

# Downgrade one revision
docker-compose exec backend alembic downgrade -1
```

## 🧪 Testing Strategy

### Backend Testing

```bash
# Unit tests
docker-compose exec backend pytest tests/unit -v

# Integration tests
docker-compose exec backend pytest tests/integration -v

# With coverage
docker-compose exec backend pytest --cov=app tests/
```

### Frontend Testing

```bash
# Unit tests
docker-compose exec frontend npm test

# E2E tests with Cypress
docker-compose exec frontend npm run test:e2e
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Recreate database
make db-reset
```

#### Container Build Issues
```bash
# Rebuild containers
make rebuild

# Clean everything and start fresh
make clean
make build
make start
```

### Reset Everything

```bash
# Complete reset (WARNING: Deletes all data)
make clean
make build
make start
make db-reset
```

## 🔐 Security Notes

- Default credentials are for development only
- Never commit `.env` file with production credentials
- Use strong passwords in production
- Enable SSL/TLS for production deployments
- Regularly update dependencies

## 📊 Database Schema

The database is initialized with SQL files from `kedro-pipeline/data/01_raw/sql/`:

- **schema/**: Table definitions
- **seed/**: Development data
- **test/**: Test data

To modify the schema:
1. Edit SQL files in `kedro-pipeline/data/01_raw/sql/schema/`
2. Run `make db-reset` to apply changes

## 🎨 Frontend Development

### Hot Reload
Frontend automatically reloads on file changes.

### Component Development
```bash
# Create new component
cd frontend/src/components
touch MyComponent.jsx
```

### API Integration
API client is configured in `frontend/src/services/api.js`

## 🔌 Backend Development

### Hot Reload
Backend automatically reloads on file changes.

### Creating Endpoints
```python
# backend/app/api/endpoints/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def get_example():
    return {"message": "Hello World"}
```

### Database Models
```python
# backend/app/models/example.py
from sqlalchemy import Column, String
from app.db.base import Base

class Example(Base):
    __tablename__ = "examples"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
```

## 📈 Monitoring

### Health Checks
- Backend: http://localhost:8000/health
- Database: `make shell-db` then `\l`
- Redis: `make shell-redis` then `ping`

### Logs
```bash
# All services
make logs

# Specific service
make logs-backend
make logs-frontend
make logs-db
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `make test`
4. Format code: `make format`
5. Create pull request

## 📝 License

MIT License - See LICENSE file for details