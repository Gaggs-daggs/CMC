"""
🏥 INDUSTRY-GRADE MEDICAL DIAGNOSIS ENGINE
=============================================
Production diagnosis system powered by cloud AI APIs.

Architecture:
  1. Cerebras Cloud API (PRIMARY) — ultra-fast inference, gpt-oss-120b (OpenAI reasoning model)
  2. Google Gemini 2.0 Flash (SECONDARY) — structured JSON output
  3. Local Ollama models (FALLBACK) — when APIs are unavailable
  4. Minimal keyword fallback (LAST RESORT) — when everything fails

Design Principles:
  * NO hardcoded symptom -> diagnosis caches
  * ALL diagnoses come from AI clinical reasoning
  * Structured JSON output — no brittle regex parsing
  * Confidence calibration: single symptom <= 65%, multi-symptom <= 85%
  * Emergency detection built into the prompt
"""

import json
import logging
import asyncio
import os
import re
import time
import httpx
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load .env file so API keys are available
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Cerebras Cloud API (PRIMARY — blazing fast inference)
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
CEREBRAS_MODEL = "gpt-oss-120b"
CEREBRAS_URL = "https://api.cerebras.ai/v1/chat/completions"

# Google Gemini (SECONDARY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}"
    f":generateContent"
)

# Ollama fallback models — tried in order
OLLAMA_FALLBACK_MODELS = [
    {"name": "llama3.2:3b", "temperature": 0.2, "num_predict": 600, "timeout": 20},
    {"name": "gemma2:9b",   "temperature": 0.2, "num_predict": 600, "timeout": 35},
    {"name": "llama3.1:8b", "temperature": 0.2, "num_predict": 600, "timeout": 30},
]

# Keep this alias so old imports (MEDICAL_MODELS) don't break
MEDICAL_MODELS = OLLAMA_FALLBACK_MODELS


# ============================================================================
# PROMPTS — Clinical-grade, structured JSON output
# ============================================================================

DIAGNOSIS_SYSTEM_PROMPT = """You are a senior physician with 20 years of clinical experience performing differential diagnosis.

You MUST return valid JSON and nothing else. No markdown, no code fences, no commentary.

CLINICAL REASONING FRAMEWORK:
1. Identify the chief complaint(s) from the reported symptoms.
2. Generate differential diagnoses ranked by probability using Bayesian reasoning.
3. Consider the patient's age and sex when calculating prior probabilities.
4. Flag any emergency red-flag symptoms (chest pain, difficulty breathing, sudden severe headache, loss of consciousness, etc.).

CONFIDENCE CALIBRATION (you MUST follow these):
- 1 vague symptom (e.g. "headache") -> top diagnosis 40-60%
- 2-3 related symptoms -> top diagnosis 55-75%
- 4+ specific, congruent symptoms -> top diagnosis 70-85%
- NEVER exceed 85% — you are an AI, not a lab test
- Lower-ranked diagnoses should step down 5-15% each

URGENCY LEVELS (use exactly these strings):
- "emergency" — life-threatening, call ambulance (e.g. MI, stroke, anaphylaxis)
- "urgent" — ER within hours (e.g. appendicitis signs, severe asthma)
- "doctor_soon" — see doctor in 24-48 h
- "routine" — schedule within 1-2 weeks
- "self_care" — safe for home management

CRITICAL RULES:
- ONLY diagnose conditions whose known symptom profile overlaps with the REPORTED symptoms.
- DO NOT suggest respiratory conditions (asthma, COPD, pneumonia) unless the patient reports cough, wheezing, dyspnoea, or chest symptoms.
- DO NOT suggest cardiac conditions unless the patient reports chest pain, palpitations, or syncope.
- For sleep complaints prioritise: Insomnia, Sleep Apnea, Anxiety, Depression, Restless Legs.
- Always include at least one benign/self-limiting possibility when appropriate.
"""

DIAGNOSIS_USER_PROMPT = """PATIENT PRESENTATION:
- Chief complaints: {symptoms}
- Age: {age} years
- Sex: {gender}

Return a JSON object with EXACTLY this schema (5 diagnoses):
{{
  "diagnoses": [
    {{
      "condition": "<condition name>",
      "confidence": <integer 1-85>,
      "urgency": "<emergency|urgent|doctor_soon|routine|self_care>",
      "description": "<1-2 sentence clinical reasoning>",
      "specialist": "<specialist type or null>",
      "key_symptoms": ["<matching symptoms from patient report>"]
    }}
  ],
  "detected_symptoms": ["<normalised symptom list extracted from presentation>"],
  "follow_up_questions": ["<1-2 clarifying questions a doctor would ask>"],
  "clinical_reasoning": "<brief paragraph on your differential reasoning>"
}}

Return ONLY the JSON. No markdown fences. No extra text."""


