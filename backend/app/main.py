"""FastAPI application for Sanas Action Items Tracker."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.actions import router as actions_router
from app.api.settings import router as settings_router

app = FastAPI(
    title=settings.app_name,
    description="Backend API for extracting action items from meeting notes and creating Jira tickets",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(actions_router)
app.include_router(settings_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
