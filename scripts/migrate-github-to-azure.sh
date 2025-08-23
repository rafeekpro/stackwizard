#!/bin/bash

# ============================================================
# Migrate GitHub Issues to Azure DevOps Work Items
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       GitHub Issues → Azure DevOps Migration Tool         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if config exists
if [ ! -f ".azuredevops/config.json" ]; then
    echo -e "${RED}❌ Azure DevOps not configured. Run setup-azure-devops.sh first${NC}"
    exit 1
fi

# Load config
ORG_NAME=$(jq -r '.organization' .azuredevops/config.json)
PROJECT=$(jq -r '.project' .azuredevops/config.json)
ORG_URL="https://dev.azure.com/$ORG_NAME"

echo -e "${YELLOW}Organization: $ORG_NAME${NC}"
echo -e "${YELLOW}Project: $PROJECT${NC}"
echo ""

# Set Azure DevOps defaults
az devops configure --defaults organization="$ORG_URL" project="$PROJECT"

# Create mapping file
echo -e "${CYAN}Step 1: Fetching GitHub Issues${NC}"
echo "================================"

# Export all GitHub issues
gh issue list --limit 1000 --json number,title,body,labels,assignees,state,milestone,createdAt,updatedAt,comments > github-issues.json

ISSUE_COUNT=$(jq '. | length' github-issues.json)
echo -e "${GREEN}✅ Found $ISSUE_COUNT GitHub issues${NC}"

# Create label mapping
cat > label-mapping.json <<'EOF'
{
  "user-story": "User Story",
  "task": "Task",
  "bug": "Bug",
  "epic": "Epic",
  "enhancement": "User Story",
  "feature": "User Story",
  "documentation": "Task",
  "priority: critical": {"field": "Microsoft.VSTS.Common.Priority", "value": 1},
  "priority: high": {"field": "Microsoft.VSTS.Common.Priority", "value": 2},
  "priority: medium": {"field": "Microsoft.VSTS.Common.Priority", "value": 3},
  "priority: low": {"field": "Microsoft.VSTS.Common.Priority", "value": 4},
  "status: backlog": "New",
  "status: ready": "Approved",
  "status: in-progress": "Active",
  "status: review": "Active",
  "status: blocked": "Active",
  "status: done": "Closed",
  "sp: 1": {"field": "Microsoft.VSTS.Scheduling.StoryPoints", "value": 1},
  "sp: 2": {"field": "Microsoft.VSTS.Scheduling.StoryPoints", "value": 2},
  "sp: 3": {"field": "Microsoft.VSTS.Scheduling.StoryPoints", "value": 3},
  "sp: 5": {"field": "Microsoft.VSTS.Scheduling.StoryPoints", "value": 5},
  "sp: 8": {"field": "Microsoft.VSTS.Scheduling.StoryPoints", "value": 8},
  "sp: 13": {"field": "Microsoft.VSTS.Scheduling.StoryPoints", "value": 13}
}
EOF

echo -e "${CYAN}Step 2: Creating Azure DevOps Work Items${NC}"
echo "=========================================="

# Create migration report
echo "GitHub Issue,Azure Work Item,Title,Type,Status" > migration-report.csv

