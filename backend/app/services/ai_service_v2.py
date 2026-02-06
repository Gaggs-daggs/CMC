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

# Import symptom normalizer for comprehensive symptom detection
try:
    from app.services.symptom_normalizer import symptom_normalizer, normalize_symptoms
    HAS_SYMPTOM_NORMALIZER = True
    logger.info("✅ Symptom normalizer loaded with 1000+ variations")
except ImportError:
    HAS_SYMPTOM_NORMALIZER = False
    logger.warning("Symptom normalizer not available - using basic matching")

# Import advanced diagnosis engine
try:
    from app.services.diagnosis_engine import (
        generate_differential_diagnosis as advanced_diagnosis,
        detect_red_flags,
        get_condition_info
    )
    HAS_ADVANCED_DIAGNOSIS = True
    logger.info("✅ Advanced diagnosis engine loaded with 60+ conditions")
except ImportError:
    HAS_ADVANCED_DIAGNOSIS = False
    logger.warning("Advanced diagnosis engine not available")

# Import AI-powered medication service
try:
    from app.services.ai_medication_service import get_smart_medications
    HAS_AI_MEDICATION = True
    logger.info("✅ AI Medication service loaded (medllama2-powered)")
except ImportError:
    HAS_AI_MEDICATION = False
    logger.warning("AI Medication service not available")

# Import Drug RAG service for PDF-based drug lookup
try:
    from app.services.drug_rag_service import get_drug_rag_service
    drug_rag = get_drug_rag_service()
    HAS_DRUG_RAG = True
    logger.info(f"✅ Drug RAG service loaded with {len(drug_rag.drugs_data)} drugs from PDF")
