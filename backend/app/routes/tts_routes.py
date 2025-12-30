"""
Text-to-Speech routes using Microsoft Edge Neural TTS
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import logging

from ..services.speech.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["text-to-speech"])
logger = logging.getLogger(__name__)

tts_service = TTSService()


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    slow: bool = False


@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Microsoft Edge Neural TTS.
    Returns MP3 audio data.
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        logger.info(f"TTS request: language={request.language}, text_length={len(request.text)}")
        
        # Generate speech using Edge TTS
        audio_bytes = await tts_service.generate_speech_bytes_async(
            text=request.text,
            language=request.language,
            slow=request.slow
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
    """
    return {
        "voices": tts_service.NEURAL_VOICES,
        "supported_languages": list(tts_service.NEURAL_VOICES.keys())
    }
