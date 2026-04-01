"""
Text-to-Speech routes using Microsoft Edge Neural TTS

Features:
- 14+ Indian languages with high-quality neural voices
- Male/Female voice selection
- Speed control: fast, normal, slow, very_slow (for elderly)
- Expressive voices for natural conversation
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Literal
import logging

from ..services.speech.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["text-to-speech"])
logger = logging.getLogger(__name__)

tts_service = TTSService()

# Simple in-memory cache to prevent duplicate TTS generation
# Key: hash of (text, language, gender, speed) → audio bytes
from hashlib import md5
_tts_cache: dict[str, bytes] = {}
_TTS_CACHE_MAX = 50  # Keep last 50 entries
_TTS_MAX_TEXT_LENGTH = 1000  # Max chars for TTS (generous for non-Latin scripts like Tamil)


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    slow: bool = False  # Legacy support
    gender: Optional[Literal["male", "female"]] = None  # Voice gender
    speed: Optional[Literal["fast", "normal", "slow", "very_slow"]] = None  # Speed control


@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Microsoft Edge Neural TTS.
    
    Args:
        text: Text to convert to speech
        language: Language code (en, hi, ta, te, bn, mr, gu, kn, ml, pa, ur, or, as, ne)
        gender: Voice gender - "male" or "female" (default: female)
        speed: Speech speed - "fast", "normal", "slow", "very_slow" (default: normal)
        slow: Legacy parameter (use 'speed' instead)
    
    Returns:
        MP3 audio data
    
    Examples:
        - Normal female voice: {"text": "Hello", "language": "en"}
        - Male Hindi voice: {"text": "नमस्ते", "language": "hi", "gender": "male"}
        - Slow for elderly: {"text": "Take medicine", "language": "en", "speed": "very_slow"}
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Truncate very long text to prevent slow TTS generation
        text = request.text.strip()
        if len(text) > _TTS_MAX_TEXT_LENGTH:
            text = text[:_TTS_MAX_TEXT_LENGTH] + "..."
        
        logger.info(
            f"TTS request: lang={request.language}, "
            f"gender={request.gender or 'female'}, "
            f"speed={request.speed or 'normal'}, "
            f"text_length={len(text)}"
        )
        
        # Check cache first
        cache_key = md5(f"{text}|{request.language}|{request.gender}|{request.speed}".encode()).hexdigest()
        if cache_key in _tts_cache:
            logger.info(f"TTS cache hit for {cache_key[:8]}")
            return Response(
                content=_tts_cache[cache_key],
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=speech.mp3"}
            )
        
        # Generate speech using Edge TTS
        audio_bytes = await tts_service.generate_speech_bytes_async(
            text=text,
            language=request.language,
            slow=request.slow,
            gender=request.gender,
            speed=request.speed
        )
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
        
        # Store in cache (evict oldest if full)
        if len(_tts_cache) >= _TTS_CACHE_MAX:
            oldest_key = next(iter(_tts_cache))
            del _tts_cache[oldest_key]
        _tts_cache[cache_key] = audio_bytes
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available voices for each language.
    
    Returns:
        - voices: Voice configuration for each language
        - supported_languages: List of language codes
        - options: Available gender and speed options
    """
    return {
        "voices": tts_service.NEURAL_VOICES,
        "supported_languages": list(tts_service.NEURAL_VOICES.keys()),
        "options": tts_service.get_voice_options()
    }


@router.get("/languages")
async def get_supported_languages():
    """
    Get detailed list of supported languages with voice info.
    """
    return {
        "languages": tts_service.supported_languages()
    }
