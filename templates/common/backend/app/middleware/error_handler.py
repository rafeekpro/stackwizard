"""
Error Handler Middleware
Comprehensive error handling for the application
"""
import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from pydantic import ValidationError

from app.core.exceptions import (
    BaseAppException,
    DatabaseException,
    ValidationException,
    ResourceNotFoundException
)

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """
    Middleware for handling all application errors
    Provides consistent error response format
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """
        Process request and handle any errors
        """
        # Generate request ID for tracking
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Handle the error
            return await self.handle_error(request, e, request_id)
    
    async def handle_error(
        self,
        request: Request,
        error: Exception,
        request_id: str
    ) -> JSONResponse:
        """
        Handle different types of errors and return appropriate response
        """
        # Log the error
        logger.error(
            f"Request {request_id} failed: {str(error)}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        # Determine error response based on exception type
        if isinstance(error, BaseAppException):
            return self.handle_app_exception(error, request_id)
        
        elif isinstance(error, RequestValidationError):
            return self.handle_validation_error(error, request_id)
        
        elif isinstance(error, StarletteHTTPException):
            return self.handle_http_exception(error, request_id)
        
        elif isinstance(error, IntegrityError):
            return self.handle_integrity_error(error, request_id)
        
        elif isinstance(error, DataError):
            return self.handle_data_error(error, request_id)
        
        elif isinstance(error, SQLAlchemyError):
            return self.handle_database_error(error, request_id)
        
        elif isinstance(error, ValidationError):
            return self.handle_pydantic_error(error, request_id)
        
        else:
            return self.handle_unexpected_error(error, request_id)
    
    def handle_app_exception(
        self,
        error: BaseAppException,
        request_id: str
    ) -> JSONResponse:
        """Handle application-specific exceptions"""
        return self.create_error_response(
            status_code=error.status_code,
            error_code=error.error_code,
            detail=error.detail,
            request_id=request_id
        )
    
    def handle_validation_error(
        self,
        error: RequestValidationError,
        request_id: str
    ) -> JSONResponse:
        """Handle FastAPI request validation errors"""
        errors = []
        for err in error.errors():
            field = ".".join(str(x) for x in err.get("loc", []))
            errors.append({
                "field": field,
                "message": err.get("msg", "Validation error"),
                "type": err.get("type", "unknown")
            })
        
        return self.create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            detail="Request validation failed",
            errors=errors,
            request_id=request_id
        )
    
    def handle_http_exception(
        self,
        error: StarletteHTTPException,
        request_id: str
    ) -> JSONResponse:
        """Handle Starlette HTTP exceptions"""
        return self.create_error_response(
            status_code=error.status_code,
            error_code="HTTP_ERROR",
            detail=error.detail,
            request_id=request_id
        )
    
    def handle_integrity_error(
        self,
        error: IntegrityError,
        request_id: str
    ) -> JSONResponse:
        """Handle database integrity constraint violations"""
        detail = "Database constraint violation"
        error_code = "INTEGRITY_ERROR"
        
        # Parse common integrity errors
        error_str = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        if "duplicate key" in error_str.lower() or "unique constraint" in error_str.lower():
            detail = "A record with this value already exists"
            error_code = "DUPLICATE_ENTRY"
        elif "foreign key" in error_str.lower():
            detail = "Referenced record does not exist"
            error_code = "FOREIGN_KEY_VIOLATION"
        elif "not null" in error_str.lower():
            detail = "Required field is missing"
            error_code = "NULL_CONSTRAINT_VIOLATION"
        
        return self.create_error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code,
            detail=detail,
            request_id=request_id
        )
    
    def handle_data_error(
        self,
        error: DataError,
        request_id: str
    ) -> JSONResponse:
        """Handle database data errors"""
        return self.create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="DATA_ERROR",
            detail="Invalid data format",
            request_id=request_id
        )
    
    def handle_database_error(
        self,
        error: SQLAlchemyError,
        request_id: str
    ) -> JSONResponse:
        """Handle general database errors"""
        return self.create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            detail="Database operation failed",
            request_id=request_id
        )
    
    def handle_pydantic_error(
        self,
        error: ValidationError,
        request_id: str
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        errors = []
        for err in error.errors():
            field = ".".join(str(x) for x in err.get("loc", []))
            errors.append({
                "field": field,
                "message": err.get("msg", "Validation error"),
                "type": err.get("type", "unknown")
            })
        
        return self.create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            detail="Data validation failed",
            errors=errors,
            request_id=request_id
        )
    
    def handle_unexpected_error(
        self,
        error: Exception,
        request_id: str
    ) -> JSONResponse:
        """Handle unexpected errors"""
        # Log full traceback for unexpected errors
        logger.error(
            f"Unexpected error in request {request_id}: {traceback.format_exc()}"
        )
        
        # Don't expose internal error details in production
        return self.create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            detail="An unexpected error occurred",
            request_id=request_id
        )
    
    def create_error_response(
        self,
        status_code: int,
        error_code: str,
        detail: Any,
        request_id: str,
        errors: Optional[list] = None
    ) -> JSONResponse:
        """
        Create standardized error response
        """
        response_body = {
            "error": {
                "code": error_code,
                "message": detail if isinstance(detail, str) else str(detail),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id
            }
        }
        
        # Add detailed errors if provided
        if errors:
            response_body["error"]["details"] = errors
        
        # Add detail object if it's a dict
        if isinstance(detail, dict):
            response_body["error"]["data"] = detail
        
        return JSONResponse(
            status_code=status_code,
            content=response_body,
            headers={
                "X-Request-ID": request_id,
                "X-Error-Code": error_code
            }
        )


def setup_exception_handlers(app):
    """
    Setup exception handlers for the FastAPI application
    """
    
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        """Handle application-specific exceptions"""
        request_id = getattr(request.state, 'request_id', str(uuid4()))
        return ErrorHandlerMiddleware(app).handle_app_exception(exc, request_id)
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        request_id = getattr(request.state, 'request_id', str(uuid4()))
        return ErrorHandlerMiddleware(app).handle_validation_error(exc, request_id)
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        request_id = getattr(request.state, 'request_id', str(uuid4()))
        return ErrorHandlerMiddleware(app).handle_http_exception(exc, request_id)
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database exceptions"""
        request_id = getattr(request.state, 'request_id', str(uuid4()))
        
        if isinstance(exc, IntegrityError):
            return ErrorHandlerMiddleware(app).handle_integrity_error(exc, request_id)
        elif isinstance(exc, DataError):
            return ErrorHandlerMiddleware(app).handle_data_error(exc, request_id)
        else:
            return ErrorHandlerMiddleware(app).handle_database_error(exc, request_id)
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        request_id = getattr(request.state, 'request_id', str(uuid4()))
        return ErrorHandlerMiddleware(app).handle_unexpected_error(exc, request_id)