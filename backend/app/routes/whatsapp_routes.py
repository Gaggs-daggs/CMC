"""
WhatsApp Business API Webhook Routes
Handles incoming messages from WhatsApp and sends AI responses
Supports voice messages in all Indian languages with auto-detection
"""

from fastapi import APIRouter, Request, Response, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import httpx
import logging
import os
import tempfile
from datetime import datetime

# Import your AI service and config
from ..services.ai_service_v2 import powerful_ai, get_ai_response
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Indian language mapping for responses
INDIAN_LANGUAGES = {
    "hi": {"name": "Hindi", "greeting": "नमस्ते", "processing": "कृपया प्रतीक्षा करें..."},
    "ta": {"name": "Tamil", "greeting": "வணக்கம்", "processing": "தயவுசெய்து காத்திருங்கள்..."},
    "te": {"name": "Telugu", "greeting": "నమస్కారం", "processing": "దయచేసి వేచి ఉండండి..."},
    "kn": {"name": "Kannada", "greeting": "ನಮಸ್ಕಾರ", "processing": "ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ..."},
    "ml": {"name": "Malayalam", "greeting": "നമസ്കാരം", "processing": "ദയവായി കാത്തിരിക്കുക..."},
    "bn": {"name": "Bengali", "greeting": "নমস্কার", "processing": "অনুগ্রহ করে অপেক্ষা করুন..."},
    "gu": {"name": "Gujarati", "greeting": "નમસ્તે", "processing": "કૃપા કરીને રાહ જુઓ..."},
    "mr": {"name": "Marathi", "greeting": "नमस्कार", "processing": "कृपया प्रतीक्षा करा..."},
    "pa": {"name": "Punjabi", "greeting": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "processing": "ਕਿਰਪਾ ਕਰਕੇ ਉਡੀਕ ਕਰੋ..."},
    "or": {"name": "Odia", "greeting": "ନମସ୍କାର", "processing": "ଦୟାକରି ଅପେକ୍ଷା କରନ୍ତୁ..."},
    "as": {"name": "Assamese", "greeting": "নমস্কাৰ", "processing": "অনুগ্ৰহ কৰি অপেক্ষা কৰক..."},
    "ur": {"name": "Urdu", "greeting": "السلام علیکم", "processing": "براہ کرم انتظار کریں..."},
    "en": {"name": "English", "greeting": "Hello", "processing": "Please wait..."},
}

# Whisper model (loaded lazily)
whisper_model = None

# WhatsApp API Configuration - using settings from config.py
WHATSAPP_CONFIG = {
    "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID or "993295210525051",
    "access_token": settings.WHATSAPP_ACCESS_TOKEN or "",
    "verify_token": settings.WHATSAPP_VERIFY_TOKEN or "cmc_health_verify_2024",
    "api_version": "v22.0"
}

# Log token status (without revealing the actual token)
logger.info(f"WhatsApp Config loaded - Token present: {bool(WHATSAPP_CONFIG['access_token'])}, Length: {len(WHATSAPP_CONFIG['access_token']) if WHATSAPP_CONFIG['access_token'] else 0}")

# Store user sessions (in production, use Redis or database)
user_sessions = {}

# Track processed message IDs to prevent duplicates
processed_messages = set()

# Store detected language per user
user_languages = {}


