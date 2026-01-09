"""
Production-Grade AI Health Assistant
=====================================
Multi-model AI service with:
- Intelligent model routing (medllama2 for medical, llama3.1 for general, llava for images)
- Streaming responses for real-time UX
- Advanced medical reasoning with chain-of-thought
- Context-aware conversation memory
- Async processing with retries
- Redis caching for performance
- Structured JSON responses for frontend
"""

import ollama
import asyncio
import json
import logging
import hashlib
import re
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
from functools import wraps
import time

logger = logging.getLogger(__name__)

# Import medical database services for drug enrichment
try:
    from app.services.medical_databases import (
        drug_info_service, 
        atc_classification,
        is_otc as check_is_otc,
        get_drug_class
    )
    HAS_DRUG_DATABASE = True
except ImportError:
    HAS_DRUG_DATABASE = False
    logger.warning("Medical database services not available - drug enrichment disabled")


class ModelType(str, Enum):
    """Available AI models"""
    MEDICAL = "medllama2"           # Medical specialist
    GENERAL = "llama3.1:8b"         # General intelligence  
    FAST = "llama3.2:3b"            # Fast responses
    VISION = "llava:7b"             # Image analysis
    REASONING = "gemma2:9b"         # Complex reasoning


class UrgencyLevel(str, Enum):
    """Medical urgency classification"""
    EMERGENCY = "emergency"          # Call 108 NOW
    URGENT = "urgent"                # ER within hours
    SOON = "doctor_soon"             # See doctor 24-48h
    ROUTINE = "routine"              # Schedule appointment
    SELF_CARE = "self_care"          # Home treatment OK


@dataclass
class AIResponse:
    """Structured AI response"""
    text: str
    urgency: UrgencyLevel
    confidence: float
    model_used: str
    reasoning: Optional[str] = None
    symptoms_detected: List[str] = field(default_factory=list)
    conditions_suggested: List[str] = field(default_factory=list)
    medications: List[Dict] = field(default_factory=list)
    specialist_recommended: Optional[str] = None
    follow_up_questions: List[str] = field(default_factory=list)
    mental_health_detected: bool = False
    processing_time_ms: int = 0


class ConversationMemory:
    """Smart conversation memory with summarization"""
    
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.conversations: Dict[str, List[Dict]] = {}
        self.summaries: Dict[str, str] = {}
        self.symptom_history: Dict[str, List[str]] = {}  # Track symptoms per session
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent messages, summarize old ones
        if len(self.conversations[session_id]) > self.max_turns:
            self._summarize_old_messages(session_id)
    
    def add_symptoms(self, session_id: str, symptoms: List[str]):
        """Track symptoms mentioned across the conversation"""
        if session_id not in self.symptom_history:
            self.symptom_history[session_id] = []
        for symptom in symptoms:
            if symptom not in self.symptom_history[session_id]:
                self.symptom_history[session_id].append(symptom)
    
    def get_all_symptoms(self, session_id: str) -> List[str]:
        """Get all symptoms mentioned in this session"""
        return self.symptom_history.get(session_id, [])
    
    def get_conversation_text(self, session_id: str) -> str:
        """Get full conversation as text for analysis"""
        if session_id not in self.conversations:
            return ""
        
        texts = []
        for msg in self.conversations[session_id]:
            if msg["role"] == "user":
                texts.append(msg["content"])
        return " ".join(texts)
    
    # Alias for consistency
    def get_full_conversation_text(self, session_id: str) -> str:
        """Alias for get_conversation_text"""
        return self.get_conversation_text(session_id)
    
    def track_symptoms(self, session_id: str, message: str):
        """Extract and track symptoms from a message - clean keywords only"""
        # Common symptom keywords to track - no generic words like "pain" or "ache"
        symptom_keywords = [
            "headache", "migraine", "fever", "chills", "sweating",
            "nausea", "vomiting", "dizziness", "fatigue", "weakness", "cough", "cold",
            "chest pain", "back pain", "stomach pain", "joint pain", "muscle pain",
            "sore throat", "rash", "itching", "swelling", "bleeding", "numbness",
            "anxiety", "depression", "stress", "insomnia", "breathing difficulty",
            "body ache", "toothache", "ear pain", "abdominal pain", "acidity",
            "indigestion", "gas", "bloating", "constipation", "diarrhea"
        ]
        
        # Common typos/variations to normalize
        typo_map = {
            "stmach pain": "stomach pain",
            "stomache pain": "stomach pain", 
            "stomachpain": "stomach pain",
            "stomach ache": "stomach pain",
            "tummy pain": "stomach pain",
            "belly pain": "stomach pain",
            "head ache": "headache",
            "headach": "headache",
            # Loose motion variations -> diarrhea
            "loose motion": "diarrhea",
            "loose motions": "diarrhea",
            "loose stool": "diarrhea",
            "loose stools": "diarrhea",
            "watery stool": "diarrhea",
            "watery stools": "diarrhea",
            "running stomach": "diarrhea",
            "runny stomach": "diarrhea",
            "upset stomach": "diarrhea",
            "dysentery": "diarrhea",
            # Fever variations
            "high temperature": "fever",
            "temperature": "fever",
            "pyrexia": "fever",
            # Cold variations
            "common cold": "cold",
            "running nose": "cold",
            # Anxiety variations
            "anxious": "anxiety",
            "worried": "anxiety",
            "panic": "anxiety",
            "nervous": "anxiety",
        }
        
        message_lower = message.lower()
        
        # Normalize typos first
        for typo, correct in typo_map.items():
            if typo in message_lower:
                message_lower = message_lower.replace(typo, correct)
        
        found_symptoms = []
        
        # Check for symptoms - longer phrases first to avoid partial matches
        sorted_keywords = sorted(symptom_keywords, key=len, reverse=True)
        for keyword in sorted_keywords:
            if keyword in message_lower and keyword not in found_symptoms:
                # Don't add if it's a substring of already found symptom
                is_substring = any(keyword in other for other in found_symptoms)
                if not is_substring:
                    found_symptoms.append(keyword)
        
        if found_symptoms:
            self.add_symptoms(session_id, found_symptoms)
            logger.info(f"🔍 Tracked symptoms: {found_symptoms} -> Total: {self.get_all_symptoms(session_id)}")
    
    def get_context(self, session_id: str) -> List[Dict]:
        """Get conversation context for AI"""
        messages = []
        
        # Add summary if exists
        if session_id in self.summaries:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {self.summaries[session_id]}"
            })
        
        # Add symptom context if exists
        symptoms = self.get_all_symptoms(session_id)
        if symptoms:
            messages.append({
                "role": "system", 
                "content": f"Patient has mentioned these symptoms so far: {', '.join(symptoms)}. Consider all symptoms together for diagnosis."
            })
        
        # Add recent messages
        if session_id in self.conversations:
            for msg in self.conversations[session_id][-10:]:  # Last 10 messages
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        return messages
    
    def _summarize_old_messages(self, session_id: str):
        """Summarize old messages to save context"""
        old_messages = self.conversations[session_id][:-10]
        if old_messages:
            summary_text = " | ".join([
                f"{m['role']}: {m['content'][:100]}" for m in old_messages[-5:]
            ])
            self.summaries[session_id] = summary_text
            self.conversations[session_id] = self.conversations[session_id][-10:]
    
    def clear(self, session_id: str):
        self.conversations.pop(session_id, None)
        self.summaries.pop(session_id, None)
        self.symptom_history.pop(session_id, None)


