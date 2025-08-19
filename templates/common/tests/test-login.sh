#!/bin/bash

echo "🔐 Comprehensive Login Tests"
echo "============================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
FAILED_TESTS=0
PASSED_TESTS=0

# Test function
test_login() {
    local test_name=$1
    local url=$2
    local username=$3
    local password=$4
    local expected_status=$5
    
    echo -e "\n${BLUE}Test: $test_name${NC}"
    echo "URL: $url"
    echo "Username: $username"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$url" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$username&password=$password")
    
    http_code=$(echo "$response" | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Status code: $http_code (expected: $expected_status)${NC}"
        ((PASSED_TESTS++))
        
        if [ "$expected_status" = "200" ]; then
            # Check for required fields in successful login
            if echo "$body" | grep -q "access_token"; then
                echo -e "${GREEN}✓ access_token present${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${RED}✗ access_token missing${NC}"
                ((FAILED_TESTS++))
            fi
            
            if echo "$body" | grep -q "refresh_token"; then
                echo -e "${GREEN}✓ refresh_token present${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${RED}✗ refresh_token missing${NC}"
                ((FAILED_TESTS++))
            fi
            
            if echo "$body" | grep -q "token_type"; then
                echo -e "${GREEN}✓ token_type present${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${RED}✗ token_type missing${NC}"
                ((FAILED_TESTS++))
            fi
            
            if echo "$body" | grep -q "expires_in"; then
                echo -e "${GREEN}✓ expires_in present${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${RED}✗ expires_in missing${NC}"
                ((FAILED_TESTS++))
            fi
        fi
    else
        echo -e "${RED}✗ Status code: $http_code (expected: $expected_status)${NC}"
        echo "Response: $body"
        ((FAILED_TESTS++))
    fi
}

echo ""
echo "========================================="
echo "1. BACKEND LOGIN TESTS"
echo "========================================="

# Test valid admin login
test_login "Valid admin login (backend)" \
    "$API_URL/api/v1/auth/login" \
    "admin@example.com" \
    "Admin123!" \
    "200"

# Test invalid password
test_login "Invalid password (backend)" \
    "$API_URL/api/v1/auth/login" \
    "admin@example.com" \
    "WrongPassword" \
    "401"

# Test non-existent user
test_login "Non-existent user (backend)" \
    "$API_URL/api/v1/auth/login" \
    "nonexistent@example.com" \
    "SomePassword123!" \
    "401"

# Test empty password
test_login "Empty password (backend)" \
    "$API_URL/api/v1/auth/login" \
    "admin@example.com" \
    "" \
    "422"

# Test empty username
test_login "Empty username (backend)" \
    "$API_URL/api/v1/auth/login" \
    "" \
    "Admin123!" \
    "422"

echo ""
echo "========================================="
echo "2. FRONTEND PROXY LOGIN TESTS"
echo "========================================="

# Test valid admin login through frontend proxy
test_login "Valid admin login (frontend proxy)" \
    "$FRONTEND_URL/api/v1/auth/login" \
    "admin@example.com" \
    "Admin123!" \
    "200"

# Test invalid password through frontend proxy
test_login "Invalid password (frontend proxy)" \
    "$FRONTEND_URL/api/v1/auth/login" \
    "admin@example.com" \
    "WrongPassword" \
    "401"

echo ""
echo "========================================="
echo "3. TOKEN VALIDATION TESTS"
echo "========================================="

echo -e "\n${BLUE}Test: Token validation${NC}"

# Get a valid token
token_response=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=Admin123!")

