"""
Gemini Medicine Service
Dynamic medicine recommendations using Google Gemini API

Features:
- Tracks symptoms across entire conversation
- Evaluates every message for symptom changes
- Diagnoses possible diseases from cumulative symptoms
- Recommends medicines with full compositions
- Updates dynamically when symptoms change
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import google.generativeai as genai

logger = logging.getLogger(__name__)

# Gemini API Configuration - Load from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Medicine Recommendation Prompt - Framed as educational/informational
MEDICINE_PROMPT = """You are a pharmaceutical information assistant providing EDUCATIONAL information about medicines available in India. You are NOT prescribing - just providing factual drug information that is publicly available.

IMPORTANT: This is for EDUCATIONAL purposes only. Always recommend consulting a doctor.

## PATIENT CONTEXT (for relevance):
- Age: {age}
- Gender: {gender}
- Known Allergies: {allergies}
- Current Medications: {current_medications}
- Existing Conditions: {conditions}

## SYMPTOMS DISCUSSED:
{symptoms_history}

## CURRENT QUERY:
{current_message}

## YOUR TASK:
Provide EDUCATIONAL pharmaceutical information:
1. Identify symptoms mentioned
2. List what conditions commonly present with these symptoms
3. Provide FACTUAL information about medicines commonly used in India for such conditions
4. Include drug compositions (this is public pharmaceutical data)

## RESPONSE FORMAT (JSON):
{{
    "symptoms_identified": ["symptom1", "symptom2"],
    "all_symptoms": ["complete symptom list"],
    "possible_conditions": [
        {{
            "name": "Condition name",
            "likelihood": "common/possible/rare",
            "description": "Brief description"
        }}
    ],
    "medicine_information": [
        {{
            "brand_name": "Indian brand name",
            "generic_name": "Generic/Salt name",
            "composition": [
                {{"ingredient": "Name", "strength": "Amount"}}
            ],
            "drug_class": "Category of medicine",
            "common_uses": ["What it's typically used for"],
            "typical_dosage": "Standard adult dosage",
            "administration": "How to take",
            "common_side_effects": ["Side effects"],
            "contraindications": ["When not to use"],
            "alternatives": ["Other brands with similar composition"],
            "otc_status": "OTC/Prescription required",
            "approximate_price": "Price range in INR"
        }}
    ],
    "important_notes": [
        "Always consult a qualified doctor before taking any medication",
        "This information is for educational purposes only"
    ],
    "when_to_see_doctor": ["Red flag symptoms requiring immediate medical attention"],
    "general_advice": ["Lifestyle and home care suggestions"]
}}

## RULES:
1. Provide FACTUAL pharmaceutical information only
2. Always include disclaimer about consulting doctors
3. For serious conditions (HIV, cancer, heart disease, etc.), emphasize doctor consultation is mandatory
4. Use Indian brand names (Crocin, Dolo, Combiflam, Allegra, etc.)
5. Include accurate compositions from pharmaceutical data
6. Mark clearly if prescription is required
7. Provide 2-3 medicine options with alternatives

