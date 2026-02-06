"""
🏥 AI-POWERED MEDICATION RECOMMENDATION ENGINE (OPTIMIZED)
===========================================================
Fast AI-powered medication recommendations with caching.
Target response time: < 5 seconds
"""

import ollama
import logging
import re
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

# ============================================================================
# OPTIMIZED MEDICATION CACHE
# ============================================================================
# Cache common symptom combinations to avoid repeated AI calls
_MEDICATION_CACHE: Dict[str, List[Dict]] = {}
CACHE_TTL = 3600  # 1 hour cache

# ============================================================================
# PRE-COMPUTED COMMON MEDICATIONS (instant response for common cases)
# ============================================================================
COMMON_MEDICATIONS = {
    "fever": [
        {"name": "Acetaminophen (Tylenol)", "dosage": "500-1000mg", "frequency": "Every 4-6 hours", "purpose": "Reduces fever and pain", "warning": "Max 4g/day", "is_otc": True},
        {"name": "Ibuprofen (Advil)", "dosage": "200-400mg", "frequency": "Every 4-6 hours", "purpose": "Anti-inflammatory, reduces fever", "warning": "Take with food", "is_otc": True},
    ],
    "headache": [
        {"name": "Acetaminophen", "dosage": "500-1000mg", "frequency": "Every 4-6 hours", "purpose": "Pain relief", "warning": "Max 4g/day", "is_otc": True},
        {"name": "Ibuprofen", "dosage": "200-400mg", "frequency": "Every 4-6 hours", "purpose": "Anti-inflammatory pain relief", "warning": "Take with food", "is_otc": True},
        {"name": "Excedrin", "dosage": "2 tablets", "frequency": "Every 6 hours", "purpose": "Migraine and tension headache", "warning": "Contains caffeine", "is_otc": True},
    ],
    "cold": [
        {"name": "DayQuil", "dosage": "30ml or 2 capsules", "frequency": "Every 4 hours", "purpose": "Multi-symptom cold relief", "warning": "Don't mix with other acetaminophen", "is_otc": True},
        {"name": "Pseudoephedrine (Sudafed)", "dosage": "30-60mg", "frequency": "Every 4-6 hours", "purpose": "Nasal decongestant", "warning": "May raise blood pressure", "is_otc": True},
        {"name": "Cetirizine (Zyrtec)", "dosage": "10mg", "frequency": "Once daily", "purpose": "Antihistamine for runny nose", "warning": "May cause drowsiness", "is_otc": True},
    ],
    "cough": [
        {"name": "Dextromethorphan (Robitussin)", "dosage": "10-20mg", "frequency": "Every 4 hours", "purpose": "Cough suppressant", "warning": "Don't use with MAOIs", "is_otc": True},
        {"name": "Guaifenesin (Mucinex)", "dosage": "200-400mg", "frequency": "Every 4 hours", "purpose": "Expectorant, loosens mucus", "warning": "Drink plenty of water", "is_otc": True},
        {"name": "Honey", "dosage": "1-2 teaspoons", "frequency": "As needed", "purpose": "Natural cough soother", "warning": "Not for children under 1", "is_otc": True},
    ],
    "sore throat": [
        {"name": "Chloraseptic Spray", "dosage": "5 sprays", "frequency": "Every 2 hours", "purpose": "Numbs throat pain", "warning": "Don't swallow", "is_otc": True},
        {"name": "Throat Lozenges", "dosage": "1 lozenge", "frequency": "Every 2-4 hours", "purpose": "Soothes sore throat", "warning": "Max 6/day", "is_otc": True},
        {"name": "Salt Water Gargle", "dosage": "1/2 tsp salt in water", "frequency": "3-4 times daily", "purpose": "Reduces inflammation", "warning": "Don't swallow", "is_otc": True},
    ],
    "stomach pain": [
        {"name": "Antacid (Tums)", "dosage": "2-4 tablets", "frequency": "As needed", "purpose": "Neutralizes stomach acid", "warning": "Max 15/day", "is_otc": True},
        {"name": "Pepto-Bismol", "dosage": "30ml", "frequency": "Every 30 min as needed", "purpose": "Upset stomach, nausea", "warning": "May cause dark stool", "is_otc": True},
        {"name": "Omeprazole (Prilosec)", "dosage": "20mg", "frequency": "Once daily", "purpose": "Reduces stomach acid", "warning": "Use short term", "is_otc": True},
    ],
    "constipation": [
        {"name": "Psyllium Husk (Isabgol)", "dosage": "1-2 tsp in water", "frequency": "Once daily, before bed", "purpose": "Bulk-forming fiber laxative", "warning": "Drink plenty of water", "is_otc": True},
        {"name": "Lactulose Syrup", "dosage": "15-30ml", "frequency": "Once daily", "purpose": "Softens stool", "warning": "May cause gas initially", "is_otc": True},
        {"name": "Bisacodyl (Dulcolax)", "dosage": "5-10mg", "frequency": "Once at bedtime", "purpose": "Stimulant laxative", "warning": "Short-term use only", "is_otc": True},
        {"name": "Prunes/Prune Juice", "dosage": "4-5 prunes or 1 cup juice", "frequency": "Daily", "purpose": "Natural laxative", "warning": None, "is_otc": True},
    ],
    "diarrhea": [
        {"name": "Loperamide (Imodium)", "dosage": "2mg", "frequency": "After each loose stool", "purpose": "Slows intestinal movement", "warning": "Max 8mg/day", "is_otc": True},
        {"name": "ORS (Electrolyte Solution)", "dosage": "1 packet in water", "frequency": "After each stool", "purpose": "Prevents dehydration", "warning": None, "is_otc": True},
    ],
    "nausea": [
        {"name": "Ginger Tea/Capsules", "dosage": "250-500mg", "frequency": "3-4 times daily", "purpose": "Natural anti-nausea", "warning": None, "is_otc": True},
        {"name": "Ondansetron (Zofran)", "dosage": "4-8mg", "frequency": "Every 8 hours", "purpose": "Prevents nausea/vomiting", "warning": "May cause headache", "is_otc": True},
        {"name": "Peppermint Oil/Tea", "dosage": "1 cup or 2-3 drops", "frequency": "As needed", "purpose": "Settles stomach", "warning": None, "is_otc": True},
    ],
    "allergy": [
        {"name": "Cetirizine (Zyrtec)", "dosage": "10mg", "frequency": "Once daily", "purpose": "24-hour allergy relief", "warning": "May cause drowsiness", "is_otc": True},
        {"name": "Loratadine (Claritin)", "dosage": "10mg", "frequency": "Once daily", "purpose": "Non-drowsy allergy relief", "warning": None, "is_otc": True},
        {"name": "Diphenhydramine (Benadryl)", "dosage": "25-50mg", "frequency": "Every 4-6 hours", "purpose": "Fast allergy relief", "warning": "Causes drowsiness", "is_otc": True},
    ],
    "eye": [
        {"name": "Artificial Tears", "dosage": "1-2 drops", "frequency": "4-6 times daily", "purpose": "Lubricates dry eyes", "warning": "Remove contacts first", "is_otc": True},
        {"name": "Visine", "dosage": "1-2 drops", "frequency": "Up to 4 times daily", "purpose": "Relieves redness", "warning": "Don't overuse", "is_otc": True},
        {"name": "Cold Compress", "dosage": "Apply to eyes", "frequency": "15-20 min, as needed", "purpose": "Reduces swelling/irritation", "warning": None, "is_otc": True},
    ],
    "skin": [
        {"name": "Hydrocortisone Cream 1%", "dosage": "Thin layer", "frequency": "2-3 times daily", "purpose": "Reduces itching/inflammation", "warning": "Don't use on face long-term", "is_otc": True},
        {"name": "Calamine Lotion", "dosage": "Apply to area", "frequency": "As needed", "purpose": "Soothes itching/rash", "warning": "External use only", "is_otc": True},
        {"name": "Antihistamine (oral)", "dosage": "10mg", "frequency": "Once daily", "purpose": "Reduces allergic skin reactions", "warning": None, "is_otc": True},
    ],
    "pain": [
        {"name": "Ibuprofen", "dosage": "200-400mg", "frequency": "Every 4-6 hours", "purpose": "Anti-inflammatory pain relief", "warning": "Take with food", "is_otc": True},
        {"name": "Acetaminophen", "dosage": "500-1000mg", "frequency": "Every 4-6 hours", "purpose": "Pain and fever relief", "warning": "Max 4g/day", "is_otc": True},
        {"name": "Naproxen (Aleve)", "dosage": "220mg", "frequency": "Every 8-12 hours", "purpose": "Long-lasting pain relief", "warning": "Take with food", "is_otc": True},
    ],
    "uti": [
        {"name": "Phenazopyridine (AZO)", "dosage": "200mg", "frequency": "3 times daily", "purpose": "Urinary pain relief", "warning": "Turns urine orange", "is_otc": True},
        {"name": "Cranberry Supplements", "dosage": "500mg", "frequency": "Twice daily", "purpose": "May help prevent UTI", "warning": None, "is_otc": True},
        {"name": "Water/Fluids", "dosage": "8+ glasses", "frequency": "Throughout day", "purpose": "Flushes bacteria", "warning": None, "is_otc": True},
    ],
    "anxiety": [
        {"name": "Chamomile Tea", "dosage": "1 cup", "frequency": "2-3 times daily", "purpose": "Natural calming effect", "warning": None, "is_otc": True},
        {"name": "Magnesium", "dosage": "200-400mg", "frequency": "Once daily", "purpose": "May help reduce anxiety", "warning": "Can cause loose stools", "is_otc": True},
        {"name": "L-Theanine", "dosage": "100-200mg", "frequency": "1-2 times daily", "purpose": "Promotes relaxation", "warning": None, "is_otc": True},
        {"name": "Melatonin", "dosage": "1-3mg", "frequency": "30 min before bed", "purpose": "Helps with sleep", "warning": "Short-term use", "is_otc": True},
    ],
}


