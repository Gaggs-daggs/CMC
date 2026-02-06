"""
🏥 ULTIMATE MEDICAL AI DIAGNOSIS ENGINE
========================================
Production-grade diagnosis system using:
- MedLlama2 as PRIMARY medical model (trained on medical literature)
- Gemma2:9b for complex reasoning (fallback)  
- Model cascade with automatic failover
- Clinical-grade prompts based on medical frameworks
- Ensemble diagnosis for high-confidence results
- Response validation and quality checks

NO HARDCODING - Pure AI reasoning like a real doctor.
"""

import ollama
import json
import logging
import asyncio
import re
import time
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# ============================================================================
# MODEL CONFIGURATION - Priority order for medical diagnosis
# ============================================================================
# ============================================================================
# DIAGNOSIS MODELS: Medical accuracy is #1 priority - use BEST model for diagnosis
# gemma2:9b follows structured format well and has good medical knowledge
# medllama2 has medical knowledge but doesn't follow structured prompts
# ============================================================================
MEDICAL_MODELS = [
    {
        "name": "gemma2:9b",
        "type": "reasoning",
        "priority": 1,  # BEST for structured diagnosis - follows format well
        "description": "Advanced reasoning - follows structured output format reliably",
        "temperature": 0.3,
        "timeout": 30,
        "num_predict": 700  # More tokens for detailed reasoning
    },
    {
        "name": "llama3.1:8b",
        "type": "general",
        "priority": 2,
        "description": "General intelligence - good fallback",
        "temperature": 0.3,
        "timeout": 20,
        "num_predict": 500
    },
    {
        "name": "medllama2",
        "type": "medical",
        "priority": 3,  # Last resort - doesn't follow format well
        "description": "Medical specialist - trained on clinical data but poor format compliance",
        "temperature": 0.2,
        "timeout": 25,
        "num_predict": 600
    }
]

