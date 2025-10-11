#!/bin/bash

# SecondBrain Application Startup Script
# This script handles the PYTHONPATH configuration and database initialization

echo "🚀 Starting SecondBrain Application..."

# Navigate to project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Set Python path to project root
echo "🔧 Setting PYTHONPATH to: $PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"

# Initialize database if needed
echo "🗄️  Initializing database..."
python -c "
from backend.models.db import Base, engine, ensure_sqlite_schema
try:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
"

# TODO: When Alembic is set up, replace the above with:
# alembic upgrade head

# Start the FastAPI application
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📖 API Documentation available at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000