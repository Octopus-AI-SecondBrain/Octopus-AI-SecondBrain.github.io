#!/bin/bash

# SecondBrain Setup Script
# Sets up the development environment from scratch

echo "🧠 SecondBrain Setup"
echo "===================="

# Navigate to project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create data directories
echo "📂 Creating data directories..."
mkdir -p data/database
mkdir -p data/vector_db

# Check if .env exists, if not copy from .env.example
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️  Creating .env from .env.example..."
        cp .env.example .env
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file and set a strong SECRET_KEY!"
        echo "   Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        echo ""
    else
        echo "❌ .env.example not found. Creating minimal .env..."
        cat > .env << EOF
# IMPORTANT: Change SECRET_KEY before deploying!
SECRET_KEY=CHANGE-ME-TO-A-SECURE-RANDOM-STRING-MIN-32-CHARS
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./data/database/secondbrain.db
CHROMA_PATH=./data/vector_db
EOF
    fi
else
    echo "✅ .env file already exists"
fi

# TODO: Initialize database migrations
echo "🗄️  Database migrations..."
echo "   Currently using automatic table creation via scripts/start.sh"
echo "   TODO: Set up Alembic for proper migrations"
echo "   Future: Run 'alembic upgrade head' here"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and set a strong SECRET_KEY (required!)"
echo "2. Run: ./scripts/start.sh"
echo ""
echo "To access the application:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend: Open frontend/index.html in a browser or serve it locally"
echo "   API Docs: http://localhost:8000/docs (development only)"