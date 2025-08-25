# 🔒 Security Features Integration Guide

## Overview
This guide explains how to integrate the new security features into your StackWizard application.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

New dependencies added:
- `slowapi==0.1.9` - Rate limiting
- `python-csrf==1.0.0` - CSRF protection  
- `secure==0.3.0` - Security headers

### 2. Update main.py

Add the following imports and setup to your `app/main.py`:

```python
from app.middleware.rate_limiter import setup_rate_limiting
from app.middleware.csrf_protection import setup_csrf_protection
from app.middleware.security_headers import setup_security_headers
from app.services.audit_logger import audit_logger

# After creating the FastAPI app
app = FastAPI(...)

# Setup security middleware (order matters!)
setup_security_headers(app)  # First - adds security headers
setup_rate_limiting(app)      # Second - rate limiting
setup_csrf_protection(app)    # Third - CSRF protection
```

### 3. Run Database Migration

Create the audit logs table:

```bash
alembic revision --autogenerate -m "Add audit logs table"
alembic upgrade head
```

## 📋 Feature Documentation

### 1️⃣ Rate Limiting

**Location**: `app/middleware/rate_limiter.py`

**Features**:
- Global rate limits: 60/minute, 1000/hour (configurable)
- Path-specific limits for sensitive endpoints
- User-based and IP-based limiting
- Redis support for distributed systems

**Usage in endpoints**:
```python
from app.middleware.rate_limiter import auth_limiter

@router.post("/login")
@auth_limiter  # 5 requests per minute
async def login(...):
    pass
```

**Configuration** (in `.env`):
```env
RATE_LIMITING_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
REDIS_URL=redis://localhost:6379/0  # Optional
```

### 2️⃣ CSRF Protection

**Location**: `app/middleware/csrf_protection.py`

**Features**:
- Automatic token generation for GET requests
- Token validation for state-changing operations
- Cookie-based token storage
- Configurable exclusions for specific paths

**Frontend Integration**:
```javascript
// Get CSRF token from cookie or response header
const csrfToken = getCookie('csrf_token');

// Include in requests
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'X-CSRF-Token': csrfToken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### 3️⃣ Security Headers

**Location**: `app/middleware/security_headers.py`

**Headers Applied**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy` (configurable)
- `Strict-Transport-Security` (production only)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` (restricts browser features)

### 4️⃣ Refresh Token Rotation

**Location**: `app/services/token_rotation.py`

**Features**:
- Automatic token rotation on refresh
- Token family tracking for security breach detection
- Replay attack prevention
- Token reuse detection with family revocation

**Updated Auth Endpoints**:
```python
from app.services.token_rotation import token_rotation_service

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    # ... validate user ...
    access_token, refresh_token, family_id = await token_rotation_service.create_token_pair(
        user=user,
        db=db,
        metadata={"login_method": "password"}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession):
    access_token, new_refresh_token = await token_rotation_service.rotate_refresh_token(
        refresh_token=refresh_token,
        db=db
    )
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
```

### 5️⃣ Security Audit Logger

**Location**: `app/services/audit_logger.py`

**Features**:
- Comprehensive event logging
- Database persistence
- Structured logging to files
- Security event detection
- Brute force detection

**Usage**:
```python
from app.services.audit_logger import audit_logger, AuditEventType

# Log login attempt
await audit_logger.log_login_attempt(
    db=db,
    email=email,
    success=True,
    user_id=user.id,
    request=request
)

# Log admin action
await audit_logger.log_admin_action(
    db=db,
    admin_id=current_user.id,
    action="user_deactivated",
    target_user_id=user_id,
    request=request
)

# Check for brute force
is_brute_force = await audit_logger.detect_brute_force(
    db=db,
    ip_address=client_ip,
    minutes=5,
    threshold=5
)
```

## 🔧 Configuration

### Environment Variables

Add to your `.env` file:

```env
# Security
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# Rate Limiting
RATE_LIMITING_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CSRF
CSRF_ENABLED=true

# Audit Logging
AUDIT_LOG_FILE=/var/log/stackwizard/audit.log

# Redis (optional, for production)
REDIS_URL=redis://localhost:6379/0
```

### Update Settings

In `app/core/config.py`, add:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Security
    ENVIRONMENT: str = "development"
    RATE_LIMITING_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    CSRF_ENABLED: bool = True
    AUDIT_LOG_FILE: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Token settings
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
```

## 🧪 Testing

### Test Rate Limiting
```bash
# Should get rate limited after 5 attempts
for i in {1..10}; do
    curl -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test&password=test"
done
```

### Test CSRF Protection
```bash
# Get CSRF token
curl -X GET http://localhost:8000/api/v1/users/me \
    -c cookies.txt

# Use token in POST request
curl -X POST http://localhost:8000/api/v1/users/me \
    -b cookies.txt \
    -H "X-CSRF-Token: <token-from-cookie>" \
    -H "Content-Type: application/json" \
    -d '{"full_name": "Test User"}'
```

### Test Security Headers
```bash
curl -I http://localhost:8000/api/health

# Should see headers like:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
```

## 📊 Monitoring

### View Audit Logs
```python
# In your admin endpoint
@router.get("/admin/audit-logs")
async def get_audit_logs(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser)
):
    recent_events = await audit_logger.get_recent_security_events(db, hours=24)
    return [event.to_dict() for event in recent_events]
```

### Check Active Sessions
```python
@router.get("/users/me/sessions")
async def get_my_sessions(
    current_user: User = Depends(get_current_active_user)
):
    sessions = await token_rotation_service.get_active_sessions(str(current_user.id))
    return sessions
```

## ⚠️ Important Notes

1. **Order of Middleware**: The order in which middleware is added matters. Security headers should be first, followed by rate limiting, then CSRF.

2. **Production Settings**: In production:
   - Use Redis for rate limiting and token storage
   - Enable HTTPS for secure cookies
   - Configure proper CORS origins
   - Set up log rotation for audit logs

3. **Frontend Updates**: Update your frontend to:
   - Handle CSRF tokens
   - Respect rate limit headers
   - Handle 429 (Too Many Requests) responses
   - Implement token refresh logic

4. **Database Performance**: The audit logs table can grow quickly. Consider:
   - Regular archiving of old logs
   - Proper indexing (already included)
   - Partitioning for large deployments

## 🚨 Security Checklist

- [ ] Dependencies installed
- [ ] Middleware integrated in correct order
- [ ] Database migrations run
- [ ] Environment variables configured
- [ ] Frontend updated for CSRF tokens
- [ ] Rate limits tested
- [ ] Security headers verified
- [ ] Audit logging working
- [ ] Token rotation tested
- [ ] Production settings reviewed

## 📚 Further Reading

- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [JWT Security Best Practices](https://tools.ietf.org/html/rfc8725)

---

*Security features implemented as part of StackWizard v1.2.0 security enhancement initiative*