def get_whisper_model():
    """Load Whisper model lazily (medium model - best accuracy for Indian languages)"""
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            logger.info("🎤 Loading Whisper model (medium) for Indian language support...")
            whisper_model = whisper.load_model("medium")
            logger.info("✅ Whisper medium model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            return None
    return whisper_model


async def download_whatsapp_media(media_id: str) -> bytes:
    """Download media file from WhatsApp"""
    access_token = get_access_token()
    
    # First, get the media URL
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get media URL
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        media_url = response.json().get("url")
        
        if not media_url:
            raise Exception("No media URL returned")
        
        # Download the actual file
        file_response = await client.get(media_url, headers=headers)
        file_response.raise_for_status()
        return file_response.content


async def transcribe_voice_message(audio_data: bytes) -> tuple[str, str]:
    """
    Transcribe voice message using Whisper medium model.
    Strategy: Try auto-detect first, then retry with explicit language hints if result is garbage.
    Returns: (transcribed_text, detected_language)
    """
    model = get_whisper_model()
    if model is None:
        return "", "en"
    
    try:
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        logger.info("🎤 Transcribing voice message with Whisper medium...")
        
        # ATTEMPT 1: Auto language detection (no initial_prompt bias)
        result = model.transcribe(
            temp_path, 
            task="transcribe", 
            fp16=False,
        )
        
        text = result.get("text", "").strip()
        detected_lang = result.get("language", "en")
        
        logger.info(f"🎤 Auto-detect result: lang={detected_lang}, text='{text[:80]}'")
        
        # Check if transcription looks like garbage (random English words for Indian audio)
        # Indicators: very short, detected wrong language, or text has no real content
        is_garbage = (
            len(text) < 3 or 
            detected_lang in ["ja", "zh", "ko", "ru", "ar", "fr", "de", "it", "es", "pt", "nl", "pl"] or
            (detected_lang == "en" and len(text) < 15 and not any(c.isalpha() for c in text))
        )
        
        # ATTEMPT 2: If garbage or misdetected, try Tamil (most common for your region)
        if is_garbage or detected_lang in ["ja", "zh", "ko", "ru"]:
            logger.info(f"🔄 Retrying with Tamil hint (auto-detect gave: {detected_lang})")
            result = model.transcribe(temp_path, language="ta", task="transcribe", fp16=False)
            text_ta = result.get("text", "").strip()
            if len(text_ta) >= 3:
                text = text_ta
                detected_lang = "ta"
                logger.info(f"🎤 Tamil retry result: '{text[:80]}'")
        
        # ATTEMPT 3: If still poor, try Hindi
        if len(text) < 3:
            logger.info("🔄 Retrying with Hindi hint...")
            result = model.transcribe(temp_path, language="hi", task="transcribe", fp16=False)
            text = result.get("text", "").strip()
            detected_lang = "hi"
        
        # ATTEMPT 4: If still poor, try English explicitly
        if len(text) < 3:
            logger.info("🔄 Retrying with English hint...")
            result = model.transcribe(temp_path, language="en", task="transcribe", fp16=False)
            text = result.get("text", "").strip()
            detected_lang = "en"
        
        # Map language codes (Whisper sometimes returns full names)
        lang_mapping = {
            "hindi": "hi", "tamil": "ta", "telugu": "te", "kannada": "kn",
            "malayalam": "ml", "bengali": "bn", "gujarati": "gu", "marathi": "mr",
            "punjabi": "pa", "odia": "or", "assamese": "as", "urdu": "ur",
            "english": "en",
        }
        
        if detected_lang.lower() in lang_mapping:
            detected_lang = lang_mapping[detected_lang.lower()]
        
        if detected_lang not in INDIAN_LANGUAGES:
            detected_lang = "en"
        
        logger.info(f"✅ Final transcription ({detected_lang}): {text[:100] if text else '(empty)'}")
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return text, detected_lang
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "", "en"


# ── Prescription detection keywords ──
PRESCRIPTION_KEYWORDS = [
    "prescription", "rx", "medicine", "tablet", "capsule", "dosage",
    "doctor", "dr.", "clinic", "hospital", "pharmacy",
    "दवाई", "दवा", "नुस्खा",  # Hindi
    "மருந்து", "மருத்துவர்",  # Tamil
    "మందు", "డాక్టర్",  # Telugu
]


async def _detect_prescription_via_groq(image_data: bytes) -> bool:
    """Quick Groq Vision check: is this a prescription?"""
    import base64 as b64m
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        return False
    try:
        b64 = b64m.b64encode(image_data).decode("utf-8")
        # Detect MIME
        mime = "image/jpeg"
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            mime = "image/png"
        elif image_data[:4] == b'RIFF':
            mime = "image/webp"

        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Is this image a medical prescription? Reply ONLY 'YES' or 'NO', nothing else."},
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                        ],
                    }],
                    "temperature": 0.0,
                    "max_tokens": 5,
                },
            )
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"].strip().upper()
            logger.info(f"📋 Prescription detection: {answer}")
            return "YES" in answer
    except Exception as e:
        logger.warning(f"Prescription detection failed: {e}")
        return False


