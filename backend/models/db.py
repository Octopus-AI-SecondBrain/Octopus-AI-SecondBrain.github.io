import os
from sqlalchemy import create_engine, inspect, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from backend.config.config import get_settings

# Get settings
settings = get_settings()

# Ensure database directory exists for SQLite
if settings.database.url.startswith("sqlite:///"):
    from pathlib import Path
    db_path = Path(settings.database.url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

# Determine if using PostgreSQL
is_postgresql = settings.database.url.startswith("postgresql://") or settings.database.url.startswith("postgresql+psycopg2://")

# Create engine with appropriate settings
if is_postgresql:
    # PostgreSQL settings
    engine = create_engine(
        settings.database.url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.database.echo
    )
else:
    # SQLite settings
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.database.url,
        connect_args=connect_args,
        echo=settings.database.echo
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# Note: Database schema creation and migrations are now handled by Alembic.
# DO NOT use Base.metadata.create_all() in production.
# Run 'alembic upgrade head' to apply migrations.
