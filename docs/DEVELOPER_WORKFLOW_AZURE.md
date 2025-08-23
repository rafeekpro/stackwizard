# 👨‍💻 Developer Workflow: Azure DevOps + GitHub

## 📚 Quick Reference

### Linking Work Items in Git
```bash
# In commit messages
git commit -m "feat: Add dark mode

Implements AB#234"

# In PR descriptions
Fixes AB#567
Related to AB#890
```

## 🎯 Daily Developer Workflow

### Morning: Check Your Work

#### Option 1: Azure DevOps Board
```bash
# Open browser
open https://dev.azure.com/yourorg/StackWizard/_boards

# Or use CLI
az boards work-item list --assigned-to "@me" --state "Active"
```

#### Option 2: CLI Quick Check
```bash
# Create alias in ~/.bashrc or ~/.zshrc
alias my-work='az boards work-item list --assigned-to "@me" --query "[?fields.\"System.State\" != \"Closed\"].{ID:id, Title:fields.\"System.Title\", State:fields.\"System.State\"}" -o table'

# Use it
my-work
```

### Start Working on a Task

#### 1. Find Your Task
```bash
# List sprint backlog
az boards work-item list --area "StackWizard" --iteration "StackWizard\Sprint 1" -o table

# Output:
# ID    Title                                    State      Assigned To
# ----  ---------------------------------------  ---------  -----------
# 234   Add database selection to CLI            Approved   Unassigned
# 567   Fix navigation auth state                Active     you@email.com
```

#### 2. Assign & Start Task
```bash
# Take the task
TASK_ID=234
az boards work-item update --id $TASK_ID --assigned-to "@me" --state "Active"

# Add initial comment
az boards work-item update --id $TASK_ID --discussion "Starting work on this task"
```

#### 3. Create Feature Branch
```bash
# ALWAYS include AB#ID in branch name for easy reference
git checkout -b feature/AB-234-database-selection

# Or for bugs
git checkout -b bugfix/AB-567-nav-auth-fix
```

#### 4. Code Your Solution
```bash
# Make changes...
code src/index.js

# Test locally
npm test

# Stage changes
git add .
```

#### 5. Commit with Azure Reference
```bash
# ✅ GOOD: Clear reference to work item
git commit -m "feat: Add database selection prompt to CLI

Implements AB#234
- Added PostgreSQL/MySQL selection
- Updated docker-compose generation
- Added validation for database type"

# ❌ BAD: No reference
git commit -m "Add database selection"
```

#### 6. Push and Create PR
```bash
# Push branch
git push -u origin feature/AB-234-database-selection

# Create PR with Azure reference
gh pr create \
  --title "AB#234: Add database selection to CLI" \
  --body "## Description
Implements database selection feature as specified in AB#234

## Changes
- Added database prompt to CLI
- Created MySQL docker template
- Updated configuration handling

## Testing
- [x] Manual testing with PostgreSQL
- [x] Manual testing with MySQL
- [x] Unit tests passing

Fixes AB#234"
```

### During Code Review

#### Add Review Comments to Azure
```bash
# When PR needs changes
az boards work-item update --id 234 \
  --discussion "PR #48 has review comments - updating based on feedback"

# When blocked
az boards work-item update --id 234 \
  --state "Active" \
  --fields "System.Tags=Blocked" \
  --discussion "Blocked: Waiting for design approval"
```

### After PR Merge

#### Automatic Updates
When PR with `Fixes AB#234` is merged:
- ✅ Work item moves to "Closed" automatically
- ✅ PR link added to work item
- ✅ Completion time logged

#### Manual Time Logging (Optional)
```bash
# Log actual hours worked
az boards work-item update --id 234 \
  --fields "Microsoft.VSTS.Scheduling.CompletedWork=6" \
           "Microsoft.VSTS.Scheduling.RemainingWork=0"
```

## 📋 Common Scenarios

### Scenario 1: Bug Found During Development
```bash
# Create bug linked to current story
PARENT_ID=234
BUG_ID=$(az boards work-item create \
  --title "Database connection fails with special characters" \
  --type "Bug" \
  --parent $PARENT_ID \
  --fields "Microsoft.VSTS.Common.Priority=2" \
           "Description=Special characters in password cause connection failure" \
  --query "id" -o tsv)

# Create bugfix branch
git checkout -b bugfix/AB-$BUG_ID-special-chars

# Fix and commit
git commit -m "fix: Escape special characters in database password

Fixes AB#$BUG_ID
Related to AB#$PARENT_ID"
```

### Scenario 2: Task Bigger Than Expected
```bash
# Update estimate
az boards work-item update --id 234 \
  --fields "Microsoft.VSTS.Scheduling.OriginalEstimate=8" \
           "Microsoft.VSTS.Scheduling.RemainingWork=6" \
  --discussion "Task more complex than expected - involves refactoring existing code"

# Create subtasks
az boards work-item create \
  --title "Refactor database configuration module" \
  --type "Task" \
  --parent 234 \
  --fields "Microsoft.VSTS.Scheduling.OriginalEstimate=3"
```

### Scenario 3: Multiple PRs for One Story
```bash
# First PR - Backend changes
git commit -m "feat: Backend support for MySQL

Implements AB#234 (backend)
- Added MySQL driver
- Updated models for MySQL compatibility"

# Second PR - Frontend changes  
git commit -m "feat: Update UI for database selection

Implements AB#234 (frontend)
- Added database dropdown
- Updated validation"

# Both PRs link to same work item!
```

