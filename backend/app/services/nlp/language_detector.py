"""
Language Detection Service
Identifies the language of input text
"""

import logging
from langdetect import detect, detect_langs, LangDetectException
from typing import Tuple, List

from app.config import settings

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Language detection service"""
    
    # Map langdetect codes to our language codes
    LANGUAGE_MAPPING = {
        "en": "en",
        "hi": "hi",
        "bn": "bn",
        "ta": "ta",
        "te": "te",
        "mr": "mr",
        "gu": "gu",
        "kn": "kn",
        "ml": "ml",
        "pa": "pa",
        "or": "or",
        "as": "as",
    }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text
        
        Args:
            text: Input text
        
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text or len(text.strip()) < 3:
            # Too short to detect reliably
            return settings.DEFAULT_LANGUAGE, 0.5
        
        try:
            # Get probabilities for all languages
            probabilities = detect_langs(text)
            
            if not probabilities:
                return settings.DEFAULT_LANGUAGE, 0.5
            
            # Get top detection
            top_detection = probabilities[0]
            detected_lang = str(top_detection.lang)
            confidence = top_detection.prob
            
            # Map to our language codes
            language_code = self.LANGUAGE_MAPPING.get(detected_lang, "en")
            
            # Verify it's a supported language
            if language_code not in settings.SUPPORTED_LANGUAGES:
                logger.warning(
                    f"Detected unsupported language: {detected_lang}, "
                    f"falling back to {settings.DEFAULT_LANGUAGE}"
                )
                return settings.DEFAULT_LANGUAGE, 0.5
            
            logger.info(f"Detected language: {language_code} (confidence: {confidence:.2f})")
            
            return language_code, confidence
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}, using default")
            return settings.DEFAULT_LANGUAGE, 0.5
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            return settings.DEFAULT_LANGUAGE, 0.5
    
    def get_all_probabilities(self, text: str) -> List[dict]:
        """
        Get probabilities for all detected languages
        
        Args:
            text: Input text
        
        Returns:
            List of {language: str, probability: float}
        """
        try:
            probabilities = detect_langs(text)
            
            results = []
            for prob in probabilities:
                lang_code = self.LANGUAGE_MAPPING.get(str(prob.lang), str(prob.lang))
                if lang_code in settings.SUPPORTED_LANGUAGES:
                    results.append({
                        "language": lang_code,
                        "probability": prob.prob
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get language probabilities: {e}")
            return [{
                "language": settings.DEFAULT_LANGUAGE,
                "probability": 0.5
            }]
    
    def is_language(self, text: str, expected_language: str, threshold: float = 0.7) -> bool:
        """
        Check if text is in expected language
        
        Args:
            text: Input text
            expected_language: Expected language code
            threshold: Confidence threshold
        
        Returns:
            True if language matches with sufficient confidence
        """
        detected_lang, confidence = self.detect_language(text)
        return detected_lang == expected_language and confidence >= threshold


# Global instance
language_detector = LanguageDetector()
