# ⚙️ Configuration

Complete configuration guide for StackWizard-generated projects, covering environment variables, service settings, and production configurations.

## 🌍 Environment Variables

### Overview

The project uses environment variables for configuration, following the 12-factor app methodology. All sensitive data and environment-specific settings are stored in `.env` files.

```bash
# File structure
.env                 # Main environment file (git-ignored)
.env.example         # Template with all variables (committed)
.env.development     # Development overrides (optional)
.env.test           # Test environment (optional)
.env.production     # Production settings (never commit)
```

### Core Environment Variables

#### Database Configuration

```env
# PostgreSQL Database
DB_HOST=db                          # Database host (use 'localhost' for local dev)
DB_PORT=5432                        # PostgreSQL port
DB_NAME=myapp_db                    # Database name
DB_USER=myapp_user                  # Database username
DB_PASSWORD=secure_password_here    # Database password (use strong password in production)

# Database URL (alternative format)
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Database Pool Settings
DB_POOL_SIZE=10                     # Connection pool size
DB_MAX_OVERFLOW=20                  # Maximum overflow connections
DB_POOL_TIMEOUT=30                  # Pool timeout in seconds
DB_POOL_RECYCLE=1800               # Recycle connections after 30 minutes
```

#### Backend Configuration

```env
# FastAPI Settings
BACKEND_HOST=0.0.0.0               # Backend host
BACKEND_PORT=8000                  # Backend port
BACKEND_RELOAD=true                # Auto-reload in development
BACKEND_WORKERS=4                  # Number of workers (production)

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256                    # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=30     # Access token expiration
REFRESH_TOKEN_EXPIRE_DAYS=7        # Refresh token expiration

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# API Settings
API_V1_STR=/api/v1                 # API version prefix
PROJECT_NAME=StackWizard App       # Project name for docs
PROJECT_VERSION=1.0.0              # Project version

# Email Settings (optional)
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@stackwizard.com
EMAILS_FROM_NAME=StackWizard

# Superuser (initial admin)
FIRST_SUPERUSER=admin@stackwizard.com
FIRST_SUPERUSER_USERNAME=admin
FIRST_SUPERUSER_PASSWORD=changethis
```

#### Frontend Configuration

```env
# React App Settings
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
REACT_APP_APP_NAME=StackWizard
REACT_APP_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_AUTH=true
REACT_APP_ENABLE_REGISTRATION=true
REACT_APP_ENABLE_SOCIAL_LOGIN=false
REACT_APP_ENABLE_DARK_MODE=true

# Third-party Services
REACT_APP_GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X
REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_xxx

# Development Tools
REACT_APP_DEBUG_MODE=false
REACT_APP_LOG_LEVEL=info
```

#### Docker Configuration

```env
# Docker Compose Settings
COMPOSE_PROJECT_NAME=stackwizard
COMPOSE_FILE=docker-compose.yml

# Container Settings
POSTGRES_VERSION=15-alpine
PYTHON_VERSION=3.11
NODE_VERSION=18-alpine

# Volume Paths
POSTGRES_DATA_PATH=./volumes/postgres
BACKEND_LOGS_PATH=./volumes/logs/backend
FRONTEND_BUILD_PATH=./volumes/dist/frontend
```

## 🔧 Application Configuration Files

### Backend Configuration (`backend/app/core/config.py`)

```python
from typing import List, Union
from pydantic import BaseSettings, AnyHttpUrl, EmailStr, validator
from secrets import token_urlsafe

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StackWizard API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = None
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    EMAILS_FROM_EMAIL: EmailStr = None
    EMAILS_FROM_NAME: str = None
    
    # Superuser
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery (optional)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
```

### Frontend Configuration (`frontend/src/config/index.js`)

```javascript
const config = {
  // API Configuration
  API_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  API_VERSION: process.env.REACT_APP_API_VERSION || 'v1',
  API_TIMEOUT: 30000, // 30 seconds
  
  // App Configuration
  APP_NAME: process.env.REACT_APP_APP_NAME || 'StackWizard',
  APP_VERSION: process.env.REACT_APP_APP_VERSION || '1.0.0',
  
  // Feature Flags
  FEATURES: {
    AUTH_ENABLED: process.env.REACT_APP_ENABLE_AUTH === 'true',
    REGISTRATION_ENABLED: process.env.REACT_APP_ENABLE_REGISTRATION === 'true',
    SOCIAL_LOGIN_ENABLED: process.env.REACT_APP_ENABLE_SOCIAL_LOGIN === 'true',
    DARK_MODE_ENABLED: process.env.REACT_APP_ENABLE_DARK_MODE === 'true',
  },
  
  // Storage Keys
  STORAGE_KEYS: {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_DATA: 'user_data',
    THEME: 'theme_preference',
    LANGUAGE: 'language_preference',
  },
  
  // Routes
  ROUTES: {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    DASHBOARD: '/dashboard',
    PROFILE: '/profile',
    SETTINGS: '/settings',
  },
  
  // Pagination
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 10,
    PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
  },
  
  // Validation
  VALIDATION: {
    PASSWORD_MIN_LENGTH: 8,
    PASSWORD_REGEX: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
    EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  
  // Third-party Services
  SERVICES: {
    GOOGLE_ANALYTICS_ID: process.env.REACT_APP_GOOGLE_ANALYTICS_ID,
    SENTRY_DSN: process.env.REACT_APP_SENTRY_DSN,
    STRIPE_PUBLIC_KEY: process.env.REACT_APP_STRIPE_PUBLIC_KEY,
  },
  
  // Development
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  DEBUG_MODE: process.env.REACT_APP_DEBUG_MODE === 'true',
  LOG_LEVEL: process.env.REACT_APP_LOG_LEVEL || 'info',
};

export default config;
```

