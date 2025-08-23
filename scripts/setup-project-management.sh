#!/bin/bash

echo "🚀 Setting up Project Management System for StackWizard"
echo "======================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with GitHub${NC}"
    echo "Running: gh auth login"
    gh auth login
fi

echo -e "\n${GREEN}Step 1: Creating GitHub Labels${NC}"
echo "--------------------------------"

# Create labels one by one
echo "Creating priority labels..."
gh label create "priority: critical" -c "d73a4a" -d "Critical priority - must be done ASAP" 2>/dev/null || echo "Label 'priority: critical' already exists"
gh label create "priority: high" -c "ff6b6b" -d "High priority" 2>/dev/null || echo "Label 'priority: high' already exists"
gh label create "priority: medium" -c "fbca04" -d "Medium priority" 2>/dev/null || echo "Label 'priority: medium' already exists"
gh label create "priority: low" -c "0e8a16" -d "Low priority" 2>/dev/null || echo "Label 'priority: low' already exists"

echo "Creating type labels..."
gh label create "user-story" -c "7057ff" -d "User Story - high-level requirement" 2>/dev/null || echo "Label 'user-story' already exists"
gh label create "task" -c "0052cc" -d "Development task" 2>/dev/null || echo "Label 'task' already exists"
gh label create "epic" -c "3e4b9e" -d "Epic - collection of user stories" 2>/dev/null || echo "Label 'epic' already exists"
gh label create "bug" -c "d73a4a" -d "Something isn't working" 2>/dev/null || echo "Label 'bug' already exists"
gh label create "enhancement" -c "a2eeef" -d "New feature or request" 2>/dev/null || echo "Label 'enhancement' already exists"

echo "Creating status labels..."
gh label create "status: backlog" -c "cfd3d7" -d "In backlog" 2>/dev/null || echo "Label 'status: backlog' already exists"
gh label create "status: ready" -c "bfdadc" -d "Ready for development" 2>/dev/null || echo "Label 'status: ready' already exists"
gh label create "status: in-progress" -c "2ea44f" -d "Work in progress" 2>/dev/null || echo "Label 'status: in-progress' already exists"
gh label create "status: review" -c "8b4789" -d "In review" 2>/dev/null || echo "Label 'status: review' already exists"
gh label create "status: blocked" -c "d73a4a" -d "Blocked by dependency" 2>/dev/null || echo "Label 'status: blocked' already exists"
gh label create "status: done" -c "0e8a16" -d "Completed" 2>/dev/null || echo "Label 'status: done' already exists"

echo "Creating story point labels..."
gh label create "sp: 1" -c "c5def5" -d "1 story point" 2>/dev/null || echo "Label 'sp: 1' already exists"
gh label create "sp: 2" -c "c5def5" -d "2 story points" 2>/dev/null || echo "Label 'sp: 2' already exists"
gh label create "sp: 3" -c "c5def5" -d "3 story points" 2>/dev/null || echo "Label 'sp: 3' already exists"
gh label create "sp: 5" -c "c5def5" -d "5 story points" 2>/dev/null || echo "Label 'sp: 5' already exists"
gh label create "sp: 8" -c "c5def5" -d "8 story points" 2>/dev/null || echo "Label 'sp: 8' already exists"
gh label create "sp: 13" -c "c5def5" -d "13 story points" 2>/dev/null || echo "Label 'sp: 13' already exists"

echo "Creating category labels..."
gh label create "frontend" -c "d4c5f9" -d "Frontend related" 2>/dev/null || echo "Label 'frontend' already exists"
gh label create "backend" -c "fef2c0" -d "Backend related" 2>/dev/null || echo "Label 'backend' already exists"
gh label create "docker" -c "006b75" -d "Docker/DevOps related" 2>/dev/null || echo "Label 'docker' already exists"
gh label create "cli" -c "5319e7" -d "CLI generator related" 2>/dev/null || echo "Label 'cli' already exists"
gh label create "documentation" -c "0075ca" -d "Documentation improvements" 2>/dev/null || echo "Label 'documentation' already exists"
gh label create "testing" -c "a2eeef" -d "Testing related" 2>/dev/null || echo "Label 'testing' already exists"

