"""
Memo AI Coach - Backend Application
FastAPI-based REST API for text evaluation
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import secrets
from datetime import datetime
from typing import Dict, Any

# Import database models
from models import db_manager, Session, Submission, Evaluation

# Import services
from services import (
    config_service, 
    get_llm_service, 
    evaluate_text_with_llm,
    get_auth_service,
    authenticate,
    validate_session,
    logout,
    get_config_manager,
    read_config_file,
    write_config_file,
    create_user,
    list_users,
    delete_user
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Memo AI Coach API",
    description="REST API for intelligent text evaluation and feedback",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Memo AI Coach API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database health
        db_health = db_manager.health_check()
        
        # Check configuration health
        config_health = config_service.health_check()
        
        # Check LLM health
        try:
            llm_service = get_llm_service()
            llm_health = llm_service.health_check()
            llm_status = llm_health["status"]
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            llm_status = "unhealthy"
        
        # Check authentication health
        try:
            auth_service = get_auth_service()
            auth_health = auth_service.health_check()
            auth_status = auth_health["status"]
        except Exception as e:
            logger.error(f"Auth health check failed: {e}")
            auth_status = "unhealthy"
        
        # Basic health check
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": "healthy",
                "database": db_health["status"],
                "configuration": config_health["status"],
                "llm": llm_status,
                "auth": auth_status
            }
        }
        
        # Add database details if available
        if db_health["status"] == "healthy":
            health_status["database_details"] = {
                "tables": db_health.get("tables", []),
                "journal_mode": db_health.get("journal_mode", ""),
                "user_count": db_health.get("user_count", 0)
            }
        else:
            health_status["database_error"] = db_health.get("error", "Unknown error")
        
        # Add configuration details if available
        if config_health["status"] == "healthy":
            health_status["config_details"] = {
                "configs_loaded": config_health.get("configs_loaded", []),
                "last_loaded": config_health.get("last_loaded", ""),
                "config_dir": config_health.get("config_dir", "")
            }
        else:
            health_status["config_error"] = config_health.get("error", "Unknown error")
        
        # Add LLM details if available
        if llm_status == "healthy":
            health_status["llm_details"] = {
                "provider": llm_health.get("provider", ""),
                "model": llm_health.get("model", ""),
                "api_accessible": llm_health.get("api_accessible", False),
                "config_loaded": llm_health.get("config_loaded", False)
            }
        else:
            health_status["llm_error"] = llm_health.get("error", "Unknown error")
        
        # Add authentication details if available
        if auth_status == "healthy":
            health_status["auth_details"] = {
                "config_loaded": auth_health.get("config_loaded", False),
                "active_sessions": auth_health.get("active_sessions", 0),
                "brute_force_protection": auth_health.get("brute_force_protection", False)
            }
        else:
            health_status["auth_error"] = auth_health.get("error", "Unknown error")
        
        # Check if any service is unhealthy
        if any(status != "healthy" for status in health_status["services"].values()):
            health_status["status"] = "unhealthy"
            return JSONResponse(status_code=503, content=health_status)
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/health/database")
async def database_health_check():
    """Database-specific health check endpoint"""
    try:
        db_health = db_manager.health_check()
        return {
            "status": db_health["status"],
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_health
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/health/config")
async def config_health_check():
    """Configuration-specific health check endpoint"""
    try:
        config_health = config_service.health_check()
        return {
            "status": config_health["status"],
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": config_health
        }
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/health/llm")
async def llm_health_check():
    """LLM service health check endpoint"""
    try:
        llm_service = get_llm_service()
        llm_health = llm_service.health_check()
        
        if llm_health["status"] == "healthy":
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "llm": llm_health
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "llm": llm_health
                }
            )
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/health/auth")
async def auth_health_check():
    """Authentication service health check endpoint"""
    try:
        auth_service = get_auth_service()
        auth_health = auth_service.health_check()
        
        if auth_health["status"] == "healthy":
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "auth": auth_health
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "auth": auth_health
                }
            )
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@app.post("/api/v1/auth/logout")
async def auth_logout(request: Request):
    """Unified logout endpoint for all users"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Session token is required",
                        "field": "session_token",
                        "details": "Please provide session token in X-Session-Token header"
                    }]
                }
            )
        
        # Validate session and logout
        valid, session_data, error = validate_session(session_token)
        
        if valid:
            auth_service = get_auth_service()
            logout_success = auth_service.logout(session_token)
            
            if logout_success:
                return {
                    "data": {
                        "message": "Logout successful"
                    },
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": []
                }
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "data": None,
                        "meta": {
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": "placeholder"
                        },
                        "errors": [{
                            "code": "LOGOUT_ERROR",
                            "message": "Logout failed",
                            "field": None,
                            "details": "Failed to terminate session"
                        }]
                    }
                )
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
            
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Logout processing failed",
                    "field": None,
                    "details": "An internal error occurred during logout processing"
                }]
            }
        )

