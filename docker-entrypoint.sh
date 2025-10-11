#!/bin/bash
set -e

echo "🚀 Starting SecondBrain Backend..."

# Initialize database schema
echo "📦 Initializing database..."
python -c "
from backend.models.db import Base, engine, ensure_sqlite_schema
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created')
    try:
        ensure_sqlite_schema()
        print('✅ SQLite schema verified')
    except Exception as e:
        print(f'⚠️  Schema verification skipped: {e}')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"

echo "🎯 Starting uvicorn server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
