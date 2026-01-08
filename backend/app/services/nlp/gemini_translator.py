"""
Gemini Translation Service
Fast, accurate translation using Google Gemini API
Handles both input (native -> English) and output (English -> native) translation
Supports multiple API keys with automatic rotation on rate limits
"""

import os
import logging
import re
import time
from typing import Optional, Tuple, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Try to import Gemini (new package)
GEMINI_AVAILABLE = False
genai = None

try:
    from google import genai as google_genai
    from google.genai import types
    genai = google_genai
    GEMINI_AVAILABLE = True
    logger.info("Using new google-genai package")
except ImportError:
    try:
        # Fallback to old package
        import google.generativeai as old_genai
        genai = old_genai
        GEMINI_AVAILABLE = True
        logger.info("Using legacy google-generativeai package")
    except ImportError:
        logger.warning("No Gemini package available")

# Load multiple API keys
def load_api_keys() -> List[str]:
    """Load Gemini API keys from environment"""
    keys = []
    
    # First try comma-separated keys
    keys_str = os.getenv("GEMINI_API_KEYS", "")
    if keys_str:
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    
    # Also add single key if different
    single_key = os.getenv("GEMINI_API_KEY", "")
    if single_key and single_key not in keys:
        keys.append(single_key)
    
    return keys

GEMINI_API_KEYS = load_api_keys()

# Language code to name mapping
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
    "ne": "Nepali",
}


