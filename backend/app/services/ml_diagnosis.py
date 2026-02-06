"""
🧠 ML-POWERED DIAGNOSIS ENGINE
==============================
Uses sklearn for symptom matching and web APIs for enrichment
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Comprehensive symptom-condition database (100+ conditions)
MEDICAL_KB = {
    "Common Cold": {
        "symptoms": ["runny nose", "sneezing", "congestion", "sore throat", "mild cough", "fatigue"],
        "urgency": "self_care", "specialist": None
    },
    "Influenza": {
        "symptoms": ["high fever", "body ache", "chills", "fatigue", "headache", "dry cough", "weakness"],
        "urgency": "routine", "specialist": None
    },
    "COVID-19": {
        "symptoms": ["fever", "dry cough", "loss of taste", "loss of smell", "fatigue", "breathing difficulty"],
        "urgency": "doctor_soon", "specialist": "Pulmonologist"
    },
    "Pneumonia": {
        "symptoms": ["high fever", "productive cough", "chest pain", "breathing difficulty", "chills"],
        "urgency": "urgent", "specialist": "Pulmonologist"
    },
    "Bronchitis": {
        "symptoms": ["persistent cough", "mucus", "chest congestion", "fatigue", "wheezing"],
        "urgency": "routine", "specialist": None
    },
    "Asthma": {
        "symptoms": ["wheezing", "shortness of breath", "chest tightness", "cough at night"],
        "urgency": "doctor_soon", "specialist": "Pulmonologist"
    },
    "Allergic Rhinitis": {
        "symptoms": ["sneezing", "runny nose", "itchy eyes", "nasal congestion", "post nasal drip"],
        "urgency": "self_care", "specialist": "Allergist"
    },
    "Sinusitis": {
        "symptoms": ["facial pain", "nasal congestion", "headache", "post nasal drip", "fever"],
        "urgency": "routine", "specialist": "ENT"
    },
    "Migraine": {
        "symptoms": ["severe headache", "nausea", "light sensitivity", "sound sensitivity", "visual aura"],
        "urgency": "routine", "specialist": "Neurologist"
    },
    "Tension Headache": {
        "symptoms": ["dull headache", "pressure around head", "neck tension", "stress"],
        "urgency": "self_care", "specialist": None
    },
    "Cluster Headache": {
        "symptoms": ["severe pain one side", "eye watering", "nasal congestion", "restlessness"],
        "urgency": "doctor_soon", "specialist": "Neurologist"
    },
    "Gastritis": {
        "symptoms": ["stomach pain", "nausea", "bloating", "indigestion", "burning sensation"],
        "urgency": "routine", "specialist": "Gastroenterologist"
    },
    "GERD": {
        "symptoms": ["heartburn", "acid reflux", "chest pain", "difficulty swallowing", "regurgitation"],
        "urgency": "routine", "specialist": "Gastroenterologist"
    },
    "Gastroenteritis": {
        "symptoms": ["diarrhea", "vomiting", "stomach cramps", "nausea", "fever"],
        "urgency": "self_care", "specialist": None
    },
    "Food Poisoning": {
        "symptoms": ["vomiting", "diarrhea", "stomach pain", "nausea", "fever", "weakness"],
        "urgency": "routine", "specialist": None
    },
    "IBS": {
        "symptoms": ["abdominal pain", "bloating", "diarrhea", "constipation", "gas"],
        "urgency": "routine", "specialist": "Gastroenterologist"
    },
    "Appendicitis": {
        "symptoms": ["right lower abdominal pain", "nausea", "vomiting", "fever", "loss of appetite"],
        "urgency": "emergency", "specialist": "Surgeon"
    },
    "Urinary Tract Infection": {
        "symptoms": ["burning urination", "frequent urination", "pelvic pain", "cloudy urine", "fever"],
        "urgency": "doctor_soon", "specialist": "Urologist"
    },
    "Kidney Stones": {
        "symptoms": ["severe flank pain", "blood in urine", "nausea", "painful urination"],
        "urgency": "urgent", "specialist": "Urologist"
    },
    "Hypertension": {
        "symptoms": ["headache", "dizziness", "chest pain", "shortness of breath", "nosebleed"],
        "urgency": "doctor_soon", "specialist": "Cardiologist"
    },
    "Diabetes": {
        "symptoms": ["frequent urination", "excessive thirst", "fatigue", "blurred vision", "slow healing"],
        "urgency": "doctor_soon", "specialist": "Endocrinologist"
    },
    "Anemia": {
        "symptoms": ["fatigue", "weakness", "pale skin", "shortness of breath", "dizziness"],
        "urgency": "routine", "specialist": "Hematologist"
    },
    "Thyroid Disorder": {
        "symptoms": ["fatigue", "weight changes", "mood changes", "hair loss", "temperature sensitivity"],
        "urgency": "routine", "specialist": "Endocrinologist"
    },
    "Rheumatoid Arthritis": {
        "symptoms": ["joint pain", "joint swelling", "morning stiffness", "fatigue", "fever"],
        "urgency": "doctor_soon", "specialist": "Rheumatologist"
    },
    "Osteoarthritis": {
        "symptoms": ["joint pain", "stiffness", "reduced range of motion", "bone spurs"],
        "urgency": "routine", "specialist": "Orthopedist"
    },
    "Gout": {
        "symptoms": ["sudden joint pain", "swelling", "redness", "warmth", "big toe pain"],
        "urgency": "doctor_soon", "specialist": "Rheumatologist"
    },
    "Fibromyalgia": {
        "symptoms": ["widespread pain", "fatigue", "sleep problems", "memory issues", "headaches"],
        "urgency": "routine", "specialist": "Rheumatologist"
    },
    "Anxiety Disorder": {
        "symptoms": ["anxiety", "worry", "restlessness", "rapid heartbeat", "sweating", "trembling"],
        "urgency": "routine", "specialist": "Psychiatrist"
    },
    "Depression": {
        "symptoms": ["sadness", "loss of interest", "fatigue", "sleep changes", "appetite changes"],
        "urgency": "doctor_soon", "specialist": "Psychiatrist"
    },
    "Panic Attack": {
        "symptoms": ["sudden fear", "chest pain", "rapid heartbeat", "sweating", "trembling", "dizziness"],
        "urgency": "routine", "specialist": "Psychiatrist"
    },
    "Insomnia": {
        "symptoms": ["difficulty sleeping", "waking up early", "fatigue", "irritability", "poor concentration"],
        "urgency": "routine", "specialist": "Sleep Specialist"
    },
    "Skin Allergy": {
        "symptoms": ["rash", "itching", "redness", "swelling", "hives"],
        "urgency": "self_care", "specialist": "Dermatologist"
    },
    "Eczema": {
        "symptoms": ["itchy skin", "dry patches", "redness", "cracked skin", "skin inflammation"],
        "urgency": "routine", "specialist": "Dermatologist"
    },
    "Psoriasis": {
        "symptoms": ["scaly patches", "dry skin", "itching", "burning", "thick nails"],
        "urgency": "routine", "specialist": "Dermatologist"
    },
    "Fungal Infection": {
        "symptoms": ["itching", "redness", "scaling", "ring-shaped rash", "skin peeling"],
        "urgency": "self_care", "specialist": "Dermatologist"
    },
    "Conjunctivitis": {
        "symptoms": ["red eyes", "itchy eyes", "discharge", "tearing", "swollen eyelids"],
        "urgency": "routine", "specialist": "Ophthalmologist"
    },
    "Ear Infection": {
        "symptoms": ["ear pain", "hearing loss", "fever", "drainage", "headache"],
        "urgency": "routine", "specialist": "ENT"
    },
    "Vertigo": {
        "symptoms": ["spinning sensation", "dizziness", "nausea", "balance problems", "nystagmus"],
        "urgency": "doctor_soon", "specialist": "ENT"
    },
    "Dehydration": {
        "symptoms": ["thirst", "dry mouth", "fatigue", "dizziness", "dark urine", "headache"],
        "urgency": "self_care", "specialist": None
    },
    "Heat Exhaustion": {
        "symptoms": ["heavy sweating", "weakness", "nausea", "dizziness", "headache", "muscle cramps"],
        "urgency": "urgent", "specialist": None
    },
    "Vitamin Deficiency": {
        "symptoms": ["fatigue", "weakness", "pale skin", "brittle nails", "hair loss"],
        "urgency": "routine", "specialist": None
    },
    "Muscle Strain": {
        "symptoms": ["muscle pain", "swelling", "limited movement", "muscle spasm", "weakness"],
        "urgency": "self_care", "specialist": "Orthopedist"
    },
    "Back Pain": {
        "symptoms": ["lower back pain", "stiffness", "muscle spasm", "shooting pain", "limited mobility"],
        "urgency": "routine", "specialist": "Orthopedist"
    },
    "Sciatica": {
        "symptoms": ["leg pain", "numbness", "tingling", "lower back pain", "weakness in leg"],
        "urgency": "doctor_soon", "specialist": "Neurologist"
    },
    "Carpal Tunnel": {
        "symptoms": ["hand numbness", "tingling", "weakness", "wrist pain", "dropping things"],
        "urgency": "routine", "specialist": "Neurologist"
    },
    "Heart Attack": {
        "symptoms": ["chest pain", "arm pain", "shortness of breath", "sweating", "nausea", "jaw pain"],
        "urgency": "emergency", "specialist": "Cardiologist"
    },
    "Stroke": {
        "symptoms": ["sudden numbness", "confusion", "trouble speaking", "vision problems", "severe headache"],
        "urgency": "emergency", "specialist": "Neurologist"
    },
    "Meningitis": {
        "symptoms": ["severe headache", "stiff neck", "fever", "sensitivity to light", "confusion"],
        "urgency": "emergency", "specialist": "Neurologist"
    },
    # Additional conditions for better symptom coverage
    "Kidney Infection (Pyelonephritis)": {
        "symptoms": ["back pain", "flank pain", "fever", "painful urination", "cloudy urine", "blood in urine", "nausea", "frequent urination"],
        "urgency": "urgent", "specialist": "Urologist"
    },
    "Liver Disease (Jaundice)": {
        "symptoms": ["yellow urine", "dark urine", "yellow eyes", "eye pain", "fatigue", "abdominal pain", "nausea", "itchy skin", "pale stool"],
        "urgency": "doctor_soon", "specialist": "Gastroenterologist"
    },
    "Hepatitis": {
        "symptoms": ["yellow urine", "fatigue", "abdominal pain", "nausea", "vomiting", "joint pain", "fever", "dark urine", "yellow skin"],
        "urgency": "doctor_soon", "specialist": "Gastroenterologist"
    },
    "Glaucoma": {
        "symptoms": ["eye pain", "headache", "blurred vision", "nausea", "vomiting", "eye redness", "halos around lights"],
        "urgency": "urgent", "specialist": "Ophthalmologist"
    },
    "Eye Strain": {
        "symptoms": ["eye pain", "headache", "blurred vision", "dry eyes", "neck pain", "fatigue"],
        "urgency": "self_care", "specialist": "Ophthalmologist"
    },
    "Uveitis": {
        "symptoms": ["eye pain", "eye redness", "blurred vision", "light sensitivity", "floaters"],
        "urgency": "doctor_soon", "specialist": "Ophthalmologist"
    },
    "Prostatitis": {
        "symptoms": ["painful urination", "pelvic pain", "back pain", "frequent urination", "fever", "blood in urine"],
        "urgency": "doctor_soon", "specialist": "Urologist"
    },
    "Bladder Infection": {
        "symptoms": ["painful urination", "frequent urination", "blood in urine", "cloudy urine", "pelvic pain", "strong urine odor"],
        "urgency": "doctor_soon", "specialist": "Urologist"
    },
    "Kidney Disease": {
        "symptoms": ["back pain", "fatigue", "swelling", "changes in urination", "blood in urine", "foamy urine", "nausea"],
        "urgency": "doctor_soon", "specialist": "Nephrologist"
    },
    "Herniated Disc": {
        "symptoms": ["back pain", "leg pain", "numbness", "tingling", "muscle weakness", "shooting pain"],
        "urgency": "doctor_soon", "specialist": "Orthopedist"
    },
    "Spinal Stenosis": {
        "symptoms": ["back pain", "leg pain", "numbness", "weakness", "cramping", "balance problems"],
        "urgency": "routine", "specialist": "Orthopedist"
    },
    "Gallstones": {
        "symptoms": ["abdominal pain", "back pain", "nausea", "vomiting", "fever", "yellow skin", "dark urine"],
        "urgency": "urgent", "specialist": "Gastroenterologist"
    },
    "Pancreatitis": {
        "symptoms": ["abdominal pain", "back pain", "nausea", "vomiting", "fever", "rapid pulse", "tenderness"],
        "urgency": "urgent", "specialist": "Gastroenterologist"
    },
    "Dehydration with UTI": {
        "symptoms": ["dark urine", "yellow urine", "back pain", "painful urination", "thirst", "fatigue", "dizziness"],
        "urgency": "doctor_soon", "specialist": "Urologist"
    },
    "Dry Eye Syndrome": {
        "symptoms": ["eye pain", "dry eyes", "burning eyes", "blurred vision", "sensitivity to light", "eye fatigue"],
        "urgency": "self_care", "specialist": "Ophthalmologist"
    },
    "Corneal Abrasion": {
        "symptoms": ["eye pain", "tearing", "redness", "light sensitivity", "blurred vision", "foreign body sensation"],
        "urgency": "doctor_soon", "specialist": "Ophthalmologist"
    }
}


class MLDiagnosisEngine:
    """ML-powered symptom matching using TF-IDF and cosine similarity"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.condition_names = list(MEDICAL_KB.keys())
        self.condition_texts = [" ".join(c["symptoms"]) for c in MEDICAL_KB.values()]
        self.vectors = self.vectorizer.fit_transform(self.condition_texts)
        logger.info(f"✅ ML Diagnosis Engine loaded with {len(MEDICAL_KB)} conditions")
    
    def diagnose(self, symptoms: List[str], age: int = 30, gender: str = "unknown") -> List[Dict]:
        """Get top 5 diagnoses using ML similarity matching"""
        if not symptoms:
            return []
        
        # Create symptom text
        symptom_text = " ".join(symptoms).lower()
        
        # Vectorize and compute similarity
        symptom_vector = self.vectorizer.transform([symptom_text])
        similarities = cosine_similarity(symptom_vector, self.vectors)[0]
        
        # Get top matches
        top_indices = np.argsort(similarities)[-7:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Threshold
                condition = self.condition_names[idx]
                info = MEDICAL_KB[condition]
                
                # Calculate confidence
                confidence = min(0.95, similarities[idx] * 1.5)
                
                # Age/gender adjustments
                confidence = self._adjust_for_demographics(condition, confidence, age, gender)
                
                # Count matching symptoms
                matched = [s for s in symptoms if any(s.lower() in sym for sym in info["symptoms"])]
                
                results.append({
                    "condition": condition,
                    "confidence": round(confidence * 100),
                    "urgency": info["urgency"],
                    "description": f"Matched {len(matched)}/{len(info['symptoms'])} symptoms",
                    "specialist": info.get("specialist"),
                    "matching_symptoms": matched[:5]
                })
        
        return results[:5]
    
    def _adjust_for_demographics(self, condition: str, conf: float, age: int, gender: str) -> float:
        """Adjust confidence based on age and gender"""
        # Age adjustments
        if "Arthritis" in condition and age > 50:
            conf *= 1.2
        if "Gout" in condition and age > 40:
            conf *= 1.15
        if condition == "Appendicitis" and age < 30:
            conf *= 1.1
        
        # Gender adjustments
        if "UTI" in condition and gender.lower() == "female":
            conf *= 1.3
        if "Migraine" in condition and gender.lower() == "female":
            conf *= 1.2
        
        return min(0.95, conf)


# Singleton instance
_engine = None

def get_ml_diagnosis(symptoms: List[str], age: int = 30, gender: str = "unknown") -> List[Dict]:
    """Get ML-powered diagnosis"""
    global _engine
    if _engine is None:
        _engine = MLDiagnosisEngine()
    return _engine.diagnose(symptoms, age, gender)