@app.post("/api/v1/admin/users/create")
async def create_user_endpoint(request: Request):
    """Create new user account (admin-only)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Session token is required",
                        "field": "session_token",
                        "details": "Please provide session token in X-Session-Token header"
                    }]
                }
            )
        
        # Validate session and check admin access
        valid, session_data, error = validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
            
        if not session_data.get('is_admin', False):
            return JSONResponse(
                status_code=403,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "PERMISSION_ERROR",
                        "message": "Admin access required",
                        "field": "session_token",
                        "details": "This endpoint requires administrator privileges"
                    }]
                }
            )
        
        # Parse request body
        body = await request.json()
        username = body.get("username", "")
        password = body.get("password", "")
        
        # Validate input
        if not username or not password:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Username and password are required",
                        "field": "credentials",
                        "details": "Please provide both username and password"
                    }]
                }
            )
        
        # Create user
        success, user_id, error = create_user(username, password)
        
        if success:
            return {
                "data": {
                    "user_id": user_id,
                    "username": username,
                    "message": "User created successfully"
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": []
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "USER_CREATION_ERROR",
                        "message": "User creation failed",
                        "field": "credentials",
                        "details": error
                    }]
                }
            )
            
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "User creation processing failed",
                    "field": None,
                    "details": "An internal error occurred during user creation"
                }]
            }
        )

@app.get("/api/v1/admin/users")
async def list_users_endpoint(request: Request):
    """List all users (admin-only)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Session token is required",
                        "field": "session_token",
                        "details": "Please provide session token in X-Session-Token header"
                    }]
                }
            )
        
        # Validate session and check admin access
        valid, session_data, error = validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
            
        if not session_data.get('is_admin', False):
            return JSONResponse(
                status_code=403,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "PERMISSION_ERROR",
                        "message": "Admin access required",
                        "field": "session_token",
                        "details": "This endpoint requires administrator privileges"
                    }]
                }
            )
        
        # Get users list
        users = list_users()
        
        return {
            "data": {
                "users": users,
                "total_users": len(users)
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": "placeholder"
            },
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"User listing failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "User listing processing failed",
                    "field": None,
                    "details": "An internal error occurred during user listing"
                }]
            }
        )

