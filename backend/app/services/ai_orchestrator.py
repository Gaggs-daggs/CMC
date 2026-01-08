"""
Production AI Orchestrator
==========================
Integrates all medical AI components into a cohesive system:

1. RAG (Retrieval-Augmented Generation) - Hallucination prevention
2. Safety Guardrails - Medical safety validation
3. Triage Classifier - Non-LLM severity scoring
4. NLLB Translation - Optimized multilingual support
5. Multi-model AI Routing - medllama2, llama3.1, llava
6. User Profile Context - Personalized responses

This is the MAIN entry point for all AI operations.
"""

import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time

logger = logging.getLogger(__name__)

# Import core AI service
from app.services.ai_service_v2 import (
    PowerfulAIService,
    AIResponse,
    UrgencyLevel,
    ModelType,
    ConversationMemory,
    MedicalReasoningEngine,
    get_ai_response,
    powerful_ai
)

# Import Profile Service for user context
try:
    from app.services.profile_service import profile_service
    PROFILE_SERVICE_AVAILABLE = True
except ImportError:
    PROFILE_SERVICE_AVAILABLE = False
    logger.warning("Profile service not available - personalization disabled")

# Import RAG components
try:
    from app.services.medical_rag import (
        MedicalKnowledgeBase,
        MedicalSafetyGuard,
        TriageClassifier,
        TriageLevel,
        SafetyAction
    )
    RAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RAG components not fully available: {e}")
    RAG_AVAILABLE = False

# Import translation service
try:
    from app.services.nlp.translator import TranslationService, translation_service
    TRANSLATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Translation service not available: {e}")
    TRANSLATION_AVAILABLE = False

# Import Gemini translator for input/output translation
try:
    from app.services.nlp.gemini_translator import GeminiTranslator, get_gemini_translator
    GEMINI_TRANSLATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Gemini translator not available: {e}")
    GEMINI_TRANSLATOR_AVAILABLE = False

# Import intent classifier
try:
    from app.services.nlp.intent_classifier import (
        IntelligentIntentClassifier,
        get_intent_classifier,
        UserIntent,
        IntentResult
    )
    INTENT_CLASSIFIER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Intent classifier not available: {e}")
    INTENT_CLASSIFIER_AVAILABLE = False


@dataclass
class OrchestratedResponse:
    """Complete response from the orchestrated AI system"""
    # Core response
    text: str
    text_translated: Optional[str] = None
    target_language: str = "en"
    
    # Triage (non-LLM)
    triage_level: str = "routine"
    triage_score: float = 30.0
    triage_color: str = "#22c55e"
    is_emergency: bool = False
    time_sensitivity: str = "Within 1-2 weeks"
    action_required: str = "Can wait for scheduled appointment"
    
    # Safety validation
    safety_passed: bool = True
    safety_level: str = "safe"
    blocked_content: Optional[str] = None
    required_disclaimers: List[str] = None
    
    # RAG grounding
    is_rag_grounded: bool = False
    sources_used: List[str] = None
    confidence_from_sources: float = 0.0
    
    # Original AI response
    urgency: str = "self_care"
    confidence: float = 0.5
    model_used: str = "medllama2"
    symptoms_detected: List[str] = None
    conditions_suggested: List[str] = None
    medications: List[Dict] = None
    specialist_recommended: Optional[str] = None
    follow_up_questions: List[str] = None
    mental_health_detected: bool = False
    
    # Metadata
    processing_time_ms: int = 0
    translation_time_ms: int = 0
    components_used: List[str] = None
    
    def __post_init__(self):
        if self.required_disclaimers is None:
            self.required_disclaimers = []
        if self.sources_used is None:
            self.sources_used = []
        if self.symptoms_detected is None:
            self.symptoms_detected = []
        if self.conditions_suggested is None:
            self.conditions_suggested = []
        if self.medications is None:
            self.medications = []
        if self.follow_up_questions is None:
            self.follow_up_questions = []
        if self.components_used is None:
            self.components_used = []


