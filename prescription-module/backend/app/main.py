"""CMC Health — Prescription Upload & AI Analysis Module."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import prescription_routes, qa_routes, reminder_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CMC Health — Prescription Manager",
    description="Upload prescriptions, get AI analysis of medicines, side effects, interactions, and set reminders.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(prescription_routes.router)
app.include_router(qa_routes.router)
app.include_router(reminder_routes.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Prescription Manager",
        "version": "1.0.0",
        "ai_services": {
            "gemini_vision": "configured" if settings.GEMINI_API_KEY else "missing",
            "cerebras_llm": "configured" if settings.CEREBRAS_API_KEY else "missing",
        },
    }


@app.get("/")
async def root():
    return {
        "message": "CMC Health — Prescription Manager API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
