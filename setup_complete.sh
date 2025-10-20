#!/bin/bash

# ==============================================================================
# Octopus Second Brain - Complete Setup Script
# ==============================================================================
# This script will set up both frontend and backend for development
#
# Usage: ./setup_complete.sh
# ==============================================================================

set -e  # Exit on error

echo "🐙 Octopus Second Brain - Complete Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# Step 1: Check Prerequisites
# ==============================================================================

echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${YELLOW}⚠️  Warning: Node.js version is below 18. Some features may not work.${NC}"
fi

echo -e "${GREEN}✅ Node.js $(node -v) found${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $(python3 --version) found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm $(npm -v) found${NC}"

echo ""

# ==============================================================================
# Step 2: Backend Setup
# ==============================================================================

echo -e "${BLUE}Step 2: Setting up backend...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists, skipping...${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    
    # Generate a random SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update SECRET_KEY in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/dev-secret-key-change-this-in-production-min-32-chars/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/dev-secret-key-change-this-in-production-min-32-chars/$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✅ Backend .env file created with secure SECRET_KEY${NC}"
else
    echo -e "${YELLOW}⚠️  Backend .env already exists, skipping...${NC}"
fi

# Create data directories
mkdir -p data/database data/vector_db
echo -e "${GREEN}✅ Data directories created${NC}"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo -e "${GREEN}✅ Database migrations complete${NC}"

echo ""

# ==============================================================================
# Step 3: Frontend Setup
# ==============================================================================

echo -e "${BLUE}Step 3: Setting up frontend...${NC}"

cd frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Create frontend .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo -e "${GREEN}✅ Frontend .env file created${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend .env already exists, skipping...${NC}"
fi

cd ..

echo ""

# ==============================================================================
# Step 4: Summary and Next Steps
# ==============================================================================

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Start the backend (in one terminal):"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "2. Start the frontend (in another terminal):"
echo -e "   ${YELLOW}cd frontend${NC}"
echo -e "   ${YELLOW}npm run dev${NC}"
echo ""
echo "3. Open your browser:"
echo -e "   ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   - Getting Started: GETTING_STARTED.md"
echo "   - Refactoring Guide: REFACTORING_COMPLETE.md"
echo "   - API Docs (when backend running): http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
