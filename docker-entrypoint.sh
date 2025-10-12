#!/bin/bash
set -e

echo "🚀 Starting SecondBrain Backend..."

# Run Alembic database migrations
echo "� Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed"
    exit 1
fi

# Run any additional migrations (if needed)
echo "🔄 Running additional migrations..."
python scripts/migrate_add_admin.py || echo "⚠️  Migration warning (may already be applied)"

echo "🎯 Starting uvicorn server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
