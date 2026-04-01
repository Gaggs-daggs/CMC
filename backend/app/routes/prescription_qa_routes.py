"""Q&A routes — ask questions about prescriptions."""

import logging
from fastapi import APIRouter, HTTPException

from app.models.prescription_schemas import QARequest, QAResponse
from app.services.prescription_store import prescription_store as store
from app.services import prescription_analysis_service as analysis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prescription", tags=["Prescription Q&A"])


@router.post("/{prescription_id}/ask", response_model=QAResponse)
async def ask_question(prescription_id: str, request: QARequest):
    """Ask a question about a specific prescription."""
    prescription = store.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(404, "Prescription not found. Upload one first.")

    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty.")

    chat_history = store.get_chat_history(prescription_id)

    answer = await analysis_service.answer_question(
        question=request.question,
        medicines=prescription.medicines,
        chat_history=chat_history,
        diagnosis=prescription.diagnosis,
    )

    # Save to chat history
    store.add_chat_message(prescription_id, "user", request.question)
    store.add_chat_message(prescription_id, "assistant", answer)

    return QAResponse(
        answer=answer,
        prescription_id=prescription_id,
        question=request.question,
    )


@router.get("/{prescription_id}/chat-history")
async def get_chat_history(prescription_id: str):
    """Get chat history for a prescription."""
    prescription = store.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(404, "Prescription not found.")

    return {
        "prescription_id": prescription_id,
        "messages": store.get_chat_history(prescription_id),
    }
