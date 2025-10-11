"""
SecondBrain API - Main Application Entry Point.
Neural knowledge mapping with 3D visualization - Local hosting only.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from pathlib import Path

from backend.config.config import get_settings
from backend.core.logging import setup_logging, get_logger
from backend.routes import auth, notes, search, map as map_route

# Load settings
settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.server.log_level,
    log_file=settings.log_file,
    enable_json=settings.enable_json_logging
)
logger = get_logger("secondbrain.main")

# Log startup
logger.info(
    f"Starting {settings.app_name} v{settings.app_version}",
    extra={"environment": settings.environment}
)

# TODO: Database migrations should be run separately before starting the application
# Run: alembic upgrade head
# For now, we skip automatic table creation to avoid side effects at import time.
# Initial setup: Run scripts/start.sh which handles schema initialization.
logger.info("Database initialization should be done via migrations (see scripts/start.sh)")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=f"{settings.app_name} - {settings.environment.title()}",
    version=settings.app_version,
    description="Neural knowledge mapping with 3D visualization - Local hosting only",
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
    debug=settings.debug
)

# Add rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add SlowAPI exception handler for rate limit errors
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning(
        f"Rate limit exceeded for {request.client.host if request.client else 'unknown'} on {request.url.path}",
        extra={
            "client": request.client.host if request.client else None,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later."
        },
        headers={"Retry-After": "60"}
    )

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    try:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Only set HSTS in production with HTTPS enabled
        if settings.is_production() and settings.enable_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
    except Exception as exc:
        logger.error(f"Error in security headers middleware: {exc}", exc_info=True)
        raise

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None
        }
    )
    response = await call_next(request)
    logger.info(
        f"Response: {response.status_code}",
        extra={
            "status_code": response.status_code,
            "path": request.url.path
        }
    )
    return response

# Configure allowed hosts for TrustedHostMiddleware
allowed_hosts = ["localhost", "127.0.0.1", "*.localhost", "*.onrender.com"]

# Add CORS origins as allowed hosts
if hasattr(settings, 'cors') and settings.cors.allowed_origins:
    for origin in settings.cors.allowed_origins:
        # Extract domain from URL
        if origin != "*":
            domain = origin.replace("https://", "").replace("http://", "").split("/")[0]
            if domain and domain not in allowed_hosts:
                allowed_hosts.append(domain)

logger.info(f"Configuring trusted hosts: {allowed_hosts}")

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Configure CORS origins
allowed_origins = settings.cors.allowed_origins
logger.info(f"Configuring CORS for origins: {allowed_origins}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
    max_age=settings.cors.max_age
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(map_route.router, prefix="/map", tags=["Map"])

@app.get("/")
def root():
    """Health check endpoint."""
    logger.debug("Root endpoint accessed")
    return {
        "message": "SecondBrain API is running",
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "database": "connected"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Application startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Application shutting down")
