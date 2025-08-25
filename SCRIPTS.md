# 📜 NPM Scripts Documentation

Complete reference for all available npm scripts in StackWizard.

## 📋 Quick Reference

```bash
npm start                     # Run the generator interactively
npm test                      # Run basic tests
npm run test:kedro:all        # Run complete Kedro test suite
npm run validate:full         # Full pre-push validation
```

## 🎯 Main Scripts

### Generator
| Script | Command | Description |
|--------|---------|-------------|
| `start` | `node src/index.js` | Launch the interactive project generator |

## 🧪 Testing Scripts

### Kedro Pipeline Tests (New!)
| Script | Command | Description |
|--------|---------|-------------|
| `test:kedro` | `node scripts/kedro-test.js` | Run Kedro tests with options |
| `test:kedro:quick` | `node scripts/kedro-test.js --quick` | Quick Kedro test suite |
| `test:kedro:release` | `node scripts/kedro-test.js --release` | Release validation tests |
| `test:kedro:package` | `cd kedro-pipeline && kedro run --pipeline test:package` | Test NPM package integrity |
| `test:kedro:structure` | `cd kedro-pipeline && kedro run --pipeline test:structure` | Test project structure generation |
| `test:kedro:docker` | `cd kedro-pipeline && kedro run --pipeline test:docker` | Test Docker configuration |
| `test:kedro:e2e` | `cd kedro-pipeline && kedro run --pipeline test:e2e` | Run end-to-end tests |
| `test:kedro:all` | `cd kedro-pipeline && kedro run --pipeline test:all` | Run complete test suite |

### Database Pipeline Tests
| Script | Command | Description |
|--------|---------|-------------|
| `test:kedro:db` | `cd kedro-pipeline && kedro run --pipeline db:init` | Initialize test database from SQL |
| `test:kedro:db:cleanup` | `cd kedro-pipeline && kedro run --pipeline db:cleanup` | Clean up test database |
| `test:kedro:db:full` | `cd kedro-pipeline && kedro run --pipeline db:full` | Full database test cycle |

### Legacy Test Scripts
| Script | Command | Description |
|--------|---------|-------------|
| `test` | `node --test src/**/*.test.js \|\| echo 'No tests found'` | Run Node.js native tests |
| `test:package` | `node test/test-npm-package-files.js` | Test NPM package files |
| `test:structure` | `node test/test-generated-structure.js` | Test generated project structure |
| `test:docker` | `node test/test-docker-compose.js` | Test Docker Compose configuration |
| `test:docker-deps` | `node test/test-docker-dependencies.js` | Test Docker dependencies |
| `test:docker-runtime` | `node test/test-docker-runtime.js` | Test Docker runtime |
| `test:docker-deps-real` | `node test/test-docker-deps-real.js` | Test real Docker dependencies |
| `test:errors` | `jest test/error-handling.test.js --verbose` | Test error handling |
| `test:all` | `npm run test:package && npm run test:structure && npm run test:errors` | Run all legacy tests |
| `test:ci` | `npm run test:package && npm run test:structure` | CI test suite |

### Test Orchestration
| Script | Command | Description |
|--------|---------|-------------|
| `test:orchestrate` | `node test-orchestrator.js` | Smart test orchestration |
| `test:orchestrate:quick` | `node test-orchestrator.js quick` | Quick orchestrated tests |
| `test:orchestrate:full` | `node test-orchestrator.js full` | Full orchestrated test suite |

## ✅ Validation Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `validate` | `node pre-push-validator.js` | Run pre-push validation |
| `validate:quick` | `node pre-push-validator.js quick` | Quick validation checks |
| `validate:full` | `node pre-push-validator.js full` | Complete validation suite |

## 🔧 Development Scripts

### Code Quality
| Script | Command | Description |
|--------|---------|-------------|
| `lint` | `eslint src/ --ext .js` | Run ESLint on source files |
| `format` | `prettier --write 'src/**/*.js'` | Format code with Prettier |
| `format:check` | `prettier --check 'src/**/*.js'` | Check code formatting |

### Git Hooks
| Script | Command | Description |
|--------|---------|-------------|
| `precommit` | `node test-orchestrator.js quick` | Pre-commit validation hook |
| `install-hooks` | `git config core.hooksPath .githooks` | Install Git hooks |

### Publishing
| Script | Command | Description |
|--------|---------|-------------|
| `prepublishOnly` | `npm run lint && npm run format:check && npm run test:package` | Pre-publish validation |

## 🚀 Usage Examples

### Daily Development
```bash
# Start developing
npm start

# Run quick tests before commit
npm run test:orchestrate:quick

# Full validation before push
npm run validate:full
```

### Testing Workflow
```bash
# Test specific component
npm run test:kedro:package

# Run all Kedro tests
npm run test:kedro:all

# Test with visual monitoring
kedro viz run
npm run test:kedro:all
```

### Database Testing
```bash
# Initialize test database
npm run test:kedro:db

# Run tests and cleanup
npm run test:kedro:db:full
```

### Pre-release Checklist
```bash
# 1. Run full test suite
npm run test:kedro:all

# 2. Validate everything
npm run validate:full

# 3. Check formatting
npm run format:check

# 4. Run release tests
npm run test:kedro:release
```

## 📊 Script Dependencies

### Required Tools
- **Node.js**: 16.0.0+
- **npm**: 7.0.0+
- **Python**: 3.11+ (for Kedro)
- **Kedro**: Install with `pipx install kedro`
- **Docker**: For container tests
- **PostgreSQL**: For database tests

### Optional Tools
- **Jest**: For error handling tests
- **Cypress**: For E2E visual tests
- **ESLint**: For code linting
- **Prettier**: For code formatting

## 🔍 Script Details

### Kedro Pipeline Scripts
These scripts interact with the Kedro pipeline system for advanced test orchestration:
- Pipeline definitions in `kedro-pipeline/src/stackwizard_pipeline/pipelines/`
- Test nodes in `kedro-pipeline/src/stackwizard_pipeline/nodes/`
- Configuration in `kedro-pipeline/conf/base/`
- Results in `kedro-pipeline/data/`

### Database Scripts
Database tests use SQL files from `kedro-pipeline/data/01_raw/sql/`:
- `schema/`: Table definitions
- `seed/`: Development data
- `test/`: Test-specific data

### Orchestrator Scripts
The test orchestrator (`test-orchestrator.js`) intelligently runs tests based on:
- Changed files
- Test dependencies
- Previous test results
- Available time

## 🐛 Troubleshooting

### Script Fails with "Command not found"
```bash
# Install dependencies
npm install

# For Kedro scripts
pipx install kedro
```

### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.js
chmod +x test/*.js
```

### Kedro Pipeline Not Found
```bash
# Initialize Kedro project
cd kedro-pipeline
kedro install
```

## 📝 Adding New Scripts

1. Add script to `package.json`:
```json
"scripts": {
  "my-script": "node scripts/my-script.js"
}
```

2. Create script file:
```javascript
// scripts/my-script.js
#!/usr/bin/env node
console.log('My new script');
```

3. Make executable:
```bash
chmod +x scripts/my-script.js
```

4. Document in this file

## 🔗 Related Documentation

- [TESTING.md](./TESTING.md) - Complete testing guide
- [README.md](./README.md) - Project overview
- [CLAUDE.md](./CLAUDE.md) - AI assistant guidelines
- [dev-environment/README.md](./dev-environment/README.md) - Development environment

---

For questions about scripts, please open a GitHub issue.