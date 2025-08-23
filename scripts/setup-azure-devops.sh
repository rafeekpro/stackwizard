#!/bin/bash

# ========================================================
# Azure DevOps + GitHub Integration Setup for StackWizard
# ========================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Azure DevOps + GitHub Integration Setup Wizard        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not installed${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    echo ""
    echo "macOS: brew install azure-cli"
    echo "Ubuntu: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi
echo -e "${GREEN}✅ Azure CLI installed${NC}"

# Check GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not installed${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi
echo -e "${GREEN}✅ GitHub CLI installed${NC}"

# Check jq
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq not installed - installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    else
        sudo apt-get install -y jq
    fi
fi
echo -e "${GREEN}✅ jq installed${NC}"

echo ""
echo -e "${CYAN}Step 1: Azure DevOps Configuration${NC}"
echo "====================================="

# Azure Login
echo -e "${YELLOW}Logging into Azure...${NC}"
az login --use-device-code

# Get or create organization
echo ""
read -p "Enter your Azure DevOps organization name (without https://): " ORG_NAME
ORG_URL="https://dev.azure.com/$ORG_NAME"

# Install Azure DevOps extension
echo -e "${YELLOW}Installing Azure DevOps CLI extension...${NC}"
az extension add --name azure-devops --yes 2>/dev/null || echo "Extension already installed"

