# SecondBrain Local Development Troubleshooting

## Quick Setup

1. **Run the application:**
   ```bash
   ./run_local.sh
   ```
   This will start both backend (port 8000) and frontend (port 3001/3000)

2. **Access the application:**
   - Frontend: http://localhost:3001 or http://localhost:3000
   - Backend API: http://localhost:8000  
   - API Documentation: http://localhost:8000/docs

## Common Issues and Fixes

### 1. "Port already in use" errors
**Symptoms:** Backend or frontend won't start due to port conflicts
**Solutions:**
- Kill existing processes: `lsof -ti:8000 | xargs kill -9` (for backend)
- Kill existing processes: `lsof -ti:3000 | xargs kill -9` (for frontend)
- The frontend will automatically try port 3001 if 3000 is busy

### 2. Python/Virtual Environment Issues
**Symptoms:** "python: command not found" or missing packages
**Solutions:**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Database Issues
**Symptoms:** "no such table" or database connection errors
**Solutions:**
```bash
# Run database migrations
source venv/bin/activate
alembic upgrade head
```

### 4. Frontend Build Issues
**Symptoms:** npm errors or missing packages
**Solutions:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 5. CORS/API Connection Issues
**Symptoms:** Frontend can't connect to backend, "CORS error"
**Fix:** Check that both servers are running and the frontend is on port 3001 (or 3000). The CORS configuration has been updated to support both ports.

### 6. Missing Features/Errors in New Code
**Symptoms:** Neural map not working, search errors, etc.
**Solutions:**
- Make sure all new dependencies are installed:
```bash
cd frontend
npm install three-spritetext react-force-graph-3d
```

### 7. OpenAI API Issues (Optional)
**Symptoms:** Semantic search not working optimally
**Note:** The app works without OpenAI API key using fallback embeddings. To use OpenAI:
1. Get API key from https://platform.openai.com/
2. Add to `.env` file: `OPENAI_API_KEY=your_key_here`

## Manual Start (Alternative)

If the `run_local.sh` script doesn't work:

**Terminal 1 - Backend:**
```bash
cd /path/to/secondbrain
source venv/bin/activate
alembic upgrade head
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /path/to/secondbrain/frontend
npm run dev
```

## Features Available

✅ **Authentication:** Login/signup with JWT tokens  
✅ **Notes CRUD:** Create, read, update, delete notes with rich editor  
✅ **Search:** Semantic search with fallback to keyword search  
✅ **Neural Map:** 2D visualization of note connections  
✅ **Dashboard:** Real analytics with note counts and activity  
✅ **Settings Page:** User preferences and API key management  

## Development

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI + SQLAlchemy + ChromaDB  
- Database: SQLite (development) with Alembic migrations
- Vector Store: ChromaDB for semantic search

## Getting Help

Check the logs in the terminal where you started the servers for detailed error messages.