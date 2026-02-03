# app.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

from app.utils.database import engine, get_db, Base
from app.utils.config import settings

# Configure CORS from .env
origins = []
if settings.CORS_ORIGINS != "*":
    origins = settings.CORS_ORIGINS.split(",")
else:
    origins = ["*"]

# Lifespan for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📊 Database: {settings.DB_NAME}@{settings.DB_HOST}")
    
    Base.metadata.create_all(bind=engine)
    
    # Test connection
    try:
        with engine.connect() as conn:
            db_info = conn.execute(text("SELECT version()")).scalar()
            print(f"✅ PostgreSQL Connected: {db_info.split(',')[0]}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    yield  # App runs here
    
    # Shutdown: Close connections
    print("👋 Shutting down...")
    engine.dispose()

# Create FastAPI app with settings from .env
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check with database
@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0",
        "debug": settings.DEBUG,
        "database": {
            "host": settings.DB_HOST,
            "name": settings.DB_NAME,
            "user": settings.DB_USER
        }
    }

