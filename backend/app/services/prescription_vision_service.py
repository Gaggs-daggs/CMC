"""Prescription Vision service — Groq Vision primary, Gemini fallback."""

from __future__ import annotations
import json
import re
import logging
import os
import io
import base64
import httpx
from app.models.prescription_schemas import PrescriptionData, MedicineInfo

logger = logging.getLogger(__name__)

# ── API Config ───────────────────────────────────────────────────────────────

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE = "https://api.groq.com/openai/v1"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

GEMINI_RX_KEY = os.getenv("GEMINI_PRESCRIPTION_KEY") or os.getenv("GEMINI_API_KEY", "")

VISION_PROMPT = """You are a medical prescription reader. Carefully analyze this prescription image and extract ALL information into structured JSON.

Return ONLY valid JSON (no markdown, no code fences) with this exact structure:
{
  "doctor_name": "Dr. Name or empty string if not visible",
  "patient_name": "Patient name or empty string if not visible",
  "date": "Date on prescription or empty string",
  "diagnosis": "Diagnosis or condition mentioned, or empty string",
  "medicines": [
    {
      "name": "Medicine name",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. twice daily",
      "duration": "e.g. 5 days",
      "instructions": "e.g. take with water",
      "timing": "e.g. after food"
    }
  ],
  "additional_notes": "Any other notes or follow-up instructions"
}

RULES:
- Read HANDWRITTEN text carefully — prescriptions are often handwritten
- Extract EVERY medicine listed, even if partially readable
- Common abbreviations: BD=twice daily, TDS=three times daily, OD=once daily, SOS=as needed
- "1+1+1" means morning+afternoon+night, "1+0+1" means morning+night
- If something is not visible, use empty string ""
- Return ONLY the JSON object, nothing else"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _repair_truncated_json(s: str) -> str:
    """Best-effort repair of truncated JSON."""
    s = re.sub(r',\s*"[^"]*$', '', s)
    s = re.sub(r':\s*"[^"]*$', ': ""', s)
    s = re.sub(r',\s*\{[^}]*$', '', s)
    s = re.sub(r',\s*$', '', s)
    opens = open_sq = 0
    in_str = escape = False
    for ch in s:
        if escape: escape = False; continue
        if ch == '\\' and in_str: escape = True; continue
        if ch == '"': in_str = not in_str; continue
        if in_str: continue
        if ch == '{': opens += 1
        elif ch == '}': opens -= 1
        elif ch == '[': open_sq += 1
        elif ch == ']': open_sq -= 1
    return s + ']' * max(open_sq, 0) + '}' * max(opens, 0)


def _parse_json(text: str) -> dict:
    """Extract JSON from an LLM response (handles code fences, truncation)."""
    fence = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    json_str = fence.group(1).strip() if fence else None
    if not json_str:
        brace = re.search(r"\{.*", text, re.DOTALL)
        json_str = brace.group(0).strip() if brace else None
    if not json_str:
        raise json.JSONDecodeError("No JSON found", text, 0)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return json.loads(_repair_truncated_json(json_str))


def _build_result(data: dict, raw_text: str) -> PrescriptionData:
    """Build PrescriptionData from parsed JSON dict."""
    medicines = []
    for med in data.get("medicines", []):
        name = med.get("name", "").strip()
        if not name or len(name) < 2:
            continue
        medicines.append(MedicineInfo(
            name=name,
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


# ── Primary: Groq Llama 4 Scout Vision ──────────────────────────────────────

async def _try_groq_vision(image_bytes: bytes, mime_type: str) -> PrescriptionData | None:
    """Use Groq's Llama 4 Scout to analyze prescription image directly."""
    try:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_image}"

        logger.info(f"Sending image to Groq {GROQ_VISION_MODEL}...")
        async with httpx.AsyncClient(timeout=60.0) as http:
            resp = await http.post(
                f"{GROQ_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_VISION_MODEL,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_PROMPT},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }],
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"].strip()

        logger.info(f"Groq response: {len(raw)} chars")
        data = _parse_json(raw)
        logger.info(f"Groq parsed: {len(data.get('medicines', []))} medicines")
        return _build_result(data, raw)
    except Exception as e:
        logger.warning(f"Groq Vision failed: {e}")
        return None


# ── Fallback: Gemini Vision ──────────────────────────────────────────────────

async def _try_gemini(image_bytes: bytes, mime_type: str) -> PrescriptionData | None:
    """Fallback: Gemini Vision API (may be rate-limited)."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_RX_KEY)
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        config = types.GenerateContentConfig(temperature=0.1, max_output_tokens=8192)

        logger.info("Trying Gemini 2.0 Flash fallback...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[VISION_PROMPT, image_part],
            config=config,
        )
        raw = response.text.strip()
        logger.info(f"Gemini response: {len(raw)} chars")
        data = _parse_json(raw)
        logger.info(f"Gemini parsed: {len(data.get('medicines', []))} medicines")
        return _build_result(data, raw)
    except Exception as e:
        logger.warning(f"Gemini fallback failed: {e}")
        return None


# ── Main entry point ────────────────────────────────────────────────────────

async def extract_prescription(image_bytes: bytes, mime_type: str = "image/jpeg") -> PrescriptionData:
    """Extract prescription: Groq Vision primary, Gemini fallback."""

    # 1. Groq Llama 4 Scout Vision (free, fast, reads handwriting)
    result = await _try_groq_vision(image_bytes, mime_type)
    if result and result.medicines:
        return result

    # 2. Gemini Vision fallback (may be rate-limited)
    logger.info("Groq unavailable, trying Gemini fallback...")
    result = await _try_gemini(image_bytes, mime_type)
    if result and result.medicines:
        return result

    # Return partial data if we got any
    if result:
        return result

    raise RuntimeError("All extraction methods failed. Please try again later or upload a clearer image.")
