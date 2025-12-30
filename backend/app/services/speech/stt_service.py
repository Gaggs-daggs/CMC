"""
Whisper Speech-to-Text Service
Transcribes audio to text with automatic language detection
"""

import whisper
import logging
import os
import tempfile
from typing import Optional, Tuple
import torch

from app.config import settings

logger = logging.getLogger(__name__)


class WhisperSTTService:
    """OpenAI Whisper Speech-to-Text service"""
    
    def __init__(self):
        self.model = None
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Whisper will use device: {self.device}")
    
    def load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model: {self.model_size}")
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
    
    def transcribe_audio(
        self, 
        audio_path: str, 
        language: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Optional language code hint (e.g., 'hi', 'en')
        
        Returns:
            Tuple of (transcribed_text, detected_language, confidence)
        """
        self.load_model()
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                language=language,  # Can be None for auto-detection
                task="transcribe",
                fp16=(self.device == "cuda"),  # Use FP16 on GPU
                verbose=False
            )
            
            text = result["text"].strip()
            detected_language = result.get("language", "unknown")
            
            # Calculate confidence from segments
            segments = result.get("segments", [])
            if segments:
                avg_confidence = sum(s.get("no_speech_prob", 0) for s in segments) / len(segments)
                confidence = 1.0 - avg_confidence
            else:
                confidence = 0.5
            
            logger.info(
                f"Transcribed audio: '{text[:50]}...' "
                f"(lang: {detected_language}, confidence: {confidence:.2f})"
            )
            
            return text, detected_language, confidence
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_audio_bytes(
        self, 
        audio_bytes: bytes,
        language: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        Transcribe audio from bytes
        
        Args:
            audio_bytes: Audio file bytes
            language: Optional language code hint
        
        Returns:
            Tuple of (transcribed_text, detected_language, confidence)
        """
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            result = self.transcribe_audio(temp_path, language)
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def supported_languages(self) -> list:
        """Get list of supported languages"""
        return [
            "en", "hi", "bn", "ta", "te", "mr", 
            "gu", "kn", "ml", "pa", "or", "as"
        ]


# Global instance
stt_service = WhisperSTTService()