# Create project
echo ""
read -p "Create new project 'StackWizard'? (y/n): " CREATE_PROJECT
if [[ $CREATE_PROJECT =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Creating Azure DevOps project...${NC}"
    az devops project create \
        --name "StackWizard" \
        --description "Full-stack project generator with FastAPI, React, PostgreSQL" \
        --org "$ORG_URL" \
        --process "Agile" \
        --visibility "private" || echo "Project might already exist"
fi

# Set defaults
az devops configure --defaults organization="$ORG_URL" project="StackWizard"
echo -e "${GREEN}✅ Azure DevOps configured${NC}"

echo ""
echo -e "${CYAN}Step 2: Create Work Item Types & Fields${NC}"
echo "========================================="

# Create Areas
echo -e "${YELLOW}Creating Area Paths...${NC}"
az boards area project create --name "Frontend" --path "\\StackWizard\\Area" 2>/dev/null || true
az boards area project create --name "Backend" --path "\\StackWizard\\Area" 2>/dev/null || true
az boards area project create --name "CLI" --path "\\StackWizard\\Area" 2>/dev/null || true
az boards area project create --name "DevOps" --path "\\StackWizard\\Area" 2>/dev/null || true
echo -e "${GREEN}✅ Areas created${NC}"

# Create Iterations (Sprints)
echo -e "${YELLOW}Creating Sprints...${NC}"
CURRENT_DATE=$(date +%Y-%m-%d)
SPRINT1_END=$(date -v+14d +%Y-%m-%d 2>/dev/null || date -d "+14 days" +%Y-%m-%d)
SPRINT2_START=$(date -v+15d +%Y-%m-%d 2>/dev/null || date -d "+15 days" +%Y-%m-%d)
SPRINT2_END=$(date -v+28d +%Y-%m-%d 2>/dev/null || date -d "+28 days" +%Y-%m-%d)

az boards iteration project create --name "Sprint 1" --start-date "$CURRENT_DATE" --finish-date "$SPRINT1_END" 2>/dev/null || true
az boards iteration project create --name "Sprint 2" --start-date "$SPRINT2_START" --finish-date "$SPRINT2_END" 2>/dev/null || true
echo -e "${GREEN}✅ Sprints created${NC}"

echo ""
echo -e "${CYAN}Step 3: GitHub Integration${NC}"
echo "============================"

# Get GitHub repo info
GITHUB_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${GREEN}GitHub Repository: $GITHUB_REPO${NC}"

# Create service connection
echo -e "${YELLOW}Creating GitHub service connection...${NC}"
read -p "Enter your GitHub Personal Access Token (with repo scope): " -s GITHUB_PAT
echo ""

# Create service endpoint JSON
cat > service-endpoint.json <<EOF
{
  "name": "GitHub-StackWizard",
  "type": "github",
  "url": "https://github.com/$GITHUB_REPO",
  "authorization": {
    "scheme": "Token",
    "parameters": {
      "AccessToken": "$GITHUB_PAT"
    }
  }
}
EOF

# Create service connection via API
echo -e "${YELLOW}Setting up service connection...${NC}"
az devops service-endpoint github create --github-service-endpoint-configuration service-endpoint.json 2>/dev/null || echo "Connection might already exist"
rm service-endpoint.json

echo -e "${GREEN}✅ GitHub connected to Azure DevOps${NC}"

echo ""
echo -e "${CYAN}Step 4: Create Sample Work Items${NC}"
echo "=================================="

# Create Epic
echo -e "${YELLOW}Creating sample Epic...${NC}"
EPIC_ID=$(az boards work-item create \
    --title "Version 1.1.0 - Database Flexibility" \
    --type "Epic" \
    --fields "Description=Support for multiple database systems (PostgreSQL, MySQL, MongoDB)" \
    --query "id" -o tsv)
echo -e "${GREEN}✅ Epic created: #$EPIC_ID${NC}"

# Create User Story
echo -e "${YELLOW}Creating sample User Story...${NC}"
US_ID=$(az boards work-item create \
    --title "As a developer, I want to choose between PostgreSQL and MySQL" \
    --type "User Story" \
    --area "StackWizard\\Backend" \
    --iteration "StackWizard\\Sprint 1" \
    --fields "Description=Allow database selection during project generation" \
             "Microsoft.VSTS.Common.AcceptanceCriteria=<ul><li>CLI prompts for database choice</li><li>Docker compose configured correctly</li><li>Migrations work with both databases</li></ul>" \
             "Microsoft.VSTS.Scheduling.StoryPoints=8" \
    --parent "$EPIC_ID" \
    --query "id" -o tsv)
echo -e "${GREEN}✅ User Story created: #$US_ID${NC}"

# Create Tasks
echo -e "${YELLOW}Creating sample Tasks...${NC}"
TASK1_ID=$(az boards work-item create \
    --title "Add database selection to CLI prompts" \
    --type "Task" \
    --parent "$US_ID" \
    --fields "Microsoft.VSTS.Scheduling.OriginalEstimate=4" \
             "Description=Update inquirer prompts in src/index.js" \
    --query "id" -o tsv)
echo -e "${GREEN}✅ Task created: #$TASK1_ID${NC}"

TASK2_ID=$(az boards work-item create \
    --title "Create MySQL Docker template" \
    --type "Task" \
    --parent "$US_ID" \
    --fields "Microsoft.VSTS.Scheduling.OriginalEstimate=3" \
             "Description=Create docker-compose template for MySQL" \
    --query "id" -o tsv)
echo -e "${GREEN}✅ Task created: #$TASK2_ID${NC}"

echo ""
echo -e "${CYAN}Step 5: Create GitHub Action Workflow${NC}"
echo "======================================="

# Create workflow file
mkdir -p .github/workflows
cat > .github/workflows/azure-boards-sync.yml <<'EOF'
name: Azure Boards Integration

on:
  pull_request:
    types: [opened, edited, closed, reopened]
  pull_request_review:
    types: [submitted]
  issues:
    types: [opened, closed, reopened, edited]
  push:
    branches: [main]

env:
  AZURE_DEVOPS_ORG: ORG_NAME_PLACEHOLDER
  AZURE_DEVOPS_PROJECT: StackWizard

jobs:
  sync-with-azure-boards:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Azure CLI
        uses: azure/CLI@v1
        with:
          azcliversion: latest
          inlineScript: |
            az extension add --name azure-devops

      - name: Azure Login
        env:
          AZURE_DEVOPS_PAT: ${{ secrets.AZURE_DEVOPS_PAT }}
        run: |
          echo $AZURE_DEVOPS_PAT | az devops login --org https://dev.azure.com/${{ env.AZURE_DEVOPS_ORG }}

      - name: Extract Work Item IDs
        id: extract
        run: |
          # Extract AB#123 patterns from PR/Issue
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            BODY="${{ github.event.pull_request.body }}"
            TITLE="${{ github.event.pull_request.title }}"
          else
            BODY="${{ github.event.issue.body }}"
            TITLE="${{ github.event.issue.title }}"
          fi
          
          # Find all AB#123 references
          WORK_ITEMS=$(echo "$TITLE $BODY" | grep -oE 'AB#[0-9]+' | sed 's/AB#//' | tr '\n' ' ')
          echo "work_items=$WORK_ITEMS" >> $GITHUB_OUTPUT
          echo "Found work items: $WORK_ITEMS"

      - name: Update Work Item Status
        if: steps.extract.outputs.work_items != ''
        run: |
          WORK_ITEMS="${{ steps.extract.outputs.work_items }}"
          EVENT="${{ github.event_name }}"
          ACTION="${{ github.event.action }}"
          
          for WI in $WORK_ITEMS; do
            echo "Processing work item #$WI"
            
            # Update based on event
            if [ "$EVENT" = "pull_request" ]; then
              if [ "$ACTION" = "opened" ] || [ "$ACTION" = "reopened" ]; then
                # Move to In Progress
                az boards work-item update --id $WI --state "Active" \
                  --org https://dev.azure.com/${{ env.AZURE_DEVOPS_ORG }} \
                  --project ${{ env.AZURE_DEVOPS_PROJECT }}
                
                # Add PR link
                az boards work-item relation add --id $WI \
                  --relation-type "GitHub Pull Request" \
                  --target-url "${{ github.event.pull_request.html_url }}" \
                  --org https://dev.azure.com/${{ env.AZURE_DEVOPS_ORG }} \
                  --project ${{ env.AZURE_DEVOPS_PROJECT }}
                  
              elif [ "$ACTION" = "closed" ] && [ "${{ github.event.pull_request.merged }}" = "true" ]; then
                # Move to Done
                az boards work-item update --id $WI --state "Closed" \
                  --org https://dev.azure.com/${{ env.AZURE_DEVOPS_ORG }} \
                  --project ${{ env.AZURE_DEVOPS_PROJECT }}
              fi
            fi
            
            # Add comment about the event
            COMMENT="GitHub $EVENT $ACTION by @${{ github.actor }}"
            if [ "$EVENT" = "pull_request" ]; then
              COMMENT="$COMMENT - PR #${{ github.event.pull_request.number }}: ${{ github.event.pull_request.title }}"
            fi
            
            az boards work-item update --id $WI --discussion "$COMMENT" \
              --org https://dev.azure.com/${{ env.AZURE_DEVOPS_ORG }} \
              --project ${{ env.AZURE_DEVOPS_PROJECT }}
          done

      - name: Update Sprint Metrics
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          echo "Updating sprint metrics in Azure DevOps..."
          # This would update velocity, burndown, etc.
EOF

# Replace placeholder
sed -i.bak "s/ORG_NAME_PLACEHOLDER/$ORG_NAME/g" .github/workflows/azure-boards-sync.yml
rm .github/workflows/azure-boards-sync.yml.bak 2>/dev/null || true

echo -e "${GREEN}✅ GitHub Action workflow created${NC}"

echo ""
echo -e "${CYAN}Step 6: Setup GitHub Secrets${NC}"
echo "=============================="

echo -e "${YELLOW}Creating GitHub secrets...${NC}"

# Create PAT for Azure DevOps
echo -e "${BLUE}You need to create a Personal Access Token in Azure DevOps:${NC}"
echo "1. Go to: https://dev.azure.com/$ORG_NAME/_usersSettings/tokens"
echo "2. Create new token with scopes: Work Items (Read & Write)"
echo "3. Copy the token"
echo ""
read -p "Enter your Azure DevOps PAT: " -s AZURE_PAT
echo ""

# Set GitHub secret
gh secret set AZURE_DEVOPS_PAT --body "$AZURE_PAT"
echo -e "${GREEN}✅ GitHub secret configured${NC}"

echo ""
echo -e "${CYAN}Step 7: Create Dashboard${NC}"
echo "=========================="

# Create queries
echo -e "${YELLOW}Creating useful queries...${NC}"

# Current Sprint Work
az boards query create \
    --name "Current Sprint Work" \
    --wiql "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo] FROM WorkItems WHERE [System.TeamProject] = 'StackWizard' AND [System.IterationPath] UNDER 'StackWizard\\Sprint 1' AND [System.State] <> 'Closed' ORDER BY [Microsoft.VSTS.Common.Priority] ASC, [System.CreatedDate] DESC" \
    2>/dev/null || true

# My Work Items
az boards query create \
    --name "My Work Items" \
    --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = 'StackWizard' AND [System.AssignedTo] = @Me AND [System.State] <> 'Closed' ORDER BY [System.ChangedDate] DESC" \
    2>/dev/null || true

echo -e "${GREEN}✅ Queries created${NC}"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Azure DevOps + GitHub Integration Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📋 What's been configured:${NC}"
echo "  ✅ Azure DevOps project: StackWizard"
echo "  ✅ Areas: Frontend, Backend, CLI, DevOps"
echo "  ✅ Sprints: Sprint 1 & 2"
echo "  ✅ Sample work items: Epic #$EPIC_ID, User Story #$US_ID, Tasks #$TASK1_ID, #$TASK2_ID"
echo "  ✅ GitHub integration workflow"
echo "  ✅ Automated status sync"
echo ""
echo -e "${CYAN}🚀 How to use:${NC}"
echo ""
echo "1. In your commits and PRs, reference Azure work items:"
echo "   ${YELLOW}git commit -m \"feat: Add MySQL support"
echo "   "
echo "   Implements AB#$US_ID\""
echo "   "
echo "   gh pr create --body \"Fixes AB#$TASK1_ID\"${NC}"
echo ""
echo "2. View your Azure DevOps board:"
echo "   ${BLUE}https://dev.azure.com/$ORG_NAME/StackWizard/_boards${NC}"
echo ""
echo "3. View sprint burndown:"
echo "   ${BLUE}https://dev.azure.com/$ORG_NAME/StackWizard/_sprints${NC}"
echo ""
echo "4. View dashboards:"
echo "   ${BLUE}https://dev.azure.com/$ORG_NAME/StackWizard/_dashboards${NC}"
echo ""
echo -e "${CYAN}📚 Quick Commands:${NC}"
echo ""
echo "  List work items:"
echo "    ${YELLOW}az boards work-item list --query \"[?fields.'System.State' != 'Closed']\"${NC}"
echo ""
echo "  Create new user story:"
echo "    ${YELLOW}az boards work-item create --type \"User Story\" --title \"Your title\"${NC}"
echo ""
echo "  Update work item:"
echo "    ${YELLOW}az boards work-item update --id 123 --state \"Active\"${NC}"
echo ""
echo -e "${MAGENTA}💡 Next steps:${NC}"
echo "  1. Commit the GitHub Action workflow"
echo "  2. Test by creating a PR with 'AB#$US_ID' in description"
echo "  3. Customize the workflow as needed"
echo "  4. Add team members to Azure DevOps project"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"

# Save configuration
cat > .azuredevops/config.json <<EOF
{
  "organization": "$ORG_NAME",
  "project": "StackWizard",
  "epic_id": "$EPIC_ID",
  "sample_user_story": "$US_ID",
  "sample_tasks": ["$TASK1_ID", "$TASK2_ID"]
}
EOF

echo ""
echo -e "${YELLOW}Configuration saved to .azuredevops/config.json${NC}"