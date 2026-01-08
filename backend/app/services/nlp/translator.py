"""
Translation Service - Production Level
Uses Meta's NLLB-200 transformer for natural, conversational translations
Falls back to Google Translate if NLLB is not available

Supports all 22 scheduled Indian languages with:
- Natural conversational tone (not literal/mechanical)
- Medical term preservation
- Emotional intelligence in translations
- Batch translation support
- Aggressive caching for speed
"""

import logging
from typing import Optional, Dict, List
import time
import hashlib

from app.config import settings

logger = logging.getLogger(__name__)

# Try to import Google Translate as fallback
GOOGLE_TRANSLATE_AVAILABLE = False
try:
    from deep_translator import GoogleTranslator as GoogleTranslator
    GOOGLE_TRANSLATE_AVAILABLE = True
    logger.info("✅ Google Translate (deep-translator) available as fallback")
except ImportError:
    logger.warning("Google Translate not available (install deep-translator)")

# Try to import NLLB service
try:
    from app.services.nlp.indictrans_translator import (
        NLLBTranslationService,
        get_nllb_service,
        INDIAN_LANGUAGES,
        MEDICAL_TERMS_TO_PRESERVE
    )
    NLLB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"NLLB not available: {e}")
    NLLB_AVAILABLE = False
    
    # Fallback language definitions (only used if NLLB import fails)
    INDIAN_LANGUAGES = {
        "en": {"name": "English", "native": "English", "tts_code": "en-IN"},
        "hi": {"name": "Hindi", "native": "हिन्दी", "tts_code": "hi-IN"},
        "ta": {"name": "Tamil", "native": "தமிழ்", "tts_code": "ta-IN"},
        "te": {"name": "Telugu", "native": "తెలుగు", "tts_code": "te-IN"},
        "bn": {"name": "Bengali", "native": "বাংলা", "tts_code": "bn-IN"},
        "mr": {"name": "Marathi", "native": "मराठी", "tts_code": "mr-IN"},
        "gu": {"name": "Gujarati", "native": "ગુજરાતી", "tts_code": "gu-IN"},
        "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "tts_code": "kn-IN"},
        "ml": {"name": "Malayalam", "native": "മലയാളം", "tts_code": "ml-IN"},
        "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "tts_code": "pa-IN"},
        "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "tts_code": "or-IN"},
        "as": {"name": "Assamese", "native": "অসমীয়া", "tts_code": "as-IN"},
        "ur": {"name": "Urdu", "native": "اردو", "tts_code": "ur-IN"},
        "sa": {"name": "Sanskrit", "native": "संस्कृतम्", "tts_code": "sa-IN"},
        "ne": {"name": "Nepali", "native": "नेपाली", "tts_code": "ne-NP"},
        "si": {"name": "Sinhala", "native": "සිංහල", "tts_code": "si-LK"},
    }
    
    MEDICAL_TERMS_TO_PRESERVE = [
        "MRI", "CT scan", "X-ray", "ECG", "EKG", "BP", "BMI", "HIV", "AIDS",
        "COVID", "PCR", "ICU", "OPD", "IPD", "mg", "ml", "mcg", "IU",
        "Paracetamol", "Ibuprofen", "Aspirin", "Amoxicillin", "Metformin",
    ]


