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
from services import config_service, get_llm_service, evaluate_text_with_llm

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
        
        # Basic health check
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": "healthy",
                "database": db_health["status"],
                "configuration": config_health["status"],
                "llm": llm_status
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

@app.post("/api/v1/sessions/create")
async def create_session():
    """Create a new session for user"""
    try:
        # Generate session ID
        session_id = secrets.token_urlsafe(32)
        
        # Create session in database
        session = Session.create(session_id=session_id)
        
        return {
            "data": {
                "session_id": session.session_id,
                "expires_at": session.expires_at.isoformat(),
                "created_at": session.created_at.isoformat()
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": session_id[:8]
            },
            "errors": []
        }
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

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
    """Submit text for evaluation"""
    try:
        # Parse request body
        body = await request.json()
        text_content = body.get("text_content", "")
        session_id = body.get("session_id", "")
        
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
        
        return {
            "data": {
                "evaluation": evaluation_result
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

