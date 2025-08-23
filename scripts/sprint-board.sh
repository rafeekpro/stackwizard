#!/bin/bash

# Simple Sprint Board CLI for StackWizard
# Usage: ./sprint-board.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           🏃 StackWizard Sprint Board 🏃                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

while true; do
    echo -e "${GREEN}What would you like to do?${NC}"
    echo ""
    echo "  ${YELLOW}--- View ---${NC}"
    echo "  1) 📋 View Sprint Board"
    echo "  2) 📝 View All User Stories"
    echo "  3) ✅ View My Tasks"
    echo "  4) 🔍 Search Issues"
    echo ""
    echo "  ${YELLOW}--- Create ---${NC}"
    echo "  5) 🎯 Create User Story"
    echo "  6) 📌 Create Task"
    echo "  7) 🐛 Report Bug"
    echo "  8) 💡 Request Feature"
    echo ""
    echo "  ${YELLOW}--- Update ---${NC}"
    echo "  9) ▶️  Start Working on Task"
    echo "  10) ✔️  Complete Task"
    echo "  11) 🚫 Block Task"
    echo "  12) 👀 Move to Review"
    echo ""
    echo "  ${YELLOW}--- Reports ---${NC}"
    echo "  13) 📊 Sprint Velocity"
    echo "  14) 📈 Burndown Chart"
    echo "  15) 🏆 Completed This Sprint"
    echo ""
    echo "  0) Exit"
    echo ""
    read -p "Select option: " choice

    case $choice in
        1)
            echo -e "\n${CYAN}📋 Current Sprint Board${NC}"
            echo "========================"
            echo -e "\n${YELLOW}📦 BACKLOG:${NC}"
            gh issue list --label "status: backlog" --limit 5
            echo -e "\n${BLUE}🔵 READY:${NC}"
            gh issue list --label "status: ready" --limit 5
            echo -e "\n${GREEN}🟢 IN PROGRESS:${NC}"
            gh issue list --label "status: in-progress" --limit 5
            echo -e "\n${MAGENTA}👀 IN REVIEW:${NC}"
            gh issue list --label "status: review" --limit 5
            echo -e "\n${RED}🔴 BLOCKED:${NC}"
            gh issue list --label "status: blocked" --limit 5
            ;;
        
        2)
            echo -e "\n${CYAN}📝 All User Stories${NC}"
            echo "==================="
            gh issue list --label "user-story" --limit 20
            ;;
        
        3)
            echo -e "\n${CYAN}✅ My Tasks${NC}"
            echo "==========="
            gh issue list --assignee "@me" --limit 20
            ;;
        
        4)
            read -p "Enter search term: " search_term
            echo -e "\n${CYAN}🔍 Search Results for: $search_term${NC}"
            echo "================================"
            gh issue list --search "$search_term"
            ;;
        
        5)
            echo -e "\n${GREEN}Creating User Story...${NC}"
            gh issue create --template user-story.md
            ;;
        
        6)
            echo -e "\n${GREEN}Creating Task...${NC}"
            gh issue create --template task.md
            ;;
        
        7)
            echo -e "\n${RED}Reporting Bug...${NC}"
            gh issue create --template bug_report.md
            ;;
        
        8)
            echo -e "\n${YELLOW}Requesting Feature...${NC}"
            gh issue create --template feature_request.md
            ;;
        
        9)
            read -p "Enter issue number to start: #" issue_num
            echo -e "${GREEN}Moving #$issue_num to In Progress...${NC}"
            gh issue edit $issue_num \
                --add-label "status: in-progress" \
                --remove-label "status: ready,status: backlog" \
                --add-assignee "@me"
            echo "✅ Task #$issue_num is now in progress and assigned to you!"
            ;;
        
        10)
            read -p "Enter issue number to complete: #" issue_num
            echo -e "${GREEN}Marking #$issue_num as Done...${NC}"
            gh issue edit $issue_num \
                --add-label "status: done" \
                --remove-label "status: in-progress,status: review,status: blocked"
            read -p "Close the issue? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                gh issue close $issue_num
                echo "✅ Issue #$issue_num completed and closed!"
            else
                echo "✅ Issue #$issue_num marked as done!"
            fi
            ;;
        
        11)
            read -p "Enter issue number to block: #" issue_num
            read -p "Reason for blocking: " block_reason
            echo -e "${RED}Blocking #$issue_num...${NC}"
            gh issue edit $issue_num \
                --add-label "status: blocked" \
                --remove-label "status: in-progress"
            gh issue comment $issue_num --body "🚫 **BLOCKED**: $block_reason"
            echo "⛔ Task #$issue_num is now blocked!"
            ;;
        
        12)
            read -p "Enter issue number to review: #" issue_num
            echo -e "${MAGENTA}Moving #$issue_num to Review...${NC}"
            gh issue edit $issue_num \
                --add-label "status: review" \
                --remove-label "status: in-progress"
            echo "👀 Task #$issue_num is now in review!"
            ;;
        
        13)
            echo -e "\n${CYAN}📊 Sprint Velocity${NC}"
            echo "=================="
            echo "Story Points by Status:"
            echo ""
            for sp in 1 2 3 5 8 13; do
                count=$(gh issue list --label "sp: $sp" --label "status: done" --json number --jq '. | length')
                total=$((count * sp))
                echo "  ${sp} points: $count issues = $total points"
            done
            ;;
        
        14)
            echo -e "\n${CYAN}📈 Sprint Burndown${NC}"
            echo "=================="
            total=$(gh issue list --label "status: backlog,status: ready,status: in-progress,status: review,status: blocked" --json number --jq '. | length')
            done=$(gh issue list --label "status: done" --json number --jq '. | length')
            echo "Remaining tasks: $total"
            echo "Completed tasks: $done"
            echo ""
            # Simple ASCII burndown
            remaining=$total
            for i in {1..10}; do
                bar=""
                for j in $(seq 1 $remaining); do
                    bar="${bar}█"
                done
                echo "Day $i: $bar"
                remaining=$((remaining - remaining/10))
            done
            ;;
        
        15)
            echo -e "\n${GREEN}🏆 Completed This Sprint${NC}"
            echo "========================"
            # Show issues closed in last 14 days
            gh issue list --state closed --limit 20 --search "closed:>$(date -v-14d +%Y-%m-%d)"
            ;;
        
        0)
            echo -e "${GREEN}Goodbye! Happy coding! 🚀${NC}"
            exit 0
            ;;
        
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🏃 StackWizard Sprint Board 🏃                  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
done