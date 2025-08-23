# ⚠️ TODO AFTER MERGING THIS PR

## Critical Actions Required

### 1. Fix Branch Protection Settings
Go to: https://github.com/rafeekpro/stackwizard/settings/branches

Edit the `main` branch protection rule and REMOVE from required checks:
- `e2e-login-test`
- `react-error-handling`

These should NOT be required because they have path filters.

### 2. Re-enable Disabled Workflows
```bash
git checkout main
git pull
mv .github/workflows/test-e2e-login.yml.disabled .github/workflows/test-e2e-login.yml
mv .github/workflows/test-react-errors.yml.disabled .github/workflows/test-react-errors.yml
git add -A
git commit -m "re-enable: e2e and react error workflows after fixing branch protection"
git push origin main
```

### 3. Verify
Create a test PR to verify:
- Only essential tests are required
- No "Waiting for status" messages
- e2e tests run only when templates change

## Why This Was Necessary
These workflows were temporarily disabled because:
1. They are marked as "Required" in branch protection
2. They have path filters so don't always run
3. This causes eternal "Waiting for status" state
4. Prevents PR from being merged

## Permanent Solution
The permanent solution is to only mark tests as "Required" if they:
- Run on EVERY PR (no path filters)
- Are fast (<1 minute)
- Are critical for functionality

Tests with path filters should be optional/informational only.