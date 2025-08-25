"""
CSRF Protection Middleware
Implements Cross-Site Request Forgery protection
"""
import secrets
import logging
from typing import Optional, Set, Dict
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware
    Validates CSRF tokens for state-changing operations
    """
    
    # Methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Paths to exclude from CSRF protection
    EXCLUDED_PATHS = {
        "/api/v1/auth/login",  # Login uses credentials
        "/api/v1/auth/register",  # Public registration
        "/api/v1/auth/refresh",  # Token refresh
        "/api/health",  # Health checks
        "/api/v1/health",
        "/docs",  # API documentation
        "/redoc",
        "/openapi.json",
    }
    
    # Headers to check for CSRF token
    TOKEN_HEADERS = ["X-CSRF-Token", "X-XSRF-Token"]
    
    def __init__(
        self,
        app,
        secret_key: Optional[str] = None,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        token_length: int = 32,
        max_age: int = 3600,  # 1 hour
        secure: bool = True,
        httponly: bool = False,  # CSRF cookie should be readable by JS
        samesite: str = "strict"
    ):
        super().__init__(app)
        self.secret_key = secret_key or getattr(settings, 'SECRET_KEY', secrets.token_urlsafe(32))
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.token_length = token_length
        self.max_age = max_age
        self.secure = secure and not settings.DEBUG  # Only secure in production
        self.httponly = httponly
        self.samesite = samesite
        
        # Token storage (in production, use Redis or database)
        self.tokens: Set[str] = set()
        self.token_timestamps: dict = {}
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate CSRF token if necessary
        """
        # Skip CSRF check for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Skip CSRF check for safe methods
        if request.method not in self.PROTECTED_METHODS:
            response = await call_next(request)
            # Set CSRF token for GET requests
            if request.method == "GET":
                await self._set_csrf_token(request, response)
            return response
        
        # Validate CSRF token for protected methods
        if not await self._validate_csrf_token(request):
            return self._csrf_error_response()
        
        # Process request
        response = await call_next(request)
        
        # Refresh CSRF token if needed
        await self._refresh_csrf_token(request, response)
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if path is excluded from CSRF protection
        """
        # Exact match
        if path in self.EXCLUDED_PATHS:
            return True
        
        # Prefix match for API docs
        excluded_prefixes = ["/docs", "/redoc", "/openapi"]
        return any(path.startswith(prefix) for prefix in excluded_prefixes)
    
    async def _generate_csrf_token(self) -> str:
        """
        Generate a new CSRF token
        """
        token = secrets.token_urlsafe(self.token_length)
        self.tokens.add(token)
        self.token_timestamps[token] = datetime.now(timezone.utc)
        
        # Clean up old tokens
        await self._cleanup_expired_tokens()
        
        return token
    
    async def _validate_csrf_token(self, request: Request) -> bool:
        """
        Validate CSRF token from request
        """
        # Get token from cookie
        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            logger.warning(f"CSRF validation failed: No cookie token for {request.url.path}")
            return False
        
        # Get token from header or form data
        header_token = None
        
        # Check headers
        for header_name in self.TOKEN_HEADERS:
            header_token = request.headers.get(header_name)
            if header_token:
                break
        
        # Check form data if no header token
        if not header_token and request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            header_token = form.get("csrf_token") or form.get("_csrf")
        
        # Check JSON body if no header token
        if not header_token and request.headers.get("content-type", "").startswith("application/json"):
            except (JSONDecodeError, ValueError):
                pass
        
        if not header_token:
            logger.warning(f"CSRF validation failed: No header token for {request.url.path}")
            return False
        
        # Validate tokens match and are valid
        if cookie_token != header_token:
            logger.warning(f"CSRF validation failed: Token mismatch for {request.url.path}")
            return False
        
        # Check if token exists and is not expired
        if cookie_token not in self.tokens:
            logger.warning(f"CSRF validation failed: Unknown token for {request.url.path}")
            return False
        
        # Check token age
        token_age = datetime.now(timezone.utc) - self.token_timestamps.get(cookie_token, datetime.now(timezone.utc))
        if token_age > timedelta(seconds=self.max_age):
            logger.warning(f"CSRF validation failed: Expired token for {request.url.path}")
            self.tokens.discard(cookie_token)
            del self.token_timestamps[cookie_token]
            return False
        
        return True
    
    async def _set_csrf_token(self, request: Request, response):
        """
        Set CSRF token in response cookie
        """
        # Check if token already exists
        existing_token = request.cookies.get(self.cookie_name)
        
        if existing_token and existing_token in self.tokens:
            # Validate token age
            token_age = datetime.now(timezone.utc) - self.token_timestamps.get(existing_token, datetime.now(timezone.utc))
            if token_age < timedelta(seconds=self.max_age):
                # Token is still valid, don't regenerate
                return response
        
        # Generate new token
        token = await self._generate_csrf_token()
        
        # Set cookie
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.max_age,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite,
            path="/"
        )
        
        # Also set token in response header for easy access
        response.headers[self.header_name] = token
        
        return response
    
    async def _refresh_csrf_token(self, request: Request, response):
        """
        Refresh CSRF token if it's close to expiration
        """
        existing_token = request.cookies.get(self.cookie_name)
        
        if existing_token and existing_token in self.tokens:
            token_age = datetime.now(timezone.utc) - self.token_timestamps.get(existing_token, datetime.now(timezone.utc))
            
            # Refresh if token is older than half of max age
            if token_age > timedelta(seconds=self.max_age / 2):
                await self._set_csrf_token(request, response)
    
    async def _cleanup_expired_tokens(self):
        """
        Remove expired tokens from memory
        """
        current_time = datetime.now(timezone.utc)
        expired_tokens = []
        
        for token, timestamp in self.token_timestamps.items():
            if current_time - timestamp > timedelta(seconds=self.max_age):
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self.tokens.discard(token)
            del self.token_timestamps[token]
    
    def _csrf_error_response(self) -> JSONResponse:
        """
        Return CSRF validation error response
        """
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": {
                    "code": "CSRF_VALIDATION_FAILED",
                    "message": "CSRF token validation failed. Please refresh the page and try again."
                }
            }
        )


def setup_csrf_protection(app):
    """
    Setup CSRF protection for the FastAPI application
    """
    # Only enable CSRF protection in production or if explicitly enabled
    if not settings.DEBUG or getattr(settings, 'CSRF_ENABLED', False):
        app.add_middleware(
            CSRFProtectionMiddleware,
            secret_key=settings.SECRET_KEY,
            secure=not settings.DEBUG,
            max_age=3600
        )
        logger.info("CSRF protection enabled")
    else:
        logger.info("CSRF protection disabled in debug mode")


# Dependency for getting CSRF token in endpoints
async def get_csrf_token(request: Request) -> str:
    """
    Dependency to get current CSRF token
    Can be used in endpoints that need to return the token
    """
    token = request.cookies.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
    return token


# Utility class for managing CSRF tokens with Redis
class CSRFTokenStore:
    """
    Redis-based CSRF token storage for production use
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.prefix = "csrf:"
        self.ttl = 3600  # 1 hour
    
    async def store_token(self, token: str, user_id: Optional[str] = None):
        """
        Store CSRF token in Redis
        """
        if not self.redis:
            return
        
        key = f"{self.prefix}{token}"
        value = user_id or "anonymous"
        await self.redis.setex(key, self.ttl, value)
    
    async def validate_token(self, token: str) -> bool:
        """
        Validate CSRF token exists in Redis
        """
        if not self.redis:
            return True  # Skip validation if Redis not available
        
        key = f"{self.prefix}{token}"
        exists = await self.redis.exists(key)
        
        # Refresh TTL on valid token
        if exists:
            await self.redis.expire(key, self.ttl)
        
        return exists
    
    async def revoke_token(self, token: str):
        """
        Revoke CSRF token
        """
        if not self.redis:
            return
        
        key = f"{self.prefix}{token}"
        await self.redis.delete(key)
    
    async def revoke_user_tokens(self, user_id: str):
        """
        Revoke all CSRF tokens for a user
        """
        if not self.redis:
            return
        
        # Scan for all tokens belonging to user
        pattern = f"{self.prefix}*"
        cursor = 0
        
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            
            for key in keys:
                value = await self.redis.get(key)
                if value and value.decode() == user_id:
                    await self.redis.delete(key)
            
            if cursor == 0:
                break