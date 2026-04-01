"""
Conversation routes for health assistant
Powered by Production AI Orchestrator with:
- RAG (Retrieval-Augmented Generation)
- Safety Guardrails
- Non-LLM Triage Classification
- NLLB Translation (No Google)
- Multi-model AI routing
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import logging
import json

# Try to use the new orchestrator, fallback to old service
# DISABLED: Using old ai_service_v2 for stability
# try:
#     from ..services.ai_orchestrator import get_ai_orchestrator, ProductionAIOrchestrator
#     ORCHESTRATOR_AVAILABLE = True
# except ImportError:
#     ORCHESTRATOR_AVAILABLE = False
ORCHESTRATOR_AVAILABLE = False  # Force use of ai_service_v2

# Import session helpers for database persistence
try:
    from .session_routes import get_or_create_session, save_message_to_session, update_session_symptoms
    SESSION_STORAGE_AVAILABLE = True
except ImportError:
    SESSION_STORAGE_AVAILABLE = False

# Fallback to old service
from ..services.ai_service_v2 import powerful_ai, get_ai_response

router = APIRouter(prefix="/conversation", tags=["conversation"])
logger = logging.getLogger(__name__)

sessions: Dict[str, Dict[str, Any]] = {}


class StartConversationRequest(BaseModel):
    user_id: str  # This will be the phone number
    language: str = "en"
    name: Optional[str] = None  # Optional name for profile


class StartConversationResponse(BaseModel):
    session_id: str
    greeting: str
    translation_engine: Optional[str] = None
    is_returning_user: bool = False
    profile_name: Optional[str] = None


class MessageRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"
    vitals: Optional[Dict] = None  # Optional vitals data
    image_base64: Optional[str] = None  # Optional image for analysis


class TriageInfo(BaseModel):
    level: str = "self_care"
    score: float = 30.0
    color: str = "#4ade80"
    is_emergency: bool = False
    time_sensitivity: str = "Within 1-2 weeks"
    action_required: str = "Can wait for scheduled appointment"
    reasoning: Optional[str] = None


class SafetyInfo(BaseModel):
    passed: bool = True
    level: str = "safe"
    disclaimers: List[str] = []


class RAGInfo(BaseModel):
    is_grounded: bool = False
    sources: List[str] = []
    confidence: float = 0.0


class MentalHealthInfo(BaseModel):
    detected: bool = False
    type: str = ""
    severity: str = ""
    support_message: str = ""
    resources: list = []


class DiagnosisInfo(BaseModel):
    """Individual diagnosis with confidence"""
    condition: str
    confidence: float
    description: str = ""
    urgency: str = "self_care"
    specialist: Optional[str] = None


class UserPreferences(BaseModel):
    """User preferences based on profile for UI customization"""
    tts_gender: str = "female"
    tts_speed: str = "normal"
    age_group: str = "adult"
    has_allergies: bool = False
    has_conditions: bool = False


class MessageResponse(BaseModel):
    response: str
    response_translated: Optional[str] = None
    language: str = "en"
    symptoms_detected: list = []
    urgency_level: str = "self_care"
    confidence: float = 0.5
    model_used: str = "medllama2"
    reasoning: Optional[str] = None
    conditions_suggested: list = []
    diagnoses: List[DiagnosisInfo] = []  # NEW: Multiple diagnoses with confidence
    specialist_recommended: Optional[str] = None
    medications: list = []
    follow_up_questions: list = []  # Now populated!
    needs_more_info: bool = False  # NEW: Flag to show we need more info
    triage: Optional[TriageInfo] = None
    safety: Optional[SafetyInfo] = None
    rag: Optional[RAGInfo] = None
    mental_health: Optional[MentalHealthInfo] = None
    processing_time_ms: int = 0
    translation_time_ms: int = 0
    components_used: List[str] = []
    user_preferences: Optional[UserPreferences] = None  # NEW: Profile-based preferences


# Import profile service for user context
try:
    from ..services.profile_service import profile_service
    PROFILE_SERVICE_AVAILABLE = True
except ImportError:
    PROFILE_SERVICE_AVAILABLE = False


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    try:
        session_id = str(uuid.uuid4())
        
        # Check/create user profile (user_id is phone number)
        is_returning_user = False
        profile_name = None
        
        if PROFILE_SERVICE_AVAILABLE:
            profile, is_new = profile_service.get_or_create_profile(
                phone_number=request.user_id,
                name=request.name,
                preferred_language=request.language
            )
            is_returning_user = not is_new
            profile_name = profile.name
            
            if is_returning_user:
                logger.info(f"👋 Returning user: {profile_name or request.user_id}")
            else:
                logger.info(f"🆕 New user registered: {request.user_id}")
        
        # IMPORTANT: Clear any old AI conversation memory for this new session
        # This ensures new sessions start fresh without old context
        try:
            powerful_ai.clear_conversation(session_id)
            logger.info(f"🧹 Cleared AI memory for new session: {session_id}")
        except Exception as e:
            logger.warning(f"Could not clear AI memory: {e}")
        
        sessions[session_id] = {
            "user_id": request.user_id,  # Phone number
            "phone_number": request.user_id,  # Explicit for clarity
            "language": request.language,
            "messages": [],
            "symptoms": [],
            "is_returning_user": is_returning_user
        }
        
        # Save session to database for sidebar persistence
        if SESSION_STORAGE_AVAILABLE:
            try:
                await get_or_create_session(
                    user_phone=request.user_id,
                    session_id=session_id,
                    language=request.language
                )
                logger.info(f"💾 Session saved to database: {session_id}")
            except Exception as e:
                logger.warning(f"Could not save session to database: {e}")
        
        # Get translation engine info
        translation_engine = None
        if ORCHESTRATOR_AVAILABLE:
            orchestrator = get_ai_orchestrator()
            status = orchestrator.get_system_status()
            translation_engine = status.get("translation_engine")
        
        # Personalized greetings for returning users
        if is_returning_user and profile_name:
            greetings = {
                "en": f"Welcome back, {profile_name}! How can I help you today?",
                "hi": f"वापस स्वागत है, {profile_name}! आज मैं आपकी कैसे मदद कर सकता हूं?",
                "ta": f"மீண்டும் வரவேற்கிறோம், {profile_name}! இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?",
                "te": f"తిరిగి స్వాగతం, {profile_name}! ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?",
            }
        else:
            greetings = {
                "en": "Hello! I'm your AI health assistant. Please describe your symptoms in detail.",
                "hi": "नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। कृपया अपने लक्षण विस्तार से बताएं।",
                "ta": "வணக்கம்! நான் உங்கள் AI சுகாதார உதவியாளர். உங்கள் அறிகுறிகளை விரிவாக சொல்லுங்கள்.",
                "te": "నమస్కారం! నేను మీ AI ఆరోగ్య సహాయకుడిని. దయచేసి మీ లక్షణాలను వివరంగా చెప్పండి.",
                "bn": "নমস্কার! আমি আপনার AI স্বাস্থ্য সহকারী। অনুগ্রহ করে আপনার উপসর্গগুলি বিস্তারিত বলুন।",
                "kn": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಆರೋಗ್ಯ ಸಹಾಯಕ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ವಿವರವಾಗಿ ಹೇಳಿ.",
                "ml": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ AI ആരോഗ്യ സഹായി ആണ്. നിങ്ങളുടെ ലക്ഷണങ്ങൾ വിശദമായി പറയൂ.",
                "gu": "નમસ્તે! હું તમારો AI સ્વાસ્થ્ય સહાયક છું. કૃપા કરીને તમારા લક્ષણો વિગતવાર જણાવો.",
                "mr": "नमस्कार! मी तुमचा AI आरोग्य सहाय्यक आहे. कृपया तुमची लक्षणे सविस्तर सांगा.",
                "es": "¡Hola! Soy tu asistente de salud con IA. Describe tus síntomas en detalle."
            }
        
        greeting = greetings.get(request.language, greetings["en"])
        logger.info(f"Started conversation: {session_id}")
        
        return StartConversationResponse(
            session_id=session_id, 
            greeting=greeting,
            translation_engine=translation_engine,
            is_returning_user=is_returning_user,
            profile_name=profile_name
        )
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    try:
        session = sessions.get(request.session_id)
        
        # If session not in memory, try to load from PostgreSQL
        if not session and SESSION_STORAGE_AVAILABLE:
            try:
                db_session = await get_or_create_session(
                    user_phone="",  # Will be fetched from DB
                    session_id=request.session_id,
                    language=request.language
                )
                if db_session:
                    # Restore session to in-memory dict
                    restored_messages = db_session.get("messages", [])
                    restored_symptoms = db_session.get("symptoms", [])
                    
                    sessions[request.session_id] = {
                        "user_id": db_session.get("user_phone") or db_session.get("phone_number", ""),
                        "phone_number": db_session.get("user_phone") or db_session.get("phone_number", ""),
                        "language": db_session.get("language", request.language),
                        "messages": restored_messages,
                        "symptoms": restored_symptoms,
                        "is_returning_user": True
                    }
                    session = sessions[request.session_id]
                    
                    # CRITICAL: Also restore AI conversation memory so follow-ups work
                    try:
                        for msg in restored_messages[-10:]:  # Last 10 messages for context
                            role = msg.get("role", "user")
                            content = msg.get("content", "")
                            if content:
                                powerful_ai.memory.add_message(request.session_id, role, content)
                                if role == "user":
                                    powerful_ai.memory.track_symptoms(request.session_id, content)
                        # Also restore tracked symptoms
                        if restored_symptoms:
                            powerful_ai.memory.add_symptoms(request.session_id, restored_symptoms)
                        logger.info(f"🧠 Restored AI memory: {len(restored_messages)} msgs, {len(restored_symptoms)} symptoms")
                    except Exception as mem_err:
                        logger.warning(f"Could not restore AI memory: {mem_err}")
                    
                    logger.info(f"🔄 Restored session from database: {request.session_id}")
            except Exception as e:
                logger.warning(f"Could not restore session from database: {e}")
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get phone number from session for profile context
        phone_number = session.get("phone_number") or session.get("user_id")
        
        # Get user preferences from profile for personalization (TTS speed, etc.)
        user_prefs = None
        if phone_number and PROFILE_SERVICE_AVAILABLE:
            try:
                profile = profile_service.get_profile(phone_number)
                if profile:
                    tts_prefs = profile.get_tts_preferences()
                    user_prefs = UserPreferences(
                        tts_gender=tts_prefs.get("gender", "female"),
                        tts_speed=tts_prefs.get("speed", "normal"),
                        age_group=profile.get_age_group(),
                        has_allergies=len(profile.allergies) > 0,
                        has_conditions=len(profile.medical_conditions) > 0
                    )
                    logger.info(f"👤 User preferences: age_group={user_prefs.age_group}, tts_speed={user_prefs.tts_speed}")
            except Exception as e:
                logger.warning(f"Could not load user preferences: {e}")
        
        # Use orchestrator if available (has RAG, Safety, Triage)
        if ORCHESTRATOR_AVAILABLE:
            orchestrator = get_ai_orchestrator()
            
            result = await orchestrator.process_message(
                message=request.message,
                session_id=request.session_id,
                target_language=request.language,
                vitals=request.vitals,
                phone_number=phone_number  # Pass phone for user context
            )
            
            # Store in session
            session["messages"].append({"role": "user", "content": request.message})
            session["messages"].append({"role": "assistant", "content": result.text})
            
            if result.symptoms_detected:
                session["symptoms"].extend(result.symptoms_detected)
            
            # Save messages to database for sidebar persistence
            if SESSION_STORAGE_AVAILABLE:
                try:
                    # Save user message
                    await save_message_to_session(
                        session_id=request.session_id,
                        role="user",
                        content=request.message
                    )
                    # Save assistant response
                    await save_message_to_session(
                        session_id=request.session_id,
                        role="assistant",
                        content=result.text_translated or result.text,
                        metadata={
                            "model_used": result.model_used,
                            "symptoms": result.symptoms_detected
                        }
                    )
                    # Update symptoms and urgency
                    if result.symptoms_detected or result.urgency:
                        await update_session_symptoms(
                            session_id=request.session_id,
                            symptoms=result.symptoms_detected or [],
                            urgency_level=result.urgency
                        )
                    logger.info(f"💾 Messages saved to database for session: {request.session_id}")
                except Exception as e:
                    logger.warning(f"Could not save messages to database: {e}")
            
            # Build response with all info
            return MessageResponse(
                response=result.text,
                response_translated=result.text_translated,
                language=request.language,
                symptoms_detected=result.symptoms_detected or [],
                urgency_level=result.urgency,
                confidence=result.confidence,
                model_used=result.model_used,
                reasoning=None,
                conditions_suggested=result.conditions_suggested or [],
                diagnoses=[DiagnosisInfo(**d) for d in (result.diagnoses or [])],
                specialist_recommended=result.specialist_recommended,
                medications=result.medications or [],
                follow_up_questions=result.follow_up_questions or [],
                needs_more_info=result.needs_more_info,
                triage=TriageInfo(
                    level=result.triage_level,
                    score=result.triage_score,
                    color=result.triage_color,
                    is_emergency=result.is_emergency,
                    time_sensitivity=result.time_sensitivity,
                    action_required=result.action_required
                ),
                safety=SafetyInfo(
                    passed=result.safety_passed,
                    level=result.safety_level,
                    disclaimers=result.required_disclaimers or []
                ),
                rag=RAGInfo(
                    is_grounded=result.is_rag_grounded,
                    sources=result.sources_used or [],
                    confidence=result.confidence_from_sources
                ),
                mental_health=MentalHealthInfo(
                    detected=result.mental_health_detected
                ) if result.mental_health_detected else None,
                processing_time_ms=result.processing_time_ms,
                translation_time_ms=result.translation_time_ms,
                components_used=result.components_used or [],
                user_preferences=user_prefs  # Include profile-based preferences for frontend
            )
        
        # Fallback to old service
        ai_response = await get_ai_response(
            message=request.message,
            session_id=request.session_id,
            language=request.language,
            vitals=request.vitals,
            image_base64=request.image_base64
        )
        
        # Store in session
        session["messages"].append({"role": "user", "content": request.message})
        session["messages"].append({"role": "assistant", "content": ai_response["response"]})
        
        if ai_response.get("symptoms_detected"):
            session["symptoms"].extend(ai_response["symptoms_detected"])
        
        # Save messages to database for sidebar persistence (fallback path)
        if SESSION_STORAGE_AVAILABLE:
            try:
                await save_message_to_session(
                    session_id=request.session_id,
                    role="user",
                    content=request.message
                )
                await save_message_to_session(
                    session_id=request.session_id,
                    role="assistant",
                    content=ai_response.get("response_translated") or ai_response["response"],
                    metadata={"symptoms": ai_response.get("symptoms_detected", [])}
                )
                if ai_response.get("symptoms_detected") or ai_response.get("urgency_level"):
                    await update_session_symptoms(
                        session_id=request.session_id,
                        symptoms=ai_response.get("symptoms_detected", []),
                        urgency_level=ai_response.get("urgency_level", "self_care")
                    )
            except Exception as e:
                logger.warning(f"Could not save messages to database: {e}")
        
        # Build triage info
        triage_info = None
        if ai_response.get("triage"):
            triage_data = ai_response["triage"]
            triage_info = TriageInfo(
                level=triage_data.get("level", "self_care"),
                color=triage_data.get("color", "#4ade80"),
                is_emergency=triage_data.get("level") == "emergency",
                reasoning=ai_response.get("reasoning"),
                action_required=""
            )
        
        # Build mental health info
        mental_health_info = None
        if ai_response.get("mental_health", {}).get("detected"):
            mental_health_info = MentalHealthInfo(
                detected=True,
                type="",
                severity="",
                support_message="",
                resources=[]
            )
        
        return MessageResponse(
            response=ai_response["response"],
            response_translated=ai_response.get("response_translated"),
            language=request.language,
            symptoms_detected=ai_response.get("symptoms_detected", []),
            urgency_level=ai_response.get("urgency_level", "self_care"),
            confidence=ai_response.get("confidence", 0.5),
            model_used=ai_response.get("model_used", "medllama2"),
            reasoning=ai_response.get("reasoning"),
            conditions_suggested=ai_response.get("conditions_suggested", []),
            diagnoses=[DiagnosisInfo(**d) for d in ai_response.get("diagnoses", [])],
            specialist_recommended=ai_response.get("specialist_recommended"),
            medications=ai_response.get("medications", []),
            follow_up_questions=ai_response.get("follow_up_questions", []),
            needs_more_info=ai_response.get("needs_more_info", False),
            triage=triage_info,
            mental_health=mental_health_info,
            processing_time_ms=ai_response.get("processing_time_ms", 0),
            user_preferences=user_prefs  # Include profile-based preferences for frontend
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": session.get("messages", [])}


@router.post("/message/stream")
async def stream_message(request: MessageRequest):
    """Stream AI response for real-time UI updates"""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def generate():
        full_response = ""
        async for chunk in powerful_ai.stream_chat(
            session_id=request.session_id,
            message=request.message,
            language=request.language
        ):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        # Save to session after streaming
        session["messages"].append({"role": "user", "content": request.message})
        session["messages"].append({"role": "assistant", "content": full_response})
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.delete("/{session_id}")
async def end_conversation(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        # Also clear from AI service memory
        powerful_ai.clear_conversation(session_id)
        return {"message": "Session ended"}
    raise HTTPException(status_code=404, detail="Session not found")