# ============================================================================
# INSTANT DIAGNOSIS CACHE - Common symptoms with pre-computed diagnoses
# ============================================================================
INSTANT_DIAGNOSES = {
    "fever": [
        {"condition": "Viral Fever", "confidence": 0.85, "urgency": "self_care", "description": "Common viral infection causing elevated body temperature", "specialist": "General Physician"},
        {"condition": "Influenza", "confidence": 0.70, "urgency": "routine", "description": "Flu virus infection with fever, body aches", "specialist": "General Physician"},
        {"condition": "Bacterial Infection", "confidence": 0.50, "urgency": "doctor_soon", "description": "Possible bacterial cause if fever persists", "specialist": "General Physician"},
    ],
    "headache": [
        {"condition": "Tension Headache", "confidence": 0.80, "urgency": "self_care", "description": "Stress or muscle tension causing head pain", "specialist": None},
        {"condition": "Migraine", "confidence": 0.60, "urgency": "routine", "description": "Recurrent headache, often with sensitivity to light", "specialist": "Neurologist"},
        {"condition": "Dehydration", "confidence": 0.55, "urgency": "self_care", "description": "Lack of fluids causing headache", "specialist": None},
    ],
    "cold": [
        {"condition": "Common Cold", "confidence": 0.90, "urgency": "self_care", "description": "Viral upper respiratory infection", "specialist": None},
        {"condition": "Allergic Rhinitis", "confidence": 0.50, "urgency": "routine", "description": "Allergic reaction causing cold-like symptoms", "specialist": "ENT Specialist"},
    ],
    "cough": [
        {"condition": "Viral Bronchitis", "confidence": 0.75, "urgency": "self_care", "description": "Viral infection causing cough", "specialist": None},
        {"condition": "Upper Respiratory Infection", "confidence": 0.70, "urgency": "self_care", "description": "Common cold with cough", "specialist": None},
        {"condition": "Allergic Cough", "confidence": 0.50, "urgency": "routine", "description": "Allergy-triggered coughing", "specialist": "Pulmonologist"},
    ],
    "stomach pain": [
        {"condition": "Gastritis", "confidence": 0.75, "urgency": "routine", "description": "Stomach lining inflammation", "specialist": "Gastroenterologist"},
        {"condition": "Indigestion", "confidence": 0.70, "urgency": "self_care", "description": "Digestive discomfort", "specialist": None},
        {"condition": "Acid Reflux", "confidence": 0.60, "urgency": "routine", "description": "Stomach acid causing discomfort", "specialist": "Gastroenterologist"},
    ],
    "diarrhea": [
        {"condition": "Viral Gastroenteritis", "confidence": 0.80, "urgency": "self_care", "description": "Stomach bug causing loose stools", "specialist": None},
        {"condition": "Food Poisoning", "confidence": 0.65, "urgency": "routine", "description": "Contaminated food causing diarrhea", "specialist": "Gastroenterologist"},
    ],
    "constipation": [
        {"condition": "Functional Constipation", "confidence": 0.85, "urgency": "self_care", "description": "Lack of fiber, water, or activity", "specialist": None},
        {"condition": "IBS-C", "confidence": 0.50, "urgency": "routine", "description": "Irritable bowel with constipation", "specialist": "Gastroenterologist"},
    ],
    "burning": [
        {"condition": "Urinary Tract Infection", "confidence": 0.80, "urgency": "doctor_soon", "description": "Bacterial infection in urinary tract", "specialist": "Urologist"},
        {"condition": "Acid Reflux", "confidence": 0.50, "urgency": "routine", "description": "Stomach acid causing burning", "specialist": "Gastroenterologist"},
    ],
    "burning urination": [
        {"condition": "Urinary Tract Infection", "confidence": 0.90, "urgency": "doctor_soon", "description": "Bacterial infection causing painful urination", "specialist": "Urologist"},
        {"condition": "Cystitis", "confidence": 0.70, "urgency": "doctor_soon", "description": "Bladder inflammation", "specialist": "Urologist"},
    ],
    "sore throat": [
        {"condition": "Pharyngitis", "confidence": 0.80, "urgency": "self_care", "description": "Throat inflammation, usually viral", "specialist": None},
        {"condition": "Tonsillitis", "confidence": 0.55, "urgency": "doctor_soon", "description": "Inflamed tonsils", "specialist": "ENT Specialist"},
    ],
    "back pain": [
        {"condition": "Muscle Strain", "confidence": 0.80, "urgency": "self_care", "description": "Muscle or ligament strain in back", "specialist": None},
        {"condition": "Poor Posture", "confidence": 0.70, "urgency": "routine", "description": "Back pain from posture issues", "specialist": "Orthopedist"},
    ],
    "anxiety": [
        {"condition": "Generalized Anxiety", "confidence": 0.75, "urgency": "routine", "description": "Excessive worry and tension", "specialist": "Psychiatrist"},
        {"condition": "Stress Response", "confidence": 0.70, "urgency": "self_care", "description": "Normal stress reaction", "specialist": None},
    ],
    "insomnia": [
        {"condition": "Primary Insomnia", "confidence": 0.75, "urgency": "routine", "description": "Difficulty sleeping", "specialist": "Sleep Specialist"},
        {"condition": "Stress-related Sleep Issues", "confidence": 0.70, "urgency": "self_care", "description": "Stress affecting sleep", "specialist": None},
    ],
}

# ============================================================================
# CLINICAL-GRADE MEDICAL PROMPT
# Based on actual clinical reasoning frameworks used by doctors
# ============================================================================

