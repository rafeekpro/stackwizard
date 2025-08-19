#!/bin/bash

# TDD Test Runner for Backend
# Run this before making any changes to ensure nothing breaks

echo "🧪 Running TDD Backend Tests"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ] || [ ! -d "app" ]; then
    echo -e "${RED}Error: Must be run from the backend directory${NC}"
    echo "Please cd to the backend directory first"
    exit 1
fi

# Install test dependencies if needed
echo -e "${BLUE}Checking test dependencies...${NC}"
pip install -q pytest pytest-cov pytest-asyncio httpx 2>/dev/null

# Function to run a specific test file
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo -e "\n${BLUE}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if pytest "$test_file" -v --tb=short; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        return 1
    fi
}

# Track failures
FAILED_TESTS=0
TOTAL_TESTS=0

# Run tests in order (most fundamental first)
echo -e "\n${YELLOW}Phase 1: Model Tests${NC}"
echo "===================="
((TOTAL_TESTS++))
if ! run_test "tests/test_models.py" "User Model Tests"; then
    ((FAILED_TESTS++))
fi

echo -e "\n${YELLOW}Phase 2: Schema Tests${NC}"
echo "====================="
((TOTAL_TESTS++))
if ! run_test "tests/test_schemas.py" "Pydantic Schema Tests"; then
    ((FAILED_TESTS++))
fi

echo -e "\n${YELLOW}Phase 3: Authentication Tests${NC}"
echo "============================="
((TOTAL_TESTS++))
if ! run_test "tests/test_auth.py" "Authentication Tests"; then
    ((FAILED_TESTS++))
fi

echo -e "\n${YELLOW}Phase 4: User Endpoint Tests${NC}"
echo "============================"
((TOTAL_TESTS++))
if ! run_test "tests/test_users.py" "User Management Tests"; then
    ((FAILED_TESTS++))
fi

echo -e "\n${YELLOW}Phase 5: Admin Tests${NC}"
echo "===================="
((TOTAL_TESTS++))
if ! run_test "tests/test_admin.py" "Admin Endpoint Tests"; then
    ((FAILED_TESTS++))
fi

# Run all tests with coverage if all phases pass
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${YELLOW}Running Full Test Suite with Coverage${NC}"
    echo "======================================"
    pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
fi

# Summary
echo ""
echo "======================================"
echo "TEST SUMMARY"
echo "======================================"
echo -e "Total test suites: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $((TOTAL_TESTS - FAILED_TESTS))${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo "Safe to proceed with changes."
    echo ""
    echo "Remember to:"
    echo "1. Run tests after each change"
    echo "2. Add new tests for new features"
    echo "3. Ensure all tests pass before committing"
    exit 0
else
    echo -e "\n${RED}❌ SOME TESTS FAILED!${NC}"
    echo ""
    echo "Please fix the failing tests before making changes."
    echo "This ensures we don't break existing functionality."
    echo ""
    echo "TDD Process:"
    echo "1. Write/fix failing tests"
    echo "2. Implement minimal code to pass tests"
    echo "3. Refactor if needed"
    echo "4. Repeat for next feature"
    exit 1
fi