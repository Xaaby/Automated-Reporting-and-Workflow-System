from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os

from app.db import init_db
from app.api import reports, runs
from app.services.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Automated Reporting and Workflow System",
    description="Internal reporting automation tool for scheduled SQL report execution",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router)
app.include_router(runs.router)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/ui")
    async def serve_frontend():
        """Serve the frontend HTML."""
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.on_event("startup")
async def startup_event():
    """
    Initialize database and start scheduler on application startup.
    """
    logger.info("Starting up application...")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    
    # Start scheduler
    try:
        start_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Stop scheduler gracefully on application shutdown.
    """
    logger.info("Shutting down application...")
    try:
        stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")


@app.get("/")
async def root():
    """
    Serve frontend or API info.
    """
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {
        "message": "Automated Reporting and Workflow System API",
        "version": "1.0.0",
        "docs": "/docs",
        "ui": "/ui",
        "endpoints": {
            "reports": "/api/reports",
            "runs": "/api/runs"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