# Process each issue
jq -c '.[]' github-issues.json | while read -r issue; do
    # Extract fields
    GH_NUMBER=$(echo "$issue" | jq -r '.number')
    TITLE=$(echo "$issue" | jq -r '.title')
    BODY=$(echo "$issue" | jq -r '.body // ""')
    STATE=$(echo "$issue" | jq -r '.state')
    MILESTONE=$(echo "$issue" | jq -r '.milestone.title // ""')
    CREATED=$(echo "$issue" | jq -r '.createdAt')
    UPDATED=$(echo "$issue" | jq -r '.updatedAt')
    
    echo -e "${YELLOW}Processing GitHub Issue #$GH_NUMBER: $TITLE${NC}"
    
    # Determine work item type
    WORK_ITEM_TYPE="Task"  # Default
    LABELS=$(echo "$issue" | jq -r '.labels[].name' | tr '\n' ' ')
    
    if [[ $LABELS == *"user-story"* ]]; then
        WORK_ITEM_TYPE="User Story"
    elif [[ $LABELS == *"bug"* ]]; then
        WORK_ITEM_TYPE="Bug"
    elif [[ $LABELS == *"epic"* ]]; then
        WORK_ITEM_TYPE="Epic"
    elif [[ $LABELS == *"task"* ]]; then
        WORK_ITEM_TYPE="Task"
    fi
    
    # Determine state
    AZ_STATE="New"
    if [[ $STATE == "closed" ]]; then
        AZ_STATE="Closed"
    elif [[ $LABELS == *"status: done"* ]]; then
        AZ_STATE="Closed"
    elif [[ $LABELS == *"status: in-progress"* ]]; then
        AZ_STATE="Active"
    elif [[ $LABELS == *"status: ready"* ]]; then
        AZ_STATE="Approved"
    fi
    
    # Extract story points
    STORY_POINTS=""
    if [[ $LABELS == *"sp: "* ]]; then
        STORY_POINTS=$(echo "$LABELS" | grep -oE 'sp: [0-9]+' | sed 's/sp: //')
    fi
    
    # Extract priority
    PRIORITY=3  # Default medium
    if [[ $LABELS == *"priority: critical"* ]]; then
        PRIORITY=1
    elif [[ $LABELS == *"priority: high"* ]]; then
        PRIORITY=2
    elif [[ $LABELS == *"priority: low"* ]]; then
        PRIORITY=4
    fi
    
    # Determine area
    AREA="StackWizard"
    if [[ $LABELS == *"frontend"* ]]; then
        AREA="StackWizard\\Frontend"
    elif [[ $LABELS == *"backend"* ]]; then
        AREA="StackWizard\\Backend"
    elif [[ $LABELS == *"docker"* ]] || [[ $LABELS == *"devops"* ]]; then
        AREA="StackWizard\\DevOps"
    elif [[ $LABELS == *"cli"* ]]; then
        AREA="StackWizard\\CLI"
    fi
    
    # Set iteration based on milestone
    ITERATION="StackWizard"
    if [ ! -z "$MILESTONE" ]; then
        ITERATION="StackWizard\\$MILESTONE"
    fi
    
    # Add GitHub reference to body
    ENHANCED_BODY="$BODY

---
**Migrated from GitHub Issue #$GH_NUMBER**
Original URL: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/issues/$GH_NUMBER
Created: $CREATED
Updated: $UPDATED
Labels: $LABELS"
    
    # Create work item
    CREATE_CMD="az boards work-item create \
        --title \"$TITLE\" \
        --type \"$WORK_ITEM_TYPE\" \
        --area \"$AREA\" \
        --iteration \"$ITERATION\" \
        --state \"$AZ_STATE\" \
        --fields \"Description=$ENHANCED_BODY\" \
                 \"Microsoft.VSTS.Common.Priority=$PRIORITY\""
    
    # Add story points if applicable
    if [ ! -z "$STORY_POINTS" ] && [ "$WORK_ITEM_TYPE" = "User Story" ]; then
        CREATE_CMD="$CREATE_CMD \"Microsoft.VSTS.Scheduling.StoryPoints=$STORY_POINTS\""
    fi
    
    # Execute creation
    AZ_ID=$(eval "$CREATE_CMD --query id -o tsv" 2>/dev/null) || {
        echo -e "${RED}❌ Failed to create work item for issue #$GH_NUMBER${NC}"
        echo "#$GH_NUMBER,FAILED,\"$TITLE\",$WORK_ITEM_TYPE,$AZ_STATE" >> migration-report.csv
        continue
    }
    
    echo -e "${GREEN}✅ Created Azure Work Item #$AZ_ID${NC}"
    echo "#$GH_NUMBER,#$AZ_ID,\"$TITLE\",$WORK_ITEM_TYPE,$AZ_STATE" >> migration-report.csv
    
    # Migrate comments
    COMMENTS=$(echo "$issue" | jq -r '.comments[]?.body // empty' 2>/dev/null)
    if [ ! -z "$COMMENTS" ]; then
        echo "$COMMENTS" | while IFS= read -r comment; do
            if [ ! -z "$comment" ]; then
                az boards work-item update --id "$AZ_ID" \
                    --discussion "$comment" 2>/dev/null || true
            fi
        done
    fi
    
    # Add assignee if exists
    ASSIGNEE=$(echo "$issue" | jq -r '.assignees[0].login // ""')
    if [ ! -z "$ASSIGNEE" ]; then
        # Note: Assignee email mapping would need to be configured
        echo "  Note: Assignee $ASSIGNEE needs manual mapping in Azure DevOps"
    fi
    
    # Small delay to avoid rate limiting
    sleep 0.5
