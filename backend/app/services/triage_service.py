"""
Smart Triage & Mental Health Detection Service
- Emergency detection with reasoning
- Urgency classification (Self-care → Doctor → Emergency)
- Mental health screening
- Crisis intervention
"""
import logging
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Triage classification levels
TRIAGE_LEVELS = {
    "emergency": {
        "priority": 1,
        "color": "#ef4444",
        "label": "🚨 EMERGENCY",
        "action": "Call emergency services (108/911) immediately",
        "timeframe": "Immediate - within minutes"
    },
    "urgent": {
        "priority": 2,
        "color": "#f97316",
        "label": "⚠️ URGENT",
        "action": "Visit emergency room or urgent care within hours",
        "timeframe": "Within 2-4 hours"
    },
    "doctor_soon": {
        "priority": 3,
        "color": "#fbbf24",
        "label": "🏥 See Doctor Soon",
        "action": "Schedule appointment with doctor",
        "timeframe": "Within 24-48 hours"
    },
    "doctor_routine": {
        "priority": 4,
        "color": "#60a5fa",
        "label": "📋 Routine Care",
        "action": "Schedule routine appointment",
        "timeframe": "Within 1-2 weeks"
    },
    "self_care": {
        "priority": 5,
        "color": "#4ade80",
        "label": "✅ Self-Care",
        "action": "Home remedies and monitoring",
        "timeframe": "Monitor for 2-3 days"
    }
}

# Emergency symptom patterns
EMERGENCY_PATTERNS = [
    {
        "patterns": ["chest pain", "chest tightness", "pressure in chest"],
        "co_symptoms": ["arm pain", "jaw pain", "shortness of breath", "sweating", "nausea"],
        "condition": "Possible Heart Attack",
        "reason": "Chest pain with radiating pain or breathing difficulty can indicate cardiac emergency",
        "action": "Call 108 immediately. Chew aspirin if not allergic. Don't drive yourself."
    },
    {
        "patterns": ["can't breathe", "cannot breathe", "difficulty breathing", "severe breathing"],
        "co_symptoms": ["blue lips", "gasping", "choking"],
        "condition": "Respiratory Emergency",
        "reason": "Severe breathing difficulty requires immediate medical intervention",
        "action": "Call 108. Sit upright. Loosen tight clothing. Stay calm."
    },
    {
        "patterns": ["stroke", "face drooping", "arm weakness", "speech difficulty", "slurred speech"],
        "co_symptoms": ["sudden confusion", "vision loss", "severe headache", "numbness"],
        "condition": "Possible Stroke",
        "reason": "FAST signs (Face, Arms, Speech, Time) indicate stroke - time critical",
        "action": "Call 108 immediately. Note time symptoms started. Don't give food/water."
    },
    {
        "patterns": ["unconscious", "not responding", "fainted", "collapsed", "unresponsive"],
        "co_symptoms": ["not breathing", "no pulse"],
        "condition": "Loss of Consciousness",
        "reason": "Unconsciousness can indicate serious underlying condition",
        "action": "Call 108. Check breathing. Place in recovery position if breathing."
    },
    {
        "patterns": ["severe bleeding", "won't stop bleeding", "blood everywhere", "heavy bleeding"],
        "co_symptoms": ["deep cut", "wound"],
        "condition": "Severe Hemorrhage",
        "reason": "Uncontrolled bleeding can lead to shock",
        "action": "Apply direct pressure. Elevate if possible. Call 108."
    },
    {
        "patterns": ["suicide", "kill myself", "want to die", "end my life", "suicidal"],
        "co_symptoms": ["hopeless", "no reason to live"],
        "condition": "Mental Health Crisis",
        "reason": "Suicidal thoughts require immediate professional intervention",
        "action": "Call iCall: 9152987821 or Vandrevala: 1860-2662-345. You're not alone."
    },
    {
        "patterns": ["overdose", "took too many pills", "poisoning", "swallowed poison"],
        "co_symptoms": ["vomiting", "confusion", "drowsy"],
        "condition": "Poisoning/Overdose",
        "reason": "Poisoning requires immediate medical attention",
        "action": "Call 108 and Poison Control. Don't induce vomiting unless directed."
    },
    {
        "patterns": ["severe allergic", "anaphylaxis", "throat swelling", "can't swallow"],
        "co_symptoms": ["hives", "swelling", "difficulty breathing"],
        "condition": "Anaphylactic Reaction",
        "reason": "Severe allergic reaction can cause airway closure",
        "action": "Call 108. Use EpiPen if available. Lie flat with legs elevated."
    }
]

