"""
Custom Exception Hierarchy
Provides structured exception handling for the application
"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base exception class for application-specific exceptions"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


# Authentication Exceptions
class AuthenticationException(BaseAppException):
    """Base exception for authentication errors"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="AUTH_FAILED"
        )


class InvalidCredentialsException(AuthenticationException):
    """Exception raised when credentials are invalid"""
    
    def __init__(self):
        super().__init__(detail="Invalid email or password")
        self.error_code = "INVALID_CREDENTIALS"


class TokenExpiredException(AuthenticationException):
    """Exception raised when token has expired"""
    
    def __init__(self):
        super().__init__(detail="Token has expired")
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenException(AuthenticationException):
    """Exception raised when token is invalid"""
    
    def __init__(self):
        super().__init__(detail="Invalid token")
        self.error_code = "INVALID_TOKEN"


# Authorization Exceptions
class AuthorizationException(BaseAppException):
    """Base exception for authorization errors"""
    
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="NOT_AUTHORIZED"
        )


class InsufficientPermissionsException(AuthorizationException):
    """Exception raised when user lacks required permissions"""
    
    def __init__(self, required_permission: Optional[str] = None):
        detail = "Insufficient permissions"
        if required_permission:
            detail = f"Insufficient permissions. Required: {required_permission}"
        super().__init__(detail=detail)
        self.error_code = "INSUFFICIENT_PERMISSIONS"


class ResourceOwnershipException(AuthorizationException):
    """Exception raised when user doesn't own the resource"""
    
    def __init__(self, resource_type: str = "resource"):
        super().__init__(detail=f"You don't own this {resource_type}")
        self.error_code = "NOT_RESOURCE_OWNER"


# Validation Exceptions
class ValidationException(BaseAppException):
    """Base exception for validation errors"""
    
    def __init__(self, detail: Any = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_FAILED"
        )


class FieldValidationException(ValidationException):
    """Exception raised when field validation fails"""
    
    def __init__(self, field: str, message: str):
        super().__init__(detail={field: message})
        self.error_code = "FIELD_VALIDATION_FAILED"


class PasswordValidationException(ValidationException):
    """Exception raised when password doesn't meet requirements"""
    
    def __init__(self, errors: list):
        super().__init__(detail={"message": "Password validation failed", "errors": errors})
        self.error_code = "PASSWORD_VALIDATION_FAILED"


# Resource Exceptions
class ResourceException(BaseAppException):
    """Base exception for resource-related errors"""
    pass


class ResourceNotFoundException(ResourceException):
    """Exception raised when resource is not found"""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Optional[str] = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail = f"{resource_type} with ID {resource_id} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND"
        )


class ResourceAlreadyExistsException(ResourceException):
    """Exception raised when resource already exists"""
    
    def __init__(self, resource_type: str = "Resource", field: Optional[str] = None, value: Optional[str] = None):
        detail = f"{resource_type} already exists"
        if field and value:
            detail = f"{resource_type} with {field} '{value}' already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="RESOURCE_EXISTS"
        )


class ResourceInUseException(ResourceException):
    """Exception raised when trying to delete a resource that's in use"""
    
    def __init__(self, resource_type: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource_type} is in use and cannot be deleted",
            error_code="RESOURCE_IN_USE"
        )


# Business Logic Exceptions
class BusinessLogicException(BaseAppException):
    """Base exception for business logic errors"""
    
    def __init__(self, detail: str = "Business logic error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_LOGIC_ERROR"
        )


class InvalidOperationException(BusinessLogicException):
    """Exception raised when an invalid operation is attempted"""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(detail=f"Cannot {operation}: {reason}")
        self.error_code = "INVALID_OPERATION"


class LimitExceededException(BusinessLogicException):
    """Exception raised when a limit is exceeded"""
    
    def __init__(self, limit_type: str, limit: int):
        super().__init__(detail=f"{limit_type} limit exceeded. Maximum allowed: {limit}")
        self.error_code = "LIMIT_EXCEEDED"


class StateTransitionException(BusinessLogicException):
    """Exception raised when an invalid state transition is attempted"""
    
    def __init__(self, from_state: str, to_state: str):
        super().__init__(detail=f"Invalid state transition from {from_state} to {to_state}")
        self.error_code = "INVALID_STATE_TRANSITION"


# Database Exceptions
class DatabaseException(BaseAppException):
    """Base exception for database-related errors"""
    
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )


class DatabaseConnectionException(DatabaseException):
    """Exception raised when database connection fails"""
    
    def __init__(self):
        super().__init__(detail="Failed to connect to database")
        self.error_code = "DATABASE_CONNECTION_FAILED"


class DatabaseTransactionException(DatabaseException):
    """Exception raised when database transaction fails"""
    
    def __init__(self, operation: str = "transaction"):
        super().__init__(detail=f"Database {operation} failed")
        self.error_code = "DATABASE_TRANSACTION_FAILED"


# External Service Exceptions
class ExternalServiceException(BaseAppException):
    """Base exception for external service errors"""
    
    def __init__(self, service: str, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service}: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )


class EmailServiceException(ExternalServiceException):
    """Exception raised when email service fails"""
    
    def __init__(self, detail: str = "Failed to send email"):
        super().__init__(service="Email Service", detail=detail)
        self.error_code = "EMAIL_SERVICE_ERROR"


class PaymentServiceException(ExternalServiceException):
    """Exception raised when payment service fails"""
    
    def __init__(self, detail: str = "Payment processing failed"):
        super().__init__(service="Payment Service", detail=detail)
        self.error_code = "PAYMENT_SERVICE_ERROR"


# Rate Limiting Exceptions
class RateLimitException(BaseAppException):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str = "minute"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED"
        )


# File Operation Exceptions
class FileOperationException(BaseAppException):
    """Base exception for file operation errors"""
    
    def __init__(self, detail: str = "File operation failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="FILE_OPERATION_FAILED"
        )


class FileNotFoundException(FileOperationException):
    """Exception raised when file is not found"""
    
    def __init__(self, filename: str):
        super().__init__(detail=f"File '{filename}' not found")
        self.error_code = "FILE_NOT_FOUND"


class FileSizeException(FileOperationException):
    """Exception raised when file size exceeds limit"""
    
    def __init__(self, max_size_mb: int):
        super().__init__(detail=f"File size exceeds maximum allowed size of {max_size_mb}MB")
        self.error_code = "FILE_SIZE_EXCEEDED"


class FileTypeException(FileOperationException):
    """Exception raised when file type is not allowed"""
    
    def __init__(self, allowed_types: list):
        super().__init__(detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}")
        self.error_code = "INVALID_FILE_TYPE"


# Configuration Exceptions
class ConfigurationException(BaseAppException):
    """Exception raised when configuration is invalid"""
    
    def __init__(self, config_key: str, detail: str = "Configuration error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error for '{config_key}': {detail}",
            error_code="CONFIGURATION_ERROR"
        )