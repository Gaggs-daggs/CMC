"""
Conversation routes for health assistant
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

from ..services.ai_service import AIService

router = APIRouter(prefix="/conversation", tags=["conversation"])
logger = logging.getLogger(__name__)

sessions = {}
ai_service = AIService()


class StartConversationRequest(BaseModel):
    user_id: str
    language: str = "en"


class StartConversationResponse(BaseModel):
    session_id: str
    greeting: str


class MessageRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"


class TriageInfo(BaseModel):
    level: str = "self_care"
    is_emergency: bool = False
    reasoning: str = ""
    action_required: str = ""


class MentalHealthInfo(BaseModel):
    detected: bool = False
    type: str = ""  # depression, anxiety, crisis
    severity: str = ""
    support_message: str = ""
    resources: list = []


class MessageResponse(BaseModel):
    response: str
    symptoms_detected: list = []
    urgency_level: str = "low"
    medications: list = []
    follow_up_questions: list = []
    triage: TriageInfo = None
    mental_health: MentalHealthInfo = None


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    try:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "user_id": request.user_id,
            "language": request.language,
            "messages": [],
            "symptoms": []
        }
        
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
        
        return StartConversationResponse(session_id=session_id, greeting=greeting)
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    try:
        session = sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        history = session.get("messages", [])
        
        ai_response = await ai_service.get_ai_response(
            user_message=request.message,
            conversation_history=history,
            language=request.language
        )
        
        session["messages"].append({"role": "user", "content": request.message})
        session["messages"].append({"role": "assistant", "content": ai_response["response"]})
        
        if ai_response.get("symptoms_detected"):
            session["symptoms"].extend(ai_response["symptoms_detected"])
        
        return MessageResponse(
            response=ai_response["response"],
            symptoms_detected=ai_response.get("symptoms_detected", []),
            urgency_level=ai_response.get("urgency_level", "low"),
            medications=ai_response.get("medications", []),
            follow_up_questions=ai_response.get("follow_up_questions", []),
            triage=TriageInfo(**ai_response.get("triage", {})) if ai_response.get("triage") else None,
            mental_health=MentalHealthInfo(**ai_response.get("mental_health", {})) if ai_response.get("mental_health") else None
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


@router.delete("/{session_id}")
async def end_conversation(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session ended"}
    raise HTTPException(status_code=404, detail="Session not found")