# Urgent (non-emergency) patterns
URGENT_PATTERNS = [
    {
        "patterns": ["high fever", "fever 103", "fever 104", "very high temperature"],
        "condition": "High Fever",
        "reason": "Fever above 103°F (39.4°C) needs prompt evaluation",
        "timeframe": "Within 2-4 hours"
    },
    {
        "patterns": ["severe pain", "unbearable pain", "worst pain", "10/10 pain"],
        "condition": "Severe Pain",
        "reason": "Severe uncontrolled pain needs urgent assessment",
        "timeframe": "Within 2-4 hours"
    },
    {
        "patterns": ["blood in urine", "blood in stool", "vomiting blood", "coughing blood"],
        "condition": "Internal Bleeding Signs",
        "reason": "Blood in bodily fluids can indicate internal issues",
        "timeframe": "Within 2-4 hours"
    },
    {
        "patterns": ["severe headache", "worst headache", "thunderclap headache"],
        "condition": "Severe Headache",
        "reason": "Sudden severe headache can indicate serious conditions",
        "timeframe": "Within 2-4 hours"
    },
    {
        "patterns": ["dehydration", "not urinating", "very thirsty", "dry mouth extreme"],
        "condition": "Severe Dehydration",
        "reason": "Severe dehydration can lead to organ damage",
        "timeframe": "Within 2-4 hours"
    }
]

# Serious medical conditions requiring specialist consultation (NOT self-care or OTC meds)
SERIOUS_CONDITIONS = [
    {
        "patterns": ["tumour", "tumor", "cancer", "lump", "mass", "growth", "malignant", "benign"],
        "condition": "Possible Tumor/Cancer Concern",
        "level": "doctor_soon",
        "reason": "Any tumor or cancer concern requires proper medical evaluation by a specialist",
        "action": "Please consult an oncologist or specialist doctor for proper diagnosis and treatment plan",
        "no_otc": True,  # Don't suggest OTC medications
        "emotional_support": True  # Needs empathetic response
    },
    {
        "patterns": ["diabetes", "diabetic", "blood sugar high", "insulin"],
        "condition": "Diabetes Management",
        "level": "doctor_soon",
        "reason": "Diabetes requires proper medical supervision and prescription medications",
        "action": "Consult an endocrinologist or your primary care physician",
        "no_otc": True
    },
    {
        "patterns": ["heart disease", "heart condition", "cardiac", "arrhythmia", "heart failure"],
        "condition": "Heart Condition",
        "level": "doctor_soon", 
        "reason": "Heart conditions require specialist care and monitoring",
        "action": "Please see a cardiologist for proper evaluation",
        "no_otc": True
    },
    {
        "patterns": ["kidney disease", "kidney failure", "dialysis"],
        "condition": "Kidney Condition",
        "level": "doctor_soon",
        "reason": "Kidney conditions require specialist care",
        "action": "Consult a nephrologist",
        "no_otc": True
    },
    {
        "patterns": ["hiv", "aids", "hepatitis"],
        "condition": "Infectious Disease",
        "level": "doctor_soon",
        "reason": "These conditions require specialized medical care and antiretroviral/antiviral therapy",
        "action": "Please consult an infectious disease specialist",
        "no_otc": True
    },
    {
        "patterns": ["surgery", "operation", "post-op", "surgical"],
        "condition": "Surgical Concern",
        "level": "doctor_soon",
        "reason": "Surgical concerns need proper medical evaluation",
        "action": "Consult your surgeon or a specialist",
        "no_otc": True
    },
    {
        "patterns": ["pregnant", "pregnancy", "expecting baby", "morning sickness"],
        "condition": "Pregnancy",
        "level": "doctor_routine",
        "reason": "Pregnancy requires regular prenatal care",
        "action": "Please consult your OB-GYN for proper prenatal care",
        "no_otc": True  # Many OTC meds are contraindicated in pregnancy
    }
]