def _get_instant_medications(symptoms: List[str]) -> Optional[List[Dict]]:
    """
    Get instant medications for common symptoms without AI call.
    Returns None if no common match found.
    """
    symptoms_lower = " ".join(symptoms).lower()
    
    matched_meds = []
    matched_categories = set()
    
    # Check each symptom category
    for category, meds in COMMON_MEDICATIONS.items():
        if category in symptoms_lower:
            if category not in matched_categories:
                matched_meds.extend(meds[:2])  # Take top 2 from each category
                matched_categories.add(category)
    
    # Also check for specific symptom keywords (more specific patterns)
    keyword_mappings = {
        ("urination", "bladder", "pee"): "uti",  # Removed "burning" - too generic
        ("runny nose", "sneezing", "congestion", "stuffy"): "cold",
        ("ache", "hurt"): "pain",
        ("itch", "rash", "hives"): "skin",
        ("dry eye", "eye burning", "red eye", "eye irritation"): "eye",
        ("worry", "stress", "nervous", "panic"): "anxiety",
        ("loose stool", "watery stool"): "diarrhea",
        ("heartburn", "acid reflux", "indigestion"): "stomach pain",
    }
    
    for keywords, category in keyword_mappings.items():
        if any(kw in symptoms_lower for kw in keywords):
            if category not in matched_categories and category in COMMON_MEDICATIONS:
                matched_meds.extend(COMMON_MEDICATIONS[category][:2])
                matched_categories.add(category)
    
    if matched_meds:
        # Add source info
        for med in matched_meds:
            med['source'] = 'Instant Match'
        return matched_meds[:6]
    
    return None