echo "Creating process labels..."
gh label create "needs-refinement" -c "d876e3" -d "Needs more details or refinement" 2>/dev/null || echo "Label 'needs-refinement' already exists"
gh label create "needs-discussion" -c "f9d0c4" -d "Needs team discussion" 2>/dev/null || echo "Label 'needs-discussion' already exists"
gh label create "needs-triage" -c "e99695" -d "Needs priority assignment" 2>/dev/null || echo "Label 'needs-triage' already exists"
gh label create "good-first-issue" -c "7057ff" -d "Good for newcomers" 2>/dev/null || echo "Label 'good-first-issue' already exists"

echo -e "${GREEN}✅ Labels created successfully!${NC}"

echo -e "\n${GREEN}Step 2: Creating Milestones${NC}"
echo "--------------------------------"

# Create milestones for releases
gh api repos/:owner/:repo/milestones -f title="v1.1.0 - Database Flexibility" -f description="Support for multiple databases (PostgreSQL, MySQL, MongoDB)" -f due_on="2025-09-30T23:59:59Z" 2>/dev/null || echo "Milestone v1.1.0 already exists"
gh api repos/:owner/:repo/milestones -f title="v1.2.0 - Frontend Expansion" -f description="More frontend framework options (Vue, Next.js, Svelte)" -f due_on="2025-10-31T23:59:59Z" 2>/dev/null || echo "Milestone v1.2.0 already exists"
gh api repos/:owner/:repo/milestones -f title="v1.3.0 - Advanced Authentication" -f description="OAuth2, 2FA, and RBAC support" -f due_on="2025-11-30T23:59:59Z" 2>/dev/null || echo "Milestone v1.3.0 already exists"

echo -e "${GREEN}✅ Milestones created!${NC}"

echo -e "\n${GREEN}Step 3: Setting up GitHub Project (Optional)${NC}"
echo "--------------------------------"
echo "To create a project board, you need to:"
echo "1. Go to: https://github.com/rafeekpro/stackwizard/projects"
echo "2. Click 'New project'"
echo "3. Choose 'Board' template"
echo "4. Name it: 'StackWizard Development Board'"
echo "5. Add columns: Backlog | Ready | In Progress | In Review | Done"

echo -e "\n${GREEN}Step 4: Creating Sample Issues${NC}"
echo "--------------------------------"
read -p "Do you want to create sample User Stories and Tasks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./scripts/create-sample-issues.sh
else
    echo "Skipping sample issues creation"
fi

echo -e "\n${GREEN}🎉 Project Management System Setup Complete!${NC}"
echo "============================================="
echo ""
echo "📋 What's been set up:"
echo "  ✅ GitHub Labels for issue management"
echo "  ✅ Milestones for release planning"
echo "  ✅ Issue templates in .github/ISSUE_TEMPLATE/"
echo "  ✅ ROADMAP.md with planned features"
echo "  ✅ SPRINTS.md for sprint tracking"
echo ""
echo "🚀 Next steps:"
echo "  1. Create your first User Story:"
echo "     gh issue create --template user-story.md"
echo ""
echo "  2. View all User Stories:"
echo "     gh issue list --label 'user-story'"
echo ""
echo "  3. View current sprint tasks:"
echo "     gh issue list --label 'status: in-progress'"
echo ""
echo "  4. Create a task:"
echo "     gh issue create --template task.md"
echo ""
echo "  5. Move task to in-progress:"
echo "     gh issue edit <number> --add-label 'status: in-progress' --remove-label 'status: ready'"
echo ""
echo "📚 Documentation:"
echo "  - ROADMAP.md: Long-term planning"
echo "  - SPRINTS.md: Sprint management"
echo "  - .github/ISSUE_TEMPLATE/: Issue templates"
echo ""
echo "🔗 Useful links:"
echo "  - Issues: https://github.com/rafeekpro/stackwizard/issues"
echo "  - Milestones: https://github.com/rafeekpro/stackwizard/milestones"
echo "  - Projects: https://github.com/rafeekpro/stackwizard/projects"