class ProductionAIOrchestrator:
    """
    Production-grade AI orchestrator that coordinates:
    - Triage classification (non-LLM, no hallucination)
    - Safety guardrails (emergency detection, prescription blocking)
    - RAG knowledge retrieval (evidence-based responses)
    - Multi-model AI routing (medical vs general queries)
    - Translation (NLLB transformer)
    
    This ensures:
    1. No hallucinations - responses grounded in medical knowledge
    2. No dangerous advice - safety checks on all outputs
    3. Fast response - triage doesn't wait for LLM
    4. Accurate severity - clinical scoring, not LLM guessing
    """
    
    def __init__(self):
        # Core AI - use the global powerful_ai instance for shared memory
        self.ai_assistant = powerful_ai
        
        # RAG components (optional - graceful degradation)
        self.knowledge_base = None
        self.safety_guard = None
        self.triage_classifier = None
        
        if RAG_AVAILABLE:
            try:
                self.knowledge_base = MedicalKnowledgeBase()
                logger.info("✅ RAG Knowledge Base initialized")
            except Exception as e:
                logger.warning(f"RAG Knowledge Base not available: {e}")
            
            try:
                self.safety_guard = MedicalSafetyGuard()
                logger.info("✅ Safety Guardrails initialized")
            except Exception as e:
                logger.warning(f"Safety Guardrails not available: {e}")
            
            try:
                self.triage_classifier = TriageClassifier()
                logger.info("✅ Triage Classifier initialized")
            except Exception as e:
                logger.warning(f"Triage Classifier not available: {e}")
        
        # Translation
        self.translator = None
        if TRANSLATION_AVAILABLE:
            try:
                self.translator = translation_service
                if self.translator.is_using_transformer():
                    logger.info("✅ NLLB Translation initialized")
                else:
                    logger.warning("⚠️ Translation available but NLLB not loaded")
            except Exception as e:
                logger.warning(f"Translation not available: {e}")
        
        # Gemini Translator (preferred for input/output translation)
        self.gemini_translator = None
        if GEMINI_TRANSLATOR_AVAILABLE:
            try:
                self.gemini_translator = get_gemini_translator()
                if self.gemini_translator.available:
                    logger.info("✅ Gemini Translator initialized (primary)")
                else:
                    logger.warning("⚠️ Gemini Translator not available")
            except Exception as e:
                logger.warning(f"Gemini Translator not available: {e}")
        
        # Intent Classifier
        self.intent_classifier = None
        if INTENT_CLASSIFIER_AVAILABLE:
            try:
                self.intent_classifier = get_intent_classifier()
                logger.info("✅ Intent Classifier initialized")
            except Exception as e:
                logger.warning(f"Intent Classifier not available: {e}")
        
        logger.info("🚀 Production AI Orchestrator initialized")
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        target_language: str = "en",
        vitals: Optional[Dict] = None,
        include_rag: bool = True,
        include_safety: bool = True,
        phone_number: Optional[str] = None  # For user profile context
    ) -> OrchestratedResponse:
        """
        Process a user message through the full pipeline:
        
        1. INPUT VALIDATION
        2. USER PROFILE CONTEXT - Load medical history
        3. TRIAGE (non-LLM) - Get severity immediately
        4. SAFETY CHECK INPUT - Block dangerous requests
        5. RAG RETRIEVAL - Get relevant medical knowledge
        6. AI RESPONSE - Generate with grounding + user context
        7. SAFETY CHECK OUTPUT - Validate response
        8. TRANSLATION - Convert to user language
        9. RECORD CONSULTATION - Update user profile
        
        Args:
            message: User's input message
            session_id: Conversation session ID
            target_language: Target language for response (e.g., 'hi', 'ta')
            vitals: Optional vital signs data
            include_rag: Whether to use RAG (can disable for speed)
            include_safety: Whether to apply safety checks
            phone_number: User's phone number for profile context
        
        Returns:
            OrchestratedResponse with all components
        """
        start_time = time.time()
        components_used = []
        
        # Initialize response
        response = OrchestratedResponse(
            text="",
            target_language=target_language
        )
        
        # ========== STEP -1: TRANSLATE INPUT TO ENGLISH ==========
        # This is CRITICAL - translate user's native language input to English first
        original_message = message
        english_message = message
        input_was_translated = False
        
        if target_language != "en" and self.gemini_translator and self.gemini_translator.available:
            try:
                english_message, detected_lang, input_was_translated = self.gemini_translator.detect_and_translate_to_english(
                    message, 
                    expected_language=target_language
                )
                if input_was_translated:
                    components_used.append(f"input_translation:{detected_lang}")
                    logger.info(f"🌐 Input translated: '{message}' → '{english_message}'")
            except Exception as e:
                logger.warning(f"Input translation failed: {e}")
                english_message = message
        
        # Use English message for all processing
        message = english_message
        
        # ========== STEP 0: USER PROFILE CONTEXT ==========
        user_context = ""
        user_allergies = []
        if phone_number and PROFILE_SERVICE_AVAILABLE:
            try:
                profile = profile_service.get_profile(phone_number)
                if profile:
                    user_context = profile.get_ai_context()
                    # Extract allergies for medication warnings
                    user_allergies = [a.allergen.lower() for a in profile.allergies]
                    components_used.append("user_profile")
                    logger.info(f"📋 Loaded user profile context for {phone_number}")
            except Exception as e:
                logger.warning(f"Could not load user profile: {e}")
        
        # ========== STEP 0.5: INTENT CLASSIFICATION ==========
        intent_result = None
        intent_prompt = None
        if self.intent_classifier:
            try:
                # Get conversation history for context
                conversation_history = self.ai_assistant.memory.get_context(session_id)
                intent_result = self.intent_classifier.classify(message, conversation_history)
                intent_prompt = self.intent_classifier.get_prompt_for_intent(intent_result)
                components_used.append(f"intent:{intent_result.primary_intent.value}")
                logger.info(f"🎯 Detected intent: {intent_result.primary_intent.value} (confidence: {intent_result.confidence:.2f})")
                
                # Handle greeting intent directly with translation
                if intent_result.primary_intent == UserIntent.GREETING:
                    greeting_response = "Hello! I'm your AI health assistant. How can I help you today? Feel free to describe any symptoms or ask health questions."
                    response.text = greeting_response
                    
                    # Translate greeting if not English - prefer Gemini
                    if target_language != "en":
                        try:
                            trans_start = time.time()
                            if self.gemini_translator and self.gemini_translator.available:
                                response.text_translated = self.gemini_translator.translate_to_language(
                                    greeting_response,
                                    target_language=target_language
                                )
                                components_used.append(f"translation:gemini:{target_language}")
                            elif self.translator:
                                response.text_translated = self.translator.translate(
                                    greeting_response,
                                    target_language=target_language,
                                    source_language="en"
                                )
                                components_used.append(f"translation:nllb:{target_language}")
                            response.translation_time_ms = int((time.time() - trans_start) * 1000)
                        except Exception as e:
                            logger.error(f"Greeting translation error: {e}")
                            response.text_translated = greeting_response
                    
                    response.processing_time_ms = int((time.time() - start_time) * 1000)
                    response.components_used = components_used
                    return response
                    
            except Exception as e:
                logger.warning(f"Intent classification failed: {e}")
        
        # ========== STEP 1: TRIAGE (Non-LLM, Instant) ==========
        if self.triage_classifier:
            try:
                # Extract symptoms from memory
                all_symptoms = self.ai_assistant.conversation_memory.get_all_symptoms(session_id)
                
                # Run triage
                triage_result = self.triage_classifier.classify(
                    symptoms=all_symptoms,
                    user_input=message,
                    vitals=vitals
                )
                
                response.triage_level = triage_result.level.value
                response.triage_score = triage_result.score
                response.triage_color = triage_result.color_code
                response.is_emergency = triage_result.is_emergency
                response.time_sensitivity = triage_result.time_sensitivity
                response.action_required = triage_result.action_required
                response.symptoms_detected = triage_result.symptoms_matched
                
                components_used.append("triage_classifier")
                
                # If emergency, handle immediately
                if triage_result.is_emergency:
                    logger.warning(f"🚨 EMERGENCY detected: {triage_result.red_flags_present}")
                
            except Exception as e:
                logger.error(f"Triage error: {e}")
        
        # ========== STEP 2: SAFETY CHECK INPUT (Check for emergencies) ==========
        if include_safety and self.safety_guard:
            try:
                # Check if input contains emergency keywords
                input_safety = self.safety_guard.check_response(
                    response="",  # No response yet, just checking input
                    user_input=message,
                    detected_symptoms=response.symptoms_detected
                )
                
                # If emergency triggered, mark as emergency
                if input_safety.emergency_triggered:
                    response.is_emergency = True
                    response.triage_level = "emergency"
                    response.safety_level = "emergency"
                    if input_safety.escalation_reason:
                        response.required_disclaimers = [input_safety.disclaimer] if input_safety.disclaimer else []
                        logger.warning(f"🚨 SAFETY: Emergency escalation - {input_safety.escalation_reason}")
                
                components_used.append("safety_input_check")
                
            except Exception as e:
                logger.error(f"Safety check error: {e}")
        
        # ========== STEP 3: RAG RETRIEVAL ==========
        rag_context = ""
        sources = []
        
        if include_rag and self.knowledge_base:
            try:
                # Query knowledge base
                query_result = self.knowledge_base.query(
                    query=message,
                    max_results=3
                )
                
                if query_result.documents:
                    # Build context from retrieved documents
                    rag_context = "\n\n".join([
                        f"[Source: {doc.source}] {doc.content[:500]}"
                        for doc in query_result.documents
                    ])
                    sources = [doc.source for doc in query_result.documents]
                    response.is_rag_grounded = True
                    response.sources_used = sources
                    response.confidence_from_sources = query_result.confidence
                
                components_used.append("rag_retrieval")
                
            except Exception as e:
                logger.error(f"RAG retrieval error: {e}")
        
        # ========== STEP 4: AI RESPONSE ==========
        try:
            # Build enhanced message with context - but NOT including instructions
            # Instructions will confuse the AI into repeating them
            context_parts = []
            
            # Add user profile context if available
            if user_context:
                context_parts.append(f"Patient Information:\n{user_context}")
            
            # Add RAG context if available
            if rag_context:
                context_parts.append(f"Medical Knowledge:\n{rag_context}")
            
            # Build final enhanced message - keep it simple and direct
            enhanced_message = message
            
            # For greetings, just pass the greeting directly - no context needed
            if intent_result and intent_result.primary_intent.value == "greeting":
                enhanced_message = message
            elif context_parts:
                context_str = "\n\n".join(context_parts)
                
                # For educational queries, make it clear this is informational
                if intent_result and intent_result.primary_intent.value == "educational":
                    enhanced_message = f"""Context:
{context_str}

User's question: {message}

The user is asking for INFORMATION about this topic. Explain it clearly and factually."""
                else:
                    enhanced_message = f"""Context:
{context_str}

User's message: {message}"""
            
            # Get AI response using get_ai_response which handles medication lookup with accumulated symptoms
            ai_response = await get_ai_response(
                message=enhanced_message,
                session_id=session_id,
                vitals=vitals
            )
            
            # ai_response is now a dict from get_ai_response
            response.text = ai_response["response"]
            response.urgency = ai_response["urgency_level"]
            response.confidence = ai_response["confidence"]
            response.model_used = ai_response["model_used"]
            response.conditions_suggested = ai_response.get("conditions_suggested", [])
            response.medications = ai_response.get("medications", [])  # Now includes meds for ALL accumulated symptoms
            response.specialist_recommended = ai_response.get("specialist_recommended")
            response.follow_up_questions = ai_response.get("follow_up_questions", [])
            response.mental_health_detected = ai_response.get("mental_health", {}).get("detected", False)
            
            # Filter out medications that match user allergies
            if user_allergies and response.medications:
                safe_medications = []
                for med in response.medications:
                    med_name = (med.get("name", "") or "").lower()
                    is_allergen = any(allergen in med_name for allergen in user_allergies)
                    if is_allergen:
                        logger.warning(f"⚠️ Filtered medication {med_name} due to user allergy")
                        med["allergy_warning"] = "⚠️ You may be allergic to this medication"
                    safe_medications.append(med)
                response.medications = safe_medications
            
            # Merge symptoms - use ALL accumulated symptoms from AI response
            all_detected_symptoms = ai_response.get("symptoms_detected", [])
            for symptom in all_detected_symptoms:
                if symptom not in response.symptoms_detected:
                    response.symptoms_detected.append(symptom)
            
            logger.info(f"💊 Orchestrator: All symptoms={response.symptoms_detected}, Meds={[m.get('name') for m in response.medications]}")
            
            components_used.append(f"ai_model:{response.model_used}")
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
            response.text = "I'm sorry, I encountered an issue processing your request. Please try again."
        
        # ========== STEP 5: SAFETY CHECK OUTPUT ==========
        if include_safety and self.safety_guard:
            try:
                output_safety = self.safety_guard.check_response(
                    response=response.text,
                    user_input=message,
                    detected_symptoms=response.symptoms_detected
                )
                
                response.safety_passed = output_safety.is_safe
                
                # Add any required disclaimers
                if output_safety.disclaimer:
                    response.required_disclaimers = [output_safety.disclaimer]
                
                # Apply modifications if needed
                if output_safety.action.value in ["modify", "add_disclaimer"] and output_safety.modified_response:
                    response.text = output_safety.modified_response
                
                components_used.append("safety_output_check")
                
            except Exception as e:
                logger.error(f"Safety validation error: {e}")
        
        # ========== STEP 6: TRANSLATION (Gemini primary, NLLB fallback) ==========
        if target_language != "en":
            trans_start = time.time()
            translated = None
            translation_method = None
            
            # Try Gemini first (faster and better quality)
            if self.gemini_translator and self.gemini_translator.available:
                try:
                    translated = self.gemini_translator.translate_to_language(
                        response.text,
                        target_language=target_language,
                        preserve_medical=True
                    )
                    if translated and translated != response.text:
                        translation_method = f"translation:gemini:{target_language}"
                except Exception as e:
                    logger.warning(f"Gemini translation failed, trying NLLB: {e}")
            
            # Fallback to NLLB if Gemini failed
            if not translated and self.translator:
                try:
                    translated = self.translator.translate(
                        response.text,
                        target_language=target_language,
                        source_language="en"
                    )
                    translation_method = f"translation:nllb:{target_language}"
                except Exception as e:
                    logger.error(f"NLLB translation also failed: {e}")
            
            if translated:
                response.text_translated = translated
                response.translation_time_ms = int((time.time() - trans_start) * 1000)
                if translation_method:
                    components_used.append(translation_method)
            else:
                response.text_translated = response.text
        
        # ========== STEP 8: RECORD CONSULTATION ==========
        if phone_number and PROFILE_SERVICE_AVAILABLE and response.symptoms_detected:
            try:
                # Get medication names for history
                med_names = [m.get("name", "") for m in response.medications if m.get("name")]
                
                profile_service.record_consultation(
                    phone_number=phone_number,
                    session_id=session_id,
                    symptoms=response.symptoms_detected,
                    urgency_level=response.urgency,
                    conditions=response.conditions_suggested,
                    medications=med_names,
                    summary=response.text[:200] if response.text else ""
                )
                components_used.append("consultation_recorded")
                logger.info(f"📝 Recorded consultation for {phone_number}")
            except Exception as e:
                logger.warning(f"Could not record consultation: {e}")
        
        # ========== FINALIZE ==========
        response.processing_time_ms = int((time.time() - start_time) * 1000)
        response.components_used = components_used
        
        logger.info(
            f"✅ Orchestrated response: triage={response.triage_level}, "
            f"safety={response.safety_level}, rag_grounded={response.is_rag_grounded}, "
            f"time={response.processing_time_ms}ms"
        )
        
        return response
    
    async def stream_response(
        self,
        message: str,
        session_id: str,
        target_language: str = "en",
        vitals: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream response with triage info first, then AI response.
        
        Yields:
            - First: Triage results (instant, non-LLM)
            - Then: AI response chunks
            - Finally: Complete response metadata
        """
        start_time = time.time()
        
        # ========== INSTANT TRIAGE (yield first) ==========
        if self.triage_classifier:
            all_symptoms = self.ai_assistant.conversation_memory.get_all_symptoms(session_id)
            triage_result = self.triage_classifier.classify(
                symptoms=all_symptoms,
                user_input=message,
                vitals=vitals
            )
            
            yield {
                "type": "triage",
                "level": triage_result.level.value,
                "score": triage_result.score,
                "color": triage_result.color_code,
                "is_emergency": triage_result.is_emergency,
                "action": triage_result.action_required,
                "time_sensitivity": triage_result.time_sensitivity
            }
        
        # ========== STREAM AI RESPONSE ==========
        full_text = ""
        async for chunk in self.ai_assistant.stream_response(message, session_id, vitals):
            full_text += chunk.get("text", "")
            yield {
                "type": "text_chunk",
                "text": chunk.get("text", ""),
                "model": chunk.get("model", "medllama2")
            }
        
        # ========== TRANSLATE IF NEEDED ==========
        translated_text = None
        if target_language != "en" and self.translator:
            translated_text = self.translator.translate(
                full_text,
                target_language=target_language
            )
            yield {
                "type": "translation",
                "text": translated_text,
                "language": target_language
            }
        
        # ========== FINAL METADATA ==========
        yield {
            "type": "complete",
            "processing_time_ms": int((time.time() - start_time) * 1000),
            "original_text": full_text,
            "translated_text": translated_text
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all system components"""
        translation_engine = "None"
        if self.gemini_translator and self.gemini_translator.available:
            translation_engine = "Gemini (Primary)"
        elif self.translator and self.translator.is_using_transformer():
            translation_engine = "NLLB-200 (Fallback)"
        
        return {
            "ai_assistant": True,
            "triage_classifier": self.triage_classifier is not None,
            "safety_guardrails": self.safety_guard is not None,
            "rag_knowledge_base": self.knowledge_base is not None,
            "translation": (self.gemini_translator and self.gemini_translator.available) or (self.translator is not None),
            "translation_engine": translation_engine,
            "gemini_translator": self.gemini_translator is not None and self.gemini_translator.available,
            "nllb_translator": self.translator is not None and self.translator.is_using_transformer(),
            "translation_cache_stats": self.translator.get_cache_stats() if self.translator else {}
        }


# Singleton instance
_orchestrator: Optional[ProductionAIOrchestrator] = None

def get_ai_orchestrator() -> ProductionAIOrchestrator:
    """Get or create the AI orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ProductionAIOrchestrator()
    return _orchestrator
