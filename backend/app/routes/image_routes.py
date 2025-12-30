"""
Image Analysis Routes for medical image analysis
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging

from ..services.image_analysis import image_analyzer

router = APIRouter(prefix="/image", tags=["image-analysis"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    context: Optional[str] = Form(default=""),
    image_type: Optional[str] = Form(default="skin")
):
    """
    Analyze a medical image for skin conditions, wounds, rashes, etc.
    
    - **file**: Image file (JPG, PNG, WebP)
    - **context**: Additional context (e.g., "appeared 2 days ago, itchy")
    - **image_type**: Type of condition (skin, wound, eye, general)
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
        
        # Analyze the image
        logger.info(f"Analyzing image: {file.filename}, type: {image_type}")
        result = await image_analyzer.analyze_image(
            image_data=content,
            context=context,
            image_type=image_type
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        return {
            "success": True,
            "analysis": result.get("raw_analysis"),
            "severity": result.get("severity"),
            "recommended_action": result.get("recommended_action"),
            "observations": result.get("observations"),
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
