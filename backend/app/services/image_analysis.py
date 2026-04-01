"""
Medical Image Analysis Service
Analyzes skin conditions, wounds, rashes, scans, and other visible symptoms
Primary: Groq Vision (Llama 4 Scout) | Fallback: Gemini Vision | Last: LLaVA via Ollama
"""
import base64
import logging
import httpx
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Groq Vision config (PRIMARY)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Gemini Vision config (SECONDARY)
GEMINI_VISION_KEY = os.getenv("GEMINI_VISION_API_KEY", "")
GEMINI_VISION_MODEL = "gemini-2.0-flash"
GEMINI_VISION_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_VISION_MODEL}:generateContent"

# Universal medical image analysis prompt — AI auto-detects image type
MEDICAL_ANALYSIS_PROMPT = """You are an expert medical AI assistant trained in radiology, dermatology, ophthalmology, emergency medicine, and general clinical analysis.

**STEP 1 — IDENTIFY THE IMAGE TYPE:**
First, determine what kind of medical image this is:
- X-ray, CT scan, MRI, ultrasound, or other radiology scan
- ECG/EKG (electrocardiogram) strip or report
- Skin condition photo (rash, lesion, wound, mole, etc.)
- Eye condition photo
- Medical prescription or lab report
- Wound or injury photo
- Echocardiogram
- Blood test report or pathology report
- Other medical document or image

**STEP 2 — ANALYZE BASED ON IMAGE TYPE:**

If it's an **X-ray / CT / MRI / Ultrasound**:
- Scan type and body region
- Key findings (normal and abnormal)
- Top 3 possible diagnoses
- Severity: ROUTINE / CONCERNING / URGENT / CRITICAL
- Which specialist to consult

If it's an **ECG/EKG**:
- Heart rate and rhythm assessment
- Any abnormalities (ST changes, arrhythmias, blocks, etc.)
- Top 3 possible conditions
- Severity and urgency
- Recommended next steps

If it's a **Skin Condition**:
- Visual description (color, size, shape, texture, borders)
- Top 3 possible conditions with likelihood
- Severity: MILD / MODERATE / SEVERE
- Home care tips and when to see a doctor

If it's a **Wound/Injury**:
- Wound type, size, depth, infection signs
- Severity: MINOR / MODERATE / SEVERE
- First aid steps
- Whether professional care is needed

If it's a **Medical Prescription**:
- List all medications with dosages
- What each medication is typically prescribed for
- Any potential drug interactions
- Important instructions or warnings

If it's a **Lab Report / Blood Test**:
- List key values that are abnormal (out of range)
- What each abnormal value may indicate
- Overall assessment
- Whether follow-up is needed

If it's an **Echocardiogram**:
- Heart chamber sizes and function
- Valve assessment
- Ejection fraction if visible
- Key findings and concerns

**STEP 3 — SUMMARY:**
- **Image Type**: (what this image is)
- **Key Findings**: (most important observations)
- **Severity**: (how urgent this is)
- **Recommended Action**: what the patient should do next

⚠️ DISCLAIMER: This is AI-assisted preliminary analysis only. Always consult a qualified healthcare professional for definitive diagnosis and treatment."""

# Keep specialized prompts as overrides when user specifies type
IMAGE_PROMPTS = {
    "scan": MEDICAL_ANALYSIS_PROMPT,
    "skin": MEDICAL_ANALYSIS_PROMPT,
    "wound": MEDICAL_ANALYSIS_PROMPT,
    "eye": MEDICAL_ANALYSIS_PROMPT,
    "ecg": MEDICAL_ANALYSIS_PROMPT,
    "prescription": MEDICAL_ANALYSIS_PROMPT,
    "lab_report": MEDICAL_ANALYSIS_PROMPT,
    "general": MEDICAL_ANALYSIS_PROMPT,
}


