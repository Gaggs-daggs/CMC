"""
User Profile Routes
API endpoints for managing user profiles and medical history

Endpoints:
- POST /profile/check - Check if phone exists, return profile status
- POST /profile/create - Create new profile
- GET /profile/{phone} - Get full profile
- PUT /profile/{phone} - Update profile
- POST /profile/{phone}/allergy - Add allergy
- POST /profile/{phone}/condition - Add medical condition
- POST /profile/{phone}/medication - Add current medication
- GET /profile/{phone}/history - Get consultation history
- GET /profile/{phone}/context - Get AI context string
- DELETE /profile/{phone} - Delete profile (GDPR)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from ..services.profile_service import profile_service
from ..models.user_profile import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
    AddAllergyRequest,
    AddConditionRequest,
    AddMedicationRequest
)

router = APIRouter(prefix="/profile", tags=["user-profiles"])
logger = logging.getLogger(__name__)


class PhoneCheckRequest(BaseModel):
    phone_number: str


class PhoneCheckResponse(BaseModel):
    phone_number: str
    exists: bool
    profile_name: Optional[str] = None
    profile_completeness: int = 0
    total_consultations: int = 0
    is_returning_user: bool = False


class EmergencyContactRequest(BaseModel):
    name: str
    relationship: str
    phone: str


@router.post("/check", response_model=PhoneCheckResponse)
async def check_phone(request: PhoneCheckRequest):
    """
    Check if a phone number has an existing profile
    Used by frontend to determine login vs registration flow
    """
    phone = request.phone_number
    exists = profile_service.phone_exists(phone)
    
    if exists:
        profile = profile_service.get_profile(phone)
        return PhoneCheckResponse(
            phone_number=phone,
            exists=True,
            profile_name=profile.name,
            profile_completeness=profile.calculate_completeness(),
            total_consultations=profile.total_consultations,
            is_returning_user=profile.total_consultations > 0
        )
    else:
        return PhoneCheckResponse(
            phone_number=phone,
            exists=False,
            is_returning_user=False
        )


@router.post("/create")
async def create_profile(request: ProfileCreateRequest):
    """
    Create a new user profile
    Returns existing profile if phone already registered
    """
    try:
        profile, is_new = profile_service.get_or_create_profile(
            phone_number=request.phone_number,
            name=request.name,
            age=request.age,
            gender=request.gender,
            preferred_language=request.preferred_language
        )
        
        # Update with additional fields if provided
        if is_new:
            if request.blood_type:
                profile_service.update_profile(request.phone_number, blood_type=request.blood_type)
            
            # Add allergies
            if request.allergies:
                for allergy_name in request.allergies:
                    profile_service.add_allergy(request.phone_number, allergy_name, severity="moderate")
            
            # Add chronic conditions
            if request.chronic_conditions:
                for condition_name in request.chronic_conditions:
                    profile_service.add_condition(request.phone_number, condition_name)
            
            # Refresh profile
            profile = profile_service.get_profile(request.phone_number)
        
        return {
            "success": True,
            "is_new": is_new,
            "message": "Profile created successfully" if is_new else "Welcome back!",
            "profile": profile.to_dict()
        }
    except Exception as e:
        logger.error(f"Profile creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{phone_number}")
async def get_profile(phone_number: str):
    """Get user profile by phone number"""
    profile = profile_service.get_profile(phone_number)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "profile": profile.to_dict()
    }


@router.put("/{phone_number}")
async def update_profile(phone_number: str, request: ProfileUpdateRequest):
    """Update user profile information"""
    updates = request.model_dump(exclude_none=True)
    
    profile = profile_service.update_profile(phone_number, **updates)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "message": "Profile updated",
        "profile": profile.to_dict()
    }


@router.post("/{phone_number}/allergy")
async def add_allergy(phone_number: str, request: AddAllergyRequest):
    """Add an allergy to user profile"""
    profile = profile_service.add_allergy(
        phone_number=phone_number,
        allergen=request.allergen,
        severity=request.severity,
        reaction=request.reaction
    )
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "message": f"Added allergy: {request.allergen}",
        "allergies": [a.model_dump() for a in profile.allergies]
    }


@router.post("/{phone_number}/condition")
async def add_condition(phone_number: str, request: AddConditionRequest):
    """Add a medical condition to user profile"""
    profile = profile_service.add_condition(
        phone_number=phone_number,
        name=request.name,
        diagnosed_date=request.diagnosed_date,
        severity=request.severity,
        notes=request.notes
    )
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "message": f"Added condition: {request.name}",
        "conditions": [c.model_dump() for c in profile.medical_conditions]
    }


@router.post("/{phone_number}/medication")
async def add_medication(phone_number: str, request: AddMedicationRequest):
    """Add a current medication to user profile"""
    profile = profile_service.add_medication(
        phone_number=phone_number,
        name=request.name,
        dosage=request.dosage,
        frequency=request.frequency,
        prescribed_for=request.prescribed_for
    )
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "message": f"Added medication: {request.name}",
        "medications": [m.model_dump() for m in profile.current_medications]
    }


@router.post("/{phone_number}/emergency-contact")
async def set_emergency_contact(phone_number: str, request: EmergencyContactRequest):
    """Set emergency contact for user"""
    profile = profile_service.set_emergency_contact(
        phone_number=phone_number,
        name=request.name,
        relationship=request.relationship,
        contact_phone=request.phone
    )
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "message": "Emergency contact updated",
        "emergency_contact": profile.emergency_contact.model_dump()
    }


@router.get("/{phone_number}/history")
async def get_consultation_history(phone_number: str, limit: int = 10):
    """Get user's consultation history"""
    history = profile_service.get_consultation_history(phone_number, limit)
    
    return {
        "phone_number": phone_number,
        "consultation_count": len(history),
        "history": history
    }


@router.get("/{phone_number}/context")
async def get_ai_context(phone_number: str):
    """
    Get AI context string for personalized responses
    This is what gets passed to the AI model
    """
    context = profile_service.get_ai_context(phone_number)
    profile = profile_service.get_profile(phone_number)
    
    return {
        "phone_number": phone_number,
        "has_profile": profile is not None,
        "ai_context": context,
        "profile_completeness": profile.calculate_completeness() if profile else 0
    }


@router.get("/{phone_number}/consultations")
async def get_consultation_history(phone_number: str, limit: int = 10):
    """
    Get consultation history for a user
    Returns past consultations with symptoms, conditions, and urgency levels
    """
    profile = profile_service.get_profile(phone_number)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    history = profile_service.get_consultation_history(phone_number, limit)
    
    return {
        "phone_number": phone_number,
        "total_consultations": profile.total_consultations if hasattr(profile, 'total_consultations') else len(history),
        "consultations": history
    }


@router.delete("/{phone_number}")
async def delete_profile(phone_number: str):
    """
    Delete user profile (GDPR compliance)
    This permanently removes all user data
    """
    success = profile_service.delete_profile(phone_number)
    
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "message": "Profile deleted successfully"
    }


@router.get("/stats/count")
async def get_profile_count():
    """Get total number of registered profiles"""
    return {
        "total_profiles": profile_service.get_all_profiles_count()
    }
