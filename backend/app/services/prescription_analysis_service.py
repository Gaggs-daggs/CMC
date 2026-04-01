"""Cerebras LLM analysis service — medicine info, side effects, interactions, Q&A."""

import json
import os
import logging
import httpx
from app.models.prescription_schemas import MedicineAnalysis, DrugInteraction, MedicineInfo

logger = logging.getLogger(__name__)

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"
CEREBRAS_MODEL = "llama3.1-8b"

ANALYSIS_HEADERS = {
    "Authorization": f"Bearer {CEREBRAS_API_KEY}",
    "Content-Type": "application/json",
}


async def _call_cerebras(messages: list[dict], temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Call Cerebras chat completions API."""
    payload = {
        "model": CEREBRAS_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{CEREBRAS_BASE_URL}/chat/completions",
            headers=ANALYSIS_HEADERS,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _clean_json(text: str) -> str:
    """Strip markdown code fences from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:])
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


async def analyze_medicine(medicine: MedicineInfo) -> MedicineAnalysis:
    """Get detailed analysis of a single medicine."""
    prompt = f"""You are a pharmacist AI assistant. Analyze this medicine and return ONLY valid JSON.

Medicine: {medicine.name}
Dosage: {medicine.dosage}
Frequency: {medicine.frequency}
Instructions: {medicine.instructions}

Return this exact JSON structure (no markdown, no code fences):
{{
  "medicine_name": "{medicine.name}",
  "purpose": "What this medicine is used for (1-2 sentences)",
  "how_it_works": "Brief mechanism of action (1-2 sentences)",
  "common_side_effects": ["side effect 1", "side effect 2", "side effect 3"],
  "serious_side_effects": ["serious effect 1", "serious effect 2"],
  "benefits": ["benefit 1", "benefit 2", "benefit 3"],
  "precautions": ["precaution 1", "precaution 2"],
  "food_interactions": "Any food interactions or dietary advice",
  "contraindications": ["when NOT to take this medicine"]
}}

Be accurate, concise, and medically sound. Focus on commonly known information."""

    try:
        result = await _call_cerebras([
            {"role": "system", "content": "You are a helpful pharmacist AI. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ])

        cleaned = _clean_json(result)
        data = json.loads(cleaned)

        return MedicineAnalysis(
            medicine_name=data.get("medicine_name", medicine.name),
            purpose=data.get("purpose", ""),
            how_it_works=data.get("how_it_works", ""),
            common_side_effects=data.get("common_side_effects", []),
            serious_side_effects=data.get("serious_side_effects", []),
            benefits=data.get("benefits", []),
            precautions=data.get("precautions", []),
            food_interactions=data.get("food_interactions", ""),
            contraindications=data.get("contraindications", []),
        )
    except json.JSONDecodeError:
        logger.error(f"Failed to parse analysis for {medicine.name}")
        return MedicineAnalysis(
            medicine_name=medicine.name,
            purpose="Analysis could not be parsed. Please try again.",
        )
    except Exception as e:
        logger.error(f"Analysis error for {medicine.name}: {e}")
        return MedicineAnalysis(
            medicine_name=medicine.name,
            purpose=f"Error analyzing medicine: {str(e)}",
        )


async def analyze_all_medicines(medicines: list[MedicineInfo]) -> list[MedicineAnalysis]:
    """Analyze all medicines from a prescription."""
    analyses = []
    for med in medicines:
        analysis = await analyze_medicine(med)
        analyses.append(analysis)
    return analyses


async def extract_medicines_from_text(raw_text: str) -> list[MedicineInfo]:
    """Extract structured medicine info from raw OCR text using Cerebras LLM."""
    prompt = f"""You are a medical prescription parser. Your job is to extract VALID PRESCRIBED MEDICINES from raw OCR text.

RAW TEXT:
{raw_text}

STRICT EXCLUSION RULES (CRITICAL):
- DO NOT extract "Fever", "Cold", "Cough", "Pain" as medicines (these are symptoms/conditions).
- DO NOT extract doctor names, clinic names, or degrees (e.g., "MBBS", "MD").
- DO NOT extract headers like "Rx", "Date", "Diagnosis", "Patient Name".
- DO NOT extract lab tests or advice (e.g., "CBC", "X-Ray").

INCLUSION RULES:
- Extract only items that are clearly medicines (tablets, syrups, injections, gels).
- Look for dosage (mg, ml), frequency (OD, BD, TDS), or duration (days).
- If a brand name is listed without dosage, only extract it if it is clearly a drug name.

Return ONLY valid JSON (no markdown, no code fences) — an array of medicines:
[
  {{
    "name": "Medicine name (e.g. Dolo-650)",
    "dosage": "e.g. 650mg",
    "frequency": "e.g. twice daily",
    "duration": "e.g. 5 days",
    "instructions": "e.g. after food",
    "timing": "e.g. night"
  }}
]

If NO valid medicines are found, return empty array []."""

    try:
        result = await _call_cerebras([
            {"role": "system", "content": "You are a strict medical text parser. Ignore symptoms and boilerplate. Return only valid JSON array."},
            {"role": "user", "content": prompt},
        ], temperature=0.1)

        cleaned = _clean_json(result)
        data = json.loads(cleaned)

        medicines = []
        for item in data:
            name = item.get("name", "Unknown").strip()
            if len(name) < 2 or name.lower() in ["fever", "cold", "cough", "pain", "rx", "date", "diagnosis"]:
                continue

            medicines.append(MedicineInfo(
                name=name,
                dosage=item.get("dosage", ""),
                frequency=item.get("frequency", ""),
                duration=item.get("duration", ""),
                instructions=item.get("instructions", ""),
                timing=item.get("timing", ""),
            ))
        logger.info(f"Extracted {len(medicines)} medicines from raw text")
        return medicines
    except Exception as e:
        logger.error(f"Failed to extract medicines from text: {e}")
        return []


async def check_drug_interactions(medicines: list[MedicineInfo]) -> list[DrugInteraction]:
    """Check for interactions between prescribed medicines."""
    if len(medicines) < 2:
        return []

    med_names = [m.name for m in medicines]
    med_list = ", ".join(med_names)

    prompt = f"""You are a pharmacist AI. Check for drug interactions between these medicines:
{med_list}

Return ONLY valid JSON (no markdown, no code fences) — an array of interactions:
[
  {{
    "drug_a": "Medicine 1 name",
    "drug_b": "Medicine 2 name",
    "severity": "mild|moderate|severe",
    "description": "What the interaction does (1-2 sentences)",
    "recommendation": "What to do about it (1-2 sentences)"
  }}
]

If there are NO significant interactions, return an empty array: []
Only include REAL, clinically significant interactions. Do not invent interactions."""

    try:
        result = await _call_cerebras([
            {"role": "system", "content": "You are a helpful pharmacist AI. Return only valid JSON array."},
            {"role": "user", "content": prompt},
        ])

        cleaned = _clean_json(result)
        data = json.loads(cleaned)

        interactions = []
        for item in data:
            interactions.append(DrugInteraction(
                drug_a=item.get("drug_a", ""),
                drug_b=item.get("drug_b", ""),
                severity=item.get("severity", "unknown"),
                description=item.get("description", ""),
                recommendation=item.get("recommendation", ""),
            ))
        return interactions
    except Exception as e:
        logger.error(f"Drug interaction check failed: {e}")
        return []


async def generate_overall_advice(medicines: list[MedicineInfo], diagnosis: str = "") -> str:
    """Generate overall advice for the prescription."""
    med_summary = "\n".join([
        f"- {m.name} {m.dosage} ({m.frequency}, {m.timing})" for m in medicines
    ])

    prompt = f"""You are a caring health advisor. The patient has been prescribed:
{med_summary}
{"Diagnosis: " + diagnosis if diagnosis else ""}

Give brief, helpful overall advice (3-5 sentences) covering:
1. General tips for taking these medicines together
2. Any lifestyle recommendations
3. When they should contact their doctor

Be warm, empathetic, and concise. Do NOT use bullet points — write in flowing paragraphs."""

    try:
        result = await _call_cerebras([
            {"role": "system", "content": "You are a warm, empathetic health advisor. Give practical advice."},
            {"role": "user", "content": prompt},
        ])
        return result.strip()
    except Exception as e:
        logger.error(f"Overall advice generation failed: {e}")
        return "Please follow your doctor's instructions carefully and take your medicines as prescribed. If you experience any unusual symptoms, contact your doctor immediately."


async def answer_question(
    question: str,
    medicines: list[MedicineInfo],
    chat_history: list[dict],
    diagnosis: str = "",
) -> str:
    """Answer a user's question about their prescription."""
    med_summary = "\n".join([
        f"- {m.name} {m.dosage} ({m.frequency}, {m.timing}, {m.instructions})" for m in medicines
    ])

    system_msg = f"""You are a helpful pharmacist AI assistant. The patient has been prescribed:
{med_summary}
{"Diagnosis: " + diagnosis if diagnosis else ""}

Answer their questions about this prescription helpfully. Be:
- Accurate and evidence-based
- Warm and empathetic
- Concise (2-4 sentences unless more detail is needed)
- Clear about when to see a doctor

IMPORTANT: You are NOT replacing a doctor. For serious concerns, always advise consulting their physician."""

    messages = [{"role": "system", "content": system_msg}]

    # Add recent chat history (last 10 messages)
    recent = chat_history[-10:] if len(chat_history) > 10 else chat_history
    messages.extend(recent)

    messages.append({"role": "user", "content": question})

    try:
        return await _call_cerebras(messages, temperature=0.5, max_tokens=1024)
    except Exception as e:
        logger.error(f"Q&A error: {e}")
        return "I'm sorry, I couldn't process your question right now. Please try again or consult your doctor for medical advice."
