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

# Run Alembic migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "⚠️  Warning: Database migration had issues. Check alembic configuration."
    echo "    For first-time setup, you may need to initialize Alembic:"
    echo "    1. Ensure the database exists"
    echo "    2. Run: alembic upgrade head"
    exit 1
fi

# Start the FastAPI application
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📖 API Documentation available at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000