# 🧪 StackWizard Testing Documentation

Comprehensive guide to testing infrastructure, pipelines, and development environment.

## 📋 Table of Contents
- [Testing Overview](#testing-overview)
- [Kedro Test Pipeline](#kedro-test-pipeline)
- [Database Testing](#database-testing)
- [Development Environment](#development-environment)
- [Legacy Testing](#legacy-testing)
- [CI/CD Integration](#cicd-integration)

## Testing Overview

StackWizard uses multiple testing strategies to ensure quality:

1. **Kedro Pipeline Tests** - Orchestrated test workflows with visual monitoring
2. **Database Tests** - SQL-based database initialization and validation
3. **Docker Tests** - Container and orchestration validation
4. **E2E Tests** - End-to-end application testing
5. **Unit Tests** - Component-level testing

## 🚀 Kedro Test Pipeline

### Installation

```bash
# Install Kedro (one-time setup)
pipx install kedro
pipx inject kedro kedro-viz kedro-datasets psycopg2-binary

# Verify installation
kedro --version
```

### Running Tests

```bash
# Individual test suites
npm run test:kedro:package    # Test NPM package integrity
npm run test:kedro:structure  # Test project structure generation
npm run test:kedro:docker     # Test Docker configuration
npm run test:kedro:e2e        # Run end-to-end tests
npm run test:kedro:all        # Run complete test suite
```

### Visual Pipeline Monitoring

```bash
# Start Kedro-Viz
kedro viz run

# Open browser at http://127.0.0.1:4141/
# Select pipeline from dropdown (test:package, test:docker, etc.)
```

### Pipeline Structure

```
kedro-pipeline/
├── src/stackwizard_pipeline/
│   ├── nodes/                 # Test implementation
│   │   ├── package_tests.py   # NPM package validation
│   │   ├── structure_tests.py # Project structure tests
│   │   ├── docker_tests.py    # Docker configuration tests
│   │   ├── e2e_tests.py       # End-to-end tests
│   │   └── database_init.py   # Database initialization
│   └── pipelines/
│       ├── test_pipeline.py   # Test orchestration
│       └── database_pipeline.py # Database workflows
├── data/
│   ├── 01_raw/sql/           # SQL source files
│   ├── 02_intermediate/       # Test results
│   └── 03_primary/           # Final reports
└── conf/
    └── base/
        ├── parameters.yml     # Test configuration
        └── catalog.yml        # Data definitions
```

### Test Results

Results are stored in JSON format:
- `data/02_intermediate/` - Individual test results
- `data/03_primary/final_test_report.json` - Aggregated report
- `data/08_reporting/last_run_summary.json` - Latest run summary

## 💾 Database Testing

### SQL-Based Initialization

Database tests use SQL files for reproducible initialization:

```
kedro-pipeline/data/01_raw/sql/
├── schema/              # Table definitions
│   ├── 001_create_users.sql
│   ├── 002_create_items.sql
│   └── 003_create_sessions.sql
├── seed/               # Development data
│   ├── 001_seed_users.sql
│   └── 002_seed_items.sql
└── test/               # Test-specific data
    ├── 001_test_users.sql
    └── 002_test_items.sql
```

### Running Database Tests

```bash
# Initialize test database
npm run test:kedro:db

# Clean up test database
npm run test:kedro:db:cleanup

# Full cycle (init + cleanup)
npm run test:kedro:db:full
```

### Database Configuration

Edit `kedro-pipeline/conf/base/parameters.yml`:

```yaml
database:
  host: "localhost"
  port: 5432
  admin_user: "your_username"
  admin_password: ""
  test_db_name: "stackwizard_test"
  test_user: "stackwizard_user"
  test_password: "stackwizard_pass"
  clean_start: true
  cleanup_after_test: false

sql_path: "data/01_raw/sql"
data_type: "seed"  # "seed" or "test"
```

## 🐳 Development Environment

### Quick Start

```bash
# Navigate to dev environment
cd dev-environment

# Copy environment configuration
cp .env.example .env

# Start all services
make start
# or
./scripts/dev.sh start

# View service URLs
make urls
```

### Available Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React application |
| Backend API | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Adminer | http://localhost:8080 | Database management UI |
| MailHog | http://localhost:8025 | Email testing interface |
| PostgreSQL | localhost:5432 | Database server |
| Redis | localhost:6379 | Cache/session store |

### Database Management

```bash
# Reset database to initial state
make db-reset

# Create database backup
make db-backup

# Restore from latest backup
make db-restore

# Run migrations
make db-migrate

# Load seed data
make db-seed
```

### Development Workflow

```bash
# View logs
make logs           # All services
make logs-backend   # Backend only
make logs-frontend  # Frontend only

# Shell access
make shell          # Backend shell
make shell-db       # PostgreSQL shell
make shell-frontend # Frontend shell

# Testing
make test           # Run all tests
make test-backend   # Backend tests only
make test-frontend  # Frontend tests only

# Code quality
make format         # Format code
make lint           # Run linters
make type-check     # Type checking
```

### VS Code Integration

The dev environment includes VS Code configurations:

1. **Debugging**: Press `F5` to start debugging
2. **Compound debugging**: Debug backend and frontend simultaneously
3. **Tasks**: Use `Ctrl+Shift+B` for build tasks
4. **Extensions**: Install recommended extensions

Configuration files:
- `.vscode/settings.json` - Editor settings
- `.vscode/launch.json` - Debug configurations

## 🔧 Legacy Testing

### JavaScript Test Files

Original test files in `test/` directory:

```bash
# Run individual tests
npm run test:package    # Package validation
npm run test:structure  # Structure validation
npm run test:docker     # Docker tests

# Test orchestration
npm run test:orchestrate       # Smart mode
npm run test:orchestrate:quick # Quick tests
npm run test:orchestrate:full  # Full suite
```

### Makefile Commands

```bash
# Test commands
make test-all          # Run all tests
make test-package      # Test NPM package
make test-structure    # Test project structure
make docker-build-test # Test Docker builds

# Validation
make pre-commit        # Pre-commit checks
make validate          # Full validation
```

## 🔄 CI/CD Integration

### GitHub Actions

The project includes GitHub Actions workflows:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Kedro tests
        run: |
          pipx install kedro
          npm run test:kedro:all
```

### Pre-commit Hooks

```bash
# Install git hooks
npm run install-hooks

# Hooks will run automatically on commit
# Manual validation
npm run validate:quick  # Quick validation
npm run validate:full   # Full validation
```

## 📊 Test Reports

### Viewing Results

```bash
# View latest test summary
cat kedro-pipeline/data/08_reporting/last_run_summary.json | jq

# View final test report
cat kedro-pipeline/data/03_primary/final_test_report.json | jq

# View specific test results
cat kedro-pipeline/data/02_intermediate/docker_test.json | jq
```

### Report Structure

```json
{
  "timestamp": "2025-08-25 18:48:18",
  "summary": {
    "total_tests": 13,
    "passed": 7,
    "failed": 6,
    "warnings": 2
  },
  "test_results": {
    "package_json_validation": {...},
    "npm_package_files": {...},
    "docker_compose_validity": {...}
  },
  "failed_tests": [...],
  "tests_with_warnings": [...]
}
```

## 🐛 Troubleshooting

### Common Issues

#### PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL (macOS)
brew services start postgresql@14

# Update database configuration
# Edit kedro-pipeline/conf/base/parameters.yml
# Set admin_user to your system username
```

#### Kedro Command Not Found
```bash
# Install Kedro with pipx
pipx install kedro

# Or with pip in virtual environment
pip install kedro kedro-viz kedro-datasets
```

#### Docker Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild containers
cd dev-environment
make rebuild
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env file
```

## 📈 Performance Optimization

### Parallel Test Execution

Kedro can run independent nodes in parallel:

```bash
# Run with parallel execution
kedro run --pipeline test:all --runner ParallelRunner
```

### Caching Test Results

Test results are cached in `data/` directory. To force re-run:

```bash
# Clear cache
rm -rf kedro-pipeline/data/02_intermediate/*
rm -rf kedro-pipeline/data/03_primary/*

# Run tests
npm run test:kedro:all
```

## 🔐 Security Testing

### Security Checks

```bash
# Check for vulnerabilities
npm audit

# Check Python dependencies
pip-audit

# Docker security scan
docker scan stackwizard-backend
```

## 📝 Contributing to Tests

### Adding New Tests

1. **Create test node** in `kedro-pipeline/src/stackwizard_pipeline/nodes/`
2. **Add to pipeline** in `kedro-pipeline/src/stackwizard_pipeline/pipelines/`
3. **Register pipeline** in `pipeline_registry.py`
4. **Add npm script** in `package.json`
5. **Update catalog** in `conf/base/catalog.yml`

Example:
```python
# nodes/my_test.py
def test_my_feature(params: Dict[str, Any]) -> Dict[str, Any]:
    """Test my new feature"""
    return {
        "test_name": "my_feature",
        "success": True,
        "errors": []
    }
```

### Test Guidelines

1. **Isolation**: Tests should not depend on external services
2. **Reproducibility**: Same input should produce same output
3. **Documentation**: Document test purpose and expected results
4. **Error Handling**: Gracefully handle failures
5. **Reporting**: Return structured JSON results

## 📚 Additional Resources

- [Kedro Documentation](https://docs.kedro.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [PostgreSQL Testing](https://www.postgresql.org/docs/current/regress.html)

---

For questions or issues, please open a GitHub issue or contact the maintainers.