class MedicalReasoningEngine:
    """Advanced medical reasoning with chain-of-thought"""
    
    # Symptom patterns for intelligent detection
    SYMPTOM_PATTERNS = {
        # Emergency patterns (call 108)
        "emergency": {
            "chest_pain_cardiac": {
                "primary": ["chest pain", "chest tightness", "pressure in chest"],
                "supporting": ["arm pain", "jaw pain", "sweating", "nausea", "shortness of breath"],
                "condition": "Possible Heart Attack",
                "action": "CALL 108 IMMEDIATELY"
            },
            "stroke": {
                "primary": ["face drooping", "arm weakness", "slurred speech", "sudden confusion"],
                "supporting": ["severe headache", "vision loss", "numbness"],
                "condition": "Possible Stroke - FAST",
                "action": "CALL 108 - Time is critical"
            },
            "breathing_emergency": {
                "primary": ["can't breathe", "severe breathing difficulty", "choking"],
                "supporting": ["blue lips", "gasping", "wheezing severely"],
                "condition": "Respiratory Emergency",
                "action": "CALL 108 - Keep upright"
            },
            "suicide_crisis": {
                "primary": ["want to die", "kill myself", "suicide", "end my life", "no reason to live"],
                "supporting": ["hopeless", "burden", "goodbye"],
                "condition": "Mental Health Crisis",
                "action": "CALL iCall 9152987821 NOW - You matter"
            }
        },
        
        # Urgent patterns (ER soon)
        "urgent": {
            "severe_pain": {
                "primary": ["severe pain", "worst pain", "unbearable pain"],
                "supporting": ["vomiting", "fever", "can't move"],
                "condition": "Severe Pain - Needs evaluation"
            },
            "head_injury": {
                "primary": ["hit head", "head injury", "concussion"],
                "supporting": ["confusion", "vomiting", "drowsy", "blurred vision"],
                "condition": "Possible Concussion"
            },
            "allergic_reaction": {
                "primary": ["throat swelling", "can't swallow", "hives spreading"],
                "supporting": ["difficulty breathing", "swollen face"],
                "condition": "Possible Anaphylaxis"
            }
        },
        
        # Common symptoms for detection - use complete terms only
        "symptoms": [
            "headache", "fever", "cough", "cold", "nausea", "vomiting",
            "diarrhea", "fatigue", "dizziness", "rash", "itching", "swelling",
            "bleeding", "weakness", "numbness", "tingling", "anxiety", "depression",
            "stress", "insomnia", "weight loss", "weight gain", "appetite loss",
            "breathing difficulty", "chest pain", "back pain", "joint pain",
            "stomach pain", "abdominal pain", "sore throat", "runny nose",
            "congestion", "sneezing", "body ache", "muscle pain", "cramps",
            "migraine", "toothache", "ear pain", "eye pain", "neck pain"
        ],
        
        # Mental health indicators
        "mental_health": [
            "anxious", "anxiety", "depressed", "depression", "stressed", "stress",
            "panic", "panic attack", "worried", "can't sleep", "insomnia",
            "sad", "hopeless", "lonely", "overwhelmed", "exhausted mentally",
            "crying", "mood swings", "angry", "irritable", "no motivation"
        ]
    }
    
    # Specialist mapping
    SPECIALISTS = {
        "heart": "Cardiologist",
        "chest pain": "Cardiologist",
        "cardiac": "Cardiologist",
        "skin": "Dermatologist",
        "rash": "Dermatologist",
        "bone": "Orthopedic",
        "joint": "Orthopedic",
        "fracture": "Orthopedic",
        "mental": "Psychiatrist",
        "anxiety": "Psychiatrist/Psychologist",
        "depression": "Psychiatrist/Psychologist",
        "diabetes": "Endocrinologist",
        "thyroid": "Endocrinologist",
        "hormone": "Endocrinologist",
        "cancer": "Oncologist",
        "tumor": "Oncologist",
        "eye": "Ophthalmologist",
        "vision": "Ophthalmologist",
        "ear": "ENT Specialist",
        "nose": "ENT Specialist",
        "throat": "ENT Specialist",
        "stomach": "Gastroenterologist",
        "digestive": "Gastroenterologist",
        "kidney": "Nephrologist",
        "urine": "Urologist",
        "brain": "Neurologist",
        "nerve": "Neurologist",
        "headache": "Neurologist",
        "migraine": "Neurologist",
        "pregnancy": "Gynecologist",
        "women": "Gynecologist",
        "child": "Pediatrician",
        "baby": "Pediatrician",
        "lung": "Pulmonologist",
        "breathing": "Pulmonologist",
        "allergy": "Allergist/Immunologist"
    }
    
    # OTC Medication suggestions for common symptoms (ONLY for minor issues)
    MEDICATIONS = {
        "headache": [
            {"name": "Paracetamol", "dosage": "500mg", "frequency": "Every 4-6 hours", "warning": "Max 4g/day"},
            {"name": "Ibuprofen", "dosage": "400mg", "frequency": "Every 6-8 hours", "warning": "Take with food"}
        ],
        "fever": [
            {"name": "Paracetamol", "dosage": "500-650mg", "frequency": "Every 4-6 hours", "warning": "Stay hydrated"},
            {"name": "Ibuprofen", "dosage": "400mg", "frequency": "Every 6-8 hours", "warning": "Not for children"}
        ],
        "cold": [
            {"name": "Cetirizine", "dosage": "10mg", "frequency": "Once daily", "warning": "May cause drowsiness"},
            {"name": "Paracetamol", "dosage": "500mg", "frequency": "As needed for aches", "warning": None}
        ],
        "cough": [
            {"name": "Dextromethorphan", "dosage": "10-20mg", "frequency": "Every 4 hours", "warning": "Dry cough only"},
            {"name": "Honey + Ginger", "dosage": "1 tsp", "frequency": "3-4 times daily", "warning": "Natural remedy"}
        ],
        "acidity": [
            {"name": "Antacid (Gelusil)", "dosage": "1-2 tablets", "frequency": "After meals", "warning": None},
            {"name": "Omeprazole", "dosage": "20mg", "frequency": "Before breakfast", "warning": "For recurring acidity"}
        ],
        "stomach pain": [
            {"name": "Dicyclomine", "dosage": "10mg", "frequency": "As needed", "warning": "For cramps only"},
            {"name": "ORS", "dosage": "1 packet in 1L water", "frequency": "Throughout the day", "warning": "Stay hydrated"}
        ],
        "diarrhea": [
            {"name": "ORS", "dosage": "1 packet in 1L water", "frequency": "Throughout the day", "warning": "Essential"},
            {"name": "Loperamide", "dosage": "2mg", "frequency": "After each loose stool", "warning": "Max 8mg/day"}
        ],
        "body ache": [
            {"name": "Ibuprofen", "dosage": "400mg", "frequency": "Every 8 hours", "warning": "Take with food"},
            {"name": "Diclofenac Gel", "dosage": "Apply locally", "frequency": "3-4 times daily", "warning": "External use only"}
        ],
        "sore throat": [
            {"name": "Strepsils", "dosage": "1 lozenge", "frequency": "Every 2-3 hours", "warning": "Max 8/day"},
            {"name": "Salt water gargle", "dosage": "1/2 tsp salt in warm water", "frequency": "3-4 times daily", "warning": "Natural remedy"}
        ],
        "allergy": [
            {"name": "Cetirizine", "dosage": "10mg", "frequency": "Once daily", "warning": "May cause drowsiness"},
            {"name": "Loratadine", "dosage": "10mg", "frequency": "Once daily", "warning": "Non-drowsy option"}
        ],
        "nausea": [
            {"name": "Domperidone", "dosage": "10mg", "frequency": "Before meals", "warning": "For motion sickness too"},
            {"name": "Ginger tea", "dosage": "1 cup", "frequency": "As needed", "warning": "Natural remedy"}
        ],
        "anxiety": [
            {"name": "Deep breathing", "dosage": "4-7-8 technique", "frequency": "When anxious", "warning": "Non-medication"},
            {"name": "Chamomile tea", "dosage": "1 cup", "frequency": "Before bed", "warning": "Natural relaxant"}
        ],
        "insomnia": [
            {"name": "Melatonin", "dosage": "3mg", "frequency": "30 min before sleep", "warning": "Short-term use only"},
            {"name": "Sleep hygiene", "dosage": "Routine", "frequency": "Daily", "warning": "Non-medication approach"}
        ]
    }
    
    def get_medications(self, symptoms: List[str], urgency: UrgencyLevel) -> List[Dict]:
        """Get medication suggestions - prioritize safe OTC options"""
        # DON'T suggest medications for serious conditions
        if urgency in [UrgencyLevel.EMERGENCY, UrgencyLevel.URGENT]:
            return []
        
        medications = []
        remedies = []
        seen_meds = set()
        
        # Categories to skip for self-care (prescription only)
        prescription_categories = ['Triptan', 'Beta Blocker', 'Anticonvulsant', 'Opioid', 'Prescription']
        
        # Map symptoms to database condition keys AND preferred subcategories
        SYMPTOM_TO_CONDITION = {
            "stomach pain": {"conditions": ["gastric"], "preferred_subcats": ["antispasmodics", "antacids"]},
            "stomach ache": {"conditions": ["gastric"], "preferred_subcats": ["antispasmodics", "antacids"]},
            "abdominal pain": {"conditions": ["gastric"], "preferred_subcats": ["antispasmodics", "antacids"]},
            "abdomen pain": {"conditions": ["gastric"], "preferred_subcats": ["antispasmodics", "antacids"]},
            "belly pain": {"conditions": ["gastric"], "preferred_subcats": ["antispasmodics", "antacids"]},
            "cramps": {"conditions": ["gastric"], "preferred_subcats": ["antispasmodics"]},
            "nausea": {"conditions": ["gastric"], "preferred_subcats": ["antiemetics", "antacids"]},
            "vomiting": {"conditions": ["gastric"], "preferred_subcats": ["antiemetics", "antacids"]},
            "diarrhea": {"conditions": ["gastric"], "preferred_subcats": ["antidiarrheal"]},
            "constipation": {"conditions": ["gastric"], "preferred_subcats": ["laxatives"]},
            "acidity": {"conditions": ["gastric"], "preferred_subcats": ["antacids", "h2_blockers", "ppi"]},
            "heartburn": {"conditions": ["gastric"], "preferred_subcats": ["antacids", "ppi"]},
            "indigestion": {"conditions": ["gastric"], "preferred_subcats": ["antacids"]},
            "cold": {"conditions": ["respiratory"], "preferred_subcats": ["decongestants", "antihistamines"]},
            "cough": {"conditions": ["respiratory"], "preferred_subcats": ["antitussives", "expectorants"]},
            "sore throat": {"conditions": ["respiratory"], "preferred_subcats": ["lozenges", "antiseptics"]},
            "runny nose": {"conditions": ["respiratory"], "preferred_subcats": ["antihistamines", "decongestants"]},
            "congestion": {"conditions": ["respiratory"], "preferred_subcats": ["decongestants"]},
            "headache": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate"]},
            "body ache": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "back pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "joint pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "muscle pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "fever": {"conditions": ["fever"], "preferred_subcats": ["adults"]},
            "allergy": {"conditions": ["allergy"], "preferred_subcats": ["non_sedating", "antihistamines"]},
            "rash": {"conditions": ["allergy", "skin"], "preferred_subcats": ["topical", "antihistamines"]},
            "itching": {"conditions": ["allergy", "skin"], "preferred_subcats": ["topical", "antihistamines"]},
            "anxiety": {"conditions": ["mental_health"], "preferred_subcats": ["otc_stress_relief", "anxiolytics"]},
            "stress": {"conditions": ["mental_health"], "preferred_subcats": ["otc_stress_relief"]},
            "insomnia": {"conditions": ["mental_health"], "preferred_subcats": ["sleep", "otc_stress_relief"]},
            "infection": {"conditions": ["antibiotics"], "preferred_subcats": []},
        }
        
        # Try to import comprehensive database
        try:
            from app.data.medical_database import DRUG_DATABASE
            from app.data.remedies_database import get_remedies_for_condition
            has_database = True
        except ImportError:
            has_database = False
        
        # Track what we've added to avoid duplicates from same category
        processed_symptom_categories = set()
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # Get mapped conditions and preferred subcategories for this symptom
            symptom_config = SYMPTOM_TO_CONDITION.get(symptom_lower, {"conditions": [], "preferred_subcats": []})
            mapped_conditions = symptom_config.get("conditions", [])
            preferred_subcats = symptom_config.get("preferred_subcats", [])
            
            # Use comprehensive database if available
            if has_database:
                # First try mapped conditions
                conditions_to_check = mapped_conditions.copy()
                
                # Then add direct matches
                for condition in DRUG_DATABASE.keys():
                    if condition in symptom_lower or symptom_lower in condition:
                        if condition not in conditions_to_check:
                            conditions_to_check.append(condition)
                
                for condition in conditions_to_check:
                    if condition not in DRUG_DATABASE:
                        continue
                    
                    # Create a unique key for this symptom+condition combo
                    symptom_condition_key = f"{symptom_lower}:{condition}"
                    if symptom_condition_key in processed_symptom_categories:
                        continue
                    processed_symptom_categories.add(symptom_condition_key)
                    
                    subcategories = DRUG_DATABASE[condition]
                    if isinstance(subcategories, dict):
                        # Safe subcategories for OTC suggestions
                        all_safe_subcats = ['mild_to_moderate', 'adults', 'non_sedating', 'otc', 'topical', 
                                           'antacids', 'antispasmodics', 'antiemetics', 'antidiarrheal',
                                           'decongestants', 'antihistamines', 'antitussives', 'expectorants',
                                           'laxatives', 'h2_blockers', 'ppi', 'lozenges', 'antiseptics',
                                           'otc_stress_relief', 'sleep']
                        
                        # First, try preferred subcategories for this symptom
                        subcats_to_try = preferred_subcats + [s for s in all_safe_subcats if s not in preferred_subcats]
                        
                        meds_for_this_symptom = 0
                        for subcat in subcats_to_try:
                            if subcat not in subcategories:
                                continue
                            drugs = subcategories[subcat]
                            if isinstance(drugs, list):
                                for drug in drugs[:2]:
                                    cat = drug.get('category', '')
                                    if cat not in prescription_categories and drug["name"] not in seen_meds:
                                        medications.append(drug)
                                        seen_meds.add(drug["name"])
                                        meds_for_this_symptom += 1
                                        if meds_for_this_symptom >= 2:  # Max 2 meds per symptom
                                            break
                            if meds_for_this_symptom >= 2:
                                break
                                            
                    elif isinstance(subcategories, list):
                        for drug in subcategories[:2]:
                            cat = drug.get('category', '')
                            if cat not in prescription_categories and drug["name"] not in seen_meds:
                                medications.append(drug)
                                seen_meds.add(drug["name"])
                
                # Add natural remedies for this symptom
                try:
                    condition_remedies = get_remedies_for_condition(symptom_lower, max_remedies=2)
                    for remedy in condition_remedies:
                        if remedy["name"] not in seen_meds:
                            remedies.append(remedy)
                            seen_meds.add(remedy["name"])
                except:
                    pass
            
            # Fallback to basic MEDICATIONS dict
            if len(medications) < 3:
                for key, meds in self.MEDICATIONS.items():
                    if key in symptom_lower:
                        for med in meds:
                            if med["name"] not in seen_meds:
                                medications.append(med)
                                seen_meds.add(med["name"])
        
        # Smart selection: ensure each symptom is represented
        # Allow 2 meds per symptom, up to 10 pharma + 2 natural for multi-symptom cases
        max_pharma = min(10, 2 * len(symptoms) + 2)  # Scale with symptom count
        final_medications = medications[:max_pharma] + remedies[:2]
        
        # Enrich with official database information (WHO ATC classification)
        if HAS_DRUG_DATABASE:
            final_medications = self._enrich_medications(final_medications)
        
        return final_medications
    
    def _enrich_medications(self, medications: List[Dict]) -> List[Dict]:
        """Enrich medications with official WHO ATC classification data"""
        enriched = []
        for med in medications:
            drug_name = med.get("name", "")
            
            # Get ATC classification (local, fast lookup)
            atc_info = atc_classification.classify_drug(drug_name)
            
            if atc_info:
                # Add verified official info
                med["verified"] = True
                med["atc_code"] = atc_info.get("atc_code")
                med["drug_class"] = atc_info.get("classification")
                med["therapeutic_group"] = atc_info.get("therapeutic_group")
                med["is_otc"] = atc_info.get("otc", True)
                med["requires_prescription"] = not atc_info.get("otc", True)
                med["source"] = "WHO ATC/DDD"
            else:
                # Not in our verified database
                med["verified"] = False
                med["is_otc"] = True  # Assume OTC for our suggestions
                med["requires_prescription"] = False
            
            # Always add disclaimer
            med["disclaimer"] = "Consult a healthcare provider before use."
            
            enriched.append(med)
        
        return enriched
    
    def analyze(self, message: str, vitals: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze message for medical reasoning"""
        message_lower = message.lower()
        
        result = {
            "urgency": UrgencyLevel.SELF_CARE,
            "confidence": 0.5,
            "symptoms_detected": [],
            "conditions_suggested": [],
            "specialist": None,
            "mental_health": False,
            "reasoning": [],
            "emergency_response": None
        }
        
        # Check for emergencies first
        for emergency_type, patterns in self.SYMPTOM_PATTERNS["emergency"].items():
            primary_match = any(p in message_lower for p in patterns["primary"])
            supporting_match = sum(1 for s in patterns["supporting"] if s in message_lower)
            
            if primary_match:
                result["urgency"] = UrgencyLevel.EMERGENCY
                result["confidence"] = 0.9 + (supporting_match * 0.02)
                result["conditions_suggested"].append(patterns["condition"])
                result["emergency_response"] = patterns["action"]
                result["reasoning"].append(f"Emergency detected: {patterns['condition']}")
                return result
        
        # Check for urgent conditions
        for urgent_type, patterns in self.SYMPTOM_PATTERNS["urgent"].items():
            primary_match = any(p in message_lower for p in patterns["primary"])
            supporting_match = sum(1 for s in patterns["supporting"] if s in message_lower)
            
            if primary_match and supporting_match >= 1:
                result["urgency"] = UrgencyLevel.URGENT
                result["confidence"] = 0.75 + (supporting_match * 0.05)
                result["conditions_suggested"].append(patterns["condition"])
                result["reasoning"].append(f"Urgent condition: {patterns['condition']}")
        
        # Detect symptoms - use word boundary to avoid partial matches
        import re
        for symptom in self.SYMPTOM_PATTERNS["symptoms"]:
            # Use word boundary to match whole words/phrases
            pattern = r'\b' + re.escape(symptom) + r'\b'
            if re.search(pattern, message_lower):
                result["symptoms_detected"].append(symptom)
        
        # Remove duplicates where one symptom contains another (e.g., "headache" contains "ache")
        unique_symptoms = []
        for s in result["symptoms_detected"]:
            is_substring = any(s != other and s in other for other in result["symptoms_detected"])
            if not is_substring:
                unique_symptoms.append(s)
        result["symptoms_detected"] = unique_symptoms
        
        # Check mental health
        for mh_indicator in self.SYMPTOM_PATTERNS["mental_health"]:
            if mh_indicator in message_lower:
                result["mental_health"] = True
                result["reasoning"].append(f"Mental health indicator: {mh_indicator}")
                break
        
        # Find specialist
        for keyword, specialist in self.SPECIALISTS.items():
            if keyword in message_lower:
                result["specialist"] = specialist
                break
        
        # Adjust urgency based on symptoms count and vitals
        if len(result["symptoms_detected"]) >= 3:
            if result["urgency"] == UrgencyLevel.SELF_CARE:
                result["urgency"] = UrgencyLevel.SOON
                result["reasoning"].append("Multiple symptoms detected")
        
        # Check vitals if provided
        if vitals:
            if vitals.get("heart_rate", 0) > 120 or vitals.get("heart_rate", 100) < 50:
                result["urgency"] = UrgencyLevel.URGENT
                result["reasoning"].append(f"Abnormal heart rate: {vitals.get('heart_rate')}")
            if vitals.get("temperature", 98.6) > 103:
                result["urgency"] = UrgencyLevel.URGENT
                result["reasoning"].append(f"High fever: {vitals.get('temperature')}°F")
            if vitals.get("spo2", 100) < 92:
                result["urgency"] = UrgencyLevel.EMERGENCY
                result["reasoning"].append(f"Low oxygen: {vitals.get('spo2')}%")
        
        return result
    
    def analyze_with_history(self, current_message: str, all_symptoms: List[str], conversation_text: str, vitals: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze message WITH conversation history for symptom continuity.
        This detects emergencies even when symptoms are mentioned across multiple messages.
        """
        # Combine current message with conversation history for full analysis
        full_text = (conversation_text + " " + current_message).lower()
        
        result = {
            "urgency": UrgencyLevel.SELF_CARE,
            "confidence": 0.5,
            "symptoms_detected": [],
            "conditions_suggested": [],
            "specialist": None,
            "mental_health": False,
            "reasoning": [],
            "emergency_response": None
        }
        
        # CRITICAL: Check for cardiac emergency pattern across ALL messages
        # Heart attack symptoms: chest pain, arm pain, sweating, shortness of breath, jaw pain
        cardiac_symptoms = {
            "chest": ["chest pain", "chest tightness", "pressure in chest", "chest"],
            "arm": ["arm pain", "arm hurting", "left arm", "arm hurt"],
            "sweating": ["sweating", "sweat", "sweaty", "perspiring"],
            "breath": ["shortness of breath", "can't breathe", "breathing difficulty", "breathless"],
            "jaw": ["jaw pain", "jaw hurting"],
            "nausea": ["nausea", "nauseous", "vomiting"]
        }
        
        cardiac_score = 0
        cardiac_matches = []
        for symptom_type, patterns in cardiac_symptoms.items():
            if any(p in full_text for p in patterns):
                cardiac_score += 1
                cardiac_matches.append(symptom_type)
        
        # If 2+ cardiac symptoms detected across conversation = EMERGENCY
        if cardiac_score >= 2:
            result["urgency"] = UrgencyLevel.EMERGENCY
            result["confidence"] = 0.85 + (cardiac_score * 0.03)
            result["conditions_suggested"].append("Possible Heart Attack")
            result["emergency_response"] = "🚨 CALL 108 IMMEDIATELY - Multiple cardiac symptoms detected!"
            result["reasoning"].append(f"CARDIAC EMERGENCY: Detected {cardiac_score} heart attack indicators: {', '.join(cardiac_matches)}")
            return result
        
        # Check for stroke pattern across messages
        stroke_symptoms = ["face droop", "arm weakness", "slurred speech", "confusion", "sudden headache", "vision", "numbness", "one side"]
        stroke_score = sum(1 for s in stroke_symptoms if s in full_text)
        if stroke_score >= 2:
            result["urgency"] = UrgencyLevel.EMERGENCY
            result["confidence"] = 0.85 + (stroke_score * 0.03)
            result["conditions_suggested"].append("Possible Stroke - FAST")
            result["emergency_response"] = "🚨 CALL 108 IMMEDIATELY - Possible stroke detected!"
            result["reasoning"].append(f"STROKE EMERGENCY: Detected {stroke_score} stroke indicators")
            return result
        
        # Check for suicide/mental health crisis
        crisis_keywords = ["suicide", "kill myself", "want to die", "end my life", "no reason to live", "better off dead"]
        if any(k in full_text for k in crisis_keywords):
            result["urgency"] = UrgencyLevel.EMERGENCY
            result["confidence"] = 0.95
            result["conditions_suggested"].append("Mental Health Crisis")
            result["emergency_response"] = "💜 Please call iCall: 9152987821 NOW. You matter. Help is available."
            result["reasoning"].append("MENTAL HEALTH CRISIS detected")
            return result
        
        # Now do standard analysis on current message
        standard_result = self.analyze(current_message, vitals)
        
        # Merge with accumulated symptoms - keep only clean keywords
        clean_symptoms = []
        for symptom in (all_symptoms + standard_result["symptoms_detected"]):
            # Only keep short, clean symptom names
            if len(symptom.split()) <= 2 and symptom not in clean_symptoms:
                clean_symptoms.append(symptom)
        
        standard_result["symptoms_detected"] = clean_symptoms[:6]  # Max 6 symptoms
        
        # Upgrade urgency if many symptoms accumulated
        if len(clean_symptoms) >= 4 and standard_result["urgency"] == UrgencyLevel.SELF_CARE:
            standard_result["urgency"] = UrgencyLevel.SOON
            standard_result["reasoning"].append(f"Multiple symptoms detected")
        
        return standard_result


class PowerfulAIService:
    """
    Production-grade AI Health Assistant
    Uses multiple models intelligently for best results
    """
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.reasoning_engine = MedicalReasoningEngine()
        self.redis_client = None
        self._init_redis()
        
        # Model configuration
        self.models = {
            "medical": ModelType.MEDICAL.value,
            "general": ModelType.GENERAL.value,
            "fast": ModelType.FAST.value,
            "vision": ModelType.VISION.value,
            "reasoning": ModelType.REASONING.value
        }
        
        # System prompts for different contexts
        self.system_prompts = {
            "medical": self._get_medical_prompt(),
            "mental_health": self._get_mental_health_prompt(),
            "emergency": self._get_emergency_prompt()
        }
    
    def _init_redis(self):
        """Initialize Redis for caching"""
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {e}")
            self.redis_client = None
    
    def _get_medical_prompt(self) -> str:
        return """You are MedAssist, a friendly AI health assistant.

RESPONSE STYLE:
- Be concise and clear (2-4 short paragraphs max)
- Use simple, everyday language
- Be warm and reassuring
- NO markdown headers, NO bullet points, NO numbered lists
- Write naturally like a caring doctor would speak

RESPONSE FORMAT (follow this exactly):
Start with acknowledging their concern in 1 sentence.
Then explain what might be causing it in 1-2 sentences.
Give practical advice in 1-2 sentences.
End with when to see a doctor if needed.

EXAMPLE GOOD RESPONSE:
"I understand you're dealing with a headache and that can be really uncomfortable. This could be from tension, dehydration, or lack of sleep. Try resting in a dark room, staying hydrated, and taking paracetamol if needed. If the headache persists for more than 2 days or gets severe, please see a doctor."

CRITICAL:
- Keep responses SHORT (under 100 words ideally)
- Do NOT use emojis in the text
- Do NOT list medications (the app shows them separately)
- Do NOT use "Understanding:", "Assessment:" headers
- Just speak naturally"""

    def _get_mental_health_prompt(self) -> str:
        return """You are MedAssist, a compassionate mental health support companion.

RESPONSE STYLE:
- Be warm, gentle, and validating
- Keep responses short (3-4 sentences)
- NO bullet points or headers
- Write like a caring friend

RESPOND LIKE THIS:
"I hear you, and what you're feeling is completely valid. [Acknowledge their specific feeling]. It can really help to [one simple suggestion]. If these feelings persist, talking to a counselor can make a real difference - iCall (9152987821) offers free support."

HELPLINES (mention naturally, not as a list):
- iCall: 9152987821 (free counseling)
- Vandrevala: 1860-2662-345 (24/7)

For crisis/suicidal thoughts:
- Lead with empathy
- Provide helpline immediately
- Keep them talking"""

    def _get_emergency_prompt(self) -> str:
        return """EMERGENCY MODE - Be direct and brief.

Give 2-3 sentences ONLY:
1. What to do NOW (call 108, position patient, etc.)
2. What NOT to do
3. Stay calm reassurance

Example: "Call 108 immediately. While waiting, keep the person lying down and loosen tight clothing. Stay with them and keep them calm - help is on the way."

NO long explanations. Action first."""

    async def chat(
        self,
        session_id: str,
        message: str,
        language: str = "en",
        vitals: Optional[Dict] = None,
        image_base64: Optional[str] = None
    ) -> AIResponse:
        """
        Main chat interface with intelligent routing
        """
        start_time = time.time()
        
        # Step 1: Get conversation history for context-aware analysis
        conversation_history = self.memory.get_full_conversation_text(session_id)
        
        # Step 2: Track symptoms from current message
        self.memory.track_symptoms(session_id, message)
        
        # Step 3: Get all accumulated symptoms
        all_symptoms = self.memory.get_all_symptoms(session_id)
        
        # Step 4: Analyze with full conversation history (critical for multi-turn symptom detection)
        analysis = self.reasoning_engine.analyze_with_history(message, all_symptoms, conversation_history, vitals)
        
        # Step 5: Check cache for similar queries (only for non-emergency, single-turn)
        cache_key = self._get_cache_key(message, language)
        if not conversation_history:  # Only use cache for first message
            cached = await self._get_cached_response(cache_key)
            if cached and analysis["urgency"] == UrgencyLevel.SELF_CARE:
                cached["processing_time_ms"] = int((time.time() - start_time) * 1000)
                return AIResponse(**cached)
        
        # Step 5: Select appropriate model and prompt
        model, system_prompt = self._select_model_and_prompt(analysis, image_base64)
        
        # Step 6: Build conversation context
        context = self.memory.get_context(session_id)
        
        # Step 7: Generate response
        try:
            if analysis["urgency"] == UrgencyLevel.EMERGENCY and analysis["emergency_response"]:
                # For emergencies, use pre-defined response + AI elaboration
                ai_text = await self._generate_emergency_response(
                    message, analysis, model, system_prompt, context
                )
            elif image_base64:
                # Use vision model for images
                ai_text = await self._analyze_image(message, image_base64)
            else:
                # Standard AI generation
                ai_text = await self._generate_response(
                    message, model, system_prompt, context, language
                )
            
            # Clean up AI response text
            ai_text = self._clean_response_text(ai_text)
            
            # Step 8: Save to memory
            self.memory.add_message(session_id, "user", message)
            self.memory.add_message(session_id, "assistant", ai_text)
            
            # Step 9: Build response
            response = AIResponse(
                text=ai_text,
                urgency=analysis["urgency"],
                confidence=analysis["confidence"],
                model_used=model,
                reasoning="; ".join(analysis["reasoning"]) if analysis["reasoning"] else None,
                symptoms_detected=analysis["symptoms_detected"],
                conditions_suggested=analysis["conditions_suggested"],
                specialist_recommended=analysis["specialist"],
                mental_health_detected=analysis["mental_health"],
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
            # Step 10: Cache if appropriate (only for first message in session)
            if analysis["urgency"] in [UrgencyLevel.SELF_CARE, UrgencyLevel.ROUTINE] and not conversation_history:
                await self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return AIResponse(
                text="I apologize, I'm having trouble processing your request. Please try again or consult a healthcare provider directly.",
                urgency=analysis["urgency"],
                confidence=0.0,
                model_used=model,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _clean_response_text(self, text: str) -> str:
        """Clean up AI-generated response text"""
        import re
        
        # Remove placeholders like [Name], [Patient's response], etc.
        text = re.sub(r'\[(?:Name|Patient\'s response|Your name|User)\]', '', text)
        
        # Remove extra quotes at start/end
        text = text.strip('"\'')
        
        # Remove markdown headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
        
        # Remove numbered list format at line start
        text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # Remove bullet points
        text = re.sub(r'^[-•]\s*', '', text, flags=re.MULTILINE)
        
        # Clean up multiple spaces/newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove any leftover weird artifacts
        text = text.replace('---', '').strip()
        
        return text.strip()

    def _select_model_and_prompt(
        self, 
        analysis: Dict, 
        has_image: bool
    ) -> Tuple[str, str]:
        """Intelligently select the best model for the task"""
        
        if has_image:
            return self.models["vision"], self.system_prompts["medical"]
        
        if analysis["urgency"] == UrgencyLevel.EMERGENCY:
            return self.models["medical"], self.system_prompts["emergency"]
        
        if analysis["mental_health"]:
            return self.models["general"], self.system_prompts["mental_health"]
        
        # Default to medical model for health queries
        return self.models["medical"], self.system_prompts["medical"]
    
    async def _generate_response(
        self,
        message: str,
        model: str,
        system_prompt: str,
        context: List[Dict],
        language: str
    ) -> str:
        """Generate AI response using Ollama, then translate if needed"""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        # Always generate in English for best quality
        # Then translate to target language
        
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512  # Keep responses shorter
                }
            )
            english_response = response["message"]["content"]
            
            # Translate to target language if not English
            if language != "en":
                try:
                    from app.services.nlp.translator import TranslationService
                    translator = TranslationService()
                    translated = translator.translate(
                        text=english_response,
                        target_language=language,
                        source_language="en",
                        preserve_medical=True
                    )
                    logger.info(f"Translated response to {language}")
                    return translated
                except Exception as trans_error:
                    logger.error(f"Translation failed: {trans_error}, returning English")
                    return english_response
            
            return english_response
            
        except Exception as e:
            logger.error(f"Ollama error with {model}: {e}")
            # Fallback to faster model
            if model != self.models["fast"]:
                return await self._generate_response(
                    message, self.models["fast"], system_prompt, context, language
                )
            raise
    
    async def _generate_emergency_response(
        self,
        message: str,
        analysis: Dict,
        model: str,
        system_prompt: str,
        context: List[Dict]
    ) -> str:
        """Generate emergency response with pre-defined action + AI"""
        
        emergency_header = f"""🚨 **{analysis['conditions_suggested'][0] if analysis['conditions_suggested'] else 'EMERGENCY'}**

**{analysis['emergency_response']}**

---

"""
        # Get AI elaboration
        elaboration_prompt = f"""The user said: "{message}"

This is an emergency situation: {analysis['conditions_suggested']}.
Provide:
1. Immediate first aid steps
2. What to tell emergency services
3. What to avoid doing
4. Reassurance

Be direct and clear. This is urgent."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({"role": "user", "content": elaboration_prompt})
        
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                options={"temperature": 0.5, "num_predict": 512}
            )
            return emergency_header + response["message"]["content"]
        except:
            return emergency_header + "Please stay calm and follow the emergency instructions above."
    
    async def _analyze_image(self, message: str, image_base64: str) -> str:
        """Analyze medical image using LLaVA"""
        
        prompt = f"""You are a medical AI assistant analyzing an image.
        
User's question: {message}

Analyze this image and provide:
1. What you observe in the image
2. Possible medical relevance
3. Whether professional consultation is needed
4. Any visible concerns

IMPORTANT: You cannot diagnose. Only describe observations and recommend professional evaluation."""

        try:
            response = ollama.chat(
                model=self.models["vision"],
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }],
                options={"temperature": 0.5}
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Vision model error: {e}")
            return "I'm unable to analyze the image at the moment. Please describe what you see, or consult a healthcare provider directly."
    
    async def stream_chat(
        self,
        session_id: str,
        message: str,
        language: str = "en"
    ) -> AsyncGenerator[str, None]:
        """Stream response for real-time UI"""
        
        analysis = self.reasoning_engine.analyze(message)
        model, system_prompt = self._select_model_and_prompt(analysis, False)
        context = self.memory.get_context(session_id)
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        full_response = ""
        
        try:
            stream = ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options={"temperature": 0.7}
            )
            
            for chunk in stream:
                if chunk and "message" in chunk and "content" in chunk["message"]:
                    text = chunk["message"]["content"]
                    full_response += text
                    yield text
            
            # Save to memory after streaming completes
            self.memory.add_message(session_id, "user", message)
            self.memory.add_message(session_id, "assistant", full_response)
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield "I apologize, there was an error generating the response."
    
    def _get_cache_key(self, message: str, language: str) -> str:
        """Generate cache key for response"""
        # Normalize message
        normalized = message.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        return f"ai_response:{language}:{hashlib.md5(normalized.encode()).hexdigest()}"
    
    async def _get_cached_response(self, key: str) -> Optional[Dict]:
        """Get cached response from Redis"""
        if not self.redis_client:
            return None
        try:
            cached = await self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None
    
    async def _cache_response(self, key: str, response: AIResponse):
        """Cache response in Redis"""
        if not self.redis_client:
            return
        try:
            data = {
                "text": response.text,
                "urgency": response.urgency.value,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "symptoms_detected": response.symptoms_detected,
                "conditions_suggested": response.conditions_suggested,
                "specialist_recommended": response.specialist_recommended
            }
            await self.redis_client.setex(key, 3600, json.dumps(data))  # 1 hour cache
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history"""
        self.memory.clear(session_id)


# Global instance
powerful_ai = PowerfulAIService()


# Wrapper function for easy integration
async def get_ai_response(
    message: str,
    session_id: str = "default",
    language: str = "en",
    vitals: Optional[Dict] = None,
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for AI responses
    Returns dict compatible with existing frontend
    """
    response = await powerful_ai.chat(
        session_id=session_id,
        message=message,
        language=language,
        vitals=vitals,
        image_base64=image_base64
    )
    
    # Get urgency value (handle both enum and string)
    urgency_value = response.urgency.value if isinstance(response.urgency, UrgencyLevel) else response.urgency
    
    # Get ALL accumulated symptoms from session (not just current message)
    all_session_symptoms = powerful_ai.memory.get_all_symptoms(session_id)
    
    # Merge with currently detected symptoms
    combined_symptoms = list(set(all_session_symptoms + (response.symptoms_detected or [])))
    
    logger.info(f"📋 Session symptoms for medication lookup: {combined_symptoms}")
    
    # Get medication suggestions based on ALL accumulated symptoms
    urgency_enum = response.urgency if isinstance(response.urgency, UrgencyLevel) else UrgencyLevel(response.urgency)
    medications = powerful_ai.reasoning_engine.get_medications(
        combined_symptoms,  # Use all accumulated symptoms
        urgency_enum
    )
    
    logger.info(f"💊 Medications for {combined_symptoms}: {[m.get('name') for m in medications]}")
    
    # Convert to dict for frontend compatibility
    return {
        "response": response.text,
        "urgency_level": urgency_value,
        "confidence": response.confidence,
        "model_used": response.model_used,
        "reasoning": response.reasoning,
        "symptoms_detected": combined_symptoms,  # Return all accumulated symptoms
        "conditions_suggested": response.conditions_suggested,
        "specialist_recommended": response.specialist_recommended,
        "medications": medications,
        "mental_health": {
            "detected": response.mental_health_detected
        },
        "processing_time_ms": response.processing_time_ms,
        "triage": {
            "level": urgency_value,
            "color": {
                "emergency": "#ef4444",
                "urgent": "#f97316",
                "doctor_soon": "#fbbf24",
                "routine": "#60a5fa",
                "self_care": "#4ade80"
            }.get(urgency_value, "#4ade80"),
            "is_emergency": urgency_value == "emergency",
            "reasoning": response.reasoning,
            "action_required": ""
        }
    }
