"""
Translation Service
Translates text between languages with comprehensive Indian language support
"""

import logging
from typing import Optional, Dict, List
from deep_translator import GoogleTranslator
import time

from app.config import settings

logger = logging.getLogger(__name__)

# Comprehensive Indian Languages Support
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

# Medical terms to preserve during translation (keep in English for accuracy)
MEDICAL_TERMS_TO_PRESERVE = [
    "MRI", "CT scan", "X-ray", "ECG", "EKG", "BP", "BMI", "HIV", "AIDS", 
    "COVID", "PCR", "ICU", "OPD", "IPD", "mg", "ml", "mcg", "IU",
    "Paracetamol", "Ibuprofen", "Aspirin", "Amoxicillin", "Metformin",
    "DNA", "RNA", "WBC", "RBC", "hemoglobin", "glucose", "cholesterol",
]


class TranslationService:
    """Translation service using Google Translate with Indian language focus"""
    
    def __init__(self):
        self._cache = {}  # Simple in-memory cache
        self._supported_languages = INDIAN_LANGUAGES
    
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
    
    def _preserve_medical_terms(self, text: str) -> tuple:
        """
        Replace medical terms with placeholders before translation
        Returns (modified_text, replacements_dict)
        """
        replacements = {}
        modified_text = text
        
        for i, term in enumerate(MEDICAL_TERMS_TO_PRESERVE):
            if term.lower() in modified_text.lower():
                placeholder = f"__MEDICAL_{i}__"
                # Case-insensitive replacement but preserve original
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                match = pattern.search(modified_text)
                if match:
                    original_term = match.group()
                    replacements[placeholder] = original_term
                    modified_text = pattern.sub(placeholder, modified_text, count=1)
        
        return modified_text, replacements
    
    def _restore_medical_terms(self, text: str, replacements: dict) -> str:
        """Restore medical terms after translation"""
        for placeholder, original in replacements.items():
            text = text.replace(placeholder, original)
        return text
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        preserve_medical: bool = True
    ) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'hi', 'en', 'ta')
            source_language: Source language (auto-detect if None)
            preserve_medical: Whether to preserve medical terms in English
        
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # If target is English, no translation needed
        if target_language == "en":
            return text
        
        # Check cache
        cache_key = f"{source_language or 'auto'}:{target_language}:{hash(text)}"
        if cache_key in self._cache:
            logger.debug(f"Translation cache hit")
            return self._cache[cache_key]
        
        try:
            # Preserve medical terms if requested
            text_to_translate = text
            replacements = {}
            if preserve_medical:
                text_to_translate, replacements = self._preserve_medical_terms(text)
            
            # Translate using deep-translator
            translator = GoogleTranslator(
                source=source_language or 'auto',
                target=target_language
            )
            translated_text = translator.translate(text_to_translate)
            
            # Restore medical terms
            if preserve_medical and replacements:
                translated_text = self._restore_medical_terms(translated_text, replacements)
            
            logger.info(
                f"Translated: {source_language or 'auto'} -> {target_language} "
                f"(preserved {len(replacements)} medical terms)"
            )
            
            # Cache result
            self._cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original text if translation fails
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
        return self.translate(text, "en", source_language)
    
    def translate_from_english(self, text: str, target_language: str) -> str:
        """
        Translate from English to target language
        
        Args:
            text: English text to translate
            target_language: Target language code
        
        Returns:
            Translated text
        """
        if target_language == "en":
            return text
        return self.translate(text, target_language, "en")
    
    def translate_batch(
        self,
        texts: list,
        target_language: str,
        source_language: Optional[str] = None
    ) -> list:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language (auto-detect if None)
        
        Returns:
            List of translated texts
        """
        translated = []
        for text in texts:
            translated_text = self.translate(text, target_language, source_language)
            translated.append(translated_text)
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return translated
    
    def preserve_medical_terms(self, text: str) -> str:
        """
        Preserve medical terminology during translation
        
        This is a placeholder for future implementation where we
        identify and preserve medical terms
        
        Args:
            text: Text with medical terms
        
        Returns:
            Text with medical terms marked for preservation
        """
        # TODO: Implement medical term preservation
        # Could use NER to identify medical terms and wrap them
        # Example: "I have {fever} and {headache}" to preserve during translation
        return text
    
    def clear_cache(self):
        """Clear translation cache"""
        self._cache.clear()
        logger.info("Translation cache cleared")


# Global instance
translation_service = TranslationService()