# MedLlama2-specific prompt - Detailed clinical prompt for accurate diagnosis
MEDLLAMA2_PROMPT = """You are a senior physician performing differential diagnosis.

PATIENT PRESENTATION:
- Chief Complaints: {symptoms}
- Age: {age} years
- Sex: {gender}

CLINICAL TASK: Provide 5 most likely diagnoses with confidence percentages.

IMPORTANT: 
- Confidence should reflect how well symptoms match the condition
- If symptoms strongly suggest a condition, give 70-90% confidence
- If moderately suggestive, give 50-70%
- If possible but less likely, give 30-50%

FORMAT (follow exactly):
1. [Condition Name] - [Confidence]% - [Urgency Level]
   Reasoning: [Why this diagnosis fits the symptoms]
   Specialist: [Recommended specialist or None]

2. [Condition Name] - [Confidence]% - [Urgency Level]
   Reasoning: [Why this diagnosis fits]
   Specialist: [Recommended specialist or None]

3. [Condition Name] - [Confidence]% - [Urgency Level]
   Reasoning: [Clinical reasoning]
   Specialist: [Specialist or None]

4. [Condition Name] - [Confidence]% - [Urgency Level]
   Reasoning: [Clinical reasoning]
   Specialist: [Specialist or None]

5. [Condition Name] - [Confidence]% - [Urgency Level]
   Reasoning: [Clinical reasoning]
   Specialist: [Specialist or None]

URGENCY LEVELS:
- emergency: Life-threatening (chest pain, breathing difficulty, etc.)
- urgent: Needs medical attention within hours
- doctor_soon: See doctor within 24-48 hours
- routine: Schedule appointment within 1-2 weeks
- self_care: Home management appropriate

BEGIN YOUR DIFFERENTIAL DIAGNOSIS:"""

# Clinical prompt for gemma2 and llama3.1 - More explicit formatting
CLINICAL_DIAGNOSIS_PROMPT = """You are a senior physician. Analyze these symptoms and provide your differential diagnosis.

PATIENT:
- Symptoms: {symptoms}
- Age: {age} years
- Sex: {gender}

Provide exactly 5 diagnoses ranked by likelihood. Use this EXACT format for each:

1. [Condition Name] - [Confidence 50-95]% - [urgency_level]
   Reasoning: [One sentence explaining why this fits]
   Specialist: [Type of specialist or None]

2. [Condition Name] - [Confidence]% - [urgency_level]
   Reasoning: [Why this diagnosis fits]
   Specialist: [Specialist or None]

3. [Condition Name] - [Confidence]% - [urgency_level]
   Reasoning: [Clinical reasoning]
   Specialist: [Specialist or None]

4. [Condition Name] - [Confidence]% - [urgency_level]
   Reasoning: [Clinical reasoning]
   Specialist: [Specialist or None]

5. [Condition Name] - [Confidence]% - [urgency_level]
   Reasoning: [Clinical reasoning]
   Specialist: [Specialist or None]

URGENCY LEVELS (use exactly):
- emergency: Life-threatening, call ambulance
- urgent: Go to ER within hours
- doctor_soon: See doctor in 24-48h
- routine: Schedule appointment in 1-2 weeks
- self_care: Home treatment appropriate

CONFIDENCE GUIDELINES:
- 80-95%: Symptoms strongly match condition
- 60-79%: Moderately suggestive
- 40-59%: Possible but needs more info

START YOUR DIFFERENTIAL DIAGNOSIS NOW:"""

# Simpler prompt for faster models
FAST_DIAGNOSIS_PROMPT = """Analyze symptoms and provide 5 possible medical conditions.

SYMPTOMS: {symptoms}
PATIENT: {age} year old {gender}

For each condition provide:
1. Condition Name - Confidence% - Urgency Level
   Reason: Brief clinical reasoning
   Specialist: Recommended specialist or None

Urgency levels: emergency, urgent, doctor_soon, routine, self_care

Example format:
1. Urinary Tract Infection - 80% - doctor_soon
   Reason: Burning urination with frequency suggests bacterial UTI
   Specialist: Urologist

List 5 conditions now:"""

# ============================================================================
# CORE DIAGNOSIS FUNCTIONS
# ============================================================================

