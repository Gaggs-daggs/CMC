"""Gemini Vision service — extracts prescription data from images."""

import json
import re
import logging
import google.generativeai as genai
from app.config import settings
from app.models.schemas import PrescriptionData, MedicineInfo

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)

EXTRACTION_PROMPT = """You are a medical prescription reader. Analyze this prescription image and extract ALL information into structured JSON.

Return ONLY valid JSON (no markdown, no code fences) with this exact structure:
{
  "doctor_name": "Dr. Name or empty string if not visible",
  "patient_name": "Patient name or empty string if not visible",
  "date": "Date on prescription or empty string",
  "diagnosis": "Diagnosis or condition mentioned, or empty string",
  "medicines": [
    {
      "name": "Medicine name (generic + brand if visible)",
      "dosage": "e.g. 500mg, 10ml",
      "frequency": "e.g. twice daily, once at night",
      "duration": "e.g. 5 days, 2 weeks",
      "instructions": "e.g. take with water, avoid dairy",
      "timing": "e.g. after food, before breakfast, morning and night"
    }
  ],
  "additional_notes": "Any other notes, follow-up instructions, or warnings on the prescription"
}

RULES:
- Extract EVERY medicine listed, even if partially readable
- For unclear text, make your best interpretation and note uncertainty
- Include dosage strength (mg, ml, etc.) whenever visible
- Capture timing instructions (before/after food, morning/night)
- If something is not visible or not mentioned, use empty string ""
- Return ONLY the JSON object, nothing else"""


async def extract_prescription(image_bytes: bytes, mime_type: str = "image/jpeg") -> PrescriptionData:
    """Extract prescription data from an image using Gemini 2.5 Flash."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        image_part = {
            "mime_type": mime_type,
            "data": image_bytes,
        }

        response = model.generate_content(
            [EXTRACTION_PROMPT, image_part],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )

        # Get full response text (may include thinking tokens + content)
        raw_text = response.text.strip()
        logger.info(f"Gemini raw text length: {len(raw_text)} chars")

        # Extract JSON from response — Gemini often wraps it in markdown code fences
        # or adds explanatory text before/after the JSON block
        json_str = None

        # Try 1: Extract from ```json ... ``` code fence
        fence_match = re.search(r"```(?:json)?\s*\n(.*?)```", raw_text, re.DOTALL)
        if fence_match:
            json_str = fence_match.group(1).strip()
            logger.info("Extracted JSON from code fence")

        # Try 2: Find the first { ... } block (greedy match for outermost object)
        if not json_str:
            brace_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if brace_match:
                json_str = brace_match.group(0).strip()
                logger.info("Extracted JSON from braces")

        if not json_str:
            raise json.JSONDecodeError("No JSON found in response", raw_text, 0)

        data = json.loads(json_str)

        medicines = []
        for med in data.get("medicines", []):
            medicines.append(MedicineInfo(
                name=med.get("name", "Unknown"),
                dosage=med.get("dosage", ""),
                frequency=med.get("frequency", ""),
                duration=med.get("duration", ""),
                instructions=med.get("instructions", ""),
                timing=med.get("timing", ""),
            ))

        return PrescriptionData(
            prescription_id="",
            doctor_name=data.get("doctor_name", ""),
            patient_name=data.get("patient_name", ""),
            date=data.get("date", ""),
            diagnosis=data.get("diagnosis", ""),
            medicines=medicines,
            additional_notes=data.get("additional_notes", ""),
            raw_text=raw_text,
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.error(f"Raw response: {raw_text[:500]}")
        return PrescriptionData(
            prescription_id="",
            additional_notes=f"OCR completed but parsing failed. Raw text: {raw_text[:1000]}",
            raw_text=raw_text,
        )
    except Exception as e:
        logger.error(f"Gemini Vision error: {e}")
        raise RuntimeError(f"Failed to process prescription image: {str(e)}")
