"""
Standardized API Response Helpers
Centralized response formatting for consistent API outputs across all endpoints
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime
import uuid

def create_standardized_response(
    data: Any, 
    status_code: int = 200,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized API response with consistent structure.
    
    Args:
        data: The main response data
        status_code: HTTP status code (default: 200)
        message: Optional success message
        
    Returns:
        Dict with standardized response structure:
        {
            "data": data,
            "meta": {
                "timestamp": "ISO timestamp",
                "request_id": "unique identifier",
                "status_code": status_code
            },
            "errors": []
        }
    """
    return {
        "data": data,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4()),
            "status_code": status_code
        },
        "errors": []
    }

def create_error_response(
    code: str,
    message: str,
    field: Optional[str] = None,
    details: Optional[Any] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Create a standardized error response with consistent structure.
    
    Args:
        code: Error code identifier
        message: Human-readable error message
        field: Optional field name where error occurred
        details: Optional additional error details
        status_code: HTTP status code (default: 400)
        
    Returns:
        Dict with standardized error response structure:
        {
            "data": null,
            "meta": {
                "timestamp": "ISO timestamp",
                "request_id": "unique identifier",
                "status_code": status_code
            },
            "errors": [{
                "code": code,
                "message": message,
                "field": field,
                "details": details
            }]
        }
    """
    error = {
        "code": code,
        "message": message
    }
    
    if field is not None:
        error["field"] = field
    
    if details is not None:
        error["details"] = details
    
    return {
        "data": None,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4()),
            "status_code": status_code
        },
        "errors": [error]
    }

def create_validation_error_response(
    validation_errors: list,
    status_code: int = 422
) -> Dict[str, Any]:
    """
    Create a standardized validation error response for multiple validation failures.
    
    Args:
        validation_errors: List of validation error dictionaries
        status_code: HTTP status code (default: 422)
        
    Returns:
        Dict with standardized validation error response structure
    """
    return {
        "data": None,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4()),
            "status_code": status_code
        },
        "errors": validation_errors
    }
