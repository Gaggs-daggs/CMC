"""Prescription routes — upload, get, full analysis."""

import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.schemas import (
    UploadResponse,
    PrescriptionResponse,
    PrescriptionData,
    MedicineInfo,
    TextAnalysisRequest,
)
from app.services.prescription_store import store
from app.services import vision_service, analysis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/prescription", tags=["Prescription"])


@router.post("/upload", response_model=PrescriptionResponse)
async def upload_prescription(file: UploadFile = File(...)):
    """Upload a prescription image and get full AI analysis."""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files are supported (JPEG, PNG, etc.)")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "File too large. Maximum 10MB.")

    prescription_id = str(uuid.uuid4())[:8]
    logger.info(f"Processing prescription {prescription_id} ({file.filename}, {len(image_bytes)} bytes)")

    # Step 1: Extract prescription data via Gemini Vision
    try:
        prescription = await vision_service.extract_prescription(
            image_bytes, mime_type=file.content_type
        )
        prescription.prescription_id = prescription_id
    except Exception as e:
        logger.error(f"Vision extraction failed: {e}")
        raise HTTPException(500, f"Failed to read prescription: {str(e)}")

    store.save_prescription(prescription)

    if not prescription.medicines:
        return PrescriptionResponse(
            prescription=prescription,
            overall_advice="No medicines could be extracted from the image. Please try uploading a clearer photo.",
        )

    # Step 2: Analyze medicines via Cerebras LLM
    try:
        analyses = await analysis_service.analyze_all_medicines(prescription.medicines)
        store.save_analyses(prescription_id, analyses)
    except Exception as e:
        logger.error(f"Medicine analysis failed: {e}")
        analyses = []

    # Step 3: Check drug interactions
    try:
        interactions = await analysis_service.check_drug_interactions(prescription.medicines)
        store.save_interactions(prescription_id, interactions)
    except Exception as e:
        logger.error(f"Interaction check failed: {e}")
        interactions = []

    # Step 4: Generate overall advice
    try:
        advice = await analysis_service.generate_overall_advice(
            prescription.medicines, prescription.diagnosis
        )
        store.save_overall_advice(prescription_id, advice)
    except Exception as e:
        logger.error(f"Advice generation failed: {e}")
        advice = "Please follow your doctor's instructions."

    return PrescriptionResponse(
        prescription=prescription,
        medicine_analyses=analyses,
        drug_interactions=interactions,
        overall_advice=advice,
    )


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(prescription_id: str):
    """Get a previously analyzed prescription by ID."""
    prescription = store.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(404, "Prescription not found")

    return PrescriptionResponse(
        prescription=prescription,
        medicine_analyses=store.get_analyses(prescription_id),
        drug_interactions=store.get_interactions(prescription_id),
        overall_advice=store.get_overall_advice(prescription_id),
    )


@router.get("/", response_model=list[PrescriptionData])
async def list_prescriptions():
    """List all uploaded prescriptions."""
    return store.list_all_prescriptions()


@router.post("/analyze-text", response_model=PrescriptionResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Analyze raw OCR text from Puter fallback (no image needed)."""

    prescription_id = str(uuid.uuid4())[:8]
    logger.info(f"Processing text-based prescription {prescription_id} ({len(request.raw_text)} chars)")

    # Parse medicine names from raw OCR text using Cerebras LLM
    try:
        medicines = await analysis_service.extract_medicines_from_text(request.raw_text)
    except Exception as e:
        logger.error(f"Medicine extraction from text failed: {e}")
        medicines = []

    prescription = PrescriptionData(
        prescription_id=prescription_id,
        doctor_name=request.doctor_name,
        patient_name=request.patient_name,
        date=request.date,
        diagnosis=request.diagnosis,
        medicines=medicines,
        additional_notes="[OCR: Puter.ai Fallback]",
        raw_text=request.raw_text,
    )
    store.save_prescription(prescription)

    if not medicines:
        return PrescriptionResponse(
            prescription=prescription,
            overall_advice="Could not extract medicine names from the text. The OCR text was: " + request.raw_text[:500],
        )

    # Steps 2-4: Same as /upload
    try:
        analyses = await analysis_service.analyze_all_medicines(medicines)
        store.save_analyses(prescription_id, analyses)
    except Exception as e:
        logger.error(f"Medicine analysis failed: {e}")
        analyses = []

    try:
        interactions = await analysis_service.check_drug_interactions(medicines)
        store.save_interactions(prescription_id, interactions)
    except Exception as e:
        logger.error(f"Interaction check failed: {e}")
        interactions = []

    try:
        advice = await analysis_service.generate_overall_advice(
            medicines, prescription.diagnosis
        )
        store.save_overall_advice(prescription_id, advice)
    except Exception as e:
        logger.error(f"Advice generation failed: {e}")
        advice = "Please follow your doctor's instructions."

    return PrescriptionResponse(
        prescription=prescription,
        medicine_analyses=analyses,
        drug_interactions=interactions,
        overall_advice=advice,
    )