@app.delete("/api/v1/admin/users/{username}")
async def delete_user_endpoint(username: str, request: Request):
    """Delete user account (admin-only)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Session token is required",
                        "field": "session_token",
                        "details": "Please provide session token in X-Session-Token header"
                    }]
                }
            )
        
        # Validate session and check admin access
        valid, session_data, error = validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
            
        if not session_data.get('is_admin', False):
            return JSONResponse(
                status_code=403,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "PERMISSION_ERROR",
                        "message": "Admin access required",
                        "field": "session_token",
                        "details": "This endpoint requires administrator privileges"
                    }]
                }
            )
        
        # Delete user
        success = delete_user(username)
        
        if success:
            return {
                "data": {
                    "username": username,
                    "message": "User deleted successfully"
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": []
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "USER_NOT_FOUND",
                        "message": "User not found",
                        "field": "username",
                        "details": f"User '{username}' does not exist"
                    }]
                }
            )
        
    except Exception as e:
        logger.error(f"User deletion failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "User deletion processing failed",
                    "field": None,
                    "details": "An internal error occurred during user deletion"
                }]
            }
        )

@app.get("/api/v1/admin/config/{config_name}")
async def get_config(config_name: str, request: Request):
    """Get configuration file content"""
    try:
        # Validate admin session
        session_token = request.headers.get("X-Session-Token", "")
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "field": "session_token",
                        "details": "Please provide valid session token"
                    }]
                }
            )
        
        valid, session_data, error = validate_session(session_token)
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
        
        # Read configuration file
        success, content, error = read_config_file(config_name)
        
        if success:
            return {
                "data": {
                    "config_name": config_name,
                    "content": content
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": []
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "CONFIG_ERROR",
                        "message": "Configuration not found",
                        "field": "config_name",
                        "details": error
                    }]
                }
            )
            
    except Exception as e:
        logger.error(f"Get config failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Configuration retrieval failed",
                    "field": None,
                    "details": "An internal error occurred during configuration retrieval"
                }]
            }
        )

@app.put("/api/v1/admin/config/{config_name}")
async def update_config(config_name: str, request: Request):
    """Update configuration file content"""
    try:
        # Validate admin session
        session_token = request.headers.get("X-Session-Token", "")
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "field": "session_token",
                        "details": "Please provide valid session token"
                    }]
                }
            )
        
        valid, session_data, error = validate_session(session_token)
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
        
        # Get new configuration content
        body = await request.json()
        content = body.get("content", "")
        
        if not content:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Configuration content is required",
                        "field": "content",
                        "details": "Please provide configuration content"
                    }]
                }
            )
        
        # Update configuration file
        success, error = write_config_file(config_name, content)
        
        if success:
            return {
                "data": {
                    "config_name": config_name,
                    "message": "Configuration updated successfully"
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": []
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "CONFIG_ERROR",
                        "message": "Configuration update failed",
                        "field": "content",
                        "details": error
                    }]
                }
            )
            
    except Exception as e:
        logger.error(f"Update config failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Configuration update failed",
                    "field": None,
                    "details": "An internal error occurred during configuration update"
                }]
            }
        )

@app.get("/api/v1/auth/validate")
async def auth_validate(request: Request):
    """Validate session token and return user info"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Session token is required",
                        "field": "session_token",
                        "details": "Please provide session token in X-Session-Token header"
                    }]
                }
            )
        
        # Validate session
        valid, session_data, error = validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error
                    }]
                }
            )
        
        return {
            "data": {
                "session_id": session_data['session_id'],
                "user_id": session_data['user_id'],
                "username": session_data['username'],
                "is_admin": session_data['is_admin'],
                "permissions": session_data['permissions'],
                "expires_at": session_data['expires_at'].isoformat(),
                "created_at": session_data['created_at'].isoformat()
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": session_data['session_id'][:8]
            },
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"Session validation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Session validation failed",
                    "field": None,
                    "details": "An internal error occurred during session validation"
                }]
            }
        )

@app.post("/api/v1/auth/login")
async def auth_login(request: Request):
    """Unified login endpoint for all users"""
    try:
        # Parse request body
        body = await request.json()
        username = body.get("username", "")
        password = body.get("password", "")
        
        # Validate input
        if not username or not password:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Username and password are required",
                        "field": "credentials",
                        "details": "Please provide both username and password"
                    }]
                }
            )
        
        # Authenticate user with unified auth
        success, session_token, error = authenticate(username, password)
        
        if success:
            # Get user info to return admin status
            valid, session_data, _ = validate_session(session_token)
            if valid:
                return {
                    "data": {
                        "session_token": session_token,
                        "username": session_data.get('username'),
                        "is_admin": session_data.get('is_admin', False),
                        "user_id": session_data.get('user_id')
                    },
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": []
                }
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "data": None,
                        "meta": {
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": "placeholder"
                        },
                        "errors": [{
                            "code": "SESSION_ERROR",
                            "message": "Failed to validate new session",
                            "field": None,
                            "details": "Session validation failed after successful authentication"
                        }]
                    }
                )
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication failed",
                        "field": "credentials",
                        "details": error
                    }]
                }
            )
            
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Login processing failed",
                    "field": None,
                    "details": "An internal error occurred during login processing"
                }]
            }
        )

