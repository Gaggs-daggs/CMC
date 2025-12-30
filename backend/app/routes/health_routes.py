from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthCheckResponse
from app.config import settings
from app.utils.database import Database

router = APIRouter()


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
    
    # TODO: Check other services (Redis, MQTT, ML models)
    services["redis"] = "not_implemented"
    services["mqtt"] = "not_implemented"
    services["ml_models"] = "not_implemented"
    
    overall_status = "healthy" if all(s in ["healthy", "healthy (in-memory)"] or "not_implemented" in s for s in services.values()) else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services=services
    )