if echo "$token_response" | grep -q "access_token"; then
    TOKEN=$(echo "$token_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    
    # Test valid token
    me_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_URL/api/v1/users/me" \
        -H "Authorization: Bearer $TOKEN")
    
    http_code=$(echo "$me_response" | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Valid token accepted${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Valid token rejected${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test invalid token
    invalid_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_URL/api/v1/users/me" \
        -H "Authorization: Bearer invalid_token_12345")
    
    http_code=$(echo "$invalid_response" | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" = "401" ]; then
        echo -e "${GREEN}✓ Invalid token rejected${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Invalid token not rejected (status: $http_code)${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test missing token
    missing_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_URL/api/v1/users/me")
    
    http_code=$(echo "$missing_response" | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" = "401" ]; then
        echo -e "${GREEN}✓ Missing token rejected${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Missing token not rejected (status: $http_code)${NC}"
        ((FAILED_TESTS++))
    fi
else
    echo -e "${RED}✗ Could not get token for validation tests${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "4. REFRESH TOKEN TEST"
echo "========================================="

echo -e "\n${BLUE}Test: Refresh token${NC}"

# Get tokens
login_response=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=Admin123!")

if echo "$login_response" | grep -q "refresh_token"; then
    REFRESH_TOKEN=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh_token'])" 2>/dev/null)
    
    # Use refresh token
    refresh_response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_URL/api/v1/auth/refresh?refresh_token=$REFRESH_TOKEN")
    
    http_code=$(echo "$refresh_response" | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$refresh_response" | sed -e 's/HTTPSTATUS:.*//')
    
    if [ "$http_code" = "200" ] && echo "$body" | grep -q "access_token"; then
        echo -e "${GREEN}✓ Refresh token works${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Refresh token failed (status: $http_code)${NC}"
        ((FAILED_TESTS++))
    fi
else
    echo -e "${RED}✗ Could not get refresh token${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "5. CONCURRENT LOGIN TEST"
echo "========================================="

echo -e "\n${BLUE}Test: Multiple concurrent logins${NC}"

# Start multiple login requests in background
for i in {1..5}; do
    (curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin@example.com&password=Admin123!" > /tmp/login_test_$i.txt) &
done

# Wait for all background jobs
wait

# Check results
all_success=true
for i in {1..5}; do
    status=$(cat /tmp/login_test_$i.txt)
    if [ "$status" != "200" ]; then
        all_success=false
        echo -e "${RED}✗ Login $i failed with status: $status${NC}"
    fi
    rm -f /tmp/login_test_$i.txt
done

if $all_success; then
    echo -e "${GREEN}✓ All concurrent logins succeeded${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}✗ Some concurrent logins failed${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "6. BROWSER LOGIN SIMULATION"
echo "========================================="

echo -e "\n${BLUE}Test: Browser-like login (with cookies)${NC}"

# Simulate browser login with cookie jar
cookie_jar="/tmp/test_cookies.txt"
rm -f $cookie_jar

# First request to get any CSRF token or session cookie
curl -s -c $cookie_jar -o /dev/null "$FRONTEND_URL/login"

# Login request with cookies
login_response=$(curl -s -b $cookie_jar -c $cookie_jar -w "HTTPSTATUS:%{http_code}" \
    -X POST "$FRONTEND_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Origin: $FRONTEND_URL" \
    -H "Referer: $FRONTEND_URL/login" \
    -d "username=admin@example.com&password=Admin123!")

http_code=$(echo "$login_response" | sed -e 's/.*HTTPSTATUS://')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Browser-like login succeeded${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}✗ Browser-like login failed (status: $http_code)${NC}"
    ((FAILED_TESTS++))
fi

rm -f $cookie_jar

echo ""
echo "========================================="
echo "7. SUMMARY"
echo "========================================="

TOTAL_TESTS=$((PASSED_TESTS + FAILED_TESTS))

echo -e "\nTest Results:"
echo -e "  ${GREEN}Passed:${NC} $PASSED_TESTS"
echo -e "  ${RED}Failed:${NC} $FAILED_TESTS"
echo -e "  Total:  $TOTAL_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL LOGIN TESTS PASSED!${NC}"
    echo "Login functionality is working correctly."
    exit 0
else
    echo -e "\n${RED}❌ SOME LOGIN TESTS FAILED!${NC}"
    echo "Please review the failed tests above."
    exit 1
fi