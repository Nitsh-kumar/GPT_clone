from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.endpoints import auth, chat
from app.models.db import create_tables, init_default_users, get_db
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting AI Chatbot API...")
    try:
        # Test database connection first
        logger.info("Testing database connection...")
        db = next(get_db())
        
        # Create database tables
        logger.info("Creating database tables...")
        create_tables()
        
        # Initialize default users
        logger.info("Initializing default users...")
        init_default_users(db)
        
        logger.info("✅ Database initialized successfully")
        logger.info("Default users created:")
        logger.info("  - admin / admin123 (Admin user)")
        logger.info("  - demo_user / demo123 (Regular user)")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        logger.error("Please check your MySQL connection and credentials in .env file")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="AI Chatbot API",
    description="Backend API for AI Chatbot with Web Search",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-status")
async def database_status():
    """Check database connection status"""
    try:
        db = next(get_db())
        # Simple query to test connection
        from app.models.orm_models import User
        user_count = db.query(User).count()
        return {
            "status": "connected",
            "user_count": user_count,
            "database": settings.DB_NAME,
            "host": settings.DB_HOST,
            "message": "Database connection is healthy"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }

@app.get("/api-info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "name": "AI Chatbot API",
        "version": "1.0.0",
        "database": settings.DB_NAME,
        "endpoints": {
            "authentication": "/api/v1/auth/",
            "chat": "/api/v1/chat/",
            "docs": "/docs",
            "health": "/health",
            "db_status": "/db-status"
        },
        "default_users": [
            {"username": "admin", "password": "admin123", "role": "admin"},
            {"username": "demo_user", "password": "demo123", "role": "user"}
        ]
    }