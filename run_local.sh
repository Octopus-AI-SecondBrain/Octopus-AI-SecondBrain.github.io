#!/usr/bin/env bash
set -euo pipefail

# Octopus AI Second Brain - Local Development Runner
# Sets up environment and starts the backend server

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/venv"

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# Trap cleanup on exit
cleanup() {
    log_info "Shutting down..."
    if [ ! -z "${SERVER_PID:-}" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

log_header "🐙 Octopus AI Second Brain - Local Setup"

# Step 1: Check Python
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_success "Found Python $PYTHON_VERSION"

# Step 2: Create/activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating virtual environment..."
    cd "$BACKEND_DIR"
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_success "Virtual environment exists"
fi

log_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
log_success "Virtual environment activated"

# Step 3: Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip -q
log_success "pip upgraded"

# Step 4: Install dependencies with numpy constraint
log_info "Installing dependencies (this may take a few minutes)..."
cd "$BACKEND_DIR"

# First install numpy with version constraint to avoid compatibility issues
log_info "Installing NumPy 1.x (required for compatibility)..."
pip install "numpy>=1.24.0,<2.0.0" -q
log_success "NumPy 1.x installed"

# Then install the package
log_info "Installing Octopus AI Second Brain..."
pip install -e . -q 2>&1 | grep -v "already satisfied" || true
log_success "All dependencies installed"

# Step 5: Create .env if needed
if [ ! -f "$BACKEND_DIR/.env" ]; then
    log_info "Creating .env file..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    
    # Generate secure secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" "$BACKEND_DIR/.env"
    else
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" "$BACKEND_DIR/.env"
    fi
    
    log_success ".env file created"
    log_warn "Add your OPENAI_API_KEY to .env for answer generation"
else
    log_success ".env file exists"
fi

# Step 6: Check PostgreSQL
log_info "Checking PostgreSQL..."
DB_HOST="localhost"
DB_PORT="5432"

if ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null && ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
    log_warn "PostgreSQL not running on $DB_HOST:$DB_PORT"
    
    if command -v docker &> /dev/null; then
        log_info "Starting PostgreSQL with Docker..."
        docker stop secondbrain-postgres 2>/dev/null || true
        docker rm secondbrain-postgres 2>/dev/null || true
        
        docker run -d \
            --name secondbrain-postgres \
            -e POSTGRES_USER=secondbrain \
            -e POSTGRES_PASSWORD=secondbrain \
            -e POSTGRES_DB=secondbrain \
            -p 5432:5432 \
            pgvector/pgvector:pg16 >/dev/null 2>&1
        
        log_success "PostgreSQL started"
        log_info "Waiting for PostgreSQL..."
        for i in {1..30}; do
            if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null || timeout 1 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
                log_success "PostgreSQL ready"
                break
            fi
            sleep 1
        done
    else
        log_error "Docker not found. Please install Docker or start PostgreSQL manually"
        echo ""
        echo "To start PostgreSQL with pgvector:"
        echo "  docker run -d --name secondbrain-postgres \\"
        echo "    -e POSTGRES_USER=secondbrain \\"
        echo "    -e POSTGRES_PASSWORD=secondbrain \\"
        echo "    -e POSTGRES_DB=secondbrain \\"
        echo "    -p 5432:5432 \\"
        echo "    pgvector/pgvector:pg16"
        exit 1
    fi
else
    log_success "PostgreSQL is running"
fi

# Step 7: Run migrations
log_info "Running database migrations..."
cd "$BACKEND_DIR"
alembic upgrade head
log_success "Database migrations completed"

# Step 8: Start server
log_header "🚀 Starting Octopus AI Second Brain"

echo ""
log_success "Backend server starting..."
echo ""
echo -e "  ${CYAN}API:${NC}     http://localhost:8000"
echo -e "  ${CYAN}Docs:${NC}    http://localhost:8000/api/docs"
echo -e "  ${CYAN}ReDoc:${NC}   http://localhost:8000/api/redoc"
echo ""
log_info "Press Ctrl+C to stop the server"
echo ""

cd "$BACKEND_DIR"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000