## 🐳 Docker Configuration

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:${POSTGRES_VERSION:-15-alpine}
    container_name: ${COMPOSE_PROJECT_NAME}_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: ${PYTHON_VERSION:-3.11}
    container_name: ${COMPOSE_PROJECT_NAME}_backend
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      SECRET_KEY: ${SECRET_KEY}
      BACKEND_CORS_ORIGINS: ${CORS_ORIGINS}
    volumes:
      - ./backend:/app
      - backend_logs:/app/logs
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NODE_VERSION: ${NODE_VERSION:-18-alpine}
    container_name: ${COMPOSE_PROJECT_NAME}_frontend
    restart: unless-stopped
    environment:
      REACT_APP_API_URL: http://backend:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    depends_on:
      - backend
    command: npm start
    networks:
      - app-network

volumes:
  postgres_data:
  backend_logs:

networks:
  app-network:
    driver: bridge
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
    networks:
      - app-network
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always
    depends_on:
      - backend
    networks:
      - app-network
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.25'
          memory: 256M

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - frontend_dist:/usr/share/nginx/html
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  frontend_dist:
  redis_data:

networks:
  app-network:
    driver: overlay
    attachable: true
```

## 🔒 Security Configuration

### SSL/TLS Configuration

```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### CORS Configuration

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Logging Configuration

### Backend Logging

```python
# backend/app/core/logging.py
import logging
import sys
from pathlib import Path
from loguru import logger

# Remove default handler
logger.remove()

# Console logging
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# File logging
log_path = Path("logs")
log_path.mkdir(exist_ok=True)

logger.add(
    log_path / "app.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)

# Error logging
logger.add(
    log_path / "error.log",
    rotation="500 MB",
    retention="30 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)
```

### Frontend Logging

```javascript
// frontend/src/utils/logger.js
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

class Logger {
  constructor(level = 'INFO') {
    this.level = LOG_LEVELS[level] || LOG_LEVELS.INFO;
  }
  
  debug(...args) {
    if (this.level <= LOG_LEVELS.DEBUG) {
      console.debug('[DEBUG]', new Date().toISOString(), ...args);
    }
  }
  
  info(...args) {
    if (this.level <= LOG_LEVELS.INFO) {
      console.info('[INFO]', new Date().toISOString(), ...args);
    }
  }
  
  warn(...args) {
    if (this.level <= LOG_LEVELS.WARN) {
      console.warn('[WARN]', new Date().toISOString(), ...args);
    }
  }
  
  error(...args) {
    if (this.level <= LOG_LEVELS.ERROR) {
      console.error('[ERROR]', new Date().toISOString(), ...args);
      
      // Send to error tracking service
      if (window.Sentry) {
        window.Sentry.captureException(args[0]);
      }
    }
  }
}

export default new Logger(process.env.REACT_APP_LOG_LEVEL);
```

## 🚀 Performance Configuration

### Database Optimization

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DEBUG_MODE,  # SQL logging in debug mode
    connect_args={
        "server_settings": {
            "application_name": settings.PROJECT_NAME,
            "jit": "off"
        },
        "command_timeout": 60,
        "options": "-c statement_timeout=30000"  # 30 seconds
    }
)
```

### Redis Caching

```python
# backend/app/core/cache.py
import redis
from functools import wraps
import json
import hashlib

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 5,  # TCP_KEEPCNT
    }
)

def cache_key_wrapper(prefix: str):
    def generate_cache_key(*args, **kwargs):
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    return generate_cache_key
```

## 🌐 Internationalization Configuration

```javascript
// frontend/src/i18n/config.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslations from './locales/en.json';
import esTranslations from './locales/es.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      es: { translation: esTranslations },
    },
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

## 📝 Configuration Best Practices

1. **Never commit sensitive data** - Use `.env` files and keep them git-ignored
2. **Use environment-specific configs** - Separate dev, test, and production settings
3. **Validate configuration** - Use Pydantic or similar for validation
4. **Document all variables** - Maintain updated `.env.example`
5. **Use secure defaults** - Default to secure settings when variables are missing
6. **Rotate secrets regularly** - Especially in production
7. **Use secret management tools** - Consider HashiCorp Vault, AWS Secrets Manager
8. **Monitor configuration changes** - Log configuration updates
9. **Keep configs DRY** - Avoid duplication, use inheritance
10. **Version control configs** - Track non-sensitive configuration changes

---

**Next**: [Development Workflow](Development-Workflow) →