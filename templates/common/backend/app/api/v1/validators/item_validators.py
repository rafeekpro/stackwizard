"""
Item Validators
Validation utilities for item operations
"""
from typing import Dict, Optional
from fastapi import HTTPException, status


def validate_item_title(title: str) -> str:
    """
    Validate item title
    
    Args:
        title: Item title to validate
    
    Returns:
        Validated title
    
    Raises:
        HTTPException: If title is invalid
    """
    from .common import sanitize_string
    
    return sanitize_string(
        title,
        max_length=200,
        min_length=3,
        field_name="Title"
    )


def validate_item_description(description: Optional[str]) -> Optional[str]:
    """
    Validate item description
    
    Args:
        description: Item description to validate
    
    Returns:
        Validated description or None
    
    Raises:
        HTTPException: If description is invalid
    """
    if not description:
        return None
    
    from .common import sanitize_string
    
    return sanitize_string(
        description,
        max_length=2000,
        field_name="Description",
        allow_empty=True
    )


def validate_item_price(price: Optional[float]) -> Optional[float]:
    """
    Validate item price
    
    Args:
        price: Price to validate
    
    Returns:
        Validated price or None
    
    Raises:
        HTTPException: If price is invalid
    """
    if price is None:
        return None
    
    if price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative"
        )
    
    if price > 1000000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price exceeds maximum allowed value"
        )
    
    # Round to 2 decimal places
    return round(price, 2)


def validate_item_quantity(quantity: int) -> int:
    """
    Validate item quantity
    
    Args:
        quantity: Quantity to validate
    
    Returns:
        Validated quantity
    
    Raises:
        HTTPException: If quantity is invalid
    """
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity cannot be negative"
        )
    
    if quantity > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity exceeds maximum allowed value"
        )
    
    return quantity


def validate_item_category(category: str, allowed_categories: Optional[list] = None) -> str:
    """
    Validate item category
    
    Args:
        category: Category to validate
        allowed_categories: List of allowed categories
    
    Returns:
        Validated category
    
    Raises:
        HTTPException: If category is invalid
    """
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is required"
        )
    
    category = category.lower().strip()
    
    # If allowed categories are specified, check against them
    if allowed_categories:
        if category not in [cat.lower() for cat in allowed_categories]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Allowed: {', '.join(allowed_categories)}"
            )
    
    return category


def validate_item_tags(tags: Optional[list]) -> Optional[list]:
    """
    Validate item tags
    
    Args:
        tags: List of tags to validate
    
    Returns:
        Validated tags or None
    
    Raises:
        HTTPException: If tags are invalid
    """
    if not tags:
        return None
    
    if len(tags) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 tags allowed"
        )
    
    validated_tags = []
    for tag in tags:
        if not isinstance(tag, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tags must be strings"
            )
        
        tag = tag.lower().strip()
        
        if len(tag) < 2:
            continue  # Skip very short tags
        
        if len(tag) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag too long (max 30 characters)"
            )
        
        # Only alphanumeric and hyphens allowed in tags
        import re
        if not re.match(r'^[a-z0-9-]+$', tag):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tag format: {tag}"
            )
        
        if tag not in validated_tags:
            validated_tags.append(tag)
    
    return validated_tags if validated_tags else None


def validate_item_status(status: str) -> str:
    """
    Validate item status
    
    Args:
        status: Status to validate
    
    Returns:
        Validated status
    
    Raises:
        HTTPException: If status is invalid
    """
    valid_statuses = ['draft', 'published', 'archived', 'deleted']
    
    if not status or status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    return status.lower()


def validate_item_data(item_data: Dict) -> Dict:
    """
    Validate complete item data
    
    Args:
        item_data: Dictionary of item data
    
    Returns:
        Validated item data
    
    Raises:
        HTTPException: If item data is invalid
    """
    validated = {}
    
    # Required fields
    if 'title' in item_data:
        validated['title'] = validate_item_title(item_data['title'])
    
    # Optional fields
    if 'description' in item_data:
        validated['description'] = validate_item_description(item_data.get('description'))
    
    if 'price' in item_data:
        validated['price'] = validate_item_price(item_data.get('price'))
    
    if 'quantity' in item_data:
        validated['quantity'] = validate_item_quantity(item_data['quantity'])
    
    if 'category' in item_data:
        validated['category'] = validate_item_category(item_data['category'])
    
    if 'tags' in item_data:
        validated['tags'] = validate_item_tags(item_data.get('tags'))
    
    if 'status' in item_data:
        validated['status'] = validate_item_status(item_data['status'])
    
    return validated