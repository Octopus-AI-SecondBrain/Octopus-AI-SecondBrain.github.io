# SecondBrain - Local Neural Knowledge Map

A powerful neural knowledge mapping application with 3D visualization, secure authentication, and local hosting for personal use.

## Features

- **3D Neural Map Visualization**: Immersive 3D network visualization with different node types (spheres, octahedrons, dodecahedrons, icosahedrons)
- **Secure Authentication**: JWT-based authentication with rate limiting and input validation
- **Apple Notes Import**: Bulk import from Apple Notes export files with intelligent parsing
- **Real-time Search**: Vector-based semantic search across your knowledge base
- **Performance Optimized**: Handles large datasets with efficient rendering and memory management
- **Security Hardened**: CORS protection, rate limiting, input validation, and security headers

## Quick Start

### Automated Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd secondbrain
   ./scripts/setup.sh
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env - IMPORTANT: Change SECRET_KEY for production!
   # Generate secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Start Application**:
   ```bash
   ./scripts/start.sh
   # This will initialize the database and start the server
   ```

4. **Access Application**:
   - Backend API: http://localhost:8000
   - Frontend: Open `frontend/index.html` in browser
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
   # Run database migrations (for now, this creates tables)
   python -c "from backend.models.db import Base, engine, ensure_sqlite_schema; Base.metadata.create_all(bind=engine); ensure_sqlite_schema()"
   
   # TODO: When Alembic is set up, use: alembic upgrade head
   ```

5. **Start Backend**:
   ```bash
   export PYTHONPATH=$(pwd)
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Configuration

### Environment Variables

All configuration is managed through environment variables (see `.env.example`):

**Required for Production:**
- `SECRET_KEY`: JWT signing key (min 32 chars, use `secrets.token_urlsafe(32)`)
- `ENVIRONMENT`: Set to `production` for production deployments
- `ENABLE_HTTPS`: Set to `true` when using HTTPS (enables HSTS)
- `DATABASE_URL`: PostgreSQL connection string recommended for production

**Optional:**
- `OPENAI_API_KEY`: For enhanced embeddings (falls back to local hashing)
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Legacy Environment Variables

For backward compatibility, the following are still supported:
- `SECONDBRAIN_DB_URL`: Overrides `DATABASE_URL`
- `SECONDBRAIN_CHROMA_PATH`: Overrides `CHROMA_PATH`

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

- **Rate Limiting**: Login (10/min), Signup (5/min)
- **Input Validation**: Username/password requirements
- **CORS Protection**: Restricted origins
- **Security Headers**: XSS, clickjacking, content-type protection
- **JWT Authentication**: Secure token-based sessions

## Performance

- **Smart Rendering**: Limits to 1000 nodes, 2000 edges for optimal performance
- **Memory Management**: Automatic geometry/material disposal
- **Object Pooling**: Efficient mesh reuse
- **Progressive Loading**: Batch import with progress tracking

## API Endpoints

- `POST /auth/signup` - Create account
- `POST /auth/token` - Login
- `GET /auth/me` - Get current user
- `POST /notes/` - Create note
- `GET /notes/` - List notes
- `GET /map/` - Get neural map data
- `POST /search` - Search notes

## Development

## Project Structure

```
secondbrain/
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── backend/                      # Python FastAPI backend
│   ├── main.py                   # Application entry point
│   ├── config/
│   │   └── settings.py           # Configuration settings
│   ├── core/
│   │   ├── security.py           # JWT and password handling
│   │   └── embeddings.py         # Text embeddings
│   ├── models/
│   │   ├── db.py                 # Database configuration
│   │   ├── user.py               # User model
│   │   └── note.py               # Note model
│   ├── routes/
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── notes.py              # Note CRUD operations
│   │   ├── search.py             # Search functionality
│   │   └── map.py                # Neural map data
│   └── services/
│       └── vector_store.py       # Vector database operations
├── frontend/                     # Web frontend
│   ├── index.html                # Main application
│   └── assets/
│       ├── css/
│       │   └── styles.css        # Application styling
│       ├── js/
│       │   ├── app.js            # Core application logic
│       │   ├── auth.js           # Authentication handling
│       │   └── config.js         # Frontend configuration
│       └── libs/
│           └── cytoscape.min.js  # Graph visualization library
├── data/                         # Data storage
│   ├── database/                 # SQLite database
│   └── vector_db/                # ChromaDB vector store
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Initial setup script
│   ├── start.sh                  # Application startup
│   └── demo/                     # Demo data scripts
├── tests/                        # Test files
└── docs/                         # Additional documentation
```

## Troubleshooting

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