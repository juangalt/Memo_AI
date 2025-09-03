"""Health check API routes."""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import os

from utils.logging_config import get_logger

from models import db_manager
from services import config_service, get_auth_service
from services.llm_service import EnhancedLLMService
from decorators import require_auth
from utils.responses import create_standardized_response, create_error_response

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)

_auth_service = get_auth_service()
_llm_service = EnhancedLLMService()


def _collect_service_status():
    """Gather status for core services."""
    try:
        db_health = db_manager.health_check()
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"Database health check failed: {e}")
        db_health = {"status": "unhealthy", "error": str(e)}

    try:
        config_health = config_service.health_check()
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"Config health check failed: {e}")
        config_health = {"status": "unhealthy", "error": str(e)}

    try:
        llm_health = _llm_service.validate_configuration()
        llm_status = "healthy" if llm_health["valid"] else "unhealthy"
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"LLM health check failed: {e}")
        llm_status = "unhealthy"
        llm_health = {"error": str(e)}

    try:
        auth_health = _auth_service.health_check()
        auth_status = auth_health["status"]
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"Auth health check failed: {e}")
        auth_status = "unhealthy"
        auth_health = {"error": str(e)}

    return db_health, config_health, llm_status, llm_health, auth_status, auth_health


@router.get("/")
async def health_check():
    """Public basic health check."""
    db_health, config_health, llm_status, _, auth_status, _ = _collect_service_status()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": db_health["status"],
            "configuration": config_health["status"],
            "llm": llm_status,
            "auth": auth_status,
        },
    }

    if any(status != "healthy" for status in health_status["services"].values()):
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=503, content=create_standardized_response(health_status))

    return create_standardized_response(health_status)


@router.get("/detailed")
@require_auth(admin_only=True)
async def detailed_health_check(request: Request):
    """Detailed health check endpoint - admin only."""
    db_health, config_health, llm_status, llm_health, auth_status, auth_health = _collect_service_status()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": db_health["status"],
            "configuration": config_health["status"],
            "llm": llm_status,
            "auth": auth_status,
        },
    }

    if db_health["status"] == "healthy":
        health_status["database_details"] = {
            "tables": db_health.get("tables", []),
            "journal_mode": db_health.get("journal_mode", ""),
            "user_count": db_health.get("user_count", 0),
        }
    else:
        health_status["database_error"] = db_health.get("error", "Unknown error")

    if config_health["status"] == "healthy":
        health_status["config_details"] = {
            "configs_loaded": config_health.get("configs_loaded", []),
            "last_loaded": config_health.get("last_loaded", ""),
            "config_dir": config_health.get("config_dir", ""),
        }
    else:
        health_status["config_error"] = config_health.get("error", "Unknown error")

    if llm_status == "healthy":
        health_status["llm_details"] = {
            "provider": "anthropic",
            "model": llm_health.get("model", "claude-3-haiku-20240307"),
            "api_accessible": llm_health.get("components", {}).get("claude_client", False),
            "config_loaded": llm_health.get("components", {}).get("prompt_config", False),
            "supported_languages": llm_health.get("supported_languages", []),
            "default_language": llm_health.get("default_language", "en"),
        }
    else:
        health_status["llm_error"] = llm_health.get("error", "Unknown error")

    if auth_status == "healthy":
        health_status["auth_details"] = {
            "config_loaded": auth_health.get("config_loaded", False),
            "active_sessions": auth_health.get("active_sessions", 0),
            "brute_force_protection": auth_health.get("brute_force_protection", False),
        }
    else:
        health_status["auth_error"] = auth_health.get("error", "Unknown error")

    app_env = os.environ.get("APP_ENV", "production")
    auth_config = config_service.get_auth_config()
    debug_mode = False
    if auth_config and "security_settings" in auth_config:
        debug_mode = auth_config["security_settings"].get("debug_mode", False)
    health_status["environment"] = {
        "app_env": app_env,
        "debug_mode": debug_mode,
        "mode": "development" if app_env == "development" or debug_mode else "production",
    }

    if any(status != "healthy" for status in health_status["services"].values()):
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=503, content=create_standardized_response(health_status))

    return create_standardized_response(health_status)


@router.get("/database")
@require_auth(admin_only=True)
async def database_health_check(request: Request):
    """Database-specific health check endpoint - admin only."""
    try:
        db_health = db_manager.health_check()
        return create_standardized_response(
            {
                "status": db_health["status"],
                "timestamp": datetime.utcnow().isoformat(),
                "database": db_health,
            }
        )
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content=create_error_response(
                "DATABASE_HEALTH_FAILED", "Database health check failed", details=str(e)
            ),
        )


@router.get("/config")
@require_auth(admin_only=True)
async def config_health_check(request: Request):
    """Configuration-specific health check endpoint - admin only."""
    try:
        config_health = config_service.health_check()
        return create_standardized_response(
            {
                "status": config_health["status"],
                "timestamp": datetime.utcnow().isoformat(),
                "configuration": {
                    "status": config_health["status"],
                    "configs_loaded": config_health.get("configs_loaded", []),
                    "last_loaded": config_health.get("last_loaded", ""),
                    "config_count": len(config_health.get("configs_loaded", [])),
                },
            }
        )
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"Configuration health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content=create_error_response(
                "CONFIG_HEALTH_FAILED", "Configuration health check failed", details=str(e)
            ),
        )


@router.get("/llm")
@require_auth(admin_only=True)
async def llm_health_check(request: Request):
    """LLM service health check endpoint - admin only."""
    try:
        llm_health = _llm_service.validate_configuration()
        sanitized_llm_health = {
            "valid": llm_health["valid"],
            "components": llm_health.get("components", {}),
            "supported_languages": llm_health.get("supported_languages", []),
            "default_language": llm_health.get("default_language", "en"),
            "model": llm_health.get("model", "unknown"),
        }
        response_data = {
            "status": "healthy" if llm_health["valid"] else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "llm": sanitized_llm_health,
        }
        if llm_health["valid"]:
            return create_standardized_response(response_data)
        return JSONResponse(status_code=503, content=create_standardized_response(response_data))
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"LLM health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content=create_error_response(
                "LLM_HEALTH_FAILED", "LLM health check failed", details=str(e)
            ),
        )


@router.get("/auth")
@require_auth(admin_only=True)
async def auth_health_check(request: Request):
    """Authentication service health check endpoint - admin only."""
    try:
        auth_health = _auth_service.health_check()
        sanitized_auth_health = {
            "status": auth_health["status"],
            "service": auth_health.get("service", "authentication"),
            "config_loaded": auth_health.get("config_loaded", False),
            "active_sessions": auth_health.get("active_sessions", 0),
            "brute_force_protection": auth_health.get("brute_force_protection", False),
            "session_expiry_hours": auth_health.get("session_expiry_hours", 24),
            "session_token_length": auth_health.get("session_token_length", 32),
        }
        response_data = {
            "status": auth_health["status"],
            "timestamp": datetime.utcnow().isoformat(),
            "auth": sanitized_auth_health,
        }
        if auth_health["status"] == "healthy":
            return create_standardized_response(response_data)
        return JSONResponse(status_code=503, content=create_standardized_response(response_data))
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"Auth health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content=create_error_response(
                "AUTH_HEALTH_FAILED", "Authentication health check failed", details=str(e)
            ),
        )
