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
import json
from datetime import datetime
from typing import Dict, Any

# Import database models
from models import db_manager, Session, Submission, Evaluation

# Import services
from services import (
    config_service, 
    get_auth_service,
    get_config_manager,
    read_config_file,
    write_config_file
)

# Import new enhanced LLM service
from services.llm_service import EnhancedLLMService

# Import authentication decorators
from decorators import require_auth

# Import centralized logging configuration
from logging_config import configure_logging, get_logger, get_recent_logs

# Configure logging centrally with default level
# Will be updated during startup based on deployment config
configure_logging()
logger = get_logger(__name__)

# Function to update logging level based on config
def update_logging_level():
    """Update logging level based on configuration"""
    try:
        # Get deployment config to check environment settings
        deployment_config = config_service.get_deployment_config()
        if deployment_config:
            env_settings = deployment_config.get('environment', {}).get('env_specific_settings', {})
            app_env = os.environ.get('APP_ENV', 'production')
            env_config = env_settings.get(app_env, {})

            log_level_str = env_config.get('log_level', 'INFO')

            # Use centralized logging configuration to update level
            from logging_config import set_log_level
            set_log_level(log_level_str)
            logger.info(f"Updated logging level to {log_level_str} for {app_env} environment")
            
            # Also log the environment configuration details for debugging
            logger.info(f"Environment: {app_env}, Log Level: {log_level_str}")
            logger.debug(f"Full environment config: {env_config}")
        else:
            logger.warning("No deployment configuration found, using default log level")
    except Exception as e:
        logger.error(f"Failed to update logging level: {e}")
        # Fallback to default level
        try:
            from logging_config import set_log_level
            set_log_level('INFO')
            logger.info("Set fallback log level to INFO")
        except Exception as fallback_error:
            logger.error(f"Failed to set fallback log level: {fallback_error}")

# Import centralized response helpers
from utils.responses import create_standardized_response, create_error_response

# Import health router
from routes.health import router as health_router

# Create FastAPI app
app = FastAPI(
    title="Memo AI Coach API",
    description="REST API for intelligent text evaluation and feedback",
    version="1.0.0"
)

# Debug environment variables at module import time
print(f"MODULE DEBUG: DOMAIN={os.environ.get('DOMAIN', 'NOT_SET')}, APP_ENV={os.environ.get('APP_ENV', 'NOT_SET')}")

# Load configurations on startup
@app.on_event("startup")
async def startup_event():
    """Load configurations on application startup"""
    try:
        logger.info("Loading configurations on startup...")
        config_service.load_all_configs()
        update_logging_level()
        logger.info("Configurations loaded successfully on startup")
    except Exception as e:
        logger.error(f"Failed to load configurations on startup: {e}")
        raise

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include health router
app.include_router(health_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Memo AI Coach API",
        "version": "1.0.0",
        "status": "running"
    }

# Health endpoints moved to dedicated router

# Detailed health endpoint moved to dedicated router

# Database health endpoint moved to dedicated router

# Configuration health endpoint moved to dedicated router

# LLM health endpoint moved to dedicated router

# Authentication health endpoint moved to dedicated router


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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
        if valid:
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

