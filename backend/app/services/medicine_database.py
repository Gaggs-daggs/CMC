"""
Indian Medicine Database
Comprehensive database of Indian medicines with compositions
Used as fallback when Gemini is restricted
"""

# Symptom -> Disease -> Medicine mapping
DISEASE_MEDICINE_DB = {
    # ==========================================
    # COMMON COLD & FLU
    # ==========================================
    "common_cold": {
        "symptoms": ["runny nose", "sneezing", "congestion", "sore throat", "mild fever", "body ache"],
        "medicines": [
            {
                "brand_name": "Sinarest",
                "generic_name": "Paracetamol + Phenylephrine + Chlorpheniramine",
                "composition": [
                    {"ingredient": "Paracetamol", "strength": "500mg"},
                    {"ingredient": "Phenylephrine", "strength": "10mg"},
                    {"ingredient": "Chlorpheniramine Maleate", "strength": "2mg"}
                ],
                "drug_class": "Decongestant + Antihistamine + Analgesic",
                "common_uses": ["Common cold", "Nasal congestion", "Runny nose", "Sneezing"],
                "typical_dosage": "1 tablet every 6-8 hours",
                "administration": "Take with or without food",
                "common_side_effects": ["Drowsiness", "Dry mouth", "Dizziness"],
                "contraindications": ["High blood pressure", "Glaucoma", "Urinary retention"],
                "alternatives": ["Coldact", "D-Cold Total", "Chericof"],
                "otc_status": "OTC",
                "approximate_price": "₹30-50 for 10 tablets"
            },
            {
                "brand_name": "Cetirizine (Cetzine/Zyrtec)",
                "generic_name": "Cetirizine Hydrochloride",
                "composition": [
                    {"ingredient": "Cetirizine Hydrochloride", "strength": "10mg"}
                ],
                "drug_class": "Antihistamine",
                "common_uses": ["Allergic rhinitis", "Sneezing", "Runny nose", "Itching"],
                "typical_dosage": "1 tablet once daily",
                "administration": "Take at night (may cause drowsiness)",
                "common_side_effects": ["Drowsiness", "Dry mouth", "Fatigue"],
                "contraindications": ["Severe kidney disease"],
                "alternatives": ["Alerid", "CTZ", "Okacet"],
                "otc_status": "OTC",
                "approximate_price": "₹20-40 for 10 tablets"
            }
        ]
    },
    
    # ==========================================
    # FEVER
    # ==========================================
    "fever": {
        "symptoms": ["high temperature", "fever", "chills", "sweating", "body ache", "weakness"],
        "medicines": [
            {
                "brand_name": "Dolo 650",
                "generic_name": "Paracetamol",
                "composition": [
                    {"ingredient": "Paracetamol", "strength": "650mg"}
                ],
                "drug_class": "Antipyretic/Analgesic",
                "common_uses": ["Fever", "Headache", "Body pain", "Cold"],
                "typical_dosage": "1 tablet every 4-6 hours as needed",
                "administration": "Take with or without food. Do not exceed 4 tablets in 24 hours",
                "common_side_effects": ["Nausea (rare)", "Allergic reactions (rare)"],
                "contraindications": ["Liver disease", "Alcohol dependence", "G6PD deficiency"],
                "alternatives": ["Crocin 650", "Calpol 650", "Pacimol 650", "P-650"],
                "otc_status": "OTC",
                "approximate_price": "₹30-35 for 15 tablets"
            },
            {
                "brand_name": "Crocin Advance",
                "generic_name": "Paracetamol",
                "composition": [
                    {"ingredient": "Paracetamol", "strength": "500mg"}
                ],
                "drug_class": "Antipyretic/Analgesic",
                "common_uses": ["Fever", "Headache", "Toothache", "Body pain"],
                "typical_dosage": "1-2 tablets every 4-6 hours",
                "administration": "Take with water. Maximum 8 tablets in 24 hours",
                "common_side_effects": ["Nausea (rare)", "Skin rash (rare)"],
                "contraindications": ["Liver disease", "Chronic alcohol use"],
                "alternatives": ["Dolo 500", "Calpol", "Pacimol"],
                "otc_status": "OTC",
                "approximate_price": "₹25-30 for 15 tablets"
            }
        ]
    },
    
    # ==========================================
    # HEADACHE & MIGRAINE
    # ==========================================
    "headache": {
        "symptoms": ["headache", "head pain", "migraine", "throbbing pain", "pressure in head"],
        "medicines": [
            {
                "brand_name": "Saridon",
                "generic_name": "Paracetamol + Propyphenazone + Caffeine",
                "composition": [
                    {"ingredient": "Paracetamol", "strength": "250mg"},
                    {"ingredient": "Propyphenazone", "strength": "150mg"},
                    {"ingredient": "Caffeine", "strength": "50mg"}
                ],
                "drug_class": "Analgesic combination",
                "common_uses": ["Headache", "Migraine", "Toothache", "Body pain"],
                "typical_dosage": "1-2 tablets as needed, max 6 tablets/day",
                "administration": "Take with water after food",
                "common_side_effects": ["Stomach upset", "Nervousness", "Insomnia"],
                "contraindications": ["Peptic ulcer", "Kidney disease", "Pregnancy"],
                "alternatives": ["Dart", "Anadin"],
                "otc_status": "OTC",
                "approximate_price": "₹25-35 for 10 tablets"
            },
            {
                "brand_name": "Disprin",
                "generic_name": "Aspirin",
                "composition": [
                    {"ingredient": "Aspirin (Acetylsalicylic acid)", "strength": "350mg"}
                ],
                "drug_class": "NSAID/Analgesic",
                "common_uses": ["Headache", "Fever", "Body pain", "Inflammation"],
                "typical_dosage": "1-2 tablets dissolved in water every 4-6 hours",
                "administration": "Dissolve in water, take after food",
                "common_side_effects": ["Stomach irritation", "Nausea", "Bleeding risk"],
                "contraindications": ["Peptic ulcer", "Bleeding disorders", "Asthma", "Children under 16"],
                "alternatives": ["Ecosprin", "Aspirin"],
                "otc_status": "OTC",
                "approximate_price": "₹15-25 for 10 tablets"
            }
        ]
    },
    
    # ==========================================
    # BODY PAIN & MUSCLE PAIN
    # ==========================================
    "body_pain": {
        "symptoms": ["body pain", "muscle pain", "joint pain", "back pain", "leg pain", "arm pain"],
        "medicines": [
            {
                "brand_name": "Combiflam",
                "generic_name": "Ibuprofen + Paracetamol",
                "composition": [
                    {"ingredient": "Ibuprofen", "strength": "400mg"},
                    {"ingredient": "Paracetamol", "strength": "325mg"}
                ],
                "drug_class": "NSAID + Analgesic",
                "common_uses": ["Body pain", "Fever", "Headache", "Dental pain", "Muscle pain"],
                "typical_dosage": "1 tablet 2-3 times daily",
                "administration": "Take after food to avoid stomach irritation",
                "common_side_effects": ["Stomach upset", "Nausea", "Dizziness"],
                "contraindications": ["Peptic ulcer", "Kidney disease", "Heart disease", "Pregnancy (3rd trimester)"],
                "alternatives": ["Ibugesic Plus", "Brufen Plus", "Ibuclin"],
                "otc_status": "OTC",
                "approximate_price": "₹35-45 for 10 tablets"
            },
            {
                "brand_name": "Flexon",
                "generic_name": "Ibuprofen + Paracetamol",
                "composition": [
                    {"ingredient": "Ibuprofen", "strength": "400mg"},
                    {"ingredient": "Paracetamol", "strength": "325mg"}
                ],
                "drug_class": "NSAID + Analgesic",
                "common_uses": ["Muscle pain", "Joint pain", "Fever", "Inflammation"],
                "typical_dosage": "1 tablet every 8 hours",
                "administration": "Take with food",
                "common_side_effects": ["Gastric irritation", "Nausea"],
                "contraindications": ["GI bleeding", "Aspirin allergy"],
                "alternatives": ["Combiflam", "Ibugesic Plus"],
                "otc_status": "OTC",
                "approximate_price": "₹30-40 for 10 tablets"
            }
        ]
    },
    
    # ==========================================
    # COUGH
    # ==========================================
    "cough": {
        "symptoms": ["cough", "dry cough", "wet cough", "productive cough", "throat irritation"],
        "medicines": [
            {
                "brand_name": "Benadryl DR",
                "generic_name": "Dextromethorphan + Diphenhydramine + Ammonium Chloride",
                "composition": [
                    {"ingredient": "Dextromethorphan HBr", "strength": "10mg/5ml"},
                    {"ingredient": "Diphenhydramine HCl", "strength": "8mg/5ml"},
                    {"ingredient": "Ammonium Chloride", "strength": "125mg/5ml"}
                ],
                "drug_class": "Antitussive + Expectorant",
                "common_uses": ["Dry cough", "Allergic cough", "Cold symptoms"],
                "typical_dosage": "10ml (2 teaspoons) every 6-8 hours",
                "administration": "Take directly or with water. Don't exceed 4 doses/day",
                "common_side_effects": ["Drowsiness", "Dry mouth", "Dizziness"],
                "contraindications": ["MAO inhibitors", "Glaucoma", "Urinary retention"],
                "alternatives": ["Corex DX", "Ascoril D", "Torex"],
                "otc_status": "OTC",
                "approximate_price": "₹80-100 for 100ml"
            },
            {
                "brand_name": "Grilinctus",
                "generic_name": "Dextromethorphan + Phenylephrine + Chlorpheniramine",
                "composition": [
                    {"ingredient": "Dextromethorphan", "strength": "10mg/5ml"},
                    {"ingredient": "Phenylephrine", "strength": "5mg/5ml"},
                    {"ingredient": "Chlorpheniramine", "strength": "2mg/5ml"}
                ],
                "drug_class": "Antitussive + Decongestant",
                "common_uses": ["Dry cough", "Cold", "Congestion"],
                "typical_dosage": "10ml 3-4 times daily",
                "administration": "Take after meals",
                "common_side_effects": ["Drowsiness", "Nausea"],
                "contraindications": ["High blood pressure", "Diabetes"],
                "alternatives": ["Benadryl", "Chericof"],
                "otc_status": "OTC",
                "approximate_price": "₹70-90 for 100ml"
            }
        ]
    },
    
    # ==========================================
    # STOMACH PAIN & ACIDITY
    # ==========================================
    "acidity": {
        "symptoms": ["acidity", "heartburn", "acid reflux", "stomach burn", "chest burn", "sour taste"],
        "medicines": [
            {
                "brand_name": "Pan 40 (Pantocid)",
                "generic_name": "Pantoprazole",
                "composition": [
                    {"ingredient": "Pantoprazole Sodium", "strength": "40mg"}
                ],
                "drug_class": "Proton Pump Inhibitor (PPI)",
                "common_uses": ["Acidity", "GERD", "Peptic ulcer", "Gastritis"],
                "typical_dosage": "1 tablet once daily before breakfast",
                "administration": "Take 30-60 minutes before first meal on empty stomach",
                "common_side_effects": ["Headache", "Diarrhea", "Nausea"],
                "contraindications": ["Liver disease (use with caution)"],
                "alternatives": ["Pantocid", "Pantop", "P-40", "Pan-D"],
                "otc_status": "OTC",
                "approximate_price": "₹80-120 for 15 tablets"
            },
            {
                "brand_name": "Digene Gel/Tablet",
                "generic_name": "Magaldrate + Simethicone",
                "composition": [
                    {"ingredient": "Magaldrate", "strength": "400mg"},
                    {"ingredient": "Simethicone", "strength": "20mg"}
                ],
                "drug_class": "Antacid + Antiflatulent",
                "common_uses": ["Acidity", "Gas", "Bloating", "Heartburn"],
                "typical_dosage": "1-2 tablets or 10ml gel after meals",
                "administration": "Chew tablets or take gel directly",
                "common_side_effects": ["Constipation", "Diarrhea"],
                "contraindications": ["Kidney disease"],
                "alternatives": ["Gelusil", "Mucaine", "Rantac"],
                "otc_status": "OTC",
                "approximate_price": "₹50-80 for 15 tablets/170ml"
            }
        ]
    },
    
    # ==========================================
    # DIARRHEA & LOOSE MOTION
    # ==========================================
    "diarrhea": {
        "symptoms": ["diarrhea", "loose motion", "loose stool", "watery stool", "stomach cramps", "frequent bowel"],
        "medicines": [
            {
                "brand_name": "Eldoper (Loperamide)",
                "generic_name": "Loperamide",
                "composition": [
                    {"ingredient": "Loperamide Hydrochloride", "strength": "2mg"}
                ],
                "drug_class": "Antidiarrheal",
                "common_uses": ["Acute diarrhea", "Traveler's diarrhea"],
                "typical_dosage": "2 capsules initially, then 1 after each loose stool. Max 8/day",
                "administration": "Take with plenty of fluids",
                "common_side_effects": ["Constipation", "Abdominal cramps", "Dizziness"],
                "contraindications": ["Bloody diarrhea", "High fever", "Children under 2"],
                "alternatives": ["Imodium", "Lopamide", "Roko"],
                "otc_status": "OTC",
                "approximate_price": "₹30-50 for 10 capsules"
            },
            {
                "brand_name": "Electral/ORS",
                "generic_name": "Oral Rehydration Salts",
                "composition": [
                    {"ingredient": "Sodium Chloride", "strength": "2.6g/L"},
                    {"ingredient": "Potassium Chloride", "strength": "1.5g/L"},
                    {"ingredient": "Sodium Citrate", "strength": "2.9g/L"},
                    {"ingredient": "Glucose Anhydrous", "strength": "13.5g/L"}
                ],
                "drug_class": "Electrolyte replacement",
                "common_uses": ["Dehydration", "Diarrhea", "Vomiting", "Heat exhaustion"],
                "typical_dosage": "Dissolve 1 sachet in 1L water, drink throughout day",
                "administration": "Sip slowly and frequently",
                "common_side_effects": ["None when used as directed"],
                "contraindications": ["Severe kidney disease", "Intestinal obstruction"],
                "alternatives": ["Pedialyte", "Enerzal", "Glucon-D ORS"],
                "otc_status": "OTC",
                "approximate_price": "₹20-30 for 4 sachets"
            }
        ]
    },
    
    # ==========================================
    # ALLERGY & SKIN RASH
    # ==========================================
    "allergy": {
        "symptoms": ["allergy", "itching", "skin rash", "hives", "swelling", "sneezing", "watery eyes"],
        "medicines": [
            {
                "brand_name": "Allegra 120/180",
                "generic_name": "Fexofenadine",
                "composition": [
                    {"ingredient": "Fexofenadine Hydrochloride", "strength": "120mg/180mg"}
                ],
                "drug_class": "Non-sedating Antihistamine",
                "common_uses": ["Allergic rhinitis", "Urticaria", "Skin allergies", "Hay fever"],
                "typical_dosage": "1 tablet (120mg) twice daily or 180mg once daily",
                "administration": "Take with water, avoid fruit juices",
                "common_side_effects": ["Headache", "Nausea", "Drowsiness (rare)"],
                "contraindications": ["Severe kidney disease"],
                "alternatives": ["Fexova", "Telfast", "Histafree"],
                "otc_status": "OTC",
                "approximate_price": "₹150-200 for 10 tablets"
            },
            {
                "brand_name": "Avil 25",
                "generic_name": "Pheniramine Maleate",
                "composition": [
                    {"ingredient": "Pheniramine Maleate", "strength": "25mg"}
                ],
                "drug_class": "Antihistamine",
                "common_uses": ["Allergic reactions", "Itching", "Insect bites", "Drug allergies"],
                "typical_dosage": "1 tablet 2-3 times daily",
                "administration": "Take with or without food",
                "common_side_effects": ["Drowsiness", "Dry mouth", "Blurred vision"],
                "contraindications": ["Glaucoma", "Urinary retention", "Pregnancy"],
                "alternatives": ["Chlorpheniramine", "Piriton"],
                "otc_status": "OTC",
                "approximate_price": "₹15-25 for 10 tablets"
            }
        ]
    },
    
    # ==========================================
    # VOMITING & NAUSEA
    # ==========================================
    "nausea": {
        "symptoms": ["nausea", "vomiting", "feeling sick", "motion sickness", "morning sickness"],
        "medicines": [
            {
                "brand_name": "Domstal (Domperidone)",
                "generic_name": "Domperidone",
                "composition": [
                    {"ingredient": "Domperidone", "strength": "10mg"}
                ],
                "drug_class": "Antiemetic/Prokinetic",
                "common_uses": ["Nausea", "Vomiting", "Bloating", "Gastroparesis"],
                "typical_dosage": "1 tablet 15-30 minutes before meals, 3 times daily",
                "administration": "Take before food",
                "common_side_effects": ["Headache", "Dry mouth", "Abdominal cramps"],
                "contraindications": ["Heart arrhythmias", "Liver disease", "GI bleeding"],
                "alternatives": ["Vomistop", "Motilium", "Domcet"],
                "otc_status": "OTC",
                "approximate_price": "₹40-60 for 10 tablets"
            },
            {
                "brand_name": "Ondem (Ondansetron)",
                "generic_name": "Ondansetron",
                "composition": [
                    {"ingredient": "Ondansetron", "strength": "4mg"}
                ],
                "drug_class": "Antiemetic (5-HT3 antagonist)",
                "common_uses": ["Severe nausea", "Vomiting", "Chemotherapy-induced nausea"],
                "typical_dosage": "1 tablet every 8 hours as needed",
                "administration": "Take 30 minutes before meals or as needed",
                "common_side_effects": ["Headache", "Constipation", "Fatigue"],
                "contraindications": ["QT prolongation", "Severe liver disease"],
                "alternatives": ["Emeset", "Vomikind", "Zofran"],
                "otc_status": "Prescription recommended",
                "approximate_price": "₹50-80 for 10 tablets"
            }
        ]
    },
    
    # ==========================================
    # CONSTIPATION
    # ==========================================
    "constipation": {
        "symptoms": ["constipation", "hard stool", "difficulty passing stool", "bloating", "incomplete evacuation"],
        "medicines": [
            {
                "brand_name": "Cremaffin",
                "generic_name": "Liquid Paraffin + Milk of Magnesia",
                "composition": [
                    {"ingredient": "Liquid Paraffin", "strength": "3.75ml/5ml"},
                    {"ingredient": "Milk of Magnesia", "strength": "3.75ml/5ml"}
                ],
                "drug_class": "Laxative combination",
                "common_uses": ["Constipation", "Hard stools", "Bowel preparation"],
                "typical_dosage": "15-30ml at bedtime",
                "administration": "Take at night with water",
                "common_side_effects": ["Abdominal cramps", "Diarrhea if overused"],
                "contraindications": ["Intestinal obstruction", "Abdominal pain of unknown cause"],
                "alternatives": ["Softovac", "Duphalac", "Isabgol"],
                "otc_status": "OTC",
                "approximate_price": "₹100-150 for 225ml"
            },
            {
                "brand_name": "Dulcoflex",
                "generic_name": "Bisacodyl",
                "composition": [
                    {"ingredient": "Bisacodyl", "strength": "5mg"}
                ],
                "drug_class": "Stimulant Laxative",
                "common_uses": ["Constipation", "Bowel evacuation before procedures"],
                "typical_dosage": "1-2 tablets at bedtime",
                "administration": "Swallow whole, don't crush. Don't take with milk/antacids",
                "common_side_effects": ["Abdominal cramps", "Diarrhea"],
                "contraindications": ["Intestinal obstruction", "Acute abdominal conditions"],
                "alternatives": ["Laxopeg", "Evacool", "Julax"],
                "otc_status": "OTC",
                "approximate_price": "₹25-40 for 10 tablets"
            }
        ]
    },
    
    # ==========================================
    # THROAT PAIN & INFECTION
    # ==========================================
    "throat_infection": {
        "symptoms": ["sore throat", "throat pain", "difficulty swallowing", "throat infection", "tonsillitis"],
        "medicines": [
            {
                "brand_name": "Strepsils",
                "generic_name": "Dichlorobenzyl alcohol + Amylmetacresol",
                "composition": [
                    {"ingredient": "2,4-Dichlorobenzyl alcohol", "strength": "1.2mg"},
                    {"ingredient": "Amylmetacresol", "strength": "0.6mg"}
                ],
                "drug_class": "Antiseptic Lozenges",
                "common_uses": ["Sore throat", "Mouth infections", "Throat pain"],
                "typical_dosage": "Dissolve 1 lozenge slowly in mouth every 2-3 hours",
                "administration": "Let it dissolve slowly, don't chew",
                "common_side_effects": ["Mild irritation (rare)"],
                "contraindications": ["Children under 6"],
                "alternatives": ["Vicks Cough Drops", "Cofsils", "Halls"],
                "otc_status": "OTC",
                "approximate_price": "₹50-70 for 24 lozenges"
            },
            {
                "brand_name": "Betadine Gargle",
                "generic_name": "Povidone Iodine",
                "composition": [
                    {"ingredient": "Povidone Iodine", "strength": "2% w/v"}
                ],
                "drug_class": "Antiseptic",
                "common_uses": ["Throat infection", "Mouth ulcers", "Oral hygiene"],
                "typical_dosage": "Gargle with 10-20ml undiluted for 30 seconds, 4 times daily",
                "administration": "Gargle and spit out, don't swallow",
                "common_side_effects": ["Temporary teeth staining", "Metallic taste"],
                "contraindications": ["Thyroid disorders", "Iodine allergy", "Pregnancy"],
                "alternatives": ["Hexidine", "Chlorhexidine mouthwash"],
                "otc_status": "OTC",
                "approximate_price": "₹80-100 for 100ml"
            }
        ]
    },
    
    # ==========================================
    # DIABETES (Information only - requires prescription)
    # ==========================================
    "diabetes": {
        "symptoms": ["high blood sugar", "frequent urination", "excessive thirst", "diabetes", "sugar"],
        "medicines": [
            {
                "brand_name": "Glycomet/Glucophage",
                "generic_name": "Metformin",
                "composition": [
                    {"ingredient": "Metformin Hydrochloride", "strength": "500mg/850mg/1000mg"}
                ],
                "drug_class": "Biguanide (Antidiabetic)",
                "common_uses": ["Type 2 Diabetes", "PCOS", "Prediabetes"],
                "typical_dosage": "As prescribed by doctor - usually 500mg twice daily initially",
                "administration": "Take with meals to reduce GI side effects",
                "common_side_effects": ["Nausea", "Diarrhea", "Metallic taste", "B12 deficiency (long-term)"],
                "contraindications": ["Kidney disease", "Liver disease", "Heart failure", "Alcoholism"],
                "alternatives": ["Gluformin", "Obimet", "Walaphage"],
                "otc_status": "PRESCRIPTION REQUIRED",
                "approximate_price": "₹50-100 for 20 tablets"
            }
        ],
        "warning": "⚠️ Diabetes requires proper medical evaluation and prescription. Do not self-medicate."
    },
    
    # ==========================================
    # HYPERTENSION (Information only)
    # ==========================================
    "hypertension": {
        "symptoms": ["high blood pressure", "hypertension", "BP high", "headache with high BP"],
        "medicines": [
            {
                "brand_name": "Amlodipine (Amlong/Stamlo)",
                "generic_name": "Amlodipine",
                "composition": [
                    {"ingredient": "Amlodipine Besylate", "strength": "5mg/10mg"}
                ],
                "drug_class": "Calcium Channel Blocker",
                "common_uses": ["Hypertension", "Angina"],
                "typical_dosage": "As prescribed - usually 5mg once daily",
                "administration": "Take at the same time daily",
                "common_side_effects": ["Ankle swelling", "Flushing", "Headache", "Dizziness"],
                "contraindications": ["Severe hypotension", "Heart failure", "Aortic stenosis"],
                "alternatives": ["Amlokind", "Amtas", "Amlopress"],
                "otc_status": "PRESCRIPTION REQUIRED",
                "approximate_price": "₹30-60 for 14 tablets"
            }
        ],
        "warning": "⚠️ High blood pressure requires proper medical evaluation. Do not self-medicate."
    }
}