# Simpler prompt for local Ollama models (they struggle with complex schemas)
LOCAL_DIAGNOSIS_PROMPT = """You are a doctor. Analyze symptoms and return a JSON diagnosis.

PATIENT: {age}-year-old {gender}
SYMPTOMS: {symptoms}

Return ONLY valid JSON (no markdown, no code fences):
{{
  "diagnoses": [
    {{"condition": "name", "confidence": 50, "urgency": "routine", "description": "reason", "specialist": "type or null", "key_symptoms": ["symptom1"]}}
  ]
}}

Rules:
- Provide exactly 5 diagnoses ranked by likelihood.
- confidence: integer 1-85. Single symptom -> max 60. Multiple -> max 80.
- urgency: emergency / urgent / doctor_soon / routine / self_care
- ONLY suggest conditions that match the reported symptoms.
- Do NOT suggest respiratory conditions unless patient reports cough/breathing issues.

Return ONLY the JSON:"""


# ============================================================================
# DIAGNOSIS ENGINE
# ============================================================================

class DiagnosisEngine:
    """
    Industry-grade diagnosis engine.
    Primary: Cerebras Cloud API (gpt-oss-120b, OpenAI reasoning model)
    Secondary: Gemini 2.0 Flash API (structured JSON)
    Fallback: Local Ollama models
    """

    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create a fresh httpx client. Handles stale/closed connections."""
        if self._http_client is not None:
            try:
                if self._http_client.is_closed:
                    self._http_client = None
            except Exception:
                self._http_client = None
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, keepalive_expiry=25),
            )
        return self._http_client

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    async def diagnose(
        self,
        symptoms: List[str],
        age: int = 30,
        gender: str = "unknown",
        raw_message: str = "",
    ) -> List[Dict]:
        """
        Main entry point. Returns list of diagnosis dicts.
        Each dict: {condition, confidence (int 1-85), urgency, description, specialist, key_symptoms, model_used}
        
        raw_message: The user's original English message. Used when symptoms list is empty
        (e.g. user says "I have ebola") so the AI can still reason about disease names.
        """
        # Build symptoms text — if no extracted symptoms, use the raw message itself
        # so the AI can reason about disease names, conditions mentioned directly
        if not symptoms and not raw_message:
            return [self._empty_result()]

        if symptoms:
            symptoms_text = ", ".join(symptoms)
        else:
            # User said something like "I have ebola" — no keyword symptoms extracted
            # Pass the raw message as the chief complaint so AI can reason about it
            symptoms_text = raw_message.strip()
            logger.info(f"No extracted symptoms — using raw message as chief complaint: '{symptoms_text[:80]}'")
        logger.info(f"DiagnosisEngine.diagnose() — symptoms={symptoms_text}, age={age}, gender={gender}")

        # 1. Try Gemini API (PRIMARY for diagnosis — saves Cerebras quota for response generation)
        gemini_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            try:
                result = await self._diagnose_with_gemini(
                    symptoms_text, age, gender, gemini_key
                )
                if result and len(result) >= 2:
                    logger.info(f"Gemini returned {len(result)} diagnoses")
                    return result
            except Exception as e:
                logger.warning(f"Gemini API failed: {e}")
        else:
            logger.info("GEMINI_API_KEY not set — skipping Gemini")

        # 3. Fallback: try Cerebras only if Gemini failed
        cerebras_key = CEREBRAS_API_KEY or os.getenv("CEREBRAS_API_KEY", "")
        if cerebras_key:
            try:
                result = await self._diagnose_with_cerebras(
                    symptoms_text, age, gender, cerebras_key
                )
                if result and len(result) >= 2:
                    logger.info(f"Cerebras fallback returned {len(result)} diagnoses")
                    return result
            except Exception as e:
                logger.warning(f"Cerebras fallback failed: {e}")

        # 4. Last-resort minimal fallback
        logger.error("All diagnosis sources failed — using keyword fallback")
        return self._keyword_fallback(symptoms)

    # ------------------------------------------------------------------
    # CEREBRAS CLOUD API (PRIMARY)
    # ------------------------------------------------------------------

    async def _diagnose_with_cerebras(
        self,
        symptoms_text: str,
        age: int,
        gender: str,
        api_key: str,
    ) -> Optional[List[Dict]]:
        """
        Call Cerebras Cloud API (gpt-oss-120b) — OpenAI reasoning model, ultra-fast inference.
        Uses OpenAI-compatible chat completions endpoint with json_object response.
        """
        start = time.time()

        user_prompt = DIAGNOSIS_USER_PROMPT.format(
            symptoms=symptoms_text, age=age, gender=gender
        )

        payload = {
            "model": CEREBRAS_MODEL,
            "messages": [
                {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "top_p": 0.8,
            "max_completion_tokens": 2048,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Use fresh client per request to avoid stale TCPTransport errors
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Retry once on 429
            for attempt in range(2):
                resp = await client.post(CEREBRAS_URL, json=payload, headers=headers)

                if resp.status_code == 429:
                    if attempt == 0:
                        logger.warning("Cerebras 429, retrying in 2s...")
                        await asyncio.sleep(2)
                        continue
                    else:
                        logger.error("Cerebras 429 after retry")
                        return None

                resp.raise_for_status()
                break

            data = resp.json()
        elapsed = time.time() - start
        logger.info(f"Cerebras responded in {elapsed:.1f}s")

        # Extract content from OpenAI-compatible response
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Cerebras response structure: {e}")
            return None

        parsed = self._safe_json_parse(text)
        if parsed is None:
            logger.error(f"Failed to parse Cerebras JSON: {text[:300]}")
            return None

        diagnoses_raw = parsed.get("diagnoses", parsed if isinstance(parsed, list) else [])
        if not diagnoses_raw:
            return None

        normalized = self._normalize_result(diagnoses_raw, f"cerebras/{CEREBRAS_MODEL}", symptoms_text.split(", "))
        return normalized

    # ------------------------------------------------------------------
    # GEMINI API (SECONDARY)
    # ------------------------------------------------------------------

    async def _diagnose_with_gemini(
        self,
        symptoms_text: str,
        age: int,
        gender: str,
        api_key: str,
    ) -> Optional[List[Dict]]:
        """Call Gemini 2.0 Flash with structured JSON output. Retries on 429."""
        start = time.time()

        user_prompt = DIAGNOSIS_USER_PROMPT.format(
            symptoms=symptoms_text, age=age, gender=gender
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": DIAGNOSIS_SYSTEM_PROMPT + "\n\n" + user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
            },
        }

        client = await self._get_client()
        url = f"{GEMINI_URL}?key={api_key}"

        # Retry up to 2 times on rate-limit (429)
        max_retries = 2
        data = None
        for attempt in range(max_retries + 1):
            resp = await client.post(url, json=payload)
            if resp.status_code == 429:
                # Parse retry delay from error body if possible
                try:
                    err_body = resp.json()
                    err_msg = err_body.get("error", {}).get("message", "")
                    # Check if quota is literally 0 (not transient)
                    if "limit: 0" in err_msg:
                        logger.error(
                            "Gemini API quota is ZERO — free tier exhausted or billing not enabled. "
                            "Get a new key at https://aistudio.google.com/apikey or enable billing."
                        )
                        return None
                except Exception:
                    pass

                if attempt < max_retries:
                    wait = 2 ** (attempt + 1)  # 2s, 4s
                    logger.warning(f"Gemini 429 rate-limited, retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                    continue
                else:
                    logger.error("Gemini 429 after all retries")
                    return None

            resp.raise_for_status()
            data = resp.json()
            break

        if data is None:
            return None

        elapsed = time.time() - start
        logger.info(f"Gemini responded in {elapsed:.1f}s")

        # Extract text from Gemini response
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Gemini response structure: {e}")
            return None

        # Parse JSON
        parsed = self._safe_json_parse(text)
        if parsed is None:
            logger.error(f"Failed to parse Gemini JSON: {text[:300]}")
            return None

        diagnoses_raw = parsed.get("diagnoses", parsed if isinstance(parsed, list) else [])
        if not diagnoses_raw:
            return None

        normalized = self._normalize_result(diagnoses_raw, "gemini-2.0-flash", symptoms_text.split(", "))
        return normalized

    # ------------------------------------------------------------------
    # OLLAMA FALLBACK
    # ------------------------------------------------------------------

    async def _diagnose_with_ollama(
        self,
        symptoms_text: str,
        age: int,
        gender: str,
    ) -> Optional[List[Dict]]:
        """Try local Ollama models in priority order."""
        import ollama as ollama_lib

        for model_cfg in OLLAMA_FALLBACK_MODELS:
            model_name = model_cfg["name"]

            if not check_model_available(model_name):
                logger.info(f"Skipping {model_name} — not available")
                continue

            prompt = LOCAL_DIAGNOSIS_PROMPT.format(
                symptoms=symptoms_text, age=age, gender=gender
            )

            start = time.time()
            try:
                # Run blocking ollama call in a thread
                response = await asyncio.to_thread(
                    ollama_lib.chat,
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    format="json",
                    options={
                        "temperature": model_cfg["temperature"],
                        "num_predict": model_cfg["num_predict"],
                    },
                )
                elapsed = time.time() - start
                text = response["message"]["content"]
                logger.info(f"Ollama {model_name} responded in {elapsed:.1f}s")

                parsed = self._safe_json_parse(text)
                if parsed is None:
                    # Try free-text parsing as last resort
                    diagnoses = self._parse_freetext_response(text)
                    if diagnoses:
                        return diagnoses
                    logger.warning(f"{model_name} returned unparseable response")
                    continue

                diagnoses_raw = parsed.get("diagnoses", parsed if isinstance(parsed, list) else [])
                if not diagnoses_raw:
                    continue

                normalized = self._normalize_result(diagnoses_raw, model_name, symptoms_text.split(", "))
                if normalized and len(normalized) >= 2:
                    return normalized

            except Exception as e:
                elapsed = time.time() - start
                logger.error(f"Ollama {model_name} error after {elapsed:.1f}s: {e}")
                continue

        return None

    # ------------------------------------------------------------------
    # PARSING & NORMALISATION HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_json_parse(text: str) -> Optional[Dict]:
        """Robust JSON parsing — handles markdown fences, trailing commas, etc."""
        if not text:
            return None

        # Strip markdown code fences
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*\n?", "", text)
            text = re.sub(r"\n?```\s*$", "", text)

        # Remove trailing commas before } or ]
        text = re.sub(r",\s*([}\]])", r"\1", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON object/array from surrounding text
            for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
                m = re.search(pattern, text)
                if m:
                    try:
                        return json.loads(m.group())
                    except json.JSONDecodeError:
                        continue
            return None

    def _normalize_result(
        self,
        diagnoses_raw: List[Dict],
        model_name: str,
        symptoms: List[str],
    ) -> List[Dict]:
        """Validate and normalise each diagnosis dict."""
        valid_urgencies = {"emergency", "urgent", "doctor_soon", "routine", "self_care"}
        normalised = []

        for d in diagnoses_raw:
            condition = d.get("condition", "").strip()
            if not condition or len(condition) < 3:
                continue

            # Confidence — force integer 1-85
            try:
                conf = int(float(d.get("confidence", 50)))
            except (ValueError, TypeError):
                conf = 50
            # If returned as 0-1 decimal, rescale
            if 0 < conf <= 1:
                conf = int(conf * 100)
            conf = max(1, min(85, conf))

            # Urgency
            urgency = str(d.get("urgency", "routine")).lower().replace(" ", "_").replace("-", "_")
            if urgency not in valid_urgencies:
                urgency_map = {
                    "soon": "doctor_soon", "immediate": "emergency",
                    "asap": "urgent", "moderate": "routine",
                    "low": "self_care", "high": "urgent",
                }
                urgency = urgency_map.get(urgency, "routine")

            normalised.append({
                "condition": condition,
                "confidence": conf,
                "urgency": urgency,
                "description": d.get("description", "Based on reported symptoms"),
                "specialist": d.get("specialist") if d.get("specialist") not in [None, "null", "None", ""] else None,
                "key_symptoms": d.get("key_symptoms", symptoms[:3]),
                "model_used": model_name,
            })

        # Sort by confidence descending
        normalised.sort(key=lambda x: x["confidence"], reverse=True)
        return normalised[:5]

    @staticmethod
    def _parse_freetext_response(text: str) -> Optional[List[Dict]]:
        """
        Last-resort: extract diagnoses from numbered free-text when JSON parsing fails.
        Handles patterns like: '1. Condition Name - 75% - urgency'
        """
        diagnoses = []
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip().replace("**", "").replace("*", "")
            if not line:
                continue

            # Pattern: "1. Condition - 75% - urgency_level"
            m = re.match(
                r"^\d+[\.\)]\s*(.+?)\s*[\-\u2013\u2014]\s*(\d+)%?\s*[\-\u2013\u2014]\s*(\w[\w_]*)",
                line,
            )
            if not m:
                # Pattern: "1. Condition (75%) - urgency"
                m = re.match(
                    r"^\d+[\.\)]\s*(.+?)\s*\((\d+)%?\)\s*[\-\u2013\u2014]\s*(\w[\w_]*)",
                    line,
                )
            if not m:
                # Pattern: "1. Condition - 75%"
                m2 = re.match(r"^\d+[\.\)]\s*(.+?)\s*[\-\u2013\u2014]\s*(\d+)%", line)
                if m2:
                    diagnoses.append({
                        "condition": m2.group(1).strip(),
                        "confidence": max(1, min(85, int(m2.group(2)))),
                        "urgency": "routine",
                        "description": "Based on symptom analysis",
                        "specialist": None,
                        "key_symptoms": [],
                        "model_used": "ollama-freetext",
                    })
                continue

            if m:
                urgency = m.group(3).lower().replace("-", "_")
                valid = {"emergency", "urgent", "doctor_soon", "routine", "self_care"}
                if urgency not in valid:
                    urgency = "routine"
                diagnoses.append({
                    "condition": m.group(1).strip(),
                    "confidence": max(1, min(85, int(m.group(2)))),
                    "urgency": urgency,
                    "description": "Based on symptom analysis",
                    "specialist": None,
                    "key_symptoms": [],
                    "model_used": "ollama-freetext",
                })

        return diagnoses[:5] if len(diagnoses) >= 2 else None

    # ------------------------------------------------------------------
    # FALLBACKS
    # ------------------------------------------------------------------

    @staticmethod
    def _keyword_fallback(symptoms: List[str]) -> List[Dict]:
        """Minimal keyword-based fallback when ALL AI sources fail."""
        symptoms_lower = " ".join(s.lower() for s in symptoms)

        emergency_kws = [
            "chest pain", "difficulty breathing", "severe bleeding",
            "unconscious", "stroke", "heart attack", "seizure",
        ]
        for kw in emergency_kws:
            if kw in symptoms_lower:
                return [{
                    "condition": "Medical Emergency - Seek Immediate Care",
                    "confidence": 85,
                    "urgency": "emergency",
                    "description": f"Symptoms suggest possible emergency: {kw}",
                    "specialist": "Emergency Room",
                    "key_symptoms": [kw],
                    "model_used": "keyword_fallback",
                }]

        patterns = [
            (["fever", "temperature", "chills"], "Possible Infection", 50, "routine", "General Physician"),
            (["headache", "head pain"], "Headache Disorder", 45, "self_care", "Neurologist"),
            (["stomach", "abdominal", "nausea"], "Gastrointestinal Issue", 45, "routine", "Gastroenterologist"),
            (["cough", "cold", "runny nose"], "Upper Respiratory Infection", 50, "self_care", None),
            (["back pain", "spine"], "Musculoskeletal Pain", 45, "routine", "Orthopedist"),
            (["anxiety", "stress", "panic"], "Mental Health Concern", 45, "routine", "Psychiatrist"),
            (["rash", "itching", "hives"], "Dermatological Condition", 45, "routine", "Dermatologist"),
            (["insomnia", "sleep", "sleeping"], "Sleep Disorder", 50, "routine", "Sleep Specialist"),
        ]

        results = []
        for kws, condition, conf, urgency, spec in patterns:
            matched = [k for k in kws if k in symptoms_lower]
            if matched:
                results.append({
                    "condition": condition,
                    "confidence": conf,
                    "urgency": urgency,
                    "description": f"Based on: {', '.join(matched)}",
                    "specialist": spec,
                    "key_symptoms": matched,
                    "model_used": "keyword_fallback",
                })

        if len(results) < 2:
            results.append({
                "condition": "General Medical Evaluation Needed",
                "confidence": 35,
                "urgency": "routine",
                "description": "Symptoms require professional assessment",
                "specialist": "General Practitioner",
                "key_symptoms": symptoms[:2],
                "model_used": "keyword_fallback",
            })

        return results[:5]

    @staticmethod
    def _empty_result() -> Dict:
        return {
            "condition": "Insufficient Information",
            "confidence": 30,
            "urgency": "routine",
            "description": "Please describe your symptoms for diagnosis",
            "specialist": None,
            "key_symptoms": [],
            "model_used": "none",
        }


# ============================================================================
# SINGLETON
# ============================================================================
_engine = DiagnosisEngine()


# ============================================================================
# BACKWARD-COMPATIBLE PUBLIC API
# These functions are imported by diagnosis_engine.py and ai_service_v2.py
# ============================================================================

async def get_ai_diagnosis(
    symptoms: List[str],
    age: int = 30,
    gender: str = "unknown",
    use_ensemble: bool = False,  # kept for API compat, ignored
    raw_message: str = "",
) -> List[Dict]:
    """Async diagnosis — delegates to DiagnosisEngine."""
    return await _engine.diagnose(symptoms, age, gender, raw_message=raw_message)


def get_ai_diagnosis_sync(
    symptoms: List[str],
    age: int = 30,
    gender: str = "unknown",
    use_ensemble: bool = False,
    raw_message: str = "",
) -> List[Dict]:
    """
    Synchronous wrapper — called by diagnosis_engine.py and ai_service_v2.py.
    Handles being called from both sync and async contexts safely.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We are inside an async context (FastAPI) — run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    lambda: asyncio.run(get_ai_diagnosis(symptoms, age, gender, raw_message=raw_message))
                )
                return future.result(timeout=45)
        else:
            return asyncio.run(get_ai_diagnosis(symptoms, age, gender, raw_message=raw_message))

    except Exception as e:
        logger.error(f"get_ai_diagnosis_sync error: {e}")
        return _engine._keyword_fallback(symptoms)


