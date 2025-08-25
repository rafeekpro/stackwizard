"""
Security Headers Middleware
Implements security headers to protect against common web vulnerabilities
"""
import logging
from typing import Dict, Optional, List

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    
    def __init__(
        self,
        app,
        custom_headers: Optional[Dict[str, str]] = None,
        excluded_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.custom_headers = custom_headers or {}
        self.excluded_paths = excluded_paths or ["/docs", "/redoc", "/openapi.json"]
        
        # Configure headers based on environment
        self.is_production = not settings.DEBUG
    
    async def dispatch(self, request: Request, call_next):
        """
        Add security headers to response
        """
        response = await call_next(request)
        
        # Skip headers for excluded paths (like documentation)
        if not self._is_excluded_path(request.url.path):
            self._add_security_headers(response, request)
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if path should be excluded from security headers
        """
        return any(path.startswith(excluded) for excluded in self.excluded_paths)
    
    def _add_security_headers(self, response: Response, request: Request):
        """
        Add security headers to the response
        """
        # Basic Security Headers (always applied)
        headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Enable browser XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy (formerly Feature Policy)
            "Permissions-Policy": self._get_permissions_policy(),
            
            # Remove server header info
            "Server": "StackWizard",
        }
        
        # Content Security Policy
        headers["Content-Security-Policy"] = self._get_csp(request)
        
        # Production-only headers
        if self.is_production:
            # HTTP Strict Transport Security
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            
            # Expect-CT for Certificate Transparency
            headers["Expect-CT"] = 'max-age=86400, enforce'
        
        # Add custom headers
        headers.update(self.custom_headers)
        
        # Apply headers to response
        for header, value in headers.items():
            response.headers[header] = value
    
    def _get_csp(self, request: Request) -> str:
        """
        Generate Content Security Policy based on environment
        """
        if not self.is_production:
            # Relaxed CSP for development
            return (
                "default-src 'self' http: https:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' http: https:; "
                "style-src 'self' 'unsafe-inline' http: https:; "
                "img-src 'self' data: blob: http: https:; "
                "font-src 'self' data: http: https:; "
                "connect-src 'self' http: https: ws: wss:; "
                "frame-ancestors 'none';"
            )
        
        # Strict CSP for production
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'strict-dynamic'",
            "style-src 'self' 'unsafe-inline'",  # Unsafe-inline for CSS (can be improved with nonces)
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests",
        ]
        
        # Add nonce for scripts if available
        if hasattr(request.state, "csp_nonce"):
            csp_directives[1] = f"script-src 'self' 'nonce-{request.state.csp_nonce}'"
        
        # Add report URI if configured
        if hasattr(settings, 'CSP_REPORT_URI'):
            csp_directives.append(f"report-uri {settings.CSP_REPORT_URI}")
        
        return "; ".join(csp_directives) + ";"
    
    def _get_permissions_policy(self) -> str:
        """
        Generate Permissions Policy (formerly Feature Policy)
        """
        policies = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()",
            "interest-cohort=()",  # Opt out of FLoC
            "autoplay=(self)",
            "fullscreen=(self)",
            "picture-in-picture=(self)",
        ]
        
        return ", ".join(policies)


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with security considerations
    """
    
    def __init__(
        self,
        app,
        allowed_origins: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None,
        expose_headers: Optional[List[str]] = None,
        allow_credentials: bool = False,
        max_age: int = 3600
    ):
        super().__init__(app)
        
        # Use settings or defaults
        self.allowed_origins = allowed_origins or self._get_allowed_origins()
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["Content-Type", "Authorization", "X-CSRF-Token"]
        self.expose_headers = expose_headers or ["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
        self.allow_credentials = allow_credentials
        self.max_age = max_age
    
    def _get_allowed_origins(self) -> List[str]:
        """
        Get allowed origins from settings
        """
        if hasattr(settings, 'BACKEND_CORS_ORIGINS'):
            return settings.BACKEND_CORS_ORIGINS
        
        # Default origins based on environment
        if settings.DEBUG:
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]
        
        # Production should explicitly set allowed origins
        return []
    
    async def dispatch(self, request: Request, call_next):
        """
        Handle CORS headers
        """
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._handle_preflight(origin)
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if origin and self._is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            
            if self.expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        return response
    
    def _is_allowed_origin(self, origin: str) -> bool:
        """
        Check if origin is allowed
        """
        # Allow all origins in debug mode with wildcard
        if settings.DEBUG and "*" in self.allowed_origins:
            return True
        
        # Check exact match
        if origin in self.allowed_origins:
            return True
        
        # Check wildcard subdomains (e.g., https://*.example.com)
        for allowed in self.allowed_origins:
            if "*" in allowed:
                pattern = allowed.replace("*", ".*")
                import re
                if re.match(pattern, origin):
                    return True
        
        return False
    
    def _handle_preflight(self, origin: Optional[str]):
        """
        Handle CORS preflight requests
        """
        headers = {}
        
        if origin and self._is_allowed_origin(origin):
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
            headers["Access-Control-Max-Age"] = str(self.max_age)
            
            if self.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"
        
        return Response(status_code=200, headers=headers)


def setup_security_headers(app):
    """
    Setup security headers for the FastAPI application
    """
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add enhanced CORS middleware if needed
    if hasattr(settings, 'BACKEND_CORS_ORIGINS') and settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSSecurityMiddleware,
            allowed_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True
        )
    
    logger.info("Security headers configured")


# Utility functions for generating secure values
def generate_csp_nonce() -> str:
    """
    Generate a CSP nonce for inline scripts
    """
    import secrets
    import base64
    
    # Generate random bytes and encode as base64
    nonce_bytes = secrets.token_bytes(16)
    nonce = base64.b64encode(nonce_bytes).decode('ascii')
    
    return nonce


def add_csp_nonce(request: Request) -> str:
    """
    Add CSP nonce to request state
    Can be used as a dependency in endpoints
    """
    nonce = generate_csp_nonce()
    request.state.csp_nonce = nonce
    return nonce


# Security headers configuration class
class SecurityHeadersConfig:
    """
    Configuration for security headers
    """
    
    PRODUCTION_HEADERS = {
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'strict-dynamic'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; upgrade-insecure-requests;",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cache-Control": "no-store, no-cache, must-revalidate, private",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    
    DEVELOPMENT_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "same-origin",
    }
    
    API_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
        "Content-Type": "application/json",
    }
    
    @classmethod
    def get_headers(cls, environment: str = "production") -> Dict[str, str]:
        """
        Get headers based on environment
        """
        if environment == "production":
            return cls.PRODUCTION_HEADERS
        elif environment == "development":
            return cls.DEVELOPMENT_HEADERS
        else:
            return cls.API_HEADERS