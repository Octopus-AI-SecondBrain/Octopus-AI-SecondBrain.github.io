#!/usr/bin/env python3
"""
Quick validation script to check for common issues after refactoring.
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False

def check_import_errors():
    """Try to import key modules to check for syntax errors."""
    print("\n🔍 Checking for import errors...")
    
    try:
        # Set PYTHONPATH
        sys.path.insert(0, str(Path.cwd()))
        
        # Set required env vars for imports
        os.environ.setdefault('SECRET_KEY', 'test-key-for-validation-only-min-32-chars')
        os.environ.setdefault('ENVIRONMENT', 'development')
        
        print("  Importing backend.config.config...")
        from backend.config import config
        print("  ✅ backend.config.config")
        
        print("  Importing backend.models.db...")
        from backend.models import db
        print("  ✅ backend.models.db")
        
        print("  Importing backend.core.security...")
        from backend.core import security
        print("  ✅ backend.core.security")
        
        print("  Importing backend.services.vector_store...")
        from backend.services import vector_store
        print("  ✅ backend.services.vector_store")
        
        print("  Importing backend.routes.auth...")
        from backend.routes import auth
        print("  ✅ backend.routes.auth")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🔍 SecondBrain Post-Refactoring Validation\n")
    print("=" * 60)
    
    all_good = True
    
    # Check critical files
    print("\n📁 Checking critical files...")
    all_good &= check_file_exists("backend/config/config.py", "Configuration")
    all_good &= check_file_exists("alembic.ini", "Alembic config")
    all_good &= check_file_exists("alembic/env.py", "Alembic environment")
    all_good &= check_file_exists("alembic/versions/001_initial_schema.py", "Initial migration")
    all_good &= check_file_exists("docker-compose.yml", "Docker Compose")
    all_good &= check_file_exists(".env.example", "Environment example")
    all_good &= check_file_exists("requirements.txt", "Requirements")
    all_good &= check_file_exists("MIGRATION_GUIDE_v2.md", "Migration guide")
    
    # Check that old file is gone
    if Path("backend/config/settings.py").exists():
        print("❌ OLD FILE STILL EXISTS: backend/config/settings.py (should be deleted)")
        all_good = False
    else:
        print("✅ Old settings.py removed")
    
    # Check imports
    all_good &= check_import_errors()
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure environment: cp .env.example .env")
        print("  3. Run migrations: alembic upgrade head")
        print("  4. Start server: ./scripts/start.sh")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease review the errors above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
