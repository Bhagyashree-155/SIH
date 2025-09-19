from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.core.config import settings
from src.core.logging import setup_logging
from src.models import User, Ticket, Team, Notification, AuditLog
from src.models.knowledge_base import KnowledgeArticle, TicketResolution, CommonIssuePattern
from src.api import auth, tickets, users, dashboard, chatbot, integrations, knowledge_base, classifications
from src.services.email_service import email_service

# Setup logging
logger = setup_logging()

# MongoDB client
mongodb_client: AsyncIOMotorClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting POWERGRID AI Ticketing System...")
    
    try:
        # Initialize MongoDB
        global mongodb_client
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Initialize Beanie with models
        await init_beanie(
            database=mongodb_client[settings.MONGODB_DB_NAME],
            document_models=[
                User,
                Ticket,
                KnowledgeArticle,
                TicketResolution,
                CommonIssuePattern,
                Team,
                Notification,
                AuditLog
            ]
        )
        
        logger.info("Database initialized successfully")
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        
        # Start email polling service if credentials are configured
        if settings.EMAIL_CREDENTIALS:
            logger.info("Starting email polling service...")
            await email_service.start_polling()
            logger.info("Email polling service started")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    
    # Stop email polling service
    if settings.EMAIL_CREDENTIALS:
        logger.info("Stopping email polling service...")
        await email_service.stop_polling()
        logger.info("Email polling service stopped")
    
    if mongodb_client:
        mongodb_client.close()


# Create FastAPI app
app = FastAPI(
    title="POWERGRID AI Ticketing System",
    description="Centralized AI-based ticketing system for POWERGRID IT operations",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "powergrid-ai-ticketing"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to POWERGRID AI Ticketing System API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API routers (only essential ones for now)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(classifications.router, prefix="/api/v1/classifications", tags=["Classifications"])


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
