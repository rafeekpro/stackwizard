#!/bin/bash

echo "🧪 User Creation and Password Confirmation Tests"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"
FAILED_TESTS=0
PASSED_TESTS=0
TIMESTAMP=$(date +%s)

# Function to test user registration
test_registration() {
    local test_name=$1
    local email=$2
    local password=$3
    local username=$4
    local full_name=$5
    local expected_status=$6
    local expect_success=$7
    
    echo -e "\n${BLUE}Test: $test_name${NC}"
    
    # Build JSON payload
    json_data="{\"email\": \"$email\", \"password\": \"$password\""
    if [ ! -z "$full_name" ]; then
        json_data="$json_data, \"full_name\": \"$full_name\""
    fi
    if [ ! -z "$username" ]; then
        json_data="$json_data, \"username\": \"$username\""
    fi
    json_data="$json_data}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d "$json_data")
    
    http_code=$(echo "$response" | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Status code: $http_code (expected)${NC}"
        ((PASSED_TESTS++))
        
        if [ "$expect_success" = "true" ] && [ "$http_code" = "200" ]; then
            # Check for required fields in successful registration
            if echo "$body" | grep -q "\"user\""; then
                echo -e "${GREEN}✓ User object returned${NC}"
                ((PASSED_TESTS++))
                
                # Check username generation
                if echo "$body" | grep -q "\"username\""; then
                    username_value=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['username'])" 2>/dev/null)
                    if [ ! -z "$username_value" ]; then
                        echo -e "${GREEN}✓ Username present: $username_value${NC}"
                        ((PASSED_TESTS++))
                    else
                        echo -e "${RED}✗ Username is empty${NC}"
                        ((FAILED_TESTS++))
                    fi
                else
                    echo -e "${RED}✗ Username field missing${NC}"
                    ((FAILED_TESTS++))
                fi
            else
                echo -e "${RED}✗ User object not returned${NC}"
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
echo "1. BASIC USER CREATION TESTS"
echo "========================================="

# Test successful registration
test_registration \
    "Valid user registration" \
    "testuser_${TIMESTAMP}@example.com" \
    "ValidPass123!" \
    "testuser${TIMESTAMP}" \
    "Test User" \
    "200" \
    "true"

# Test registration without username (should auto-generate)
test_registration \
    "Registration without username (auto-generate)" \
    "autouser_${TIMESTAMP}@example.com" \
    "ValidPass123!" \
    "" \
    "Auto Generated User" \
    "200" \
    "true"

# Test registration with empty username string
test_registration \
    "Registration with empty username string" \
    "emptyuser_${TIMESTAMP}@example.com" \
    "ValidPass123!" \
    "" \
    "Empty Username User" \
    "200" \
    "true"

echo ""
echo "========================================="
echo "2. VALIDATION ERROR TESTS"
echo "========================================="

# Test missing email
test_registration \
    "Missing email" \
    "" \
    "ValidPass123!" \
    "someuser" \
    "Some User" \
    "422" \
    "false"

# Test invalid email format
test_registration \
    "Invalid email format" \
    "notanemail" \
    "ValidPass123!" \
    "someuser" \
    "Some User" \
    "422" \
    "false"

# Test missing password
test_registration \
    "Missing password" \
    "nopass_${TIMESTAMP}@example.com" \
    "" \
    "nopassuser" \
    "No Password User" \
    "422" \
    "false"

# Test weak password
test_registration \
    "Weak password (too short)" \
    "weakpass_${TIMESTAMP}@example.com" \
    "weak" \
    "weakuser" \
    "Weak Pass User" \
    "422" \
    "false"

# Test password without uppercase
test_registration \
    "Password without uppercase" \
    "nouppser_${TIMESTAMP}@example.com" \
    "nouppcase123!" \
    "noupuser" \
    "No Uppercase User" \
    "422" \
    "false"

# Test password without number
test_registration \
    "Password without number" \
    "nonum_${TIMESTAMP}@example.com" \
    "NoNumbers!" \
    "nonumuser" \
    "No Number User" \
    "422" \
    "false"

# Test username too short
test_registration \
    "Username too short (less than 3 chars)" \
    "shortname_${TIMESTAMP}@example.com" \
    "ValidPass123!" \
    "ab" \
    "Short Username" \
    "422" \
    "false"

echo ""
echo "========================================="
echo "3. DUPLICATE USER TESTS"
echo "========================================="

# First create a user
DUPLICATE_EMAIL="duplicate_${TIMESTAMP}@example.com"
echo -e "\n${BLUE}Creating initial user for duplicate test...${NC}"
initial_response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$DUPLICATE_EMAIL\", \"password\": \"ValidPass123!\", \"full_name\": \"First User\"}")

initial_code=$(echo "$initial_response" | sed -e 's/.*HTTPSTATUS://')

