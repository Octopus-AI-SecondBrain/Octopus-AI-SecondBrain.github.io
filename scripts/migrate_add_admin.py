#!/usr/bin/env python3
"""
Database migration script - Adds is_admin field to users table
Run this after deploying the new code to Render
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.models.db import engine, SessionLocal
from backend.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("migration")

def run_migration():
    """Run the database migration to add is_admin column."""
    try:
        logger.info("Starting migration: Add is_admin column to users table")
        
        with engine.connect() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'is_admin'
            """)
            
            result = conn.execute(check_query)
            exists = result.fetchone() is not None
            
            if exists:
                logger.info("Column 'is_admin' already exists in users table - skipping migration")
                return True
            
            # Add the column
            logger.info("Adding is_admin column to users table...")
            alter_query = text("""
                ALTER TABLE users 
                ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE
            """)
            conn.execute(alter_query)
            
            # Create index
            logger.info("Creating index on is_admin column...")
            index_query = text("""
                CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin)
            """)
            conn.execute(index_query)
            
            conn.commit()
            logger.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Database Migration: Add is_admin field")
    logger.info("=" * 60)
    
    success = run_migration()
    
    if success:
        logger.info("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Migration failed!")
        sys.exit(1)