async def _detect_and_handle_prescription(
    image_data: bytes, caption: str, from_number: str, session_id: str, user_lang: str
) -> bool:
    """
    Detect if image is a prescription. If yes, extract medicines via Groq Vision
    and send structured response. Returns True if handled as prescription.
    """
    # Step 1: Quick keyword check on caption
    caption_lower = (caption or "").lower()
    caption_hints = any(kw in caption_lower for kw in PRESCRIPTION_KEYWORDS)
    
    # Step 2: If no caption hint, ask Groq Vision to classify
    if caption_hints:
        is_prescription = True
        logger.info(f"📋 Caption hints at prescription: '{caption[:50]}'")
    else:
        is_prescription = await _detect_prescription_via_groq(image_data)
    
    if not is_prescription:
        return False  # Not a prescription — let normal image pipeline handle it
    
    # ── It's a prescription! Extract structured data ──
    logger.info(f"💊 Processing prescription from {from_number}...")
    
    try:
        from ..services.prescription_vision_service import extract_prescription
        from ..services.prescription_store import prescription_store
        
        # Detect MIME type
        mime_type = "image/jpeg"
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            mime_type = "image/png"
        elif image_data[:4] == b'RIFF':
            mime_type = "image/webp"
        
        # Extract prescription data via Groq Vision
        rx_data = await extract_prescription(image_data, mime_type)
        
        # Store it
        import uuid
        rx_id = uuid.uuid4().hex[:8]
        rx_data.prescription_id = rx_id
        prescription_store.save(rx_id, rx_data, session_id)
        
        # ── Format WhatsApp message ──
        parts = ["📋 *Prescription Analyzed*\n"]
        
        if rx_data.doctor_name:
            parts.append(f"👨‍⚕️ *Doctor:* {rx_data.doctor_name}")
        if rx_data.patient_name:
            parts.append(f"👤 *Patient:* {rx_data.patient_name}")
        if rx_data.date:
            parts.append(f"📅 *Date:* {rx_data.date}")
        if rx_data.diagnosis:
            parts.append(f"🔍 *Diagnosis:* {rx_data.diagnosis}")
        
        if rx_data.medicines:
            parts.append(f"\n💊 *Medicines ({len(rx_data.medicines)}):*")
            for i, med in enumerate(rx_data.medicines, 1):
                line = f"  {i}. *{med.name}*"
                if med.dosage:
                    line += f" — {med.dosage}"
                parts.append(line)
                details = []
                if med.frequency:
                    details.append(f"Frequency: {med.frequency}")
                if med.duration:
                    details.append(f"Duration: {med.duration}")
                if med.timing:
                    details.append(f"Timing: {med.timing}")
                if med.instructions:
                    details.append(f"Note: {med.instructions}")
                if details:
                    parts.append(f"     _{', '.join(details)}_")
        else:
            parts.append("\n⚠️ Could not extract medicines clearly. Please try a clearer photo.")
        
        if rx_data.additional_notes:
            parts.append(f"\n📝 *Notes:* {rx_data.additional_notes}")
        
        parts.append("\n_💡 Reply with questions about this prescription, e.g. \"What is Amoxicillin for?\" or \"Any side effects?\"_")
        parts.append("_⚠️ AI-assisted analysis. Always follow your doctor's advice._")
        
        response_msg = "\n".join(parts)
        await send_whatsapp_message(from_number, response_msg)
        
        logger.info(f"✅ Prescription sent to {from_number}: {len(rx_data.medicines)} medicines, id={rx_id}")
        return True
        
    except Exception as e:
        logger.error(f"Prescription extraction failed: {e}")
        # Fall through — let normal image pipeline handle it as a general medical image
        return False


