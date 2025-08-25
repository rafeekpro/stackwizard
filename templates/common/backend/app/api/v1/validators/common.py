"""
Common Validators
Shared validation utilities used across multiple endpoints
"""
import re
from typing import Optional, Tuple, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status


def validate_uuid(value: str, field_name: str = "id") -> UUID:
    """
    Validate UUID format
    
    Args:
        value: String to validate as UUID
        field_name: Name of the field for error messages
    
    Returns:
        Valid UUID object
    
    Raises:
        HTTPException: If value is not a valid UUID
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}: '{value}' is not a valid UUID"
        )


def validate_email(email: str) -> str:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        Validated email in lowercase
    
    Raises:
        HTTPException: If email format is invalid
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Additional checks
    if len(email) > 254:  # RFC 5321
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address too long (max 254 characters)"
        )
    
    return email.lower().strip()


def validate_pagination(
    skip: int = 0,
    limit: int = 100,
    max_limit: int = 1000
) -> Tuple[int, int]:
    """
    Validate pagination parameters
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        max_limit: Maximum allowed limit
    
    Returns:
        Tuple of (skip, limit) with validated values
    
    Raises:
        HTTPException: If pagination params are invalid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip value must be non-negative"
        )
    
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be at least 1"
        )
    
    if limit > max_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit exceeds maximum of {max_limit}"
        )
    
    return skip, limit


def validate_sort_params(
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    allowed_fields: Optional[list] = None
) -> Tuple[Optional[str], str]:
    """
    Validate sorting parameters
    
    Args:
        sort_by: Field to sort by
        order: Sort order (asc/desc)
        allowed_fields: List of allowed sort fields
    
    Returns:
        Tuple of (sort_by, order) with validated values
    
    Raises:
        HTTPException: If sort params are invalid
    """
    if order and order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be 'asc' or 'desc'"
        )
    
    if sort_by and allowed_fields and sort_by not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field. Allowed: {', '.join(allowed_fields)}"
        )
    
    return sort_by, order.lower() if order else "asc"


def sanitize_string(
    value: str,
    max_length: int = 255,
    min_length: int = 0,
    field_name: str = "field",
    allow_empty: bool = False,
    strip_html: bool = True
) -> str:
    """
    Sanitize and validate string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        min_length: Minimum required length
        field_name: Name of the field for error messages
        allow_empty: Whether to allow empty strings
        strip_html: Whether to strip HTML tags
    
    Returns:
        Sanitized string
    
    Raises:
        HTTPException: If string validation fails
    """
    if value is None:
        if allow_empty:
            return ""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} is required"
        )
    
    # Strip whitespace
    value = value.strip()
    
    # Check empty
    if not value and not allow_empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot be empty"
        )
    
    # Strip HTML tags if requested
    if strip_html:
        import html
        value = re.sub(r'<[^>]+>', '', value)
        value = html.unescape(value)
    
    # Check length
    if len(value) < min_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be at least {min_length} characters"
        )
    
    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must not exceed {max_length} characters"
        )
    
    return value


def validate_phone_number(phone: Optional[str]) -> Optional[str]:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
    
    Returns:
        Validated phone number or None
    
    Raises:
        HTTPException: If phone format is invalid
    """
    if not phone:
        return None
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    
    # Check if it's all digits
    if not cleaned.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must contain only digits"
        )
    
    # Check length (international numbers can be 7-15 digits)
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number length"
        )
    
    return cleaned


def validate_url(url: str, field_name: str = "URL") -> str:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        field_name: Name of the field for error messages
    
    Returns:
        Validated URL
    
    Raises:
        HTTPException: If URL format is invalid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if not url or not url_pattern.match(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format"
        )
    
    return url


def validate_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Validate date range
    
    Args:
        start_date: Start date string
        end_date: End date string
    
    Returns:
        Tuple of (start_date, end_date) validated
    
    Raises:
        HTTPException: If date range is invalid
    """
    from datetime import datetime
    
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            
            if start > end:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start date must be before end date"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
            )
    
    return start_date, end_date