## 🚀 Sprint Ceremonies

### Daily Standup
```bash
# Before standup, run:
./scripts/azure-standup.sh

# Or manually:
echo "📅 $(date '+%A, %B %d')"
echo "Yesterday:"
az boards work-item list --assigned-to "@me" --changed-date "1 day" -o table

echo "Today:"
az boards work-item list --assigned-to "@me" --state "Active" -o table

echo "Blockers:"
az boards work-item list --assigned-to "@me" --tags "Blocked" -o table
```

### Sprint Planning
```bash
# Move items to sprint
az boards work-item update --id 234 \
  --iteration "StackWizard\Sprint 2" \
  --fields "Microsoft.VSTS.Common.Priority=2"

# Batch update
for id in 234 567 890; do
  az boards work-item update --id $id --iteration "StackWizard\Sprint 2"
done
```

### Sprint Review
```bash
# Show completed work
az boards query --wiql \
  "SELECT [System.Id], [System.Title] 
   FROM WorkItems 
   WHERE [System.IterationPath] = 'StackWizard\Sprint 1' 
   AND [System.State] = 'Closed'"
```

## 🔧 Useful Aliases & Functions

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Azure DevOps aliases
alias azb='az boards'
alias my-work='az boards work-item list --assigned-to "@me" --state "Active" -o table'
alias sprint='az boards work-item list --iteration "@CurrentIteration" -o table'

# Function to create branch with work item
function feature() {
  if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: feature <work-item-id> <branch-description>"
    echo "Example: feature 234 database-selection"
    return 1
  fi
  
  git checkout -b feature/AB-$1-$2
  echo "Created branch: feature/AB-$1-$2"
  echo "Remember to reference AB#$1 in your commits!"
}

# Function to start work on item
function start-work() {
  if [ -z "$1" ]; then
    echo "Usage: start-work <work-item-id>"
    return 1
  fi
  
  # Update Azure
  az boards work-item update --id $1 --assigned-to "@me" --state "Active"
  
  # Get title for branch name
  TITLE=$(az boards work-item show --id $1 --query "fields.\"System.Title\"" -o tsv)
  BRANCH_NAME=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | cut -c1-30)
  
  # Create branch
  git checkout -b feature/AB-$1-$BRANCH_NAME
  
  echo "✅ Started work on AB#$1"
  echo "📌 Branch: feature/AB-$1-$BRANCH_NAME"
}

# Function to finish work
function finish-work() {
  if [ -z "$1" ]; then
    echo "Usage: finish-work <work-item-id>"
    return 1
  fi
  
  # Create PR
  gh pr create \
    --title "AB#$1: $(az boards work-item show --id $1 --query 'fields.\"System.Title\"' -o tsv)" \
    --body "Fixes AB#$1"
  
  echo "✅ PR created for AB#$1"
}
```

## 📊 VSCode Integration

### Install Extensions
```bash
code --install-extension ms-vsts.team
code --install-extension GitHub.vscode-pull-request-github
```

### Settings.json
```json
{
  "azure-boards.organization": "https://dev.azure.com/yourorg",
  "azure-boards.project": "StackWizard",
  "azure-boards.autoRefresh": true,
  "git.commitMessageFormat": "feat: ${input}\n\nImplements AB#${workItemId}"
}
```

## 🎯 Best Practices

### ✅ DO:
- Always reference AB#ID in commits and PRs
- Update work item state as you progress
- Log blockers immediately
- Keep work items small (< 8 hours)
- Comment on work items for important decisions

### ❌ DON'T:
- Work on tasks not assigned to you without asking
- Forget to reference work items in commits
- Leave work items in "Active" when blocked
- Create huge PRs (split them)
- Skip daily status updates

## 🆘 Troubleshooting

### Work item not updating from PR
```bash
# Check if reference is correct
grep -E "AB#[0-9]+" .git/COMMIT_EDITMSG

# Manually link PR to work item
az boards work-item relation add \
  --id 234 \
  --relation-type "GitHub Pull Request" \
  --target-url "https://github.com/org/repo/pull/48"
```

### Can't find work item
```bash
# Search by keyword
az boards query --wiql \
  "SELECT [System.Id], [System.Title] 
   FROM WorkItems 
   WHERE [System.Title] CONTAINS 'database'"

# List all your items
az boards work-item list --assigned-to "@me"
```

### Sync issues
```bash
# Force sync
gh workflow run azure-boards-sync.yml

# Check workflow status
gh run list --workflow=azure-boards-sync.yml
```

## 📚 Quick Commands Cheatsheet

```bash
# Work Items
az boards work-item create --type "Task" --title "Title"
az boards work-item update --id 234 --state "Active"
az boards work-item show --id 234
az boards work-item list --assigned-to "@me"

# Queries
az boards query --id [query-guid]
az boards query --wiql "SELECT ..."

# Iterations
az boards iteration project list
az boards iteration team list

# Areas
az boards area project list

# Git/GitHub
git commit -m "message\n\nFixes AB#234"
gh pr create --body "Implements AB#234"
```

---

**Remember:** The magic is in `AB#123` - use it everywhere! 🪄