#!/bin/bash

# Critical System Tests - Run this before any changes!
# This ensures critical functionality is never broken

echo "🛡️ CRITICAL SYSTEM TESTS"
echo "========================"
echo "These tests MUST pass before making any changes!"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
CRITICAL_FAILURES=0

# Function to run critical test
critical_test() {
    local test_name=$1
    local command=$2
    local expected=$3
    
    echo -n "Testing $test_name... "
    
    result=$(eval "$command" 2>/dev/null)
    
    if echo "$result" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Expected: $expected"
        echo "  Got: $result"
        ((CRITICAL_FAILURES++))
    fi
}

echo "1. BACKEND HEALTH CHECKS"
echo "-------------------------"

# Test backend is running
critical_test "Backend is accessible" \
    "curl -s -o /dev/null -w '%{http_code}' $API_URL/" \
    "200"

# Test health endpoint
critical_test "Health endpoint works" \
    "curl -s $API_URL/health | python3 -c 'import sys, json; print(json.load(sys.stdin)[\"status\"])'" \
    "healthy"

echo ""
echo "2. AUTHENTICATION TESTS"
echo "------------------------"

# Test login endpoint
critical_test "Login endpoint exists" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST $API_URL/api/v1/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=test&password=test'" \
    "401"

# Test admin login
critical_test "Admin can login" \
    "curl -s -X POST $API_URL/api/v1/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin@example.com&password=Admin123!' | grep -o 'access_token'" \
    "access_token"

# Test registration endpoint
critical_test "Registration endpoint exists" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST $API_URL/api/v1/auth/register -H 'Content-Type: application/json' -d '{}'" \
    "422"

echo ""
echo "3. USER MANAGEMENT TESTS"
echo "-------------------------"

# Get token for tests
TOKEN=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=Admin123!" | \
    python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    # Test /users/me endpoint
    critical_test "Users/me endpoint works" \
        "curl -s -o /dev/null -w '%{http_code}' $API_URL/api/v1/users/me -H 'Authorization: Bearer $TOKEN'" \
        "200"
    
    # Test users list endpoint
    critical_test "Users list endpoint works" \
        "curl -s -o /dev/null -w '%{http_code}' $API_URL/api/v1/users/ -H 'Authorization: Bearer $TOKEN'" \
        "200"
else
    echo -e "${RED}✗ Could not get auth token for protected endpoint tests${NC}"
    ((CRITICAL_FAILURES++))
fi

echo ""
echo "4. FRONTEND PROXY TESTS"
echo "------------------------"

# Test frontend is running
critical_test "Frontend is accessible" \
    "curl -s -o /dev/null -w '%{http_code}' $FRONTEND_URL/" \
    "200"

# Test frontend proxy to backend
critical_test "Frontend proxy to backend works" \
    "curl -s -X POST $FRONTEND_URL/api/v1/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin@example.com&password=Admin123!' | grep -o 'access_token'" \
    "access_token"

echo ""
echo "5. DATABASE CONNECTION TEST"
echo "----------------------------"

# Test database is accessible
critical_test "Database is running" \
    "docker exec test-app-db pg_isready -U postgres | grep -o 'accepting connections'" \
    "accepting connections"

echo ""
echo "6. CRITICAL FILES CHECK"
echo "------------------------"

# Check critical files exist
critical_test "Backend main.py exists" \
    "test -f /tmp/test-app/backend/app/main.py && echo 'exists'" \
    "exists"

critical_test "Frontend auth.js exists" \
    "test -f /tmp/test-app/frontend/src/services/auth.js && echo 'exists'" \
    "exists"

critical_test "Docker-compose.yml exists" \
    "test -f /tmp/test-app/docker-compose.yml && echo 'exists'" \
    "exists"

# Check proxy configuration
critical_test "Frontend proxy configured correctly" \
    "grep -o 'backend:8000' /tmp/test-app/frontend/package.json" \
    "backend:8000"

echo ""
echo "========================================="
echo "RESULTS"
echo "========================================="

if [ $CRITICAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CRITICAL TESTS PASSED!${NC}"
    echo "System is functioning correctly. Safe to proceed with changes."
    exit 0
else
    echo -e "${RED}❌ $CRITICAL_FAILURES CRITICAL TESTS FAILED!${NC}"
    echo ""
    echo "⚠️  WARNING: Do not make any changes until these issues are fixed!"
    echo "⚠️  Critical functionality is broken!"
    echo ""
    echo "To fix:"
    echo "1. Check if all containers are running: docker ps"
    echo "2. Check container logs: docker logs test-app-backend"
    echo "3. Restart containers if needed: docker compose restart"
    echo "4. Verify proxy settings in frontend/package.json"
    exit 1
fi