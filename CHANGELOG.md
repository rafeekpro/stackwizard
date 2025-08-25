# Changelog

All notable changes to StackWizard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-08-25

### ✨ New Features
- **API Structure Optimization** - Complete backend API refactoring for better maintainability
  - Split large monolithic files into focused, modular components
  - Created organized user endpoints module with sub-modules (profile, management, statistics, export)
  - Added comprehensive validation utilities module with 30+ validators
  - Centralized input validation logic for consistency
  - Improved code organization with single-responsibility modules

### 🚀 Improvements
- **Better Test Coverage** - Added comprehensive API structure tests
  - Tests for response format consistency
  - Tests for modular imports verification
  - Tests for validator functionality
  - Prevention of API structure regression

### 🐛 Bug Fixes
- **User Deletion** - Changed from hard delete to soft delete for better data retention
- **Response Structures** - Fixed UserResponse schema to include success field
- **Test Fixtures** - Corrected fixture references for proper test execution

### 📚 Documentation
- **Code Organization** - Better separation of concerns with clear module boundaries
- **Validator Documentation** - Comprehensive validation functions with clear error messages

## [1.1.2] - 2025-08-24

### 🐛 Bug Fixes
- **Docker npm dependencies** - Fixed missing dependencies in containers
  - Use `npm ci` for respecting package-lock.json
  - Fallback to `npm install` if lock file is missing
  - Resolves issues with @headlessui/react and @heroicons/react in Tailwind template

### 📚 Documentation
- **Version Management Rules** - Added clear version bumping guidelines to CLAUDE.md
  - Specified when to increment PATCH, MINOR, or MAJOR versions
  - Listed when version updates are required vs optional
  - Ensures consistent versioning practices

## [1.1.1] - 2025-08-24

### ✨ New Features
- **Comprehensive Error Handling System** - Enhanced error handling for better user experience
  - Added 20+ specific error codes for different failure scenarios
  - Implemented error recovery mechanisms with automatic retry
  - Created user-friendly error messages with clear solutions
  - Added error context tracking for debugging
  - System requirements checking with version validation (`--check-requirements` flag)
  - Port availability checking before project creation
  - Backup creation before cleanup for large projects

### 🔧 Improvements
- **Enhanced Validators** - Improved input validation
  - Project name validation with reserved names check
  - Port validation with commonly used ports warning
  - Database configuration validation
  - Password strength requirements
- **Logging System** - Advanced debug logging (`--debug` flag)
  - Automatic log file cleanup (keeps last 10 logs)
  - Structured logging with different levels
  - Error context capture with system information
  - Debug mode with detailed error traces
- **Error Recovery** - Smart recovery strategies
  - Automatic recovery for optional features (Git, npm, pip)
  - Recovery attempt tracking with maximum limits
  - Graceful degradation for non-critical failures
  - Cleanup with backup for partially created projects
- **Version Detection** - Improved Python/pip version detection
  - Removed shell operators (`||`) for consistent detection
  - Proper fallback logic (tries python3/pip3 first, then python/pip)
  - Shows which specific command was used in output

### 🧪 Testing
- **Error Handling Tests** - Comprehensive test suite
  - Unit tests for all error codes and validators
  - Integration tests for error recovery flows
  - System requirements checking tests
  - Port availability detection tests
  - Cleanup and backup functionality tests
  - Added Jest as dev dependency for testing

## [1.1.0] - 2025-08-23

### ✨ New Features
- **Backend Service Layer Architecture** - Complete refactoring with clean separation of concerns
  - Implemented Service Layer pattern (UserService, ItemService, AdminService)
  - Added Repository Pattern for data access abstraction
  - Created BaseService and BaseRepository for common operations
  - Full TDD approach with comprehensive test coverage
- **Advanced Error Handling System** - Structured exception hierarchy
  - Custom exception classes for different error types
  - Centralized error handler middleware
  - Request ID tracking for debugging
  - Standardized error response format
