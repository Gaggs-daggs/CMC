"""
Test NLP Pipeline
Quick test script to verify symptom extraction and analysis
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.nlp.language_detector import language_detector
from backend.app.services.nlp.translator import translation_service
from backend.app.services.nlp.symptom_extractor import symptom_extractor
from backend.app.services.symptom_analyzer.analyzer import symptom_analyzer
from backend.app.models.schemas import VitalsReading


def test_nlp_pipeline():
    """Test the NLP pipeline with sample inputs"""
    
    print("="* 60)
    print("Testing Multilingual NLP Pipeline")
    print("=" * 60)
    print()
    
    # Test 1: English input
    print("Test 1: English - Common Cold")
    print("-" * 40)
    text_en = "I have a fever, cough, and body ache for 2 days"
    
    lang, conf = language_detector.detect_language(text_en)
    print(f"Language: {lang} (confidence: {conf:.2f})")
    
    symptoms = symptom_extractor.extract_symptoms(text_en, lang)
    print(f"Extracted Symptoms:")
    for s in symptoms:
        print(f"  - {s.name} (severity: {s.severity}, duration: {s.duration})")
    
    diagnosis = symptom_analyzer.analyze(symptoms)
    print(f"\nDiagnosis:")
    print(f"  Urgency: {diagnosis.urgency_level}")
    print(f"  Conditions: {', '.join(diagnosis.possible_conditions)}")
    print(f"  Recommendations: {len(diagnosis.recommendations)}")
    print()
    
    # Test 2: Hindi input
    print("Test 2: Hindi - Fever and Headache")
    print("-" * 40)
    text_hi = "मुझे बुखार और सिर दर्द है"
    
    lang, conf = language_detector.detect_language(text_hi)
    print(f"Language: {lang} (confidence: {conf:.2f})")
    
    # Translate to English
    text_en2 = translation_service.translate_to_english(text_hi, lang)
    print(f"Translation: '{text_en2}'")
    
    symptoms2 = symptom_extractor.extract_symptoms(text_en2, lang)
    print(f"Extracted Symptoms:")
    for s in symptoms2:
        print(f"  - {s.name}")
    
    # Add vitals
    vitals = VitalsReading(
        heart_rate=95,
        spo2=97,
        temperature=101.5
    )
    
    diagnosis2 = symptom_analyzer.analyze(symptoms2, vitals)
    print(f"\nDiagnosis (with vitals):")
    print(f"  Urgency: {diagnosis2.urgency_level}")
    print(f"  Confidence: {diagnosis2.confidence:.2f}")
    print(f"  Recommendations:")
    for rec in diagnosis2.recommendations[:3]:
        print(f"    • {rec}")
    print()
    
    # Test 3: Emergency scenario
    print("Test 3: Emergency - Severe symptoms")
    print("-" * 40)
    text_emergency = "I have severe difficulty breathing and chest pain"
    
    symptoms3 = symptom_extractor.extract_symptoms(text_emergency, "en")
    print(f"Extracted Symptoms:")
    for s in symptoms3:
        print(f"  - {s.name} (severity: {s.severity})")
    
    vitals_emergency = VitalsReading(
        heart_rate=130,
        spo2=88,
        temperature=98.6
    )
    
    diagnosis3 = symptom_analyzer.analyze(symptoms3, vitals_emergency)
    print(f"\nDiagnosis:")
    print(f"  Urgency: {diagnosis3.urgency_level} ⚠️")
    print(f"  Emergency Contact: {diagnosis3.emergency_contact}")
    print(f"  Red Flags: {', '.join(diagnosis3.red_flags)}")
    print()
    
    # Test 4: Translation round-trip
    print("Test 4: Translation Round-trip")
    print("-" * 40)
    original = "You should rest and drink plenty of fluids"
    print(f"Original (EN): '{original}'")
    
    hindi_translation = translation_service.translate(original, "hi", "en")
    print(f"Hindi: '{hindi_translation}'")
    
    back_to_english = translation_service.translate(hindi_translation, "en", "hi")
    print(f"Back to EN: '{back_to_english}'")
    print()
    
    print("=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_nlp_pipeline()
