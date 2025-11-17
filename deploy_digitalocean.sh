#!/bin/bash
# DigitalOcean Deployment Script for SecondBrain

set -e

echo "🚀 DigitalOcean SecondBrain Deployment Helper"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${YELLOW}⚠️  doctl CLI not found${NC}"
    echo "Installing doctl..."

    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install doctl
        else
            echo -e "${RED}❌ Homebrew not found. Please install from: https://brew.sh${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        cd ~
        wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
        tar xf doctl-1.104.0-linux-amd64.tar.gz
        sudo mv doctl /usr/local/bin
        rm doctl-1.104.0-linux-amd64.tar.gz
    else
        echo -e "${RED}❌ Unsupported OS. Please install doctl manually: https://docs.digitalocean.com/reference/doctl/how-to/install/${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ doctl is installed${NC}"
echo ""

# Check if authenticated
if ! doctl auth list &> /dev/null; then
    echo -e "${YELLOW}🔑 Please authenticate with DigitalOcean${NC}"
    echo ""
    echo "Steps:"
    echo "1. Go to: https://cloud.digitalocean.com/account/api/tokens"
    echo "2. Generate New Token (name it 'secondbrain-deploy')"
    echo "3. Copy the token"
    echo ""
    read -p "Paste your DigitalOcean API token: " DO_TOKEN
    doctl auth init --access-token "$DO_TOKEN"
    echo -e "${GREEN}✅ Authenticated!${NC}"
else
    echo -e "${GREEN}✅ Already authenticated with DigitalOcean${NC}"
fi
echo ""

# Generate SECRET_KEY
echo "🔐 Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "${GREEN}✅ SECRET_KEY generated${NC}"
echo ""

# Get GitHub info
echo "📝 Repository Configuration"
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your repository name [secondbrain]: " GITHUB_REPO
GITHUB_REPO=${GITHUB_REPO:-secondbrain}
echo ""

# Get GitHub Pages URL
GITHUB_PAGES="https://${GITHUB_USER}.github.io"
echo "Your GitHub Pages URL will be: $GITHUB_PAGES"
echo ""

# Optional: OpenAI API Key
read -p "Do you have an OpenAI API key? (y/n) [n]: " HAS_OPENAI
HAS_OPENAI=${HAS_OPENAI:-n}
if [[ "$HAS_OPENAI" == "y" ]]; then
    read -p "Enter your OpenAI API key: " OPENAI_KEY
else
    OPENAI_KEY=""
    echo "ℹ️  You can add OpenAI key later in app settings"
fi
echo ""

# Update app.yaml with user's info
echo "📝 Updating deployment configuration..."
sed -i.bak "s|YOUR_GITHUB_USERNAME/YOUR_REPO_NAME|${GITHUB_USER}/${GITHUB_REPO}|g" .do/app.yaml
sed -i.bak "s|YOUR_GITHUB_USERNAME|${GITHUB_USER}|g" .do/app.yaml
rm .do/app.yaml.bak
echo -e "${GREEN}✅ Configuration updated${NC}"
echo ""

# Create app
echo "🚀 Creating DigitalOcean App..."
echo "This will:"
echo "  1. Create a PostgreSQL database"
echo "  2. Deploy your FastAPI backend"
echo "  3. Set up automatic deployments from GitHub"
echo ""
read -p "Continue? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Create the app
APP_ID=$(doctl apps create --spec .do/app.yaml --format ID --no-header)
echo -e "${GREEN}✅ App created! App ID: $APP_ID${NC}"
echo ""

# Set secrets
echo "🔐 Setting environment secrets..."
doctl apps update "$APP_ID" --spec .do/app.yaml
doctl apps update "$APP_ID" --env "SECRET_KEY=$SECRET_KEY"
if [[ -n "$OPENAI_KEY" ]]; then
    doctl apps update "$APP_ID" --env "OPENAI_API_KEY=$OPENAI_KEY"
fi
echo -e "${GREEN}✅ Secrets configured${NC}"
echo ""

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
echo "This can take 5-10 minutes..."
doctl apps create-deployment "$APP_ID" --wait

# Get app URL
APP_URL=$(doctl apps get "$APP_ID" --format LiveURL --no-header)
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo "Backend API: $APP_URL"
echo "Health Check: ${APP_URL}/api/healthz"
echo "API Docs: ${APP_URL}/api/docs"
echo ""
echo "Next Steps:"
echo "1. Visit $APP_URL to verify backend is running"
echo "2. Set GitHub Secret for frontend:"
echo "   - Go to: https://github.com/${GITHUB_USER}/${GITHUB_REPO}/settings/secrets/actions"
echo "   - Add secret: VITE_API_URL = $APP_URL"
echo "3. Push to main branch to deploy frontend"
echo ""
echo "Dashboard: https://cloud.digitalocean.com/apps/$APP_ID"
echo ""