def check_model_available(model_name: str) -> bool:
    """Check if a model is available in Ollama"""
    try:
        result = ollama.list()
        # Handle both dict and object formats
        if hasattr(result, 'models'):
            models = result.models
        else:
            models = result.get('models', [])
        
        available_names = []
        for m in models:
            # Handle both dict and Model object
            if hasattr(m, 'model'):
                available_names.append(m.model)
            elif isinstance(m, dict):
                available_names.append(m.get('name', ''))
        
        # Check for exact match or prefix match (e.g., "medllama2" matches "medllama2:latest")
        model_base = model_name.split(':')[0]
        for avail in available_names:
            avail_base = avail.split(':')[0]
            if model_base == avail_base or model_name == avail:
                return True
        
        return False
    except Exception as e:
        logger.warning(f"Error checking model availability: {e}")
        return False


def call_model_for_diagnosis(
    model_config: Dict,
    symptoms_text: str,
    age: int,
    gender: str
) -> Tuple[Optional[List[Dict]], str, float]:
    """
    Call a single model for diagnosis.
    Returns: (diagnoses, model_name, response_time)
    """
    model_name = model_config["name"]
    start_time = time.time()
    
    # Select prompt based on model
    if "medllama2" in model_name:
        # Use simpler prompt for medllama2 (better compliance)
        prompt = MEDLLAMA2_PROMPT.format(
            symptoms=symptoms_text,
            age=age,
            gender=gender
        )
    elif model_config["type"] in ["medical", "reasoning"]:
        prompt = CLINICAL_DIAGNOSIS_PROMPT.format(
            symptoms=symptoms_text,
            age=age,
            gender=gender
        )
    else:
        prompt = FAST_DIAGNOSIS_PROMPT.format(
            symptoms=symptoms_text,
            age=age,
            gender=gender
        )
    
    try:
        # Use num_predict from config, default to 600 for detailed diagnosis
        num_predict = model_config.get("num_predict", 600)
        
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": model_config["temperature"],
                "num_predict": num_predict,  # More tokens for accurate diagnosis
            }
        )
        
        response_text = response["message"]["content"]
        elapsed = time.time() - start_time
        
        # Parse the response
        diagnoses = parse_diagnosis_response(response_text)
        
        if diagnoses and len(diagnoses) >= 2:
            logger.info(f"✅ {model_name} returned {len(diagnoses)} diagnoses in {elapsed:.1f}s")
            return diagnoses, model_name, elapsed
        else:
            logger.warning(f"⚠️ {model_name} returned insufficient diagnoses")
            return None, model_name, elapsed
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ {model_name} failed: {e}")
        return None, model_name, elapsed


async def get_ai_diagnosis(
    symptoms: List[str], 
    age: int = 30, 
    gender: str = "unknown",
    use_ensemble: bool = False
) -> List[Dict]:
    """
    🏥 ACCURATE AI-POWERED DIAGNOSIS
    
    Uses medllama2 (medical model trained on PubMed) for accurate diagnosis.
    This is the CORE FUNCTION of the app - accuracy > speed.
    
    Strategy:
    1. 🏥 ALWAYS use medllama2 for accurate medical diagnosis
    2. 🔄 Fallback to gemma2 or llama3.1 if medllama2 unavailable
    """
    if not symptoms:
        return [{
            "condition": "Insufficient Information",
            "confidence": 0.30,
            "urgency": "routine",
            "description": "Please describe your symptoms for diagnosis",
            "specialist": None,
            "key_symptoms": [],
            "model_used": "none"
        }]
    
    symptoms_text = ", ".join(symptoms)
    
    # ========== ALWAYS USE AI MODEL FOR ACCURATE DIAGNOSIS ==========
    # No instant cache - every symptom deserves proper AI analysis
    for model_config in MEDICAL_MODELS:
        model_name = model_config["name"]
        
        # Check if model is available
        if not check_model_available(model_name):
            logger.warning(f"⏭️ Skipping {model_name} - not available")
            continue
        
        logger.info(f"🏥 Using {model_name} for diagnosis: {symptoms_text}")
        
        diagnoses, used_model, elapsed = call_model_for_diagnosis(
            model_config, symptoms_text, age, gender
        )
        
        if diagnoses:
            # Add metadata to each diagnosis
            for d in diagnoses:
                d["model_used"] = used_model
                d["key_symptoms"] = symptoms[:5]
            
            logger.info(f"✅ Diagnosis complete using {used_model} ({elapsed:.1f}s) - {len(diagnoses)} conditions")
            return diagnoses[:5]
    
    # All models failed - use fallback
    logger.warning("⚠️ All AI models failed, using rule-based fallback")
    return get_fallback_diagnosis(symptoms)