@app.post("/api/v1/sessions/create")
async def create_session(request: Request):
    """Create authenticated session for user (requires login first)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "field": "session_token",
                        "details": "Please log in first to create a session"
                    }]
                }
            )
        
        # Validate session with unified auth
        valid, session_data, error = validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error or "Please log in again"
                    }]
                }
            )
        
        # Return session info
        return {
            "data": {
                "session_id": session_data['session_id'],
                "user_id": session_data['user_id'],
                "username": session_data['username'],
                "is_admin": session_data['is_admin'],
                "expires_at": session_data['expires_at'].isoformat(),
                "created_at": session_data['created_at'].isoformat()
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": session_data['session_id'][:8]
            },
            "errors": []
        }
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Session creation failed",
                    "field": None,
                    "details": "An internal error occurred during session creation"
                }]
            }
        )

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session by ID"""
    try:
        session = Session.get_by_session_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "data": {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "is_admin": session.is_admin,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "is_active": session.is_active
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": session_id[:8]
            },
            "errors": []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

@app.post("/api/v1/evaluations/submit")
async def submit_evaluation(request: Request):
    """Submit text for evaluation (authenticated users only)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "field": "session_token",
                        "details": "Please log in to submit evaluations"
                    }]
                }
            )
        
        # Validate session
        valid, session_data, error = validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid session",
                        "field": "session_token",
                        "details": error or "Please log in again"
                    }]
                }
            )
        
        # Parse request body
        body = await request.json()
        text_content = body.get("text_content", "")
        
        # Validate input
        if not text_content or len(text_content.strip()) == 0:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Text content is required",
                        "field": "text_content",
                        "details": "Please provide text content for evaluation"
                    }]
                }
            )
        
        if len(text_content) > 10000:
            return JSONResponse(
                status_code=400,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "VALIDATION_ERROR",
                        "message": "Text content too long",
                        "field": "text_content",
                        "details": "Text content exceeds maximum length of 10,000 characters"
                    }]
                }
            )
        
        # Use LLM service for text evaluation
        success, evaluation_result, error = evaluate_text_with_llm(text_content)
        
        if not success:
            return JSONResponse(
                status_code=500,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "LLM_ERROR",
                        "message": "Evaluation processing failed",
                        "field": None,
                        "details": error
                    }]
                }
            )
        
        # Session data already contains user association
        
        return {
            "data": {
                "evaluation": evaluation_result,
                "user_id": session_data['user_id'],
                "username": session_data['username'],
                "is_admin": session_data['is_admin']
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": "placeholder"
            },
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"Evaluation submission failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": "placeholder"
                },
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Evaluation processing failed",
                    "field": None,
                    "details": "An internal error occurred during evaluation processing"
                }]
            }
        )

@app.get("/api/v1/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    """Get evaluation results by ID"""
    try:
        # Placeholder implementation
        return {
            "data": {
                "evaluation": {
                    "id": evaluation_id,
                    "overall_score": 3.5,
                    "strengths": "Sample strengths",
                    "opportunities": "Sample opportunities",
                    "rubric_scores": {},
                    "segment_feedback": [],
                    "created_at": datetime.utcnow().isoformat()
                }
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": "placeholder"
            },
            "errors": []
        }
    except Exception as e:
        logger.error(f"Evaluation retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve evaluation")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

