#!/bin/bash
# Google Cloud Run Deployment Script for SecondBrain

set -e

echo "🚀 Google Cloud Run SecondBrain Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found${NC}"
    echo ""
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "Quick install:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  curl https://sdk.cloud.google.com | bash"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  curl https://sdk.cloud.google.com | bash"
    fi
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI is installed${NC}"
echo ""

# Authenticate
echo "🔑 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q @; then
    echo -e "${YELLOW}Please authenticate with Google Cloud${NC}"
    gcloud auth login
fi
echo -e "${GREEN}✅ Authenticated${NC}"
echo ""

# Set/select project
echo "📝 Project Configuration"
read -p "Enter your Google Cloud Project ID (or press Enter to create new): " PROJECT_ID

if [[ -z "$PROJECT_ID" ]]; then
    echo "Creating new project..."
    read -p "Enter project name [secondbrain]: " PROJECT_NAME
    PROJECT_NAME=${PROJECT_NAME:-secondbrain}
    PROJECT_ID="secondbrain-$(date +%s)"

    gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME"
    echo -e "${GREEN}✅ Project created: $PROJECT_ID${NC}"
fi

gcloud config set project "$PROJECT_ID"
echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"
echo ""

# Enable billing (required for Cloud Run)
echo -e "${YELLOW}⚠️  Please ensure billing is enabled for this project${NC}"
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
read -p "Press Enter when billing is enabled..."
echo ""

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com \
    --project="$PROJECT_ID"
echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# Generate SECRET_KEY
echo "🔐 Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "${GREEN}✅ SECRET_KEY generated${NC}"
echo ""

# Database setup
echo "💾 Database Configuration"
echo ""
echo "Choose database option:"
echo "1) Use Cloud SQL PostgreSQL (Recommended - $7-15/month)"
echo "2) Use external PostgreSQL (ElephantSQL, Supabase, etc.)"
echo ""
read -p "Enter choice [1]: " DB_CHOICE
DB_CHOICE=${DB_CHOICE:-1}

if [[ "$DB_CHOICE" == "1" ]]; then
    echo "Creating Cloud SQL PostgreSQL instance..."
    echo "This will take 5-10 minutes..."

    INSTANCE_NAME="secondbrain-db"

    # Check if instance already exists
    if gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT_ID" &> /dev/null; then
        echo -e "${YELLOW}Instance $INSTANCE_NAME already exists${NC}"
    else
        gcloud sql instances create "$INSTANCE_NAME" \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=us-central1 \
            --project="$PROJECT_ID"
    fi

    # Create database
    gcloud sql databases create secondbrain \
        --instance="$INSTANCE_NAME" \
        --project="$PROJECT_ID" || true

    # Set postgres password
    DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    gcloud sql users set-password postgres \
        --instance="$INSTANCE_NAME" \
        --password="$DB_PASSWORD" \
        --project="$PROJECT_ID"

    # Get connection name
    CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --format="value(connectionName)")

    # Install pgvector extension (requires proxy)
    echo "⚠️  Remember to enable pgvector extension after deployment:"
    echo "  gcloud sql connect $INSTANCE_NAME --user=postgres"
    echo "  Then run: CREATE EXTENSION IF NOT EXISTS vector;"
    echo ""

    DATABASE_URL="postgresql://postgres:${DB_PASSWORD}@localhost/secondbrain?host=/cloudsql/${CONNECTION_NAME}"
    echo -e "${GREEN}✅ Cloud SQL instance created${NC}"

else
    echo "Using external PostgreSQL..."
    read -p "Enter your PostgreSQL connection URL: " DATABASE_URL
fi
echo ""

# GitHub info
echo "📝 Repository Configuration"
GITHUB_REPO=$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/' || echo "")
if [[ -n "$GITHUB_REPO" ]]; then
    echo "Detected repository: $GITHUB_REPO"
    read -p "Use this repository? (y/n) [y]: " USE_REPO
    USE_REPO=${USE_REPO:-y}
    if [[ "$USE_REPO" != "y" ]]; then
        read -p "Enter GitHub username/repo: " GITHUB_REPO
    fi
else
    read -p "Enter GitHub username/repo (e.g., username/secondbrain): " GITHUB_REPO
fi

GITHUB_USER=$(echo "$GITHUB_REPO" | cut -d'/' -f1)
GITHUB_PAGES="https://${GITHUB_USER}.github.io"
echo ""

# Build and deploy
echo "🏗️  Building Docker image..."
SERVICE_NAME="secondbrain-api"
REGION="us-central1"

# Build with Cloud Build
gcloud builds submit \
    --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --project="$PROJECT_ID" \
    --file=infra/Dockerfile.cloudrun \
    .

echo -e "${GREEN}✅ Image built${NC}"
echo ""

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."

# Base deployment command
DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project=$PROJECT_ID \
    --set-env-vars=ENVIRONMENT=production,DEBUG=false,SECRET_KEY=$SECRET_KEY,CORS_ORIGINS=$GITHUB_PAGES,LOG_LEVEL=INFO,ENABLE_HTTPS=true"

# Add database URL
DEPLOY_CMD="$DEPLOY_CMD,DATABASE_URL=$DATABASE_URL"

# Add Cloud SQL connection if using Cloud SQL
if [[ "$DB_CHOICE" == "1" ]]; then
    DEPLOY_CMD="$DEPLOY_CMD --add-cloudsql-instances=$CONNECTION_NAME"
fi

# Execute deployment
eval $DEPLOY_CMD

echo -e "${GREEN}✅ Deployed to Cloud Run${NC}"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

# Run migrations
echo "🔄 Running database migrations..."
gcloud run jobs create migrate-db \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --region $REGION \
    --project=$PROJECT_ID \
    --set-env-vars=DATABASE_URL=$DATABASE_URL \
    --execute-now \
    --wait \
    --command=alembic \
    --args="upgrade,head" || echo "Migration job already exists"

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Backend API: $SERVICE_URL"
echo "Health Check: ${SERVICE_URL}/api/healthz"
echo "API Docs: ${SERVICE_URL}/api/docs"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo ""
if [[ "$DB_CHOICE" == "1" ]]; then
    echo "Database: Cloud SQL ($INSTANCE_NAME)"
    echo "Connection: $CONNECTION_NAME"
    echo ""
    echo "⚠️  IMPORTANT: Enable pgvector extension:"
    echo "  gcloud sql connect $INSTANCE_NAME --user=postgres --project=$PROJECT_ID"
    echo "  Then run: CREATE EXTENSION IF NOT EXISTS vector;"
    echo ""
fi
echo "Next Steps:"
echo "1. Test backend: curl ${SERVICE_URL}/api/healthz"
echo "2. Enable pgvector (if using Cloud SQL)"
echo "3. Set GitHub Secret VITE_API_URL = $SERVICE_URL"
echo "4. Push to deploy frontend"
echo ""
echo "Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""
