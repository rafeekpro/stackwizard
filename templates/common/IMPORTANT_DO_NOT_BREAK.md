# ⚠️ CRITICAL SYSTEM COMPONENTS - DO NOT BREAK! ⚠️

## 🔴 BEFORE MAKING ANY CHANGES

**ALWAYS RUN:** `./test-critical.sh`

If any test fails, DO NOT proceed with changes!

## 🛡️ CRITICAL COMPONENTS THAT MUST NEVER BREAK

### 1. Authentication System
- **Login endpoint**: `/api/v1/auth/login`
- **Token format**: OAuth2 with `username` field (not `email`!)
- **Admin credentials**: `admin@example.com` / `Admin123!`
- **Files involved**:
  - Backend: `/backend/app/api/v1/auth.py`
  - Frontend: `/frontend/src/services/auth.js`
  - Login Page: `/frontend/src/pages/LoginPage.js`

### 2. Frontend Proxy Configuration
- **MUST BE**: `"proxy": "http://backend:8000"` in `/frontend/package.json`
- **NOT**: `"proxy": "http://localhost:8000"` (this breaks Docker networking!)
- After changing, restart frontend: `docker compose restart frontend`

### 3. Health Check Endpoint
- **Endpoint**: `/health` (for Docker health checks)
- **Location**: `/backend/app/main.py`
- **Response**: `{"status": "healthy", "service": "backend"}`

### 4. User Registration
- **Username validation**: Empty string `""` must be converted to `None`
- **Auto-generation**: Username generated from email if not provided
- **Location**: `/backend/app/schemas/user.py` - `UserRegister` class

## 🧪 TEST SUITE

### Quick Health Check
```bash
./test-critical.sh  # MUST pass before any changes
```

### Full Test Suite
```bash
./test-login.sh           # 21 tests for login functionality
./test-all-fields.sh      # 50 tests for field validation
./test-user-creation.sh   # 26 tests for user creation
```

## 🚨 COMMON ISSUES AND FIXES

### Problem: Login returns 404 or 500
**Fix:**
1. Check proxy: `grep proxy frontend/package.json`
2. Should be: `"proxy": "http://backend:8000"`
3. Restart: `docker compose restart frontend`

### Problem: Health check failing (container unhealthy)
**Fix:**
1. Check endpoint: `curl http://localhost:8000/health`
2. Should return: `{"status": "healthy", "service": "backend"}`

### Problem: Can't create users (422 error)
**Fix:**
1. Check username validation in `/backend/app/schemas/user.py`
2. Empty strings must be converted to `None`
3. Minimum length is 3 characters when provided

### Problem: Password confirmation not working
**Fix:**
1. Frontend only - check `/frontend/src/pages/UsersPage.js`
2. Fields: `password` and `passwordConfirm` must match
3. Validation before form submission

## 📋 CHECKLIST BEFORE COMMITTING

- [ ] Run `./test-critical.sh` - ALL tests pass
- [ ] Login works: `admin@example.com` / `Admin123!`
- [ ] Can create new users
- [ ] Can update users
- [ ] Frontend proxy points to `backend:8000`
- [ ] Health endpoint returns 200 OK

## 🔧 DOCKER COMMANDS

```bash
# Check container status
docker ps

# View logs
docker logs test-app-backend
docker logs test-app-frontend

# Restart containers
docker compose restart
docker compose restart backend
docker compose restart frontend

# Full rebuild (if needed)
docker compose down
docker compose up -d --build
```

## ⚡ QUICK FIXES

```bash
# Fix proxy and restart
sed -i 's/"proxy": "http:\/\/localhost:8000"/"proxy": "http:\/\/backend:8000"/' frontend/package.json
docker compose restart frontend

# Test login quickly
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!"
```

---

**Remember**: If you break login, users can't access the system! 
Always test before and after changes! 🔒