# 🔐 Advanced Authentication Backend

This branch implements a comprehensive authentication system for the StackWizard backend template with FastAPI, SQLAlchemy 2.0 (async), and modern security practices.

## ✨ Features Implemented

### 🛡️ Authentication & Security
- **JWT Tokens**: Access and refresh token system
- **Password Security**: Bcrypt hashing with configurable rounds
- **Email Verification**: Token-based email verification system
- **Password Recovery**: Secure password reset via email tokens
- **User Permissions**: Role-based access control (superuser/admin)

### 👤 User Management
- **UUID Primary Keys**: PostgreSQL UUID for better security
- **User Profiles**: Email, username, full name support
- **Account States**: Active/inactive, verified/unverified
- **Login Tracking**: Last login timestamp and login count
- **Admin Controls**: Full user management for superusers

### 🗄️ Database & Migrations
- **Async SQLAlchemy 2.0**: Modern async database operations
- **Alembic Migrations**: Database schema versioning
- **PostgreSQL**: Full PostgreSQL support with async drivers
- **Auto-initialization**: Creates first superuser on startup

## 🏗️ Architecture

### Models (`app/models/`)
- **User Model**: Comprehensive user model with UUID, authentication fields, and metadata

### Schemas (`app/schemas/`)
- **Authentication Schemas**: Login, register, token, password reset
- **User Schemas**: CRUD operations, admin operations, responses
- **Validation**: Strong password requirements and email validation

### Services (`app/services/`)
- **AuthService**: JWT token management, password hashing, user lookups
- **SecurityService**: Password strength validation, secure token generation

### API Endpoints (`app/api/v1/`)

#### Authentication (`/api/v1/auth/`)
- `POST /login` - OAuth2 compatible login
- `POST /login-json` - JSON login with remember me
- `POST /register` - User registration
- `POST /refresh` - Refresh access tokens
- `POST /logout` - User logout
- `POST /password-recovery/{email}` - Request password reset
- `POST /reset-password` - Reset password with token
- `GET /verify-token` - Verify current token

#### User Management (`/api/v1/users/`)
- `GET /me` - Get current user info
- `PUT /me` - Update current user
- `PUT /me/password` - Change password
- `DELETE /me` - Deactivate account
- `POST /verify-email/{token}` - Verify email address
- `POST /resend-verification` - Resend verification email

#### Admin Panel (`/api/v1/admin/`)
- `GET /users` - List all users (with filtering)
- `GET /users/stats` - User statistics
- `GET /users/{id}` - Get specific user
- `POST /users` - Create user as admin
- `PUT /users/{id}` - Update user as admin
- `DELETE /users/{id}` - Deactivate user
- `POST /users/{id}/activate` - Activate user
- `POST /users/{id}/make-superuser` - Grant admin rights
- `POST /users/{id}/remove-superuser` - Remove admin rights
- `POST /users/{id}/verify-email` - Manually verify email

## 🔧 Configuration

### Environment Variables
```env
# Authentication
SECRET_KEY=your-very-secure-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@yourapp.com
```

### Database
```env
DATABASE_URL=postgresql://user:password@db:5432/database
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Migrations
```bash
# Initialize database and create superuser
python scripts/migrate.py init

# Or just run migrations
alembic upgrade head
```

### 4. Start Server
```bash
uvicorn app.main:app --reload
```

### 5. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one digit
- Maximum 128 characters

### Token Security
- JWT tokens with expiration
- Separate access and refresh tokens
- Secure token generation for password reset
- Email verification tokens

### Access Control
- Role-based permissions (user, superuser)
- Protected admin endpoints
- Email verification requirements
- Account activation/deactivation

## 🧪 Testing

### Create Test User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","username":"testuser"}'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123"
```

### Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔄 Migration from Previous Version

The new authentication system is backward compatible. Existing endpoints are still available under `/api/` for legacy support.

### Breaking Changes
- Database schema requires migration (UUID primary keys)
- New environment variables required
- User model structure changed

## 📝 TODO
- [ ] Email service implementation (SMTP)
- [ ] Rate limiting for auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Two-factor authentication (2FA)
- [ ] Social login integration
- [ ] Audit logging system