#!/usr/bin/env bash
set -euo pipefail

# SecondBrain Local Development Runner
# Starts backend (FastAPI) and frontend (Vite) in parallel with proper cleanup

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

BACKEND_PORT=8001
FRONTEND_PORT=5173

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_backend() { echo -e "${BLUE}[BACKEND]${NC} $1"; }
log_frontend() { echo -e "${GREEN}[FRONTEND]${NC} $1"; }

# Trap cleanup on exit signals
cleanup() {
    log_info "Shutting down servers..."
    
    # Kill process groups to ensure all subprocesses are terminated
    if [ ! -z "${BACKEND_PID:-}" ]; then
        kill -- -"$BACKEND_PID" 2>/dev/null || true
        log_info "Backend stopped (PID $BACKEND_PID)"
    fi
    
    if [ ! -z "${FRONTEND_PID:-}" ]; then
        kill -- -"$FRONTEND_PID" 2>/dev/null || true
        log_info "Frontend stopped (PID $FRONTEND_PID)"
    fi
    
    log_success "Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

log_info "Starting SecondBrain Local Development Environment"
echo ""

# Step 1: Python virtual environment
if [ ! -d "venv" ]; then
    log_warn "Virtual environment not found, creating..."
    python3 -m venv venv
    log_success "Virtual environment created"
fi

# Step 2: Backend dependencies
log_info "Checking backend dependencies..."
source venv/bin/activate

if ! pip show fastapi &>/dev/null; then
    log_warn "Installing backend dependencies..."
    pip install -q -r requirements.txt
    log_success "Backend dependencies installed"
else
    log_success "Backend dependencies OK"
fi

# Step 3: Database migrations
log_info "Running database migrations..."
alembic upgrade head 2>&1 | while IFS= read -r line; do
    log_info "$line"
done
log_success "Database migrations complete"

deactivate

# Step 4: Frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    log_warn "Installing frontend dependencies..."
    (cd frontend && npm install)
    log_success "Frontend dependencies installed"
else
    log_success "Frontend dependencies OK"
fi

echo ""
log_info "Starting servers..."
echo ""

# Step 5: Start backend in a subshell with process group
(
    source venv/bin/activate
    cd "$PROJECT_ROOT"
    export PYTHONPATH="$PROJECT_ROOT"
    python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" 2>&1 | \
        while IFS= read -r line; do log_backend "$line"; done
) &
BACKEND_PID=$!

sleep 2

# Step 6: Start frontend in a subshell with process group
(
    cd "$PROJECT_ROOT/frontend"
    npm run dev 2>&1 | \
        while IFS= read -r line; do log_frontend "$line"; done
) &
FRONTEND_PID=$!

sleep 3

# Print status
echo ""
log_success "SecondBrain is running!"
echo ""
echo -e "  ${CYAN}Frontend:${NC}  http://localhost:$FRONTEND_PORT"
echo -e "  ${BLUE}Backend:${NC}   http://localhost:$BACKEND_PORT"
echo -e "  ${BLUE}API Docs:${NC}  http://localhost:$BACKEND_PORT/docs"
echo ""
log_info "Press Ctrl+C to stop all servers"
echo ""

# Wait indefinitely until signal received
wait