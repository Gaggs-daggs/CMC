"""
Image Analysis Routes for medical image analysis
Pipes Groq Vision output through Cerebras gpt-oss-120b for full diagnosis pipeline
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging
import base64

from ..services.image_analysis import image_analyzer

# Import the same AI response pipeline used by conversation routes
from ..services.ai_service_v2 import get_ai_response

router = APIRouter(prefix="/image", tags=["image-analysis"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    context: Optional[str] = Form(default=""),
    image_type: Optional[str] = Form(default="skin"),
    session_id: Optional[str] = Form(default="image_session"),
    language: Optional[str] = Form(default="en")
):
    """
    Analyze a medical image and return FULL diagnosis pipeline response.
    
    Pipeline: Groq Vision (image understanding) → Cerebras gpt-oss-120b (diagnosis)
    Returns the same rich response as /conversation/message — diagnoses, medications, triage, etc.
    """
    try:
        # Validate file type
        if file.filename:
            ext = "." + file.filename.split(".")[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Convert to base64 for the AI pipeline
        image_b64 = base64.b64encode(content).decode("utf-8")
        
        # Build the message — include user context if provided
        user_message = context if context else "Please analyze this medical image"
        
        logger.info(f"📸 Image uploaded: {file.filename}, piping through full diagnosis pipeline")
        
        # ── Pipe through the SAME get_ai_response() used by /conversation/message ──
        # This gives us: diagnoses, medications, triage, follow-up questions, etc.
        ai_response = await get_ai_response(
            message=user_message,
            session_id=session_id,
            language=language,
            vitals=None,
            image_base64=image_b64
        )
        
        logger.info(f"✅ Full image diagnosis pipeline complete: {len(ai_response.get('diagnoses', []))} diagnoses, "
                     f"{len(ai_response.get('medications', []))} medications")
        
        # Return the FULL response — same format as /conversation/message
        return {
            "success": True,
            # Core response text
            "response": ai_response.get("response", ""),
            "response_translated": ai_response.get("response_translated"),
            # Full diagnosis data
            "diagnoses": ai_response.get("diagnoses", []),
            "medications": ai_response.get("medications", []),
            "follow_up_questions": ai_response.get("follow_up_questions", []),
            "needs_more_info": ai_response.get("needs_more_info", False),
            # Symptoms and conditions
            "symptoms_detected": ai_response.get("symptoms_detected", []),
            "conditions_suggested": ai_response.get("conditions_suggested", []),
            "specialist_recommended": ai_response.get("specialist_recommended"),
            # Triage
            "triage": ai_response.get("triage"),
            "urgency_level": ai_response.get("urgency_level", "self_care"),
            # Metadata
            "confidence": ai_response.get("confidence", 0.5),
            "model_used": ai_response.get("model_used", "groq-vision+cerebras"),
            "processing_time_ms": ai_response.get("processing_time_ms", 0),
            # Legacy fields for backward compat
            "analysis": ai_response.get("response", ""),
            "severity": ai_response.get("urgency_level", "self_care"),
            "disclaimer": "This is AI-assisted analysis, not a medical diagnosis. Please consult a healthcare professional."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types")
async def get_supported_types():
    """Get list of supported image types and conditions"""
    return {
        "file_formats": list(ALLOWED_EXTENSIONS),
        "max_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "condition_types": [
            {"id": "scan", "name": "Medical Scans", "examples": ["MRI", "CT scan", "X-ray", "ultrasound", "PET scan"]},
            {"id": "skin", "name": "Skin Conditions", "examples": ["rash", "acne", "eczema", "psoriasis", "moles"]},
            {"id": "wound", "name": "Wounds & Injuries", "examples": ["cuts", "burns", "bruises", "bites", "lacerations"]},
            {"id": "eye", "name": "Eye Conditions", "examples": ["redness", "swelling", "discharge"]},
            {"id": "general", "name": "General", "examples": ["swelling", "discoloration", "other"]}
        ]
    }