class TranslationService:
    """
    Production-level translation service using NLLB-200 transformer.
    Falls back to Google Translate if NLLB is not available.
    
    Speed optimizations:
    - Pre-cached common medical phrases (instant)
    - LRU memory cache (instant for repeated queries)
    - Disk persistence cache
    - INT8 quantization for CPU
    - Greedy decoding (vs beam search)
    """
    
    def __init__(self):
        self._cache = {}
        self._supported_languages = INDIAN_LANGUAGES
        self._nllb = None
        self._google_translator = None
        
        # Initialize NLLB if available
        if NLLB_AVAILABLE:
            try:
                self._nllb = get_nllb_service()
                if self._nllb.is_available():
                    logger.info("✅ TranslationService using NLLB-200 transformer")
                else:
                    logger.warning("⚠️ NLLB model not loaded")
            except Exception as e:
                logger.error(f"Failed to initialize NLLB: {e}")
        
        # Initialize Google Translate fallback
        if not self.is_using_transformer() and GOOGLE_TRANSLATE_AVAILABLE:
            try:
                # deep-translator uses class instantiation per translation
                self._google_translator = True  # Flag to indicate availability
                logger.info("✅ TranslationService using Google Translate fallback")
            except Exception as e:
                logger.error(f"Failed to initialize Google Translate: {e}")
    
    def is_using_transformer(self) -> bool:
        """Check if using NLLB transformer"""
        return self._nllb is not None and self._nllb.is_available()
    
    def is_using_google(self) -> bool:
        """Check if using Google Translate fallback"""
        return self._google_translator is not None and GOOGLE_TRANSLATE_AVAILABLE
    
    def get_supported_languages(self) -> Dict:
        """Get all supported Indian languages"""
        return self._supported_languages
    
    def get_language_info(self, lang_code: str) -> Optional[Dict]:
        """Get information about a specific language"""
        return self._supported_languages.get(lang_code)
    
    def get_tts_code(self, lang_code: str) -> str:
        """Get the TTS voice code for a language"""
        lang_info = self._supported_languages.get(lang_code, {})
        return lang_info.get("tts_code", "en-IN")
    
    def get_cache_stats(self) -> Dict:
        """Get translation cache statistics"""
        if self._nllb:
            return self._nllb.get_cache_stats()
        return {"cache_hits": 0, "cache_misses": 0, "hit_rate_percent": 0}
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        preserve_medical: bool = True
    ) -> str:
        """
        Translate text to target language using NLLB transformer ONLY.
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'hi', 'en', 'ta')
            source_language: Source language (defaults to 'en')
            preserve_medical: Whether to preserve medical terms in English
        
        Returns:
            Naturally translated text with conversational tone
        """
        if not text or not text.strip():
            return text
        
        # If target is English or same as source, no translation needed
        if target_language == "en":
            return text
        
        # Default source to English
        src_lang = source_language or "en"
        
        if src_lang == target_language:
            return text
        
        # Check local cache
        cache_key = f"{src_lang}:{target_language}:{hashlib.md5(text.encode()).hexdigest()}"
        if cache_key in self._cache:
            logger.debug("Translation cache hit (local)")
            return self._cache[cache_key]
        
        try:
            # Use NLLB if available
            if self.is_using_transformer():
                translated_text = self._nllb.translate(
                    text=text,
                    target_language=target_language,
                    source_language=src_lang,
                    preserve_medical=preserve_medical
                )
                logger.info(f"✅ NLLB: {src_lang} -> {target_language}")
            elif self.is_using_google():
                # Use Google Translate fallback (deep-translator)
                try:
                    translator = GoogleTranslator(source=src_lang, target=target_language)
                    translated_text = translator.translate(text)
                    logger.info(f"✅ Google Translate: {src_lang} -> {target_language}")
                except Exception as ge:
                    logger.error(f"Google Translate failed: {ge}")
                    translated_text = text
            else:
                # No translator available - return original text
                logger.warning(f"No translator available, returning original text")
                translated_text = text
            
            # Cache result locally
            self._cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original on error
    
    def translate_to_english(self, text: str, source_language: Optional[str] = None) -> str:
        """
        Translate text to English using NLLB
        
        Args:
            text: Text to translate
            source_language: Source language code
        
        Returns:
            English translation
        """
        if not source_language or source_language == "en":
            return text
        
        # NLLB supports Indic->English
        if self.is_using_transformer():
            return self._nllb.translate(
                text=text,
                target_language="en",
                source_language=source_language
            )
        return text
    
    def translate_from_english(self, text: str, target_language: str) -> str:
        """
        Translate from English to target Indian language
        Uses NLLB transformer for natural, conversational tone
        
        Args:
            text: English text to translate
            target_language: Target language code
        
        Returns:
            Naturally translated text
        """
        if target_language == "en":
            return text
        return self.translate(text, target_language, "en")
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None
    ) -> List[str]:
        """
        Translate multiple texts efficiently in batch
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language (defaults to 'en')
        
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        src_lang = source_language or "en"
        
        # Use NLLB batch translation if available
        if self.is_using_transformer():
            return self._nllb.translate_batch(
                texts=texts,
                target_language=target_language,
                source_language=src_lang
            )
        
        # Return original texts if NLLB not available
        return texts
    
    def clear_cache(self):
        """Clear translation cache"""
        self._cache.clear()
        if self._nllb:
            self._nllb._cache.clear()
        logger.info("Translation cache cleared")
    
    def get_translation_engine(self) -> str:
        """Get the name of the translation engine being used"""
        if self.is_using_transformer():
            return "NLLB-200 (Meta's No Language Left Behind)"
        elif self.is_using_google():
            return "Google Translate"
        return "None (translations disabled)"


# Global instance
translation_service = TranslationService()
