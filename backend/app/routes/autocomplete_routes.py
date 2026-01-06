"""
Autocomplete Routes
API endpoints for medical data autocomplete (allergies, conditions, medications)
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Any
import logging

from ..services.database.postgres_profile_service import postgres_profile_service

router = APIRouter(prefix="/autocomplete", tags=["autocomplete"])
logger = logging.getLogger(__name__)


@router.get("/allergens")
async def search_allergens(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results")
) -> Dict[str, Any]:
    """
    Search allergens for autocomplete
    Returns matching allergens with category and typical severity
    """
    try:
        results = postgres_profile_service.search_allergens(q, limit)
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Allergen search error: {e}")
        return {
            "success": False,
            "query": q,
            "count": 0,
            "results": [],
            "error": str(e)
        }


@router.get("/conditions")
async def search_conditions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results")
) -> Dict[str, Any]:
    """
    Search medical conditions for autocomplete
    Returns matching conditions with category and ICD-10 code
    """
    try:
        results = postgres_profile_service.search_conditions(q, limit)
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Condition search error: {e}")
        return {
            "success": False,
            "query": q,
            "count": 0,
            "results": [],
            "error": str(e)
        }


@router.get("/medications")
async def search_medications(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results")
) -> Dict[str, Any]:
    """
    Search medications for autocomplete
    Returns matching medications with generic name and drug class
    """
    try:
        results = postgres_profile_service.search_medications(q, limit)
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Medication search error: {e}")
        return {
            "success": False,
            "query": q,
            "count": 0,
            "results": [],
            "error": str(e)
        }


@router.get("/stats")
async def get_autocomplete_stats() -> Dict[str, Any]:
    """Get statistics about available autocomplete data"""
    try:
        stats = postgres_profile_service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