- **Enhanced Backend Capabilities**
  - Bulk operations support (create, update, delete)
  - Advanced search functionality
  - Soft delete with recovery option
  - Eager loading for optimized queries
  - GDPR-compliant data export

### 🔧 Improvements
- **Code Quality** - Applied SOLID principles and design patterns
  - Single Responsibility Principle in all services
  - Dependency Injection for loose coupling
  - Generic types for reusable components
  - Comprehensive docstrings and type hints
- **Testability** - Improved test infrastructure
  - Services can be tested in isolation
  - Easy mocking of dependencies
  - 100% coverage of critical business logic
- **Performance** - Optimized database operations
  - Query optimization with eager loading
  - Bulk operations for batch processing
  - Prepared for caching layer integration

### 📚 Documentation
- Added SERVICE_LAYER_REFACTORING.md with complete architecture guide
- Added REFACTORING_SUMMARY.md with migration strategy
- Updated API documentation with new service layer structure

## [1.0.17] - 2025-08-23

### 🐛 Bug Fixes
- **Fixed Items page display** - Items page now shows sample data after initialization
  - Added `create_sample_items()` function in backend initialization
  - Creates 3 sample items (Laptop, Mouse, Keyboard) for demo purposes
- **Fixed My Account Statistics** - Statistics tab now displays real user data
  - Added `/api/v1/users/me/statistics` endpoint
  - Shows total items, login count, last login, account age, verification status
  - Frontend fetches and displays actual statistics from API
- **Fixed Export Data functionality** - Export button now works correctly
  - Fixed `/api/v1/users/me/export` endpoint
  - Returns complete user profile and items in JSON format
  - Sets proper Content-Disposition header for file download

### ✨ New Features
- **Azure DevOps Integration** - Complete hybrid workflow support
  - Setup script for Azure DevOps + GitHub integration
  - Migration tool for GitHub issues to Azure work items
  - Automatic work item status sync with pull requests
  - Comprehensive developer workflow documentation
- **Functional Tests** - Added comprehensive test suite for all fixes
  - Tests both Material UI and Tailwind templates
  - Verifies items display, statistics, and export functionality
  - Uses Puppeteer for browser automation
  - Docker Compose integration testing

### 🔧 Improvements
- **Test Maintainability** - Refactored test code for better organization
  - Extracted code templates into separate files
  - Improved test structure and reusability
  - Fixed CommonJS compatibility issues

## [1.0.16] - 2025-08-23

### 🐛 Bug Fixes
- **Fixed navigation auth state** - Navigation menu now properly updates after login/logout
  - Added authentication logic to Tailwind navbar component
  - Backend now returns user data with authentication tokens
  - Fixed UserSchema to include all required fields (is_verified, login_count)
  - Created separate RegisterResponse schema for registration endpoint
- **Fixed backend tests** - All 77 backend tests now passing
  - Fixed ResponseValidationError in auth endpoints
  - Updated schemas to match User model requirements

### ✨ New Features
- **Comprehensive navigation authentication tests**
  - Added E2E tests for navigation state changes
  - Tests both Material UI and Tailwind templates
  - Prevents regression of auth state bugs

## [1.0.15] - 2025-08-23

### 🐛 Docker Compose Fixes
- **Fixed duplicate alembic migrations** - Removed alembic command from Dockerfile CMD
- **Fixed netcat compatibility** - Changed from `nc.traditional` to `nc` in docker-compose
- **Fixed netcat package** - Switched from `netcat-traditional` to `netcat-openbsd` 
- **Fixed bcrypt warning** - Added explicit `bcrypt==4.0.1` to requirements.txt
- **Fixed uvicorn reload** - Added `--workers 1` flag to prevent reload issues

### 🧪 Comprehensive Testing Suite
- **NPM Package Files Test** (`test/test-npm-package-files.js`)
  - Verifies all critical template files are included in npm package
  - Prevents "only frontend folder" issue
  - Runs automatically before npm publish via `prepublishOnly` hook
