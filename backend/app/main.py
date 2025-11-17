"""
Octopus AI Second Brain - FastAPI Application
Main application entry point with all routes and middleware.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import text

from .core.logging import get_logger, setup_logging
from .core.settings import get_settings
from .core.redis import get_redis, close_redis
from .db.session import engine, get_db
from .api.healthz import router as healthz_router
from .api.auth import router as auth_router
from .api.notes import router as notes_router
from .api.rag import router as rag_router
from .api.jobs import router as jobs_router

# Setup logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Octopus AI Second Brain")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize Redis
    try:
        redis = await get_redis()
        health = await redis.health_check()
        logger.info(f"Redis status: {health['status']} (backend: {health['backend']})")
    except Exception as e:
        logger.warning(f"Redis initialization warning: {e}")

    # Test database connection
    try:
        # Get a test session
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            break
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Octopus AI Second Brain")
    await close_redis()
    await engine.dispose()
    logger.info("Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="Octopus AI Second Brain",
    description="A modular multi-modal RAG application for building your personal knowledge base",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.credentials,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: The request
        exc: The exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# Register routers
app.include_router(healthz_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "name": "Octopus AI Second Brain",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