# Mental health indicators
MENTAL_HEALTH_INDICATORS = {
    "depression": {
        "keywords": ["depressed", "sad all the time", "no energy", "hopeless", "worthless", 
                    "can't enjoy", "lost interest", "empty inside", "crying", "no motivation",
                    "don't care anymore", "what's the point", "tired of living"],
        "severity_escalators": ["every day", "weeks", "months", "always", "constant"],
        "questions": [
            "How long have you been feeling this way?",
            "Are you able to do your daily activities?",
            "Do you have thoughts of harming yourself?"
        ]
    },
    "anxiety": {
        "keywords": ["anxious", "worried", "panic", "can't relax", "racing thoughts",
                    "fear", "nervous", "scared", "heart racing", "can't calm down",
                    "overthinking", "restless", "on edge", "tense"],
        "severity_escalators": ["panic attack", "can't breathe", "chest tight", "constant"],
        "questions": [
            "What triggers your anxiety?",
            "How often do you feel this way?",
            "Does it affect your sleep or daily life?"
        ]
    },
    "stress": {
        "keywords": ["stressed", "overwhelmed", "too much pressure", "can't cope",
                    "burnout", "exhausted", "breaking point", "falling apart"],
        "severity_escalators": ["can't handle", "breaking down", "losing control"],
        "questions": [
            "What's causing the most stress?",
            "Are you getting enough rest?",
            "Do you have support from family or friends?"
        ]
    },
    "grief": {
        "keywords": ["lost someone", "death", "died", "grieving", "mourning",
                    "miss them", "passed away", "gone forever"],
        "severity_escalators": ["can't go on", "want to join them"],
        "questions": [
            "I'm sorry for your loss. When did this happen?",
            "Do you have people to talk to about this?",
            "Are you taking care of basic needs like eating and sleeping?"
        ]
    },
    "loneliness": {
        "keywords": ["lonely", "alone", "no friends", "isolated", "nobody cares",
                    "no one to talk to", "feel invisible", "abandoned"],
        "severity_escalators": ["completely alone", "nobody would notice"],
        "questions": [
            "When did you start feeling this way?",
            "Is there anyone you can reach out to?",
            "Would you like to talk about what's making you feel isolated?"
        ]
    },
    "crisis": {
        "keywords": ["suicide", "kill myself", "want to die", "end it all", "no point living",
                    "better off dead", "self-harm", "cutting myself", "hurt myself"],
        "severity_escalators": ["have a plan", "going to do it", "goodbye"],
        "immediate_response": True
    }
}

# Supportive responses for mental health
SUPPORTIVE_RESPONSES = {
    "depression": {
        "acknowledgment": "I hear you, and I want you to know that what you're feeling is valid. Depression is real and treatable.",
        "support": "You don't have to face this alone. Many people have felt this way and found help.",
        "resources": [
            "iCall (Free counseling): 9152987821",
            "Vandrevala Foundation: 1860-2662-345-6",
            "NIMHANS: 080-46110007"
        ],
        "self_care": [
            "Try to maintain a routine, even a simple one",
            "Small walks or any movement can help",
            "Reach out to one person you trust",
            "Be gentle with yourself - recovery takes time"
        ]
    },
    "anxiety": {
        "acknowledgment": "Anxiety can feel overwhelming, but you're not alone in this. What you're experiencing is a real challenge.",
        "support": "Let's work through this together. Anxiety is manageable with the right support.",
        "grounding_exercise": "Try this: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
        "breathing_exercise": "Breathe in for 4 counts, hold for 4, breathe out for 6. Repeat 5 times.",
        "resources": [
            "iCall: 9152987821",
            "Vandrevala Foundation: 1860-2662-345-6"
        ]
    },
    "crisis": {
        "acknowledgment": "I'm really glad you're reaching out. What you're feeling right now is serious, and you deserve immediate support.",
        "urgent_message": "Please reach out to a crisis helpline right now. Someone is available 24/7 to talk with you.",
        "resources": [
            "🆘 iCall (24/7): 9152987821",
            "🆘 Vandrevala Foundation (24/7): 1860-2662-345-6",
            "🆘 AASRA: 9820466726"
        ],
        "safety": "If you're in immediate danger, please call 108 or go to the nearest hospital emergency."
    },
    "general": {
        "acknowledgment": "Thank you for sharing how you're feeling. It takes courage to talk about this.",
        "support": "Your mental health matters just as much as physical health.",
        "resources": [
            "iCall (Free counseling): 9152987821",
            "Vandrevala Foundation: 1860-2662-345-6"
        ]
    }
}


