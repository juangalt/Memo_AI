"""
Authentication decorators for securing endpoints
"""

import functools
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from services.auth_service import validate_session
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

def require_auth(admin_only: bool = False):
    """
    Decorator to require authentication for endpoints
    
    Args:
        admin_only: If True, only admin users can access the endpoint
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            # Extract session token from header
            session_token = request.headers.get("X-Session-Token", "")
            
            if not session_token:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "field": "session_token",
                        "details": "Please log in to access this endpoint"
                    }
                )
            
            # Validate session
            valid, session_data, error = validate_session(session_token)
            
            if not valid:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error or "Please log in again"
                    }
                )
            
            # Check admin requirement if needed
            if admin_only and not session_data.get('is_admin', False):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "AUTHORIZATION_ERROR",
                        "message": "Admin access required",
                        "field": None,
                        "details": "This endpoint requires administrator privileges"
                    }
                )
            
            # Add session data to request state for use in the function
            request.state.session_data = session_data
            
            return await func(*args, request=request, **kwargs)
        
        return wrapper
    return decorator

# Import centralized response helpers
from utils.responses import create_error_response
