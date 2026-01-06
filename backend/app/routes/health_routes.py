from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthCheckResponse
from app.config import settings
from app.utils.database import Database

router = APIRouter()


# Try to import orchestrator for system status
try:
    from app.services.ai_orchestrator import get_ai_orchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    
    services = {}
    
    # Check MongoDB / In-memory storage
    try:
        if hasattr(Database, 'client') and Database.client:
            await Database.client.admin.command('ping')
            services["mongodb"] = "healthy"
        elif Database._in_memory_store is not None:
            services["mongodb"] = "healthy (in-memory)"
        else:
            services["mongodb"] = "not_connected"
    except Exception as e:
        services["mongodb"] = f"unhealthy: {str(e)}"
    
    # Check AI Orchestrator components
    if ORCHESTRATOR_AVAILABLE:
        try:
            orchestrator = get_ai_orchestrator()
            status = orchestrator.get_system_status()
            services["ai_assistant"] = "healthy" if status.get("ai_assistant") else "unhealthy"
            services["triage_classifier"] = "healthy" if status.get("triage_classifier") else "not_available"
            services["safety_guardrails"] = "healthy" if status.get("safety_guardrails") else "not_available"
            services["rag_knowledge_base"] = "healthy" if status.get("rag_knowledge_base") else "not_available"
            services["translation"] = "healthy" if status.get("translation") else "not_available"
            services["translation_engine"] = status.get("translation_engine", "None")
        except Exception as e:
            services["ai_orchestrator"] = f"error: {str(e)}"
    else:
        services["ai_orchestrator"] = "not_available"
    
    # Legacy service checks
    services["redis"] = "not_implemented"
    services["mqtt"] = "not_implemented"
    
    overall_status = "healthy" if all(
        s in ["healthy", "healthy (in-memory)", "not_available", "not_implemented"] or "not_" in str(s)
        for k, s in services.items() if k != "translation_engine"
    ) else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services=services
    )


@router.get("/health/ai")
async def ai_health_check():
    """Detailed AI system health check"""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "unavailable", "message": "AI Orchestrator not loaded"}
    
    try:
        orchestrator = get_ai_orchestrator()
        status = orchestrator.get_system_status()
        
        return {
            "status": "healthy",
            "components": status,
            "translation_cache": status.get("translation_cache_stats", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
