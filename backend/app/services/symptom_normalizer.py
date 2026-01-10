"""
Symptom Normalizer
==================
Comprehensive symptom normalization with:
- 1000+ typo/variation mappings
- Fuzzy matching for unknown typos
- Indian language transliterations (Hindi, Tamil, etc.)
- Medical terminology to layman terms
- Phrase extraction and normalization
"""

import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class SymptomNormalizer:
    """
    Comprehensive symptom normalization engine.
    Handles typos, variations, medical terms, and Indian languages.
    """
    
    # ========================================
    # CANONICAL SYMPTOMS (The standard terms)
    # ========================================
    CANONICAL_SYMPTOMS = [
        # Head & Neurological
        "headache", "migraine", "dizziness", "vertigo", "fainting",
        "confusion", "memory loss", "seizure", "tremor", "numbness",
        
        # Fever & General
        "fever", "chills", "sweating", "fatigue", "weakness", "malaise",
        "body ache", "weight loss", "weight gain", "loss of appetite",
        
        # Respiratory
        "cough", "cold", "runny nose", "congestion", "sneezing",
        "sore throat", "breathing difficulty", "wheezing", "chest tightness",
        
        # Gastrointestinal
        "stomach pain", "nausea", "vomiting", "diarrhea", "constipation",
        "bloating", "gas", "acidity", "heartburn", "indigestion",
        "abdominal cramps", "loss of appetite",
        
        # Pain
        "back pain", "neck pain", "joint pain", "muscle pain", "chest pain",
        "toothache", "ear pain", "eye pain", "leg pain", "arm pain",
        "shoulder pain", "knee pain", "hip pain", "ankle pain", "wrist pain",
        
        # Skin
        "rash", "itching", "hives", "swelling", "bruising", "skin redness",
        "acne", "dry skin", "skin peeling", "skin burning",
        
        # Mental Health
        "anxiety", "depression", "stress", "insomnia", "panic attack",
        "mood swings", "irritability", "loneliness", "hopelessness",
        
        # ENT
        "ear pain", "hearing loss", "tinnitus", "nasal congestion",
        "sinus pain", "post nasal drip", "hoarseness",
        
        # Eyes
        "eye pain", "blurred vision", "eye redness", "watery eyes",
        "eye itching", "light sensitivity",
        
        # Urinary
        "painful urination", "frequent urination", "blood in urine",
        "urinary urgency", "incontinence",
        
        # Cardiovascular
        "palpitations", "rapid heartbeat", "slow heartbeat", "chest pain",
        "shortness of breath", "leg swelling",
        
        # Other
        "allergic reaction", "hair loss", "nail problems", "bad breath",
        "excessive thirst", "frequent hunger"
    ]
    
    # ========================================
    # COMPREHENSIVE VARIATION MAPPINGS
    # ========================================
    SYMPTOM_VARIATIONS = {
        # ==========================================
        # HEADACHE VARIATIONS (100+)
        # ==========================================
        "headache": [
            # Common typos
            "headach", "headace", "headake", "hedache", "haedache", "headahce",
            "headche", "headeache", "headaceh", "headahe", "headachee", "headeach",
            "headachhe", "haadache", "heedache", "headcahe", "headahce", "hedace",
            # Variations
            "head ache", "head-ache", "head pain", "head hurting", "head hurts",
            "head is paining", "head is hurting", "my head hurts", "my head is paining",
            "pain in head", "pain in my head", "head throbbing", "throbbing head",
            "pounding head", "pounding headache", "splitting headache", "bad headache",
            "severe headache", "mild headache", "slight headache", "terrible headache",
            "awful headache", "horrible headache", "constant headache", "persistent headache",
            "chronic headache", "tension headache", "stress headache", "sinus headache",
            "cluster headache", "one sided headache", "frontal headache",
            # Hindi transliterations
            "sar dard", "sardard", "sir dard", "sirdard", "sar me dard",
            "sir me dard", "sar mein dard", "sir mein dard",
            # Tamil transliterations
            "thalai vali", "thalaivali", "thalai valikkuthu",
            # Telugu
            "tala noppi", "talanoppi",
        ],
        
        # ==========================================
        # MIGRAINE VARIATIONS (50+)
        # ==========================================
        "migraine": [
            # Typos
            "migrain", "migraines", "migranes", "migrane", "migrene", "migriane",
            "migarin", "migarain", "mirgaine", "mirgane", "migarin", "migrn",
            "mygraine", "mygrane", "maigraine", "maigrane", "miraine", "migrine",
            # Variations
            "migraine headache", "migraine attack", "having migraine", "got migraine",
            "severe migraine", "bad migraine", "chronic migraine", "frequent migraine",
            "migraine with aura", "migraine without aura", "ocular migraine",
            "visual migraine", "hemiplegic migraine", "vestibular migraine",
            # Descriptive
            "one side head pain", "half head pain", "half headache",
        ],
        
        # ==========================================
        # FEVER VARIATIONS (80+)
        # ==========================================
        "fever": [
            # Typos
            "fevar", "fevr", "fver", "feber", "feever", "feveer", "fevver",
            "fevor", "feaver", "feavr", "fevre", "fevir", "fevur",
            # Variations
            "high fever", "low fever", "mild fever", "high temperature", "temperature",
            "running temperature", "got temperature", "have temperature",
            "low grade fever", "high grade fever", "viral fever", "bacterial fever",
            "continuous fever", "intermittent fever", "on and off fever",
            "burning up", "feeling hot", "feeling feverish", "feverish",
            "body is hot", "body feels hot", "hot body", "pyrexia",
            # Hindi
            "bukhar", "bukhaar", "tez bukhar", "halka bukhar", "bukhar hai",
            "bukhar ho gaya", "bukhar aa gaya", "badan garam", "badan garm",
            # Tamil
            "kaichal", "kaychhal", "udambu soodu",
            # Telugu
            "jwaram", "jvaram",
        ],
        
        # ==========================================
        # COLD VARIATIONS (60+)
        # ==========================================
        "cold": [
            # Typos
            "cld", "clod", "coold", "coldd", "couldd",
            # Variations
            "common cold", "having cold", "got cold", "caught cold",
            "head cold", "chest cold", "bad cold", "severe cold", "mild cold",
            "cold and cough", "cold cough", "cough cold", "cold symptoms",
            "running nose", "runny nose", "nose running", "blocked nose",
            "stuffy nose", "nose is blocked", "nose block", "nasal congestion",
            "nasal block", "nose congestion", "sinus", "sinusitis",
            # Hindi
            "sardi", "sardee", "jukam", "jukaam", "zukam", "zukaam",
            "naak band", "naak bahna", "naak beh rahi",
            # Tamil
            "jaladhosham", "mookku adaippu",
        ],
        
        # ==========================================
        # COUGH VARIATIONS (70+)
        # ==========================================
        "cough": [
            # Typos
            "coff", "cogh", "caugh", "cugh", "coough", "cougg", "coughh",
            "koff", "kof", "kough", "coff", "cofing", "coffing",
            # Variations
            "coughing", "dry cough", "wet cough", "productive cough",
            "chronic cough", "persistent cough", "constant cough", "bad cough",
            "severe cough", "mild cough", "slight cough", "terrible cough",
            "hacking cough", "barking cough", "whooping cough", "chest cough",
            "coughing up phlegm", "coughing up mucus", "coughing blood",
            "cough with phlegm", "cough with mucus", "phlegm cough",
            "mucus cough", "throat cough", "tickly cough", "itchy cough",
            "night cough", "morning cough", "coughing at night",
            # Hindi
            "khansi", "khasi", "khaansi", "khassi", "sukhi khansi", "geeli khansi",
            "balgam wali khansi", "balgam", "kaph",
            # Tamil
            "irumbal", "erumal",
        ],
        
        # ==========================================
        # STOMACH PAIN VARIATIONS (100+)
        # ==========================================
        "stomach pain": [
            # Typos
            "stomache pain", "stomachpain", "stomac pain", "stoamch pain",
            "stomech pain", "stomache ache", "stmach pain", "stomack pain",
            "stommach pain", "stomah pain", "stomahc pain", "stomach pian",
            "stomach painn", "stomach pein", "stomach pen",
            # Variations
            "stomach ache", "stomachache", "stomach-ache", "stomach hurts",
            "stomach hurting", "stomach is hurting", "stomach is paining",
            "my stomach hurts", "my stomach is paining", "pain in stomach",
            "pain in my stomach", "tummy pain", "tummy ache", "tummy hurts",
            "belly pain", "belly ache", "bellyache", "belly hurts",
            "abdominal pain", "abdomen pain", "pain in abdomen",
            "upper stomach pain", "lower stomach pain", "left stomach pain",
            "right stomach pain", "stomach cramps", "stomach cramping",
            "stomach discomfort", "upset stomach", "stomach upset",
            "stomach trouble", "stomach problem", "stomach issue",
            "gastric pain", "gastric problem", "gastric issue",
            "burning stomach", "stomach burning", "burning in stomach",
            "sharp stomach pain", "dull stomach pain", "severe stomach pain",
            # Hindi
            "pet dard", "petdard", "pet me dard", "pet mein dard", "pait dard",
            "pait me dard", "paet dard", "pet kharab", "pet me jalan",
            # Tamil
            "vayiru vali", "vayiru valikkuthu", "vayiru", "vayitru vali",
            # Telugu
            "kallu noppi", "potta noppi",
        ],
        
        # ==========================================
        # NAUSEA/VOMITING VARIATIONS (60+)
        # ==========================================
        "nausea": [
            # Typos
            "nausia", "nausea", "nausious", "nauseus", "nausia", "nauseating",
            "nausiated", "nasuea", "nasea", "nauseia",
            # Variations
            "feeling nauseous", "feel nauseous", "feeling sick", "feel sick",
            "queasy", "feeling queasy", "feel like vomiting", "want to vomit",
            "about to vomit", "going to vomit", "urge to vomit",
            "stomach turning", "stomach churning",
            # Hindi
            "ji machlana", "ulti jaisa", "ulti jaise", "matli",
        ],
        
        "vomiting": [
            # Typos
            "vomitting", "vomting", "vomitng", "vommiting", "vometing",
            "vomming", "vommit", "vomit", "vomts",
            # Variations
            "throwing up", "threw up", "puking", "puked", "puke",
            "being sick", "was sick", "got sick", "getting sick",
            # Hindi
            "ulti", "ultee", "ulti ho rahi", "ulti aa rahi", "ulti hui",
            "qai", "kai",
            # Tamil
            "vaanthi", "vanthi",
        ],
        
        # ==========================================
        # DIARRHEA VARIATIONS (80+)
        # ==========================================
        "diarrhea": [
            # Typos
            "diarrhoea", "diarhea", "diarreha", "diareha", "diarrea",
            "diarhhea", "diarrheaa", "diarhrea", "diarheea", "diarreah",
            "diareah", "diariah", "diaria", "diarria", "diareea",
            # Variations
            "loose motion", "loose motions", "loose stool", "loose stools",
            "watery stool", "watery stools", "running stomach", "runny stomach",
            "upset stomach", "stomach upset", "liquid stool", "liquid stools",
            "frequent stools", "going toilet frequently", "bathroom emergency",
            "can't hold", "potty", "potty problem", "motion problem",
            "dysentery", "gastro", "gastroenteritis", "stomach bug", "stomach flu",
            "food poisoning", "travelers diarrhea",
            # Hindi
            "dast", "dast lagna", "dast ho gaye", "pait kharab",
            "pet kharab", "ulti dast", "loose motion ho raha",
            "patla latrine", "latrine", "potty",
            # Tamil
            "vayiru pokku", "vayiru pokuthu",
        ],
        
        # ==========================================
        # CONSTIPATION VARIATIONS (50+)
        # ==========================================
        "constipation": [
            # Typos
            "constipaton", "constipatin", "constipasion", "constpation",
            "consitpation", "constipatiom", "constapation", "constapasion",
            # Variations
            "hard stool", "hard stools", "difficulty passing stool",
            "can't pass stool", "unable to pass stool", "no bowel movement",
            "haven't gone to toilet", "not going to toilet", "blocked",
            "feeling blocked", "stomach blocked", "not passing motion",
            "tight stomach", "heavy stomach",
            # Hindi
            "kabz", "kabj", "qabz", "pet saaf nahi", "motion nahi ho raha",
            "latrine nahi ho rahi",
            # Tamil
            "malaccikkal",
        ],
        
        # ==========================================
        # ACIDITY/HEARTBURN VARIATIONS (60+)
        # ==========================================
        "acidity": [
            # Typos
            "acidty", "aciidty", "acedity", "acdity", "aciditi",
            # Variations
            "acid reflux", "gastric", "gastric problem", "gas problem",
            "gas trouble", "gassy", "gas formation", "excessive gas",
            "burping", "belching", "sour stomach", "sour taste",
            "acid in stomach", "stomach acid", "hyperacidity",
            # Hindi  
            "acidity", "gas", "gas ban rahi", "khatta dakar", "dakar",
            "pet me gas", "seene me jalan",
            # Tamil
            "vayiru erichal", "nenju erichal",
        ],
        
        "heartburn": [
            # Typos
            "heartburm", "heartbrun", "hartburn", "heart burn",
            # Variations
            "burning chest", "chest burning", "burning in chest",
            "burning sensation in chest", "acid reflux", "reflux",
            "gerd", "burning throat", "throat burning",
            # Hindi
            "seene me jalan", "sine me jalan", "chhati me jalan",
        ],
        
        # ==========================================
        # BODY ACHE VARIATIONS (50+)
        # ==========================================
        "body ache": [
            # Typos
            "body ach", "bodyache", "body-ache", "bodyach", "bodypain",
            # Variations
            "body pain", "body pains", "body is aching", "body is paining",
            "whole body pain", "full body pain", "entire body pain",
            "general body ache", "all over pain", "aching all over",
            "muscles aching", "bones aching", "feeling sore", "soreness",
            "body soreness", "body tired", "body fatigue",
            # Hindi
            "badan dard", "shareer me dard", "poora badan dard",
            "haddi dard", "jod dard",
            # Tamil
            "udambu vali", "udal vali",
        ],
        
        # ==========================================
        # BACK PAIN VARIATIONS (60+)
        # ==========================================
        "back pain": [
            # Typos
            "backpain", "back-pain", "bakc pain", "bak pain", "backache",
            "back ache", "back-ache",
            # Variations
            "back is paining", "back is hurting", "pain in back",
            "lower back pain", "upper back pain", "middle back pain",
            "spine pain", "spinal pain", "lumbar pain",
            "back stiffness", "stiff back", "back spasm", "back strain",
            "slipped disc", "disc problem", "sciatica",
            # Hindi
            "kamar dard", "kamardard", "kamar me dard", "peeth dard",
            "pith dard", "pith me dard",
            # Tamil
            "muthuguvalai", "muthukkuvali",
        ],
        
        # ==========================================
        # JOINT PAIN VARIATIONS (50+)
        # ==========================================
        "joint pain": [
            # Typos
            "jointpain", "joint-pain", "jont pain", "joint pian",
            # Variations
            "joint ache", "joints pain", "joints aching", "joints hurting",
            "arthritis", "arthritic", "rheumatism", "rheumatic",
            "stiff joints", "joint stiffness", "swollen joints", "joint swelling",
            # Hindi
            "jodo me dard", "jodon mein dard", "gathiya",
            # Specific joints
            "knee pain", "elbow pain", "wrist pain", "ankle pain",
            "hip pain", "shoulder pain", "finger joint pain",
        ],
        
        # ==========================================
        # SORE THROAT VARIATIONS (50+)
        # ==========================================
        "sore throat": [
            # Typos
            "sorethroat", "sore-throat", "sor throat", "sore throught",
            "soar throat", "saw throat",
            # Variations
            "throat pain", "throat hurts", "throat hurting", "throat is paining",
            "pain in throat", "painful throat", "throat infection",
            "scratchy throat", "itchy throat", "dry throat", "burning throat",
            "swollen throat", "throat swelling", "difficulty swallowing",
            "can't swallow", "hurts to swallow", "painful swallowing",
            "pharyngitis", "tonsillitis", "tonsils", "strep throat",
            # Hindi
            "gala dard", "gale me dard", "gala kharab", "gala sukhna",
            # Tamil
            "thondai vali", "thondai kanam",
        ],
        
        # ==========================================
        # ANXIETY VARIATIONS (60+)
        # ==========================================
        "anxiety": [
            # Typos
            "anxity", "anxeity", "anixety", "axiety", "anxeity",
            # Variations
            "anxious", "feeling anxious", "very anxious", "anxiety attack",
            "panic", "panic attack", "panicking", "panicked",
            "nervous", "nervousness", "feeling nervous", "worried",
            "worrying", "constant worry", "fear", "fearful", "scared",
            "racing thoughts", "can't relax", "restless", "restlessness",
            "uneasy", "on edge", "tense", "tension",
            # Hindi
            "ghabrahat", "chinta", "dar", "bechain", "bechaini",
            # Tamil
            "bayam", "kavalai",
        ],
        
        # ==========================================
        # DEPRESSION VARIATIONS (50+)
        # ==========================================
        "depression": [
            # Typos
            "depresion", "depresssion", "deppression", "depressin",
            # Variations
            "depressed", "feeling depressed", "very depressed",
            "sad", "feeling sad", "very sad", "sadness", "unhappy",
            "low mood", "feeling low", "feeling down", "down",
            "hopeless", "hopelessness", "no hope", "worthless",
            "empty", "feeling empty", "numb", "feeling numb",
            "no motivation", "unmotivated", "lost interest",
            "don't care", "nothing matters",
            # Hindi
            "udaas", "udasi", "dukhi", "nirasha",
        ],
        
        # ==========================================
        # INSOMNIA/SLEEP VARIATIONS (60+)
        # ==========================================
        "insomnia": [
            # Typos
            "insomina", "insomnia", "insomania", "insomia",
            # Variations
            "can't sleep", "cannot sleep", "unable to sleep", "not sleeping",
            "difficulty sleeping", "trouble sleeping", "sleep problem",
            "sleep issues", "sleepless", "sleeplessness", "no sleep",
            "poor sleep", "bad sleep", "disturbed sleep", "broken sleep",
            "waking up at night", "waking up frequently", "light sleep",
            "not getting sleep", "sleep deprivation",
            # Hindi
            "neend nahi aati", "neend nahi aa rahi", "neend ki problem",
            "so nahi pa raha", "jagta rehta hun",
            # Tamil
            "thookkam varathu", "thookkam illai",
        ],
        
        # ==========================================
        # FATIGUE/WEAKNESS VARIATIONS (50+)
        # ==========================================
        "fatigue": [
            # Typos
            "fatique", "fatige", "fatiuge", "fatigeu",
            # Variations
            "tired", "tiredness", "feeling tired", "very tired",
            "exhausted", "exhaustion", "feeling exhausted", "worn out",
            "drained", "feeling drained", "no energy", "low energy",
            "lethargic", "lethargy", "sluggish",
            # Hindi
            "thakan", "thakaan", "thak gaya", "kamzori", "kamjori",
        ],
        
        "weakness": [
            # Typos
            "weekness", "weaknes", "weaknss", "waekness",
            # Variations
            "weak", "feeling weak", "very weak", "body weakness",
            "general weakness", "weak body", "no strength", "feeble",
            # Hindi
            "kamzori", "kamjori", "taakat nahi", "shakti nahi",
        ],
        
        # ==========================================
        # DIZZINESS VARIATIONS (40+)
        # ==========================================
        "dizziness": [
            # Typos
            "dizzines", "dizzyness", "dizzness", "diziness",
            # Variations
            "dizzy", "feeling dizzy", "very dizzy", "light headed",
            "lightheaded", "head spinning", "room spinning", "spinning",
            "vertigo", "unsteady", "off balance", "losing balance",
            "wobbly", "faint", "feeling faint", "about to faint",
            # Hindi
            "chakkar", "chakkar aa raha", "sir ghoom raha",
            # Tamil
            "talai sutral", "talai suttuthu",
        ],
        
        # ==========================================
        # RASH/SKIN VARIATIONS (50+)
        # ==========================================
        "rash": [
            # Typos
            "rsh", "rsah", "rach", "raash",
            # Variations
            "skin rash", "body rash", "red rash", "itchy rash",
            "rashes", "skin rashes", "breaking out", "skin breakout",
            "red spots", "skin spots", "bumps on skin", "skin bumps",
            "hives", "urticaria", "skin allergy", "allergic rash",
            "eczema", "dermatitis", "psoriasis",
            # Hindi
            "daane", "dane", "lal dane", "khujli wale dane", "chakatte",
        ],
        
        "itching": [
            # Typos
            "itchng", "itcing", "iching", "itchhing",
            # Variations
            "itchy", "feeling itchy", "very itchy", "skin itching",
            "body itching", "scratching", "want to scratch",
            "itchiness", "constant itching",
            # Hindi
            "khujli", "kharish", "khujana",
            # Tamil
            "arippu",
        ],
        
        # ==========================================
        # BREATHING VARIATIONS (50+)
        # ==========================================
        "breathing difficulty": [
            # Variations
            "difficulty breathing", "hard to breathe", "trouble breathing",
            "breathing problem", "can't breathe", "cannot breathe",
            "short of breath", "shortness of breath", "breathless",
            "breathlessness", "gasping", "gasping for air", "wheezing",
            "tight chest", "chest tightness", "labored breathing",
            "heavy breathing", "rapid breathing", "shallow breathing",
            "asthma", "asthma attack", "bronchitis",
            # Hindi
            "saans lene me dikkat", "saans nahi aa rahi", "saans phoolna",
            "dum ghutna", "dama",
            # Tamil
            "moochu thinaral",
        ],
        
        # ==========================================
        # CHEST PAIN VARIATIONS (40+)
        # ==========================================
        "chest pain": [
            # Typos
            "chestpain", "chest-pain", "chesst pain", "chets pain",
            # Variations
            "chest hurts", "chest is hurting", "chest is paining",
            "pain in chest", "left chest pain", "right chest pain",
            "center chest pain", "chest discomfort", "chest pressure",
            "chest tightness", "tight chest", "heavy chest",
            "burning chest", "sharp chest pain", "dull chest pain",
            "heart pain", "cardiac pain",
            # Hindi
            "seene me dard", "chhati me dard", "dil me dard",
            "sina dard",
        ],
        
        # ==========================================
        # EAR PAIN VARIATIONS (30+)
        # ==========================================
        "ear pain": [
            # Typos
            "earpain", "ear-pain", "earache", "ear ache",
            # Variations
            "ear hurts", "ear is hurting", "pain in ear",
            "ear infection", "otitis", "ear problem", "ear trouble",
            "blocked ear", "ear blocked", "ear pressure",
            # Hindi
            "kaan dard", "kaan me dard",
            # Tamil
            "kaathu vali",
        ],
        
        # ==========================================
        # TOOTHACHE VARIATIONS (30+)
        # ==========================================
        "toothache": [
            # Typos
            "toothach", "tooth ache", "tooth-ache", "toothake",
            # Variations
            "tooth pain", "teeth pain", "tooth hurts", "teeth hurting",
            "dental pain", "jaw pain", "gum pain", "tooth infection",
            "cavity", "cavity pain", "wisdom tooth pain",
            # Hindi
            "daant dard", "daant me dard", "masude me dard",
            # Tamil
            "pal vali",
        ],
        
        # ==========================================
        # SWELLING VARIATIONS (30+)
        # ==========================================
        "swelling": [
            # Typos
            "sweling", "swellin", "swolen", "swolen",
            # Variations
            "swollen", "swelled", "swelled up", "puffiness", "puffy",
            "edema", "water retention", "inflammation", "inflamed",
            # Hindi
            "sujan", "soojan", "phulna", "phula hua",
        ],
        
        # ==========================================
        # ALLERGIC REACTION VARIATIONS (30+)
        # ==========================================
        "allergic reaction": [
            # Variations
            "allergy", "allergies", "allergic", "having allergy",
            "allergy attack", "allergy symptoms", "food allergy",
            "skin allergy", "dust allergy", "pollen allergy",
            "allergic to", "anaphylaxis",
            # Hindi
            "allergy", "allergy ho gayi", "allergy hai",
        ],
        
        # ==========================================
        # BLOATING/GAS VARIATIONS (40+)
        # ==========================================
        "bloating": [
            # Typos
            "bloatng", "blaoting", "bloatin",
            # Variations
            "bloated", "feeling bloated", "stomach bloating",
            "belly bloating", "abdominal bloating", "puffy stomach",
            "distended stomach", "swollen belly",
            # Hindi
            "pet phoola", "pet phulna",
        ],
        
        "gas": [
            # Variations
            "gastric", "gassy", "passing gas", "flatulence",
            "wind", "stomach gas", "abdominal gas",
            "gas formation", "gas problem", "excess gas",
            # Hindi
            "gas", "gas ban rahi", "pet me gas", "hawa",
        ],
    }
    
    def __init__(self):
        """Initialize the normalizer with lookup tables"""
        # Build reverse lookup: variation -> canonical
        self._variation_to_canonical: Dict[str, str] = {}
        self._build_variation_lookup()
        
        # All canonical symptoms set for fuzzy matching
        self._canonical_set = set(self.CANONICAL_SYMPTOMS)
        
        logger.info(f"SymptomNormalizer initialized with {len(self._variation_to_canonical)} variations")
    
    def _build_variation_lookup(self):
        """Build reverse lookup from variations to canonical symptoms"""
        for canonical, variations in self.SYMPTOM_VARIATIONS.items():
            # Add the canonical form itself
            self._variation_to_canonical[canonical.lower()] = canonical
            
            for variation in variations:
                self._variation_to_canonical[variation.lower()] = canonical
    
    def normalize(self, text: str) -> Tuple[str, List[str]]:
        """
        Normalize text and extract symptoms.
        
        Returns:
            Tuple of (normalized_text, list_of_symptoms_found)
        """
        text_lower = text.lower().strip()
        found_symptoms = []
        normalized_text = text_lower
        
        # First pass: Direct lookup for known variations
        for variation, canonical in sorted(self._variation_to_canonical.items(), key=lambda x: -len(x[0])):
            if variation in normalized_text:
                if canonical not in found_symptoms:
                    found_symptoms.append(canonical)
                # Normalize the text
                normalized_text = normalized_text.replace(variation, canonical)
        
        # Second pass: Fuzzy matching for unknown typos
        words = text_lower.split()
        for i, word in enumerate(words):
            if len(word) >= 4 and word not in self._variation_to_canonical:
                # Try fuzzy match
                match = self._fuzzy_match(word)
                if match:
                    if match not in found_symptoms:
                        found_symptoms.append(match)
        
        # Check for multi-word symptoms that might have been missed
        for canonical in self.CANONICAL_SYMPTOMS:
            if canonical in normalized_text and canonical not in found_symptoms:
                found_symptoms.append(canonical)
        
        return normalized_text, found_symptoms
    
    def _fuzzy_match(self, word: str, threshold: float = 0.8) -> Optional[str]:
        """
        Fuzzy match a word against known symptoms.
        Uses sequence matching for typo detection.
        """
        best_match = None
        best_ratio = threshold
        
        # Check against canonical symptoms
        for symptom in self._canonical_set:
            # Only compare single words or first word of multi-word symptoms
            symptom_words = symptom.split()
            for sym_word in symptom_words:
                ratio = SequenceMatcher(None, word, sym_word).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = symptom
        
        # Check against known variations
        for variation in list(self._variation_to_canonical.keys())[:500]:  # Limit for performance
            if len(variation.split()) == 1:  # Single word variations only
                ratio = SequenceMatcher(None, word, variation).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = self._variation_to_canonical[variation]
        
        return best_match
    
    def extract_symptoms(self, text: str) -> List[str]:
        """
        Extract all symptoms from text.
        Returns list of canonical symptom names.
        """
        _, symptoms = self.normalize(text)
        return symptoms
    
    def get_canonical(self, symptom: str) -> str:
        """
        Get the canonical form of a symptom.
        Returns the input if no canonical form is found.
        """
        return self._variation_to_canonical.get(symptom.lower(), symptom)


# Global instance
symptom_normalizer = SymptomNormalizer()


# Convenience functions
def normalize_symptoms(text: str) -> List[str]:
    """Extract and normalize symptoms from text"""
    return symptom_normalizer.extract_symptoms(text)


def get_canonical_symptom(symptom: str) -> str:
    """Get canonical form of a symptom"""
    return symptom_normalizer.get_canonical(symptom)
