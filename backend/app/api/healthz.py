"""
Octopus AI Second Brain - Health Check Endpoint
"""
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..schemas.common import HealthResponse
from ..core.logging import get_logger
from ..core.redis import get_redis

logger = get_logger(__name__)
router = APIRouter()


@router.get("/healthz", response_model=HealthResponse, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.

    Returns system health status including database and Redis connectivity.
    """
    from sqlalchemy import text
    from ..core.settings import get_settings

    settings = get_settings()

    # Test database connection
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    # Test Redis connection
    try:
        redis = await get_redis()
        redis_health = await redis.health_check()
        redis_status = redis_health["status"]
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"

    # Determine overall status
    if db_status == "healthy" and redis_status in ("healthy", "disabled"):
        overall_status = "healthy"
    elif db_status == "unhealthy":
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version="2.0.0",
        environment=settings.environment,
        database=db_status,
        redis=redis_status,
        vector_store="pgvector",
        openai="not_checked",
        message=(
            "System operational"
            if overall_status == "healthy"
            else "System degraded or unhealthy"
        ),
    )


@router.get("/healthz/detailed", tags=["Health"])
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Detailed health check with comprehensive service status.

    Checks:
    - Database connectivity and version
    - Redis connectivity and info
    - Disk space availability
    - Memory usage (if psutil available)

    Returns:
        Detailed health check with individual service status

    Raises:
        HTTPException: If critical services are unhealthy (503)
    """
    from sqlalchemy import text

    checks = {}
    all_healthy = True

    # 1. Database health check with version
    try:
        result = await db.execute(text("SELECT version()"))
        version = result.scalar()
        checks["database"] = {"status": "healthy", "version": version[:100] if version else "unknown"}
        logger.debug("Database health check: OK")
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)[:100]}
        all_healthy = False
        logger.error(f"Database health check failed: {e}")

    # 2. Redis health check
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = {"status": "healthy"}
        logger.debug("Redis health check: OK")
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)[:100]}
        all_healthy = False
        logger.error(f"Redis health check failed: {e}")

    # 3. Disk space check
    try:
        total, used, free = shutil.disk_usage("/")
        percent_used = (used / total) * 100
        free_gb = free / (1024 ** 3)

        disk_status = "healthy"
        if percent_used > 90:
            disk_status = "warning"
            logger.warning(f"Disk space running low: {percent_used:.1f}% used")

        checks["disk_space"] = {
            "status": disk_status,
            "percent_used": f"{percent_used:.1f}%",
            "free_gb": f"{free_gb:.1f}",
            "total_gb": f"{total / (1024 ** 3):.1f}",
        }
    except Exception as e:
        checks["disk_space"] = {"status": "unknown", "error": str(e)[:100]}
        logger.warning(f"Disk space check failed: {e}")

    # 4. Memory check (optional, requires psutil)
    try:
        import psutil
        memory = psutil.virtual_memory()
        percent_used = memory.percent

        memory_status = "healthy"
        if percent_used > 90:
            memory_status = "warning"
            logger.warning(f"Memory usage high: {percent_used:.1f}%")

        checks["memory"] = {
            "status": memory_status,
            "percent_used": f"{percent_used:.1f}%",
            "available_gb": f"{memory.available / (1024 ** 3):.1f}",
        }
    except ImportError:
        checks["memory"] = {"status": "not_available", "note": "psutil not installed"}
    except Exception as e:
        checks["memory"] = {"status": "unknown", "error": str(e)[:100]}

    # Determine overall status
    if all_healthy:
        overall_status = "healthy"
    elif checks.get("database", {}).get("status") == "healthy" and \
         checks.get("redis", {}).get("status") == "healthy":
        overall_status = "degraded"  # Critical services OK, but some warnings
    else:
        overall_status = "unhealthy"

    # If critical services are down, return 503
    if overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": overall_status,
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Critical services are unavailable",
            },
        )

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "checks": checks,
    }


@router.get("/healthz/ready", tags=["Health"])
async def readiness_probe(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if the application is ready to serve traffic.
    Checks critical dependencies (database, redis).

    Returns:
        Ready status

    Raises:
        HTTPException: If critical services are unavailable (503)
    """
    from sqlalchemy import text

    checks = []

    # Quick database check
    try:
        await db.execute(text("SELECT 1"))
        checks.append("database:ok")
    except Exception as e:
        logger.error(f"Readiness probe: database check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "reason": "database unavailable"},
        )

    # Quick Redis check
    try:
        redis = await get_redis()
        await redis.ping()
        checks.append("redis:ok")
    except Exception as e:
        logger.error(f"Readiness probe: redis check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "reason": "redis unavailable"},
        )

    return {
        "status": "ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }
