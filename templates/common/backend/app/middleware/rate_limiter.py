"""
Rate Limiting Middleware
Implements request rate limiting to prevent abuse
"""
from typing import Optional, Callable
from functools import wraps
import logging

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_real_client_ip(request: Request) -> str:
    """
    Get the real client IP address, considering proxy headers
    """
    # Check for proxy headers in order of preference
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, get the first one
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "127.0.0.1"


def get_user_id(request: Request) -> str:
    """
    Get user ID from request if authenticated, otherwise use IP
    """
    # Try to get user ID from request state (set by auth dependency)
    if hasattr(request.state, "user_id") and request.state.user_id:
        return f"user:{request.state.user_id}"
    
    # Fallback to IP address
    return f"ip:{get_real_client_ip(request)}"


# Create limiter instance with custom key function
limiter = Limiter(
    key_func=get_user_id,
    default_limits=[
        f"{settings.RATE_LIMIT_PER_MINUTE}/minute" if hasattr(settings, 'RATE_LIMIT_PER_MINUTE') else "60/minute",
        f"{settings.RATE_LIMIT_PER_HOUR}/hour" if hasattr(settings, 'RATE_LIMIT_PER_HOUR') else "1000/hour"
    ],
    enabled=getattr(settings, 'RATE_LIMITING_ENABLED', True),
    headers_enabled=True,  # Include rate limit headers in response
    strategy="fixed-window",  # or "moving-window" for more precise limiting
    storage_uri=getattr(settings, 'REDIS_URL', None) or "memory://",  # Use Redis if available
)


# Custom rate limit exceeded handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors
    """
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {exc.detail}",
                "retry_after": exc.headers.get("Retry-After", "60")
            }
        }
    )
    
    # Add rate limit headers
    response.headers.update(exc.headers)
    
    # Log rate limit violation
    logger.warning(
        f"Rate limit exceeded for {get_user_id(request)} on {request.url.path}",
        extra={
            "client_ip": get_real_client_ip(request),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return response


def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI application
    """
    # Add limiter to app state
    app.state.limiter = limiter
    
    # Add exception handler
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
    
    # Add middleware for automatic rate limiting
    app.add_middleware(SlowAPIMiddleware)
    
    logger.info("Rate limiting configured successfully")


# Decorators for custom rate limits on specific endpoints
def rate_limit(
    limit: str = "10/minute",
    key_func: Optional[Callable] = None,
    error_message: Optional[str] = None
):
    """
    Decorator for applying custom rate limits to specific endpoints
    
    Usage:
        @rate_limit("5/minute")
        async def sensitive_endpoint():
            ...
    """
    def decorator(func):
        # Use the limiter's limit decorator with custom settings
        limited = limiter.limit(
            limit,
            key_func=key_func or get_user_id,
            error_message=error_message
        )(func)
        return limited
    
    return decorator


# Specific rate limiters for different endpoint types
auth_limiter = rate_limit(
    "5/minute",
    error_message="Too many authentication attempts. Please try again later."
)

admin_limiter = rate_limit(
    "30/minute",
    error_message="Admin rate limit exceeded."
)

api_limiter = rate_limit(
    "100/minute",
    error_message="API rate limit exceeded."
)

public_limiter = rate_limit(
    "20/minute",
    key_func=get_real_client_ip,
    error_message="Public endpoint rate limit exceeded."
)


class RateLimitConfig:
    """
    Configuration for rate limiting rules
    """
    # Authentication endpoints - strict limits
    AUTH_ENDPOINTS = {
        "/api/v1/auth/login": "5/minute",
        "/api/v1/auth/register": "3/minute",
        "/api/v1/auth/password-recovery": "3/minute",
        "/api/v1/auth/reset-password": "3/minute",
    }
    
    # Admin endpoints - moderate limits
    ADMIN_ENDPOINTS = {
        "/api/v1/admin/": "30/minute",
    }
    
    # Public endpoints - relaxed limits
    PUBLIC_ENDPOINTS = {
        "/api/health": "60/minute",
        "/api/v1/health": "60/minute",
        "/docs": "30/minute",
        "/redoc": "30/minute",
    }
    
    # User endpoints - standard limits
    USER_ENDPOINTS = {
        "/api/v1/users/": "60/minute",
        "/api/v1/items/": "60/minute",
    }
    
    @classmethod
    def get_limit_for_path(cls, path: str) -> Optional[str]:
        """
        Get rate limit for a specific path
        """
        # Check exact matches first
        for endpoint_dict in [cls.AUTH_ENDPOINTS, cls.ADMIN_ENDPOINTS, 
                             cls.PUBLIC_ENDPOINTS, cls.USER_ENDPOINTS]:
            for pattern, limit in endpoint_dict.items():
                if path == pattern or path.startswith(pattern):
                    return limit
        
        return None


# Middleware for path-specific rate limiting
class PathBasedRateLimitMiddleware:
    """
    Middleware that applies different rate limits based on the request path
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """
        Apply rate limiting based on request path
        """
        path = request.url.path
        custom_limit = RateLimitConfig.get_limit_for_path(path)
        
        if custom_limit:
            # Store custom limit in request state for the limiter to use
            request.state.rate_limit = custom_limit
        
        response = await call_next(request)
        return response