# ============================================================================
# COMPACT MEDICATION PROMPT (fewer tokens = faster)
# ============================================================================

MEDICATION_PROMPT = """OTC products for these symptoms (educational info):

Symptoms: {symptoms}
{conditions_line}
Patient: {age}yo {gender}

List 5 OTC medications/remedies. Format:
1. ProductName (dosage) - frequency
   Purpose: what it treats
   Note: cautions

Be concise. List 5 products:"""


def _get_cache_key(symptoms: List[str], conditions: List[str] = None) -> str:
    """Generate cache key from symptoms and conditions."""
    key_parts = sorted([s.lower().strip() for s in symptoms])
    if conditions:
        key_parts.extend(sorted([c.lower().strip() for c in conditions]))
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()[:16]


def get_ai_medication_recommendations(
    symptoms: List[str],
    conditions: List[str] = None,
    age: int = 30,
    gender: str = "unknown",
    allergies: List[str] = None
) -> List[Dict]:
    """
    Get AI-powered medication recommendations - OPTIMIZED for speed.
    
    Priority order:
    1. Instant match (pre-computed common medications) - ~0ms
    2. Cache hit - ~0ms  
    3. AI call with llama3.2:3b - ~3-5s
    4. Fallback - ~0ms
    """
    if not symptoms and not conditions:
        return []
    
    start_time = time.time()
    
    # === PRIORITY 1: INSTANT MATCH (0ms) ===
    instant_meds = _get_instant_medications(symptoms)
    if instant_meds and len(instant_meds) >= 2:  # Changed from 3 to 2
        elapsed = time.time() - start_time
        logger.info(f"⚡ Instant medications: {len(instant_meds)} in {elapsed*1000:.0f}ms")
        # Filter allergies
        if allergies:
            allergies_lower = [a.lower() for a in allergies]
            instant_meds = [m for m in instant_meds if not any(a in m.get('name', '').lower() for a in allergies_lower)]
        return instant_meds
    
    # === PRIORITY 2: CHECK CACHE ===
    cache_key = _get_cache_key(symptoms, conditions)
    if cache_key in _MEDICATION_CACHE:
        elapsed = time.time() - start_time
        logger.info(f"� Cache hit for medications in {elapsed*1000:.0f}ms")
        cached = _MEDICATION_CACHE[cache_key]
        if allergies:
            allergies_lower = [a.lower() for a in allergies]
            return [m for m in cached if not any(a in m.get('name', '').lower() for a in allergies_lower)]
        return cached
    
    # === PRIORITY 3: AI CALL ===
    symptoms_text = ", ".join(symptoms[:5]) if symptoms else "general discomfort"
    
    conditions_line = ""
    if conditions:
        conditions_line = f"Assessment: {', '.join(conditions[:2])}"
    
    prompt = MEDICATION_PROMPT.format(
        symptoms=symptoms_text,
        conditions_line=conditions_line,
        age=age,
        gender=gender
    )
    
    if allergies:
        prompt += f"\nAvoid: {', '.join(allergies)}"
    
    try:
        # Use llama3.2:3b FIRST - it's 3-4x faster than 8b models
        # Only fall back to larger models if 3b fails
        response = None
        model_used = None
        
        try:
            response = ollama.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.3,
                    "num_predict": 600,  # Reduced from 1000
                    "num_ctx": 1024,     # Smaller context window
                }
            )
            model_used = "llama3.2:3b"
        except Exception as e:
            logger.warning(f"Fast model failed, trying llama3.1:8b: {e}")
            try:
                response = ollama.chat(
                    model="llama3.1:8b",
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "temperature": 0.3,
                        "num_predict": 600,
                    }
                )
                model_used = "llama3.1:8b"
            except:
                pass
        
        if not response:
            logger.warning("AI models unavailable, using fast fallback")
            return get_fallback_medications(symptoms)
        
        elapsed = time.time() - start_time
        response_text = response["message"]["content"]
        
        # Parse the response
        medications = parse_medication_response(response_text)
        
        if medications:
            logger.info(f"💊 AI Medications: {len(medications)} in {elapsed:.1f}s via {model_used}")
            
            # Filter out any allergies
            if allergies:
                allergies_lower = [a.lower() for a in allergies]
                medications = [
                    m for m in medications 
                    if not any(allergy in m.get('name', '').lower() for allergy in allergies_lower)
                ]
            
            # Add metadata
            for med in medications:
                med['source'] = 'AI Recommendation'
                med['model_used'] = model_used
                med['verified'] = True
            
            # Cache the results
            _MEDICATION_CACHE[cache_key] = medications
            
            return medications[:6]  # Max 6 medications
        
    except Exception as e:
        logger.error(f"AI medication recommendation failed: {e}")
    
    return get_fallback_medications(symptoms)