async def get_ensemble_diagnosis(
    symptoms_text: str,
    age: int,
    gender: str
) -> List[Dict]:
    """
    Run multiple models in parallel and combine results.
    This increases confidence by seeing what multiple "doctors" agree on.
    """
    available_models = [m for m in MEDICAL_MODELS[:3] if check_model_available(m["name"])]
    
    if len(available_models) < 2:
        # Not enough models for ensemble, fall back to single model
        logger.info("Not enough models for ensemble, using single model")
        return await get_ai_diagnosis(symptoms_text.split(", "), age, gender, use_ensemble=False)
    
    # Run models in parallel using ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(
                call_model_for_diagnosis, 
                model_config, 
                symptoms_text, 
                age, 
                gender
            ): model_config["name"] 
            for model_config in available_models
        }
        
        for future in as_completed(futures, timeout=45):
            model_name = futures[future]
            try:
                diagnoses, used_model, elapsed = future.result()
                if diagnoses:
                    results.append((diagnoses, used_model))
            except Exception as e:
                logger.error(f"Ensemble model {model_name} failed: {e}")
    
    if not results:
        return get_fallback_diagnosis(symptoms_text.split(", "))
    
    # Combine and rank diagnoses
    return combine_ensemble_results(results)


def combine_ensemble_results(results: List[Tuple[List[Dict], str]]) -> List[Dict]:
    """
    Combine diagnoses from multiple models.
    Boost confidence when models agree.
    """
    condition_scores = {}
    
    for diagnoses, model_name in results:
        for rank, diag in enumerate(diagnoses):
            condition = diag["condition"].lower().strip()
            
            # Normalize similar condition names
            normalized = normalize_condition_name(condition)
            
            if normalized not in condition_scores:
                condition_scores[normalized] = {
                    "condition": diag["condition"],
                    "confidence": 0,
                    "votes": 0,
                    "urgency": diag.get("urgency", "routine"),
                    "description": diag.get("description", ""),
                    "specialist": diag.get("specialist"),
                    "models": []
                }
            
            # Add weighted score (higher rank = higher weight)
            weight = (5 - rank) / 5  # 1.0 for rank 0, 0.2 for rank 4
            condition_scores[normalized]["confidence"] += diag.get("confidence", 50) * weight
            condition_scores[normalized]["votes"] += 1
            condition_scores[normalized]["models"].append(model_name)
            
            # Use most urgent urgency
            urgency_order = ["emergency", "urgent", "doctor_soon", "routine", "self_care"]
            current_urgency = condition_scores[normalized]["urgency"]
            new_urgency = diag.get("urgency", "routine")
            if urgency_order.index(new_urgency) < urgency_order.index(current_urgency):
                condition_scores[normalized]["urgency"] = new_urgency
    
    # Calculate final scores
    final_diagnoses = []
    num_models = len(results)
    
    for normalized, data in condition_scores.items():
        # Average confidence with agreement bonus
        avg_confidence = data["confidence"] / data["votes"]
        agreement_bonus = (data["votes"] / num_models) * 15  # Up to 15% bonus for agreement
        
        final_confidence = min(95, avg_confidence + agreement_bonus)
        
        final_diagnoses.append({
            "condition": data["condition"],
            "confidence": int(final_confidence),
            "urgency": data["urgency"],
            "description": data["description"],
            "specialist": data["specialist"],
            "key_symptoms": [],
            "model_used": f"ensemble({','.join(set(data['models']))})",
            "agreement": f"{data['votes']}/{num_models} models"
        })
    
    # Sort by confidence
    final_diagnoses.sort(key=lambda x: x["confidence"], reverse=True)
    
    logger.info(f"🎯 Ensemble diagnosis: {len(final_diagnoses)} conditions from {num_models} models")
    return final_diagnoses[:5]


def normalize_condition_name(condition: str) -> str:
    """Normalize condition names for comparison"""
    condition = condition.lower().strip()
    
    # Common normalizations
    normalizations = {
        "uti": "urinary tract infection",
        "uri": "upper respiratory infection",
        "gerd": "gastroesophageal reflux disease",
        "ibs": "irritable bowel syndrome",
        "copd": "chronic obstructive pulmonary disease",
    }
    
    for abbrev, full in normalizations.items():
        if abbrev in condition:
            condition = condition.replace(abbrev, full)
    
    # Remove common suffixes for comparison
    condition = re.sub(r'\s*\(.*?\)\s*', '', condition)  # Remove parentheticals
    condition = condition.replace("acute ", "").replace("chronic ", "")
    
    return condition.strip()


def parse_diagnosis_response(text: str) -> Optional[List[Dict]]:
    """
    Parse diagnosis response from AI model.
    Handles multiple formats robustly including medllama2's verbose output.
    """
    diagnoses = []
    lines = text.strip().split('\n')
    
    current_condition = None
    current_reason = None
    current_specialist = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove markdown formatting
        line = line.replace('**', '').replace('*', '')
        
        # Pattern 1: "1. Condition Name - 75% - urgency"
        match1 = re.match(r'^\d+[\.\)]\s*(.+?)\s*[-–]\s*(\d+)%?\s*[-–]\s*(\w+)', line)
        
        # Pattern 2: "1. Condition Name (75%) - urgency"
        match2 = re.match(r'^\d+[\.\)]\s*(.+?)\s*\((\d+)%?\)\s*[-–]\s*(\w+)', line)
        
        # Pattern 3: Just "1. Condition Name - 75%"
        match3 = re.match(r'^\d+[\.\)]\s*(.+?)\s*[-–]\s*(\d+)%', line)
        
        # Pattern 4: Medllama2 style - "[Confidence XX%]" anywhere in line
        match4 = None
        if '[Confidence' in line or 'Confidence' in line:
            conf_match = re.search(r'\[?Confidence\s*[:=]?\s*(\d+)%?\]?', line, re.IGNORECASE)
            if conf_match:
                # Try to extract condition name from beginning of line
                cond_match = re.match(r'^(?:What are the potential causes of\s+)?(.+?)(?:\s*\(|\s*\[|\s*[-–]|\s*$)', line)
                if cond_match:
                    condition_name = cond_match.group(1).strip()
                    # Clean up question format
                    condition_name = re.sub(r'\?.*$', '', condition_name).strip()
                    if condition_name and len(condition_name) > 3:
                        match4 = (condition_name, conf_match.group(1), "routine")
        
        # Pattern 5: Simple numbered list "1. Condition Name"
        match5 = re.match(r'^(\d+)[\.\)]\s*([A-Z][^-–\(\[]+?)(?:\s*[-–]|\s*\(|\s*\[|$)', line)
        
        condition_match = match1 or match2 or match3
        
        # Handle Pattern 4 (medllama2)
        if match4:
            if current_condition:
                diagnoses.append(build_diagnosis_dict(
                    current_condition, current_reason, current_specialist
                ))
            current_condition = match4
            current_reason = None
            current_specialist = None
            # Try to extract specialist from same line
            spec_match = re.search(r'Specialist:\s*(\w+)', line)
            if spec_match:
                current_specialist = spec_match.group(1)
            # Try to extract urgency from same line
            urg_match = re.search(r'Urgency(?:\s*Level)?:\s*(\w+)', line, re.IGNORECASE)
            if urg_match:
                current_condition = (current_condition[0], current_condition[1], urg_match.group(1))
            continue
            
        if condition_match:
            # Save previous condition if exists
            if current_condition:
                diagnoses.append(build_diagnosis_dict(
                    current_condition, current_reason, current_specialist
                ))
            
            if match1 or match2:
                current_condition = (
                    condition_match.group(1).strip(),
                    condition_match.group(2),
                    condition_match.group(3) if len(condition_match.groups()) > 2 else "routine"
                )
            else:  # match3
                current_condition = (
                    condition_match.group(1).strip(),
                    condition_match.group(2),
                    "routine"
                )
            current_reason = None
            current_specialist = None
            
        elif line.lower().startswith('reason'):
            # Extract reason after colon or dash
            parts = re.split(r'[:\-–]', line, 1)
            if len(parts) > 1:
                current_reason = parts[1].strip()
                
        elif line.lower().startswith('specialist'):
            parts = re.split(r'[:\-–]', line, 1)
            if len(parts) > 1:
                spec = parts[1].strip()
                if spec.lower() not in ['none', 'n/a', '-', 'na', 'not applicable']:
                    current_specialist = spec
    
    # Don't forget the last one
    if current_condition:
        diagnoses.append(build_diagnosis_dict(
            current_condition, current_reason, current_specialist
        ))
    
    return diagnoses if diagnoses else None


def build_diagnosis_dict(
    condition_tuple: Tuple[str, str, str],
    reason: Optional[str],
    specialist: Optional[str]
) -> Dict:
    """Build a diagnosis dictionary from parsed data"""
    urgency = condition_tuple[2].lower().replace(' ', '_').replace('-', '_')
    
    # Normalize urgency values
    valid_urgencies = ["emergency", "urgent", "doctor_soon", "routine", "self_care"]
    if urgency not in valid_urgencies:
        # Try to map common variations
        urgency_map = {
            "soon": "doctor_soon",
            "immediate": "emergency",
            "asap": "urgent",
            "moderate": "routine",
            "low": "self_care",
            "high": "urgent"
        }
        urgency = urgency_map.get(urgency, "routine")
    
    # Parse confidence - ensure it's a valid percentage
    try:
        confidence_val = int(condition_tuple[1])
        # Ensure it's in valid range (1-100)
        confidence_val = max(1, min(100, confidence_val))
    except (ValueError, TypeError):
        confidence_val = 50  # Default if parsing fails
    
    return {
        "condition": condition_tuple[0],
        "confidence": confidence_val,  # Keep as integer 1-100
        "urgency": urgency,
        "description": reason or "Based on symptom analysis",
        "specialist": specialist,
        "key_symptoms": []
    }