class TriageService:
    """Smart triage system for medical urgency classification"""
    
    def __init__(self):
        self.emergency_patterns = EMERGENCY_PATTERNS
        self.urgent_patterns = URGENT_PATTERNS
        self.serious_conditions = SERIOUS_CONDITIONS
        self.triage_levels = TRIAGE_LEVELS
    
    def analyze(self, message: str, vitals: Dict = None) -> Dict[str, Any]:
        """
        Analyze message and vitals to determine triage level
        """
        message_lower = message.lower()
        
        # Check for emergency patterns first
        emergency_match = self._check_emergency(message_lower)
        if emergency_match:
            return {
                "level": "emergency",
                **self.triage_levels["emergency"],
                "detected_condition": emergency_match["condition"],
                "reason": emergency_match["reason"],
                "specific_action": emergency_match["action"],
                "co_symptoms_found": emergency_match.get("co_symptoms_found", []),
                "no_otc": True
            }
        
        # Check for serious medical conditions (tumors, cancer, diabetes, etc.)
        serious_match = self._check_serious_conditions(message_lower)
        if serious_match:
            level = serious_match.get("level", "doctor_soon")
            return {
                "level": level,
                **self.triage_levels[level],
                "detected_condition": serious_match["condition"],
                "reason": serious_match["reason"],
                "specific_action": serious_match.get("action", "Please consult a specialist"),
                "no_otc": serious_match.get("no_otc", True),
                "emotional_support": serious_match.get("emotional_support", False)
            }
        
        # Check for urgent patterns
        urgent_match = self._check_urgent(message_lower)
        if urgent_match:
            return {
                "level": "urgent",
                **self.triage_levels["urgent"],
                "detected_condition": urgent_match["condition"],
                "reason": urgent_match["reason"],
                "specific_timeframe": urgent_match.get("timeframe", "Within 2-4 hours"),
                "no_otc": False
            }
        
        # Check vitals if provided
        if vitals:
            vitals_triage = self._check_vitals(vitals)
            if vitals_triage:
                return vitals_triage
        
        # Check for doctor-needed patterns
        doctor_needed = self._check_doctor_needed(message_lower)
        if doctor_needed:
            return {
                "level": "doctor_soon",
                **self.triage_levels["doctor_soon"],
                "reason": doctor_needed,
                "no_otc": False
            }
        
        # Default to self-care
        return {
            "level": "self_care",
            **self.triage_levels["self_care"],
            "reason": "Symptoms appear manageable with home care and monitoring",
            "no_otc": False
        }
    
    def _check_serious_conditions(self, message: str) -> Dict | None:
        """Check for serious medical conditions that need specialist care"""
        for condition in self.serious_conditions:
            if any(p in message for p in condition["patterns"]):
                return condition
        return None
    
    def _check_emergency(self, message: str) -> Dict | None:
        """Check for emergency patterns"""
        for pattern in self.emergency_patterns:
            # Check main patterns
            main_match = any(p in message for p in pattern["patterns"])
            if main_match:
                # Check for co-symptoms (increases confidence)
                co_symptoms_found = [s for s in pattern.get("co_symptoms", []) if s in message]
                
                # If main pattern matches AND has co-symptoms, definitely emergency
                # If only main pattern for critical conditions, still emergency
                if co_symptoms_found or pattern["condition"] in ["Mental Health Crisis", "Possible Heart Attack", "Respiratory Emergency"]:
                    return {
                        **pattern,
                        "co_symptoms_found": co_symptoms_found
                    }
        return None
    
    def _check_urgent(self, message: str) -> Dict | None:
        """Check for urgent (non-emergency) patterns"""
        for pattern in self.urgent_patterns:
            if any(p in message for p in pattern["patterns"]):
                return pattern
        return None
    
    def _check_vitals(self, vitals: Dict) -> Dict | None:
        """Check vitals for concerning values"""
        concerns = []
        
        # Heart rate
        hr = vitals.get("heartRate") or vitals.get("heart_rate")
        if hr:
            if hr > 120 or hr < 50:
                concerns.append(f"Heart rate {hr} bpm is outside normal range")
        
        # Blood oxygen
        spo2 = vitals.get("spo2") or vitals.get("oxygen")
        if spo2:
            if spo2 < 92:
                return {
                    "level": "emergency",
                    **self.triage_levels["emergency"],
                    "detected_condition": "Low Blood Oxygen",
                    "reason": f"SpO2 of {spo2}% is dangerously low (normal: 95-100%)",
                    "specific_action": "Seek immediate medical attention. Low oxygen can be life-threatening."
                }
            elif spo2 < 95:
                concerns.append(f"SpO2 {spo2}% is below normal")
        
        # Temperature
        temp = vitals.get("temp") or vitals.get("temperature")
        if temp:
            temp_f = float(temp) if isinstance(temp, (int, float, str)) else 98.6
            if temp_f > 103:
                return {
                    "level": "urgent",
                    **self.triage_levels["urgent"],
                    "detected_condition": "High Fever",
                    "reason": f"Temperature {temp_f}°F requires prompt medical evaluation"
                }
            elif temp_f > 100.4:
                concerns.append(f"Fever of {temp_f}°F detected")
        
        # Blood pressure (if available)
        bp = vitals.get("bp") or vitals.get("bloodPressure")
        if bp and "/" in str(bp):
            try:
                systolic, diastolic = map(int, str(bp).split("/"))
                if systolic > 180 or diastolic > 120:
                    return {
                        "level": "urgent",
                        **self.triage_levels["urgent"],
                        "detected_condition": "Hypertensive Crisis",
                        "reason": f"Blood pressure {bp} mmHg is critically high"
                    }
                elif systolic > 140 or diastolic > 90:
                    concerns.append(f"Elevated blood pressure: {bp}")
            except:
                pass
        
        if concerns:
            return {
                "level": "doctor_soon",
                **self.triage_levels["doctor_soon"],
                "reason": "; ".join(concerns)
            }
        
        return None
    
    def _check_doctor_needed(self, message: str) -> str | None:
        """Check if symptoms warrant doctor visit"""
        doctor_indicators = [
            ("persistent", "Persistent symptoms need professional evaluation"),
            ("getting worse", "Worsening symptoms should be evaluated"),
            ("not improving", "Symptoms not improving may need treatment"),
            ("several days", "Prolonged symptoms warrant medical attention"),
            ("recurring", "Recurring symptoms should be investigated"),
            ("unusual", "Unusual symptoms deserve professional assessment"),
            ("never had before", "New symptoms should be evaluated by a doctor"),
            ("concerned", "When you're concerned, it's best to see a doctor"),
            ("pregnant", "Symptoms during pregnancy need medical attention"),
            ("diabetes", "Diabetic patients should consult doctor for new symptoms"),
            ("heart condition", "Those with heart conditions need prompt evaluation"),
        ]
        
        for indicator, reason in doctor_indicators:
            if indicator in message:
                return reason
        
        return None


