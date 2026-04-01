"""
SMS Gateway Routes using textbee.dev
Handles incoming SMS messages via webhook and sends AI health responses back.
Enables zero-internet users to access Atlas Health guidance via plain SMS.

Flow:
1. User sends SMS to the Android phone running textbee app
2. textbee forwards the SMS to our webhook endpoint
3. Our AI processes the symptom/health query
4. We reply back via textbee send-sms API
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import logging
import os
import time
import asyncio
from datetime import datetime

# Import AI service
from ..services.ai_service_v2 import powerful_ai, get_ai_response
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS Gateway"])

# ── textbee.dev Configuration ──
TEXTBEE_API_KEY = os.getenv("TEXTBEE_API_KEY", "a0ee7a1b-5bfe-4d52-b105-46c389ea872a")
TEXTBEE_DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID", "69993535deb3cd9fe7a93e7a")
TEXTBEE_BASE_URL = "https://api.textbee.dev/api/v1"

# Store SMS user sessions (phone_number → session_id)
sms_sessions: Dict[str, str] = {}

# Track processed SMS IDs to prevent duplicates
processed_sms_ids: set = set()

# Track in-flight requests per sender to prevent parallel processing
_inflight_senders: set = set()

# Shared httpx client for reuse (avoids creating new connections each time)
_sms_http_client: Optional[httpx.AsyncClient] = None


def _get_http_client() -> httpx.AsyncClient:
    """Get or create a shared httpx client for textbee API calls"""
    global _sms_http_client
    if _sms_http_client is None or _sms_http_client.is_closed:
        _sms_http_client = httpx.AsyncClient(timeout=30.0)
    return _sms_http_client

# Indian language detection keywords
HINDI_KEYWORDS = ["मुझे", "मेरा", "दर्द", "बुखार", "सिर", "पेट", "खांसी", "सर्दी", "दवा", "बीमार", "तबीयत", "डॉक्टर"]
TAMIL_KEYWORDS = ["எனக்கு", "வலி", "காய்ச்சல", "தலை", "வயிறு", "இருமல்", "சளி", "மருந்து"]
TELUGU_KEYWORDS = ["నాకు", "నొప్పి", "జ్వరం", "తలనొప్పి", "కడుపు", "దగ్గు"]
BENGALI_KEYWORDS = ["আমার", "ব্যথা", "জ্বর", "মাথা", "পেট", "কাশি"]

# SMS character limit (standard SMS = 160 chars, but we allow longer for concatenated SMS)
SMS_MAX_LENGTH = 450  # ~3 concatenated SMS segments


def detect_language_from_text(text: str) -> str:
    """Detect language from SMS text using character sets and keywords"""
    # Check for Devanagari script (Hindi/Marathi)
    if any('\u0900' <= c <= '\u097F' for c in text):
        return "hi"
    # Tamil
    if any('\u0B80' <= c <= '\u0BFF' for c in text):
        return "ta"
    # Telugu
    if any('\u0C00' <= c <= '\u0C7F' for c in text):
        return "te"
    # Bengali/Assamese
    if any('\u0980' <= c <= '\u09FF' for c in text):
        return "bn"
    # Kannada
    if any('\u0C80' <= c <= '\u0CFF' for c in text):
        return "kn"
    # Malayalam
    if any('\u0D00' <= c <= '\u0D7F' for c in text):
        return "ml"
    # Gujarati
    if any('\u0A80' <= c <= '\u0AFF' for c in text):
        return "gu"
    # Punjabi (Gurmukhi)
    if any('\u0A00' <= c <= '\u0A7F' for c in text):
        return "pa"
    # Odia
    if any('\u0B00' <= c <= '\u0B7F' for c in text):
        return "or"
    # Urdu (Arabic script)
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return "ur"
    # Default to English
    return "en"


def truncate_for_sms(text: str, max_length: int = SMS_MAX_LENGTH) -> str:
    """Truncate AI response to fit SMS length, keeping it meaningful"""
    if len(text) <= max_length:
        return text
    
    # Try to cut at a sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    
    cut_point = max(last_period, last_newline)
    if cut_point > max_length * 0.5:  # Only cut at boundary if it's past halfway
        truncated = truncated[:cut_point + 1]
    else:
        truncated = truncated[:max_length - 3] + "..."
    
    return truncated


def format_sms_response(ai_response: Dict[str, Any], language: str) -> str:
    """Format AI response for SMS (concise, no markdown)"""
    parts = []
    
    # Main response text
    response_text = ai_response.get("response_translated") or ai_response.get("response", "")
    
    # Clean up markdown formatting for SMS
    response_text = response_text.replace("**", "")
    response_text = response_text.replace("*", "")
    response_text = response_text.replace("##", "")
    response_text = response_text.replace("#", "")
    response_text = response_text.replace("- ", "• ")
    
    parts.append(response_text)
    
    # Add urgency warning if needed
    urgency = ai_response.get("urgency_level", "self_care")
    if urgency in ["emergency", "urgent"]:
        if language == "hi":
            parts.append("\n⚠️ कृपया तुरंत डॉक्टर से मिलें!")
        elif language == "ta":
            parts.append("\n⚠️ உடனடியாக மருத்துவரை அணுகவும்!")
        else:
            parts.append("\n⚠️ Please see a doctor immediately!")
    
    # Add disclaimer
    if language == "hi":
        parts.append("\n📋 यह AI सलाह है, डॉक्टर की जगह नहीं।")
    elif language == "ta":
        parts.append("\n📋 இது AI ஆலோசனை, மருத்துவரின் மாற்று அல்ல.")
    else:
        parts.append("\n📋 This is AI guidance, not a substitute for medical advice.")
    
    # Add Atlas branding
    parts.append("\n— Atlas Health AI 🏥")
    
    full_response = "\n".join(parts)
    return truncate_for_sms(full_response)


async def send_sms_via_textbee(to_number: str, message: str) -> bool:
    """Send SMS reply via textbee.dev API"""
    url = f"{TEXTBEE_BASE_URL}/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
    
    headers = {
        "x-api-key": TEXTBEE_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "recipients": [to_number],
        "message": message
    }
    
    try:
        client = _get_http_client()
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ SMS sent to {to_number}: {message[:50]}...")
            return True
        else:
            logger.error(f"❌ textbee API error {response.status_code}: {response.text}")
            return False
                
    except Exception as e:
        logger.error(f"❌ Failed to send SMS via textbee: {e}")
        return False


async def process_sms_message(sender: str, message: str) -> str:
    """Process incoming SMS through Atlas Health AI and return response text.
    Has a 15-second timeout to prevent stalling when AI APIs are rate-limited."""
    start_time = time.time()
    
    # Get or create session for this phone number
    if sender not in sms_sessions:
        import uuid
        session_id = f"sms_{uuid.uuid4().hex[:8]}"
        sms_sessions[sender] = session_id
        logger.info(f"📱 New SMS session for {sender}: {session_id}")
    else:
        session_id = sms_sessions[sender]
    
    # Detect language
    language = detect_language_from_text(message)
    logger.info(f"📱 SMS from {sender} (lang={language}): {message[:80]}")
    
    # Handle special commands
    message_lower = message.strip().lower()
    if message_lower in ["hi", "hello", "help", "start", "namaste", "नमस्ते"]:
        if language == "hi":
            return ("🏥 Atlas Health AI में आपका स्वागत है!\n"
                    "अपने लक्षण SMS करें और AI स्वास्थ्य सलाह पाएं।\n"
                    "उदाहरण: 'मुझे सिरदर्द और बुखार है'\n"
                    "— Atlas Health AI")
        elif language == "ta":
            return ("🏥 Atlas Health AI-க்கு வரவேற்கிறோம்!\n"
                    "உங்கள் அறிகுறிகளை SMS செய்து AI ஆரோக்கிய ஆலோசனை பெறுங்கள்.\n"
                    "— Atlas Health AI")
        else:
            return ("🏥 Welcome to Atlas Health AI!\n"
                    "SMS your symptoms and get AI health guidance.\n"
                    "Example: 'I have a headache and fever'\n"
                    "Reply RESET to start a new conversation.\n"
                    "— Atlas Health AI")
    
    if message_lower in ["reset", "new", "clear"]:
        # Reset session
        import uuid
        sms_sessions[sender] = f"sms_{uuid.uuid4().hex[:8]}"
        if language == "hi":
            return "🔄 नई बातचीत शुरू! अपने लक्षण बताएं। — Atlas Health AI"
        else:
            return "🔄 New conversation started! Describe your symptoms. — Atlas Health AI"
    
    try:
        # Get AI response with a 15-second timeout to prevent stalling
        ai_result = await asyncio.wait_for(
            get_ai_response(
                message=message,
                session_id=session_id,
                language=language
            ),
            timeout=15.0
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"⚡ SMS AI response in {processing_time}ms for {sender}")
        
        # Format for SMS
        return format_sms_response(ai_result, language)
    
    except asyncio.TimeoutError:
        logger.warning(f"⏰ SMS AI response timed out after 15s for {sender}")
        if language == "hi":
            return "⏰ AI सर्वर व्यस्त है। कृपया 1 मिनट बाद दोबारा भेजें। — Atlas Health AI"
        else:
            return "⏰ AI server is busy. Please resend your message in 1 minute. — Atlas Health AI"
        
    except Exception as e:
        logger.error(f"❌ AI processing error for SMS from {sender}: {e}")
        if language == "hi":
            return "❌ क्षमा करें, कुछ गड़बड़ हुई। कृपया दोबारा कोशिश करें। — Atlas Health AI"
        else:
            return "❌ Sorry, something went wrong. Please try again. — Atlas Health AI"


# ── Webhook Endpoint (receives incoming SMS from textbee) ──

async def _process_and_reply_sms(sender: str, message: str, sms_id: str):
    """Background task: process the SMS through AI and send reply.
    Runs after the webhook has already returned 200 to textbee."""
    try:
        # Prevent parallel AI calls for the same sender
        if sender in _inflight_senders:
            logger.info(f"⏭️ Skipping — already processing SMS for {sender}")
            return
        _inflight_senders.add(sender)
        
        reply_text = await process_sms_message(sender, message.strip())
        sent = await send_sms_via_textbee(sender, reply_text)
        logger.info(f"{'✅' if sent else '❌'} SMS reply to {sender} ({len(reply_text)} chars)")
    except Exception as e:
        logger.error(f"❌ Background SMS processing error for {sender}: {e}", exc_info=True)
    finally:
        _inflight_senders.discard(sender)


@router.post("/incoming")
async def sms_incoming_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for textbee.dev
    Receives incoming SMS and sends AI health response back via SMS.
    
    Returns 200 IMMEDIATELY to avoid textbee timeouts, then processes in background.
    
    textbee webhook payload:
    {
        "smsId": "...",
        "sender": "+91XXXXXXXXXX",
        "message": "I have a headache",
        "receivedAt": "2026-02-21T...",
        "deviceId": "...",
        "webhookEvent": "MESSAGE_RECEIVED"
    }
    """
    try:
        data = await request.json()
        
        # Extract fields from textbee webhook payload
        sms_id = data.get("smsId", "")
        sender = data.get("sender", "")
        message = data.get("message", "")
        webhook_event = data.get("webhookEvent", "")
        
        # FAST EXIT: Only process MESSAGE_RECEIVED events
        # textbee sends floods of MESSAGE_SENT / MESSAGE_DELIVERED for every SMS segment — ignore silently
        if webhook_event != "MESSAGE_RECEIVED":
            return {"status": "ok"}
        
        logger.info(f"📨 SMS received from {sender}: {message[:80]}")
        
        # Deduplicate by smsId
        if sms_id and sms_id in processed_sms_ids:
            logger.info(f"⏭️ Duplicate SMS skipped: {sms_id}")
            return {"status": "duplicate"}
        
        if sms_id:
            processed_sms_ids.add(sms_id)
            # Keep set manageable
            if len(processed_sms_ids) > 1000:
                processed_sms_ids.clear()
        
        if not sender or not message:
            return {"status": "error", "reason": "missing sender or message"}
        
        # Skip if already processing a message from this sender
        if sender in _inflight_senders:
            logger.info(f"⏭️ Already processing for {sender}, skipping")
            return {"status": "busy", "reason": "already processing for this sender"}
        
        # Process in background — return 200 immediately so textbee doesn't timeout/retry
        background_tasks.add_task(_process_and_reply_sms, sender, message, sms_id)
        
        return {"status": "accepted", "sms_id": sms_id}
        
    except Exception as e:
        logger.error(f"❌ SMS webhook error: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}


# ── Manual SMS Send Endpoint (for testing) ──

class SendSMSRequest(BaseModel):
    to: str
    message: str


@router.post("/send")
async def send_sms(request: SendSMSRequest):
    """
    Manually send an SMS via textbee (for testing purposes).
    """
    success = await send_sms_via_textbee(request.to, request.message)
    return {
        "success": success,
        "to": request.to,
        "message_length": len(request.message)
    }


# ── Test/Simulate Endpoint (for local testing without textbee) ──

class SimulateSMSRequest(BaseModel):
    sender: str = "+919876543210"
    message: str


@router.post("/simulate")
async def simulate_sms(request: SimulateSMSRequest):
    """
    Simulate an incoming SMS locally (no textbee needed).
    Processes through AI but returns the reply instead of sending SMS.
    Useful for testing the SMS flow during development.
    """
    reply = await process_sms_message(request.sender, request.message)
    return {
        "sender": request.sender,
        "original_message": request.message,
        "ai_reply": reply,
        "reply_length": len(reply),
        "language_detected": detect_language_from_text(request.message)
    }


# ── Health Check ──

@router.get("/status")
async def sms_status():
    """Check SMS gateway configuration status"""
    return {
        "status": "active",
        "gateway": "textbee.dev",
        "device_id": TEXTBEE_DEVICE_ID[:8] + "..." if TEXTBEE_DEVICE_ID else "not set",
        "api_key_set": bool(TEXTBEE_API_KEY),
        "active_sessions": len(sms_sessions),
        "webhook_url": "/api/v1/sms/incoming",
        "instructions": {
            "1": "Set webhook URL in textbee dashboard to: https://<your-ngrok-url>/api/v1/sms/incoming",
            "2": "Select event: MESSAGE_RECEIVED",
            "3": "Send SMS to the phone running textbee app",
            "4": "AI will auto-reply with health guidance"
        }
    }
