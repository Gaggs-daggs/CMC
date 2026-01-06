"""
Translation Service - Production Level
Uses AI4Bharat's IndicTrans2 transformer for natural, conversational translations

Supports all 22 scheduled Indian languages with:
- Natural conversational tone (not literal/mechanical)
- Medical term preservation
- Emotional intelligence in translations
- Batch translation support
"""

import logging
from typing import Optional, Dict, List
import time

from app.config import settings

logger = logging.getLogger(__name__)

# Try to import IndicTrans2 service
try:
    from app.services.nlp.indictrans_translator import (
        IndicTrans2Service,
        get_indictrans_service,
        INDIAN_LANGUAGES,
        MEDICAL_TERMS_TO_PRESERVE
    )
    INDICTRANS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"IndicTrans2 not available: {e}. Falling back to Google Translate.")
    INDICTRANS_AVAILABLE = False
    
    # Fallback language definitions
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
    Production-level translation service using IndicTrans2 transformer.
    Falls back to Google Translate if IndicTrans2 is not available.
    """
    
    def __init__(self):
        self._cache = {}
        self._supported_languages = INDIAN_LANGUAGES
        self._indictrans = None
        
        # Initialize IndicTrans2 if available
        if INDICTRANS_AVAILABLE:
            try:
                self._indictrans = get_indictrans_service()
                if self._indictrans.is_available():
                    logger.info("✅ TranslationService using IndicTrans2 transformer")
                else:
                    logger.warning("⚠️ IndicTrans2 model not loaded, will use Google Translate")
            except Exception as e:
                logger.error(f"Failed to initialize IndicTrans2: {e}")
    
    def is_using_transformer(self) -> bool:
        """Check if using IndicTrans2 transformer (vs Google Translate)"""
        return self._indictrans is not None and self._indictrans.is_available()
    
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
    
    def _google_translate_fallback(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> str:
        """Fallback to Google Translate"""
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(
                source=source_language or 'auto',
                target=target_language
            )
            return translator.translate(text)
        except Exception as e:
            logger.error(f"Google Translate fallback failed: {e}")
            return text
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        preserve_medical: bool = True
    ) -> str:
        """
        Translate text to target language using IndicTrans2 transformer.
        
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
        
        # Check cache
        cache_key = f"{src_lang}:{target_language}:{hash(text)}"
        if cache_key in self._cache:
            logger.debug("Translation cache hit")
            return self._cache[cache_key]
        
        try:
            # Use IndicTrans2 if available
            if self.is_using_transformer():
                translated_text = self._indictrans.translate(
                    text=text,
                    target_language=target_language,
                    source_language=src_lang,
                    preserve_medical=preserve_medical
                )
                logger.info(f"✅ IndicTrans2: {src_lang} -> {target_language}")
            else:
                # Fallback to Google Translate
                logger.warning(f"Using Google Translate fallback: {src_lang} -> {target_language}")
                translated_text = self._google_translate_fallback(
                    text, target_language, src_lang
                )
            
            # Cache result
            self._cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def translate_to_english(self, text: str, source_language: Optional[str] = None) -> str:
        """
        Translate text to English
        
        Args:
            text: Text to translate
            source_language: Source language (auto-detect if None)
        
        Returns:
            English translation
        """
        # Note: IndicTrans2 currently only supports En->Indic
        # For Indic->En, we use Google Translate fallback
        return self._google_translate_fallback(text, "en", source_language)
    
    def translate_from_english(self, text: str, target_language: str) -> str:
        """
        Translate from English to target Indian language
        Uses IndicTrans2 transformer for natural, conversational tone
        
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
        
        # Use IndicTrans2 batch translation if available
        if self.is_using_transformer():
            return self._indictrans.translate_batch(
                texts=texts,
                target_language=target_language,
                source_language=src_lang
            )
        
        # Fallback to individual translations
        translated = []
        for text in texts:
            translated_text = self.translate(text, target_language, src_lang)
            translated.append(translated_text)
            time.sleep(0.1)  # Rate limiting for Google Translate
        
        return translated
    
    def clear_cache(self):
        """Clear translation cache"""
        self._cache.clear()
        if self._indictrans:
            self._indictrans._cache.clear()
        logger.info("Translation cache cleared")
    
    def get_translation_engine(self) -> str:
        """Get the name of the translation engine being used"""
        if self.is_using_transformer():
            return "IndicTrans2 (AI4Bharat Transformer)"
        return "Google Translate (Fallback)"


# Global instance
translation_service = TranslationService()
