"""
Medical Safety Guardrails System
Prevents unsafe medical advice, blocks prescriptions, handles emergencies

This module ensures the AI NEVER:
- Prescribes medication dosages for serious conditions
- Provides diagnosis for serious conditions
- Misses emergency escalation
- Gives advice that could delay emergency care
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyAction(Enum):
    """Actions the safety system can take"""
    ALLOW = "allow"                    # Response is safe
    MODIFY = "modify"                  # Response needs modification
    BLOCK = "block"                    # Response should be blocked
    ESCALATE = "escalate"              # Escalate to emergency
    ADD_DISCLAIMER = "add_disclaimer"  # Add safety disclaimer


@dataclass
class SafetyCheckResult:
    """Result of safety check"""
    action: SafetyAction
    is_safe: bool
    violations: List[str]
    modified_response: Optional[str]
    disclaimer: Optional[str]
    emergency_triggered: bool
    escalation_reason: Optional[str]


# ============= SAFETY RULES =============

# Words that trigger prescription blocking
PRESCRIPTION_TRIGGERS = [
    "prescribe", "prescription", "you should take", "take this medication",
    "dosage for", "mg twice daily", "tablets daily", "inject", "infusion",
    "antibiotics for", "steroid for", "controlled substance"
]

# Conditions that require professional diagnosis (AI cannot diagnose)
SERIOUS_CONDITIONS = [
    "heart attack", "myocardial infarction", "stroke", "cancer", "tumor",
    "diabetes", "hypertension", "epilepsy", "seizure disorder", "hiv", "aids",
    "tuberculosis", "hepatitis", "kidney disease", "liver disease", "meningitis",
    "appendicitis", "pneumonia", "blood clot", "pulmonary embolism", "aneurysm"
]

# Emergency keywords that trigger immediate escalation
EMERGENCY_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life", "self harm",
    "cutting myself", "overdose", "chest pain", "can't breathe", "heart attack",
    "stroke symptoms", "unconscious", "severe bleeding", "poisoning", "choking"
]

# Phrases AI must NEVER say
FORBIDDEN_PHRASES = [
    "you definitely have", "you are diagnosed with", "i diagnose you",
    "this is certainly", "100% sure", "guaranteed cure", "miracle cure",
    "don't go to doctor", "skip the hospital", "no need for medical care",
    "stop taking your medication", "ignore your doctor"
]

# Required disclaimers by category
DISCLAIMERS = {
    "general": "⚕️ This information is for educational purposes only and not a substitute for professional medical advice. Please consult a healthcare provider for proper diagnosis and treatment.",
    "medication": "💊 Never start, stop, or change medication without consulting your doctor or pharmacist. Dosages mentioned are general guidelines only.",
    "mental_health": "🧠 If you're experiencing a mental health crisis, please reach out to a professional. Helplines: iCALL 9152987821, AASRA 9820466726",
    "emergency": "🚨 This appears to be a medical emergency. Please call 108 (ambulance) or go to the nearest emergency room immediately.",
    "serious_condition": "⚠️ The symptoms you describe may indicate a serious condition that requires professional medical evaluation. Please see a doctor promptly."
}


class MedicalSafetyGuard:
    """
    Production-grade medical safety guardrails
    
    Ensures all AI responses are:
    - Safe and not harmful
    - Appropriately disclaimed
    - Not prescriptive for serious conditions
    - Properly escalated for emergencies
    """
    
    def __init__(self):
        self.prescription_patterns = [re.compile(p, re.IGNORECASE) for p in PRESCRIPTION_TRIGGERS]
        self.emergency_patterns = [re.compile(p, re.IGNORECASE) for p in EMERGENCY_KEYWORDS]
        logger.info("✅ Medical Safety Guard initialized")
    
    def check_response(
        self,
        response: str,
        user_input: str,
        detected_symptoms: List[str] = None
    ) -> SafetyCheckResult:
        """
        Check if AI response is safe to send
        
        Args:
            response: The AI-generated response
            user_input: Original user input
            detected_symptoms: Symptoms detected from input
        
        Returns:
            SafetyCheckResult with action to take
        """
        violations = []
        action = SafetyAction.ALLOW
        modified_response = response
        disclaimer = None
        emergency = False
        escalation_reason = None
        
        # 1. Check for emergency in user input
        emergency, escalation_reason = self._check_emergency(user_input)
        if emergency:
            action = SafetyAction.ESCALATE
            disclaimer = DISCLAIMERS["emergency"]
            modified_response = self._add_emergency_response(response)
            return SafetyCheckResult(
                action=action,
                is_safe=True,  # Safe because we're escalating
                violations=[],
                modified_response=modified_response,
                disclaimer=disclaimer,
                emergency_triggered=True,
                escalation_reason=escalation_reason
            )
        
        # 2. Check for forbidden phrases
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in response.lower():
                violations.append(f"Forbidden phrase: '{phrase}'")
                action = SafetyAction.MODIFY
                modified_response = self._remove_phrase(modified_response, phrase)
        
        # 3. Check for prescription language
        if self._has_prescription_language(response):
            violations.append("Contains prescription-like language")
            action = SafetyAction.MODIFY
            modified_response = self._soften_prescription_language(modified_response)
            disclaimer = DISCLAIMERS["medication"]
        
        # 4. Check for serious condition diagnosis
        for condition in SERIOUS_CONDITIONS:
            if condition.lower() in response.lower():
                if "you have" in response.lower() or "diagnosed" in response.lower():
                    violations.append(f"Appears to diagnose serious condition: {condition}")
                    action = SafetyAction.MODIFY
                    disclaimer = DISCLAIMERS["serious_condition"]
        
        # 5. Check mental health content
        if self._is_mental_health_content(user_input, response):
            if not disclaimer:
                disclaimer = DISCLAIMERS["mental_health"]
            # Ensure helpline is mentioned
            if "9152987821" not in response and "icall" not in response.lower():
                modified_response = self._add_mental_health_resources(modified_response)
        
        # 6. Add general disclaimer if none set
        if not disclaimer:
            disclaimer = DISCLAIMERS["general"]
        
        # 7. Ensure disclaimer is in response
        if disclaimer and disclaimer not in modified_response:
            modified_response = f"{modified_response}\n\n{disclaimer}"
        
        return SafetyCheckResult(
            action=action,
            is_safe=len(violations) == 0 or action != SafetyAction.BLOCK,
            violations=violations,
            modified_response=modified_response,
            disclaimer=disclaimer,
            emergency_triggered=emergency,
            escalation_reason=escalation_reason
        )
    
    def check_input(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Pre-check user input for emergencies before processing
        
        Returns:
            (is_emergency, emergency_type)
        """
        return self._check_emergency(user_input)
    
    def _check_emergency(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if text contains emergency indicators"""
        text_lower = text.lower()
        
        for pattern in self.emergency_patterns:
            if pattern.search(text_lower):
                match = pattern.search(text_lower)
                return True, f"Emergency keyword detected: {match.group()}"
        
        return False, None
    
    def _has_prescription_language(self, text: str) -> bool:
        """Check if text contains prescription-like language"""
        for pattern in self.prescription_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _is_mental_health_content(self, user_input: str, response: str) -> bool:
        """Check if content is mental health related"""
        mental_keywords = ["anxiety", "depression", "stress", "panic", "worried", 
                         "sad", "lonely", "hopeless", "overwhelmed", "mental"]
        combined = (user_input + " " + response).lower()
        return any(kw in combined for kw in mental_keywords)
    
    def _remove_phrase(self, text: str, phrase: str) -> str:
        """Remove a forbidden phrase from text"""
        return re.sub(re.escape(phrase), "", text, flags=re.IGNORECASE)
    
    def _soften_prescription_language(self, text: str) -> str:
        """Replace prescriptive language with advisory language"""
        replacements = [
            (r"you should take", "you may consider discussing with your doctor about"),
            (r"take this medication", "a doctor might recommend"),
            (r"prescribe", "suggest consulting a doctor about"),
            (r"dosage for", "consult a healthcare provider for appropriate dosage of"),
        ]
        result = text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    def _add_emergency_response(self, response: str) -> str:
        """Add emergency information to response"""
        emergency_info = """
🚨 **IMPORTANT: This appears to be an emergency situation.**

**If you or someone is in immediate danger:**
- Call **108** (Ambulance) immediately
- Call **100** (Police) if needed
- Go to the nearest emergency room

**Mental Health Crisis Helplines (24/7):**
- iCALL: **9152987821**
- AASRA: **9820466726**
- Vandrevala Foundation: **1860-2662-345**

Your safety is the priority. Please reach out for help.
"""
        return emergency_info + "\n\n" + response
    
    def _add_mental_health_resources(self, response: str) -> str:
        """Add mental health resources to response"""
        resources = "\n\n💚 **Support is available:** If you need to talk to someone, iCALL (9152987821) provides free counseling."
        if resources not in response:
            return response + resources
        return response
    
    def get_safe_medication_info(self, medication: str) -> Dict:
        """
        Get medication info in a safe, non-prescriptive way
        """
        return {
            "note": f"Information about {medication} is for educational purposes only.",
            "recommendation": "Please consult a doctor or pharmacist before taking any medication.",
            "disclaimer": DISCLAIMERS["medication"]
        }


# Singleton instance
_safety_guard: Optional[MedicalSafetyGuard] = None

def get_safety_guard() -> MedicalSafetyGuard:
    """Get or create the safety guard singleton"""
    global _safety_guard
    if _safety_guard is None:
        _safety_guard = MedicalSafetyGuard()
    return _safety_guard
