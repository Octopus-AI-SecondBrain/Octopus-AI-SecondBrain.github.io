#!/usr/bin/env bash
# Quick fix script for port conflicts

echo "🔧 Fixing port conflicts..."

# Kill processes on ports 8001 and 5173
echo "Clearing port 8001..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || echo "Port 8001 already clear"

echo "Clearing port 5173..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "Port 5173 already clear"

echo "✅ Ports cleared!"
echo ""
echo "Now run: ./run_local.sh"
