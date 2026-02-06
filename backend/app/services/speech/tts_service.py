"""
Text-to-Speech Service using Microsoft Edge TTS
High-quality neural voices for Indian languages

Features:
- Expressive voices for natural conversation
- Male/Female voice options for all languages
- Speed control: normal, slow, very_slow (for elderly users)
- 14+ Indian languages supported
"""

import edge_tts
import asyncio
import logging
import os
import tempfile
from typing import Optional, Dict, List, Literal
from enum import Enum

logger = logging.getLogger(__name__)


class VoiceGender(str, Enum):
    FEMALE = "female"
    MALE = "male"


class SpeechSpeed(str, Enum):
    FAST = "fast"          # +15% speed
    NORMAL = "normal"      # Default speed
    SLOW = "slow"          # -20% speed
    VERY_SLOW = "very_slow"  # -35% speed (for elderly)


# Speed adjustments for different modes
SPEED_ADJUSTMENTS = {
    SpeechSpeed.FAST: 15,
    SpeechSpeed.NORMAL: 0,
    SpeechSpeed.SLOW: -20,
    SpeechSpeed.VERY_SLOW: -35,
}


# High-Quality Neural Voice Mapping for Indian Languages
# Using latest expressive voices where available
NEURAL_VOICES = {
    "en": {
        "voice_female": "en-IN-NeerjaExpressiveNeural",  # NEW: Expressive voice!
        "voice_male": "en-IN-PrabhatNeural",
        "name": "English (India)",
        "rate": "+0%",
        "pitch": "+0Hz"
    },
    "hi": {
        "voice_female": "hi-IN-SwaraNeural",
        "voice_male": "hi-IN-MadhurNeural",
        "name": "Hindi",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "ta": {
        "voice_female": "ta-IN-PallaviNeural",
        "voice_male": "ta-IN-ValluvarNeural",
        "name": "Tamil",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "te": {
        "voice_female": "te-IN-ShrutiNeural",
        "voice_male": "te-IN-MohanNeural",
        "name": "Telugu",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "bn": {
        "voice_female": "bn-IN-TanishaaNeural",
        "voice_male": "bn-IN-BashkarNeural",
        "name": "Bengali",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "mr": {
        "voice_female": "mr-IN-AarohiNeural",
        "voice_male": "mr-IN-ManoharNeural",
        "name": "Marathi",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "gu": {
        "voice_female": "gu-IN-DhwaniNeural",
        "voice_male": "gu-IN-NiranjanNeural",
        "name": "Gujarati",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "kn": {
        "voice_female": "kn-IN-SapnaNeural",
        "voice_male": "kn-IN-GaganNeural",
        "name": "Kannada",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "ml": {
        "voice_female": "ml-IN-SobhanaNeural",
        "voice_male": "ml-IN-MidhunNeural",
        "name": "Malayalam",
        "rate": "-10%",
        "pitch": "+0Hz"
    },
    "pa": {
        "voice_female": "pa-IN-GurpreetNeural",
        "voice_male": "pa-IN-GurpreetNeural",  # Only one voice available
        "name": "Punjabi",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "ur": {
        "voice_female": "ur-IN-GulNeural",
        "voice_male": "ur-IN-SalmanNeural",
        "name": "Urdu",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "or": {
        "voice_female": "hi-IN-SwaraNeural",  # Fallback to Hindi
        "voice_male": "hi-IN-MadhurNeural",
        "name": "Odia",
        "rate": "-10%",
        "pitch": "+0Hz",
        "fallback": True
    },
    "as": {
        "voice_female": "bn-IN-TanishaaNeural",  # Fallback to Bengali
        "voice_male": "bn-IN-BashkarNeural",
        "name": "Assamese",
        "rate": "-10%",
        "pitch": "+0Hz",
        "fallback": True
    },
    "ne": {
        "voice_female": "ne-NP-HemkalaNeural",
        "voice_male": "ne-NP-SagarNeural",
        "name": "Nepali",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "si": {
        "voice_female": "si-LK-ThiliniNeural",
        "voice_male": "si-LK-SameeraNeural",
        "name": "Sinhala",
        "rate": "-5%",
        "pitch": "+0Hz"
    }
}


class TTSService:
    """
    Microsoft Edge Neural TTS - High quality voices
    
    Features:
    - Male/Female voice selection
    - Speed control: fast, normal, slow, very_slow
    - Expressive voices for natural conversation
    - 14+ Indian languages
    """
    
    def __init__(self):
        self._voices = NEURAL_VOICES
        self._default_gender = VoiceGender.FEMALE
        self._default_speed = SpeechSpeed.NORMAL
    
    def get_voice_for_language(
        self, 
        lang_code: str, 
        gender: VoiceGender = None
    ) -> str:
        """Get the voice name for a language and gender."""
        config = self._voices.get(lang_code, self._voices["en"])
        gender = gender or self._default_gender
        
        if gender == VoiceGender.MALE:
            return config.get("voice_male", config["voice_female"])
        return config["voice_female"]
    
    def _calculate_rate(
        self, 
        language: str, 
        speed: SpeechSpeed = None,
        slow: bool = False  # Legacy support
    ) -> str:
        """Calculate speech rate based on language and speed setting."""
        config = self._voices.get(language, self._voices["en"])
        base_rate = int(config.get("rate", "+0%").replace("%", "").replace("+", ""))
        
        # Legacy support for old 'slow' parameter
        if slow and speed is None:
            speed = SpeechSpeed.SLOW
        
        speed = speed or self._default_speed
        adjustment = SPEED_ADJUSTMENTS.get(speed, 0)
        
        final_rate = base_rate + adjustment
        return f"{final_rate:+d}%"
    
    async def generate_speech_async(
        self, 
        text: str, 
        language: str = "en", 
        slow: bool = False,  # Legacy support
        gender: str = None,  # "male" or "female"
        speed: str = None    # "fast", "normal", "slow", "very_slow"
    ) -> str:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            language: Language code (en, hi, ta, te, etc.)
            slow: Legacy parameter for slow speech
            gender: Voice gender - "male" or "female"
            speed: Speech speed - "fast", "normal", "slow", "very_slow"
        
        Returns:
            Path to generated audio file (MP3)
        """
        try:
            config = self._voices.get(language, self._voices["en"])
            
            # Parse gender
            voice_gender = VoiceGender.FEMALE
            if gender:
                voice_gender = VoiceGender(gender.lower()) if gender.lower() in ["male", "female"] else VoiceGender.FEMALE
            
            # Parse speed
            speech_speed = None
            if speed:
                try:
                    speech_speed = SpeechSpeed(speed.lower())
                except ValueError:
                    speech_speed = SpeechSpeed.NORMAL
            
            voice = self.get_voice_for_language(language, voice_gender)
            rate = self._calculate_rate(language, speech_speed, slow)
            pitch = config.get("pitch", "+0Hz")
            
            clean_text = self._clean_text(text)
            if not clean_text.strip():
                return None
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            audio_path = temp_file.name
            temp_file.close()
            
            communicate = edge_tts.Communicate(text=clean_text, voice=voice, rate=rate, pitch=pitch)
            await communicate.save(audio_path)
            
            logger.info(f"Generated TTS: voice={voice}, lang={language}, gender={voice_gender.value}, speed={rate}")
            return audio_path
            
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TTS - remove markdown and emojis."""
        import re
        clean = text.replace("**", "")
        clean = re.sub(r'[\U0001F300-\U0001F9FF]', '', clean)
        clean = re.sub(r'[\u2600-\u26FF]', '', clean)
        clean = re.sub(r'\n{2,}', '. ', clean)
        clean = re.sub(r'\n', ', ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def generate_speech(
        self, 
        text: str, 
        language: str = "en", 
        slow: bool = False,
        gender: str = None,
        speed: str = None
    ) -> str:
        """Sync wrapper for generate_speech_async."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.generate_speech_async(text, language, slow, gender, speed)
            )
        finally:
            loop.close()
    
    def generate_speech_bytes(
        self, 
        text: str, 
        language: str = "en", 
        slow: bool = False,
        gender: str = None,
        speed: str = None
    ) -> bytes:
        """Generate speech and return bytes."""
        audio_path = self.generate_speech(text, language, slow, gender, speed)
        if not audio_path or not os.path.exists(audio_path):
            return b''
        try:
            with open(audio_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
    
    async def generate_speech_bytes_async(
        self, 
        text: str, 
        language: str = "en", 
        slow: bool = False,
        gender: str = None,
        speed: str = None
    ) -> bytes:
        """Async version for FastAPI routes."""
        audio_path = await self.generate_speech_async(text, language, slow, gender, speed)
        if not audio_path or not os.path.exists(audio_path):
            return b''
        try:
            with open(audio_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
    
    @property
    def NEURAL_VOICES(self):
        return self._voices
    
    def supported_languages(self) -> List[Dict]:
        """Get list of supported languages with voice info."""
        return [
            {
                "code": k, 
                "name": v["name"], 
                "voice_female": v["voice_female"],
                "voice_male": v["voice_male"],
                "fallback": v.get("fallback", False)
            } 
            for k, v in self._voices.items()
        ]
    
    def get_voice_options(self) -> Dict:
        """Get available voice options for UI."""
        return {
            "genders": [g.value for g in VoiceGender],
            "speeds": [s.value for s in SpeechSpeed],
            "speed_descriptions": {
                "fast": "Faster than normal (+15%)",
                "normal": "Normal speed",
                "slow": "Slower for clarity (-20%)",
                "very_slow": "Very slow for elderly (-35%)"
            }
        }


tts_service = TTSService()
