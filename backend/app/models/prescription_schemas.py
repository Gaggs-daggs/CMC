"""Pydantic schemas for the Prescription Analyzer module."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MedicineFrequency(str, Enum):
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THRICE_DAILY = "thrice_daily"
    FOUR_TIMES = "four_times_daily"
    AS_NEEDED = "as_needed"
    CUSTOM = "custom"


class MedicineInfo(BaseModel):
    name: str
    dosage: str = ""
    frequency: str = ""
    duration: str = ""
    instructions: str = ""
    timing: str = ""  # e.g. "before food", "after food", "morning"


class PrescriptionData(BaseModel):
    prescription_id: str
    doctor_name: str = ""
    patient_name: str = ""
    date: str = ""
    diagnosis: str = ""
    medicines: list[MedicineInfo] = []
    additional_notes: str = ""
    raw_text: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class MedicineAnalysis(BaseModel):
    medicine_name: str
    purpose: str = ""
    how_it_works: str = ""
    common_side_effects: list[str] = []
    serious_side_effects: list[str] = []
    benefits: list[str] = []
    precautions: list[str] = []
    food_interactions: str = ""
    contraindications: list[str] = []


class DrugInteraction(BaseModel):
    drug_a: str
    drug_b: str
    severity: str = ""  # mild, moderate, severe
    description: str = ""
    recommendation: str = ""


class PrescriptionAnalysisResponse(BaseModel):
    prescription: PrescriptionData
    medicine_analyses: list[MedicineAnalysis] = []
    drug_interactions: list[DrugInteraction] = []
    overall_advice: str = ""


class UploadResponse(BaseModel):
    prescription_id: str
    status: str = "processing"
    message: str = ""


class PrescriptionResponse(BaseModel):
    prescription: PrescriptionData
    medicine_analyses: list[MedicineAnalysis] = []
    drug_interactions: list[DrugInteraction] = []
    overall_advice: str = ""


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str
    prescription_id: str
    question: str


class ReminderCreate(BaseModel):
    prescription_id: str
    medicine_name: str
    times: list[str] = []  # ["08:00", "14:00", "20:00"]
    contact: str = ""  # phone or email
    channel: str = "whatsapp"  # whatsapp, email


class ReminderResponse(BaseModel):
    reminder_id: str
    prescription_id: str
    medicine_name: str
    times: list[str] = []
    contact: str = ""
    channel: str = "whatsapp"
    active: bool = True


class TextAnalysisRequest(BaseModel):
    """Request body for analyzing raw OCR text (from Puter fallback)."""
    raw_text: str
    doctor_name: str = ""
    patient_name: str = ""
    date: str = ""
    diagnosis: str = ""
