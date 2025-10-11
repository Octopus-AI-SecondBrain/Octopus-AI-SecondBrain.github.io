# Development Guide

## Getting Started

1. **Setup Development Environment**:
   ```bash
   ./scripts/setup.sh
   ```

2. **Start Development Server**:
   ```bash
   ./scripts/start.sh
   ```

## Development Workflow

### Backend Development

The backend is built with FastAPI and follows a modular structure:

- `backend/main.py` - Application entry point and middleware setup
- `backend/models/` - Database models and schemas
- `backend/routes/` - API endpoint definitions
- `backend/services/` - Business logic and external service integrations
- `backend/core/` - Core utilities (security, embeddings, etc.)
- `backend/config/` - Configuration management

### Frontend Development

The frontend is a vanilla JavaScript application with:

- `frontend/index.html` - Main application interface
- `frontend/assets/js/` - JavaScript modules
- `frontend/assets/css/` - Styling
- `frontend/assets/libs/` - Third-party libraries

### Database

- SQLite database stored in `data/database/`
- Vector embeddings stored in ChromaDB in `data/vector_db/`
- Database models defined in `backend/models/`

## Testing

Run tests with:
```bash
cd tests
python -m pytest test_app.py
```

## Code Style

- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- Use meaningful variable and function names
- Add comments for complex logic

## Adding New Features

1. Create feature branch
2. Add backend API endpoints in `backend/routes/`
3. Add frontend functionality in `frontend/assets/js/`
4. Update documentation
5. Add tests
6. Submit pull request