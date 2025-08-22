# Branch Protection Rules for Main Branch

## 🔒 Current Protection Status: ENABLED

The `main` branch is fully protected with the following rules:

### ✅ Required Status Checks (All must pass)
- Test CLI
- Test Generator CLI  
- Test Backend Template
- Test Frontend MUI Template
- Test Frontend Tailwind Template
- Test API Endpoints Match
- Test ESLint - Material UI Template
- Test ESLint - Tailwind Template
- Lint and Format Check
- Security Scan

### 🚫 Direct Push Protection
- **enforce_admins**: `true` - Even admins cannot bypass these rules
- **allow_force_pushes**: `false` - Force pushes are completely disabled
- **allow_deletions**: `false` - Branch cannot be deleted

### 👥 Pull Request Requirements
- **Required approving reviews**: 1
- **Dismiss stale reviews**: Yes (when new commits are pushed)
- **Require review from last pusher**: Yes
- **Require conversation resolution**: Yes (all PR comments must be resolved)

### 🛡️ Additional Protections
- **Strict status checks**: Yes (branch must be up to date with base branch)
- **Block direct commits**: Yes (all changes must go through PR)

## How to Work with Protected Main

### ✅ Correct Workflow
```bash
# 1. Create a feature branch
git checkout -b feature/my-feature

# 2. Make your changes
git add .
git commit -m "feat: Add new feature"

# 3. Push to feature branch
git push origin feature/my-feature

# 4. Create Pull Request
gh pr create

# 5. Wait for:
#    - All CI checks to pass
#    - Code review approval
#    - All conversations to be resolved

# 6. Merge PR (via GitHub UI or CLI)
gh pr merge --merge
```

### ❌ What Will NOT Work
```bash
# These will all be rejected:
git push origin main                    # Direct push
git push --force origin main           # Force push  
git push origin :main                  # Delete branch
git commit --amend && git push origin main  # Amend and push
```

## Local Git Hook (Additional Protection)

To prevent accidental push attempts to main locally, add this pre-push hook:

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
protected_branch='main'
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

if [ "$current_branch" = "$protected_branch" ]; then
    echo "🚫 Direct push to main branch is not allowed!"
    echo "Please create a feature branch and submit a pull request."
    echo ""
    echo "To create a feature branch:"
    echo "  git checkout -b feature/your-feature-name"
    echo "  git push origin feature/your-feature-name"
    echo "  gh pr create"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-push
```

## Emergency Override (Use with EXTREME Caution)

If absolutely necessary, an admin can temporarily disable protection:

```bash
# ⚠️ DANGER: Only use in emergencies
gh api -X DELETE repos/rafeekpro/stackwizard/branches/main/protection

# Make emergency fix
git push origin main

# ⚠️ CRITICAL: Re-enable protection immediately
gh api -X PUT repos/rafeekpro/stackwizard/branches/main/protection \
  --input .github/branch-protection.json
```

## Verification

To verify branch protection is active:

```bash
# Check protection status
gh api repos/rafeekpro/stackwizard/branches/main/protection

# Test (this should fail)
git checkout main
echo "test" >> README.md
git add . && git commit -m "test"
git push origin main  # Should be rejected
```

## Why These Rules?

1. **Code Quality**: All changes are tested before merging
2. **Peer Review**: At least one other person reviews code
3. **No Accidents**: Can't accidentally push to main
4. **Audit Trail**: All changes tracked through PRs
5. **CI/CD Safety**: Ensures deployments only happen from tested code

---
*Last Updated: 2025-08-22*
*Protection Level: Maximum*