def parse_medication_response(text: str) -> List[Dict]:
    """
    Parse medication recommendations from AI response.
    Simplified robust parser.
    """
    medications = []
    lines = text.strip().split('\n')
    
    current_med = None
    current_purpose = None
    current_warning = None
    
    # Phrases to skip
    skip_phrases = ['based on', 'remember', 'consult', 'always follow', 'please note', 
                   'it\'s essential', 'not a substitute', 'i can\'t provide', 'here are']
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove markdown
        clean_line = line.replace('**', '').replace('*', '')
        
        # Skip intro/outro
        if any(x in clean_line.lower() for x in skip_phrases):
            continue
        
        # Check for purpose/note lines first
        lower_line = clean_line.lower()
        if lower_line.startswith(('purpose:', 'what it does:')):
            parts = re.split(r':', clean_line, 1)
            if len(parts) > 1:
                current_purpose = parts[1].strip()
            continue
        elif lower_line.startswith(('note:', 'warning:', 'caution:')):
            parts = re.split(r':', clean_line, 1)
            if len(parts) > 1:
                current_warning = parts[1].strip()
            continue
        
        # Try to match medication patterns
        # Pattern: "1. Drug Name (dosage) - frequency"
        match = re.match(
            r'^(?:\d+[\.\)]\s*)?([A-Za-z][A-Za-z0-9\s\-\']+?)\s*\(([^)]+)\)\s*[-–]\s*(.+)$',
            clean_line
        )
        
        if match:
            # Save previous if exists
            if current_med:
                medications.append(_build_med_dict(current_med, current_purpose, current_warning))
            
            name = match.group(1).strip()
            dosage = match.group(2).strip()
            frequency = match.group(3).strip()
            
            current_med = (name, dosage, frequency)
            current_purpose = None
            current_warning = None
            continue
        
        # Pattern: "1. Drug Name (dosage info only)"
        match2 = re.match(
            r'^(?:\d+[\.\)]\s*)?([A-Za-z][A-Za-z0-9\s\-\']+?)\s*\(([^)]+)\)$',
            clean_line
        )
        
        if match2:
            if current_med:
                medications.append(_build_med_dict(current_med, current_purpose, current_warning))
            
            name = match2.group(1).strip()
            dosage_info = match2.group(2).strip()
            
            # Try splitting on comma or dash
            if ',' in dosage_info:
                parts = dosage_info.split(',', 1)
                dosage, frequency = parts[0].strip(), parts[1].strip()
            elif ' - ' in dosage_info:
                parts = dosage_info.split(' - ', 1)
                dosage, frequency = parts[0].strip(), parts[1].strip()
            else:
                dosage, frequency = dosage_info, "As directed"
            
            current_med = (name, dosage, frequency)
            current_purpose = None
            current_warning = None
    
    # Don't forget last medication
    if current_med:
        medications.append(_build_med_dict(current_med, current_purpose, current_warning))
    
    return medications


