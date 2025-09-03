"""Standardized API response helpers."""
from datetime import datetime
from typing import Any, Dict, Optional

def create_standardized_response(data: Any) -> Dict[str, Any]:
    """Create API response envelope with metadata and no errors."""
    return {
        "data": data,
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": "placeholder",
        },
        "errors": [],
    }

def create_error_response(
    code: str,
    message: str,
    field: Optional[str] = None,
    details: Optional[str] = None,
) -> Dict[str, Any]:
    """Create standardized error response envelope."""
    return {
        "data": None,
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": "placeholder",
        },
        "errors": [
            {
                "code": code,
                "message": message,
                "field": field,
                "details": details,
            }
        ],
    }
