"""
Optimized AI Orchestrator
=========================
High-performance AI pipeline with:
- Parallel processing (diagnosis + response simultaneously)
- Session-based diagnosis caching
- Full user profile integration
- Smart symptom aggregation

Performance targets:
- First message (new symptoms): ~20-25s
- Follow-up (same symptoms): ~3-5s (cached)
- Simple questions: ~2-3s
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Thread pool for parallel AI calls (blocking Ollama operations)
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ai_worker")

# Import cache
from .diagnosis_cache import diagnosis_cache, DiagnosisCache

# Import profile model
try:
    from ..models.user_profile import UserProfile
    PROFILE_AVAILABLE = True
except ImportError:
    PROFILE_AVAILABLE = False
    logger.warning("UserProfile not available")

# Import symptom normalizer
try:
    from .symptom_analyzer.symptom_normalizer import SymptomNormalizer
    symptom_normalizer = SymptomNormalizer()
    NORMALIZER_AVAILABLE = True
except ImportError:
    NORMALIZER_AVAILABLE = False
    logger.warning("SymptomNormalizer not available, using fallback")


@dataclass
class OptimizedResponse:
    """Response from the optimized orchestrator"""
    response: str
    symptoms_detected: List[str]
    diagnoses: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    urgency_level: str
    confidence: float
    user_preferences: Optional[Dict[str, Any]]
    processing_time_ms: int
    cache_hit: bool
    model_used: str


class OptimizedAIOrchestrator:
    """
    High-performance AI orchestrator with caching and parallel processing.
    
    Features:
    - Diagnosis caching per session
    - Parallel AI calls (diagnosis + response)
    - User profile integration for personalization
    - Age-appropriate responses
    - Allergy-safe medication filtering
    """
    
    def __init__(self):
        self.cache = diagnosis_cache
        logger.info("✅ OptimizedAIOrchestrator initialized")
    
    # ========== SYMPTOM EXTRACTION ==========
    
    def _extract_symptoms_fast(self, text: str) -> List[str]:
        """Fast symptom extraction using regex and keywords"""
        if NORMALIZER_AVAILABLE:
            try:
                return symptom_normalizer.normalize(text)
            except Exception as e:
                logger.warning(f"Normalizer failed: {e}")
        
        # Fallback: simple keyword matching
        text_lower = text.lower()
        symptoms = []
        
        symptom_keywords = [
            "headache", "fever", "cough", "cold", "pain", "ache",
            "nausea", "vomiting", "diarrhea", "fatigue", "tired",
            "dizziness", "weakness", "rash", "itching", "swelling",
            "breathing", "chest pain", "stomach", "throat", "ear",
            "back pain", "joint pain", "muscle", "insomnia", "anxiety",
            "blood", "bleeding", "infection", "allergy", "sore"
        ]
        
        for keyword in symptom_keywords:
            if keyword in text_lower:
                symptoms.append(keyword)
        
        return symptoms
    
    def _aggregate_symptoms(
        self, 
        current_message: str, 
        conversation_history: List[Dict]
    ) -> List[str]:
        """Aggregate symptoms from current message and history"""
        all_symptoms = set()
        
        # From current message
        current_symptoms = self._extract_symptoms_fast(current_message)
        all_symptoms.update(current_symptoms)
        
        # From last 5 user messages in history
        for msg in conversation_history[-10:]:
            if msg.get("role") == "user":
                hist_symptoms = self._extract_symptoms_fast(msg.get("content", ""))
                all_symptoms.update(hist_symptoms)
        
        return list(all_symptoms)
    
    # ========== DIAGNOSIS (CACHED) ==========
    
    async def _run_diagnosis(
        self, 
        symptoms: List[str], 
        profile_context: str
    ) -> Tuple[List[Dict], str]:
        """
        Run AI diagnosis (gemma2:9b for quality).
        Returns (diagnoses, urgency_level)
        """
        if not symptoms:
            return [], "self_care"
        
        loop = asyncio.get_event_loop()
        
        def diagnose_sync():
            try:
                import ollama
                
                # Build prompt with profile context
                prompt = f"""You are a medical diagnosis AI. Based on the symptoms and patient info, provide possible conditions.

PATIENT CONTEXT:
{profile_context if profile_context else "No profile information available."}

SYMPTOMS: {', '.join(symptoms)}

Provide exactly 3-5 possible conditions in this JSON format:
[
  {{"condition": "Condition Name", "confidence": 85, "urgency": "routine", "description": "Brief description"}},
  {{"condition": "Another Condition", "confidence": 65, "urgency": "self_care", "description": "Brief description"}}
]

Urgency levels: emergency, urgent, doctor_soon, routine, self_care
Confidence: 0-100 (percentage)

