#!/usr/bin/env python3
"""
Pre-deployment script for Render.com
Runs database migrations before starting the web service
"""
import subprocess
import sys
import os
import time

def run_migrations():
    """Run Alembic database migrations."""
    try:
        print("🔧 Running database migrations...")
        
        # First, ensure alembic can connect to the database
        print("🔌 Testing database connection...")
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"Current migration status: {result.stdout}")
        
        # Run the migrations
        print("⬆️ Upgrading to head...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        print("✅ Database migrations completed successfully")
        print(result.stdout)
        if result.stderr:
            print(f"Migration warnings: {result.stderr}")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Migration timed out. Database might be slow to respond.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed in requirements.txt")
        return False

def main():
    """Main pre-deployment function."""
    print("🚀 Starting pre-deployment setup...")
    
    # Check if DATABASE_URL is set (required for production)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    # Check if it's PostgreSQL (expected for Render)
    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        print(f"✅ PostgreSQL database detected")
    elif database_url.startswith("sqlite://"):
        print("⚠️ SQLite database detected (development mode)")
    else:
        print(f"⚠️ Unknown database type: {database_url[:20]}...")
    
    # Wait a moment for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(2)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migration failed, but continuing startup...")
        # Don't exit with error on Render, let the app handle it
        # sys.exit(1)
    
    print("✅ Pre-deployment setup completed!")

if __name__ == "__main__":
    main()