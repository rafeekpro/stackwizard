# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains **StackWizard** - a magical full-stack project generator CLI that creates complete boilerplate applications with:
- **Backend**: FastAPI with SQLAlchemy ORM and PostgreSQL
- **Frontend**: React with configurable UI libraries (Material UI or Tailwind CSS)
- **DevOps**: Docker Compose for containerized development environment

## Architecture

The generator uses a template-based architecture:

```
project-generator-cli/
├── src/index.js                    # Main CLI application
├── templates/
│   ├── common/                     # Shared backend and Docker templates
│   │   ├── backend/               # Complete FastAPI application
│   │   ├── database/              # PostgreSQL initialization
│   │   ├── docker-compose.yml    # Container orchestration
│   │   └── .env.example          # Environment configuration
│   ├── frontend-mui/             # React + Material UI template
│   └── frontend-tailwind/        # React + Tailwind CSS template
```

### Backend Architecture (FastAPI)
- **Models**: SQLAlchemy models in `app/models/`
- **Schemas**: Pydantic schemas for validation in `app/schemas/`
- **API Routes**: RESTful endpoints in `app/api/`
- **CRUD Operations**: Database operations in `app/crud/`
- **Configuration**: Settings management in `app/core/config.py`

### Frontend Architecture
Both frontend variants follow similar patterns:
- **Components**: Reusable UI components
- **Pages**: Route-based page components
- **Services**: API client and utilities
- **Routing**: React Router for SPA navigation

## Development Commands

### Running the Generator
```bash
# Navigate to the generator directory
cd project-generator-cli

# Install dependencies
npm install

# Run the generator
npm start
# or
node src/index.js

# Install globally for system-wide use
npm install -g .
stackwizard
```

### Generated Project Commands
The generated projects include these common commands:

#### Full Stack (Docker Compose)
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

#### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

## Template Customization

### Adding New Frontend Templates
1. Create new template directory: `templates/frontend-{name}/`
2. Include complete React project structure
3. Update CLI script to include new option in inquirer prompts
4. Ensure consistent API service integration

### Modifying Backend Template
- Backend template is in `templates/common/backend/`
- Follows FastAPI best practices with separation of concerns
- Uses SQLAlchemy for database operations
- Includes health check endpoints and CORS configuration

### Environment Configuration
Templates use placeholder variables replaced during generation:
- `{{PROJECT_NAME}}` - User-provided project name
- `{{DB_NAME}}`, `{{DB_USER}}`, `{{DB_PASSWORD}}` - Database configuration
- `{{API_PORT}}`, `{{FRONTEND_PORT}}` - Service ports

## Key Features

### Interactive CLI
- Project name validation (lowercase, numbers, hyphens only)
- UI library selection (Material UI or Tailwind CSS)
- Database and port configuration
- Automatic environment file generation

### Generated Project Features
- **Health Monitoring**: API and database health check endpoints
- **CRUD Examples**: Complete User and Item management
- **Docker Support**: Multi-service development environment
- **API Documentation**: Automatic Swagger/OpenAPI docs at `/docs`
- **Responsive UI**: Mobile-first design in both UI variants
- **Error Handling**: Comprehensive error handling and validation

## Testing Generated Projects

After generation, verify the project works:

1. **Start services**: `docker compose up -d`
2. **Check health**: Visit frontend URL and verify API/DB status
3. **Test CRUD**: Create, read, update, delete users and items
4. **API docs**: Visit `/api/docs` for interactive API testing

## Common Issues

- **Port conflicts**: Ensure configured ports are available
- **Docker issues**: Verify Docker and Docker Compose are installed
- **Database connection**: Check PostgreSQL container startup and credentials
- **CORS errors**: Frontend and backend must be properly configured for cross-origin requests

## 🚨 CRITICAL DEVELOPMENT RULES

### 1. Version Control & Branching
- **ALWAYS CREATE NEW BRANCH**: Create one feature/fix branch for each issue or feature
  - Use descriptive names: `feat/feature-name`, `fix/bug-description`, `docs/update-xyz`
  - Never commit directly to `main` branch
  - Create PR for review before merging

### 2. Test-Driven Development (TDD)
- **WRITE TESTS FIRST**: Follow TDD methodology
  1. Write failing test that defines desired improvement
  2. Write minimal code to make test pass
  3. Refactor while keeping tests green
- **TEST CATEGORIES**:
  - Unit tests for individual functions/components
  - Integration tests for feature workflows
  - E2E tests for critical user paths
  - Docker tests for deployment verification