Return ONLY valid JSON array, no other text."""

                response = ollama.chat(
                    model="gemma2:9b",
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "temperature": 0.3,
                        "num_predict": 500,
                        "num_ctx": 2048
                    }
                )
                
                # Parse JSON response
                import json
                import re
                
                content = response["message"]["content"]
                
                # Extract JSON from response
                json_match = re.search(r'\[[\s\S]*\]', content)
                if json_match:
                    diagnoses = json.loads(json_match.group())
                    
                    # Determine overall urgency
                    urgency_priority = {
                        "emergency": 5, "urgent": 4, "doctor_soon": 3,
                        "routine": 2, "self_care": 1
                    }
                    max_urgency = "self_care"
                    max_priority = 1
                    
                    for d in diagnoses:
                        u = d.get("urgency", "self_care")
                        p = urgency_priority.get(u, 1)
                        if p > max_priority:
                            max_priority = p
                            max_urgency = u
                    
                    return diagnoses, max_urgency
                
                return [], "self_care"
                
            except Exception as e:
                logger.error(f"Diagnosis error: {e}")
                return [], "self_care"
        
        return await loop.run_in_executor(_executor, diagnose_sync)
    
    # ========== RESPONSE GENERATION ==========
    
    async def _generate_response(
        self,
        message: str,
        symptoms: List[str],
        diagnoses: List[Dict],
        profile_context: str,
        conversation_history: List[Dict]
    ) -> str:
        """
        Generate empathetic response (llama3.2:3b for speed).
        Uses full diagnosis context for high-quality, relevant responses.
        """
        loop = asyncio.get_event_loop()
        
        def generate_sync():
            try:
                import ollama
                
                # Build detailed diagnosis context
                diagnosis_info = "No specific diagnosis yet - gathering more information."
                if diagnoses:
                    diag_lines = []
                    for i, d in enumerate(diagnoses[:3], 1):
                        condition = d.get('condition', 'Unknown')
                        confidence = d.get('confidence', 50)
                        urgency = d.get('urgency', 'routine')
                        description = d.get('description', '')
                        diag_lines.append(
                            f"{i}. {condition} (confidence: {confidence}%, urgency: {urgency})"
                            f"\n   Description: {description}"
                        )
                    diagnosis_info = "\n".join(diag_lines)
                
                # Build comprehensive system prompt
                system_prompt = f"""You are a caring, knowledgeable medical AI assistant named CMC Health Assistant.

PATIENT PROFILE:
{profile_context if profile_context else "No profile information available."}

DETECTED SYMPTOMS: {', '.join(symptoms) if symptoms else 'Not specified yet'}

DIAGNOSIS ANALYSIS:
{diagnosis_info}

YOUR RESPONSE MUST:
1. DIRECTLY answer the patient's question or concern
2. Reference the specific conditions identified above
3. Provide specific, actionable advice based on the diagnosis
4. Recommend appropriate home remedies or treatments
5. Clearly state urgency level (when to see a doctor)
6. Be warm, empathetic, and reassuring
7. If patient is elderly (60+), use simpler, clearer language
8. If child, recommend parental supervision for any treatment
9. NEVER suggest medications patient is allergic to
10. Keep response focused and concise (2-3 paragraphs)

