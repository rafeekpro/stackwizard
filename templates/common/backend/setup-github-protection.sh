#!/bin/bash

# GitHub Protection Setup Script
# This script configures branch protection rules using GitHub CLI

echo "🛡️ Setting up GitHub branch protection..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
if [ -z "$REPO" ]; then
    echo "❌ Not in a GitHub repository"
    exit 1
fi

echo "📦 Repository: $REPO"

# Function to set branch protection
set_branch_protection() {
    local BRANCH=$1
    echo "🔒 Protecting branch: $BRANCH"
    
    # Enable branch protection with all checks
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/repos/$REPO/branches/$BRANCH/protection" \
        --field required_status_checks='{"strict":true,"contexts":["Run Tests","Protection Validation","Merge Protection Gate"]}' \
        --field enforce_admins=true \
        --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field required_conversation_resolution=true \
        --field lock_branch=false
    
    if [ $? -eq 0 ]; then
        echo "✅ Branch $BRANCH protected"
    else
        echo "⚠️ Failed to protect $BRANCH (might need admin rights)"
    fi
}

# Create GitHub Actions secrets
echo "🔑 Setting up secrets..."
echo "Note: You'll need to manually add these secrets in GitHub Settings > Secrets:"
echo "  - DATABASE_URL"
echo "  - SECRET_KEY"
echo "  - CODECOV_TOKEN (optional)"

# Set up branch protection for main
set_branch_protection "main"

# Set up branch protection for develop (if exists)
if git show-ref --verify --quiet refs/heads/develop; then
    set_branch_protection "develop"
fi

# Create .github/CODEOWNERS file
echo "📝 Creating CODEOWNERS file..."
cat > .github/CODEOWNERS << 'EOF'
# Code Owners for automatic review requests

# Global owners
* @YOUR_GITHUB_USERNAME

# Backend protection
/app/core/security.py @YOUR_GITHUB_USERNAME
/app/core/dependencies.py @YOUR_GITHUB_USERNAME
/app/models/ @YOUR_GITHUB_USERNAME
/app/api/v1/auth.py @YOUR_GITHUB_USERNAME

# Test protection
/tests/ @YOUR_GITHUB_USERNAME

# CI/CD protection
/.github/ @YOUR_GITHUB_USERNAME
EOF

echo "⚠️ Remember to update .github/CODEOWNERS with your GitHub username"

# Create PR template
echo "📄 Creating PR template..."
mkdir -p .github
cat > .github/pull_request_template.md << 'EOF'
## Description
Brief description of changes

## Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🎨 Style update (formatting, renaming)
- [ ] ♻️ Code refactor (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update
- [ ] 🔧 Configuration change

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Test Results
```
Tests passed: XX/78
Coverage: XX%
```

## Breaking Changes
List any breaking changes and migration steps

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Additional Notes
Any additional information that reviewers should know
EOF

# Create issue templates
echo "📋 Creating issue templates..."
mkdir -p .github/ISSUE_TEMPLATE

cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: ''
---

## Describe the bug
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected behavior
A clear and concise description of what you expected to happen.

## Actual behavior
What actually happened

## Environment
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.11]
- Project version/commit: 

## Additional context
Add any other context about the problem here.
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement'
assignees: ''
---

## Is your feature request related to a problem?
A clear and concise description of what the problem is.

## Describe the solution you'd like
A clear and concise description of what you want to happen.

## Describe alternatives you've considered
A clear and concise description of any alternative solutions or features you've considered.

## Additional context
Add any other context or screenshots about the feature request here.

## Impact on existing code
- [ ] No breaking changes
- [ ] Minor breaking changes
- [ ] Major breaking changes

## Test requirements
Describe what tests would be needed for this feature
EOF

# Set up GitHub Pages for documentation (optional)
echo "📚 Setting up documentation..."
cat > .github/workflows/docs.yml << 'EOF'
name: Deploy Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - 'README.md'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install mkdocs mkdocs-material
    
    - name: Build documentation
      run: mkdocs build
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
EOF

echo "✅ GitHub protection setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .github/CODEOWNERS with your GitHub username"
echo "2. Go to Settings > Secrets and add required secrets"
echo "3. Go to Settings > Branches to verify protection rules"
echo "4. Create a PR to test the automation"
echo ""
echo "🔒 Protection features enabled:"
echo "  • Required status checks before merge"
echo "  • Required PR reviews"
echo "  • No force pushes"
echo "  • No branch deletion"
echo "  • Automated testing on every PR"
echo "  • Test regression detection"
echo "  • Security scanning"
echo "  • Docker build validation"