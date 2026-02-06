from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.config import settings
from app.utils.database import db
from app.utils.logging_config import setup_logging
from app.routes import conversation_routes, user_routes, vitals_routes, health_routes, image_routes, drug_routes, tts_routes, profile_routes, autocomplete_routes, session_routes, whatsapp_routes

# Setup logging
logger = setup_logging(settings.APP_NAME, settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting application...")
    
    # Connect to PostgreSQL (or fallback to in-memory)
    try:
        await db.connect_db(settings.DATABASE_URL, settings.MONGODB_DB_NAME)
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed, using in-memory storage: {e}")
        await db.connect_db(None, None)  # Force in-memory mode
    
    # TODO: Initialize ML models
    # TODO: Connect to MQTT broker
    # TODO: Start Prometheus metrics server
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await db.close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multilingual AI Symptom Checker for Basic Healthcare Guidance",
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    
    # Log slow requests
    if process_time > settings.MAX_INFERENCE_TIME * 1000:
        logger.warning(
            f"Slow request: {request.method} {request.url.path}",
            extra={"duration_ms": process_time}
        )
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Include routers
app.include_router(health_routes.router, prefix="/api/v1", tags=["Health"])
app.include_router(conversation_routes.router, prefix="/api/v1", tags=["Conversation"])
app.include_router(user_routes.router, prefix="/api/v1", tags=["Users"])
app.include_router(vitals_routes.router, prefix="/api/v1", tags=["Vitals"])
app.include_router(image_routes.router, prefix="/api/v1", tags=["Image Analysis"])
app.include_router(drug_routes.router, prefix="/api/v1", tags=["Medications"])
app.include_router(tts_routes.router, prefix="/api/v1", tags=["Text-to-Speech"])
app.include_router(profile_routes.router, prefix="/api/v1", tags=["User Profiles"])
app.include_router(autocomplete_routes.router, prefix="/api/v1", tags=["Autocomplete"])
app.include_router(session_routes.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(whatsapp_routes.router, prefix="/api/v1", tags=["WhatsApp"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
