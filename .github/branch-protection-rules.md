# Branch Protection Rules for Main Branch

## ⚠️ IMPORTANT: Configure These Settings in GitHub

Go to: Settings → Branches → Add rule

### Branch name pattern:
```
main
```

### ✅ Protection Rules to Enable:

#### 1. **Require a pull request before merging**
- [x] Require a pull request before merging
- [x] Require approvals: 1
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require review from CODEOWNERS

#### 2. **Require status checks to pass before merging**
- [x] Require status checks to pass before merging
- [x] Require branches to be up to date before merging

#### 3. **Required Status Checks** (ALL should be required):
Select ALL of these:
- ✅ `Test Generator CLI`
- ✅ `Test Backend Template`
- ✅ `Test Frontend MUI Template`
- ✅ `Test Frontend Tailwind Template`
- ✅ `Test ESLint - Material UI Template`
- ✅ `Test ESLint - Tailwind Template`
- ✅ `Test API Endpoints Match`
- ✅ `Lint and Format Check`
- ✅ `Security Scan`
- ✅ `Test Coverage Report`
- ✅ `Bundle Size Check`
- ✅ `Docker Build Test`
- ✅ `Integration Test - Generate Project`

#### 4. **Additional Settings**
- [x] Require conversation resolution before merging
- [x] Require signed commits (optional but recommended)
- [x] Require linear history
- [x] Include administrators
- [x] Restrict who can push to matching branches

#### 5. **Who can push to main:**
- Nobody (all changes through PRs)

## 🔒 Why This Matters:

1. **Quality Assurance**: Every test must pass before code reaches main
2. **No Broken Builds**: Prevents merging code that breaks tests
3. **Consistency**: All PRs go through the same quality checks
4. **Security**: Prevents direct pushes that bypass reviews

## 📝 How to Configure:

1. Go to: https://github.com/rafeekpro/stackwizard/settings/branches
2. Click "Add rule"
3. Enter `main` as the branch name pattern
4. Check all the boxes listed above
5. For "Required status checks", search and add each test
6. Click "Create" or "Save changes"

## 🚨 Current Issue:
**Main branch is NOT protected!** This means:
- Direct pushes are allowed
- Tests are not required
- Code can be merged without review
- Quality is not guaranteed

**ACTION REQUIRED**: Apply these protection rules immediately!

## 📊 Expected Result:
After applying these rules:
- All PRs will show "X checks required"
- Cannot merge until all tests pass
- Cannot push directly to main
- Code quality is enforced

---

*Last updated: 2025-08-22*
*This file serves as documentation for required branch protection settings*