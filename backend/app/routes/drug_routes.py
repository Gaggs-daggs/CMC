"""
Drug/Medication Routes
- OTC medication suggestions
- Drug interaction checker
- Official drug database lookups (RxNorm, DailyMed, WHO ATC)
- Enhanced medicine enrichment with ALL databases
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..services.drug_service import drug_service

# Import official drug database services
try:
    from ..services.medical_databases import (
        drug_info_service,
        get_drug_info,
        get_drug_safety,
        is_otc,
        get_drug_class
    )
    HAS_DRUG_DATABASE = True
except ImportError:
    HAS_DRUG_DATABASE = False

# Import enhanced medicine service
try:
    from ..services.enhanced_medicine_service import (
        enhanced_medicine_service,
        enrich_medicine,
        enrich_medications,
        get_quick_medicines
    )
    HAS_ENHANCED_MEDICINE = True
except ImportError:
    HAS_ENHANCED_MEDICINE = False

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


# ============================================
# Official Drug Database Endpoints
# ============================================

class DrugLookupRequest(BaseModel):
    drug_name: str
    include_safety: bool = True


@router.get("/info/{drug_name}")
async def get_drug_information(drug_name: str, include_safety: bool = True):
    """
    Get comprehensive drug information from official databases
    
    Sources:
    - RxNorm (NIH) - Drug normalization
    - DailyMed (FDA) - Safety labels
    - WHO ATC - Drug classification
    
    - **drug_name**: Name of the drug (brand or generic)
    - **include_safety**: Whether to include FDA safety info (default: True)
    """
    if not HAS_DRUG_DATABASE:
        raise HTTPException(
            status_code=503,
            detail="Drug database service not available"
        )
    
    try:
        info = await drug_info_service.get_drug_info(drug_name, include_safety)
        return info.to_dict()
    except Exception as e:
        logger.error(f"Drug info lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/safety/{drug_name}")
async def get_drug_safety_info(drug_name: str):
    """
    Get FDA safety information for a drug
    
    Returns:
    - Warnings
    - Contraindications
    - Side effects
    - Pregnancy warnings
    
    - **drug_name**: Name of the drug
    """
    if not HAS_DRUG_DATABASE:
        raise HTTPException(
            status_code=503,
            detail="Drug database service not available"
        )
    
    try:
        safety = await drug_info_service.get_drug_safety(drug_name)
        return safety
    except Exception as e:
        logger.error(f"Drug safety lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class/{drug_name}")
async def get_drug_classification(drug_name: str):
    """
    Get WHO ATC classification for a drug (fast, local lookup)
    
    - **drug_name**: Name of the drug
    """
    if not HAS_DRUG_DATABASE:
        raise HTTPException(
            status_code=503, 
            detail="Drug database service not available"
        )
    
    drug_class = get_drug_class(drug_name)
    is_over_counter = is_otc(drug_name)
    
    return {
        "drug_name": drug_name,
        "drug_class": drug_class,
        "is_otc": is_over_counter,
        "requires_prescription": not is_over_counter if is_over_counter is not None else None,
        "found": drug_class is not None
    }


@router.get("/search/{query}")
async def search_drugs(query: str, limit: int = 5):
    """
    Search for drugs by name
    
    - **query**: Search term
    - **limit**: Maximum results (default: 5)
    """
    if not HAS_DRUG_DATABASE:
        raise HTTPException(
            status_code=503,
            detail="Drug database service not available"
        )
    
    try:
        results = await drug_info_service.search_drugs(query, limit)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Drug search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich")
async def enrich_medication_list(medications: List[dict]):
    """
    Enrich a list of medications with official database info
    
    - **medications**: List of medication objects with 'name' field
    """
    if not HAS_DRUG_DATABASE:
        raise HTTPException(
            status_code=503,
            detail="Drug database service not available"
        )
    
    try:
        enriched = await drug_info_service.enrich_medications_batch(medications)
        return {
            "medications": enriched,
            "enriched_count": sum(1 for m in enriched if m.get("verified"))
        }
    except Exception as e:
        logger.error(f"Medication enrichment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Enhanced Medicine Service Endpoints
# Uses ALL available databases for comprehensive info
# ============================================

class EnhancedMedicineRequest(BaseModel):
    name: str
    include_safety: bool = True
    user_allergies: Optional[List[str]] = []


class SymptomMedicinesRequest(BaseModel):
    symptoms: List[str]
    max_per_symptom: int = 2
    user_allergies: Optional[List[str]] = []


@router.get("/enhanced/{drug_name}")
async def get_enhanced_drug_info(drug_name: str, include_safety: bool = True):
    """
    Get COMPREHENSIVE drug information from ALL available databases
    
    Sources combined:
    - Indian Medicine Database (local, fast)
    - Comprehensive Drug Database (local, fast)
    - WHO ATC Classification (local, fast)
    - RxNorm (NIH) - Drug normalization
    - DailyMed (FDA) - Safety labels
    
    Returns:
    - Full composition with ingredients and strengths
    - Generic and brand names
    - Drug classification (ATC code)
    - Dosage and administration
    - Safety warnings and contraindications
    - Side effects
    - Alternative medicines
    - Indian brand names and prices
    - Verification status and confidence score
    
    - **drug_name**: Name of the drug (brand or generic)
    - **include_safety**: Whether to include FDA safety info (default: True)
    """
    if not HAS_ENHANCED_MEDICINE:
        raise HTTPException(
            status_code=503,
            detail="Enhanced medicine service not available"
        )
    
    try:
        enriched = await enhanced_medicine_service.enrich_medicine(
            {"name": drug_name},
            include_safety=include_safety
        )
        return enriched.to_dict()
    except Exception as e:
        logger.error(f"Enhanced drug info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhanced/enrich")
async def enhanced_enrich_medications(request: EnhancedMedicineRequest):
    """
    Enrich a single medication with ALL available database information
    
    - **name**: Drug name to enrich
    - **include_safety**: Whether to fetch FDA safety info
    - **user_allergies**: List of user's allergies for warnings
    """
    if not HAS_ENHANCED_MEDICINE:
        raise HTTPException(
            status_code=503,
            detail="Enhanced medicine service not available"
        )
    
    try:
        enriched = await enhanced_medicine_service.enrich_medicine(
            {"name": request.name},
            include_safety=request.include_safety,
            user_allergies=request.user_allergies
        )
        return enriched.to_dict()
    except Exception as e:
        logger.error(f"Enhanced enrichment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhanced/batch")
async def enhanced_enrich_batch(
    medications: List[dict],
    include_safety: bool = True,
    user_allergies: Optional[List[str]] = None
):
    """
    Enrich multiple medications with ALL available databases
    
    - **medications**: List of medication objects with 'name' field
    - **include_safety**: Whether to include FDA safety info
    - **user_allergies**: User's allergies for personalized warnings
    """
    if not HAS_ENHANCED_MEDICINE:
        raise HTTPException(
            status_code=503,
            detail="Enhanced medicine service not available"
        )
    
    try:
        enriched = await enrich_medications(
            medications,
            include_safety=include_safety
        )
        
        # Add allergy warnings if provided
        if user_allergies:
            for med in enriched:
                med_name = (med.get("name", "") or "").lower()
                generic = (med.get("generic_name", "") or "").lower()
                for allergen in user_allergies:
                    allergen_lower = allergen.lower()
                    if allergen_lower in med_name or allergen_lower in generic:
                        if "warnings" not in med:
                            med["warnings"] = []
                        med["warnings"].insert(0, f"⚠️ ALLERGY WARNING: Contains {allergen}")
        
        return {
            "medications": enriched,
            "total": len(enriched),
            "verified_count": sum(1 for m in enriched if m.get("verified")),
            "sources_used": list(set(
                source for m in enriched for source in m.get("sources", [])
            ))
        }
    except Exception as e:
        logger.error(f"Enhanced batch enrichment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/for-symptoms")
async def get_medicines_for_symptoms(request: SymptomMedicinesRequest):
    """
    Get medicines for symptoms (fast, local database lookup)
    
    This endpoint is FAST - uses only local databases, no API calls.
    Perfect for quick symptom-based medicine suggestions.
    
    - **symptoms**: List of symptoms (e.g., ["headache", "fever"])
    - **max_per_symptom**: Maximum medicines per symptom (default: 2)
    - **user_allergies**: User's allergies to filter medicines
    """
    if not HAS_ENHANCED_MEDICINE:
        raise HTTPException(
            status_code=503,
            detail="Enhanced medicine service not available"
        )
    
    try:
        medicines = get_quick_medicines(
            symptoms=request.symptoms,
            user_allergies=request.user_allergies
        )
        
        return {
            "symptoms": request.symptoms,
            "medicines": medicines,
            "total": len(medicines),
            "filtered_allergies": request.user_allergies or []
        }
    except Exception as e:
        logger.error(f"Symptom medicines error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alternatives/{drug_name}")
async def get_drug_alternatives(drug_name: str):
    """
    Get alternative medicines for a drug
    
    - **drug_name**: Name of the drug
    """
    if not HAS_ENHANCED_MEDICINE:
        raise HTTPException(
            status_code=503,
            detail="Enhanced medicine service not available"
        )
    
    try:
        alternatives = enhanced_medicine_service.get_alternatives(drug_name)
        return {
            "drug_name": drug_name,
            "alternatives": alternatives,
            "count": len(alternatives)
        }
    except Exception as e:
        logger.error(f"Alternatives lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_drug_services_status():
    """
    Get status of all drug database services
    """
    return {
        "drug_database": HAS_DRUG_DATABASE,
        "enhanced_medicine_service": HAS_ENHANCED_MEDICINE,
        "services": {
            "rxnorm": HAS_DRUG_DATABASE,
            "dailymed": HAS_DRUG_DATABASE,
            "atc_classification": HAS_DRUG_DATABASE,
            "indian_medicine_db": HAS_ENHANCED_MEDICINE,
            "comprehensive_drug_db": HAS_ENHANCED_MEDICINE
        }
    }

