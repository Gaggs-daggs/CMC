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
    """Load Whisper model lazily (small model - good balance of speed and accuracy)"""
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            logger.info("🎤 Loading Whisper model (small) for Indian language support...")
            whisper_model = whisper.load_model("small")
            logger.info("✅ Whisper small model loaded successfully")
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
    Transcribe voice message using Whisper
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
        
        logger.info("🎤 Transcribing voice message...")
        
        # Transcribe with auto language detection
        # Use initial_prompt to help with Indian languages
        result = model.transcribe(
            temp_path, 
            task="transcribe", 
            fp16=False,
            initial_prompt="This is a health-related query in an Indian language like Hindi, Tamil, Telugu, or English."
        )
        
        text = result.get("text", "").strip()
        detected_lang = result.get("language", "en")
        
        # If empty or just noise, try with Tamil hint (common in your region)
        if len(text) < 5 or detected_lang in ["ja", "zh", "ko", "zh-CN", "zh-TW"]:
            logger.info(f"🔄 Retrying with Tamil hint (detected: {detected_lang}, text: '{text[:20]}')")
            result = model.transcribe(temp_path, language="ta", task="transcribe", fp16=False)
            text = result.get("text", "").strip()
            detected_lang = "ta"
            
            # If still empty, try Hindi
            if len(text) < 5:
                logger.info("🔄 Retrying with Hindi hint...")
                result = model.transcribe(temp_path, language="hi", task="transcribe", fp16=False)
                text = result.get("text", "").strip()
                detected_lang = "hi"
        
        # Map language codes
        lang_mapping = {
            "hindi": "hi", "tamil": "ta", "telugu": "te", "kannada": "kn",
            "malayalam": "ml", "bengali": "bn", "gujarati": "gu", "marathi": "mr",
            "punjabi": "pa", "odia": "or", "assamese": "as", "urdu": "ur",
        }
        
        if detected_lang.lower() in lang_mapping:
            detected_lang = lang_mapping[detected_lang.lower()]
        
        if detected_lang not in INDIAN_LANGUAGES:
            detected_lang = "en"
        
        logger.info(f"✅ Transcribed ({detected_lang}): {text[:80] if text else '(empty)'}...")
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return text, detected_lang
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "", "en"


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
    session_id = f"whatsapp_{from_number}"
    
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "created": datetime.now().isoformat(),
            "message_count": 0
        }
    
    user_sessions[session_id]["message_count"] += 1
    user_sessions[session_id]["last_message"] = datetime.now().isoformat()
    
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
        
        # Format response for WhatsApp
        ai_response = response.get("response", "I'm sorry, I couldn't process your request. Please try again.")
        
        # Add a friendly prefix for first-time users in their language
        if user_sessions[session_id]["message_count"] == 1:
            greeting = lang_info["greeting"]
            ai_response = f"🏥 *CMC Health Assistant*\n\n{greeting}! " + ai_response
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment. 🙏"


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
                                            "🎤 Sorry, I couldn't understand the voice message. Please try again or send a text message."
                                        )
                                        continue
                                except Exception as e:
                                    logger.error(f"Voice processing error: {e}")
                                    await send_whatsapp_message(
                                        from_number,
                                        "🎤 Sorry, I had trouble processing your voice message. Please try sending a text message."
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
