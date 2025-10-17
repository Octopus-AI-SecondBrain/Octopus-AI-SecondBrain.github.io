"""
SecondBrain API - Main Application Entry Point.
Neural knowledge mapping with 3D visualization - Local hosting only.
"""

import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from backend.config.config import get_settings
from backend.core.logging import setup_logging, get_logger
from backend.routes import auth, notes, search, map as map_route
from backend.models.db import engine

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

# IMPORTANT: Database migrations must be run separately before starting the application
# Run: alembic upgrade head
# DO NOT use Base.metadata.create_all() in production - it can cause race conditions
# and doesn't support proper schema versioning.
# See scripts/start.sh for the proper startup sequence.
logger.info(
    "Database schema should be managed via Alembic migrations. "
    "Run 'alembic upgrade head' before starting the application."
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


def check_database_schema():
    """
    Check if required database tables exist.
    Logs critical warning if migrations haven't been run.
    """
    try:
        with engine.connect() as connection:
            # Check for existence of key tables - works for both SQLite and PostgreSQL
            db_url = str(engine.url)
            if 'sqlite' in db_url:
                # SQLite query
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'notes')"))
            else:
                # PostgreSQL query
                result = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name IN ('users', 'notes')"
                ))
            
            existing_tables = {row[0] for row in result.fetchall()}
            
            required_tables = {'users', 'notes'}
            missing_tables = required_tables - existing_tables
            
            if missing_tables:
                logger.critical(
                    f"CRITICAL: Required database tables missing: {missing_tables}. "
                    f"Run 'alembic upgrade head' to create the database schema before starting the application."
                )
                return False
            else:
                logger.info("Database schema check passed - all required tables exist")
                return True
                
    except OperationalError as exc:
        logger.critical(
            f"CRITICAL: Cannot connect to database or database file missing: {exc}. "
            f"Run 'alembic upgrade head' to create the database schema."
        )
        return False
    except Exception as exc:
        logger.error(f"Unexpected error during database schema check: {exc}", exc_info=True)
        return False

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
allowed_hosts = [
    "localhost", 
    "127.0.0.1", 
    "*.localhost", 
    "*.onrender.com", 
    "*.github.io",
    "octopus-ai-secondbrain.github.io",
    "testserver"
]

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
    # Check database schema as part of health check
    schema_ok = check_database_schema()
    
    return {
        "status": "healthy" if schema_ok else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "database": "connected" if schema_ok else "schema_missing",
        "message": "OK" if schema_ok else "Database schema missing - run 'alembic upgrade head'"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    # Check database schema
    schema_ok = check_database_schema()
    if not schema_ok:
        logger.critical("APPLICATION STARTUP BLOCKED: Database schema not ready")
        # Only block startup if not in test environment
        # Test environment is detected by special test patterns in database URLs or pytest detection
        test_environment = (
            "test" in settings.database.url.lower() or
            "pytest" in str(Path.cwd()) or
            os.getenv("PYTEST_CURRENT_TEST") is not None
        )
        
        if not test_environment:
            # Raise exception to prevent startup if database is not properly initialized
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not properly initialized. Please run 'alembic upgrade head' to create the required tables."
            )
        else:
            logger.warning("Database schema missing but allowing startup in test environment")
    
    logger.info("Application startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Application shutting down")
