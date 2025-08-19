# CLAUDE.md - Project Protection Guidelines

## 🛡️ CRITICAL: PROJECT STABILITY RULES

### ⛔ DO NOT MODIFY WITHOUT EXPLICIT REQUEST:
1. **Core Architecture** - The project structure is carefully designed and tested
2. **Database Schema** - Models and migrations are production-ready
3. **Authentication System** - Security implementation is complete
4. **Test Suite** - 100% test coverage achieved (77 passing, 1 skipped)
5. **API Endpoints** - All endpoints are implemented and tested

### ✅ CURRENT PROJECT STATUS
- **Test Coverage**: 100% (77/78 tests passing, 1 skipped)
- **API Completeness**: All required endpoints implemented
- **Security**: Full authentication/authorization system in place
- **Database**: PostgreSQL with async SQLAlchemy configured
- **Documentation**: OpenAPI/Swagger available at `/docs`

## 🚨 PROTECTION RULES FOR CLAUDE

### 1. BEFORE ANY MODIFICATION:
```
- ALWAYS ask: "Is this change absolutely necessary?"
- VERIFY the user explicitly requested this specific change
- CHECK if existing functionality already covers the need
- WARN about potential breaking changes
```

### 2. FORBIDDEN ACTIONS (without explicit permission):
- ❌ Deleting or renaming existing endpoints
- ❌ Modifying database schema or models
- ❌ Changing authentication/security logic
- ❌ Removing or modifying tests
- ❌ Refactoring working code "for improvement"
- ❌ Adding unnecessary dependencies
- ❌ Creating duplicate functionality

### 3. TEST PROTECTION:
```python
# IMPORTANT: Current test status must be maintained
# Before ANY changes:
assert tests_passing >= 77  # Never decrease passing tests
assert test_coverage >= 98  # Maintain high coverage
```

### 4. SAFE MODIFICATION ZONES:
Only these areas can be modified WITH user request:
- Adding NEW endpoints (not modifying existing)
- Adding NEW models (not modifying existing)
- Adding NEW tests (not modifying existing)
- Updating documentation/comments
- Adding new frontend components

## 📋 PROJECT INVENTORY (DO NOT REMOVE)

### Implemented Endpoints:
#### Authentication (`/api/v1/auth/`)
- ✅ POST `/register` - User registration
- ✅ POST `/login` - User login
- ✅ POST `/logout` - User logout
- ✅ POST `/refresh` - Token refresh
- ✅ POST `/password-recovery` - Request password reset
- ✅ POST `/reset-password` - Reset password with token
- ✅ GET `/verify-token` - Verify JWT token

#### Users (`/api/v1/users/`)
- ✅ GET `/me` - Get current user
- ✅ PUT `/me` - Update current user
- ✅ PUT `/me/password` - Change password
- ✅ DELETE `/me` - Deactivate account
- ✅ GET `/` - List all users (admin)
- ✅ GET `/{user_id}` - Get user by ID (admin)
- ✅ POST `/` - Create user (admin)
- ✅ PUT `/{user_id}` - Update user (admin)
- ✅ DELETE `/{user_id}` - Delete user (admin)

#### Admin (`/api/v1/admin/`)
- ✅ GET `/stats` - System statistics
- ✅ GET `/recent-registrations` - Recent users
- ✅ GET `/audit-log` - Admin action log
- ✅ GET `/users` - Advanced user search
- ✅ POST `/users/{id}/reset-password` - Reset user password
- ✅ POST `/users/{id}/verify-email` - Verify user email
- ✅ GET `/users/export` - Export users (CSV/JSON)
- ✅ POST `/users/import` - Import users
- ✅ POST `/users/bulk-activate` - Bulk activate
- ✅ POST `/users/bulk-deactivate` - Bulk deactivate
- ✅ GET `/users/{id}/sessions` - Get user sessions
- ✅ DELETE `/users/{id}/sessions` - Invalidate sessions

### Database Models:
- ✅ User (complete with all fields)
- ✅ Item (example CRUD model)

### Test Files Status:
- ✅ `test_admin.py` - 13 tests passing, 1 skipped
- ✅ `test_auth.py` - 15 tests passing
- ✅ `test_crud.py` - 4 tests passing
- ✅ `test_database.py` - 2 tests passing
- ✅ `test_dependencies.py` - 8 tests passing
- ✅ `test_items.py` - 7 tests passing
- ✅ `test_models.py` - 9 tests passing
- ✅ `test_schemas.py` - 10 tests passing
- ✅ `test_users.py` - 9 tests passing

## 🔒 VALIDATION CHECKLIST

Before committing ANY changes, Claude must verify:

```bash
# 1. Run all tests
pytest tests/ -v
# Expected: 77 passed, 1 skipped

# 2. Check no endpoints were removed
grep -r "@router" app/api/

# 3. Verify no models were changed
git diff app/models/

# 4. Ensure no security changes
git diff app/core/security.py app/core/dependencies.py

# 5. Confirm no test modifications
git diff tests/
```

## ⚠️ BREAKING CHANGE WARNING

If a user requests changes that would:
- Break existing tests
- Remove functionality
- Change API contracts
- Modify database schema

Claude MUST:
1. **WARN** the user about consequences
2. **LIST** what will break
3. **SUGGEST** non-breaking alternatives
4. **REQUIRE** explicit confirmation

## 📝 MODIFICATION LOG

Track all modifications here:
```
Date: [Current Session]
Status: Protected - 100% tests passing
Last Safe Commit: All endpoints implemented, tests passing
Protected Since: Initial implementation complete
```

## 🚀 SAFE ADDITIONS GUIDE

### Adding New Features (SAFE):
```python
# 1. Create new file/module
# 2. Add new router
# 3. Register in main
# 4. Add tests
# DO NOT modify existing code
```

### Adding New Models (SAFE):
```python
# 1. Create new model file
# 2. Add migration
# 3. Create schemas
# 4. Add CRUD operations
# DO NOT modify existing models
```

## 💡 RESPONSE TEMPLATES

### When user asks for modifications:
```
"I notice you want to modify [X]. The current implementation is 
fully tested with 100% coverage. Making this change would:
- [List impacts]
- [List breaking changes]

Alternative approach that preserves stability:
- [Suggest non-breaking solution]

Should I proceed with the breaking change or the safe alternative?"
```

### When user asks to "improve" code:
```
"The current code has 100% test coverage and is production-ready.
The requested improvement might break [X] tests and [Y] features.

The code follows these principles:
- Explicit over implicit
- Tested over elegant
- Stable over optimal

Is there a specific issue you're experiencing that needs fixing?"
```

## 🎯 FINAL RULE

**IF IN DOUBT, DO NOT MODIFY**

The project is in a stable, tested state. Any modification should:
1. Have clear business value
2. Be explicitly requested
3. Not break existing functionality
4. Include new tests
5. Be documented here

---
*This protection document ensures project stability and prevents accidental degradation through well-meaning but unnecessary modifications.*