class MentalHealthService:
    """Mental health detection and supportive intervention"""
    
    def __init__(self):
        self.indicators = MENTAL_HEALTH_INDICATORS
        self.responses = SUPPORTIVE_RESPONSES
    
    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analyze message for mental health indicators
        """
        message_lower = message.lower()
        
        detected = {
            "has_mental_health_content": False,
            "categories": [],
            "severity": "low",
            "is_crisis": False,
            "supportive_response": None,
            "resources": [],
            "follow_up_questions": [],
            "grounding_exercise": None
        }
        
        # Check for crisis first (highest priority)
        crisis_check = self._check_crisis(message_lower)
        if crisis_check["is_crisis"]:
            return {
                "has_mental_health_content": True,
                "categories": ["crisis"],
                "severity": "critical",
                "is_crisis": True,
                "supportive_response": self._build_crisis_response(),
                "resources": self.responses["crisis"]["resources"],
                "immediate_action_needed": True
            }
        
        # Check other mental health categories
        for category, data in self.indicators.items():
            if category == "crisis":
                continue
                
            keyword_matches = [kw for kw in data["keywords"] if kw in message_lower]
            if keyword_matches:
                detected["has_mental_health_content"] = True
                detected["categories"].append(category)
                
                # Check severity escalators
                severity_matches = [s for s in data.get("severity_escalators", []) if s in message_lower]
                if severity_matches:
                    detected["severity"] = "high"
                elif len(keyword_matches) >= 2:
                    detected["severity"] = "moderate"
                else:
                    detected["severity"] = "low"
        
        # Build supportive response if mental health content detected
        if detected["has_mental_health_content"]:
            primary_category = detected["categories"][0] if detected["categories"] else "general"
            detected["supportive_response"] = self._build_supportive_response(
                primary_category, 
                detected["severity"]
            )
            detected["resources"] = self._get_resources(primary_category)
            detected["follow_up_questions"] = self._get_follow_up_questions(primary_category)
            
            if primary_category == "anxiety":
                detected["grounding_exercise"] = self.responses["anxiety"].get("grounding_exercise")
                detected["breathing_exercise"] = self.responses["anxiety"].get("breathing_exercise")
        
        return detected
    
    def _check_crisis(self, message: str) -> Dict:
        """Check for crisis/suicidal content"""
        crisis_data = self.indicators.get("crisis", {})
        
        for keyword in crisis_data.get("keywords", []):
            if keyword in message:
                # Check severity escalators
                for escalator in crisis_data.get("severity_escalators", []):
                    if escalator in message:
                        return {"is_crisis": True, "severity": "immediate"}
                return {"is_crisis": True, "severity": "high"}
        
        return {"is_crisis": False}
    
    def _build_crisis_response(self) -> str:
        """Build crisis intervention response"""
        crisis = self.responses["crisis"]
        return f"""{crisis['acknowledgment']}

