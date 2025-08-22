# CLAUDE.md - Critical Instructions for AI Assistants

## 🔴 CRITICAL: NEVER DISABLE BRANCH PROTECTION

### ⛔ ABSOLUTE PROHIBITION:
**UNDER NO CIRCUMSTANCES** should you:
- Disable branch protection rules
- Make tests optional instead of required
- Suggest bypassing failing tests
- Use admin overrides to force merge
- Remove or weaken any protection settings

### Required Protection (NEVER CHANGE):
- ALL 13+ tests MUST be required
- ALL tests MUST pass before merge
- NO direct pushes to main
- NO exceptions, even for "emergencies"

**If tests fail: FIX THE CODE, don't disable the tests!**

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

## Quality Standards

### All Code Changes MUST:
1. Pass ALL automated tests (100% required)
2. Not introduce new ESLint warnings
3. Not create console errors
4. Maintain or improve test coverage
5. Follow existing code patterns

### Testing Requirements:
- `Test Generator CLI` - MUST PASS
- `Test Backend Template` - MUST PASS
- `Test Frontend MUI Template` - MUST PASS
- `Test Frontend Tailwind Template` - MUST PASS
- `Test ESLint - Material UI Template` - MUST PASS
- `Test ESLint - Tailwind Template` - MUST PASS
- `Test API Endpoints Match` - MUST PASS
- `Lint and Format Check` - MUST PASS
- `Security Scan` - MUST PASS
- `Test Coverage Report` - MUST PASS
- `Bundle Size Check` - MUST PASS
- `Docker Build Test` - MUST PASS
- `Integration Test - Generate Project` - MUST PASS

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

### Testing
```bash
# Run ESLint tests
node test/test-eslint-warnings.js

# Run API endpoint validation
node test/test-api-endpoints.js

# Run console error detection (requires Docker)
node test/test-console-errors.js
```

## Common Issues & Solutions

### If Tests Fail:
1. **FIX the code** - Never disable tests
2. **Debug locally** - Run tests individually
3. **Check logs** - Use `gh run view` for CI details
4. **Verify changes** - Ensure no regressions

### If Branch Protection Seems "In the Way":
**IT'S NOT!** Branch protection is protecting you from:
- Broken deployments
- Angry users
- NPM package disasters
- Security vulnerabilities

## Release Process

1. All changes through PRs - NO direct pushes
2. All tests must pass - NO exceptions
3. Version bump through PR
4. NPM publish automatic after merge

## 🚨 Security Incidents

**Disabling branch protection = CRITICAL SECURITY INCIDENT**

If you find branch protection disabled:
1. Re-enable IMMEDIATELY
2. Document the incident
3. Investigate how it happened
4. Implement additional safeguards

---

*This file is mandatory reading for all AI assistants working on this repository*
*Violation of these rules will result in immediate session termination*
*Last updated: 2025-08-22*