"""
Health Check Router
Centralized health endpoint management with shared service instances for efficiency
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import logging

try:
    # When imported from main application
    from services.config_service import ConfigService
    from services.auth_service import AuthService
    from services.llm_service import EnhancedLLMService
    from utils.responses import create_standardized_response, create_error_response
    from decorators import require_auth
except ImportError:
    # When imported from tests or other contexts
    from ..services.config_service import ConfigService
    from ..services.auth_service import AuthService
    from ..services.llm_service import EnhancedLLMService
    from ..utils.responses import create_standardized_response, create_error_response
    from ..decorators import require_auth

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/health", tags=["health"])

# Shared service instances (instantiated once)
config_service = ConfigService()
auth_service = AuthService(config_service=config_service)



def get_llm_service() -> EnhancedLLMService:
    """Get LLM service instance with error handling"""
    try:
        return EnhancedLLMService()
    except Exception as e:
        logger.error(f"Failed to instantiate LLM service: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"LLM service unavailable: {str(e)}"
        )

def check_database_health() -> Dict[str, Any]:
    """Check database health status"""
    try:
        # Import here to avoid circular imports
        try:
            from models.database import db_manager
        except ImportError:
            from ..models.database import db_manager
        return db_manager.health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Database connection or query failed"
        }

def check_config_health() -> Dict[str, Any]:
    """Check configuration service health"""
    try:
        return config_service.health_check()
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Configuration loading or validation failed"
        }

def check_llm_health() -> Dict[str, Any]:
    """Check LLM service health"""
    try:
        llm_service = get_llm_service()
        health_result = llm_service.validate_configuration()
        return {
            "status": "healthy" if health_result["valid"] else "unhealthy",
            "details": health_result.get("details", "LLM service validation completed"),
            "model": health_result.get("model", "unknown"),
            "provider": health_result.get("provider", "unknown")
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "LLM service initialization or validation failed"
        }

def check_auth_health() -> Dict[str, Any]:
    """Check authentication service health"""
    try:
        return auth_service.health_check()
    except Exception as e:
        logger.error(f"Authentication health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Authentication service initialization or validation failed"
        }

@router.get("/")
@router.get("")
async def health_check():
    """Basic health check endpoint - public access"""
    try:
        # Check database health
        db_health = check_database_health()
        
        # Check configuration health
        config_health = check_config_health()
        
        # Check LLM health
        llm_health = check_llm_health()
        
        # Check authentication health
        auth_health = check_auth_health()
        
        # Determine overall health status
        all_services = [db_health, config_health, llm_health, auth_health]
        overall_status = "healthy" if all(s.get("status") == "healthy" for s in all_services) else "unhealthy"
        
        # Basic health status (minimal information for public access)
        health_status = {
            "status": overall_status,
            "timestamp": "2024-01-01T00:00:00Z",  # Will be overridden by response helper
            "version": "1.0.0",
            "services": {
                "api": {
                    "status": "healthy",
                    "details": "API service responding normally"
                },
                "database": db_health,
                "configuration": config_health,
                "llm": llm_health,
                "auth": auth_health
            }
        }
        
        return create_standardized_response(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response(
            "HEALTH_CHECK_ERROR",
            "Health check failed",
            details=str(e),
            status_code=500
        )

@router.get("/detailed")
@router.get("/detailed/")
@require_auth(admin_only=True)
async def detailed_health_check(request: Request):
    """Detailed health check endpoint - requires admin authentication"""
    try:
        # Check database health
        db_health = check_database_health()
        
        # Check configuration health
        config_health = check_config_health()
        
        # Check LLM health
        llm_health = check_llm_health()
        
        # Check authentication health
        auth_health = check_auth_health()
        
        # Determine overall health status
        all_services = [db_health, config_health, llm_health, auth_health]
        overall_status = "healthy" if all(s.get("status") == "healthy" for s in all_services) else "unhealthy"
        
        # Detailed health status with full service information
        health_status = {
            "status": overall_status,
            "timestamp": "2024-01-01T00:00:00Z",  # Will be overridden by response helper
            "version": "1.0.0",
            "services": {
                "api": {
                    "status": "healthy",
                    "details": "API service responding normally"
                },
                "database": db_health,
                "configuration": config_health,
                "llm": llm_health,
                "auth": auth_health
            }
        }
        
        return create_standardized_response(health_status)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return create_error_response(
            "HEALTH_CHECK_ERROR",
            "Detailed health check failed",
            details=str(e),
            status_code=500
        )

@router.get("/database")
@router.get("/database/")
@require_auth(admin_only=True)
async def database_health(request: Request):
    """Database health check endpoint - requires admin authentication"""
    try:
        db_health = check_database_health()
        return create_standardized_response(db_health)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return create_error_response(
            "DATABASE_HEALTH_ERROR",
            "Database health check failed",
            details=str(e),
            status_code=500
        )

@router.get("/config")
@router.get("/config/")
@require_auth(admin_only=True)
async def config_health(request: Request):
    """Configuration health check endpoint - requires admin authentication"""
    try:
        config_health = check_config_health()
        return create_standardized_response(config_health)
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        return create_error_response(
            "CONFIG_HEALTH_ERROR",
            "Configuration health check failed",
            details=str(e),
            status_code=500
        )

@router.get("/llm")
@router.get("/llm/")
@require_auth(admin_only=True)
async def llm_health(request: Request):
    """LLM service health check endpoint - requires admin authentication"""
    try:
        llm_health = check_llm_health()
        return create_standardized_response(llm_health)
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return create_error_response(
            "LLM_HEALTH_ERROR",
            "LLM service health check failed",
            details=str(e),
            status_code=500
        )

@router.get("/auth")
@router.get("/auth/")
@require_auth(admin_only=True)
async def auth_health(request: Request):
    """Authentication service health check endpoint - requires admin authentication"""
    try:
        auth_health = check_auth_health()
        return create_standardized_response(auth_health)
    except Exception as e:
        logger.error(f"Authentication health check failed: {e}")
        return create_error_response(
            "AUTH_HEALTH_ERROR",
            "Authentication service health check failed",
            details=str(e),
            status_code=500
        )
