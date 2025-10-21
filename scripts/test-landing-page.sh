#!/bin/bash

# 🧪 Test Landing Page Locally
# This script serves the docs/ folder locally for testing before deployment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Landing Page Locally${NC}"
echo ""

# Check if docs/ exists
if [ ! -d "docs" ]; then
    echo -e "${YELLOW}⚠️  docs/ directory not found!${NC}"
    echo "Run this script from the project root directory."
    exit 1
fi

# Check if docs/index.html exists
if [ ! -f "docs/index.html" ]; then
    echo -e "${YELLOW}⚠️  docs/index.html not found!${NC}"
    echo "Landing page files may be missing."
    exit 1
fi

# Function to test with different servers
test_server() {
    PORT=8000
    
    echo -e "${GREEN}✓${NC} Landing page files found"
    echo ""
    echo -e "${BLUE}Starting local server on http://localhost:$PORT${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    echo "Testing:"
    echo "  • Landing page: http://localhost:$PORT/"
    echo "  • Check responsive design"
    echo "  • Test beta form"
    echo "  • Test modal"
    echo "  • Check animations"
    echo ""
    
    # Try Python 3's http.server
    if command -v python3 &> /dev/null; then
        cd docs
        python3 -m http.server $PORT
    elif command -v python &> /dev/null; then
        cd docs
        python -m SimpleHTTPServer $PORT
    else
        echo -e "${YELLOW}⚠️  Python not found. Install Python or use another server.${NC}"
        echo ""
        echo "Alternatives:"
        echo "  • npm install -g serve && serve docs"
        echo "  • npm install -g http-server && http-server docs"
        exit 1
    fi
}

# Start server
test_server
