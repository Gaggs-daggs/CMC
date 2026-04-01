"""Reminder routes — CRUD for medication reminders."""

import uuid
import logging
from fastapi import APIRouter, HTTPException

from app.models.prescription_schemas import ReminderCreate, ReminderResponse
from app.services.prescription_store import prescription_store as store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reminders", tags=["Prescription Reminders"])


@router.post("/", response_model=ReminderResponse)
async def create_reminder(request: ReminderCreate):
    """Create a medication reminder."""
    prescription = store.get_prescription(request.prescription_id)
    if not prescription:
        raise HTTPException(404, "Prescription not found.")

    reminder = ReminderResponse(
        reminder_id=str(uuid.uuid4())[:8],
        prescription_id=request.prescription_id,
        medicine_name=request.medicine_name,
        times=request.times,
        contact=request.contact,
        channel=request.channel,
        active=True,
    )

    store.save_reminder(reminder)
    logger.info(f"Reminder created: {reminder.reminder_id} for {reminder.medicine_name}")

    return reminder


@router.get("/{prescription_id}", response_model=list[ReminderResponse])
async def get_reminders(prescription_id: str):
    """Get all reminders for a prescription."""
    return store.get_reminders(prescription_id)