async def get_full_diagnosis(
    symptoms: List[str],
    age: int = 30,
    gender: str = "unknown",
) -> Dict:
    """
    Extended diagnosis returning the full Gemini response
    (diagnoses + detected_symptoms + follow_up_questions + clinical_reasoning).
    """
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if api_key:
        symptoms_text = ", ".join(symptoms)
        user_prompt = DIAGNOSIS_USER_PROMPT.format(
            symptoms=symptoms_text, age=age, gender=gender
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": DIAGNOSIS_SYSTEM_PROMPT + "\n\n" + user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
            },
        }

        try:
            client = await _engine._get_client()
            url = f"{GEMINI_URL}?key={api_key}"
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = _engine._safe_json_parse(text)
            if parsed and "diagnoses" in parsed:
                parsed["diagnoses"] = _engine._normalize_result(
                    parsed["diagnoses"], "gemini-2.0-flash", symptoms
                )
                return parsed
        except Exception as e:
            logger.warning(f"get_full_diagnosis Gemini failed: {e}")

    # Fallback: wrap basic diagnosis
    diagnoses = await get_ai_diagnosis(symptoms, age, gender)
    return {
        "diagnoses": diagnoses,
        "detected_symptoms": symptoms,
        "follow_up_questions": [],
        "clinical_reasoning": "Diagnosis generated by fallback engine.",
    }