# Symptom keywords for matching
SYMPTOM_KEYWORDS = {
    "fever": ["fever", "temperature", "बुखार", "high temp", "febrile"],
    "headache": ["headache", "head pain", "head ache", "सिरदर्द", "migraine"],
    "cold": ["cold", "runny nose", "sneezing", "सर्दी", "जुकाम", "congestion"],
    "cough": ["cough", "खांसी", "coughing"],
    "body_pain": ["body pain", "muscle pain", "joint pain", "दर्द", "back pain"],
    "acidity": ["acidity", "heartburn", "एसिडिटी", "acid reflux", "gas", "bloating"],
    "diarrhea": ["diarrhea", "loose motion", "दस्त", "loose stool"],
    "allergy": ["allergy", "allergic", "एलर्जी", "itching", "rash", "hives"],
    "nausea": ["nausea", "vomiting", "उल्टी", "throwing up"],
    "constipation": ["constipation", "कब्ज", "hard stool"],
    "throat_infection": ["sore throat", "throat pain", "गला दर्द", "tonsil"]
}


def match_symptoms_to_diseases(symptoms: list) -> list:
    """Match symptoms to diseases and return medicine recommendations"""
    matched_diseases = []
    symptoms_lower = [s.lower() for s in symptoms]
    
    for disease, data in DISEASE_MEDICINE_DB.items():
        disease_symptoms = [s.lower() for s in data["symptoms"]]
        match_count = sum(1 for s in symptoms_lower if any(ds in s or s in ds for ds in disease_symptoms))
        
        if match_count > 0:
            matched_diseases.append({
                "disease": disease,
                "match_score": match_count,
                "data": data
            })
    
    # Sort by match score
    matched_diseases.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_diseases


def get_medicine_info(disease_key: str) -> dict:
    """Get medicine information for a specific disease"""
    return DISEASE_MEDICINE_DB.get(disease_key, {})
