# Testing Guide for StackWizard Backend

This guide explains how to set up and run tests for the FastAPI backend using PostgreSQL.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ installed
- PostgreSQL container running (from docker-compose)

## Setup Instructions

### 1. Start PostgreSQL Container

First, ensure PostgreSQL is running using Docker:

```bash
# From the project root (where docker-compose.yml is located)
docker-compose up -d db

# Or if you already have the container running
docker ps | grep postgres
```

### 2. Create Test Database

Create a separate database for testing:

```bash
# Create test database
docker exec <container_name> psql -U postgres -c "CREATE DATABASE test_app_test;"

# Add UUID extension (required for PostgreSQL UUID support)
docker exec <container_name> psql -U postgres -d test_app_test -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

Replace `<container_name>` with your PostgreSQL container name (e.g., `test-app-db`).

### 3. Set Up Python Environment

```bash
# Navigate to backend directory
cd templates/common/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Test Database Configuration
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_app_test

# Main Database Configuration (for running the app)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/test_app
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_app
DB_USER=postgres
DB_PASSWORD=postgres

# Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Account
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=admin123
```

### 5. Run Database Migrations

Before running tests, ensure the test database has the correct schema:

```bash
# For the test database
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_app_test \
PYTHONPATH=. ./venv/bin/alembic upgrade head

# For the main database (if running the app)
PYTHONPATH=. ./venv/bin/alembic upgrade head
```

## Running Tests

### Run All Tests

```bash
# Run all tests with verbose output
./venv/bin/pytest -v

# Run with short traceback for cleaner output
./venv/bin/pytest -v --tb=short

# Run with coverage report
./venv/bin/pytest --cov=app --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only model tests
./venv/bin/pytest tests/test_models.py -v

# Run only authentication tests
./venv/bin/pytest tests/test_auth.py -v

# Run only schema tests
./venv/bin/pytest tests/test_schemas.py -v

# Run only user endpoint tests
./venv/bin/pytest tests/test_users.py -v

# Run only admin tests
./venv/bin/pytest tests/test_admin.py -v
```

### Run a Single Test

```bash
# Run specific test by name
./venv/bin/pytest tests/test_models.py::TestUserModel::test_user_table_exists -v
```

## Test Architecture

The test suite uses PostgreSQL instead of SQLite to ensure compatibility with production:

- **Database**: PostgreSQL running in Docker container
- **Test Database**: Separate `test_app_test` database
- **Isolation**: Each test function gets a fresh database session
- **Fixtures**: Defined in `tests/conftest.py`

### Key Configuration Changes

The test configuration has been modified to use PostgreSQL:

```python
# tests/conftest.py
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_app_test"
)
```

## Current Test Status

As of the latest run:
- ✅ **24 tests passing**
- ✅ **9 model tests passing** (all User model tests)
- ✅ **6 authentication tests passing**
- ✅ **7 schema tests passing** (with 3 known issues)
- ⚠️ Some endpoint tests require the app to not be running during tests

## Troubleshooting

### Issue: "database does not exist"
**Solution**: Create the test database:
```bash
docker exec <container_name> psql -U postgres -c "CREATE DATABASE test_app_test;"
```

### Issue: "relation 'users' does not exist"
**Solution**: Run migrations on the test database:
```bash
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_app_test \
PYTHONPATH=. ./venv/bin/alembic upgrade head
```

### Issue: UUID type errors
**Solution**: Add UUID extension to PostgreSQL:
```bash
docker exec <container_name> psql -U postgres -d test_app_test \
  -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### Issue: Connection refused
**Solution**: Ensure PostgreSQL container is running:
```bash
docker-compose up -d db
docker ps | grep postgres
```

## Running the Application

To run the FastAPI application for manual testing:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
./venv/bin/python -m uvicorn app.main:app --reload --port 8000

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Admin: admin@example.com / admin123
```

## Continuous Integration

For CI/CD pipelines, use these commands:

```bash
# Setup
pip install -r requirements.txt
pip install -r requirements-test.txt

# Create and prepare test database
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_app_test
createdb -h localhost -U postgres test_app_test
psql -h localhost -U postgres -d test_app_test -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# Run migrations
PYTHONPATH=. alembic upgrade head

# Run tests
pytest -v --tb=short --cov=app --cov-report=xml
```

## Best Practices

1. **Always use PostgreSQL for tests** - SQLite doesn't support all PostgreSQL features
2. **Use separate test database** - Never run tests against production or development database
3. **Clean database state** - Each test should start with a clean database state
4. **Test in isolation** - Tests should not depend on each other
5. **Mock external services** - Use mocks for email, external APIs, etc.

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Use appropriate fixtures from `conftest.py`
3. Test both success and failure cases
4. Include tests for edge cases
5. Ensure tests are independent and can run in any order