Respond with ONLY valid JSON."""


class GeminiMedicineService:
    """
    Dynamic medicine recommendation service using Gemini API
    Tracks symptoms per session and updates recommendations in real-time
    """
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = None
        self.session_symptoms: Dict[str, Dict] = {}  # session_id -> symptom tracking
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API with adjusted safety settings for medical content"""
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY not set. Medicine service will use fallback.")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            
            # Safety settings to allow medical/health content
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            # Generation config for consistent JSON output
            generation_config = {
                "temperature": 0.3,  # Lower temperature for more factual responses
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,
            }
            
            self.model = genai.GenerativeModel(
                'gemini-flash-latest',
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            logger.info("✅ Gemini Medicine Service initialized with medical safety settings")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.model = None
    
    def _get_session_data(self, session_id: str) -> Dict:
        """Get or create session symptom tracking data"""
        if session_id not in self.session_symptoms:
            self.session_symptoms[session_id] = {
                "symptoms": [],
                "messages": [],
                "last_diagnosis": None,
                "last_medicines": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        return self.session_symptoms[session_id]
    
    def _update_session(self, session_id: str, new_symptoms: List[str], 
                        diagnosis: Dict, medicines: List[Dict]):
        """Update session with new data"""
        session = self._get_session_data(session_id)
        
        # Add new symptoms (avoid duplicates)
        for symptom in new_symptoms:
            if symptom.lower() not in [s.lower() for s in session["symptoms"]]:
                session["symptoms"].append(symptom)
        
        session["last_diagnosis"] = diagnosis
        session["last_medicines"] = medicines
        session["updated_at"] = datetime.now().isoformat()
    
    async def evaluate_message(
        self,
        session_id: str,
        message: str,
        user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a message for symptoms and get medicine recommendations
        Called for EVERY message in the conversation
        
        Args:
            session_id: Unique conversation session ID
            message: Current user message
            user_profile: User's medical profile (age, allergies, etc.)
        
        Returns:
            Dictionary with symptoms, diagnosis, and medicine recommendations
        """
        session = self._get_session_data(session_id)
        session["messages"].append({
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # If Gemini not available, use fallback
        if not self.model:
            return self._fallback_evaluation(session_id, message)
        
        # Build prompt with context
        profile = user_profile or {}
        prompt = MEDICINE_PROMPT.format(
            age=profile.get("age", "Unknown"),
            gender=profile.get("gender", "Unknown"),
            allergies=", ".join(profile.get("allergies", [])) or "None reported",
            current_medications=", ".join(profile.get("current_medications", [])) or "None",
            conditions=", ".join(profile.get("conditions", [])) or "None reported",
            symptoms_history=", ".join(session["symptoms"]) if session["symptoms"] else "No symptoms reported yet",
            current_message=message
        )
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON response (remove markdown code blocks if present)
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            # Parse JSON response
            result = json.loads(response_text)
            
            # Update session with new data
            new_symptoms = result.get("new_symptoms_found", [])
            diagnosis = result.get("diagnosis", {})
            medicines = result.get("medicines", [])
            
            self._update_session(session_id, new_symptoms, diagnosis, medicines)
            
            # Add session context to response
            result["session_id"] = session_id
            result["total_symptoms"] = session["symptoms"]
            result["symptom_count"] = len(session["symptoms"])
            result["evaluation_time"] = datetime.now().isoformat()
            
            logger.info(f"🏥 Gemini evaluation complete - {len(new_symptoms)} new symptoms, {len(medicines)} medicines")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response was: {response_text[:500]}")
            return self._fallback_evaluation(session_id, message)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_evaluation(session_id, message)
    
    def _fallback_evaluation(self, session_id: str, message: str) -> Dict[str, Any]:
        """Enhanced fallback using local medicine database when Gemini is unavailable or restricted"""
        from .medicine_database import match_symptoms_to_diseases, SYMPTOM_KEYWORDS
        
        session = self._get_session_data(session_id)
        
        # Extract symptoms from message
        message_lower = message.lower()
        found_symptoms = []
        
        for symptom_key, keywords in SYMPTOM_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    if symptom_key not in found_symptoms:
                        found_symptoms.append(symptom_key)
                    break
        
        # Add to session symptoms
        for symptom in found_symptoms:
            if symptom not in session["symptoms"]:
                session["symptoms"].append(symptom)
        
        # Match symptoms to diseases and get medicines
        all_symptoms = session["symptoms"]
        matched = match_symptoms_to_diseases(all_symptoms)
        
        medicines = []
        possible_conditions = []
        
        for match in matched[:3]:  # Top 3 matches
            disease_data = match["data"]
            possible_conditions.append({
                "name": match["disease"].replace("_", " ").title(),
                "likelihood": "common" if match["match_score"] > 2 else "possible",
                "description": f"Matches {match['match_score']} symptoms"
            })
            
            # Add medicines from this disease
            for med in disease_data.get("medicines", []):
                if med not in medicines:
                    medicines.append(med)
        
        # Limit medicines to avoid overwhelming
        medicines = medicines[:4]
        
        return {
            "symptoms_identified": found_symptoms,
            "all_symptoms": all_symptoms,
            "possible_conditions": possible_conditions,
            "medicine_information": medicines,
            "important_notes": [
                "This information is from our local database (AI evaluation unavailable)",
                "Always consult a qualified doctor before taking any medication",
                "If symptoms persist or worsen, seek medical attention immediately"
            ],
            "when_to_see_doctor": ["If symptoms don't improve in 2-3 days", "If you develop new symptoms"],
            "general_advice": ["Stay hydrated", "Get adequate rest"],
            "fallback_mode": True,
            "session_id": session_id,
            "total_symptoms": all_symptoms,
            "symptom_count": len(all_symptoms)
        }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of symptoms and recommendations for a session"""
        session = self._get_session_data(session_id)
        
        return {
            "session_id": session_id,
            "total_symptoms": session["symptoms"],
            "symptom_count": len(session["symptoms"]),
            "current_diagnosis": session["last_diagnosis"],
            "current_medicines": session["last_medicines"],
            "message_count": len(session["messages"]),
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        if session_id in self.session_symptoms:
            del self.session_symptoms[session_id]
            logger.info(f"Cleared medicine session: {session_id}")
    
    def add_symptom_manually(self, session_id: str, symptom: str):
        """Manually add a symptom to session tracking"""
        session = self._get_session_data(session_id)
        if symptom.lower() not in [s.lower() for s in session["symptoms"]]:
            session["symptoms"].append(symptom)
            session["updated_at"] = datetime.now().isoformat()


# Global instance
gemini_medicine_service = GeminiMedicineService()