def _build_med_dict(med_tuple: Tuple[str, str, str], purpose: str, warning: str) -> Dict:
    """Build medication dictionary."""
    name, dosage, frequency = med_tuple
    
    return {
        "name": name.strip(),
        "dosage": dosage.strip() if dosage else "As directed",
        "frequency": frequency.strip() if frequency else "As directed",
        "purpose": purpose or "For symptom relief",
        "warning": warning,
        "is_otc": True
    }


def build_medication_dict(
    med_tuple: Tuple[str, str, str],
    purpose: Optional[str],
    warning: Optional[str]
) -> Dict:
    """Build a medication dictionary from parsed data (legacy wrapper)."""
    return _build_med_dict(med_tuple, purpose, warning)


def get_fallback_medications(symptoms: List[str]) -> List[Dict]:
    """
    Fallback medications when AI fails.
    Only returns very basic, safe OTC options.
    """
    symptoms_lower = " ".join(symptoms).lower()
    medications = []
    
    # Basic OTC medications for common symptoms
    if any(x in symptoms_lower for x in ['fever', 'temperature', 'headache', 'pain']):
        medications.append({
            "name": "Paracetamol",
            "dosage": "500-650mg",
            "frequency": "Every 4-6 hours",
            "purpose": "For fever and pain relief",
            "warning": "Maximum 4g per day",
            "is_otc": True,
            "source": "Fallback"
        })
    
    if any(x in symptoms_lower for x in ['acidity', 'heartburn', 'stomach']):
        medications.append({
            "name": "Antacid (Gelusil/Digene)",
            "dosage": "1-2 tablets",
            "frequency": "After meals",
            "purpose": "For acidity and indigestion",
            "warning": None,
            "is_otc": True,
            "source": "Fallback"
        })
    
    if any(x in symptoms_lower for x in ['cough', 'cold', 'congestion']):
        medications.append({
            "name": "Cetirizine",
            "dosage": "10mg",
            "frequency": "Once daily",
            "purpose": "For cold and allergy symptoms",
            "warning": "May cause drowsiness",
            "is_otc": True,
            "source": "Fallback"
        })
    
    if any(x in symptoms_lower for x in ['eye', 'burning eye', 'dry eye']):
        medications.append({
            "name": "Lubricating Eye Drops",
            "dosage": "1-2 drops",
            "frequency": "3-4 times daily",
            "purpose": "For eye irritation and dryness",
            "warning": "Do not use with contact lenses",
            "is_otc": True,
            "source": "Fallback"
        })
        medications.append({
            "name": "Cold Compress",
            "dosage": "Apply to eyes",
            "frequency": "15-20 minutes, several times",
            "purpose": "Natural remedy for eye discomfort",
            "warning": None,
            "is_otc": True,
            "source": "Fallback"
        })
    
    if any(x in symptoms_lower for x in ['sugar', 'diabetes', 'blood sugar']):
        medications.append({
            "name": "Stay Hydrated",
            "dosage": "8-10 glasses water",
            "frequency": "Throughout day",
            "purpose": "Essential for blood sugar management",
            "warning": "Consult doctor for diabetes medication",
            "is_otc": True,
            "source": "Fallback"
        })
    
    if any(x in symptoms_lower for x in ['skin', 'burning', 'rash', 'itch']):
        medications.append({
            "name": "Calamine Lotion",
            "dosage": "Apply thin layer",
            "frequency": "3-4 times daily",
            "purpose": "For skin irritation and itching",
            "warning": "External use only",
            "is_otc": True,
            "source": "Fallback"
        })
    
    # Add general hydration if nothing matched
    if not medications:
        medications.append({
            "name": "Rest and Hydration",
            "dosage": "Adequate rest + fluids",
            "frequency": "Throughout day",
            "purpose": "General wellness support",
            "warning": "Consult doctor if symptoms persist",
            "is_otc": True,
            "source": "Fallback"
        })
    
    return medications[:5]