IMPORTANT: Answer the CURRENT question directly. If they ask "what should I do?" - give specific action steps.
If they ask about medications, recommend safe ones. If they ask about a doctor, advise on urgency."""

                # Build messages with history
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add last 4 conversation messages for context
                for msg in conversation_history[-4:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                
                # Add current message
                messages.append({"role": "user", "content": message})
                
                response = ollama.chat(
                    model="llama3.2:3b",
                    messages=messages,
                    options={
                        "temperature": 0.7,
                        "num_predict": 250,
                        "num_ctx": 2048
                    }
                )
                
                return response["message"]["content"]
                
            except Exception as e:
                logger.error(f"Response generation error: {e}")
                return "I understand you're experiencing some health concerns. Could you please tell me more about your symptoms so I can help you better?"
        
        return await loop.run_in_executor(_executor, generate_sync)
    
    # ========== MEDICATION LOOKUP ==========
    
    async def _get_medications(
        self,
        symptoms: List[str],
        diagnoses: List[Dict],
        user_allergies: List[str]
    ) -> List[Dict]:
        """
        Get medications for symptoms, filtered by allergies.
        """
        loop = asyncio.get_event_loop()
        
        def get_meds_sync():
            try:
                from .ai_medication_service import get_smart_medications
                
                # Get medications
                meds = get_smart_medications(
                    symptoms=symptoms,
                    diagnoses=diagnoses[:3]
                )
                
                # Filter by allergies
                if user_allergies:
                    allergy_names = [a.lower() for a in user_allergies]
                    safe_meds = []
                    
                    for med in meds:
                        med_name = med.get("name", "").lower()
                        is_safe = True
                        
                        for allergen in allergy_names:
                            if allergen in med_name or med_name in allergen:
                                logger.info(f"⚠️ Filtered {med['name']} (allergy: {allergen})")
                                is_safe = False
                                break
                        
                        if is_safe:
                            safe_meds.append(med)
                    
                    return safe_meds
                
                return meds
                
            except Exception as e:
                logger.error(f"Medication lookup error: {e}")
                return []
        
        return await loop.run_in_executor(_executor, get_meds_sync)
    
    # ========== MAIN PROCESSING ==========
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        conversation_history: List[Dict],
        user_profile: Optional[Any] = None,
        language: str = "en"
    ) -> OptimizedResponse:
        """
        Process message with caching and parallel execution.
        
        Flow:
        1. Extract symptoms from message + history
        2. Check diagnosis cache
        3. If cache miss: run diagnosis + response in parallel
        4. If cache hit: only generate response
        5. Get medications (filtered by allergies)
        6. Build response with user preferences
        """
        start_time = time.time()
        cache_hit = False
        
        # Build profile context
        profile_context = ""
        user_allergies = []
        user_preferences = None
        
        if user_profile and PROFILE_AVAILABLE:
            try:
                profile_context = user_profile.get_ai_context()
                user_allergies = [a.allergen for a in user_profile.allergies]
                
                # Get TTS preferences based on age
                tts_prefs = user_profile.get_tts_preferences()
                user_preferences = {
                    "tts_gender": tts_prefs.get("gender", "female"),
                    "tts_speed": tts_prefs.get("speed", "normal"),
                    "age_group": user_profile.get_age_group(),
                    "has_allergies": len(user_allergies) > 0,
                    "has_conditions": len(user_profile.medical_conditions) > 0
                }
                
                logger.info(f"👤 Profile: {user_profile.name or 'User'}, age: {user_profile.age}, allergies: {user_allergies}")
            except Exception as e:
                logger.warning(f"Profile error: {e}")
        
        # Step 1: Aggregate symptoms
        symptoms = self._aggregate_symptoms(message, conversation_history)
        logger.info(f"🔍 Symptoms detected: {symptoms}")
        
        # Step 2: Check cache
        cached = self.cache.get(session_id, symptoms, profile_context)
        
        if cached:
            # Cache HIT - only generate response
            cache_hit = True
            logger.info(f"⚡ Cache HIT for session {session_id[:8]}...")
            
            diagnoses = cached.diagnoses
            urgency_level = cached.urgency_level
            medications = cached.medications
            
            # Generate response with cached diagnosis - full context available!
            logger.info(f"📋 Using cached diagnosis: {[d.get('condition') for d in diagnoses[:3]]}")
            
            response = await self._generate_response(
                message=message,
                symptoms=symptoms,
                diagnoses=diagnoses,
                profile_context=profile_context,
                conversation_history=conversation_history
            )
            
        else:
            # Cache MISS - run diagnosis FIRST, then generate quality response
            logger.info(f"🔄 Cache MISS - running diagnosis first for quality response...")
            
            # Step 1: Run diagnosis first (this is the slower part ~15-20s)
            diagnoses, urgency_level = await self._run_diagnosis(symptoms, profile_context)
            logger.info(f"📋 Diagnosis complete: {[d.get('condition') for d in diagnoses[:3]]}")
            
            # Step 2: Get medications in parallel with response generation
            meds_task = asyncio.create_task(
                self._get_medications(
                    symptoms=symptoms,
                    diagnoses=diagnoses,
                    user_allergies=user_allergies
                )
            )
            
            # Step 3: Generate response WITH full diagnosis context
            response_task = asyncio.create_task(
                self._generate_response(
                    message=message,
                    symptoms=symptoms,
                    diagnoses=diagnoses,  # Now we have real diagnosis!
                    profile_context=profile_context,
                    conversation_history=conversation_history
                )
            )
            
            # Wait for both
            medications, response = await asyncio.gather(meds_task, response_task)
            
            # Cache the diagnosis for follow-up messages
            self.cache.set(
                session_id=session_id,
                symptoms=symptoms,
                diagnoses=diagnoses,
                medications=medications,
                urgency_level=urgency_level,
                profile_context=profile_context
            )
            logger.info(f"💾 Diagnosis cached for session {session_id[:8]}")
        
        # Calculate processing time
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Calculate confidence from diagnoses
        confidence = 0.5
        if diagnoses:
            top_confidence = diagnoses[0].get("confidence", 50)
            confidence = top_confidence / 100.0
        
        logger.info(f"✅ Response ready in {elapsed_ms}ms (cache_hit={cache_hit})")
        
        return OptimizedResponse(
            response=response,
            symptoms_detected=symptoms,
            diagnoses=diagnoses,
            medications=medications,
            urgency_level=urgency_level,
            confidence=confidence,
            user_preferences=user_preferences,
            processing_time_ms=elapsed_ms,
            cache_hit=cache_hit,
            model_used="gemma2:9b+llama3.2:3b"
        )
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()


# Global instance
optimized_orchestrator = OptimizedAIOrchestrator()


def get_optimized_orchestrator() -> OptimizedAIOrchestrator:
    """Get the global optimized orchestrator instance"""
    return optimized_orchestrator