class ImageAnalysisService:
    """Medical image analysis — Groq Vision primary, Gemini secondary, LLaVA fallback"""
    
    def __init__(self):
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_VISION_KEY
        logger.info(f"🖼️ Image Analysis: Groq key: {bool(self.groq_key)}, Gemini key: {bool(self.gemini_key)}")
    
    def _detect_image_type(self, context: str, image_type: str) -> str:
        """Auto-detect the best prompt type based on context — but AI does the real detection"""
        combined = ((context or "") + " " + (image_type or "")).lower()
        
        scan_keywords = ["mri", "ct", "x-ray", "xray", "scan", "ultrasound", "pet", 
                        "brain", "tumor", "tumour", "cancer", "radiology", "imaging"]
        if any(w in combined for w in scan_keywords):
            return "scan"
        
        ecg_keywords = ["ecg", "ekg", "electrocardiogram", "heart rhythm", "heart rate"]
        if any(w in combined for w in ecg_keywords):
            return "ecg"
        
        prescription_keywords = ["prescription", "medicine", "tablet", "capsule", "dosage", "rx"]
        if any(w in combined for w in prescription_keywords):
            return "prescription"
        
        lab_keywords = ["lab report", "blood test", "cbc", "hemoglobin", "pathology", "test result"]
        if any(w in combined for w in lab_keywords):
            return "lab_report"
        
        wound_keywords = ["wound", "cut", "burn", "laceration", "injury", "bleeding", 
                         "bite", "stitches", "healing", "bruise"]
        if any(w in combined for w in wound_keywords):
            return "wound"
        
        eye_keywords = ["eye", "vision", "red eye", "pink eye", "swollen eye", "conjunctiv"]
        if any(w in combined for w in eye_keywords):
            return "eye"
        
        skin_keywords = ["skin", "rash", "acne", "eczema", "psoriasis", "mole", 
                        "bump", "spot", "itchy", "dermatitis", "pimple", "boil"]
        if any(w in combined for w in skin_keywords):
            return "skin"
        
        # Default to general — the universal prompt will auto-detect
        return "general"
    
    def _get_mime_type(self, image_data: bytes) -> str:
        """Detect MIME type from image bytes"""
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        elif image_data[:2] == b'\xff\xd8':
            return "image/jpeg"
        elif image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            return "image/webp"
        elif image_data[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        return "image/jpeg"
    
    async def analyze_image(
        self, 
        image_data: bytes, 
        context: str = "",
        image_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze a medical image — Groq primary, Gemini secondary, LLaVA fallback
        """
        # Try Groq Vision first (fastest, ~0.7s)
        result = await self._analyze_with_groq(image_data, context, image_type)
        if result and result.get("success"):
            return result
        
        # Try Gemini Vision second
        logger.warning("⚠️ Groq Vision failed, trying Gemini...")
        result = await self._analyze_with_gemini(image_data, context, image_type)
        if result and result.get("success"):
            return result
        
        # Fallback to LLaVA via Ollama
        logger.warning("⚠️ Gemini Vision failed, trying LLaVA fallback...")
        result = await self._analyze_with_ollama(image_data, context, image_type)
        if result and result.get("success"):
            return result
        
        return {
            "success": False,
            "error": "All image analysis providers failed",
            "raw_analysis": "Unable to analyze image. Please try again or consult a doctor directly.",
            "severity": "unknown",
            "recommended_action": "consult_doctor"
        }
    
    async def _analyze_with_groq(
        self, image_data: bytes, context: str, image_type: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze image using Groq Llama 4 Scout Vision (PRIMARY — fastest)"""
        if not self.groq_key:
            logger.warning("No Groq API key configured")
            return None
        
        try:
            detected_type = self._detect_image_type(context, image_type)
            prompt = IMAGE_PROMPTS.get(detected_type, IMAGE_PROMPTS["general"])
            
            if context:
                prompt += f"\n\nPatient's description: {context}"
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            mime_type = self._get_mime_type(image_data)
            
            payload = {
                "model": GROQ_VISION_MODEL,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }}
                    ]
                }],
                "max_tokens": 2048,
                "temperature": 0.3
            }
            
            logger.info(f"🖼️ Analyzing image with Groq Vision ({detected_type})...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code == 429:
                    logger.warning("Groq Vision rate limited")
                    return None
                
                response.raise_for_status()
                data = response.json()
            
            choices = data.get("choices", [])
            if not choices:
                logger.warning("Groq Vision returned no choices")
                return None
            
            analysis_text = choices[0].get("message", {}).get("content", "")
            
            if not analysis_text:
                logger.warning("Groq Vision returned empty text")
                return None
            
            logger.info(f"✅ Groq Vision analysis complete ({detected_type}): {len(analysis_text)} chars")
            
            result = self._parse_analysis(analysis_text, detected_type)
            result["raw_analysis"] = analysis_text
            result["success"] = True
            result["detected_type"] = detected_type
            result["model"] = "groq-llama4-scout-vision"
            
            return result
            
        except Exception as e:
            logger.error(f"Groq Vision error: {e}")
            return None
    
    async def _analyze_with_gemini(
        self, image_data: bytes, context: str, image_type: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze image using Gemini 2.0 Flash Vision (SECONDARY)"""
        if not self.gemini_key:
            logger.warning("No Gemini Vision API key configured")
            return None
        
        try:
            detected_type = self._detect_image_type(context, image_type)
            prompt = IMAGE_PROMPTS.get(detected_type, IMAGE_PROMPTS["general"])
            
            if context:
                prompt += f"\n\nPatient's description: {context}"
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            mime_type = self._get_mime_type(image_data)
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "topP": 0.9,
                    "maxOutputTokens": 1024
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            
            url = f"{GEMINI_VISION_URL}?key={self.gemini_key}"
            
            logger.info(f"🖼️ Analyzing image with Gemini Vision ({detected_type})...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 429:
                    logger.warning("Gemini Vision rate limited")
                    return None
                
                response.raise_for_status()
                data = response.json()
            
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini Vision returned no candidates")
                return None
            
            analysis_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not analysis_text:
                logger.warning("Gemini Vision returned empty text")
                return None
            
            logger.info(f"✅ Gemini Vision analysis complete ({detected_type}): {len(analysis_text)} chars")
            
            result = self._parse_analysis(analysis_text, detected_type)
            result["raw_analysis"] = analysis_text
            result["success"] = True
            result["detected_type"] = detected_type
            result["model"] = "gemini-2.0-flash-vision"
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini Vision error: {e}")
            return None
    
    async def _analyze_with_ollama(
        self, image_data: bytes, context: str, image_type: str
    ) -> Optional[Dict[str, Any]]:
        """Fallback: Analyze image using LLaVA via Ollama"""
        try:
            import ollama
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            detected_type = self._detect_image_type(context, image_type)
            prompt = IMAGE_PROMPTS.get(detected_type, IMAGE_PROMPTS["general"])
            
            if context:
                prompt += f"\n\nPatient notes: {context}"
            
            logger.info(f"🖼️ Analyzing image with LLaVA fallback ({detected_type})...")
            
            response = ollama.chat(
                model="llava:7b",
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }],
                options={"temperature": 0.3, "num_predict": 500}
            )
            
            analysis_text = response['message']['content']
            result = self._parse_analysis(analysis_text, detected_type)
            result["raw_analysis"] = analysis_text
            result["success"] = True
            result["detected_type"] = detected_type
            result["model"] = "llava-7b"
            
            logger.info(f"✅ LLaVA analysis complete ({detected_type})")
            return result
            
        except Exception as e:
            logger.error(f"LLaVA fallback error: {e}")
            return None
    
    def _parse_analysis(self, text: str, detected_type: str = "general") -> Dict[str, Any]:
        """Parse the AI response to extract structured information"""
        text_lower = text.lower()
        
        # Auto-detect actual image type from AI response
        actual_type = detected_type
        if "x-ray" in text_lower or "xray" in text_lower or "radiograph" in text_lower:
            actual_type = "xray"
        elif "ct scan" in text_lower or "computed tomography" in text_lower:
            actual_type = "ct_scan"
        elif "mri" in text_lower or "magnetic resonance" in text_lower:
            actual_type = "mri"
        elif "ultrasound" in text_lower or "sonograph" in text_lower:
            actual_type = "ultrasound"
        elif "ecg" in text_lower or "ekg" in text_lower or "electrocardiogram" in text_lower:
            actual_type = "ecg"
        elif "echocardiogram" in text_lower or "echo" in text_lower and "heart" in text_lower:
            actual_type = "echocardiogram"
        elif "prescription" in text_lower or "medication" in text_lower and "dosage" in text_lower:
            actual_type = "prescription"
        elif "lab report" in text_lower or "blood test" in text_lower or "cbc" in text_lower:
            actual_type = "lab_report"
        elif "skin" in text_lower and ("rash" in text_lower or "lesion" in text_lower or "dermat" in text_lower):
            actual_type = "skin"
        elif "wound" in text_lower or "laceration" in text_lower or "burn" in text_lower:
            actual_type = "wound"
        
        result = {
            "observations": "",
            "possible_conditions": [],
            "severity": "unknown",
            "recommended_action": "consult_doctor",
            "home_care_tips": [],
            "image_type": actual_type
        }
        
        # Determine severity
        if any(w in text_lower for w in ["critical", "emergency", "immediate", "life-threatening"]):
            result["severity"] = "critical"
            result["recommended_action"] = "emergency"
        elif any(w in text_lower for w in ["severe", "serious", "urgent", "malignant"]):
            result["severity"] = "severe"
            result["recommended_action"] = "see_specialist"
        elif any(w in text_lower for w in ["moderate", "concerning", "abnormal", "medical attention"]):
            result["severity"] = "moderate"
            result["recommended_action"] = "see_doctor"
        elif any(w in text_lower for w in ["mild", "minor", "home care", "self-care", "normal", "routine"]):
            result["severity"] = "mild"
            result["recommended_action"] = "self_care"
        
        # Scans and ECGs default to specialist if severity unknown
        if actual_type in ["xray", "ct_scan", "mri", "ultrasound", "ecg", "echocardiogram"] and result["severity"] == "unknown":
            result["severity"] = "requires_review"
            result["recommended_action"] = "see_specialist"
        
        # Extract first meaningful observation
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 20 and not line.startswith('#') and not line.startswith('⚠'):
                result["observations"] = line
                break
        
        return result
    
    async def analyze_from_file(self, file_path: str, context: str = "") -> Dict[str, Any]:
        """Analyze image from a file path"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            image_data = path.read_bytes()
            image_type = "general"
            filename_lower = path.name.lower()
            if any(w in filename_lower for w in ["skin", "rash", "acne"]):
                image_type = "skin"
            elif any(w in filename_lower for w in ["wound", "cut", "burn"]):
                image_type = "wound"
            elif any(w in filename_lower for w in ["eye"]):
                image_type = "eye"
            
            return await self.analyze_image(image_data, context, image_type)
            
        except Exception as e:
            logger.error(f"File analysis error: {e}")
            return {"success": False, "error": str(e)}


# Global instance
image_analyzer = ImageAnalysisService()
