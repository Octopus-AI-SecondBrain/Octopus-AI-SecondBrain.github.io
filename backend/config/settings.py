"""
Configuration settings for SecondBrain application
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = DATA_DIR / "database"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Database settings
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/secondbrain.db"

# Vector store settings
CHROMA_DB_PATH = str(VECTOR_DB_DIR)

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Server settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]