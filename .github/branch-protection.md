# Branch Protection Configuration

## Required Status Checks for `main` branch

### Always Required (Essential)
These tests must ALWAYS pass before merging to main:

1. **ci-essential / lint-and-format** - Code quality checks
2. **ci-essential / test-generator** - Core functionality test
3. **Test API Endpoints Match** - API consistency check

### Conditionally Required
These tests run only when relevant files are changed:

4. **ci-essential / test-backend** (when backend files change)
5. **ci-essential / test-frontend** (when frontend files change)  
6. **ci-essential / test-docker** (when Docker files change)

### Optional Tests (Not Required for Merge)
These tests provide additional validation but don't block merging:

- **e2e-login-test** - Runs when templates change
- **react-error-handling** - Runs when frontend templates change
- **react-router-test** - Runs when frontend templates change
- **Bundle Size Check** - Informational
- **Test Coverage Report** - Informational
- **Security Scan** - Periodic security check

## How to Configure in GitHub

1. Go to Settings → Branches
2. Edit protection rule for `main`
3. Enable "Require status checks to pass before merging"
4. Add these required checks:
   - `ci-essential / lint-and-format`
   - `ci-essential / test-generator`
   - `Test API Endpoints Match`
5. Do NOT add conditional tests as required (they won't run on all PRs)

## Manual Test Triggers

For comprehensive testing before releases:
- Add label `test:all` to PR to run all tests
- Or manually trigger workflows from Actions tab

## Test Optimization Rationale

- **Essential tests**: ~2-3 minutes total
- **All tests**: ~15-20 minutes total
- **Savings**: ~80% reduction in CI time for most PRs

This configuration ensures:
- Fast feedback for developers
- Protection against critical bugs
- Full testing when needed (via labels or manual triggers)