class WhatsAppMessage(BaseModel):
    """Model for outgoing WhatsApp messages"""
    to: str
    message: str


def get_whatsapp_api_url():
    """Get the WhatsApp API URL"""
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID or "993295210525051"
    return f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"


def get_access_token():
    """Get the access token - read fresh from settings each time"""
    return settings.WHATSAPP_ACCESS_TOKEN or ""


async def send_whatsapp_message(to: str, message: str) -> dict:
    """
    Send a message via WhatsApp Business API
    """
    url = get_whatsapp_api_url()
    access_token = get_access_token()
    
    logger.info(f"Sending message to {to}, token length: {len(access_token)}")
    
    if not access_token:
        logger.error("No WhatsApp access token configured!")
        raise HTTPException(status_code=500, detail="WhatsApp access token not configured")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Split long messages (WhatsApp has 4096 char limit)
    max_length = 4000
    messages_to_send = []
    
    if len(message) > max_length:
        # Split by paragraphs first
        paragraphs = message.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 < max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    messages_to_send.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            messages_to_send.append(current_chunk.strip())
    else:
        messages_to_send = [message]
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for msg in messages_to_send:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": msg
                }
            }
            
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                results.append(response.json())
                logger.info(f"Message sent to {to}: {msg[:50]}...")
            except httpx.HTTPError as e:
                logger.error(f"Failed to send WhatsApp message: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
    
    return {"status": "sent", "messages": len(results)}


async def process_incoming_message(from_number: str, message_text: str, language: str = "en") -> str:
    """
    Process incoming message through CMC AI and return response in user's language
    """
    # Create or get session for this user
    # Auto-reset session if last message was more than 30 minutes ago (prevents stale context)
    session_id = f"whatsapp_{from_number}"
    
    now = datetime.now()
    if session_id in user_sessions:
        last_msg_str = user_sessions[session_id].get("last_message", "")
        try:
            last_msg_time = datetime.fromisoformat(last_msg_str)
            idle_minutes = (now - last_msg_time).total_seconds() / 60
            if idle_minutes > 30:
                logger.info(f"🔄 Resetting stale WhatsApp session for {from_number} (idle {idle_minutes:.0f} min)")
                # Clear AI memory for this session so old symptoms don't carry over
                try:
                    from ..services.ai_service_v2 import powerful_ai
                    if session_id in powerful_ai.memory.conversations:
                        del powerful_ai.memory.conversations[session_id]
                    if session_id in powerful_ai.memory.symptom_history:
                        del powerful_ai.memory.symptom_history[session_id]
                    if session_id in powerful_ai.memory.summaries:
                        del powerful_ai.memory.summaries[session_id]
                except Exception as e:
                    logger.warning(f"Could not clear AI memory: {e}")
                del user_sessions[session_id]
        except (ValueError, TypeError):
            pass
    
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "created": now.isoformat(),
            "message_count": 0
        }
    
    user_sessions[session_id]["message_count"] += 1
    user_sessions[session_id]["last_message"] = now.isoformat()
    
    # Store user's preferred language
    if language != "en":
        user_languages[from_number] = language
    
    # Get user's language preference
    user_lang = user_languages.get(from_number, language)
    lang_info = INDIAN_LANGUAGES.get(user_lang, INDIAN_LANGUAGES["en"])
    
    try:
        # Get AI response using your existing service
        response = await get_ai_response(
            session_id=session_id,
            message=message_text,
            language=user_lang  # Pass detected language
        )
        
        # Use translated response for non-English users, English response otherwise
        if user_lang != "en" and response.get("response_translated"):
            ai_text = response["response_translated"]
        else:
            ai_text = response.get("response", "I'm sorry, I couldn't process your request. Please try again.")
        
        # ====== BUILD CLEAN WHATSAPP MESSAGE ======
        parts = []
        
        # Add greeting for first-time users
        if user_sessions[session_id]["message_count"] == 1:
            greeting = lang_info["greeting"]
            parts.append(f"*CMC Health Assistant*\n\n{greeting}!")
        
        # Main AI response text (this is the core message)
        parts.append(ai_text)
        
        # Add urgency warning ONLY if urgent/emergency
        urgency = response.get("urgency_level", "self_care")
        if urgency in ("emergency", "urgent"):
            urgency_labels = {
                "emergency": "🚨 *EMERGENCY — Call 108 immediately!*",
                "urgent": "⚠️ *Please see a doctor within 24 hours*",
            }
            parts.append(urgency_labels.get(urgency, ''))
        
        # Add possible conditions/diagnoses (top 3)
        diagnoses = response.get("diagnoses", [])
        if diagnoses and len(diagnoses) > 0:
            diag_lines = []
            for d in diagnoses[:3]:
                name = d.get("condition", d.get("name", ""))
                conf = d.get("confidence", 0)
                if isinstance(conf, float) and conf <= 1:
                    conf = int(conf * 100)
                if name:
                    filled = int(conf / 10)
                    bar = "█" * filled + "░" * (10 - filled)
                    diag_lines.append(f"• {name} — {conf}% {bar}")
            if diag_lines:
                parts.append("🔍 *Possible Conditions:*\n" + "\n".join(diag_lines))
        
        # Add medications (top 3)
        medications = response.get("medications", [])
        if medications and len(medications) > 0:
            med_lines = [f"• {m.get('name', '')} — {m.get('dosage', '')}" for m in medications[:3] if m.get('name')]
            if med_lines:
                parts.append("💊 *Suggested Medications:*\n" + "\n".join(med_lines))
        
        # Add home remedies from medications that are remedies
        remedies = [m for m in medications if m.get('type') == 'remedy' or m.get('category') == 'remedy']
        non_remedy_meds = [m for m in medications if m.get('type') != 'remedy' and m.get('category') != 'remedy']
        if remedies:
            remedy_lines = [f"• {r.get('name', '')}" for r in remedies[:3] if r.get('name')]
            if remedy_lines:
                parts.append("🌿 *Home Remedies:*\n" + "\n".join(remedy_lines))
        
        # Add specialist recommendation
        specialist = response.get("specialist_recommended")
        if specialist:
            parts.append(f"👨‍⚕️ *Recommended Specialist:* {specialist}")
        
        # Add 1 follow-up question if AI needs more info
        follow_ups = response.get("follow_up_questions", [])
        if follow_ups and len(follow_ups) > 0:
            parts.append(f"🤔 {follow_ups[0]}")
        
        # Combine all parts
        ai_response = "\n\n".join(parts)
        
        logger.info(f"📱 WhatsApp response built: {len(ai_response)} chars, {len(diagnoses)} diagnoses, {len(medications)} meds, urgency={urgency}")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Webhook verification endpoint for WhatsApp
    Meta sends a GET request to verify the webhook
    """
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_CONFIG["verify_token"]:
        logger.info("Webhook verified successfully!")
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        logger.warning(f"Webhook verification failed. Expected: {WHATSAPP_CONFIG['verify_token']}, Got: {hub_verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_message(request: Request):
    """
    Receive incoming WhatsApp messages and respond with AI
    """
    import asyncio
    
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Extract message data
        if "entry" not in body:
            return {"status": "ok"}
        
        # Process messages in background to respond quickly to Meta
        async def process_messages():
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Check if this is a message
                    if "messages" not in value:
                        continue
                    
                    for message in value.get("messages", []):
                        # Get message ID and check for duplicates
                        message_id = message.get("id")
                        if message_id in processed_messages:
                            logger.info(f"Skipping duplicate message: {message_id}")
                            continue
                        processed_messages.add(message_id)
                        
                        # Skip old messages (older than 2 minutes)
                        msg_timestamp = int(message.get("timestamp", 0))
                        current_time = int(datetime.now().timestamp())
                        if current_time - msg_timestamp > 120:  # 2 minutes
                            logger.info(f"Skipping old message (age: {current_time - msg_timestamp}s): {message_id}")
                            continue
                        
                        from_number = message.get("from")
                        msg_type = message.get("type")
                        message_text = ""
                        detected_language = "en"
                        
                        # Handle text messages
                        if msg_type == "text":
                            message_text = message.get("text", {}).get("body", "")
                        
                        # Handle voice/audio messages
                        elif msg_type == "audio":
                            audio_info = message.get("audio", {})
                            media_id = audio_info.get("id")
                            
                            if media_id:
                                logger.info(f"🎤 Voice message received from {from_number}")
                                try:
                                    # Download and transcribe
                                    audio_data = await download_whatsapp_media(media_id)
                                    message_text, detected_language = await transcribe_voice_message(audio_data)
                                    
                                    if message_text:
                                        logger.info(f"🎤 Transcribed ({detected_language}): {message_text[:50]}...")
                                    else:
                                        # Send error message if transcription failed
                                        await send_whatsapp_message(
                                            from_number, 
                                            "Sorry, I couldn't understand the voice message. Please try again or send a text message."
                                        )
                                        continue
                                except Exception as e:
                                    logger.error(f"Voice processing error: {e}")
                                    await send_whatsapp_message(
                                        from_number,
                                        "Sorry, I had trouble processing your voice message. Please try sending a text message."
                                    )
                                    continue
                        # Handle image messages
                        elif msg_type == "image":
                            image_info = message.get("image", {})
                            media_id = image_info.get("id")
                            caption = image_info.get("caption", "")
                            
                            if media_id:
                                logger.info(f"🖼️ Image received from {from_number} (caption: {caption[:50] if caption else 'none'})")
                                try:
                                    import base64 as b64module
                                    from ..services.ai_service_v2 import get_ai_response
                                    
                                    # Download image from WhatsApp
                                    image_data = await download_whatsapp_media(media_id)
                                    logger.info(f"🖼️ Downloaded image: {len(image_data)} bytes")
                                    
                                    session_id = f"whatsapp_{from_number}"
                                    user_lang = user_languages.get(from_number, "en")
                                    
                                    # ── Smart Detection: Is this a prescription? ──
                                    is_prescription = await _detect_and_handle_prescription(
                                        image_data, caption, from_number, session_id, user_lang
                                    )
                                    if is_prescription:
                                        continue
                                    
                                    # ── Not a prescription → Full medical image analysis pipeline ──
                                    image_b64 = b64module.b64encode(image_data).decode("utf-8")
                                    user_message = caption if caption else "Please analyze this medical image"
                                    
                                    # Pipe through Groq Vision → Cerebras diagnosis pipeline
                                    ai_response = await get_ai_response(
                                        message=user_message,
                                        session_id=session_id,
                                        language=user_lang,
                                        vitals=None,
                                        image_base64=image_b64
                                    )
                                    
                                    # Use translated response if available
                                    response_text = ai_response.get("response_translated") or ai_response.get("response", "Unable to analyze.")
                                    urgency = ai_response.get("urgency_level", "self_care")
                                    diagnoses = ai_response.get("diagnoses", [])
                                    medications = ai_response.get("medications", [])
                                    follow_ups = ai_response.get("follow_up_questions", [])
                                    specialist = ai_response.get("specialist_recommended")
                                    
                                    # ── Format rich response (same style as text messages) ──
                                    parts = ["*Image Analysis*"]
                                    
                                    # Main AI response
                                    parts.append(response_text)
                                    
                                    # Diagnoses with confidence bars (matching text handler)
                                    if diagnoses and len(diagnoses) > 0:
                                        diag_lines = ["*Possible Conditions:*"]
                                        for i, d in enumerate(diagnoses[:5], 1):
                                            condition = d.get("condition", "Unknown")
                                            confidence = d.get("confidence", 0)
                                            pct = int(confidence * 100) if confidence <= 1 else int(confidence)
                                            filled = pct // 10
                                            bar = "█" * filled + "░" * (10 - filled)
                                            diag_lines.append(f"• *{condition}* — {pct}%  {bar}")
                                            desc = d.get("description", "")
                                            if desc:
                                                diag_lines.append(f"   _{desc[:100]}_")
                                        parts.append("\n".join(diag_lines))
                                    
                                    # Urgency level
                                    urgency_labels = {
                                        "emergency": "*EMERGENCY — Call 108/ambulance immediately!*",
                                        "urgent": "*Urgent — See a doctor within 24 hours*",
                                        "doctor_soon": "*See a doctor within a few days*",
                                        "routine": "*Routine — Schedule a checkup*",
                                        "self_care": "*Self-care at home*"
                                    }
                                    if urgency != "self_care":
                                        parts.append(urgency_labels.get(urgency, f"*Urgency: {urgency}*"))
                                    
                                    # Medications
                                    if medications and len(medications) > 0:
                                        med_lines = ["*Suggested Medications:*"]
                                        for med in medications[:4]:
                                            name = med.get("name", "")
                                            dosage = med.get("dosage", "")
                                            if name:
                                                med_lines.append(f"  • *{name}* — {dosage}" if dosage else f"  • *{name}*")
                                        parts.append("\n".join(med_lines))
                                    
                                    # Follow-up questions
                                    if follow_ups and len(follow_ups) > 0:
                                        fq_lines = ["*I'd also like to know:*"]
                                        for q in follow_ups[:3]:
                                            fq_lines.append(f"  • {q}")
                                        parts.append("\n".join(fq_lines))
                                    
                                    # Specialist recommendation
                                    if specialist:
                                        parts.append(f"*Recommended specialist:* {specialist}")
                                    
                                    parts.append("_This is AI-assisted analysis only. Please consult a healthcare professional for proper diagnosis._")
                                    
                                    response_msg = "\n\n".join(parts)
                                    
                                    await send_whatsapp_message(from_number, response_msg)
                                    logger.info(f"✅ Full image diagnosis sent to {from_number}: {len(diagnoses)} diagnoses, {len(medications)} meds, follow_ups={len(follow_ups)}")
                                    continue
                                except Exception as e:
                                    logger.error(f"Image processing error: {e}")
                                    await send_whatsapp_message(
                                        from_number,
                                        "Sorry, I had trouble analyzing your image. Please try describing your symptoms in text."
                                    )
                                    continue
                        
                        else:
                            # Skip unsupported message types
                            logger.info(f"Skipping unsupported message type: {msg_type}")
                            continue
                        
                        if not from_number or not message_text:
                            continue
                        
                        logger.info(f"Message from {from_number} ({detected_language}): {message_text}")
                        
                        try:
                            # Process through AI and get response
                            ai_response = await process_incoming_message(from_number, message_text, detected_language)
                            
                            # Send response back to user
                            await send_whatsapp_message(from_number, ai_response)
                        except Exception as e:
                            logger.error(f"Error processing message from {from_number}: {e}")
        
        # Start background task and return immediately
        asyncio.create_task(process_messages())
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Always return 200 to prevent Meta from retrying
        return {"status": "error", "message": str(e)}


@router.post("/send")
async def send_message_endpoint(message: WhatsAppMessage):
    """
    Manually send a WhatsApp message (for testing)
    """
    result = await send_whatsapp_message(message.to, message.message)
    return result


@router.get("/health")
async def whatsapp_health():
    """
    Health check for WhatsApp integration
    """
    return {
        "status": "healthy",
        "phone_number_id": WHATSAPP_CONFIG["phone_number_id"],
        "api_version": WHATSAPP_CONFIG["api_version"],
        "active_sessions": len(user_sessions)
    }