@app.get("/api/v1/admin/logs")
async def get_admin_logs(request: Request):
    """Return recent application logs (admin-only).

    Query params:
      - limit: int (1..1000), default 200
      - level: optional level filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)
      - since: optional ISO timestamp (UTC), e.g. 2025-01-01T00:00:00Z
    """
    try:
        session_token = request.headers.get("X-Session-Token", "")
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": "placeholder"},
                    "errors": [{
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "field": "session_token",
                        "details": "Please provide valid session token"
                    }]
                }
            )

        # Validate session and admin rights
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "data": None,
                    "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": "placeholder"},
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
                    "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": "placeholder"},
                    "errors": [{
                        "code": "PERMISSION_ERROR",
                        "message": "Admin access required",
                        "field": "session_token",
                        "details": "This endpoint requires administrator privileges"
                    }]
                }
            )

        # Parse query params
        qp = request.query_params
        try:
            limit = int(qp.get('limit', '200'))
        except ValueError:
            limit = 200
        limit = max(1, min(limit, 1000))
        level = qp.get('level')
        since = qp.get('since')

        # Fetch recent logs from in-memory buffer
        logs = get_recent_logs(limit=limit, level=level, since=since)

        return {
            "data": {"logs": logs},
            "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": "placeholder"},
            "errors": []
        }

    except Exception as e:
        logger.error(f"Get admin logs failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": "placeholder"},
                "errors": [{
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve logs",
                    "field": None,
                    "details": "An internal error occurred while retrieving logs"
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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
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
        auth_service = get_auth_service(config_service=config_service)
        success, user_id, error = auth_service.create_user(username, password)
        
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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
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
        users = auth_service.list_users()
        
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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
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
        success = auth_service.delete_user(username)
        
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
        
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
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
        
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
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
        auth_service = get_auth_service(config_service=config_service)
        success, session_token, error = auth_service.authenticate(username, password)
        
        if success:
            # Get user info to return admin status
            valid, session_data, _ = auth_service.validate_session(session_token)
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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
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
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
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
        
        # Create submission record
        submission = Submission.create(text_content, session_data['session_id'])
        
        # Use enhanced LLM service for text evaluation
        try:
            llm_service = EnhancedLLMService()
            evaluation_result = llm_service.evaluate_text_with_llm(text_content)
        except Exception as e:
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
                        "details": str(e)
                    }]
                }
            )
        
        # Create evaluation record with raw data and language detection metadata
        evaluation = Evaluation.create(
            submission_id=submission.id,
            overall_score=evaluation_result['overall_score'],
            strengths=json.dumps(evaluation_result['strengths']),
            opportunities=json.dumps(evaluation_result['opportunities']),
            rubric_scores=json.dumps(evaluation_result['rubric_scores']),
            segment_feedback=json.dumps(evaluation_result['segment_feedback']),
            llm_provider='claude',
            llm_model=evaluation_result.get('metadata', {}).get('llm_model', 'claude-3-haiku-20240307'),
            raw_prompt=evaluation_result.get('metadata', {}).get('raw_prompt', ''),
            raw_response=evaluation_result.get('metadata', {}).get('raw_response', ''),
            debug_enabled=True,  # Enable debug mode
            processing_time=evaluation_result.get('metadata', {}).get('processing_time', 0)
        )
        
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

@app.get("/api/v1/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    domain = os.environ.get('DOMAIN', 'NOT_SET')
    app_env = os.environ.get('APP_ENV', 'NOT_SET')
    print(f"DEBUG ENV: DOMAIN={domain}, APP_ENV={app_env}")
    return {
        "data": {
            "DOMAIN": domain,
            "APP_ENV": app_env,
            "all_env": {k: v for k, v in os.environ.items() if 'DOMAIN' in k or 'APP' in k}
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": "debug"
        },
        "errors": []
    }

@app.get("/api/v1/config/frontend")
async def get_frontend_config():
    """Get frontend-specific configuration"""
    try:
        # Force reload configurations to ensure DOMAIN override is applied
        logger.info("Reloading configurations for frontend config request...")
        config_service.reload_configs()
        
        # Get deployment configuration
        deployment_config = config_service.get_deployment_config()
        
        if not deployment_config:
            return JSONResponse(
                status_code=500,
                content={
                    "data": None,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": "placeholder"
                    },
                    "errors": [{
                        "code": "CONFIG_ERROR",
                        "message": "Deployment configuration not found",
                        "field": None,
                        "details": "Frontend configuration could not be loaded"
                    }]
                }
            )
        
        frontend_config = deployment_config.get('frontend', {})
        
        # Get DOMAIN from environment variable with localhost as fallback
        domain = os.environ.get('DOMAIN', 'localhost')
        backend_url = f"https://{domain}"
        print(f"DEBUG: Frontend config API called - DOMAIN: {domain}, backend_url: {backend_url}")
        logger.info(f"Frontend config API called - DOMAIN: {domain}, backend_url: {backend_url}")
        
        return {
            "data": {
                "backend_url": backend_url,
                "session_warning_threshold": frontend_config.get('session_warning_threshold', 10),
                "session_refresh_interval": frontend_config.get('session_refresh_interval', 60),
                "debug_console_log_limit": frontend_config.get('debug_console_log_limit', 50),
                "llm_timeout_expectation": frontend_config.get('llm_timeout_expectation', 15),
                "default_response_time": frontend_config.get('default_response_time', 1000)
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": "placeholder"
            },
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"Frontend configuration retrieval failed: {e}")
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
                    "message": "Frontend configuration retrieval failed",
                    "field": None,
                    "details": "An internal error occurred while retrieving frontend configuration"
                }]
            }
        )

