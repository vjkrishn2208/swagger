from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import session_routes
from db.mongo_client import connect_to_mongo, close_mongo_connection
from security.api_key_auth import get_api_key
from app_config import settings
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cvp_lite.log')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    session_routes.router,
    prefix="/api",
    dependencies=[Depends(get_api_key)],
    tags=["CVP Lite Sessions"]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# Health check endpoint (no auth required)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CVP Lite API",
        "version": settings.API_VERSION,
        "timestamp": "2024-01-01T00:00:00Z"  # This would be dynamic in production
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to CVP Lite API",
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Startup event
@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection and services on startup"""
    try:
        logger.info("Starting CVP Lite API...")
        
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("MongoDB connection established")
        
        # Initialize Pinecone if configured
        try:
            from services.pinecone_client import init_pinecone
            init_pinecone()
            logger.info("Pinecone initialized successfully")
        except Exception as e:
            logger.warning(f"Pinecone initialization failed: {e}")
        
        # Validate OpenAI configuration
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured - AI features will be limited")
        else:
            logger.info("OpenAI configuration validated")
        
        logger.info("CVP Lite API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # In production, you might want to exit here
        # sys.exit(1)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean up resources on shutdown"""
    try:
        logger.info("Shutting down CVP Lite API...")
        
        # Close MongoDB connection
        await close_mongo_connection()
        logger.info("MongoDB connection closed")
        
        logger.info("CVP Lite API shutdown completed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Additional middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests"""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )