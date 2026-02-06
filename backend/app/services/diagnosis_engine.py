"""
🏥 ADVANCED DIFFERENTIAL DIAGNOSIS ENGINE
==========================================
A powerful medical diagnosis system with:
- AI-POWERED dynamic symptom analysis (no fixed mappings!)
- Fallback to ML-powered TF-IDF symptom matching
- Risk factor analysis (age, gender, medical history)
- Vital signs integration
- Red flag detection
- Specialist recommendations
"""

from typing import Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)

# Import AI-powered diagnosis engine (DYNAMIC - no fixed symptoms!)
try:
    from app.services.ai_diagnosis import get_ai_diagnosis_sync
    HAS_AI_DIAGNOSIS = True
    logger.info("✅ AI-Powered Dynamic Diagnosis Engine loaded")
except ImportError:
    HAS_AI_DIAGNOSIS = False
    logger.warning("⚠️ AI Diagnosis not available")

# Import ML diagnosis engine as fallback
try:
    from app.services.ml_diagnosis import get_ml_diagnosis, MLDiagnosisEngine
    HAS_ML_ENGINE = True
    logger.info("✅ ML Diagnosis Engine loaded")
except ImportError:
    HAS_ML_ENGINE = False
    logger.warning("⚠️ ML Diagnosis Engine not available")

# 🔬 COMPREHENSIVE CONDITION DATABASE (fallback only)
# Each condition has: symptoms with weights, patterns, risk factors, red flags
CONDITION_DATABASE = {
    # ==================== RESPIRATORY CONDITIONS ====================
    "Common Cold": {
        "symptoms": {
            "primary": ["runny nose", "sneezing", "congestion", "sore throat", "cold"],
            "secondary": ["cough", "fatigue", "mild headache", "watery eyes"],
            "rare": ["low fever", "body ache"]
        },
        "patterns": ["gradual_onset", "seasonal"],
        "duration_typical": "7-10 days",
        "base_confidence": 0.75,
        "urgency": "self_care",
        "description": "Viral upper respiratory infection, self-limiting",
        "distinguishing": "No high fever, gradual symptom progression",
        "home_treatment": "Rest, fluids, OTC decongestants, honey for cough"
    },
    "Influenza (Flu)": {
        "symptoms": {
            "primary": ["high fever", "severe body ache", "fatigue", "chills", "fever"],
            "secondary": ["headache", "dry cough", "sore throat", "weakness"],
            "rare": ["vomiting", "diarrhea"]
        },
        "patterns": ["sudden_onset", "seasonal", "winter"],
        "base_confidence": 0.72,
        "urgency": "routine",
        "description": "Viral infection with sudden onset of severe symptoms",
        "distinguishing": "Sudden onset, high fever, severe muscle aches",
        "red_flags": ["breathing difficulty", "chest pain", "confusion"],
        "home_treatment": "Rest, fluids, antivirals within 48 hours if prescribed"
    },
    "COVID-19": {
        "symptoms": {
            "primary": ["fever", "dry cough", "fatigue", "loss of taste", "loss of smell"],
            "secondary": ["sore throat", "headache", "body ache", "breathing difficulty"],
            "rare": ["diarrhea", "rash", "red eyes"]
        },
        "patterns": ["gradual_onset"],
        "base_confidence": 0.65,
        "urgency": "doctor_soon",
        "description": "Coronavirus infection - get tested if suspected",
        "distinguishing": "Loss of taste/smell is highly suggestive",
        "red_flags": ["severe breathing difficulty", "chest pain", "confusion", "bluish lips"],
        "specialist": "Infectious Disease/Pulmonologist"
    },
    "Acute Bronchitis": {
        "symptoms": {
            "primary": ["persistent cough", "mucus production", "chest congestion"],
            "secondary": ["fatigue", "mild fever", "sore throat", "wheezing"],
            "rare": ["chest pain when coughing"]
        },
        "patterns": ["follows_cold", "cough_worsens"],
        "base_confidence": 0.68,
        "urgency": "routine",
        "description": "Inflammation of bronchial tubes, usually viral",
        "distinguishing": "Productive cough lasting 1-3 weeks, follows URI",
        "home_treatment": "Rest, fluids, humidifier, honey, avoid irritants"
    },
    "Pneumonia": {
        "symptoms": {
            "primary": ["high fever", "productive cough", "chest pain", "breathing difficulty"],
            "secondary": ["chills", "fatigue", "rapid breathing", "confusion"],
            "rare": ["coughing blood", "bluish skin"]
        },
        "patterns": ["fever_persistent", "worsening"],
        "base_confidence": 0.60,
        "urgency": "urgent",
        "description": "Lung infection requiring medical attention",
        "distinguishing": "High fever with productive cough and chest pain",
        "red_flags": ["confusion", "bluish skin", "severe breathing difficulty"],
        "specialist": "Pulmonologist"
    },
    "Asthma Exacerbation": {
        "symptoms": {
            "primary": ["wheezing", "shortness of breath", "chest tightness", "asthma"],
            "secondary": ["cough", "difficulty speaking", "rapid breathing", "anxiety"],
            "rare": ["bluish lips"]
        },
        "patterns": ["triggered", "night_worse", "exercise_induced"],
        "base_confidence": 0.72,
        "urgency": "doctor_soon",
        "description": "Airway inflammation causing breathing difficulty",
        "distinguishing": "Wheezing with triggers, responds to bronchodilator",
        "red_flags": ["severe breathlessness", "can't complete sentences", "bluish color"],
        "specialist": "Pulmonologist/Allergist"
    },
    "Allergic Rhinitis": {
        "symptoms": {
            "primary": ["sneezing", "runny nose", "itchy nose", "watery eyes", "allergy", "allergic"],
            "secondary": ["congestion", "itchy throat", "postnasal drip", "fatigue"],
            "rare": ["headache", "ear fullness"]
        },
        "patterns": ["seasonal", "triggered_by_allergens", "recurring"],
        "base_confidence": 0.78,
        "urgency": "self_care",
        "description": "Allergic reaction to airborne allergens",
        "distinguishing": "Clear nasal discharge, itching, triggered by exposure",
        "home_treatment": "Avoid allergens, antihistamines, nasal saline"
    },
    "Sinusitis": {
        "symptoms": {
            "primary": ["facial pain", "nasal congestion", "thick nasal discharge", "sinus"],
            "secondary": ["postnasal drip", "cough", "fatigue", "fever", "headache"],
            "rare": ["toothache", "bad breath", "ear pain"]
        },
        "patterns": ["follows_cold", "pressure_worsens_bending"],
        "base_confidence": 0.70,
        "urgency": "routine",
        "description": "Inflammation of sinuses causing facial pressure",
        "distinguishing": "Facial pain worse when bending forward, thick discharge",
        "specialist": "ENT Specialist"
    },
    
    # ==================== GASTROINTESTINAL CONDITIONS ====================
    "Gastroenteritis (Stomach Flu)": {
        "symptoms": {
            "primary": ["diarrhea", "vomiting", "nausea", "stomach cramps", "stomach pain"],
            "secondary": ["fever", "headache", "muscle aches", "loss of appetite"],
            "rare": ["bloody stool"]
        },
        "patterns": ["sudden_onset", "outbreak_related"],
        "base_confidence": 0.75,
        "urgency": "self_care",
        "description": "Viral stomach infection, usually self-limiting",
        "distinguishing": "Sudden onset of vomiting and diarrhea together",
        "red_flags": ["bloody stool", "severe dehydration", "high fever"],
        "home_treatment": "ORS, clear fluids, BRAT diet, rest"
    },
    "Food Poisoning": {
        "symptoms": {
            "primary": ["nausea", "vomiting", "diarrhea", "stomach cramps"],
            "secondary": ["fever", "weakness", "headache"],
            "rare": ["bloody diarrhea", "muscle paralysis"]
        },
        "patterns": ["within_hours_of_eating", "multiple_affected"],
        "base_confidence": 0.72,
        "urgency": "self_care",
        "description": "Illness from contaminated food, resolves in 24-48 hours",
        "distinguishing": "Onset within hours of eating suspicious food",
        "red_flags": ["bloody stool", "fever >101°F", "severe dehydration"],
        "home_treatment": "Rest, clear fluids, avoid solid food initially"
    },
    "Acid Reflux / GERD": {
        "symptoms": {
            "primary": ["heartburn", "chest burning", "acidity", "regurgitation", "sour taste"],
            "secondary": ["difficulty swallowing", "chronic cough", "hoarseness"],
            "rare": ["chest pain", "asthma-like symptoms"]
        },
        "patterns": ["after_meals", "lying_down_worse", "chronic"],
        "base_confidence": 0.74,
        "urgency": "routine",
        "description": "Stomach acid flowing back into esophagus",
        "distinguishing": "Burning sensation after meals, worse when lying down",
        "home_treatment": "Avoid trigger foods, don't lie down after eating, antacids",
        "specialist": "Gastroenterologist"
    },
    "Gastritis": {
        "symptoms": {
            "primary": ["upper stomach pain", "nausea", "bloating", "indigestion"],
            "secondary": ["loss of appetite", "vomiting", "feeling of fullness"],
            "rare": ["vomiting blood", "black stool"]
        },
        "patterns": ["related_to_food", "stress_related", "nsaid_use"],
        "base_confidence": 0.68,
        "urgency": "routine",
        "description": "Inflammation of stomach lining",
        "distinguishing": "Gnawing upper abdominal pain, worse with empty stomach",
        "red_flags": ["vomiting blood", "black tarry stool"],
        "specialist": "Gastroenterologist"
    },
    "Irritable Bowel Syndrome (IBS)": {
        "symptoms": {
            "primary": ["abdominal pain", "bloating", "gas", "constipation", "diarrhea"],
            "secondary": ["mucus in stool", "cramping", "incomplete evacuation"],
            "rare": ["weight loss"]
        },
        "patterns": ["chronic", "stress_related", "food_related"],
        "base_confidence": 0.62,
        "urgency": "routine",
        "description": "Functional bowel disorder affecting gut motility",
        "distinguishing": "Chronic symptoms, relieved by bowel movement",
        "specialist": "Gastroenterologist"
    },
    "Appendicitis": {
        "symptoms": {
            "primary": ["right lower abdominal pain", "nausea", "loss of appetite"],
            "secondary": ["fever", "vomiting", "abdominal tenderness"],
            "rare": ["diarrhea", "constipation"]
        },
        "patterns": ["pain_migration_to_right", "worsening_rapidly"],
        "base_confidence": 0.55,
        "urgency": "emergency",
        "description": "Inflamed appendix - surgical emergency",
        "distinguishing": "Pain starts around navel, moves to right lower abdomen",
        "red_flags": ["severe worsening pain", "rigid abdomen", "high fever"],
        "specialist": "Surgeon"
    },
    "Constipation": {
        "symptoms": {
            "primary": ["infrequent bowel movements", "hard stool", "straining", "bloating"],
            "secondary": ["abdominal discomfort", "incomplete evacuation"],
            "rare": ["rectal bleeding", "abdominal pain"]
        },
        "patterns": ["chronic", "diet_related", "medication_related"],
        "base_confidence": 0.80,
        "urgency": "self_care",
        "description": "Difficulty or infrequent bowel movements",
        "distinguishing": "Less than 3 bowel movements per week",
        "home_treatment": "Fiber, fluids, exercise, prunes, avoid straining"
    },
    
    # ==================== NEUROLOGICAL CONDITIONS ====================
    "Tension Headache": {
        "symptoms": {
            "primary": ["headache", "pressure sensation", "tight band feeling"],
            "secondary": ["neck stiffness", "scalp tenderness", "mild light sensitivity"],
            "rare": ["nausea"]
        },
        "patterns": ["stress_related", "end_of_day", "computer_use"],
        "base_confidence": 0.78,
        "urgency": "self_care",
        "description": "Most common headache type, related to muscle tension",
        "distinguishing": "Dull, pressing pain on both sides, no nausea",
        "home_treatment": "OTC pain relievers, rest, stress management, massage"
    },
    "Migraine": {
        "symptoms": {
            "primary": ["severe headache", "throbbing pain", "nausea", "light sensitivity", "migraine"],
            "secondary": ["sound sensitivity", "vomiting", "visual aura", "dizziness"],
            "rare": ["numbness", "speech difficulty"]
        },
        "patterns": ["one_sided", "triggered", "with_aura", "family_history"],
        "base_confidence": 0.72,
        "urgency": "routine",
        "description": "Recurring severe headaches with neurological symptoms",
        "distinguishing": "Throbbing one-sided pain with nausea/light sensitivity",
        "red_flags": ["worst headache ever", "fever with headache", "confusion"],
        "specialist": "Neurologist"
    },
    "Vertigo (BPPV)": {
        "symptoms": {
            "primary": ["spinning sensation", "dizziness", "vertigo", "balance problems"],
            "secondary": ["nausea", "vomiting", "lightheadedness"],
            "rare": ["hearing loss", "tinnitus"]
        },
        "patterns": ["position_related", "brief_episodes", "triggered_by_movement"],
        "base_confidence": 0.70,
        "urgency": "routine",
        "description": "Inner ear disorder causing spinning sensation",
        "distinguishing": "Brief spinning episodes triggered by head position changes",
        "specialist": "ENT/Neurologist"
    },
    
    # ==================== MUSCULOSKELETAL CONDITIONS ====================
    "Muscle Strain": {
        "symptoms": {
            "primary": ["localized pain", "muscle stiffness", "limited movement", "muscle pain"],
            "secondary": ["swelling", "bruising", "muscle weakness"],
            "rare": ["popping sensation"]
        },
        "patterns": ["activity_related", "overuse", "sudden_movement"],
        "base_confidence": 0.78,
        "urgency": "self_care",
        "description": "Overstretched or torn muscle fibers",
        "distinguishing": "Pain worsens with movement of affected muscle",
        "home_treatment": "RICE: Rest, Ice, Compression, Elevation"
    },
    "Lower Back Pain": {
        "symptoms": {
            "primary": ["lower back pain", "back pain", "stiffness", "muscle spasm"],
            "secondary": ["limited range of motion", "pain with bending"],
            "rare": ["referred pain to buttocks"]
        },
        "patterns": ["activity_related", "prolonged_sitting", "lifting"],
        "base_confidence": 0.75,
        "urgency": "self_care",
        "description": "Non-specific back pain from muscles/ligaments",
        "distinguishing": "No leg numbness/weakness, no bladder issues",
        "red_flags": ["leg weakness", "numbness", "bladder dysfunction"],
        "home_treatment": "Gentle movement, heat/ice, OTC pain relievers, good posture"
    },
    "Sciatica": {
        "symptoms": {
            "primary": ["back pain radiating to leg", "leg numbness", "shooting pain"],
            "secondary": ["tingling", "weakness in leg", "pain sitting"],
            "rare": ["bladder issues", "foot drop"]
        },
        "patterns": ["radiating_pain", "one_sided", "worse_sitting"],
        "base_confidence": 0.65,
        "urgency": "routine",
        "description": "Nerve compression causing pain from back down leg",
        "distinguishing": "Pain follows path from lower back to leg",
        "red_flags": ["bladder dysfunction", "severe weakness", "numbness in groin"],
        "specialist": "Orthopedic/Neurologist"
    },
    "Arthritis": {
        "symptoms": {
            "primary": ["joint pain", "stiffness", "reduced range of motion", "joint swelling"],
            "secondary": ["swelling", "crepitus", "morning stiffness"],
            "rare": ["joint deformity"]
        },
        "patterns": ["age_related", "worse_with_activity", "better_with_rest"],
        "age_risk": "45+",
        "base_confidence": 0.68,
        "urgency": "routine",
        "description": "Joint inflammation causing pain and stiffness",
        "distinguishing": "Pain worsens with activity, improves with rest",
        "specialist": "Rheumatologist/Orthopedic"
    },
    "Frozen Shoulder": {
        "symptoms": {
            "primary": ["shoulder pain", "limited shoulder movement", "stiffness"],
            "secondary": ["night pain", "difficulty reaching behind"],
            "rare": ["bilateral involvement"]
        },
        "patterns": ["gradual_onset", "three_phases"],
        "age_risk": "40-60",
        "base_confidence": 0.65,
        "urgency": "routine",
        "description": "Adhesive capsulitis limiting shoulder movement",
        "distinguishing": "Progressive limitation of active AND passive movement",
        "specialist": "Orthopedic/Physiotherapist"
    },
    "Carpal Tunnel Syndrome": {
        "symptoms": {
            "primary": ["hand numbness", "tingling in fingers", "wrist pain"],
            "secondary": ["weakness in hand", "dropping objects", "night symptoms"],
            "rare": ["muscle wasting at thumb base"]
        },
        "patterns": ["repetitive_use", "night_worse", "thumb_index_middle_affected"],
        "base_confidence": 0.70,
        "urgency": "routine",
        "description": "Nerve compression at wrist causing hand symptoms",
        "distinguishing": "Numbness in thumb, index, middle fingers, night symptoms",
        "specialist": "Neurologist/Orthopedic"
    },
    
    # ==================== CARDIOVASCULAR CONDITIONS ====================
    "Hypertension": {
        "symptoms": {
            "primary": ["high blood pressure"],
            "secondary": ["headache", "dizziness", "nosebleeds"],
            "rare": ["chest pain", "vision changes", "shortness of breath"]
        },
        "patterns": ["silent", "detected_on_screening"],
        "age_risk": "40+",
        "base_confidence": 0.45,
        "urgency": "doctor_soon",
        "description": "High blood pressure - the silent killer",
        "distinguishing": "Usually no symptoms, detected by measurement",
        "red_flags": ["severe headache", "chest pain", "vision changes"],
        "specialist": "Cardiologist"
    },
    "Angina": {
        "symptoms": {
            "primary": ["chest pressure", "chest tightness", "chest pain"],
            "secondary": ["shortness of breath", "arm pain", "jaw pain", "sweating", "nausea"],
            "rare": ["palpitations"]
        },
        "patterns": ["exertion_related", "relieved_by_rest", "emotional_trigger"],
        "age_risk": "45+",
        "gender_risk": "male",
        "base_confidence": 0.50,
        "urgency": "urgent",
        "description": "Reduced blood flow to heart muscle",
        "distinguishing": "Chest discomfort with exertion, relieved by rest",
        "red_flags": ["pain at rest", "worsening pattern", "lasting >20 min"],
        "specialist": "Cardiologist"
    },
    "Palpitations": {
        "symptoms": {
            "primary": ["heart racing", "skipped beats", "fluttering sensation", "palpitation"],
            "secondary": ["anxiety", "lightheadedness"],
            "rare": ["chest pain", "fainting"]
        },
        "patterns": ["caffeine_related", "stress_related", "brief_episodes"],
        "base_confidence": 0.65,
        "urgency": "routine",
        "description": "Awareness of heartbeat, often benign",
        "distinguishing": "Brief episodes, no fainting, related to triggers",
        "red_flags": ["fainting", "chest pain", "prolonged episodes"],
        "specialist": "Cardiologist"
    },
    
    # ==================== SKIN CONDITIONS ====================
    "Contact Dermatitis": {
        "symptoms": {
            "primary": ["itchy rash", "redness", "swelling", "skin rash"],
            "secondary": ["blisters", "dry skin", "burning sensation", "skin peeling"],
            "rare": ["oozing", "crusting"]
        },
        "patterns": ["localized", "contact_with_irritant"],
        "base_confidence": 0.75,
        "urgency": "self_care",
        "description": "Skin reaction to contact with irritant/allergen",
        "distinguishing": "Rash pattern follows area of contact",
        "home_treatment": "Avoid irritant, hydrocortisone cream, moisturizer"
    },
    "Eczema": {
        "symptoms": {
            "primary": ["itchy skin", "dry patches", "redness", "skin inflammation"],
            "secondary": ["skin thickening", "cracked skin", "oozing"],
            "rare": ["skin infection"]
        },
        "patterns": ["chronic", "flares_and_remissions", "flexural_areas"],
        "base_confidence": 0.70,
        "urgency": "routine",
        "description": "Chronic inflammatory skin condition",
        "distinguishing": "Chronic itchy rash in typical locations (elbows, knees)",
        "specialist": "Dermatologist"
    },
    "Urticaria (Hives)": {
        "symptoms": {
            "primary": ["raised welts", "itching", "hives", "redness"],
            "secondary": ["swelling", "burning sensation"],
            "rare": ["throat swelling", "breathing difficulty"]
        },
        "patterns": ["allergic_trigger", "comes_and_goes"],
        "base_confidence": 0.78,
        "urgency": "self_care",
        "description": "Allergic skin reaction causing itchy welts",
        "distinguishing": "Raised welts that change location, resolve in 24 hours",
        "red_flags": ["throat swelling", "breathing difficulty"],
        "home_treatment": "Antihistamines, cool compress, avoid triggers"
    },
    "Fungal Infection": {
        "symptoms": {
            "primary": ["itchy rash", "ring-shaped rash", "scaling", "skin peeling"],
            "secondary": ["redness", "blisters", "discoloration"],
            "rare": ["nail involvement"]
        },
        "patterns": ["spreading_edge", "central_clearing"],
        "base_confidence": 0.72,
        "urgency": "routine",
        "description": "Fungal infection of skin (ringworm, athlete's foot)",
        "distinguishing": "Ring-shaped rash with clear center, spreading edge",
        "home_treatment": "Antifungal cream, keep area dry, don't share items"
    },
    "Cellulitis": {
        "symptoms": {
            "primary": ["red swollen skin", "warm to touch", "pain", "spreading redness"],
            "secondary": ["fever", "chills", "swollen lymph nodes"],
            "rare": ["blisters", "skin breakdown"]
        },
        "patterns": ["rapid_spreading", "follows_skin_break"],
        "base_confidence": 0.60,
        "urgency": "doctor_soon",
        "description": "Bacterial skin infection requiring antibiotics",
        "distinguishing": "Rapidly spreading redness, warmth, pain, often with fever",
        "red_flags": ["rapid spreading", "high fever", "red streaks"],
        "specialist": "Dermatologist/Emergency"
    },
    "Skin Allergy": {
        "symptoms": {
            "primary": ["rash", "itching", "redness", "allergic reaction"],
            "secondary": ["hives", "swelling", "dry skin"],
            "rare": ["blisters"]
        },
        "patterns": ["triggered", "localized_or_widespread"],
        "base_confidence": 0.75,
        "urgency": "self_care",
        "description": "Allergic reaction on skin causing rash and itching",
        "distinguishing": "Appears after exposure to allergen",
        "home_treatment": "Antihistamines, calamine lotion, avoid trigger"
    },
    
    # ==================== MENTAL HEALTH CONDITIONS ====================
    "Generalized Anxiety": {
        "symptoms": {
            "primary": ["excessive worry", "restlessness", "anxiety", "nervousness"],
            "secondary": ["muscle tension", "sleep problems", "fatigue", "irritability", "stress"],
            "rare": ["panic attacks", "avoidance behavior"]
        },
        "patterns": ["chronic", "multiple_areas_of_worry"],
        "base_confidence": 0.65,
        "urgency": "routine",
        "description": "Persistent excessive worry affecting daily life",
        "distinguishing": "Worry about multiple things, difficulty controlling worry",
        "specialist": "Psychiatrist/Psychologist",
        "home_treatment": "Exercise, relaxation techniques, limit caffeine"
    },
    "Panic Disorder": {
        "symptoms": {
            "primary": ["sudden intense fear", "racing heart", "sweating", "trembling", "panic"],
            "secondary": ["chest pain", "shortness of breath", "dizziness", "fear of dying"],
            "rare": ["numbness", "detachment feeling"]
        },
        "patterns": ["sudden_onset", "peaks_in_minutes", "unpredictable"],
        "base_confidence": 0.62,
        "urgency": "routine",
        "description": "Recurrent unexpected panic attacks",
        "distinguishing": "Sudden surge of intense fear peaking in minutes",
        "red_flags": ["chest pain - rule out cardiac first"],
        "specialist": "Psychiatrist/Psychologist"
    },
    "Depression": {
        "symptoms": {
            "primary": ["persistent sadness", "loss of interest", "fatigue", "depression"],
            "secondary": ["sleep changes", "appetite changes", "concentration problems", "worthlessness", "hopelessness"],
            "rare": ["suicidal thoughts"]
        },
        "patterns": ["persistent_2_weeks", "functional_impairment"],
        "base_confidence": 0.60,
        "urgency": "doctor_soon",
        "description": "Clinical depression requiring professional help",
        "distinguishing": "Symptoms most of the day, nearly every day, for 2+ weeks",
        "red_flags": ["suicidal thoughts", "self-harm", "psychotic symptoms"],
        "specialist": "Psychiatrist/Psychologist"
    },
    "Insomnia": {
        "symptoms": {
            "primary": ["difficulty falling asleep", "difficulty staying asleep", "early waking", "insomnia", "sleep problems"],
            "secondary": ["daytime fatigue", "irritability", "concentration problems"],
            "rare": ["anxiety about sleep"]
        },
        "patterns": ["chronic", "stress_related"],
        "base_confidence": 0.75,
        "urgency": "routine",
        "description": "Persistent sleep difficulties affecting function",
        "distinguishing": "Sleep problems despite adequate opportunity to sleep",
        "specialist": "Sleep Specialist/Psychiatrist",
        "home_treatment": "Sleep hygiene, regular schedule, limit screens"
    },
    
    # ==================== URINARY CONDITIONS ====================
    "Urinary Tract Infection": {
        "symptoms": {
            "primary": ["burning urination", "frequent urination", "urgency", "UTI"],
            "secondary": ["cloudy urine", "pelvic pain", "blood in urine"],
            "rare": ["fever", "back pain"]
        },
        "patterns": ["more_common_in_women", "sexually_active"],
        "gender_risk": "female",
        "base_confidence": 0.75,
        "urgency": "doctor_soon",
        "description": "Bacterial infection of urinary tract",
        "distinguishing": "Burning with urination and frequency",
        "red_flags": ["high fever", "back pain", "vomiting"],
        "specialist": "Urologist"
    },
    "Kidney Stones": {
        "symptoms": {
            "primary": ["severe flank pain", "pain radiating to groin", "blood in urine"],
            "secondary": ["nausea", "vomiting", "frequent urination"],
            "rare": ["fever", "chills"]
        },
        "patterns": ["colicky_pain", "comes_in_waves"],
        "base_confidence": 0.60,
        "urgency": "urgent",
        "description": "Stones in urinary tract causing severe pain",
        "distinguishing": "Severe colicky flank pain radiating to groin",
        "red_flags": ["fever with stone", "unable to urinate"],
        "specialist": "Urologist"
    },
    
    # ==================== ENDOCRINE CONDITIONS ====================
    "Diabetes Symptoms": {
        "symptoms": {
            "primary": ["excessive thirst", "frequent urination", "unexplained weight loss"],
            "secondary": ["fatigue", "blurred vision", "slow healing wounds"],
            "rare": ["numbness in feet", "frequent infections"]
        },
        "patterns": ["gradual_onset", "polyuria_polydipsia"],
        "age_risk": "40+",
        "base_confidence": 0.55,
        "urgency": "doctor_soon",
        "description": "Signs suggesting diabetes - needs blood sugar check",
        "distinguishing": "Classic triad: thirst, urination, weight loss",
        "specialist": "Endocrinologist"
    },
    "Hypothyroidism": {
        "symptoms": {
            "primary": ["fatigue", "weight gain", "cold intolerance", "thyroid"],
            "secondary": ["constipation", "dry skin", "hair loss", "depression", "muscle weakness"],
            "rare": ["hoarse voice", "puffy face"]
        },
        "patterns": ["gradual_onset", "more_common_in_women"],
        "gender_risk": "female",
        "base_confidence": 0.50,
        "urgency": "routine",
        "description": "Underactive thyroid affecting metabolism",
        "distinguishing": "Fatigue, weight gain, cold intolerance together",
        "specialist": "Endocrinologist"
    },
    
    # ==================== ENT CONDITIONS ====================
    "Ear Infection": {
        "symptoms": {
            "primary": ["ear pain", "fever", "hearing difficulty"],
            "secondary": ["ear discharge", "irritability", "sleep difficulty"],
            "rare": ["vertigo", "facial weakness"]
        },
        "patterns": ["follows_cold", "more_common_in_children"],
        "base_confidence": 0.72,
        "urgency": "routine",
        "description": "Middle ear infection, often following cold",
        "distinguishing": "Ear pain with fever, often after cold",
        "specialist": "ENT Specialist"
    },
    "Tonsillitis": {
        "symptoms": {
            "primary": ["sore throat", "difficulty swallowing", "swollen tonsils", "fever"],
            "secondary": ["white patches on tonsils", "neck lymph nodes", "bad breath"],
            "rare": ["muffled voice", "drooling"]
        },
        "patterns": ["acute_onset"],
        "base_confidence": 0.70,
        "urgency": "routine",
        "description": "Inflammation of tonsils, viral or bacterial",
        "distinguishing": "Visible swollen tonsils with sore throat and fever",
        "specialist": "ENT Specialist"
    },
    
    # ==================== EYE CONDITIONS ====================
    "Conjunctivitis": {
        "symptoms": {
            "primary": ["red eyes", "eye discharge", "itching", "tearing"],
            "secondary": ["crusting", "gritty feeling", "swollen eyelids"],
            "rare": ["vision changes"]
        },
        "patterns": ["contagious", "can_be_bilateral"],
        "base_confidence": 0.75,
        "urgency": "routine",
        "description": "Pink eye - inflammation of eye surface",
        "distinguishing": "Red eye with discharge, often starts in one eye",
        "home_treatment": "Warm/cool compress, artificial tears, avoid touching"
    },
    "Dry Eye Syndrome": {
        "symptoms": {
            "primary": ["eye dryness", "burning sensation", "gritty feeling", "dry eyes"],
            "secondary": ["eye fatigue", "sensitivity to light", "blurred vision"],
            "rare": ["excessive tearing"]
        },
        "patterns": ["computer_use", "air_conditioning", "aging"],
        "base_confidence": 0.72,
        "urgency": "self_care",
        "description": "Insufficient tear production or quality",
        "distinguishing": "Symptoms worse with screen use, in dry environments",
        "home_treatment": "Artificial tears, 20-20-20 rule, humidifier"
    },
    
    # ==================== GENERAL/OTHER ====================
    "Dehydration": {
        "symptoms": {
            "primary": ["thirst", "dry mouth", "dark urine", "dehydrated"],
            "secondary": ["fatigue", "dizziness", "headache", "decreased urination"],
            "rare": ["confusion", "rapid heartbeat"]
        },
        "patterns": ["inadequate_fluids", "hot_weather", "illness_related"],
        "base_confidence": 0.72,
        "urgency": "self_care",
        "description": "Insufficient body fluids",
        "distinguishing": "Dark urine, dry mouth, reduced urination",
        "red_flags": ["confusion", "no urination", "fainting"],
        "home_treatment": "Drink water, ORS, avoid caffeine/alcohol"
    },
    "Anemia": {
        "symptoms": {
            "primary": ["fatigue", "weakness", "pale skin", "shortness of breath"],
            "secondary": ["dizziness", "cold hands/feet", "headache", "chest pain"],
            "rare": ["pica", "restless legs"]
        },
        "patterns": ["gradual_onset", "more_common_in_women"],
        "gender_risk": "female",
        "base_confidence": 0.55,
        "urgency": "routine",
        "description": "Low red blood cells or hemoglobin",
        "distinguishing": "Fatigue, pallor, shortness of breath on exertion",
        "specialist": "Hematologist"
    },
    "Vitamin D Deficiency": {
        "symptoms": {
            "primary": ["fatigue", "bone pain", "muscle weakness"],
            "secondary": ["depression", "hair loss", "frequent infections"],
            "rare": ["bone fractures"]
        },
        "patterns": ["indoor_lifestyle", "winter", "dark_skin"],
        "base_confidence": 0.50,
        "urgency": "routine",
        "description": "Insufficient vitamin D levels",
        "distinguishing": "Vague symptoms, fatigue, bone/muscle aches",
        "home_treatment": "Sunlight exposure, vitamin D supplements"
    },
    "General Malaise": {
        "symptoms": {
            "primary": ["feeling unwell", "fatigue", "weakness", "malaise"],
            "secondary": ["mild fever", "loss of appetite", "body aches"],
            "rare": []
        },
        "patterns": ["vague", "prodromal"],
        "base_confidence": 0.40,
        "urgency": "self_care",
        "description": "General feeling of discomfort - more info needed",
        "distinguishing": "Non-specific symptoms, may be early viral illness"
    },
    "Viral Syndrome": {
        "symptoms": {
            "primary": ["fatigue", "body aches", "low fever", "malaise"],
            "secondary": ["headache", "mild sore throat", "loss of appetite"],
            "rare": ["rash"]
        },
        "patterns": ["self_limiting", "seasonal"],
        "base_confidence": 0.55,
        "urgency": "self_care",
        "description": "General viral infection - monitor and rest",
        "distinguishing": "Multiple mild symptoms without clear focus",
        "home_treatment": "Rest, fluids, OTC pain/fever medication"
    }
}


def calculate_condition_score(condition_data: Dict, symptoms_lower: List[str], 
                               vitals: Optional[Dict] = None, age: Optional[int] = None, 
                               gender: Optional[str] = None) -> Tuple[float, List[str], Dict]:
    """
    Calculate comprehensive score for a condition based on:
    - Primary symptoms (weight: 3.0)
    - Secondary symptoms (weight: 1.5)
    - Rare symptoms (weight: 2.0 - highly specific)
    - Risk factors (age, gender)
    - Vital signs
    """
    score = 0.0
    matched_symptoms = []
    score_breakdown = {}
    
    symptoms_text = " ".join(symptoms_lower)
    
    # Score primary symptoms (high weight)
    primary_matches = 0
    for symptom in condition_data["symptoms"].get("primary", []):
        symptom_lower = symptom.lower()
        if any(symptom_lower in s or s in symptom_lower for s in symptoms_lower) or symptom_lower in symptoms_text:
            primary_matches += 1
            matched_symptoms.append(symptom)
    primary_score = primary_matches * 3.0
    score_breakdown["primary"] = primary_score
    
    # Score secondary symptoms (medium weight)
    secondary_matches = 0
    for symptom in condition_data["symptoms"].get("secondary", []):
        symptom_lower = symptom.lower()
        if any(symptom_lower in s or s in symptom_lower for s in symptoms_lower) or symptom_lower in symptoms_text:
            secondary_matches += 1
            matched_symptoms.append(symptom)
    secondary_score = secondary_matches * 1.5
    score_breakdown["secondary"] = secondary_score
    
    # Score rare symptoms (indicates specific condition - bonus)
    rare_matches = 0
    for symptom in condition_data["symptoms"].get("rare", []):
        symptom_lower = symptom.lower()
        if any(symptom_lower in s or s in symptom_lower for s in symptoms_lower) or symptom_lower in symptoms_text:
            rare_matches += 1
            matched_symptoms.append(symptom)
    rare_score = rare_matches * 2.0  # Rare symptoms are highly specific
    score_breakdown["rare"] = rare_score
    
    # Total symptom score
    total_symptom_score = primary_score + secondary_score + rare_score
    score += total_symptom_score
    
    # Calculate match ratio for confidence
    total_primary = len(condition_data["symptoms"].get("primary", []))
    match_ratio = primary_matches / max(total_primary, 1)
    score_breakdown["match_ratio"] = match_ratio
    
    # Risk factor adjustments
    if age and "age_risk" in condition_data:
        age_risk = condition_data["age_risk"]
        if "+" in str(age_risk):
            min_age = int(str(age_risk).replace("+", ""))
            if age >= min_age:
                score += 0.5
                score_breakdown["age_risk"] = 0.5
        elif "-" in str(age_risk):
            range_parts = str(age_risk).split("-")
            if len(range_parts) == 2:
                try:
                    if int(range_parts[0]) <= age <= int(range_parts[1]):
                        score += 0.5
                        score_breakdown["age_risk"] = 0.5
                except ValueError:
                    pass
    
    if gender and "gender_risk" in condition_data:
        if gender.lower() == condition_data["gender_risk"].lower():
            score += 0.3
            score_breakdown["gender_risk"] = 0.3
    
    # Vital signs analysis
    if vitals:
        if "temperature" in vitals:
            temp = vitals.get("temperature", 98.6)
            # Check if condition has fever-related symptoms
            has_fever_symptom = any("fever" in str(s).lower() for s in 
                                    condition_data["symptoms"].get("primary", []) + 
                                    condition_data["symptoms"].get("secondary", []))
            if has_fever_symptom and temp > 100.4:
                score += 0.5
                score_breakdown["vital_temp"] = 0.5
        
        if "heart_rate" in vitals:
            hr = vitals.get("heart_rate", 75)
            has_heart_symptom = any("heart" in str(condition_data).lower() or 
                                   "racing" in str(condition_data).lower() or
                                   "palpitation" in str(condition_data).lower())
            if has_heart_symptom and (hr > 100 or hr < 60):
                score += 0.3
                score_breakdown["vital_hr"] = 0.3
    
    return score, matched_symptoms, score_breakdown


def generate_differential_diagnosis(symptoms: List[str], vitals: Optional[Dict] = None, 
                                     age: Optional[int] = None, gender: Optional[str] = None,
                                     medical_history: Optional[List[str]] = None) -> List[Dict]:
    """
    🏥 ADVANCED DIFFERENTIAL DIAGNOSIS
    Generate comprehensive differential diagnosis with confidence scores.
    NOW USES AI FOR DYNAMIC ANALYSIS - no fixed symptom mappings!
    Returns top 5 most likely conditions.
    """
    if not symptoms:
        return [{
            "condition": "Insufficient Information",
            "confidence": 0.30,
            "urgency": "routine",
            "description": "Please describe your symptoms to receive diagnosis suggestions",
            "distinguishing": "Tell me what you're experiencing"
        }]
    
    # 🧠 TRY AI-POWERED DIAGNOSIS FIRST (Dynamic, no fixed mappings!)
    if HAS_AI_DIAGNOSIS:
        try:
            ai_diagnoses = get_ai_diagnosis_sync(symptoms, age or 30, gender or "unknown")
            if ai_diagnoses and len(ai_diagnoses) >= 2:
                # Format AI results
                formatted = []
                for d in ai_diagnoses:
                    formatted.append({
                        "condition": d.get("condition", "Unknown"),
                        "confidence": d.get("confidence", 50) / 100.0,  # Convert to 0-1
                        "urgency": d.get("urgency", "routine"),
                        "description": d.get("description", ""),
                        "specialist": d.get("specialist"),
                        "matching_symptoms": len(d.get("key_symptoms", [])),
                        "matched_symptoms_list": d.get("key_symptoms", []),
                        "ai_powered": True
                    })
                logger.info(f"🧠 AI Diagnosis returned {len(formatted)} conditions for: {symptoms}")
                return formatted[:5]
        except Exception as e:
            logger.warning(f"AI Diagnosis failed, falling back to rule-based: {e}")
    
    # FALLBACK: Rule-based diagnosis with fixed mappings
    diagnoses = []
    symptoms_lower = [s.lower().strip() for s in symptoms]
    
    for condition_name, condition_data in CONDITION_DATABASE.items():
        score, matched, breakdown = calculate_condition_score(
            condition_data, symptoms_lower, vitals, age, gender
        )
        
        if score > 0 or len(matched) > 0:
            # Calculate final confidence
            base_conf = condition_data.get("base_confidence", 0.50)
            match_ratio = breakdown.get("match_ratio", 0)
            
            # Confidence formula: base * (0.4 + 0.6 * match_ratio) + score adjustment
            confidence = base_conf * (0.4 + 0.6 * match_ratio)
            
            # Boost for multiple primary matches
            primary_score = breakdown.get("primary", 0)
            if primary_score >= 9:  # 3+ primary symptoms
                confidence += 0.20
            elif primary_score >= 6:  # 2+ primary symptoms
                confidence += 0.12
            elif primary_score >= 3:  # 1+ primary symptoms
                confidence += 0.05
            
            # Boost for rare symptom match (highly specific)
            if breakdown.get("rare", 0) > 0:
                confidence += 0.12
            
            # Small boost for secondary matches
            if breakdown.get("secondary", 0) >= 3:
                confidence += 0.05
            
            # Cap confidence
            confidence = min(0.95, max(0.15, confidence))
            
            diagnoses.append({
                "condition": condition_name,
                "confidence": round(confidence, 2),
                "matching_symptoms": len(matched),
                "matched_symptoms_list": list(set(matched))[:5],  # Top 5 unique matched
                "urgency": condition_data.get("urgency", "routine"),
                "description": condition_data.get("description", ""),
                "distinguishing": condition_data.get("distinguishing", ""),
                "home_treatment": condition_data.get("home_treatment"),
                "red_flags": condition_data.get("red_flags", []),
                "specialist": condition_data.get("specialist"),
                "score": round(score, 2)  # For debugging/transparency
            })
    
    # Sort by confidence (primary) and score (secondary)
    diagnoses.sort(key=lambda x: (x["confidence"], x["score"]), reverse=True)
    
    # If no matches, return generic
    if not diagnoses:
        diagnoses = [
            {
                "condition": "General Malaise",
                "confidence": 0.40,
                "urgency": "self_care",
                "description": "General feeling of discomfort - more information needed",
                "distinguishing": "Non-specific symptoms"
            },
            {
                "condition": "Viral Syndrome",
                "confidence": 0.35,
                "urgency": "self_care",
                "description": "Possible viral infection - monitor symptoms",
                "distinguishing": "Multiple mild symptoms"
            }
        ]
    
    # 🧠 ENHANCE WITH ML ENGINE - merge results for better accuracy
    if HAS_ML_ENGINE:
        try:
            ml_results = get_ml_diagnosis(symptoms, age or 30, gender or "unknown")
            
            # Add ML results that aren't already in our diagnoses
            existing_conditions = {d["condition"].lower() for d in diagnoses}
            
            for ml_result in ml_results:
                ml_condition = ml_result["condition"]
                ml_confidence = ml_result["confidence"] / 100.0  # Convert to 0-1 scale
                
                # Check if already exists
                found = False
                for diag in diagnoses:
                    if ml_condition.lower() in diag["condition"].lower() or diag["condition"].lower() in ml_condition.lower():
                        # Merge: boost confidence if ML agrees
                        diag["confidence"] = min(0.95, diag["confidence"] + ml_confidence * 0.3)
                        diag["ml_validated"] = True
                        found = True
                        break
                
                if not found and ml_confidence > 0.2:
                    # Add new diagnosis from ML
                    diagnoses.append({
                        "condition": ml_condition,
                        "confidence": ml_confidence,
                        "urgency": ml_result.get("urgency", "routine"),
                        "description": ml_result.get("description", "ML-detected condition"),
                        "specialist": ml_result.get("specialist"),
                        "matching_symptoms": len(ml_result.get("matching_symptoms", [])),
                        "ml_source": True
                    })
            
            # Re-sort after ML merge
            diagnoses.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            logger.info(f"🧠 ML enhanced diagnoses: {len(diagnoses)} conditions")
            
        except Exception as e:
            logger.warning(f"ML diagnosis enhancement failed: {e}")
    
    # Return top 5 with some diversity
    return diagnoses[:5]