@app.get("/api/v1/admin/last-evaluations")
async def get_last_evaluations(request: Request):
    """Get last evaluation for each user (admin only)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    "AUTHENTICATION_ERROR",
                    "Authentication required",
                    "session_token",
                    "Please log in to access admin functions"
                )
            )
        
        # Validate session and check admin status
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    "AUTHENTICATION_ERROR",
                    "Invalid session",
                    "session_token",
                    error or "Please log in again"
                )
            )
        
        if not session_data.get('is_admin', False):
            return JSONResponse(
                status_code=403,
                content=create_error_response(
                    "AUTHORIZATION_ERROR",
                    "Admin access required",
                    None,
                    "This endpoint requires administrator privileges"
                )
            )
        
        # Get last evaluation for each user
        query = """
            SELECT 
                e.id, e.submission_id, e.overall_score, e.processing_time,
                e.created_at, e.llm_provider, e.llm_model, e.debug_enabled,
                e.raw_prompt, e.raw_response,
                s.text_content as submission_content,
                u.username, u.is_admin
            FROM evaluations e
            JOIN submissions s ON e.submission_id = s.id
            JOIN sessions sess ON s.session_id = sess.session_id
            JOIN users u ON sess.user_id = u.id
            WHERE e.id IN (
                SELECT MAX(e2.id) FROM evaluations e2
                JOIN submissions s2 ON e2.submission_id = s2.id
                JOIN sessions sess2 ON s2.session_id = sess2.session_id
                GROUP BY sess2.user_id
            )
            ORDER BY e.created_at DESC
            LIMIT 50
        """
        
        result = db_manager.execute_query(query)
        
        evaluations = []
        for row in result:
            evaluations.append({
                "id": row['id'],
                "submission_id": row['submission_id'],
                "overall_score": row['overall_score'],
                "processing_time": row['processing_time'],
                "created_at": row['created_at'],
                "llm_provider": row['llm_provider'],
                "llm_model": row['llm_model'],
                "debug_enabled": bool(row['debug_enabled']),
                # Consider raw data available if either prompt or response exists
                "has_raw_data": bool(row['raw_prompt'] or row['raw_response']),
                "submission_preview": row['submission_content'][:100] + "..." if len(row['submission_content']) > 100 else row['submission_content'],
                "username": row['username'],
                "is_admin": bool(row['is_admin'])
            })
        
        return {
            "data": {
                "evaluations": evaluations,
                "total": len(evaluations)
            },
            "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": str(secrets.token_urlsafe(16))},
            "errors": []
        }
    except Exception as e:
        logger.error(f"Failed to get last evaluations: {e}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                "INTERNAL_ERROR",
                "Failed to retrieve evaluations",
                None,
                "An internal error occurred while retrieving evaluation data"
            )
        )

@app.get("/api/v1/admin/evaluation/{evaluation_id}/raw")
async def get_evaluation_raw_data(evaluation_id: int, request: Request):
    """Get raw data for specific evaluation (admin only)"""
    try:
        # Get session token from header
        session_token = request.headers.get("X-Session-Token", "")
        
        if not session_token:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    "AUTHENTICATION_ERROR",
                    "Authentication required",
                    "session_token",
                    "Please log in to access admin functions"
                )
            )
        
        # Validate session and check admin status
        auth_service = get_auth_service(config_service=config_service)
        valid, session_data, error = auth_service.validate_session(session_token)
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    "AUTHENTICATION_ERROR",
                    "Invalid session",
                    "session_token",
                    error or "Please log in again"
                )
            )
        
        if not session_data.get('is_admin', False):
            return JSONResponse(
                status_code=403,
                content=create_error_response(
                    "AUTHORIZATION_ERROR",
                    "Admin access required",
                    None,
                    "This endpoint requires administrator privileges"
                )
            )
        
        # Get evaluation by ID
        evaluation = Evaluation.get_by_id(evaluation_id)
        if not evaluation:
            return JSONResponse(
                status_code=404,
                content=create_error_response(
                    "NOT_FOUND",
                    "Evaluation not found",
                    "evaluation_id",
                    f"Evaluation with ID {evaluation_id} does not exist"
                )
            )
        
        # Get submission data
        submission = Submission.get_by_id(evaluation.submission_id)
        
        return {
            "data": {
                "evaluation": {
                    "id": evaluation.id,
                    "submission_id": evaluation.submission_id,
                    "overall_score": evaluation.overall_score,
                    "processing_time": evaluation.processing_time,
                    "created_at": evaluation.created_at.isoformat(),
                    "llm_provider": evaluation.llm_provider,
                    "llm_model": evaluation.llm_model,
                    "debug_enabled": evaluation.debug_enabled,
                    "raw_prompt": evaluation.raw_prompt,
                    "raw_response": evaluation.raw_response,
                    "submission": {
                        "id": submission.id if submission else None,
                        "content": submission.text_content if submission else "",
                        "created_at": submission.created_at.isoformat() if submission else None
                    }
                }
            },
            "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": str(secrets.token_urlsafe(16))},
            "errors": []
        }
    except Exception as e:
        logger.error(f"Failed to get evaluation raw data: {e}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                "INTERNAL_ERROR",
                "Failed to retrieve evaluation raw data",
                None,
                "An internal error occurred while retrieving evaluation raw data"
            )
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