### 3. Testing Requirements
- **BEFORE EVERY COMMIT**: Run all relevant tests
  ```bash
  npm run test:package    # Verify npm package integrity
  npm run test:structure  # Verify generated project structure
  npm run test:docker     # If Docker files changed
  ```
- **BEFORE RELEASE**: Run full test suite
  ```bash
  npm run test:all
  ```
- **CI/CD COMPLIANCE**: Ensure all required checks pass in PR

### 4. CHANGELOG Management
- **ALWAYS UPDATE CHANGELOG.md** for:
  - New features (### ✨ New Features)
  - Bug fixes (### 🐛 Bug Fixes)
  - Breaking changes (### ⚠️ BREAKING CHANGES)
  - Performance improvements (### ⚡ Performance)
  - Documentation updates (### 📚 Documentation)
- **FORMAT**: Follow Keep a Changelog format
- **LOCATION**: Add changes to `[Unreleased]` section
- **VERSIONING**: Follow Semantic Versioning (MAJOR.MINOR.PATCH)

### 5. Code Quality Standards
- **LINTING**: Code must pass ESLint checks
  ```bash
  npm run lint
  ```
- **FORMATTING**: Use Prettier for consistent formatting
  ```bash
  npm run format
  ```
- **TYPE SAFETY**: Use PropTypes or TypeScript where applicable
- **ERROR HANDLING**: Always handle errors gracefully with user-friendly messages

### 6. Docker & Deployment
- **TEST LOCALLY**: Always test Docker Compose locally before committing
  ```bash
  docker compose up -d
  docker compose logs -f
  ```
- **VERIFY HEALTH**: Check all services are healthy
  ```bash
  curl http://localhost:8000/health
  curl http://localhost:3000
  ```
- **CLEANUP**: Always provide cleanup instructions

### 7. Documentation
- **CODE COMMENTS**: Comment complex logic, not obvious code
- **README UPDATES**: Update README.md when adding features
- **API DOCS**: Keep OpenAPI/Swagger docs updated
- **MIGRATION GUIDES**: Document breaking changes with migration steps

### 8. Security Best Practices
- **NO SECRETS IN CODE**: Never commit passwords, API keys, or tokens
- **USE ENV VARIABLES**: All configuration through environment variables
- **VALIDATE INPUT**: Always validate and sanitize user input
- **DEPENDENCY UPDATES**: Regularly update dependencies for security patches

### 9. Performance Considerations
- **OPTIMIZE CI/CD**: Use conditional workflows to reduce CI time
- **LAZY LOADING**: Implement code splitting in frontend
- **DATABASE INDEXES**: Add appropriate indexes for queries
- **CACHING**: Implement caching where appropriate

### 10. Release Process
1. **Create Release Branch**: `release/vX.Y.Z`
2. **Update Version**: In `package.json`
3. **Update CHANGELOG**: Move unreleased items to new version section
4. **Run Full Tests**: `npm run test:all`
5. **Create PR**: For review
6. **Merge & Tag**: After approval
7. **Publish to NPM**: `npm publish`

### 11. Version Bumping Rules
**ALWAYS update version when merging to main:**
- **PATCH (x.x.+1)**: Bug fixes, dependency updates, minor improvements
  - Any bug fix merged to main
  - Dependency security updates
  - Documentation fixes that affect functionality
  - Template fixes (Docker, config, etc.)
  
- **MINOR (x.+1.0)**: New features, enhancements
  - New CLI features or options
  - New template features
  - Significant improvements to existing features
  - Non-breaking API changes
  
- **MAJOR (+1.0.0)**: Breaking changes
  - Changes to CLI interface that break existing usage
  - Template structure changes that affect existing projects
  - Removal of features or options
  - Changes requiring user migration

**Version bump NOT required for:**
- Documentation-only changes (README, comments) unless significant
- Dev dependency updates that don't affect build/output
- CI/CD workflow changes
- Test-only changes

**Important:** Every PR that affects users MUST include a version bump

## 🎯 GOLDEN RULES

1. **If it's not tested, it's broken**
2. **If it's not in CHANGELOG, it didn't happen**
3. **If it's not documented, it doesn't exist**
4. **If tests don't pass, don't merge**
5. **If Docker doesn't work, users can't use it**

## 📋 PR Checklist

Before creating a Pull Request, ensure:
- [ ] Tests written and passing
- [ ] CHANGELOG.md updated
- [ ] Documentation updated if needed
- [ ] Lint and format checks pass
- [ ] Docker Compose tested locally
- [ ] No hardcoded secrets or credentials
- [ ] Branch follows naming convention
- [ ] PR description explains what and why