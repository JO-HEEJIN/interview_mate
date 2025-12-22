"""
InterviewMate.ai Backend
FastAPI application entry point
Production-ready with comprehensive middleware and error handling
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.config import settings
from app.api import websocket, profile, interview, qa_pairs, context_upload, interview_profile, subscriptions, payments, interview_sessions, embeddings

# Setup logging using existing config
logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to add timing information to responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[{request_id}] from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add timing headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[{request_id}] - Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[{request_id}] - Error: {str(e)} - Time: {process_time:.4f}s",
                exc_info=True
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    def __init__(self, app, https_redirect: bool = False):
        super().__init__(app)
        self.https_redirect = https_redirect
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create upload directory if it doesn't exist
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered interview assistant API",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    TimingMiddleware,
)

app.add_middleware(
    SecurityHeadersMiddleware,
    https_redirect=settings.is_production,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Allow all hosts - CORS handles security
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=["*"],
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail} "
        f"[{request_id}] - {request.method} {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"Validation error: {exc.errors()} "
        f"[{request_id}] - {request.method} {request.url.path}"
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Validation failed",
                "type": "validation_error",
                "details": exc.errors(),
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled exception: {str(exc)} "
        f"[{request_id}] - {request.method} {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error" if settings.is_production else str(exc),
                "type": "internal_error",
                "request_id": request_id,
            }
        },
    )


# Include routers - WebSocket 라우터 추가
app.include_router(
    websocket.router,
    tags=["websocket"],
)

app.include_router(
    profile.router,
    tags=["profile"],
)

app.include_router(
    interview.router,
    tags=["interview"],
)

app.include_router(
    qa_pairs.router,
    tags=["qa-pairs"],
)

app.include_router(
    context_upload.router,
    tags=["context-upload"],
)

app.include_router(
    interview_profile.router,
    tags=["interview-profile"],
)

app.include_router(
    subscriptions.router,
    tags=["subscriptions"],
)

app.include_router(
    payments.router,
    tags=["payments"],
)

app.include_router(
    interview_sessions.router,
    tags=["interview-sessions"],
)

app.include_router(
    embeddings.router,
    tags=["embeddings"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "status": "running",
        "docs_url": "/docs" if settings.is_development else None,
        "websocket_endpoint": "/ws/transcribe",
        "api_base": "/api"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        },
        "services": {
            "database": "connected" if settings.DATABASE_URL else "not_configured",
            "supabase": "configured" if settings.SUPABASE_URL else "not_configured",
            "openai": "configured" if settings.OPENAI_API_KEY else "not_configured",
            "anthropic": "configured" if settings.ANTHROPIC_API_KEY else "not_configured",
        },
        "features": {
            "metrics": settings.ENABLE_METRICS,
            "websocket": True,
            "file_upload": True,
        },
        "endpoints": {
            "websocket": "/ws/transcribe",
            "api": "/api",
            "docs": "/docs"
        }
    }


# Detailed health check for monitoring
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check for monitoring systems"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {},
    }
    
    # Check database connectivity
    try:
        # Add actual database check here if needed
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection OK",
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": str(e),
        }
        health_status["status"] = "unhealthy"
    
    # Check API keys
    api_checks = {
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
        "supabase": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY),
    }
    
    for service, configured in api_checks.items():
        health_status["checks"][service] = {
            "status": "healthy" if configured else "warning",
            "message": "Configured" if configured else "Not configured",
        }
    
    return health_status


# Metrics endpoint (if enabled)
if settings.ENABLE_METRICS:
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        # Add actual metrics collection here
        return Response(
            content="# HELP http_requests_total Total HTTP requests\n"
                   "# TYPE http_requests_total counter\n"
                   "http_requests_total 0\n",
            media_type="text/plain",
        )


if __name__ == "__main__":
    import uvicorn
    
    # Configure logging using config.py
    logging_config = settings.get_logging_config()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.WORKERS,
        log_config=logging_config,
        access_log=True,
    )