def get_condition_info(condition_name: str) -> Optional[Dict]:
    """Get detailed information about a specific condition"""
    return CONDITION_DATABASE.get(condition_name)


def detect_red_flags(symptoms: List[str], diagnoses: List[Dict]) -> List[str]:
    """Detect any red flags from symptoms and diagnoses"""
    red_flags_found = []
    symptoms_lower = [s.lower() for s in symptoms]
    
    # Check symptom-based red flags
    CRITICAL_SYMPTOMS = [
        "chest pain", "difficulty breathing", "severe breathing difficulty",
        "confusion", "fainting", "unconscious", "bluish lips", "bluish skin",
        "sudden weakness", "facial drooping", "slurred speech", "severe headache",
        "vomiting blood", "blood in stool", "suicidal thoughts", "self harm"
    ]
    
    for symptom in symptoms_lower:
        for critical in CRITICAL_SYMPTOMS:
            if critical in symptom:
                red_flags_found.append(f"⚠️ {critical.title()} detected - seek immediate care")
    
    # Check diagnosis-based red flags
    for diag in diagnoses:
        if diag.get("urgency") == "emergency":
            red_flags_found.append(f"🚨 {diag['condition']} is a potential emergency")
        for rf in diag.get("red_flags", []):
            if any(rf.lower() in s for s in symptoms_lower):
                red_flags_found.append(f"⚠️ Red flag: {rf}")
    
    return list(set(red_flags_found))[:3]  # Top 3 unique red flags
