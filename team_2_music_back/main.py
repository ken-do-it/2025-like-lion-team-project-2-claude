# -*- coding: utf-8 -*-
"""
AI Music Gen - Backend API
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.core.database import check_db_connection, init_db, close_db
from app.core.redis import get_redis
from app.routes import users, tracks, follows, interactions, playlists, tags, history, notifications

# FastAPI app creation
app = FastAPI(
    title=settings.APP_NAME,
    description="Music Sharing Social Platform Backend API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users.router)
app.include_router(tracks.router)
app.include_router(follows.router)
app.include_router(interactions.router)
app.include_router(playlists.router)
app.include_router(tags.router)
app.include_router(history.router)
app.include_router(notifications.router)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check server health status including database and Redis
    """
    # Check database
    db_status = "connected" if check_db_connection() else "disconnected"

    # Check Redis
    redis = get_redis()
    redis_status = "connected" if redis.check_connection() else "disconnected"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "redis": redis_status
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API Information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }


# API v1 Router (to be added later)
@app.get("/api/v1", tags=["API Info"])
async def api_v1_info():
    """
    API v1 Information
    """
    return {
        "version": "v1",
        "endpoints": {
            "health": "/health",
            "users": "/api/v1/users (Coming soon)",
            "tracks": "/api/v1/tracks (Coming soon)",
            "playlists": "/api/v1/playlists (Coming soon)"
        }
    }


# Application Startup/Shutdown Events
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    Initialize database and Redis connections
    """
    print("=" * 50)
    print(f"{settings.APP_NAME} starting up...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")

    # Initialize Redis
    redis = get_redis()
    redis.connect()

    # Check database connection
    db_ok = check_db_connection()
    if not db_ok:
        print("WARNING: Database connection failed!")

    # Initialize database tables
    # await init_db()  # Uncomment when you have models defined

    print(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Health Check: http://{settings.HOST}:{settings.PORT}/health")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    Close database and Redis connections
    """
    print(f"{settings.APP_NAME} shutting down...")

    # Close Redis connection
    redis = get_redis()
    redis.disconnect()

    # Close database connections
    await close_db()


# Direct execution
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
