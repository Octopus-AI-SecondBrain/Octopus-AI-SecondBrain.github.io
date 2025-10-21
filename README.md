# 🐙 SecondBrain – Your AI Knowledge Hub

> A modern, production-ready neural knowledge mapping application with 3D visualization, semantic search, and secure authentication. Built with FastAPI + React.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://octopus-ai-secondbrain.github.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

## 🌐 Live Demo

- **Landing Page**: [https://octopus-ai-secondbrain.github.io](https://octopus-ai-secondbrain.github.io)
- **Join Beta**: [Sign up here](https://forms.gle/wz51dsAm3vmePibr6) to get early access!

## ✨ Key Features

### 🧠 Knowledge Management
- **Rich Text Editor** with formatting (bold, italic, lists, headings, code blocks)
- **Bulk Import** - Import multiple notes at once with auto-tag extraction
- **Smart Tags** - Automatic hashtag detection and organization
- **Full CRUD** - Create, read, update, delete notes with validation

### 🔍 AI-Powered Search
- **Semantic Search** - Find notes by meaning, not just keywords
- **Vector Embeddings** - Powered by OpenAI or local Sentence Transformers
- **Smart Ranking** - Results sorted by relevance with similarity scores
- **Hybrid Fallback** - Automatic keyword search when embeddings unavailable

### 🗺️ 3D Neural Map
- **2D/3D Toggle** - Switch between canvas and WebGL visualization
- **Custom Layouts** - Tree, radial, planetary, and force-directed
- **Interactive** - Drag nodes, zoom, pan, rotate (3D)
- **Semantic Connections** - Links based on content similarity
- **Tag Filtering** - Focus on specific topics
- **Node Scaling** - Size reflects number of connections
- **Smart Spacing** - Advanced collision detection prevents overlap

### 🎨 Modern UI
- **Light & Dark Mode** - Seamless theme switching
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Keyboard Shortcuts** - Vim-style navigation (j/k/n/s/m)
- **Theme Persistence** - Preferences saved across sessions
- **Accessibility** - Respects `prefers-reduced-motion`

### 📊 Analytics
- **Real-time Stats** - Note counts, word counts, weekly activity
- **Embedding Coverage** - Track search readiness
- **Knowledge Graph** - Visual connection statistics
- **Health Monitoring** - System status indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io.git
cd Octopus-AI-SecondBrain.github.io
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional but recommended)

# Run database migrations
alembic upgrade head

# Start backend
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Open Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### Creating Notes
1. Click "New Note" or press `n`
2. Write in the rich text editor
3. Add tags using #hashtag format
4. Save to see connections in Neural Map

### Bulk Import
1. Click "Bulk Import" button
2. Paste multiple notes separated by `---`
3. Preview and import all at once
4. Demo data available in `demo_notes_bulk_import.txt`

### Neural Map
1. Navigate to Neural Map page
2. Toggle 2D/3D view
3. Apply custom layouts (tree, radial, planetary)
4. Filter by tags
5. Adjust similarity threshold
6. Click nodes to view/edit notes

### Search
1. Press `s` or click search icon
2. Type your query
3. Get semantic results ranked by relevance
4. Click results to open notes

### Keyboard Shortcuts
- `j` - Next note
- `k` - Previous note  
- `n` - New note
- `s` - Focus search
- `m` - Go to Neural Map
- `?` - Show all shortcuts

## 🏗️ Tech Stack

### Frontend
- **React 18.3** - UI framework
- **Vite 5** - Build tool
- **TailwindCSS 3.4** - Styling
- **react-force-graph** - Graph visualization
- **Three.js** - 3D rendering
- **TipTap** - Rich text editor
- **Framer Motion** - Animations

### Backend
- **FastAPI** - Python web framework
- **SQLite** - Primary database
- **ChromaDB** - Vector database
- **OpenAI API** - Embeddings (optional)
- **Sentence Transformers** - Local embeddings (fallback)
- **Alembic** - Database migrations
- **Pydantic** - Data validation

## 🚀 Deployment

### GitHub Pages (Landing Page)
```bash
# Automatic deployment via GitHub Actions
git add .
git commit -m "Deploy"
git push origin main

# Enable GitHub Pages in Settings → Pages
# Source: gh-pages branch
```

### Render.com (Backend + Database)
1. Sign up at [render.com](https://render.com)
2. Create PostgreSQL database
3. Create Web Service from GitHub
4. Add environment variables
5. Deploy!

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.**

## 📁 Project Structure

```
.
├── backend/           # FastAPI backend
│   ├── main.py       # App entry point
│   ├── config/       # Configuration
│   ├── core/         # Core utilities (embeddings, security)
│   ├── models/       # Database models
│   ├── routes/       # API endpoints
│   └── services/     # Business logic
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── context/     # React context
│   │   ├── hooks/       # Custom hooks
│   │   └── utils/       # Utilities
│   └── public/
├── docs/             # GitHub Pages landing page
│   ├── index.html    # Landing page
│   ├── styles.css    # Styling
│   └── script.js     # Interactions
├── alembic/          # Database migrations
├── scripts/          # Utility scripts
├── tests/            # Test files
└── data/             # Local data (gitignored)
```

## 🎨 Features in Detail

### Bulk Import
Import multiple notes efficiently:
- Paste text with `---` separators
- Automatic hashtag extraction
- Preview before importing
- Batch processing

### Neural Map Layouts
- **Force-Directed**: Natural clustering by similarity
- **Tree**: Hierarchical organization
- **Radial**: Circular arrangement
- **Planetary**: Solar system-style layout

### 3D Visualization
- WebGL-powered rendering
- Smooth camera controls
- Node glow effects
- Dynamic link width based on similarity
- Optimized for hundreds of nodes

### Search Quality
- **With OpenAI**: True semantic search, understands context
- **Without OpenAI**: Sentence Transformers (free, local)
- **Fallback**: Keyword-based search always available

## 🔧 Configuration

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=sqlite:///./data/database/secondbrain.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...  # Optional but recommended
ENVIRONMENT=development

# Frontend (.env.development)
VITE_API_URL=http://localhost:8000/api
```

### OpenAI Setup (Optional)
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add $5 credit (costs ~$0.10-0.20/month)
3. Add to backend `.env`
4. Restart backend

**Alternative**: Use free Sentence Transformers (see docs)

## 📊 Performance

- **Frontend**: <2s initial load, <100ms page transitions
- **Backend**: <100ms API response time
- **3D Map**: Handles 500+ nodes smoothly
- **Search**: <200ms for semantic queries

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Quick reference
- [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) - Architecture diagrams
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run migrations
alembic upgrade head
```

### Frontend shows CORS errors
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `.env.development`
- Restart both frontend and backend

### Search not working
- Add OpenAI API key to `.env`
- Or install Sentence Transformers: `pip install sentence-transformers`
- Keyword search always works as fallback

### 3D Map is slow
- Reduce node count with filters
- Switch to 2D mode
- Adjust similarity threshold
- Close other browser tabs

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://reactjs.org/) - Frontend framework
- [Three.js](https://threejs.org/) - 3D graphics
- [react-force-graph](https://github.com/vasturiano/react-force-graph) - Graph visualization
- [TipTap](https://tiptap.dev/) - Rich text editor
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - Embeddings API

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/issues)
- **Beta Signup**: [Join Waitlist](https://forms.gle/wz51dsAm3vmePibr6)
- **Discussions**: [GitHub Discussions](https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io/discussions)

---

**Made with ❤️ by the Octopus SecondBrain Team**

[⬆ back to top](#-secondbrain--your-ai-knowledge-hub)


## ✨ Features

### 🧠 Knowledge Management
- **Rich Text Editor**: TipTap-powered WYSIWYG editor with formatting tools (bold, italic, lists, headings, code blocks)
- **Full CRUD Operations**: Create, read, update, and delete notes with validation
- **Note Detail View**: Click to expand notes in a modal with full formatting
- **Auto-save**: Inline validation prevents empty notes from being saved
- **HTML Persistence**: Rich formatting stored as HTML, displayed beautifully

### 🔍 Advanced Search
- **Semantic Search**: Vector-based similarity search powered by ChromaDB embeddings
- **AI-Powered Explanations**: LLM summarization of search results (optional OpenAI integration)
- **Search Highlighting**: Highlighted matched terms in results with relevance scores
- **Hybrid Search**: Automatic fallback to keyword search when vector embeddings unavailable
- **Search Method Indicators**: Visual badges show whether results used semantic or keyword matching

### 🗺️ Neural Map Visualization
- **2D/3D Rendering**: Toggle between 2D canvas and 3D WebGL visualization modes
- **Semantic Similarity**: Uses vector embeddings (cosine similarity) for true semantic connections
- **Tag-Based Filtering**: Multi-select tag filters to focus on specific topics
- **Smart Fallback**: Automatic keyword-based similarity when embeddings unavailable
- **Interactive Controls**: Adjust similarity thresholds, connections per node, max nodes, isolate visibility
- **Glow Effects**: Emissive materials and outer glow spheres on connected nodes (respects prefers-reduced-motion)
- **Rich Metadata**: Each node displays tags, timestamps, connection counts, and content previews
- **Event Integration**: Click nodes to open notes, receive focus events from Notes/Search pages
- **Real-time Statistics**: View avg degree, similarity range, isolated nodes, embedding coverage
- **Performance Optimized**: AbortController prevents request stacking, handles hundreds of notes smoothly

### 📊 Analytics Dashboard
- **Real-time Statistics**: Live note counts, total words, weekly activity
- **Search Readiness**: Track embedding coverage across your knowledge base
- **Knowledge Graph Status**: See at-a-glance if your neural map is ready
- **System Health**: Integrated health monitoring with status indicators

### 🎨 Theming & Visual Design
- **Light & Dark Mode**: First-class support for both themes with seamless switching
- **Theme Persistence**: User preference saved to localStorage and restored on reload
- **System Preference**: Respects `prefers-color-scheme` on first visit
- **CSS Variables**: Entire UI uses CSS custom properties for consistent theming
- **Neon Glow Effects**: Buttons, cards, pills, and navigation use brand-colored glows
- **Reduced Motion**: Respects `prefers-reduced-motion` for accessibility
- **Brand Colors**: Consistent use of primary (#F24D80), secondary (#A855F7), accent (#FF8F3C)
- **Smooth Transitions**: All theme switches are instant without flash or flicker

### ⚙️ Settings & Customization
- **Profile Management**: Update email address and password through Settings
- **Backend Integration**: Profile updates persist to database with validation
- **API Key Storage**: Securely store OpenAI API key locally for AI features
- **Theme Toggle**: Switch between light and dark themes instantly
- **Animated Background**: Optional neural network background effects

### 🎛️ System Reliability  
- **Resilient Architecture**: Note operations succeed even when vector store fails
- **Health Monitoring**: Real-time system health indicators with component status
- **Graceful Degradation**: Features work with reduced functionality when services are down
- **Error Recovery**: Automatic retry and fallback mechanisms
- **Clean Session Management**: Never leaves database in inconsistent state

### 🔐 Security & Authentication
- **JWT Cookie Authentication**: Secure session management with HTTP-only cookies
- **Email-Based Signup**: Email collection for account recovery and future features
- **Return-Value Auth Pattern**: Login/signup return explicit success/user objects
- **Rate Limiting**: Protection against abuse with intelligent rate limiting
- **Password Security**: Strong password requirements with validation
- **CORS & Security Headers**: Production-grade security configuration

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+  
- Git

### Local Development (Easy Mode)

The simplest way to run SecondBrain locally:

```bash
# 1. Clone repository
git clone https://github.com/Octopus-AI-SecondBrain/Octopus-AI-SecondBrain.github.io.git
cd Octopus-AI-SecondBrain.github.io

# 2. Run the local development script
./run_local.sh
```

The script automatically:
- Creates/activates Python virtual environment
- Installs backend dependencies
- Runs database migrations
- Starts backend server (port 8001)
- Installs frontend dependencies
- Starts frontend dev server (port 5173)
- Handles Ctrl+C gracefully to stop both servers

### Manual Development Setup

For more control, run backend and frontend separately:

```bash
# Backend (Terminal 1)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

# Frontend (Terminal 2)
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8001" > .env.local
npm run dev
```

Access the application at `http://localhost:5173` (frontend) with backend at `http://localhost:8001`.

## 🔧 Environment Configuration

### Required Variables

#### Backend (.env)
```bash
# Core Configuration
SECRET_KEY=your-secret-key-min-32-chars-long
DATABASE_URL=sqlite:///./data/database/secondbrain.db
ENVIRONMENT=development

# Vector Store
CHROMA_PATH=./data/vector_db

# Optional: AI Features
OPENAI_API_KEY=sk-...  # Enables LLM-powered search explanations

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-domain.com
```

#### Frontend (.env.local)
```bash
# API Connection
VITE_API_URL=http://localhost:8000  # For local development
# VITE_API_URL=https://your-backend.render.com  # For production
```

### Feature Configuration

#### AI-Powered Search Explanations
- Set `OPENAI_API_KEY` in backend .env OR in Settings page (stored locally)
- Enables LLM summarization of search results via /search/explain endpoint
- Without API key, provides rule-based explanations as fallback
- Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)

#### Vector Embeddings & Semantic Similarity
- **Automatic Generation**: Embeddings created for every note (with or without OpenAI key)
- **Hashed Fallback**: When OpenAI unavailable, uses hash-based embeddings for consistency
- **Cosine Similarity**: Neural map uses true semantic similarity via vector math
- **Tag Boost**: Shared tags add bonus similarity (up to +0.15) to connections
- **Coverage Tracking**: View embedding coverage percentage in neural map stats
- **Graceful Degradation**: Falls back to keyword/tag matching if embeddings fail
- **No Blocking**: Note CRUD operations succeed even when vector store is down

#### Rich Text Editor
- **TipTap Editor**: WYSIWYG editor with toolbar for formatting
- **Supported Formats**: Bold, italic, headings, lists, blockquotes, code, horizontal rules
- **HTML Storage**: Content persisted as HTML in database
- **Validation**: Inline errors prevent saving empty titles or content
- **Accessibility**: Keyboard shortcuts and ARIA labels

#### Analytics Dashboard
- Real-time statistics automatically enabled
- Tracks: total notes, word count, weekly activity, embedding coverage
- Data refreshes on each dashboard visit
- No backend configuration required

#### Neural Map Visualization
- **2D/3D Toggle**: Switch between canvas-based 2D and WebGL 3D rendering
- **Similarity Controls**: Min similarity threshold, connections per node (top-K), max nodes
- **Tag Filtering**: Multi-select tags to focus on specific topics
- **Visual Effects**: Emissive glow on connected nodes (respects prefers-reduced-motion)
- **Accessibility**: Keyboard-accessible controls, detail drawer for selected nodes
- **Statistics**: Real-time metrics including avg degree, similarity range, embedding coverage
- **Event Integration**: Nodes sync with Notes/Search pages via custom events
- **Settings Persistence**: Controls saved per session, no backend config needed

**Access Application:**
- Frontend: http://localhost:5173 (or displayed URL)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (dev only)

## 🌐 Production Deployment

### Architecture
- **Frontend**: React SPA deployed to GitHub Pages  
- **Backend**: FastAPI deployed to Render.com
- **Database**: Render PostgreSQL (managed)
- **Auth**: Secure cross-origin cookies

### Deploy to Production

**📖 [Complete Deployment Guide](DEPLOYMENT.md)**

**Quick Setup:**

1. **Backend (Render.com)**:
   - Connect GitHub repo to Render
   - Create PostgreSQL database
   - Set environment variables: `DATABASE_URL`, `SECRET_KEY`, `GITHUB_PAGES_URL`
   - Deploy automatically from `main` branch

2. **Frontend (GitHub Pages)**:
   - Set repository secret: `VITE_API_URL` (your Render URL)
   - Push to `main` → automatic deployment
   - Access at: `https://username.github.io/repo-name/`

3. **Environment Variables**:
   ```bash
   # Render Backend (required)
   SECRET_KEY="your-32-char-secret-key"
   DATABASE_URL="postgresql://user:pass@host:port/db"  # Auto-provided by Render
   ENVIRONMENT="production"
   ENABLE_HTTPS="true"
   GITHUB_PAGES_URL="https://username.github.io"
   
   # GitHub Pages Frontend (repository secret)
   VITE_API_URL="https://your-app.onrender.com"
   ```

**CORS Configuration**: The backend is pre-configured to accept requests from common development ports:
- `3000`, `8080` (Create React App, various dev servers)
- `5173`, `4173` (Vite default ports)
- Both `localhost` and `127.0.0.1` variants
- Production GitHub Pages origin

**Important**: Use **host origins only** (e.g., `https://example.com`), not paths (e.g., ~~`https://example.com/path`~~). Browsers reject path-based origins.

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
- `SameSite=None` when HTTPS enabled (for cross-origin GitHub Pages → Render), `Lax` for development
- Token expiration configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30)

**Optional:**
- `OPENAI_API_KEY`: For OpenAI embeddings (recommended for better semantic search)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (defaults include common dev ports: 3000, 5173, 4173, 8080). **Use host URLs only, no path segments** (e.g., `https://example.com` not `https://example.com/path`)
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

## 🚀 Production Deployment

### Quick Deploy (15 minutes)

Deploy your own instance for **$0/month** using free tiers:

1. **Backend**: Render.com (PostgreSQL + FastAPI)
2. **Frontend**: GitHub Pages (Landing page + React app)
3. **Beta Signups**: Formspree (50/month free)

```bash
# 1. Deploy backend to Render.com
# See DEPLOYMENT_GUIDE.md for detailed steps

# 2. Update URLs
# Edit: docs/index.html, frontend/src/utils/api.js, backend/main.py

# 3. Deploy to GitHub Pages
git add .
git commit -m "Deploy to production"
git push origin main

# 4. Enable GitHub Pages
# Settings → Pages → Deploy from gh-pages branch
```

**Complete Documentation**:
- 📖 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment instructions
- ✅ [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Quick reference checklist
- 🎉 [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) - What's included in deployment package

**Features Included**:
- Professional landing page with animated neural map
- Beta signup form with email collection
- Demo video section (ready for YouTube embed)
- Auto-deployment via GitHub Actions
- Free hosting with 99.9% uptime

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
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions

## License

MIT License - see LICENSE file for details.