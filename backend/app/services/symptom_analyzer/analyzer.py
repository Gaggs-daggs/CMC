"""
Symptom Analyzer Service
Analyzes symptoms and generates health recommendations
"""

import logging
import json
from typing import List, Optional
from pathlib import Path

from app.models.schemas import (
    ExtractedSymptom,
    DiagnosisResult,
    UrgencyLevel,
    VitalsReading
)
from app.config import settings

logger = logging.getLogger(__name__)


class SymptomAnalyzer:
    """Analyze symptoms and generate diagnosis"""
    
    def __init__(self):
        self.knowledge_graph = self._load_knowledge_graph()
    
    def _load_knowledge_graph(self) -> dict:
        """Load medical knowledge graph"""
        try:
            kg_path = Path(settings.KNOWLEDGE_GRAPH_PATH)
            with open(kg_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            return {"symptoms": {}, "conditions": {}}
    
    def analyze(
        self,
        symptoms: List[ExtractedSymptom],
        vitals: Optional[VitalsReading] = None,
        emotion_stress: float = 0.0
    ) -> DiagnosisResult:
        """
        Analyze symptoms and generate diagnosis
        """
        if not symptoms:
            return self._no_symptoms_diagnosis()
        
        logger.info(f"Analyzing {len(symptoms)} symptoms with vitals={vitals is not None}")
        
        # Check for missing information to generate follow-up questions
        questions = self._generate_follow_up_questions(symptoms)
        
        # Find matching conditions
        possible_conditions = self._match_conditions(symptoms)
        
        # Determine urgency level
        urgency_level, red_flags = self._determine_urgency(
            symptoms, vitals, possible_conditions, emotion_stress
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            urgency_level, possible_conditions, symptoms, vitals
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(symptoms, vitals)
        
        # If we have questions and urgency is NOT emergency, lower confidence and add questions
        if questions and urgency_level != UrgencyLevel.EMERGENCY:
            confidence *= 0.8 # Reduce confidence if info is missing
            # Prepend questions to recommendations to make it interactive
            # In a real system, this would be a separate field, but for now we add to response text
            recommendations = questions + ["---"] + recommendations
        
        # Determine follow-up timeline
        follow_up = self._determine_follow_up(urgency_level)
        
        # Emergency contact if needed
        emergency_contact = None
        if urgency_level == UrgencyLevel.EMERGENCY:
            emergency_contact = "108 (Ambulance) or 112 (Emergency)"
        
        diagnosis = DiagnosisResult(
            urgency_level=urgency_level,
            confidence=confidence,
            possible_conditions=[c['name'] for c in possible_conditions],
            recommendations=recommendations,
            red_flags=red_flags,
            follow_up_timeline=follow_up,
            emergency_contact=emergency_contact
        )
        
        return diagnosis

    def _generate_follow_up_questions(self, symptoms: List[ExtractedSymptom]) -> List[str]:
        """Generate clarifying questions for symptoms"""
        questions = []
        
        for symptom in symptoms:
            # Skip if we already have good info or it's a lab result
            if symptom.name in ['infection', 'low_platelets', 'emergency_condition']:
                continue
                
            if not symptom.severity:
                questions.append(f"❓ How severe is your {symptom.name.replace('_', ' ')}? (Mild, Moderate, or Severe?)")
            
            if not symptom.duration:
                questions.append(f"❓ How long have you had the {symptom.name.replace('_', ' ')}?")
                
        return questions[:2] # Limit to 2 questions to avoid overwhelming
    
    def _match_conditions(self, symptoms: List[ExtractedSymptom]) -> List[dict]:
        """Match symptoms to possible conditions"""
        symptom_names = {s.name for s in symptoms}
        conditions = []
        
        for condition_name, condition_data in self.knowledge_graph.get('conditions', {}).items():
            common_symptoms = set(condition_data.get('common_symptoms', []))
            
            # Calculate overlap
            overlap = symptom_names.intersection(common_symptoms)
            if overlap:
                match_score = len(overlap) / len(common_symptoms)
                conditions.append({
                    'name': condition_name,
                    'score': match_score,
                    'matched_symptoms': list(overlap),
                    'data': condition_data
                })
        
        # Sort by score
        conditions.sort(key=lambda x: x['score'], reverse=True)
        
        return conditions[:3]  # Top 3 conditions
    
    def _determine_urgency(
        self,
        symptoms: List[ExtractedSymptom],
        vitals: Optional[VitalsReading],
        conditions: List[dict],
        emotion_stress: float
    ) -> tuple:
        """Determine urgency level"""
        red_flags = []
        urgency_score = 0.0
        
        logger.info(f"Determining urgency for symptoms: {[s.name for s in symptoms]}")
        
        # Check emergency symptoms
        emergency_symptoms = self.knowledge_graph.get('emergency_conditions', [])
        for symptom in symptoms:
            if symptom.name in emergency_symptoms:
                red_flags.append(f"Emergency symptom detected: {symptom.name}")
                urgency_score += 3.0
            
            # Special handling for new emergency intent
            if symptom.name == 'emergency_condition':
                red_flags.append("⚠️ CRITICAL: Emergency intent detected")
                urgency_score += 10.0  # Immediate emergency
            
            if symptom.name == 'low_platelets' and symptom.severity == 'severe':
                red_flags.append("⚠️ CRITICAL: Very low platelets")
                urgency_score += 3.0
            
            if symptom.name == 'infection' and symptom.severity == 'severe':
                red_flags.append("Severe infection markers")
                urgency_score += 2.0

        # Check symptom severity
        for symptom in symptoms:
            symptom_data = self.knowledge_graph.get('symptoms', {}).get(symptom.name, {})
            urgency_factors = symptom_data.get('urgency_factors', {})
            
            if symptom.severity == 'severe':
                urgency_score += 1.5
                red_flags.append(f"Severe {symptom.name}")
            
            # Check specific urgency factors
            # Only count if we have evidence (which we don't have in current ExtractedSymptom)
            # So we skip this for now to avoid false positives
            pass
        
        # Check vitals for abnormalities
        if vitals:
            if vitals.spo2 and vitals.spo2 < 90:
                red_flags.append("⚠️ CRITICAL: Low blood oxygen (SpO₂ < 90%)")
                urgency_score += 3.0
            elif vitals.spo2 and vitals.spo2 < 95:
                red_flags.append("Low blood oxygen")
                urgency_score += 1.5
            
            if vitals.heart_rate and vitals.heart_rate > 120:
                red_flags.append("Very high heart rate")
                urgency_score += 1.5
            
            if vitals.temperature and vitals.temperature > 103:
                red_flags.append("Very high fever (>103°F)")
                urgency_score += 2.0
        
        # Check emotion stress
        if emotion_stress > 0.8:
            urgency_score += 0.5
            red_flags.append("High stress detected")
        
        # Determine final urgency level
        if urgency_score >= 3.0:
            urgency_level = UrgencyLevel.EMERGENCY
        elif urgency_score >= 1.0:
            urgency_level = UrgencyLevel.DOCTOR_NEEDED
        else:
            urgency_level = UrgencyLevel.SELF_CARE
        
        logger.info(f"Urgency calculation: score={urgency_score}, level={urgency_level}, red_flags={red_flags}")
        return urgency_level, red_flags
    
    def _generate_recommendations(
        self,
        urgency_level: UrgencyLevel,
        conditions: List[dict],
        symptoms: List[ExtractedSymptom],
        vitals: Optional[VitalsReading]
    ) -> List[str]:
        """Generate health recommendations"""
        recommendations = []
        
        if urgency_level == UrgencyLevel.EMERGENCY:
            recommendations.append("⚠️ SEEK IMMEDIATE MEDICAL ATTENTION")
            recommendations.append("Call 108 (Ambulance) or go to nearest hospital emergency room")
            recommendations.append("Do not drive yourself - ask someone to take you")
            return recommendations
        
        # Get recommendations from matched conditions
        if conditions:
            top_condition = conditions[0]
            condition_recommendations = top_condition['data'].get('recommendations', {}).get('en', [])
            recommendations.extend(condition_recommendations)
        
        # Add general recommendations based on urgency
        if urgency_level == UrgencyLevel.DOCTOR_NEEDED:
            recommendations.append("📋 Consult a doctor within 24-48 hours")
            recommendations.append("Monitor your symptoms and note any changes")
        else:
            recommendations.append("Monitor your symptoms for the next 24-48 hours")
            recommendations.append("Rest and stay hydrated")
        
        # Symptom-specific recommendations
        symptom_names = [s.name for s in symptoms]
        
        if 'fever' in symptom_names:
            recommendations.append("Take paracetamol for fever as directed")
            recommendations.append("Drink plenty of fluids")
        
        if 'headache' in symptom_names:
            recommendations.append("Rest in a quiet, dark room")
            recommendations.append("Apply cold compress to forehead")
        
        if 'cough' in symptom_names:
            recommendations.append("Drink warm liquids (tea, soup)")
            recommendations.append("Try steam inhalation")
        
        # Vitals-based recommendations
        if vitals:
            if vitals.temperature and vitals.temperature > 100.4:
                recommendations.append("Keep yourself cool, use light clothing")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:8]  # Max 8 recommendations
    
    def _calculate_confidence(
        self,
        symptoms: List[ExtractedSymptom],
        vitals: Optional[VitalsReading]
    ) -> float:
        """Calculate confidence score for diagnosis"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence with more symptoms
        if len(symptoms) >= 3:
            confidence += 0.2
        elif len(symptoms) >= 2:
            confidence += 0.1
        
        # Higher confidence with vitals data
        if vitals:
            confidence += 0.2
        
        # Factor in symptom confidence
        if symptoms:
            avg_symptom_confidence = sum(s.confidence for s in symptoms) / len(symptoms)
            confidence = (confidence + avg_symptom_confidence) / 2
        
        return min(confidence, 0.95)  # Cap at 0.95
    
    def _determine_follow_up(self, urgency_level: UrgencyLevel) -> str:
        """Determine follow-up timeline"""
        if urgency_level == UrgencyLevel.EMERGENCY:
            return "Immediately"
        elif urgency_level == UrgencyLevel.DOCTOR_NEEDED:
            return "Within 24-48 hours"
        else:
            return "If symptoms persist for more than 2-3 days or worsen"
    
    def _no_symptoms_diagnosis(self) -> DiagnosisResult:
        """Diagnosis when no symptoms are identified"""
        return DiagnosisResult(
            urgency_level=UrgencyLevel.SELF_CARE,
            confidence=0.5,
            possible_conditions=[],
            recommendations=[
                "No specific symptoms were identified.",
                "If you have health concerns, please describe them in more detail.",
                "You can also send a voice message to explain your symptoms."
            ],
            red_flags=[],
            follow_up_timeline="As needed",
            emergency_contact=None
        )


# Global instance
symptom_analyzer = SymptomAnalyzer()