- **Generated Structure Test** (`test/test-generated-structure.js`)
  - Verifies complete project structure generation
  - Checks all directories and files are created
  - Validates placeholder replacements
- **Docker Integration Test** (`test/test-docker-compose.js`)
  - Generates test project and runs docker-compose
  - Waits for services health checks
  - Tests API endpoints including login
  - Validates no critical errors in logs

### ⚡ CI/CD Optimizations
- **Essential CI Workflow** (`ci-essential.yml`)
  - Runs only critical tests on every PR (~2-3 minutes)
  - Conditional tests based on changed files
  - 80% reduction in CI time for most PRs
- **Smart Test Execution**
  - Backend tests only when backend files change
  - Frontend tests only when frontend files change
  - Docker tests only when Docker files change
- **Manual Test Triggers**
  - Added `workflow_dispatch` for manual testing
  - Support for `test:all` label to run full suite

### 📚 Documentation
- **Development Rules** (`CLAUDE.md`)
  - Comprehensive development guidelines
  - TDD requirements and testing standards
  - CHANGELOG management rules
  - PR checklist and golden rules
- **Branch Protection Guide** (`.github/branch-protection.md`)
  - Clear documentation of required vs optional tests
  - Configuration instructions for GitHub
  - Test optimization rationale

## [1.0.14] - 2025-08-23

### 🐛 Critical Bug Fix
- **NPM Package Generation**: Fixed critical issue where npm package only generated frontend folder
  - Root cause: `.npmignore` was excluding essential template files (.env.example, .github, *.md)
  - Added exceptions to include template files needed for project generation
  - Verified all components (backend, database, docker-compose) are now included

### 🔧 Technical Details
- Modified `.npmignore` to exclude `.env` files but include `templates/**/.env.example`
- Modified `.npmignore` to exclude `.github` but include `templates/**/.github/`
- Modified `.npmignore` to exclude `*.md` but include `templates/**/*.md`

## [1.0.13] - 2025-08-23

### ✨ New Features
- **Conditional Navigation**: Added authentication-based conditional navigation in Material UI template
  - Unauthenticated users see: Home, About | Sign In, Sign Up (on the right)
  - Authenticated users see: Home, About, Users, Items, My Account | Logout (on the right)
- **My Account Page**: Added comprehensive user account management page with three tabs:
  - Profile tab: Update username and full name
  - Password tab: Change password with validation
  - Statistics tab: View account statistics and usage metrics
- **Navigation Component**: Enhanced Navbar component with useAuth hook integration
- **Protected Routes**: Added My Account route with authentication protection

### 🧪 Testing
- **TDD Approach**: Implemented Test-Driven Development for navigation components
- **Navigation Tests**: Added comprehensive tests for conditional navigation display
- **CI/CD**: All integration tests passing including e2e-login and react-error-handling

### 🔧 Technical Improvements
- **Workflow Triggers**: Fixed GitHub Actions workflow triggers for release branches
- **Test Coverage**: Maintained 100% test coverage across all critical paths
- **Code Quality**: Clean implementation following React best practices

## [1.0.12] - 2025-08-22

### 🚀 Release Summary
Complete release with all React Router fixes and improvements from v1.0.11

### Included Changes from v1.0.11
- React Router v7 future flags configuration
- Missing /unauthorized and 404 routes fixed
- New error pages (UnauthorizedPage, NotFoundPage)
- Comprehensive Router testing

### 📦 Publishing
- Official npm release of all accumulated fixes
- Ensures all users get the latest improvements

## [1.0.11] - 2025-08-22

### 🐛 Bug Fixes
- **React Router v7**: Added future flags to prevent deprecation warnings
- **Missing Routes**: Added /unauthorized route for proper 401 handling
- **404 Page**: Added catch-all route with NotFoundPage component

### ✨ New Features
- **Error Pages**: Added UnauthorizedPage (401) and NotFoundPage (404) components
- **Router Configuration**: Configured v7_startTransition and v7_relativeSplatPath flags
- **Route Testing**: Added comprehensive test for React Router issues detection

