# 🔧 How to Fix Branch Protection (Required Tests Issue)

## Problem
The following tests are marked as "Required" but have path filters, causing them to get stuck in "Waiting for status" state:
- `e2e-login-test`
- `react-error-handling`
- `react-router-test` (if applicable)

## Solution: Update Branch Protection Rules

### Steps to Fix:

1. **Go to Repository Settings**
   - Navigate to: https://github.com/rafeekpro/stackwizard/settings
   - Click on "Branches" in the left sidebar

2. **Edit Main Branch Protection**
   - Find the "main" branch rule
   - Click "Edit"

3. **Update Required Status Checks**
   
   Find the section "Require status checks to pass before merging"
   
   **REMOVE these from required** (uncheck them):
   - ❌ `e2e-login-test`
   - ❌ `react-error-handling` 
   - ❌ `react-router-test`
   
   **KEEP these as required** (checked):
   - ✅ `ci-essential / lint-and-format`
   - ✅ `ci-essential / test-generator`
   - ✅ `Test API Endpoints Match`

4. **Save Changes**
   - Click "Save changes" at the bottom

## Why This Fix Works

### Required Tests (Always Run)
These tests run on EVERY PR and should be required:
- **Lint and Format** - Code quality (fast, <15s)
- **Test Generator** - Core functionality (fast, <30s)
- **API Endpoints Match** - API consistency (fast, <15s)

### Optional Tests (Conditional)
These tests only run when relevant files change and should NOT be required:
- **e2e-login-test** - Only when templates change (slow, 5-10min)
- **react-error-handling** - Only when frontend changes (slow, 5-10min)
- **react-router-test** - Only when frontend changes (slow, 5-10min)
- **Docker tests** - Only when Docker files change (slow, 10min)

## Benefits

- ✅ No more "Waiting for status" issues
- ✅ Faster PR merges (only essential tests required)
- ✅ Tests still run when needed (path-based triggers)
- ✅ Can manually trigger tests with labels or workflow_dispatch

## Alternative: Force Run Tests

If you need to run these tests anyway:
1. Add label `force-tests` to the PR
2. Or manually trigger from Actions tab
3. Or modify a file in the relevant path to trigger the test

## Verification

After updating branch protection:
1. Create a test PR with minor changes
2. Only essential tests should be required
3. PR should be mergeable once essential tests pass
4. No more "Waiting for status" messages