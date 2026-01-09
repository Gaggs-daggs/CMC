"""
Translation Service - Google Translate Based
Uses Google Translate (free, no API key) for high-quality translations.
"""

import logging
from typing import Optional, Dict
import hashlib

logger = logging.getLogger(__name__)

GOOGLE_TRANSLATE_AVAILABLE = False
GoogleTranslator = None

try:
    from deep_translator import GoogleTranslator as GT
    GoogleTranslator = GT
    GOOGLE_TRANSLATE_AVAILABLE = True
    logger.info("Google Translate initialized")
except ImportError:
    logger.error("deep-translator not installed")

INDIAN_LANGUAGES = {
    "en": {"name": "English", "native": "English", "tts_code": "en-IN", "google_code": "en"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "tts_code": "hi-IN", "google_code": "hi"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "tts_code": "ta-IN", "google_code": "ta"},
    "te": {"name": "Telugu", "native": "తెలుగు", "tts_code": "te-IN", "google_code": "te"},
    "bn": {"name": "Bengali", "native": "বাংলা", "tts_code": "bn-IN", "google_code": "bn"},
    "mr": {"name": "Marathi", "native": "मराठी", "tts_code": "mr-IN", "google_code": "mr"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "tts_code": "gu-IN", "google_code": "gu"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "tts_code": "kn-IN", "google_code": "kn"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "tts_code": "ml-IN", "google_code": "ml"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "tts_code": "pa-IN", "google_code": "pa"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "tts_code": "or-IN", "google_code": "or"},
    "ur": {"name": "Urdu", "native": "اردو", "tts_code": "ur-IN", "google_code": "ur"},
    "ne": {"name": "Nepali", "native": "नेपाली", "tts_code": "ne-NP", "google_code": "ne"},
}

MEDICAL_TERMS_TO_PRESERVE = ["paracetamol", "ibuprofen", "dolo", "crocin", "mg", "ml"]


class TranslationService:
    def __init__(self):
        self._cache = {}
        self._supported_languages = INDIAN_LANGUAGES
        if GOOGLE_TRANSLATE_AVAILABLE:
            logger.info("TranslationService ready")
    
    def is_available(self):
        return GOOGLE_TRANSLATE_AVAILABLE
    
    def is_using_transformer(self):
        return False
    
    def get_supported_languages(self):
        return self._supported_languages
    
    def get_language_info(self, lang_code):
        return self._supported_languages.get(lang_code)
    
    def get_tts_code(self, lang_code):
        info = self._supported_languages.get(lang_code, {})
        return info.get("tts_code", "en-IN")
    
    def get_google_code(self, lang_code):
        info = self._supported_languages.get(lang_code, {})
        return info.get("google_code", lang_code)
    
    def get_cache_stats(self):
        return {"cache_hits": 0, "cache_misses": 0}
    
    def translate(self, text, target_language, source_language=None, preserve_medical=True):
        if not text or target_language == "en":
            return text
        
        src = source_language or "en"
        if src == target_language:
            return text
        
        cache_key = f"{src}:{target_language}:{hashlib.md5(text.encode()).hexdigest()}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not GOOGLE_TRANSLATE_AVAILABLE:
            return text
        
        try:
            translator = GoogleTranslator(source=self.get_google_code(src), target=self.get_google_code(target_language))
            result = translator.translate(text)
            if result:
                self._cache[cache_key] = result
                logger.info(f"Translated: {src} -> {target_language}")
                return result
            return text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def translate_to_english(self, text, source_language=None):
        if not text or not source_language or source_language == "en":
            return text
        if not GOOGLE_TRANSLATE_AVAILABLE:
            return text
        try:
            translator = GoogleTranslator(source=self.get_google_code(source_language), target='en')
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text
    
    def translate_from_english(self, text, target_language):
        """Translate from English to target language - alias for translate"""
        return self.translate(text, target_language, source_language="en")
    
    def get_translation_engine(self):
        return "Google Translate" if GOOGLE_TRANSLATE_AVAILABLE else "None"


_translator_instance = None

def get_translator():
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = TranslationService()
    return _translator_instance

# Singleton for backward compatibility
translation_service = TranslationService()