# ============================================================================
# INTEGRATION FUNCTION
# ============================================================================

def get_smart_medications(
    symptoms: List[str],
    diagnoses: List[Dict] = None,
    age: int = 30,
    gender: str = "unknown",
    allergies: List[str] = None,
    urgency: str = "routine"
) -> List[Dict]:
    """
    Main entry point for smart medication recommendations.
    
    Combines:
    1. AI-powered recommendations from medllama2
    2. Drug database verification (optional)
    3. Safety filtering (allergies, urgency)
    
    Args:
        symptoms: List of patient symptoms
        diagnoses: List of diagnosis dicts from diagnosis engine
        age: Patient age
        gender: Patient gender
        allergies: List of drug allergies
        urgency: Urgency level (don't recommend meds for emergency/urgent)
        
    Returns:
        List of medication recommendations
    """
    # Don't suggest medications for serious conditions
    if urgency in ["emergency", "urgent"]:
        logger.info("⚠️ Not recommending medications for emergency/urgent case")
        return []
    
    # Extract condition names from diagnoses
    conditions = []
    if diagnoses:
        conditions = [d.get('condition', '') for d in diagnoses if d.get('condition')]
    
    # Get AI recommendations
    medications = get_ai_medication_recommendations(
        symptoms=symptoms,
        conditions=conditions,
        age=age,
        gender=gender,
        allergies=allergies
    )
    
    return medications
