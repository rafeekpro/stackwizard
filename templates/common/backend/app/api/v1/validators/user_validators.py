"""
User Validators
Validation utilities specific to user operations
"""
import re
from typing import Dict, List, Tuple, Optional
from fastapi import HTTPException, status


def validate_username(username: str) -> str:
    """
    Validate username format
    
    Args:
        username: Username to validate
    
    Returns:
        Validated username
    
    Raises:
        HTTPException: If username is invalid
    """
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is required"
        )
    
    # Length check
    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )
    
    if len(username) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must not exceed 30 characters"
        )
    
    # Format check: alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can only contain letters, numbers, underscores, and hyphens"
        )
    
    # No consecutive special characters
    if re.search(r'[_-]{2,}', username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot have consecutive special characters"
        )
    
    # Must start with letter or number
    if not re.match(r'^[a-zA-Z0-9]', username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must start with a letter or number"
        )
    
    # Check for reserved usernames
    reserved = ['admin', 'root', 'system', 'api', 'null', 'undefined']
    if username.lower() in reserved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is reserved"
        )
    
    return username.lower()


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_numbers: bool = True,
    require_special: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        require_uppercase: Require uppercase letters
        require_lowercase: Require lowercase letters
        require_numbers: Require numbers
        require_special: Require special characters
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not password:
        return False, ["Password is required"]
    
    # Length check
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters")
    
    if len(password) > 128:
        errors.append("Password must not exceed 128 characters")
    
    # Complexity checks
    if require_uppercase and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if require_lowercase and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if require_numbers and not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Common password check
    common_passwords = [
        'password', '123456', 'password123', 'admin', 'letmein',
        'qwerty', 'abc123', '111111', 'password1', 'iloveyou'
    ]
    if password.lower() in common_passwords:
        errors.append("Password is too common")
    
    # Repeated characters check
    if re.search(r'(.)\1{4,}', password):
        errors.append("Password contains too many repeated characters")
    
    # Sequential characters check
    if any(seq in password.lower() for seq in ['12345', 'abcde', 'qwerty']):
        errors.append("Password contains sequential characters")
    
    return len(errors) == 0, errors


def validate_user_update(update_data: Dict) -> Dict:
    """
    Validate user update data
    
    Args:
        update_data: Dictionary of fields to update
    
    Returns:
        Validated update data
    
    Raises:
        HTTPException: If update data is invalid
    """
    allowed_fields = {
        'email', 'username', 'full_name', 'bio', 'phone',
        'avatar_url', 'preferences', 'notification_settings'
    }
    
    # Check for unknown fields
    unknown_fields = set(update_data.keys()) - allowed_fields
    if unknown_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown fields: {', '.join(unknown_fields)}"
        )
    
    # Validate individual fields if present
    if 'email' in update_data:
        from .common import validate_email
        update_data['email'] = validate_email(update_data['email'])
    
    if 'username' in update_data:
        update_data['username'] = validate_username(update_data['username'])
    
    if 'full_name' in update_data:
        from .common import sanitize_string
        update_data['full_name'] = sanitize_string(
            update_data['full_name'],
            max_length=100,
            field_name="Full name"
        )
    
    if 'bio' in update_data:
        from .common import sanitize_string
        update_data['bio'] = sanitize_string(
            update_data.get('bio', ''),
            max_length=500,
            field_name="Bio",
            allow_empty=True
        )
    
    if 'phone' in update_data:
        from .common import validate_phone_number
        update_data['phone'] = validate_phone_number(update_data['phone'])
    
    if 'avatar_url' in update_data and update_data['avatar_url']:
        from .common import validate_url
        update_data['avatar_url'] = validate_url(
            update_data['avatar_url'],
            field_name="Avatar URL"
        )
    
    return update_data


def validate_bulk_operation(
    user_ids: List[str],
    operation: str,
    max_users: int = 100
) -> List[str]:
    """
    Validate bulk user operation
    
    Args:
        user_ids: List of user IDs
        operation: Operation to perform
        max_users: Maximum users allowed in bulk operation
    
    Returns:
        Validated list of user IDs
    
    Raises:
        HTTPException: If bulk operation is invalid
    """
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users specified for bulk operation"
        )
    
    if len(user_ids) > max_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bulk operation limited to {max_users} users"
        )
    
    # Validate each ID
    from .common import validate_uuid
    validated_ids = []
    for user_id in user_ids:
        try:
            validated_ids.append(str(validate_uuid(user_id, "User ID")))
        except HTTPException:
            # Log invalid IDs for debugging
            logging.warning(f"Invalid user ID skipped during bulk operation: {user_id}")
    
    if not validated_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid user IDs provided"
        )
    
    # Validate operation
    allowed_operations = [
        'activate', 'deactivate', 'delete', 'verify',
        'reset_password', 'send_notification'
    ]
    if operation not in allowed_operations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation. Allowed: {', '.join(allowed_operations)}"
        )
    
    return validated_ids


def validate_user_role(role: str) -> str:
    """
    Validate user role
    
    Args:
        role: Role to validate
    
    Returns:
        Validated role
    
    Raises:
        HTTPException: If role is invalid
    """
    valid_roles = ['user', 'moderator', 'admin', 'superuser']
    
    if not role or role.lower() not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    return role.lower()


def validate_user_status(status: str) -> str:
    """
    Validate user status
    
    Args:
        status: Status to validate
    
    Returns:
        Validated status
    
    Raises:
        HTTPException: If status is invalid
    """
    valid_statuses = ['active', 'inactive', 'suspended', 'pending', 'deleted']
    
    if not status or status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    return status.lower()