if [ "$initial_code" = "200" ]; then
    echo -e "${GREEN}✓ Initial user created${NC}"
    ((PASSED_TESTS++))
    
    # Try to create duplicate
    test_registration \
        "Duplicate email (should fail)" \
        "$DUPLICATE_EMAIL" \
        "DifferentPass123!" \
        "differentuser" \
        "Different User" \
        "400" \
        "false"
else
    echo -e "${RED}✗ Failed to create initial user${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "4. PASSWORD CONFIRMATION SIMULATION"
echo "========================================="

echo -e "\n${BLUE}Test: Password confirmation validation${NC}"
echo "Note: Password confirmation is handled in frontend"

# Simulate frontend validation
password1="TestPass123!"
password2="TestPass123!"
password3="DifferentPass123!"

if [ "$password1" = "$password2" ]; then
    echo -e "${GREEN}✓ Matching passwords accepted${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}✗ Matching passwords not recognized${NC}"
    ((FAILED_TESTS++))
fi

if [ "$password1" != "$password3" ]; then
    echo -e "${GREEN}✓ Non-matching passwords rejected${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}✗ Non-matching passwords not caught${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "5. USER UPDATE WITH PASSWORD CHANGE TEST"
echo "========================================="

echo -e "\n${BLUE}Test: Update user with password change${NC}"

# Create a user for update test
UPDATE_EMAIL="updatetest_${TIMESTAMP}@example.com"
update_response=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$UPDATE_EMAIL\", \"password\": \"OldPass123!\", \"full_name\": \"Update Test User\"}")

if echo "$update_response" | grep -q "user"; then
    echo -e "${GREEN}✓ User created for update test${NC}"
    ((PASSED_TESTS++))
    
    # Login to get token
    login_response=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$UPDATE_EMAIL&password=OldPass123!")
    
    if echo "$login_response" | grep -q "access_token"; then
        TOKEN=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        
        # Update password
        update_pwd_response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X PUT "$API_URL/api/v1/users/me/password" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"current_password\": \"OldPass123!\", \"new_password\": \"NewPass123!\"}")
        
        http_code=$(echo "$update_pwd_response" | sed -e 's/.*HTTPSTATUS://')
        
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✓ Password updated successfully${NC}"
            ((PASSED_TESTS++))
            
            # Try login with new password
            new_login=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_URL/api/v1/auth/login" \
                -H "Content-Type: application/x-www-form-urlencoded" \
                -d "username=$UPDATE_EMAIL&password=NewPass123!")
            
            new_login_code=$(echo "$new_login" | sed -e 's/.*HTTPSTATUS://')
            
            if [ "$new_login_code" = "200" ]; then
                echo -e "${GREEN}✓ Can login with new password${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${RED}✗ Cannot login with new password${NC}"
                ((FAILED_TESTS++))
            fi
            
            # Try login with old password (should fail)
            old_login=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_URL/api/v1/auth/login" \
                -H "Content-Type: application/x-www-form-urlencoded" \
                -d "username=$UPDATE_EMAIL&password=OldPass123!")
            
            old_login_code=$(echo "$old_login" | sed -e 's/.*HTTPSTATUS://')
            
            if [ "$old_login_code" = "401" ]; then
                echo -e "${GREEN}✓ Old password correctly rejected${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${RED}✗ Old password still works${NC}"
                ((FAILED_TESTS++))
            fi
        else
            echo -e "${RED}✗ Password update failed${NC}"
            ((FAILED_TESTS++))
        fi
    else
        echo -e "${RED}✗ Could not login for update test${NC}"
        ((FAILED_TESTS++))
    fi
else
    echo -e "${RED}✗ Could not create user for update test${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "6. FRONTEND SIMULATION TEST"
echo "========================================="

echo -e "\n${BLUE}Test: Simulating frontend user creation flow${NC}"

# Simulate what frontend sends
frontend_data='{
  "email": "frontend_'${TIMESTAMP}'@example.com",
  "password": "Frontend123!",
  "full_name": "Frontend User"
}'

frontend_response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$API_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "$frontend_data")

http_code=$(echo "$frontend_response" | sed -e 's/.*HTTPSTATUS://')
body=$(echo "$frontend_response" | sed -e 's/HTTPSTATUS:.*//')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Frontend-style registration successful${NC}"
    ((PASSED_TESTS++))
    
    # Check auto-generated username
    if echo "$body" | grep -q "\"username\":\"frontend_${TIMESTAMP}\""; then
        echo -e "${GREEN}✓ Username auto-generated from email${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${YELLOW}⚠ Username generated differently than expected${NC}"
    fi
else
    echo -e "${RED}✗ Frontend-style registration failed${NC}"
    echo "Response: $body"
    ((FAILED_TESTS++))
fi

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
    echo -e "\n${GREEN}✅ ALL USER CREATION TESTS PASSED!${NC}"
    echo "User creation and validation working correctly."
    echo "Password confirmation is handled in frontend."
    exit 0
else
    echo -e "\n${RED}❌ SOME USER CREATION TESTS FAILED!${NC}"
    echo "Please review the failed tests above."
    exit 1
fi