class GeminiTranslator:
    """Fast translation using Gemini API with key rotation"""
    
    def __init__(self):
        self.available = False
        self.client = None
        self.api_keys = GEMINI_API_KEYS.copy()
        self.current_key_index = 0
        self.rate_limit_cooldowns = {}  # Track cooldown times for each key
        self.is_new_api = False
        
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini not available - translation disabled")
            return
            
        if not self.api_keys:
            logger.warning("No GEMINI_API_KEYS set - translation disabled")
            return
        
        try:
            # Initialize with first available key
            self._configure_with_key(self.api_keys[0])
            self.available = True
            logger.info(f"✅ Gemini Translator initialized with {len(self.api_keys)} API key(s)")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def _configure_with_key(self, api_key: str):
        """Configure Gemini with specific API key"""
        try:
            # Try new google-genai package first
            from google import genai as google_genai
            self.client = google_genai.Client(api_key=api_key)
            self.is_new_api = True
            logger.info(f"🔑 Using new Gemini API with key ...{api_key[-6:]}")
        except ImportError:
            # Fallback to old package
            import google.generativeai as old_genai
            old_genai.configure(api_key=api_key)
            self.client = old_genai.GenerativeModel('gemini-2.0-flash')
            self.is_new_api = False
            logger.info(f"🔑 Using legacy Gemini API with key ...{api_key[-6:]}")
    
    def _rotate_key(self) -> bool:
        """Rotate to next available API key. Returns True if successful."""
        if len(self.api_keys) <= 1:
            return False
        
        current_time = time.time()
        
        # Try each key
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            next_key = self.api_keys[self.current_key_index]
            
            # Check if this key is in cooldown
            cooldown_until = self.rate_limit_cooldowns.get(next_key, 0)
            if current_time > cooldown_until:
                try:
                    self._configure_with_key(next_key)
                    logger.info(f"🔄 Rotated to key {self.current_key_index + 1}/{len(self.api_keys)}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to configure key: {e}")
        
        return False
    
    def _handle_rate_limit(self, api_key: str):
        """Mark a key as rate-limited with cooldown"""
        # 60-second cooldown for rate-limited keys
        self.rate_limit_cooldowns[api_key] = time.time() + 60
        logger.warning(f"⏳ Key ...{api_key[-6:]} rate limited, cooldown 60s")
    
    def _call_with_rotation(self, prompt: str, max_tokens: int = 200, temperature: float = 0.1) -> Optional[str]:
        """Call Gemini API with automatic key rotation on rate limits"""
        attempts = 0
        max_attempts = len(self.api_keys) + 1
        
        while attempts < max_attempts:
            try:
                current_key = self.api_keys[self.current_key_index]
                
                if self.is_new_api:
                    # New google-genai package
                    from google.genai import types
                    response = self.client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens
                        )
                    )
                    return response.text.strip() if response.text else None
                else:
                    # Old google-generativeai package
                    import google.generativeai as old_genai
                    response = self.client.generate_content(
                        prompt,
                        generation_config=old_genai.types.GenerationConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens
                        )
                    )
                    return response.text.strip()
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for rate limit (429) or quota exceeded
                if '429' in error_str or 'rate limit' in error_str or 'quota' in error_str or 'resource_exhausted' in error_str:
                    current_key = self.api_keys[self.current_key_index]
                    self._handle_rate_limit(current_key)
                    
                    if self._rotate_key():
                        attempts += 1
                        continue
                    else:
                        logger.error("All Gemini keys exhausted/rate-limited")
                        raise
                else:
                    # Other error, don't retry
                    raise
        
        raise Exception("Max retry attempts exceeded")
    
    def detect_and_translate_to_english(self, text: str, expected_language: str = None) -> Tuple[str, str, bool]:
        """
        Detect language and translate to English if needed.
        
        Args:
            text: Input text (could be in any language, romanized or native script)
            expected_language: The language the user has selected (hint)
        
        Returns:
            Tuple of (english_text, detected_language, was_translated)
        """
        if not self.available:
            return text, "en", False
        
        # Quick check if already English
        if self._is_likely_english(text):
            return text, "en", False
        
        try:
            prompt = f"""Analyze this text and translate to English if needed.

Input text: "{text}"
User's selected language: {LANGUAGE_NAMES.get(expected_language, 'Unknown')}

Instructions:
1. Detect the language (could be romanized Indian language like "ennaku vomit varuthu" which is Tamil)
2. If not English, translate to natural English
3. Preserve medical terms and symptom descriptions accurately

Respond in this exact format:
DETECTED: [language name]
ENGLISH: [english translation or original if already English]

Examples:
- "ennaku vomit varuthu" → DETECTED: Tamil (romanized), ENGLISH: I feel like vomiting
- "sir dard ho raha hai" → DETECTED: Hindi (romanized), ENGLISH: I have a headache
- "I have fever" → DETECTED: English, ENGLISH: I have fever
- "தலைவலி" → DETECTED: Tamil, ENGLISH: headache
- "pet mein dard" → DETECTED: Hindi (romanized), ENGLISH: stomach pain
"""
            
            result = self._call_with_rotation(prompt, max_tokens=200, temperature=0.1)
            
            if not result:
                return text, "unknown", False
            
            # Parse response
            detected = "unknown"
            english = text
            
            for line in result.split('\n'):
                if line.startswith('DETECTED:'):
                    detected = line.replace('DETECTED:', '').strip()
                elif line.startswith('ENGLISH:'):
                    english = line.replace('ENGLISH:', '').strip()
            
            was_translated = detected.lower() != "english"
            
            logger.info(f"🌐 Input translation: '{text}' ({detected}) → '{english}'")
            
            return english, detected, was_translated
            
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text, "unknown", False
    
    def translate_to_language(self, text: str, target_language: str, preserve_medical: bool = True) -> str:
        """
        Translate English text to target language.
        
        Args:
            text: English text to translate
            target_language: Target language code (e.g., 'ta', 'hi')
            preserve_medical: Whether to preserve medical terms in English
        
        Returns:
            Translated text
        """
        if not self.available:
            return text
        
        if target_language == "en":
            return text
        
        target_name = LANGUAGE_NAMES.get(target_language, "Hindi")
        
        try:
            preserve_instruction = ""
            if preserve_medical:
                preserve_instruction = """
Keep these medical terms in English (just transliterate if needed):
- Medicine names (Paracetamol, Ibuprofen, ORS, etc.)
- Dosage terms (mg, ml, tablets)
- Medical conditions if commonly known in English
"""
            
            prompt = f"""Translate this health-related text to {target_name}.

English text: "{text}"

Instructions:
1. Translate naturally to {target_name}
2. Use simple, easy-to-understand language
3. Be warm and caring in tone
{preserve_instruction}
4. Do NOT add any extra information or explanations
5. Just provide the translation, nothing else

Translation:"""
            
            translated = self._call_with_rotation(prompt, max_tokens=500, temperature=0.3)
            
            if not translated:
                raise Exception("Empty translation response")
            
            # Clean up any artifacts
            translated = translated.replace('Translation:', '').strip()
            translated = translated.strip('"\'')
            
            logger.info(f"🌐 Output translation: en → {target_language}")
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation to {target_language} failed: {e}")
            # Re-raise exception so caller can fallback to NLLB
            raise
    
    def _is_likely_english(self, text: str) -> bool:
        """Quick check if text is likely English"""
        # Check for non-ASCII characters (native scripts)
        if any(ord(c) > 127 for c in text):
            return False
        
        # Common English health words
        english_indicators = [
            'i have', 'i am', 'my', 'pain', 'ache', 'fever', 'cold',
            'headache', 'stomach', 'feeling', 'symptoms', 'doctor',
            'medicine', 'help', 'please', 'thank', 'hello', 'hi'
        ]
        
        text_lower = text.lower()
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        # If multiple English health words, likely English
        return english_count >= 2


# Singleton instance
_gemini_translator: Optional[GeminiTranslator] = None

def get_gemini_translator() -> GeminiTranslator:
    """Get or create Gemini translator singleton"""
    global _gemini_translator
    if _gemini_translator is None:
        _gemini_translator = GeminiTranslator()
    return _gemini_translator
