"""
Text-to-Speech Service using Microsoft Edge TTS
High-quality neural voices for Indian languages
"""

import edge_tts
import asyncio
import logging
import os
import tempfile
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# High-Quality Neural Voice Mapping for Indian Languages
NEURAL_VOICES = {
    "en": {
        "voice": "en-IN-NeerjaNeural",
        "voice_alt": "en-IN-PrabhatNeural",
        "name": "English (India)",
        "rate": "+0%",
        "pitch": "+0Hz"
    },
    "hi": {
        "voice": "hi-IN-SwaraNeural",
        "voice_alt": "hi-IN-MadhurNeural",
        "name": "Hindi",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "ta": {
        "voice": "ta-IN-PallaviNeural",
        "voice_alt": "ta-IN-ValluvarNeural",
        "name": "Tamil",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "te": {
        "voice": "te-IN-ShrutiNeural",
        "voice_alt": "te-IN-MohanNeural",
        "name": "Telugu",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "bn": {
        "voice": "bn-IN-TanishaaNeural",
        "voice_alt": "bn-IN-BashkarNeural",
        "name": "Bengali",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "mr": {
        "voice": "mr-IN-AarohiNeural",
        "voice_alt": "mr-IN-ManoharNeural",
        "name": "Marathi",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "gu": {
        "voice": "gu-IN-DhwaniNeural",
        "voice_alt": "gu-IN-NiranjanNeural",
        "name": "Gujarati",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "kn": {
        "voice": "kn-IN-SapnaNeural",
        "voice_alt": "kn-IN-GaganNeural",
        "name": "Kannada",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "ml": {
        "voice": "ml-IN-SobhanaNeural",
        "voice_alt": "ml-IN-MidhunNeural",
        "name": "Malayalam",
        "rate": "-10%",
        "pitch": "+0Hz"
    },
    "pa": {
        "voice": "pa-IN-GurpreetNeural",
        "voice_alt": "pa-IN-GurpreetNeural",
        "name": "Punjabi",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "ur": {
        "voice": "ur-IN-GulNeural",
        "voice_alt": "ur-IN-SalmanNeural",
        "name": "Urdu",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "or": {
        "voice": "hi-IN-SwaraNeural",
        "voice_alt": "hi-IN-MadhurNeural",
        "name": "Odia",
        "rate": "-10%",
        "pitch": "+0Hz",
        "fallback": True
    },
    "as": {
        "voice": "bn-IN-TanishaaNeural",
        "voice_alt": "bn-IN-BashkarNeural",
        "name": "Assamese",
        "rate": "-10%",
        "pitch": "+0Hz",
        "fallback": True
    },
    "ne": {
        "voice": "ne-NP-HemkalaNeural",
        "voice_alt": "ne-NP-SagarNeural",
        "name": "Nepali",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    "si": {
        "voice": "si-LK-ThiliniNeural",
        "voice_alt": "si-LK-SameeraNeural",
        "name": "Sinhala",
        "rate": "-5%",
        "pitch": "+0Hz"
    }
}


class TTSService:
    """Microsoft Edge Neural TTS - High quality voices"""
    
    def __init__(self):
        self._voices = NEURAL_VOICES
        self._use_male_voice = False
    
    def get_voice_for_language(self, lang_code: str) -> str:
        config = self._voices.get(lang_code, self._voices["en"])
        if self._use_male_voice:
            return config.get("voice_alt", config["voice"])
        return config["voice"]
    
    async def generate_speech_async(self, text: str, language: str = "en", slow: bool = False) -> str:
        try:
            config = self._voices.get(language, self._voices["en"])
            voice = self.get_voice_for_language(language)
            rate = config.get("rate", "+0%")
            if slow:
                current_rate = int(rate.replace("%", "").replace("+", ""))
                rate = f"{current_rate - 20}%"
            pitch = config.get("pitch", "+0Hz")
            clean_text = self._clean_text(text)
            if not clean_text.strip():
                return None
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            audio_path = temp_file.name
            temp_file.close()
            
            communicate = edge_tts.Communicate(text=clean_text, voice=voice, rate=rate, pitch=pitch)
            await communicate.save(audio_path)
            logger.info(f"Generated TTS: {voice}, {language}")
            return audio_path
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        import re
        clean = text.replace("**", "")
        clean = re.sub(r'[\U0001F300-\U0001F9FF]', '', clean)
        clean = re.sub(r'[\u2600-\u26FF]', '', clean)
        clean = re.sub(r'\n{2,}', '. ', clean)
        clean = re.sub(r'\n', ', ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def generate_speech(self, text: str, language: str = "en", slow: bool = False) -> str:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.generate_speech_async(text, language, slow))
        finally:
            loop.close()
    
    def generate_speech_bytes(self, text: str, language: str = "en", slow: bool = False) -> bytes:
        audio_path = self.generate_speech(text, language, slow)
        if not audio_path or not os.path.exists(audio_path):
            return b''
        try:
            with open(audio_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
    
    async def generate_speech_bytes_async(self, text: str, language: str = "en", slow: bool = False) -> bytes:
        """Async version for FastAPI routes"""
        audio_path = await self.generate_speech_async(text, language, slow)
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
        return [{"code": k, "name": v["name"], "voice": v["voice"]} for k, v in self._voices.items()]


tts_service = TTSService()
