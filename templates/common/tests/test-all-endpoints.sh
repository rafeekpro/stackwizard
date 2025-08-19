#!/bin/bash

echo "🔍 Testing All API Endpoints"
echo "============================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

BACKEND="http://localhost:8000"
FRONTEND="http://localhost:3000"
FAILED=0
PASSED=0

# Get auth token
TOKEN=$(curl -s -X POST "$BACKEND/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}✗ Failed to get auth token${NC}"
  exit 1
fi

echo "✓ Got auth token"
echo ""

test_endpoint() {
  local name=$1
  local url=$2
  local method=${3:-GET}
  local data=${4:-}
  
  echo -n "Testing $name... "
  
  if [ "$method" = "GET" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" \
      -H "Authorization: Bearer $TOKEN")
  else
    response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data")
  fi
  
  if [ "$response" = "200" ] || [ "$response" = "201" ] || [ "$response" = "307" ]; then
    echo -e "${GREEN}✓ $response${NC}"
    ((PASSED++))
  else
    echo -e "${RED}✗ $response${NC}"
    ((FAILED++))
  fi
}

echo "BACKEND ENDPOINTS"
echo "-----------------"
test_endpoint "Health" "$BACKEND/health"
test_endpoint "API Health" "$BACKEND/api/v1/health"
test_endpoint "Users list" "$BACKEND/api/v1/users/"
test_endpoint "Current user" "$BACKEND/api/v1/users/me"
test_endpoint "Items list" "$BACKEND/api/v1/items/"

echo ""
echo "FRONTEND PROXY ENDPOINTS"
echo "------------------------"
test_endpoint "Proxy: Users list" "$FRONTEND/api/v1/users/"
test_endpoint "Proxy: Current user" "$FRONTEND/api/v1/users/me"
test_endpoint "Proxy: Items list" "$FRONTEND/api/v1/items/"

echo ""
echo "AUTH ENDPOINTS (No token needed)"
echo "---------------------------------"
echo -n "Testing Login... "
login_response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!")
if [ "$login_response" = "200" ]; then
  echo -e "${GREEN}✓ $login_response${NC}"
  ((PASSED++))
else
  echo -e "${RED}✗ $login_response${NC}"
  ((FAILED++))
fi

echo -n "Testing Register (validation)... "
reg_response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{}')
if [ "$reg_response" = "422" ]; then
  echo -e "${GREEN}✓ $reg_response (expected)${NC}"
  ((PASSED++))
else
  echo -e "${RED}✗ $reg_response${NC}"
  ((FAILED++))
fi

echo ""
echo "CREATE/UPDATE/DELETE TEST"
echo "-------------------------"

# Create test item
echo -n "Creating test item... "
ITEM_ID=$(curl -s -X POST "$BACKEND/api/v1/items/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Item", "description": "Test Description", "price": 10.50}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$ITEM_ID" ]; then
  echo -e "${GREEN}✓ Created: $ITEM_ID${NC}"
  ((PASSED++))
  
  # Update item
  echo -n "Updating test item... "
  update_response=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BACKEND/api/v1/items/$ITEM_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title": "Updated Item", "price": 20.00}')
  
  if [ "$update_response" = "200" ]; then
    echo -e "${GREEN}✓ $update_response${NC}"
    ((PASSED++))
  else
    echo -e "${RED}✗ $update_response${NC}"
    ((FAILED++))
  fi
  
  # Delete item
  echo -n "Deleting test item... "
  delete_response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BACKEND/api/v1/items/$ITEM_ID" \
    -H "Authorization: Bearer $TOKEN")
  
  if [ "$delete_response" = "200" ]; then
    echo -e "${GREEN}✓ $delete_response${NC}"
    ((PASSED++))
  else
    echo -e "${RED}✗ $delete_response${NC}"
    ((FAILED++))
  fi
else
  echo -e "${RED}✗ Failed to create${NC}"
  ((FAILED++))
fi

echo ""
echo "========================================="
echo "RESULTS"
echo "========================================="
TOTAL=$((PASSED + FAILED))
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Total:  $TOTAL"

if [ $FAILED -eq 0 ]; then
  echo -e "\n${GREEN}✅ ALL ENDPOINTS WORKING!${NC}"
  exit 0
else
  echo -e "\n${RED}❌ SOME ENDPOINTS FAILED!${NC}"
  exit 1
fi