except Exception as e:
    HAS_DRUG_RAG = False
    drug_rag = None
    logger.warning(f"Drug RAG service not available: {e}")



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
class DiagnosisCandidate:
    """A possible diagnosis with confidence"""
    condition: str
    confidence: float  # 0.0 to 1.0
    description: str = ""
    urgency: str = "self_care"
    specialist: Optional[str] = None


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
    diagnoses: List[Dict] = field(default_factory=list)  # Multiple diagnoses with confidence
    medications: List[Dict] = field(default_factory=list)
    specialist_recommended: Optional[str] = None
    follow_up_questions: List[str] = field(default_factory=list)
    needs_more_info: bool = False  # True if we need to ask more questions
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
        """Extract and track symptoms from a message using comprehensive normalizer"""
        
        # Use comprehensive symptom normalizer if available
        if HAS_SYMPTOM_NORMALIZER:
            found_symptoms = normalize_symptoms(message)
            if found_symptoms:
                self.add_symptoms(session_id, found_symptoms)
                logger.info(f"🔍 Normalized symptoms: {found_symptoms} -> Total: {self.get_all_symptoms(session_id)}")
            return
        
        # Fallback to basic matching if normalizer not available
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
            # Migraine variations
            "migrain": "migraine",
            "migranes": "migraine",
            "migrane": "migraine",
            "migraines": "migraine",
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
            "feverish": "fever",
            # Cold variations
            "common cold": "cold",
            "running nose": "cold",
            "runny nose": "cold",
            # Anxiety variations
            "anxious": "anxiety",
            "worried": "anxiety",
            "panic": "anxiety",
            "nervous": "anxiety",
            # Cough variations
            "coughing": "cough",
            "khansi": "cough",
            # Body ache variations
            "body aches": "body ache",
            "bodyache": "body ache",
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
        "migraine": [
            {"name": "Paracetamol", "dosage": "1000mg", "frequency": "At onset", "warning": "Take early for best effect"},
            {"name": "Ibuprofen", "dosage": "400-600mg", "frequency": "At onset", "warning": "Take with food, works best early"},
            {"name": "Aspirin", "dosage": "900-1000mg", "frequency": "At onset", "warning": "Not for children, take with food"},
            {"name": "Excedrin Migraine", "dosage": "2 tablets", "frequency": "At onset", "warning": "Contains caffeine"},
            {"name": "Dark room rest", "dosage": "Lie down", "frequency": "During attack", "warning": "Natural remedy"},
            {"name": "Cold compress", "dosage": "On forehead/neck", "frequency": "15-20 mins", "warning": "Natural remedy"}
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
    
    def get_medications(self, symptoms: List[str], urgency: UrgencyLevel, 
                        diagnoses: List[Dict] = None, age: int = 30, 
                        gender: str = "unknown", allergies: List[str] = None) -> List[Dict]:
        """
        Get medication suggestions using AI-powered recommendations.
        Falls back to basic matching if AI fails.
        """
        # DON'T suggest medications for serious conditions
        if urgency in [UrgencyLevel.EMERGENCY, UrgencyLevel.URGENT]:
            return []
        
        # === TRY AI-POWERED MEDICATION SERVICE FIRST ===
        if HAS_AI_MEDICATION:
            try:
                urgency_str = urgency.value if hasattr(urgency, 'value') else str(urgency)
                ai_meds = get_smart_medications(
                    symptoms=symptoms,
                    diagnoses=diagnoses,
                    age=age,
                    gender=gender,
                    allergies=allergies,
                    urgency=urgency_str
                )
                if ai_meds and len(ai_meds) >= 2:
                    logger.info(f"💊 AI Medication service returned {len(ai_meds)} recommendations")
                    return ai_meds
            except Exception as e:
                logger.warning(f"AI Medication service failed: {e}")
        
        # === FALLBACK: Basic keyword matching ===
        logger.info("Using fallback medication matching")
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
            "migraine": {"conditions": ["pain", "migraine"], "preferred_subcats": ["mild_to_moderate", "migraine_otc"]},
            "body ache": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "back pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "joint pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "muscle pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "neck pain": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate", "topical"]},
            "toothache": {"conditions": ["pain"], "preferred_subcats": ["mild_to_moderate"]},
            "ear pain": {"conditions": ["pain", "ent"], "preferred_subcats": ["mild_to_moderate"]},
            "fever": {"conditions": ["fever"], "preferred_subcats": ["adults"]},
            "allergy": {"conditions": ["allergy"], "preferred_subcats": ["non_sedating", "antihistamines"]},
            "rash": {"conditions": ["allergy", "skin"], "preferred_subcats": ["topical", "antihistamines"]},
            "itching": {"conditions": ["allergy", "skin"], "preferred_subcats": ["topical", "antihistamines"]},
            "anxiety": {"conditions": ["mental_health"], "preferred_subcats": ["otc_stress_relief", "anxiolytics"]},
            "stress": {"conditions": ["mental_health"], "preferred_subcats": ["otc_stress_relief"]},
            "insomnia": {"conditions": ["mental_health"], "preferred_subcats": ["sleep", "otc_stress_relief"]},
            "depression": {"conditions": ["mental_health"], "preferred_subcats": ["otc_stress_relief"]},
            "dizziness": {"conditions": ["vertigo"], "preferred_subcats": ["antiemetics"]},
            "fatigue": {"conditions": ["general"], "preferred_subcats": ["vitamins", "supplements"]},
            "weakness": {"conditions": ["general"], "preferred_subcats": ["vitamins", "supplements"]},
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
        
        # === Drug RAG Integration: Always search PDF-based drug database for official drugs ===
        if HAS_DRUG_RAG and drug_rag:
            try:
                # Build search query from symptoms - also add condition inference terms
                search_terms = list(symptoms) if symptoms else []
                
                # Add condition inference terms based on symptom patterns
                symptoms_lower = [s.lower() for s in symptoms]
                symptoms_text = ' '.join(symptoms_lower)
                
                # Infer condition categories from symptoms
                if any(x in symptoms_text for x in ['urinary', 'urine', 'burning urination', 'uti', 'bladder']):
                    search_terms.extend(['infection', 'bacterial', 'antibacterial', 'urinary tract'])
                if any(x in symptoms_text for x in ['fever', 'temperature', 'chills']):
                    search_terms.extend(['antipyretic', 'fever'])
                if any(x in symptoms_text for x in ['cough', 'cold', 'congestion', 'sneeze']):
                    search_terms.extend(['respiratory', 'cough', 'expectorant'])
                if any(x in symptoms_text for x in ['diarrhea', 'loose stool', 'watery stool']):
                    search_terms.extend(['antidiarrhoeal', 'diarrhea'])
                if any(x in symptoms_text for x in ['vomit', 'nausea', 'throw up']):
                    search_terms.extend(['antiemetic', 'nausea'])
                if any(x in symptoms_text for x in ['allergy', 'allergic', 'itching', 'rash', 'hives']):
                    search_terms.extend(['antiallergic', 'antihistamine'])
                if any(x in symptoms_text for x in ['acidity', 'heartburn', 'indigestion', 'gastric', 'stomach pain', 'stomach ache', 'abdominal pain', 'abdomen pain']):
                    search_terms.extend(['antacid', 'peptic ulcer', 'gastric', 'anti peptic'])
                if any(x in symptoms_text for x in ['headache', 'migraine', 'head pain']):
                    search_terms.extend(['migraine', 'analgesic'])
                if any(x in symptoms_text for x in ['diabetes', 'blood sugar', 'glucose']):
                    search_terms.extend(['hypoglycaemic', 'diabetes'])
                if any(x in symptoms_text for x in ['blood pressure', 'hypertension', 'bp']):
                    search_terms.extend(['antihypertensive', 'blood pressure'])
                if any(x in symptoms_text for x in ['depression', 'sad', 'mood']):
                    search_terms.extend(['antidepressant', 'depression'])
                if any(x in symptoms_text for x in ['anxiety', 'panic', 'nervous']):
                    search_terms.extend(['anxiolytic', 'anxiety'])
                if any(x in symptoms_text for x in ['constipation', 'hard stool', 'difficulty passing']):
                    search_terms.extend(['laxative', 'constipation'])
                if any(x in symptoms_text for x in ['vertigo', 'dizzy', 'dizziness', 'spinning']):
                    search_terms.extend(['antivertigo', 'vertigo'])
                if any(x in symptoms_text for x in ['spasm', 'cramp', 'muscle pain']):
                    search_terms.extend(['antispasmodic', 'muscle relaxant'])
                if any(x in symptoms_text for x in ['fungal', 'fungus', 'ringworm', 'athlete foot']):
                    search_terms.extend(['antifungal', 'fungal'])
                if any(x in symptoms_text for x in ['worm', 'intestinal worm', 'parasites']):
                    search_terms.extend(['antihelminthic', 'worm'])
                
                search_query = ' '.join(search_terms)
                logger.info(f"🔍 Searching Drug RAG for: {search_query}")
                
                # Helper function to extract dosage from drug name
                def extract_dosage_from_name(name: str) -> str:
                    dosage_match = re.search(r'(\d+\.?\d*\s*(mg|ml|g|mcg|iu|%|mg/\d+ml))', name, re.IGNORECASE)
                    if dosage_match:
                        return dosage_match.group(1).strip()
                    return "As directed"
                
                # Use the new search_drugs method
                rag_drugs = drug_rag.search_drugs(search_query, symptoms=symptoms, n_results=5)
                logger.info(f"📋 Drug RAG returned {len(rag_drugs)} drugs")
                added_count = 0
                for drug in rag_drugs:
                    drug_name = drug.get('base_name', drug.get('name', ''))
                    if drug_name not in seen_meds:
                        # Add source info - these are from official drug list PDF
                        med_entry = {
                            "name": drug_name,
                            "full_name": drug.get('name', drug_name),
                            "category": drug.get('category', 'General'),
                            "dosage": extract_dosage_from_name(drug.get('name', '')),
                            "source": "DrugList PDF",
                            "verified": True,
                            "is_otc": True
                        }
                        medications.append(med_entry)
                        seen_meds.add(drug_name)
                        added_count += 1
                        logger.info(f"📋 Added RAG drug: {drug_name} ({drug.get('category', 'N/A')})")
                logger.info(f"✅ Added {added_count} drugs from Drug RAG")
            except Exception as e:
                logger.warning(f"Drug RAG lookup failed: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        else:
            logger.debug("Drug RAG not available (HAS_DRUG_RAG=False)")
        
        # === Smart Deduplication: Remove duplicate drugs with different formulations ===
        # e.g., "Paracetamol inj 500 mg", "Paracetamol tab 650 mg" -> keep only one
        # Also handles "Dolo 650 (Paracetamol)" matching with "Paracetamol"
        
        def extract_base_drug_name(name: str) -> str:
            """Extract base drug name without formulation details"""
            import re
            name_lower = name.lower().strip()
            
            # First, check for generic name in parentheses like "Dolo 650 (Paracetamol)"
            paren_match = re.search(r'\(([^)]+)\)', name_lower)
            if paren_match:
                generic = paren_match.group(1).strip()
                # If it looks like a drug name (not just "for pain" etc.), use it
                if len(generic) > 3 and not any(x in generic for x in ['for ', 'with ', 'and ']):
                    return generic
            
            # Remove brand name patterns like "Dolo 650 / Crocin"
            if ' / ' in name_lower:
                # Take the first part before /
                name_lower = name_lower.split(' / ')[0].strip()
            
            # Remove common formulation patterns: tab, inj, cap, syrup, mg, ml, etc.
            patterns_to_remove = [
                r'\s+(tab|tablet|tablets|inj|injection|cap|capsule|capsules|syrup|susp|suspension)\s*',
                r'\s+\d+\s*(mg|ml|mcg|g|iu)\b',  # Dosage like "500 mg", "10 ml"
                r'\s+\d+\s*$',  # Trailing numbers
                r'\s*\([^)]+\)\s*$',  # Parenthetical info at end
            ]
            result = name_lower
            for pattern in patterns_to_remove:
                result = re.sub(pattern, ' ', result, flags=re.IGNORECASE)
            return result.strip()
        
        def deduplicate_medications(meds: List[Dict]) -> List[Dict]:
            """Keep only one medication per base drug name, prefer branded with details"""
            seen_base_names = {}  # base_name -> best medication
            seen_generics = set()  # Track generic names we've seen
            
            for med in meds:
                name = med.get('name', '')
                base_name = extract_base_drug_name(name)
                
                # Skip if this generic drug was already added
                if base_name in seen_generics:
                    continue
                
                if base_name not in seen_base_names:
                    seen_base_names[base_name] = med
                    seen_generics.add(base_name)
                else:
                    # Prefer more detailed entries (branded with generic in parens)
                    existing = seen_base_names[base_name]
                    existing_name = existing.get('name', '').lower()
                    new_name = name.lower()
                    
                    # Prefer entries with brand names (have "/" or "()")
                    existing_has_details = '/' in existing_name or '(' in existing_name
                    new_has_details = '/' in new_name or '(' in new_name
                    
                    if new_has_details and not existing_has_details:
                        seen_base_names[base_name] = med
                    # Prefer tablets/capsules over injections
                    elif 'inj' in existing_name and ('tab' in new_name or 'cap' in new_name):
                        seen_base_names[base_name] = med
                    # Prefer common dosages (500-650mg for paracetamol, etc.)
                    elif '650' in new_name or '500' in new_name:
                        if '1000' in existing_name or '250' in existing_name:
                            seen_base_names[base_name] = med
            
            return list(seen_base_names.values())
        
        def filter_invalid_medications(meds: List[Dict]) -> List[Dict]:
            """Remove invalid entries like category names, single words that aren't drugs"""
            # Category names and invalid entries to filter out
            invalid_names = {
                'laxatives', 'antacids', 'antibiotics', 'antivirals', 'antifungals',
                'analgesics', 'antipyretics', 'antihistamines', 'decongestants',
                'expectorants', 'antitussives', 'nsaids', 'steroids', 'hormones',
                'vitamins', 'minerals', 'supplements', 'topical', 'oral', 'injectable',
                'tablet', 'capsule', 'syrup', 'injection', 'cream', 'ointment', 'gel',
                'drops', 'spray', 'inhaler', 'patch', 'suppository'
            }
            filtered = []
            for med in meds:
                name = med.get('name', '').lower().strip()
                # Skip if name is a category/invalid entry
                if name in invalid_names:
                    continue
                # Skip very short names (likely not real drugs)
                if len(name) < 3:
                    continue
                filtered.append(med)
            return filtered
        
        # Filter out invalid entries first, then deduplicate
        medications = filter_invalid_medications(medications)
        remedies = filter_invalid_medications(remedies)
        
        # Apply deduplication to all medications
        medications = deduplicate_medications(medications)
        remedies = deduplicate_medications(remedies)
        logger.info(f"🧹 After deduplication: {len(medications)} medications, {len(remedies)} remedies")
        
        # Smart selection: Prioritize official PDF drugs, then other medications
        # Separate medications by source for proper prioritization
        rag_meds = [m for m in medications if m.get('source') == 'DrugList PDF']
        other_meds = [m for m in medications if m.get('source') != 'DrugList PDF']
        
        # Allow more meds for multi-symptom cases
        max_total = min(10, 2 * len(symptoms) + 4)  # Scale with symptom count
        
        # Prioritize: RAG drugs first (official), then other medications, then remedies
        final_medications = rag_meds[:4] + other_meds[:max_total - len(rag_meds[:4])] + remedies[:2]
        logger.info(f"💊 Final selection: {len(rag_meds[:4])} RAG + {len(other_meds[:max_total-len(rag_meds[:4])])} other + {len(remedies[:2])} remedies")
        
        # Enrich with official database information (WHO ATC classification)
        if HAS_DRUG_DATABASE:
            final_medications = self._enrich_medications(final_medications)
        
        return final_medications
    
    def _enrich_medications(self, medications: List[Dict]) -> List[Dict]:
        """Enrich medications with official WHO ATC classification data"""
        enriched = []
        for med in medications:
            drug_name = med.get("name", "")
            original_source = med.get("source")  # Preserve original source
            
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
                # Only set source if not already set (preserve DrugList PDF source)
                if not original_source:
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
    
    def generate_follow_up_questions(self, symptoms: List[str], conversation_text: str) -> List[str]:
        """
        Generate smart follow-up questions based on symptoms to gather more info.
        A good doctor asks before diagnosing!
        IMPROVED: Better context checking to avoid repetitive questions.
        """
        questions = []
        symptoms_lower = [s.lower() for s in symptoms]
        # Clean conversation text - remove punctuation for better matching
        import re
        conv_lower = re.sub(r'[^\w\s]', ' ', conversation_text.lower())
        conv_words = set(conv_lower.split())
        
        # Symptom-specific follow-up questions
        SYMPTOM_QUESTIONS = {
            "headache": [
                ("Where exactly is the headache located - forehead, sides, or back of head?", ["forehead", "sides", "back", "located", "where"]),
                ("Is it a throbbing pain or constant pressure?", ["throbbing", "pressure", "constant", "pulsing"]),
                ("Did it start suddenly or gradually?", ["suddenly", "gradually", "started", "began"]),
                ("Any sensitivity to light or sound?", ["light", "sound", "sensitivity", "sensitive"])
            ],
            "migraine": [
                ("Do you see any visual disturbances like flashing lights?", ["visual", "flashing", "lights", "aura"]),
                ("Is the pain on one side of your head or both?", ["one side", "both sides", "left", "right"]),
                ("Any nausea or vomiting along with it?", ["nausea", "vomiting", "sick"]),
                ("Have you had migraines before?", ["before", "history", "previous", "recurring"])
            ],
            "fever": [
                ("What is your temperature reading?", ["temperature", "reading", "degrees", "measured"]),
                ("Any chills or sweating?", ["chills", "sweating", "shivering", "cold"]),
                ("When did the fever start?", ["started", "began", "since", "days"]),
                ("Any body aches or weakness along with fever?", ["aches", "weakness", "body pain", "tired"])
            ],
            "cough": [
                ("Is it a dry cough or producing mucus?", ["dry", "mucus", "phlegm", "wet"]),
                ("What color is the mucus if any?", ["color", "yellow", "green", "white", "clear"]),
                ("Does the cough worsen at night?", ["night", "worse", "evening", "sleeping"]),
                ("Any chest pain when coughing?", ["chest", "pain", "hurts"])
            ],
            "stomach pain": [
                ("Where exactly is the pain - upper, lower, left or right side?", ["upper", "lower", "left", "right", "location"]),
                ("Is it sharp pain or dull ache?", ["sharp", "dull", "ache", "stabbing"]),
                ("Any relation to eating - before or after meals?", ["eating", "meals", "food", "after"]),
                ("Any vomiting, diarrhea or constipation?", ["vomiting", "diarrhea", "constipation", "loose"])
            ],
            "joint pain": [
                ("Which joints are affected?", ["knee", "elbow", "shoulder", "wrist", "ankle", "hip", "joints"]),
                ("Any swelling, redness, or warmth?", ["swelling", "redness", "warmth", "swollen", "red", "warm"]),
                ("Worse in morning or after activity?", ["morning", "activity", "exercise", "movement"]),
                ("Any recent injury or overuse?", ["injury", "hurt", "fell", "accident"])
            ],
            "rash": [
                ("Where on your body is the rash?", ["arm", "leg", "chest", "back", "face", "body"]),
                ("Is it itchy, painful, or neither?", ["itchy", "painful", "scratchy", "burning"]),
                ("Any new products, foods, or medications recently?", ["new", "product", "medication", "food", "allergy"]),
                ("Is it spreading or staying in one area?", ["spreading", "growing", "same", "area"])
            ],
            "anxiety": [
                ("What triggers your anxious feelings?", ["trigger", "cause", "situation", "when"]),
                ("Any physical symptoms like racing heart or sweating?", ["heart", "racing", "sweating", "trembling"]),
                ("How long have you been feeling this way?", ["long", "days", "weeks", "months"]),
                ("Any trouble sleeping or concentrating?", ["sleep", "sleeping", "concentrate", "focus"])
            ]
        }
        
        # General questions if we have few symptoms
        GENERAL_QUESTIONS = [
            ("How long have you been experiencing these symptoms?", ["long", "days", "weeks", "started", "duration"]),
            ("On a scale of 1-10, how severe is your discomfort?", ["scale", "severity", "severe", "mild", "10"]),
            ("Are you currently taking any medications?", ["medication", "medicine", "taking", "drugs", "pills"]),
            ("Do you have any known allergies?", ["allergy", "allergic", "allergies"]),
        ]
        
        def is_already_answered(check_words):
            """Check if any of the key words are already in the conversation"""
            return any(word in conv_words for word in check_words)
        
        # Add symptom-specific questions (max 2 per symptom)
        for symptom in symptoms_lower:
            for pattern, q_list in SYMPTOM_QUESTIONS.items():
                if pattern in symptom or symptom in pattern:
                    for question, check_words in q_list:
                        # Don't ask if already answered in conversation
                        if not is_already_answered(check_words):
                            if question not in questions:
                                questions.append(question)
                                if len(questions) >= 2:  # Max 2 questions total per symptom
                                    break
                    break
        
        # If we have few symptom-specific questions, add general ones
        if len(questions) < 2:
            for question, check_words in GENERAL_QUESTIONS:
                if not is_already_answered(check_words):
                    if question not in questions:
                        questions.append(question)
                if len(questions) >= 3:
                    break
        
        return questions[:3]  # Return max 3 questions (reduced from 4)
    
    def generate_differential_diagnosis(self, symptoms: List[str], vitals: Optional[Dict] = None, 
                                         age: int = 30, gender: str = "unknown") -> List[Dict]:
        """
        Generate differential diagnosis using AI - no hardcoded database!
        Uses Ollama LLM for dynamic, intelligent diagnosis like a real doctor.
        """
        # Try advanced AI diagnosis first
        if HAS_ADVANCED_DIAGNOSIS:
            try:
                # Use the imported advanced_diagnosis from diagnosis_engine
                # which internally uses ai_diagnosis.py with Ollama LLM
                ai_result = advanced_diagnosis(symptoms, age=age, gender=gender)
                if ai_result:
                    logger.info(f"🧠 AI Diagnosis returned {len(ai_result)} conditions for: {symptoms}")
                    # Normalize format if needed (confidence as decimal)
                    for diag in ai_result:
                        if isinstance(diag.get("confidence"), (int, float)) and diag["confidence"] > 1:
                            diag["confidence"] = diag["confidence"] / 100.0
                        diag["confidence"] = round(diag.get("confidence", 0.5), 2)
                    return ai_result[:5]
            except Exception as e:
                logger.error(f"Advanced diagnosis failed: {e}")
        
        # Fallback: Try direct AI diagnosis
        try:
            from app.services.ai_diagnosis import get_ai_diagnosis_sync
            ai_result = get_ai_diagnosis_sync(symptoms, age=age, gender=gender)
            if ai_result:
                logger.info(f"🧠 Direct AI Diagnosis: {len(ai_result)} conditions")
                # Normalize confidence to decimal
                for diag in ai_result:
                    if isinstance(diag.get("confidence"), (int, float)) and diag["confidence"] > 1:
                        diag["confidence"] = diag["confidence"] / 100.0
                    diag["confidence"] = round(diag.get("confidence", 0.5), 2)
                return ai_result[:5]
        except Exception as e:
            logger.error(f"Direct AI diagnosis failed: {e}")
        
        # Ultimate fallback - minimal generic response
        logger.warning("All AI diagnosis methods failed, using minimal fallback")
        return [
            {"condition": "Requires Assessment", "confidence": 0.40, "urgency": "routine", 
             "description": f"Symptoms ({', '.join(symptoms[:3])}) need proper medical evaluation"},
            {"condition": "General Medical Consultation Needed", "confidence": 0.35, "urgency": "routine",
             "description": "Please consult a healthcare provider for accurate diagnosis"},
        ]
    
    def should_ask_followup(self, symptoms: List[str], message_count: int) -> bool:
        """
        Determine if we should ask follow-up questions before giving diagnosis.
        Returns True ONLY if we really need more information.
        
        CHANGED: Be less aggressive - prefer giving advice over asking questions
        """
        # If we have at least one clear symptom, give advice first
        if len(symptoms) >= 1:
            return False  # Give advice, don't ask more questions
        
        # Only ask follow-up if symptoms are very vague
        vague_symptoms = ["pain", "discomfort", "unwell", "sick", "bad", "not feeling well"]
        if all(any(v in s.lower() for v in vague_symptoms) for s in symptoms):
            return True
        
        return False


class PowerfulAIService:
    """
    Production-grade AI Health Assistant
    Uses multiple models intelligently for best results
    
    Model Routing Strategy:
    - medllama2: Medical queries (trained on medical literature)
    - gemma2:9b: Complex reasoning tasks
    - llama3.1:8b: General queries
    - llama3.2:3b: Fast/simple queries
    - llava:7b: Image analysis
    """
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.reasoning_engine = MedicalReasoningEngine()
        self.redis_client = None
        self._init_redis()
        
        # Model configuration - MEDICAL FIRST for accuracy
        # Trade-off: medllama2 is slower (~10-15s) but more accurate for medical
        # Use intelligent routing based on query type
        self.models = {
            "medical": ModelType.MEDICAL.value,  # medllama2 - trained on medical data
            "general": ModelType.GENERAL.value,  # llama3.1:8b - broad knowledge
            "fast": ModelType.FAST.value,        # llama3.2:3b - quick responses
            "vision": ModelType.VISION.value,    # llava:7b - image analysis
            "reasoning": ModelType.REASONING.value  # gemma2:9b - complex reasoning
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
        return """You are MedAssist, a helpful health assistant.

RULES:
- Give practical advice, not just "see a doctor"
- 2-3 short paragraphs max
- No bullet points or headers
- Be warm and helpful

FORMAT:
1. Acknowledge symptom
2. Explain likely cause
3. Give 2-3 home remedies
4. When to see doctor (only if serious)

EXAMPLE: "I understand constipation is uncomfortable. This usually happens from low fiber, dehydration, or inactivity. Try drinking 8 glasses of water, eating more fruits/veggies, and taking a 20-min walk. Isabgol before bed can help. See a doctor if it lasts over a week or causes severe pain."
- Keep responses under 100 words"""

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

    def _get_follow_up_prompt(self) -> str:
        return """You are MedAssist, a caring AI health assistant gathering information.

BEHAVIOR: Like a good doctor, you need to understand the patient's condition better before making any assessment.

RESPONSE STYLE:
- Acknowledge what they've shared
- Ask 1-2 clarifying questions naturally in conversation
- Be warm and reassuring
- Keep response SHORT (2-3 sentences max)

EXAMPLE:
User: "I have a headache"
You: "I'm sorry to hear you're dealing with a headache. To help you better, could you tell me where exactly it hurts and when it started? Also, is it a throbbing pain or more like pressure?"

IMPORTANT:
- Do NOT diagnose yet
- Do NOT suggest medications yet
- Just gather more information naturally
- Ask relevant follow-up questions
- Be conversational, not clinical"""

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
        Now includes follow-up questions and differential diagnosis!
        """
        start_time = time.time()
        
        # Step 1: Track symptoms from current message FIRST (before getting history)
        self.memory.track_symptoms(session_id, message)
        
        # Step 2: Get conversation history INCLUDING current message for context-aware analysis
        conversation_history = self.memory.get_full_conversation_text(session_id)
        # Append current message to ensure it's included in context checks
        full_conversation = f"{conversation_history} {message}".strip()
        
        # Step 3: Get all accumulated symptoms
        all_symptoms = self.memory.get_all_symptoms(session_id)
        
        # Step 4: Analyze with full conversation history (critical for multi-turn symptom detection)
        analysis = self.reasoning_engine.analyze_with_history(message, all_symptoms, full_conversation, vitals)
        
        # Step 4.5: Count conversation turns to decide if we need more info
        turn_count = len(self.memory.conversations.get(session_id, [])) // 2 + 1
        
        # Step 4.6: Determine if we should ask follow-up questions
        needs_more_info = False
        follow_up_questions = []
        
        # Don't ask follow-ups for emergencies or if we have enough info
        if analysis["urgency"] != UrgencyLevel.EMERGENCY:
            needs_more_info = self.reasoning_engine.should_ask_followup(all_symptoms, turn_count)
            if needs_more_info or len(all_symptoms) >= 1:
                follow_up_questions = self.reasoning_engine.generate_follow_up_questions(
                    all_symptoms, full_conversation  # Use full_conversation which includes current message
                )
        
        # Step 4.7: Generate differential diagnosis
        diagnoses = self.reasoning_engine.generate_differential_diagnosis(all_symptoms, vitals)
        
        # Step 5: Check cache for similar queries (only for non-emergency, single-turn)
        cache_key = self._get_cache_key(message, language)
        if not full_conversation.strip():  # Only use cache for first message
            cached = await self._get_cached_response(cache_key)
            if cached and analysis["urgency"] == UrgencyLevel.SELF_CARE:
                cached["processing_time_ms"] = int((time.time() - start_time) * 1000)
                return AIResponse(**cached)
        
        # Step 5: Select appropriate model and prompt
        model, system_prompt = self._select_model_and_prompt(analysis, image_base64)
        
        # Step 5.5: Modify prompt if we need to ask follow-up questions
        if needs_more_info and follow_up_questions and not image_base64:
            system_prompt = self._get_follow_up_prompt()
        
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
            
            # Step 8.5: AI-powered symptom extraction - SKIP if we already have symptoms (speed optimization)
            # Only run AI extraction for vague/complex messages without clear symptoms
            if len(analysis["symptoms_detected"]) < 1:
                ai_extracted_symptoms = await self._extract_symptoms_with_ai(full_conversation, message)
                if ai_extracted_symptoms:
                    self.memory.add_symptoms(session_id, ai_extracted_symptoms)
                    all_symptoms = list(set(analysis["symptoms_detected"] + ai_extracted_symptoms))
                    analysis["symptoms_detected"] = all_symptoms
                    logger.info(f"📋 Updated symptoms with AI extraction: {all_symptoms}")
            else:
                logger.info(f"⚡ Skipping AI symptom extraction - already have {len(analysis['symptoms_detected'])} symptoms")
            
            # Step 9: Build response with diagnoses and follow-up questions
            response = AIResponse(
                text=ai_text,
                urgency=analysis["urgency"],
                confidence=analysis["confidence"],
                model_used=model,
                reasoning="; ".join(analysis["reasoning"]) if analysis["reasoning"] else None,
                symptoms_detected=analysis["symptoms_detected"],
                conditions_suggested=analysis["conditions_suggested"],
                diagnoses=diagnoses,  # NEW: Multiple diagnoses with confidence
                specialist_recommended=analysis["specialist"],
                follow_up_questions=follow_up_questions,  # NEW: Follow-up questions
                needs_more_info=needs_more_info,  # NEW: Flag for UI
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
        """
        SPEED-OPTIMIZED model selection.
        Use FAST model by default, only use slow medical model for complex cases.
        """
        
        if has_image:
            return self.models["vision"], self.system_prompts["medical"]
        
        # ONLY use medical model for true emergencies
        if analysis["urgency"] == UrgencyLevel.EMERGENCY:
            return self.models["medical"], self.system_prompts["emergency"]
        
        if analysis["mental_health"]:
            return self.models["general"], self.system_prompts["mental_health"]
        
        # SPEED OPTIMIZATION: Use FAST model for most queries
        # medllama2 is ~3x slower but only marginally better for common symptoms
        return self.models["fast"], self.system_prompts["medical"]

    def _extract_dosage(self, drug_name: str) -> str:
        """Extract dosage information from drug name string."""
        import re
        # Look for patterns like "650 mg", "500mg", "100 mg/5ml"
        dosage_match = re.search(r'(\d+\.?\d*\s*(mg|ml|g|mcg|iu|%|mg/\d+ml))', drug_name, re.IGNORECASE)
        if dosage_match:
            return dosage_match.group(1).strip()
        return "As directed"

    async def _extract_symptoms_with_ai(self, conversation_text: str, current_message: str) -> List[str]:
        """
        Use AI to extract symptoms from conversation context.
        This understands contextual references like "it is green" referring to urine.
        """
        prompt = f"""Extract medical symptoms from this conversation. Output ONLY symptom names separated by commas.

Conversation: {conversation_text}
Current: {current_message}

Rules:
- Output ONLY symptoms, nothing else
- Use format: symptom1, symptom2, symptom3
- Be specific: "green urine" not just "green"
- If user says "it is green" after discussing urination, output "green urine"
- No explanations, no sentences, just symptoms

Symptoms:"""

        try:
            response = ollama.chat(
                model=self.models["fast"],
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.0,  # Zero for deterministic
                    "num_predict": 50,  # Very short response
                }
            )
            
            symptoms_text = response["message"]["content"].strip()
            
            # Parse comma-separated symptoms
            symptoms = []
            for s in symptoms_text.replace("\n", ",").split(","):
                symptom = s.strip().lower()
                # Filter out non-symptoms and garbage
                if (symptom and 
                    len(symptom) > 2 and 
                    len(symptom) < 50 and  # Filter long garbage
                    symptom not in ["none", "no symptoms", "n/a", ""] and
                    not symptom.startswith("note") and
                    not symptom.startswith("based") and
                    not symptom.startswith("here")):
                    # Clean up common prefixes
                    symptom = symptom.lstrip("- •").strip()
                    if symptom and len(symptom.split()) <= 4:  # Max 4 words per symptom
                        symptoms.append(symptom)
            
            logger.info(f"🧠 AI extracted symptoms: {symptoms}")
            return symptoms[:6]  # Max 6 symptoms
            
        except Exception as e:
            logger.warning(f"AI symptom extraction failed: {e}")
            return []

    async def _generate_response(
        self,
        message: str,
        model: str,
        system_prompt: str,
        context: List[Dict],
        language: str
    ) -> str:
        """Generate AI response using Ollama - directly in native language for better quality"""
        
        # Language names for prompting
        LANGUAGE_NAMES = {
            "hi": "Hindi (हिंदी)", "ta": "Tamil (தமிழ்)", "te": "Telugu (తెలుగు)",
            "kn": "Kannada (ಕನ್ನಡ)", "ml": "Malayalam (മലയാളം)", "bn": "Bengali (বাংলা)",
            "gu": "Gujarati (ગુજરાતી)", "mr": "Marathi (मराठी)", "pa": "Punjabi (ਪੰਜਾਬੀ)",
            "or": "Odia (ଓଡ଼ିଆ)", "as": "Assamese (অসমীয়া)", "ur": "Urdu (اردو)", "en": "English"
        }
        
        # Modify system prompt to generate in native language
        if language != "en" and language in LANGUAGE_NAMES:
            lang_name = LANGUAGE_NAMES[language]
            native_prompt = f"""{system_prompt}

CRITICAL LANGUAGE & FORMAT INSTRUCTIONS:
1. RESPOND ONLY IN {lang_name} - use native script, not transliteration.
2. KEEP RESPONSE CONCISE - maximum 3-4 sentences.
3. STRUCTURE: Start with empathy → Give 1-2 possible causes → Suggest 1-2 home remedies → Advise when to see doctor.
4. Be warm like a family doctor. Use simple words.
5. ALWAYS complete your sentences - never leave response incomplete.
6. If stomach pain: mention antacids, light food, rest.
7. If fever: mention paracetamol, fluids, rest."""
            messages = [{"role": "system", "content": native_prompt}]
        else:
            messages = [{"role": "system", "content": system_prompt}]
        
        messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": 0.5,  # Slightly higher for more natural language
                    "top_p": 0.85,
                    "num_predict": 400,  # Increased for complete native language responses
                    "num_ctx": 2048,     # Larger context for better understanding
                }
            )
            native_response = response["message"]["content"]
            logger.info(f"Generated native {language} response directly from AI")
            return native_response
            
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
        "diagnoses": response.diagnoses,  # NEW: Multiple diagnoses with confidence
        "follow_up_questions": response.follow_up_questions,  # NEW: Follow-up questions for UI
        "needs_more_info": response.needs_more_info,  # NEW: Flag to show follow-up UI
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
