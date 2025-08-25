"""
Authentication Validators
Validation utilities for authentication operations
"""
import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status


def validate_login_credentials(
    username_or_email: str,
    password: str
) -> Dict[str, str]:
    """
    Validate login credentials
    
    Args:
        username_or_email: Username or email for login
        password: Password for login
    
    Returns:
        Dictionary with validated credentials
    
    Raises:
        HTTPException: If credentials are invalid
    """
    if not username_or_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required"
        )
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    # Determine if it's an email or username
    is_email = '@' in username_or_email
    
    if is_email:
        from .common import validate_email
        username_or_email = validate_email(username_or_email)
    else:
        from .user_validators import validate_username
        username_or_email = validate_username(username_or_email)
    
    return {
        'identifier': username_or_email,
        'password': password,
        'is_email': is_email
    }


def validate_registration_data(
    email: str,
    password: str,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    terms_accepted: bool = False
) -> Dict:
    """
    Validate registration data
    
    Args:
        email: Email address
        password: Password
        username: Optional username
        full_name: Optional full name
        terms_accepted: Whether terms are accepted
    
    Returns:
        Dictionary with validated registration data
    
    Raises:
        HTTPException: If registration data is invalid
    """
    from .common import validate_email, sanitize_string
    from .user_validators import validate_username, validate_password_strength
    
    # Validate required fields
    validated_data = {
        'email': validate_email(email)
    }
    
    # Validate password
    is_valid, errors = validate_password_strength(password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors}
        )
    validated_data['password'] = password
    
    # Validate optional fields
    if username:
        validated_data['username'] = validate_username(username)
    
    if full_name:
        validated_data['full_name'] = sanitize_string(
            full_name,
            max_length=100,
            min_length=2,
            field_name="Full name"
        )
    
    # Check terms acceptance
    if not terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the terms and conditions"
        )
    
    return validated_data


def validate_token_format(token: str, token_type: str = "Bearer") -> str:
    """
    Validate token format
    
    Args:
        token: Token string to validate
        token_type: Expected token type
    
    Returns:
        Extracted token value
    
    Raises:
        HTTPException: If token format is invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required"
        )
    
    # Check for Bearer prefix if expected
    if token_type == "Bearer":
        if not token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format. Expected: Bearer <token>"
            )
        token = token[7:]  # Remove "Bearer " prefix
    
    # Basic JWT format validation (three parts separated by dots)
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    # Check each part is not empty
    if not all(parts):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token"
        )
    
    return token


def validate_password_reset_token(token: str) -> str:
    """
    Validate password reset token format
    
    Args:
        token: Reset token to validate
    
    Returns:
        Validated token
    
    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token is required"
        )
    
    # Check token length (should be a reasonable length for a secure token)
    if len(token) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check for valid characters (alphanumeric and some special chars)
    if not re.match(r'^[a-zA-Z0-9_-]+$', token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token format"
        )
    
    return token


def validate_oauth_provider(provider: str) -> str:
    """
    Validate OAuth provider
    
    Args:
        provider: OAuth provider name
    
    Returns:
        Validated provider name
    
    Raises:
        HTTPException: If provider is invalid
    """
    valid_providers = ['google', 'github', 'facebook', 'twitter', 'microsoft']
    
    if not provider or provider.lower() not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OAuth provider. Supported: {', '.join(valid_providers)}"
        )
    
    return provider.lower()


def validate_two_factor_code(code: str) -> str:
    """
    Validate two-factor authentication code
    
    Args:
        code: 2FA code to validate
    
    Returns:
        Validated code
    
    Raises:
        HTTPException: If code is invalid
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA code is required"
        )
    
    # Remove spaces and hyphens
    code = code.replace(' ', '').replace('-', '')
    
    # Check if it's a 6-digit code
    if not code.isdigit() or len(code) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code. Must be 6 digits"
        )
    
    return code


def validate_session_duration(
    remember_me: bool = False,
    max_duration_days: int = 30
) -> timedelta:
    """
    Validate and calculate session duration
    
    Args:
        remember_me: Whether to extend session duration
        max_duration_days: Maximum allowed session duration
    
    Returns:
        Session duration as timedelta
    """
    if remember_me:
        # Extended session for "remember me"
        return timedelta(days=max_duration_days)
    else:
        # Default session duration
        return timedelta(hours=24)


def validate_refresh_token(refresh_token: str) -> str:
    """
    Validate refresh token format
    
    Args:
        refresh_token: Refresh token to validate
    
    Returns:
        Validated refresh token
    
    Raises:
        HTTPException: If refresh token is invalid
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required"
        )
    
    # Basic validation - check it looks like a token
    if len(refresh_token) < 20:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return refresh_token