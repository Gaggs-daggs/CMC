"""
Conversation Handler
Coordinates NLP pipeline for processing user messages
"""

import logging
from typing import Tuple, List, Optional

from app.models.schemas import (
    ExtractedSymptom,
    DiagnosisResult,
    VitalsReading,
    LanguageCode
)
from app.services.nlp.language_detector import language_detector
from app.services.nlp.translator import translation_service
from app.services.nlp.symptom_extractor import symptom_extractor
from app.services.symptom_analyzer.analyzer import symptom_analyzer
from app.services.speech.tts_service import tts_service

logger = logging.getLogger(__name__)


class ConversationHandler:
    """Handles conversation processing through NLP pipeline"""
    
    async def process_text_message(
        self,
        user_message: str,
        user_language: Optional[str] = None,
        vitals: Optional[VitalsReading] = None
    ) -> Tuple[str, List[ExtractedSymptom], Optional[DiagnosisResult], float]:
        """
        Process user text message through NLP pipeline
        
       Args:
            user_message: User's input text
            user_language: Preferred language (auto-detect if None)
            vitals: Optional vitals reading
        
        Returns:
            Tuple of (response_text, extracted_symptoms, diagnosis, confidence)
        """
        try:
            # Step 1: Detect language if not provided
            if not user_language:
                user_language, lang_confidence = language_detector.detect_language(user_message)
                logger.info(f"Detected language: {user_language} (confidence: {lang_confidence:.2f})")
            
            # Step 2: Translate to English if needed for processing
            english_text = user_message
            if user_language != "en":
                english_text = translation_service.translate_to_english(user_message, user_language)
                logger.info(f"Translated to English: '{english_text}'")
            
            # Step 3: Extract symptoms
            symptoms = symptom_extractor.extract_symptoms(english_text, user_language)
            logger.info(f"Extracted {len(symptoms)} symptoms")
            
            # Step 4: Analyze symptoms and generate diagnosis
            diagnosis = symptom_analyzer.analyze(
                symptoms=symptoms,
                vitals=vitals,
                emotion_stress=0.0  # TODO: Add emotion detection
            )
            logger.info(f"Diagnosis complete: urgency={diagnosis.urgency_level}")
            
            # Step 5: Generate response
            response_text = self._generate_response(symptoms, diagnosis, user_language)
            
            # Step 6: Translate response back to user's language if needed
            if user_language != "en":
                response_text = translation_service.translate_from_english(response_text, user_language)
                logger.info(f"Translated response to {user_language}")
            
            return response_text, symptoms, diagnosis, diagnosis.confidence
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Return fallback response
            fallback = "I'm having trouble processing your message. Please try again or describe your symptoms differently."
            return fallback, [], None, 0.5
    
    def _generate_response(
        self,
        symptoms: List[ExtractedSymptom],
        diagnosis: DiagnosisResult,
        language: str
    ) -> str:
        """Generate human-readable response"""
        
        if not symptoms:
            return (
                "I couldn't identify specific symptoms from your message. "
                "Could you please describe what you're experiencing? "
                "For example: 'I have a fever and headache' or 'My stomach hurts'"
            )
        
        # Build response parts
        parts = []
        
        # Acknowledge symptoms
        symptom_names = [s.name.replace('_', ' ').title() for s in symptoms]
        if len(symptom_names) == 1:
            parts.append(f"I understand you have {symptom_names[0]}.")
        else:
            symptom_list = ", ".join(symptom_names[:-1]) + f" and {symptom_names[-1]}"
            parts.append(f"I understand you have {symptom_list}.")
        
        # Add urgency assessment
        if diagnosis.urgency_level == "emergency":
            parts.append("\n\n🚨 **URGENT:** This requires immediate medical attention!")
        elif diagnosis.urgency_level == "doctor_needed":
            parts.append("\n\n⚠️ You should see a doctor soon.")
        else:
            parts.append("\n\nThis appears to be manageable with self-care.")
        
        # Add possible conditions
        if diagnosis.possible_conditions:
            conditions = ", ".join(diagnosis.possible_conditions).replace('_', ' ').title()
            parts.append(f"\n\nPossible condition(s): {conditions}")
        
        # Add recommendations
        if diagnosis.recommendations:
            parts.append("\n\n**Recommendations:**")
            for i, rec in enumerate(diagnosis.recommendations, 1):
                parts.append(f"\n{i}. {rec}")
        
        # Add red flags
        if diagnosis.red_flags:
            parts.append("\n\n⚠️ **Warning Signs:**")
            for flag in diagnosis.red_flags:
                parts.append(f"\n• {flag}")
        
        # Add follow-up
        if diagnosis.follow_up_timeline:
            parts.append(f"\n\n📅 Follow up: {diagnosis.follow_up_timeline}")
        
        # Add emergency contact
        if diagnosis.emergency_contact:
            parts.append(f"\n\n🚨 Emergency: {diagnosis.emergency_contact}")
        
        # Add disclaimer
        parts.append(
            "\n\n---\n"
            "⚕️ This is general guidance only. For medical advice, please consult a qualified healthcare professional."
        )
        
        return "".join(parts)
    
    async def generate_voice_response(
        self,
        response_text: str,
        language: str
    ) -> str:
        """
        Generate voice audio from response text
        
        Args:
            response_text: Text to convert to speech
            language: Language code
        
        Returns:
            Path to generated audio file
        """
        try:
            # Remove markdown formatting for TTS
            clean_text = response_text.replace('**', '').replace('*', '').replace('#', '')
            clean_text = clean_text.replace('🚨', '').replace('⚠️', '').replace('📅', '').replace('⚕️', '')
            
            # Generate audio
            audio_path = tts_service.generate_speech(clean_text, language)
            logger.info(f"Generated voice response: {audio_path}")
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Failed to generate voice response: {e}")
            return None


# Global instance
conversation_handler = ConversationHandler()