### 🧪 Testing
- **New Test**: Created test-react-router-issues.js to detect routing problems
- **CI Workflow**: Added React Router test workflow for continuous validation
- **Coverage**: Tests both MUI and Tailwind templates for router issues

## [1.0.10] - 2025-08-22

### 🐛 Critical Bug Fixes
- **Login Authentication**: Fixed 422 error on login - frontend now correctly sends form-data instead of JSON
- **OAuth2 Compatibility**: Updated AuthContext to use URLSearchParams for OAuth2PasswordRequestForm
- **Content-Type**: Fixed Content-Type header to 'application/x-www-form-urlencoded' for login

### ✨ Improvements
- **Login Test**: Added comprehensive form-data login test
- **Both Templates**: Fixed login in both Material UI and Tailwind CSS templates
- **Authentication**: Ensured admin@example.com / admin123 credentials work correctly

## [1.0.9] - 2025-08-22

### 🐛 Bug Fixes
- **React Render Error**: Fixed "Objects are not valid as a React child" error in AuthContext
- **Error Handling**: Properly handle FastAPI validation error objects in frontend
- **Login/Register**: Fixed error display to show strings instead of objects

### ✨ Improvements
- **Error Detection**: Added React render error detection test
- **CI/CD**: Added workflow to test React error handling
- **Type Safety**: Added proper type checking for API error responses

## [1.0.8] - 2025-08-22

### 🐛 Bug Fixes
- **Admin Endpoints**: Fixed admin API paths in frontend templates to include `/api/v1` prefix
- **Frontend API Paths**: Corrected all admin dashboard API calls in both MUI and Tailwind templates
- **Auth Endpoints**: Fixed authentication endpoint paths from `/auth/login` to `/api/v1/auth/login`
- **Admin User Creation**: Added username field to admin user initialization to fix OAuth2 login
- **Items Table Migration**: Added missing migration for items table to fix 500 errors

### ✨ Improvements  
- **E2E Testing**: Added comprehensive end-to-end login test with Puppeteer
- **Endpoint Verification**: Created test to verify all frontend API calls match backend endpoints
- **API Testing**: Added comprehensive API endpoint validation test covering 39 endpoints
- **Runtime Testing**: Added runtime API testing with Docker environment
- **CI/CD**: Added E2E login test workflow and automated API testing
- **Test Coverage**: Updated all auth-related tests to use correct API paths

### 📚 Documentation
- **Changelog**: Updated CHANGELOG.md for better version tracking
- **Critical Rules**: Added changelog update requirements to critical rules

## [1.0.7] - 2025-08-22

### 🐛 Bug Fixes
- **Health Endpoints**: Fixed health endpoint 404 errors reported by users
- **Database Status**: Fixed database connectivity status display
- **SQL Compatibility**: Added proper SQLAlchemy text() wrapper for raw SQL queries

### ✨ Improvements  
- **Health Testing**: Added comprehensive health endpoint testing
- **CI Workflows**: Added CI workflow for automated health endpoint validation
- **API Detection**: Improved API endpoint detection in tests

## [1.0.6] - 2025-08-22

### 🐛 Bug Fixes
- **Health Paths**: Fixed health endpoint paths to resolve 404 errors
- **Console Errors**: Added console error detection tests
- **API Validation**: Fixed API endpoint validation

### ✨ Improvements
- **Error Detection**: Added comprehensive testing for console errors
- **CI Pipeline**: Improved CI/CD pipeline with additional test coverage
- **Documentation**: Enhanced branch protection documentation

## [1.0.5] - 2025-08-22

### ✨ Features
- **Stable Release**: Production-ready version of StackWizard
- **UI Options**: Full support for Material UI and Tailwind CSS
- **Auth System**: Complete authentication system with JWT
- **Admin Features**: Admin dashboard with comprehensive user management
- **Docker Support**: Full Docker Compose orchestration
- **Test Suites**: Comprehensive test coverage

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