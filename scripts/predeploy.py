#!/usr/bin/env python3
"""
Pre-deployment script for Render.com
Runs database migrations before starting the web service
"""
import subprocess
import sys
import os

def run_migrations():
    """Run Alembic database migrations."""
    try:
        print("🔧 Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Database migrations completed successfully")
        print(result.stdout)
        return True
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
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    print("✅ Pre-deployment setup completed successfully!")

if __name__ == "__main__":
    main()