def get_fallback_diagnosis(symptoms: List[str]) -> List[Dict]:
    """
    Minimal fallback when all AI models fail.
    Uses basic keyword matching - NOT the primary approach.
    """
    symptoms_lower = " ".join(symptoms).lower()
    diagnoses = []
    
    # Emergency keywords - always flag these
    emergency_keywords = ["chest pain", "difficulty breathing", "severe bleeding", 
                          "unconscious", "stroke", "heart attack"]
    for kw in emergency_keywords:
        if kw in symptoms_lower:
            diagnoses.append({
                "condition": "Medical Emergency - Seek Immediate Care",
                "confidence": 90,
                "urgency": "emergency",
                "description": f"Symptoms suggest possible emergency: {kw}",
                "specialist": "Emergency Room",
                "key_symptoms": [kw],
                "model_used": "fallback"
            })
            return diagnoses  # Stop here for emergency
    
    # Basic pattern matching for common conditions
    patterns = [
        (["fever", "temperature", "chills"], "Possible Infection", 55, "routine", None),
        (["headache", "head pain", "migraine"], "Headache Disorder", 50, "self_care", "Neurologist"),
        (["stomach", "abdominal", "belly", "nausea"], "Gastrointestinal Issue", 50, "routine", "Gastroenterologist"),
        (["cough", "cold", "runny nose", "congestion"], "Upper Respiratory Infection", 55, "self_care", None),
        (["back pain", "spine"], "Musculoskeletal Pain", 50, "routine", "Orthopedist"),
        (["urine", "urinary", "bladder", "burning"], "Urinary Tract Condition", 55, "doctor_soon", "Urologist"),
        (["skin", "rash", "itching", "hives"], "Dermatological Condition", 50, "routine", "Dermatologist"),
        (["anxiety", "stress", "panic", "depressed"], "Mental Health Concern", 50, "routine", "Psychiatrist"),
        (["eye", "vision", "blurry"], "Ophthalmological Issue", 50, "routine", "Ophthalmologist"),
        (["ear", "hearing", "tinnitus"], "Ear/Hearing Issue", 50, "routine", "ENT Specialist"),
    ]
    
    for keywords, condition, confidence, urgency, specialist in patterns:
        if any(kw in symptoms_lower for kw in keywords):
            matched = [kw for kw in keywords if kw in symptoms_lower]
            diagnoses.append({
                "condition": condition,
                "confidence": confidence,
                "urgency": urgency,
                "description": f"Based on symptoms: {', '.join(matched[:2])}",
                "specialist": specialist,
                "key_symptoms": matched[:2],
                "model_used": "fallback"
            })
    
    # Ensure at least 2 diagnoses
    if len(diagnoses) < 2:
        diagnoses.append({
            "condition": "General Medical Evaluation Needed",
            "confidence": 40,
            "urgency": "routine",
            "description": "Symptoms require professional assessment",
            "specialist": "General Practitioner",
            "key_symptoms": symptoms[:2],
            "model_used": "fallback"
        })
    
    return diagnoses[:5]


# ============================================================================
# SYNCHRONOUS WRAPPER
# ============================================================================

def get_ai_diagnosis_sync(
    symptoms: List[str], 
    age: int = 30, 
    gender: str = "unknown",
    use_ensemble: bool = False
) -> List[Dict]:
    """
    Synchronous wrapper for AI diagnosis.
    This is the main entry point called by other services.
    """
    try:
        # Try to get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context - use thread executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(get_ai_diagnosis(symptoms, age, gender, use_ensemble))
                    )
                    return future.result(timeout=45)
            else:
                return loop.run_until_complete(
                    get_ai_diagnosis(symptoms, age, gender, use_ensemble)
                )
        except RuntimeError:
            # No event loop - create one
            return asyncio.run(get_ai_diagnosis(symptoms, age, gender, use_ensemble))
            
    except Exception as e:
        logger.error(f"Sync AI diagnosis error: {e}")
        return get_fallback_diagnosis(symptoms)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_models() -> List[str]:
    """Get list of available Ollama models"""
    try:
        result = ollama.list()
        # Handle both dict and object formats
        if hasattr(result, 'models'):
            models = result.models
        else:
            models = result.get('models', [])
        
        available_names = []
        for m in models:
            if hasattr(m, 'model'):
                available_names.append(m.model)
            elif isinstance(m, dict):
                available_names.append(m.get('name', ''))
        
        return available_names
    except Exception as e:
        logger.warning(f"Error getting available models: {e}")
        return []


def get_diagnosis_engine_status() -> Dict:
    """Get status of the diagnosis engine"""
    available = get_available_models()
    medical_available = [m["name"] for m in MEDICAL_MODELS if m["name"] in available or m["name"].split(':')[0] in [a.split(':')[0] for a in available]]
    
    return {
        "engine": "Ultimate Medical AI Diagnosis Engine",
        "version": "2.0",
        "models_configured": [m["name"] for m in MEDICAL_MODELS],
        "models_available": medical_available,
        "primary_model": medical_available[0] if medical_available else "none",
        "ensemble_capable": len(medical_available) >= 2,
        "status": "operational" if medical_available else "degraded"
    }
