#!/bin/bash

# Script to update branch protection rules via GitHub API
# This removes e2e-login-test and react-error-handling from required checks

echo "🔧 Updating branch protection rules..."

# These should be the ONLY required checks
# Everything else should be optional
REQUIRED_CHECKS='[
  "Lint and Format",
  "Test Generator CLI",
  "Test API Endpoints Match"
]'

# Update branch protection using GitHub CLI
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/rafeekpro/stackwizard/branches/main/protection \
  -f "required_status_checks[strict]=true" \
  -f "required_status_checks[contexts][]=$REQUIRED_CHECKS" \
  -f "enforce_admins=false" \
  -f "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -f "required_pull_request_reviews[require_code_owner_reviews]=false" \
  -f "required_pull_request_reviews[required_approving_review_count]=1" \
  -f "allow_force_pushes=false" \
  -f "allow_deletions=false"

echo "✅ Branch protection updated!"
echo ""
echo "Required checks are now:"
echo "- Lint and Format"
echo "- Test Generator CLI" 
echo "- Test API Endpoints Match"
echo ""
echo "Optional checks (run conditionally):"
echo "- e2e-login-test"
echo "- react-error-handling"
echo "- react-router-test"