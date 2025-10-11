#!/bin/bash

# Frontend Server Script
# Serves the frontend files locally

echo "🌐 Starting Frontend Server"
echo "=========================="

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

echo "📁 Serving files from: $(pwd)"
echo "🌐 Frontend will be available at: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start a simple HTTP server
python -m http.server 8080