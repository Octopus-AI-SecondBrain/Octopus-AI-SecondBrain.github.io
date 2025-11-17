"""
Octopus AI Second Brain - Database Session and Engine
SQLAlchemy 2.0 async setup with PostgreSQL and pgvector support.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from ..core.settings import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.get_database_url().replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.database.echo,
)


# Session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# Base class for models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.

    Yields:
        Database session

    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