done

echo ""
echo -e "${CYAN}Step 3: Creating Issue Mapping${NC}"
echo "================================"

# Create mapping file for future reference
cat > .azuredevops/issue-mapping.json <<EOF
{
  "migration_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "github_repo": "$(gh repo view --json nameWithOwner -q .nameWithOwner)",
  "azure_project": "$PROJECT",
  "total_migrated": $ISSUE_COUNT
}
EOF

echo -e "${GREEN}✅ Mapping saved to .azuredevops/issue-mapping.json${NC}"

echo ""
echo -e "${CYAN}Step 4: Update GitHub Issues with Azure Links${NC}"
echo "================================================"

read -p "Add Azure DevOps links to GitHub issues? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    while IFS=, read -r gh_num az_num title type status; do
        if [[ $gh_num == "#"* ]] && [[ $az_num == "#"* ]]; then
            GH_ID=${gh_num:1}
            AZ_ID=${az_num:1}
            
            if [ "$AZ_ID" != "FAILED" ]; then
                echo "Updating GitHub issue #$GH_ID with Azure link..."
                
                COMMENT="🔄 **Migrated to Azure DevOps**
Work Item: #$AZ_ID
URL: https://dev.azure.com/$ORG_NAME/$PROJECT/_workitems/edit/$AZ_ID

This issue is now tracked in Azure DevOps for sprint planning and project management.
Continue using GitHub for code reviews and pull requests.

Reference this work item in PRs using: \`AB#$AZ_ID\`"
                
                gh issue comment "$GH_ID" --body "$COMMENT" 2>/dev/null || true
                
                # Add label to indicate migration
                gh issue edit "$GH_ID" --add-label "azure-migrated" 2>/dev/null || true
            fi
        fi
    done < migration-report.csv
    
    echo -e "${GREEN}✅ GitHub issues updated with Azure links${NC}"
fi

echo ""
echo -e "${CYAN}Step 5: Create Queries in Azure DevOps${NC}"
echo "========================================"

# Create migration query
az boards query create \
    --name "Migrated from GitHub" \
    --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = '$PROJECT' AND [System.Description] CONTAINS 'Migrated from GitHub Issue' ORDER BY [System.CreatedDate] DESC" \
    2>/dev/null || true

echo -e "${GREEN}✅ Query created for migrated items${NC}"

# Cleanup
rm github-issues.json label-mapping.json 2>/dev/null || true

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Migration Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📊 Migration Summary:${NC}"
echo "  Total issues processed: $ISSUE_COUNT"
echo "  Migration report: migration-report.csv"
echo ""
echo -e "${CYAN}📋 Next Steps:${NC}"
echo "  1. Review migrated items in Azure DevOps:"
echo "     ${BLUE}https://dev.azure.com/$ORG_NAME/$PROJECT/_workitems${NC}"
echo ""
echo "  2. Verify work item types and states are correct"
echo ""
echo "  3. Manually map GitHub users to Azure DevOps users"
echo ""
echo "  4. Close GitHub issues or add 'azure-migrated' label"
echo ""
echo -e "${YELLOW}⚠️  Note:${NC}"
echo "  - User assignments need manual mapping"
echo "  - File attachments are not migrated"
echo "  - PR links need to be updated manually"
echo ""
echo -e "${GREEN}Happy planning in Azure DevOps! 📈${NC}"