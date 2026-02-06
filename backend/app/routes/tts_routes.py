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
        
        logger.info(
            f"TTS request: lang={request.language}, "
            f"gender={request.gender or 'female'}, "
            f"speed={request.speed or 'normal'}, "
            f"text_length={len(request.text)}"
        )
        
        # Generate speech using Edge TTS
        audio_bytes = await tts_service.generate_speech_bytes_async(
            text=request.text,
            language=request.language,
            slow=request.slow,
            gender=request.gender,
            speed=request.speed
        )
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
        
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
