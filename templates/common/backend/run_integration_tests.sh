#!/bin/bash

# Integration tests runner for StackWizard generated projects
# This script runs integration tests to verify CORS, API endpoints, and static files

echo "🧪 Running Integration Tests..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
check_backend() {
    echo -e "${YELLOW}Checking if backend is running...${NC}"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Backend is not running${NC}"
        echo -e "${YELLOW}Please start the backend first:${NC}"
        echo "  docker-compose up -d"
        echo "  OR"
        echo "  cd backend && uvicorn app.main:app --reload"
        return 1
    fi
}

# Run integration tests
run_tests() {
    echo -e "${YELLOW}Running integration tests...${NC}"
    cd backend
    python tests/test_integration.py
    return $?
}

# Main execution
main() {
    if check_backend; then
        echo ""
        if run_tests; then
            echo ""
            echo -e "${GREEN}✨ All integration tests passed!${NC}"
            exit 0
        else
            echo ""
            echo -e "${RED}❌ Some integration tests failed${NC}"
            exit 1
        fi
    else
        exit 1
    fi
}

main