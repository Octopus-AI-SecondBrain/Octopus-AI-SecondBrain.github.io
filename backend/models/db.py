import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config.config import get_settings

# Get settings
settings = get_settings()

# Ensure database directory exists
if settings.database.url.startswith("sqlite:///"):
    from pathlib import Path
    db_path = Path(settings.database.url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

# Create engine with settings
connect_args = {"check_same_thread": False} if settings.database.url.startswith("sqlite") else {}
engine = create_engine(
    settings.database.url,
    connect_args=connect_args,
    echo=settings.database.echo
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def ensure_sqlite_schema() -> None:
    """Make sure legacy SQLite databases have the latest columns."""
    if not settings.database.url.startswith("sqlite"):
        return

    with engine.begin() as conn:
        result = conn.exec_driver_sql("PRAGMA table_info('notes')")
        columns = {row[1] for row in result}
        if not columns:
            return

        if "embedding_model" not in columns:
            conn.exec_driver_sql("ALTER TABLE notes ADD COLUMN embedding_model TEXT")
            columns.add("embedding_model")

        # For SQLite, we need to use DEFAULT (datetime('now')) instead of CURRENT_TIMESTAMP for ALTER TABLE
        if "created_at" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE notes ADD COLUMN created_at TIMESTAMP"
            )
            # Update existing rows with current timestamp
            conn.exec_driver_sql(
                "UPDATE notes SET created_at = datetime('now') WHERE created_at IS NULL"
            )
            columns.add("created_at")

        if "updated_at" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE notes ADD COLUMN updated_at TIMESTAMP"
            )
            # Update existing rows with current timestamp
            conn.exec_driver_sql(
                "UPDATE notes SET updated_at = datetime('now') WHERE updated_at IS NULL"
            )
            columns.add("updated_at")
