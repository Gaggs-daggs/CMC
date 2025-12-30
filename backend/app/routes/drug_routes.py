"""
Drug/Medication Routes
- OTC medication suggestions
- Drug interaction checker
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..services.drug_service import drug_service

router = APIRouter(prefix="/drugs", tags=["medications"])
logger = logging.getLogger(__name__)


class SymptomRequest(BaseModel):
    symptoms_text: str
    current_medications: Optional[List[str]] = []


class InteractionCheckRequest(BaseModel):
    medications: List[str]


@router.post("/suggest")
async def suggest_medications(request: SymptomRequest):
    """
    Get OTC medication suggestions based on symptoms
    
    - **symptoms_text**: Description of symptoms (e.g., "I have headache and fever")
    - **current_medications**: List of medications user is already taking
    """
    try:
        result = drug_service.get_prescription_response(
            request.symptoms_text,
            request.current_medications
        )
        
        # Add formatted text response
        result["formatted_response"] = drug_service.format_prescription_text(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Drug suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactions")
async def check_interactions(request: InteractionCheckRequest):
    """
    Check for drug interactions between medications
    
    - **medications**: List of medication names to check
    """
    try:
        interactions = drug_service.check_interactions(request.medications)
        
        return {
            "medications_checked": request.medications,
            "interactions_found": len(interactions) > 0,
            "interactions": interactions,
            "safe": len(interactions) == 0
        }
        
    except Exception as e:
        logger.error(f"Interaction check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{symptom}")
async def list_medications_for_symptom(symptom: str):
    """
    Get list of OTC medications for a specific symptom
    """
    symptom_lower = symptom.lower().replace("-", " ").replace("_", " ")
    
    if symptom_lower in drug_service.medications:
        return {
            "symptom": symptom_lower,
            "medications": drug_service.medications[symptom_lower]
        }
    
    # Try to find similar symptom
    for key in drug_service.medications.keys():
        if symptom_lower in key or key in symptom_lower:
            return {
                "symptom": key,
                "medications": drug_service.medications[key]
            }
    
    raise HTTPException(status_code=404, detail=f"No medications found for symptom: {symptom}")


@router.get("/symptoms")
async def list_supported_symptoms():
    """
    Get list of all supported symptoms
    """
    return {
        "symptoms": list(drug_service.medications.keys()),
        "total": len(drug_service.medications)
    }