{crisis['urgent_message']}

📞 **Crisis Helplines (24/7):**
{chr(10).join(crisis['resources'])}

{crisis['safety']}

You matter. Please reach out right now. 💙"""
    
    def _build_supportive_response(self, category: str, severity: str) -> str:
        """Build supportive response based on category and severity"""
        data = self.responses.get(category, self.responses["general"])
        
        response_parts = [data["acknowledgment"]]
        
        if "support" in data:
            response_parts.append(data["support"])
        
        if severity in ["moderate", "high"] and "self_care" in data:
            response_parts.append("\n**Things that might help:**")
            for tip in data["self_care"][:3]:
                response_parts.append(f"• {tip}")
        
        if category == "anxiety" and severity == "high":
            if "breathing_exercise" in data:
                response_parts.append(f"\n**Try this breathing exercise:** {data['breathing_exercise']}")
        
        return "\n\n".join(response_parts)
    
    def _get_resources(self, category: str) -> List[str]:
        """Get relevant mental health resources"""
        data = self.responses.get(category, self.responses["general"])
        return data.get("resources", self.responses["general"]["resources"])
    
    def _get_follow_up_questions(self, category: str) -> List[str]:
        """Get follow-up questions for the category"""
        data = self.indicators.get(category, {})
        return data.get("questions", [])


# Global instances
triage_service = TriageService()
mental_health_service = MentalHealthService()


def analyze_message(message: str, vitals: Dict = None) -> Dict[str, Any]:
    """
    Comprehensive analysis combining triage and mental health
    """
    # Mental health analysis
    mental_health = mental_health_service.analyze(message)
    
    # Triage analysis
    triage = triage_service.analyze(message, vitals)
    
    # If crisis detected, override triage to emergency
    if mental_health.get("is_crisis"):
        triage = {
            "level": "emergency",
            **TRIAGE_LEVELS["emergency"],
            "detected_condition": "Mental Health Crisis",
            "reason": "Immediate mental health support needed",
            "specific_action": "Please call a crisis helpline immediately"
        }
    
    return {
        "triage": triage,
        "mental_health": mental_health,
        "requires_immediate_attention": triage["level"] in ["emergency", "urgent"] or mental_health.get("is_crisis", False)
    }
