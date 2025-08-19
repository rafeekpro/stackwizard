#!/bin/bash

echo "🧪 Comprehensive Field Validation Tests"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"
TEST_TIMESTAMP=$(date +%s)
TEST_EMAIL="fieldtest_${TEST_TIMESTAMP}@example.com"
TEST_PASSWORD="TestPassword123!"
FAILED_TESTS=0
PASSED_TESTS=0

# Function to check if field exists and is not null/empty
check_field() {
    local json=$1
    local field=$2
    local description=$3
    local allow_null=$4
    
    value=$(echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('$field', 'FIELD_NOT_FOUND'))" 2>/dev/null)
    
    if [ "$value" = "FIELD_NOT_FOUND" ]; then
        echo -e "  ${RED}✗ MISSING${NC} - $field: $description"
        ((FAILED_TESTS++))
        return 1
    elif [ "$value" = "None" ] || [ "$value" = "" ]; then
        if [ "$allow_null" = "true" ]; then
            echo -e "  ${YELLOW}⚠ NULL${NC}    - $field: $value (allowed)"
            ((PASSED_TESTS++))
        else
            echo -e "  ${RED}✗ EMPTY${NC}   - $field: $description"
            ((FAILED_TESTS++))
            return 1
        fi
    else
        echo -e "  ${GREEN}✓ OK${NC}      - $field: $value"
        ((PASSED_TESTS++))
    fi
    return 0
}

echo ""
echo "========================================="
echo "1. USER REGISTRATION FIELD TEST"
echo "========================================="

echo -e "\n${BLUE}Creating test user...${NC}"

# Register a new user
register_response=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"full_name\": \"Field Test User\"
    }")

echo "Registration Response Fields:"
echo "$register_response" | python3 -m json.tool 2>/dev/null || echo "$register_response"

if echo "$register_response" | grep -q "user"; then
    user_data=$(echo "$register_response" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)['user']))" 2>/dev/null)
    
    echo -e "\n${BLUE}Checking Required User Fields:${NC}"
    check_field "$user_data" "id" "User ID (UUID)"
    check_field "$user_data" "email" "Email address"
    check_field "$user_data" "username" "Username (should be auto-generated)"
    check_field "$user_data" "full_name" "Full name"
    check_field "$user_data" "is_active" "Active status"
    check_field "$user_data" "is_superuser" "Superuser status"
    check_field "$user_data" "is_verified" "Email verification status"
    check_field "$user_data" "created_at" "Creation timestamp"
    check_field "$user_data" "updated_at" "Update timestamp"
    check_field "$user_data" "last_login_at" "Last login time" true
    check_field "$user_data" "login_count" "Login count"
else
    echo -e "${RED}✗ Registration failed or user already exists${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "2. LOGIN AND TOKEN TEST"
echo "========================================="

echo -e "\n${BLUE}Testing login...${NC}"

# Login to get token
login_response=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${TEST_EMAIL}&password=${TEST_PASSWORD}")

echo "Login Response Fields:"
echo "$login_response" | python3 -m json.tool 2>/dev/null || echo "$login_response"

if echo "$login_response" | grep -q "access_token"; then
    echo -e "\n${BLUE}Checking Login Response Fields:${NC}"
    check_field "$login_response" "access_token" "JWT access token"
    check_field "$login_response" "token_type" "Token type (should be 'bearer')"
    check_field "$login_response" "expires_in" "Token expiration time"
    check_field "$login_response" "refresh_token" "Refresh token"
    
    TOKEN=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
else
    echo -e "${RED}✗ Login failed${NC}"
    ((FAILED_TESTS++))
fi

echo ""
echo "========================================="
echo "3. GET CURRENT USER TEST (/api/v1/users/me)"
echo "========================================="

if [ ! -z "$TOKEN" ]; then
    echo -e "\n${BLUE}Getting current user info...${NC}"
    
    me_response=$(curl -s "$API_URL/api/v1/users/me" \
        -H "Authorization: Bearer $TOKEN")
    
    echo "Current User Response Fields:"
    echo "$me_response" | python3 -m json.tool 2>/dev/null || echo "$me_response"
    
    if ! echo "$me_response" | grep -q "detail"; then
        echo -e "\n${BLUE}Checking /users/me Fields:${NC}"
        check_field "$me_response" "id" "User ID"
        check_field "$me_response" "email" "Email"
        check_field "$me_response" "username" "Username"
        check_field "$me_response" "full_name" "Full name"
        check_field "$me_response" "is_active" "Active status"
        check_field "$me_response" "is_superuser" "Superuser status"
        check_field "$me_response" "is_verified" "Verification status"
        check_field "$me_response" "created_at" "Created timestamp"
        check_field "$me_response" "updated_at" "Updated timestamp"
        check_field "$me_response" "last_login_at" "Last login" true
        check_field "$me_response" "login_count" "Login count"
    else
        echo -e "${RED}✗ Failed to get user info${NC}"
        ((FAILED_TESTS++))
    fi