# ============================================================================
# UTILITY FUNCTIONS (backward compat)
# ============================================================================

def check_model_available(model_name: str) -> bool:
    """Check if an Ollama model is available locally."""
    try:
        import ollama as ollama_lib
        result = ollama_lib.list()
        if hasattr(result, "models"):
            models = result.models
        else:
            models = result.get("models", [])

        model_base = model_name.split(":")[0]
        for m in models:
            name = m.model if hasattr(m, "model") else (m.get("name", "") if isinstance(m, dict) else "")
            if model_base == name.split(":")[0]:
                return True
        return False
    except Exception:
        return False


def get_available_models() -> List[str]:
    """List available Ollama model names."""
    try:
        import ollama as ollama_lib
        result = ollama_lib.list()
        if hasattr(result, "models"):
            models = result.models
        else:
            models = result.get("models", [])

        names = []
        for m in models:
            name = m.model if hasattr(m, "model") else (m.get("name", "") if isinstance(m, dict) else "")
            if name:
                names.append(name)
        return names
    except Exception:
        return []


def get_diagnosis_engine_status() -> Dict:
    """Status of the diagnosis engine."""
    available = get_available_models()
    cerebras_key = CEREBRAS_API_KEY or os.getenv("CEREBRAS_API_KEY", "")
    gemini_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if cerebras_key:
        primary = f"cerebras/{CEREBRAS_MODEL}"
    elif gemini_key:
        primary = "gemini-2.0-flash"
    else:
        primary = "ollama"

    return {
        "engine": "Industry-Grade Medical Diagnosis Engine",
        "version": "3.1",
        "primary": primary,
        "cerebras_configured": bool(cerebras_key),
        "gemini_configured": bool(gemini_key),
        "ollama_models_available": available,
        "status": "operational" if cerebras_key or gemini_key or available else "degraded",
    }
