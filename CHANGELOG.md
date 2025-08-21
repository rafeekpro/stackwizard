# Changelog

All notable changes to StackWizard will be documented in this file.

## [1.0.4] - 2024-08-21

### 🐛 Bug Fixes
- **CORS Configuration**: Fixed CORS headers not being sent properly by changing origins type from `List[AnyHttpUrl]` to `List[str]`
- **API Health Endpoint**: Added missing `/api/health` endpoint for frontend health checks
- **Static Files**: Added favicon.ico files to both Material UI and Tailwind templates to prevent 500 errors
- **Docker Networking**: Fixed proxy configuration to use `backend:8000` instead of `localhost:8000` for proper container communication
- **Uploads Directory**: Added automatic creation of uploads directory during project generation

### ✨ New Features
- **Integration Tests**: Added comprehensive integration test suite (`test_integration.py`) to all generated projects
- **Test Runner Script**: Added `run_integration_tests.sh` for easy integration test execution
- **Enhanced CORS Support**: Added support for `127.0.0.1` origins and improved validator for environment variable configuration

### 📚 Documentation
- Updated PROJECT_README.md with integration test instructions
- Added integration test documentation

### 🔧 Technical Improvements
- Removed unnecessary conditional check for BACKEND_CORS_ORIGINS
- Removed redundant `.strip()` call on hardcoded strings
- Fixed and improved CORS origins validator with JSON string support
- Added `requests` library to requirements.txt for integration tests

## [1.0.3] - 2024-08-20

### 🐛 Bug Fixes
- Fixed Docker network conflicts by using unique network names
- Improved container health checks
- Fixed database connection issues

## [1.0.2] - 2024-08-19

### ✨ New Features
- Added comprehensive authentication system
- Added admin panel functionality
- Improved test coverage to 100%

## [1.0.1] - 2024-08-18

### 🐛 Bug Fixes
- Fixed template path issues
- Improved error handling
- Fixed package.json configuration

## [1.0.0] - 2024-08-17

### 🎉 Initial Release
- FastAPI backend with authentication
- React frontend with Material UI and Tailwind CSS options
- PostgreSQL database with SQLAlchemy ORM
- Docker Compose for containerized development
- Alembic migrations
- JWT authentication
- Comprehensive test suite
- Interactive CLI with beautiful UI