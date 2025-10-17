# 🐙 Octopus – Your AI Second Brain

A modern, production-ready neural knowledge mapping application with 3D visualization, semantic search, and beautiful UI.

> **Note**: This project has been completely refactored! See [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) and [GETTING_STARTED.md](GETTING_STARTED.md) for the new architecture.

## 🚀 Quick Start

⚠️ **IMPORTANT**: You must run database migrations before starting the application!

```bash
# Backend Setup (FastAPI)
cd /path/to/secondbrain
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# REQUIRED: Run database migrations first
alembic upgrade head

# Start backend on port 8000
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Frontend Setup (React + Vite + Tailwind) - in another terminal
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env

# Start frontend (defaults to port 5173)
npm run dev
```

**Visit**: The frontend will show the URL (typically http://localhost:5173)

## 🚀 Production Deployment

This application is ready for production deployment with:

- **Frontend**: GitHub Pages (automatic deployment from main branch)
- **Backend**: Render.com (managed PostgreSQL, auto-deploy, free tier available)

**📖 [Complete Deployment Guide](DEPLOYMENT.md)** - Step-by-step instructions for deploying to production.

**Quick Deploy Summary**:
1. **Frontend**: Push to GitHub → automatic GitHub Pages deployment
2. **Backend**: Connect GitHub repo to Render.com → automatic deployments
3. **Database**: Use Render's managed PostgreSQL
4. **Environment**: Set required environment variables (SECRET_KEY, DATABASE_URL, OPENAI_API_KEY)

**Live Demo**: `https://octopus-ai-secondbrain.github.io/Octopus-AI-SecondBrain.github.io/` (after deployment)

**CORS Configuration**: The backend is pre-configured to accept requests from common development ports:
- `3000`, `8080` (Create React App, various dev servers)
- `5173`, `4173` (Vite default ports)
- Both `localhost` and `127.0.0.1` variants
- Production GitHub Pages origin

To use a custom port, set the `CORS_ORIGINS` environment variable:
```bash
export CORS_ORIGINS="http://localhost:3001,http://127.0.0.1:3001"
# Or in .env file:
# CORS_ORIGINS=http://localhost:3001,http://127.0.0.1:3001
```

## Features

- **3D Neural Map Visualization**: Immersive 3D network visualization with different node types (spheres, octahedrons, dodecahedrons, icosahedrons)
- **Secure Authentication**: JWT-based authentication with httpOnly cookies, rate limiting, and input validation
- **Vector Semantic Search**: ChromaDB-powered vector search for finding related notes
- **Real-time Search**: Vector-based semantic search across your knowledge base
- **Performance Optimized**: Handles large datasets with efficient rendering and memory management
- **Security Hardened**: CORS protection, rate limiting, input validation, security headers, and cookie-based auth
- **Database Migrations**: Alembic-managed schema evolution for safe production deployments

## Quick Start

### Automated Setup (Recommended)

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd secondbrain
   chmod +x scripts/*.sh
   ./scripts/setup.sh
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env - IMPORTANT: Change SECRET_KEY for production!
   # Generate secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
   # For production: Set ENVIRONMENT=production and ENABLE_HTTPS=true
   ```

3. **Start Application**:
   ```bash
   ./scripts/start.sh
   # This will:
   # - Activate virtual environment
   # - Run Alembic database migrations
   # - Start the FastAPI server
   ```

4. **Access Application**:
   - Backend API: http://localhost:8000
   - Frontend: Open `index.html` in your browser
   - API Documentation: http://localhost:8000/docs (development only)

### Manual Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   # CRITICAL: Set a strong SECRET_KEY (min 32 characters)
   # For production: Set ENVIRONMENT=production and ENABLE_HTTPS=true
   ```

4. **Initialize Database**:
   ```bash
   # CRITICAL: Run Alembic migrations to create tables - required before starting the app!
   alembic upgrade head
   ```

5. **Start Backend**:
   ```bash
   export PYTHONPATH=$(pwd)
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup (Alternative)

Use Docker Compose for a complete environment with PostgreSQL:

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services (backend, postgres, frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Services:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

## Configuration

### Environment Variables

All configuration is managed through environment variables (see `.env.example`):

**Required for Production:**
- `SECRET_KEY`: JWT signing key (min 32 chars, use `secrets.token_urlsafe(32)`)
- `ENVIRONMENT`: Set to `production` for production deployments (enforces SECRET_KEY requirement)
- `ENABLE_HTTPS`: Set to `true` when using HTTPS (enables HSTS headers)
- `DATABASE_URL`: PostgreSQL connection string recommended for production

**Authentication:**
- JWTs are stored in secure, httpOnly cookies (not localStorage)
- Cookies are marked as `secure` in production with HTTPS enabled
- `SameSite=Lax` for CSRF protection
- Token expiration configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30)

**Optional:**
- `OPENAI_API_KEY`: For OpenAI embeddings (recommended for better semantic search)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (defaults include common dev ports: 3000, 5173, 4173, 8080)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `CHROMA_PATH`: Vector database storage path (default: ./data/vector_db)

### Database Migrations

⚠️ **CRITICAL**: Always run migrations before starting the application!

This project uses Alembic for database schema management:

```bash
# REQUIRED: Run migrations before starting the app
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

**Important Notes:**
- The application will fail to start properly without running migrations first
- Never use `Base.metadata.create_all()` in production. Always use Alembic migrations
- The startup health check will detect missing migrations and warn about schema issues
- Use `scripts/start.sh` which automatically runs migrations before starting the server

## Usage

### Authentication
1. Create an account or log in
2. The app will remember your session with secure JWT tokens

### 3D Visualization
1. Toggle "3D Neural Map" to switch between 2D and 3D views
2. Use mouse to navigate:
   - **Drag**: Rotate view
   - **Scroll**: Zoom in/out
   - **Double-click**: Focus on node
   - **Hover**: View node details

### Import Notes
1. **Apple Notes**: Export from Apple Notes app as .txt files and select them
2. **Bulk Text**: Paste multiple notes separated by `---`
3. **Supported formats**: .txt, .md, .rtf, .csv, .json

### Node Types
- **Sphere (Blue)**: Regular notes
- **Octahedron (Purple)**: Concepts and ideas  
- **Dodecahedron (Green)**: Topics and categories
- **Icosahedron (Orange)**: Important/highlighted content

## Security Features

- **Cookie-Based Authentication**: JWTs stored in secure, httpOnly cookies (immune to XSS attacks)
- **Rate Limiting**: Login (10/min), Signup (5/min), configurable per endpoint
- **Input Validation**: Pydantic schemas with password complexity requirements
- **CORS Protection**: Configurable allowed origins
- **Security Headers**: XSS, clickjacking, content-type protection, conditional HSTS
- **Password Security**: Bcrypt hashing with salt
- **Environment-Based Security**: Enforces strong SECRET_KEY in non-development environments

## Performance

- **Smart Rendering**: Limits to 1000 nodes, 2000 edges for optimal performance
- **Memory Management**: Automatic geometry/material disposal
- **Object Pooling**: Efficient mesh reuse
- **Progressive Loading**: Batch import with progress tracking

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/token` - Login (sets httpOnly cookie)
- `POST /auth/logout` - Logout (clears cookie)
- `GET /auth/me` - Get current user info

### Notes
- `POST /notes/` - Create note
- `GET /notes/` - List user's notes
- `GET /notes/{id}` - Get specific note
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note

### Map & Search
- `GET /map/` - Get neural map data with similarity edges
- `POST /search/` - Semantic search across notes

All authenticated endpoints require a valid session cookie (automatically handled by the browser).

## Development

## Project Structure

```
secondbrain/
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── docker-compose.yml            # Docker orchestration
├── nginx.conf                    # Nginx configuration for Docker
├── alembic.ini                   # Alembic configuration
├── alembic/                      # Database migrations
│   ├── env.py                    # Migration environment
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration scripts
│       └── 001_initial_schema.py # Initial schema
├── config/
│   └── local.env                 # Local development settings
├── backend/                      # Python FastAPI backend
│   ├── main.py                   # Application entry point
│   ├── config/
│   │   └── config.py             # Pydantic settings with validation
│   ├── core/
│   │   ├── security.py           # JWT and password handling
│   │   ├── embeddings.py         # Text embeddings
│   │   └── logging.py            # Structured logging
│   ├── models/
│   │   ├── db.py                 # Database configuration
│   │   ├── user.py               # User model
│   │   └── note.py               # Note model
│   ├── routes/
│   │   ├── auth.py               # Authentication endpoints (cookie-based)
│   │   ├── notes.py              # Note CRUD operations
│   │   ├── search.py             # Search functionality
│   │   └── map.py                # Neural map data
│   └── services/
│       └── vector_store.py       # Thread-safe ChromaDB operations
├── assets/                       # Frontend assets
│   ├── css/
│   │   └── styles.css            # Application styling
│   ├── js/
│   │   ├── app.js                # Core app (cookie-based auth)
│   │   ├── auth.js               # Authentication (no localStorage)
│   │   └── config.js             # Frontend configuration
│   └── libs/
│       └── cytoscape.min.js      # Graph visualization library
├── data/                         # Data storage (gitignored)
│   ├── database/                 # SQLite database
│   └── vector_db/                # ChromaDB vector store
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Initial setup script
│   ├── start.sh                  # Application startup with migrations
│   └── demo/                     # Demo data scripts
├── tests/                        # Test files
│   └── test_app.py               # API tests
└── docs/                         # Additional documentation
    ├── api.md                    # API documentation
    ├── development.md            # Development guide
    └── PROFESSIONAL_GUIDELINES.md # Professional practices
```

## Troubleshooting

### CORS / Network Errors
- **"Cannot reach server"** or **"Network Error"**: Usually a CORS issue
- Check that the backend is running on port 8000: `curl http://localhost:8000/health`
- Verify your frontend dev server port is in the CORS allowlist (3000, 5173, 4173, 8080 by default)
- For custom ports, set `CORS_ORIGINS`: `export CORS_ORIGINS="http://localhost:YOURPORT"`
- Restart the backend after changing CORS settings

### Database / Migration Errors
- **"Database not properly initialized"**: Run `alembic upgrade head` before starting the backend
- **503 errors on signup/login**: Usually means migrations haven't been run
- Check that the `data/database/` directory exists and is writable

### 3D Visualization Not Loading
- Check browser console for Three.js errors
- Ensure modern browser with WebGL support
- Try toggling 3D mode off and on

### Authentication Issues
- Verify backend is running on port 8000
- Check browser network tab for API errors
- Clear browser storage and try again

### Performance Issues
- Use filters to limit nodes displayed
- Switch to 2D mode for large datasets
- Close other browser tabs to free memory

## Scripts

- `./scripts/setup.sh` - Initial project setup
- `./scripts/start.sh` - Start the backend server
- `./scripts/serve-frontend.sh` - Serve frontend files locally

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes following the project structure
4. Add tests for new functionality
5. Update documentation as needed
6. Submit pull request

## Documentation

- [API Documentation](docs/api.md) - REST API endpoints
- [Development Guide](docs/development.md) - Development workflow and guidelines

## License

MIT License - see LICENSE file for details.