fi

echo ""
echo "========================================="
echo "4. USER LIST TEST (/api/v1/users/)"
echo "========================================="

# Try with admin token first
echo -e "\n${BLUE}Logging in as admin...${NC}"

admin_login=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=Admin123!")

if echo "$admin_login" | grep -q "access_token"; then
    ADMIN_TOKEN=$(echo "$admin_login" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    
    echo -e "\n${BLUE}Getting user list...${NC}"
    
    users_response=$(curl -s "$API_URL/api/v1/users/" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    if echo "$users_response" | python3 -c "import sys, json; data=json.load(sys.stdin); sys.exit(0 if isinstance(data, list) else 1)" 2>/dev/null; then
        first_user=$(echo "$users_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data[0]) if data else '{}')" 2>/dev/null)
        
        if [ "$first_user" != "{}" ]; then
            echo -e "\n${BLUE}Checking User List Item Fields:${NC}"
            check_field "$first_user" "id" "User ID"
            check_field "$first_user" "email" "Email"
            check_field "$first_user" "username" "Username"
            check_field "$first_user" "full_name" "Full name"
            check_field "$first_user" "is_active" "Active status"
            check_field "$first_user" "is_superuser" "Superuser status"
            check_field "$first_user" "is_verified" "Verification status"
            check_field "$first_user" "created_at" "Created timestamp"
            check_field "$first_user" "updated_at" "Updated timestamp"
        else
            echo -e "${YELLOW}⚠ User list is empty${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Could not parse user list${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Admin login failed, skipping user list test${NC}"
fi

echo ""
echo "========================================="
echo "5. DATABASE FIELD VALIDATION"
echo "========================================="

echo -e "\n${BLUE}Checking database schema...${NC}"

# Check database directly
db_check=$(docker compose exec -T db psql -U postgres -d test_db -c "
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'users'
    ORDER BY ordinal_position;
" 2>/dev/null)

echo "$db_check"

required_columns=(
    "id"
    "email"
    "hashed_password"
    "username"
    "full_name"
    "is_active"
    "is_superuser"
    "is_verified"
    "created_at"
    "updated_at"
)

echo -e "\n${BLUE}Verifying Required Columns:${NC}"
for col in "${required_columns[@]}"; do
    if echo "$db_check" | grep -q " $col "; then
        echo -e "  ${GREEN}✓${NC} Column exists: $col"
        ((PASSED_TESTS++))
    else
        echo -e "  ${RED}✗${NC} Column missing: $col"
        ((FAILED_TESTS++))
    fi
done

echo ""
echo "========================================="
echo "6. FIELD CONSISTENCY TEST"
echo "========================================="

echo -e "\n${BLUE}Testing field consistency across endpoints...${NC}"

# Compare fields from different endpoints
if [ ! -z "$TOKEN" ]; then
    # Get same user from different endpoints
    me_fields=$(curl -s "$API_URL/api/v1/users/me" -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(','.join(sorted(data.keys())))
except:
    print('ERROR')
" 2>/dev/null)
    
    echo "Fields from /users/me: $me_fields"
    
    # Check if all critical fields are present
    critical_fields=("id" "email" "username" "full_name" "is_active")
    for field in "${critical_fields[@]}"; do
        if echo "$me_fields" | grep -q "$field"; then
            echo -e "  ${GREEN}✓${NC} Critical field present: $field"
            ((PASSED_TESTS++))
        else
            echo -e "  ${RED}✗${NC} Critical field missing: $field"
            ((FAILED_TESTS++))
        fi
    done
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
    echo -e "\n${GREEN}✅ ALL FIELD TESTS PASSED!${NC}"
    echo "All required fields are present and properly populated."
    exit 0
else
    echo -e "\n${RED}❌ SOME FIELD TESTS FAILED!${NC}"
    echo "Please review the missing or empty fields above."
    exit 1
fi