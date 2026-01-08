"""
Comprehensive Medical Database
Contains drugs, remedies, conditions, and treatment protocols
"""

# ========================================
# COMPREHENSIVE DRUG DATABASE
# Organized by therapeutic category
# ========================================

DRUG_DATABASE = {
    # ==========================================
    # ANALGESICS (Pain Relievers)
    # ==========================================
    "pain": {
        "mild_to_moderate": [
            {"name": "Dolo 650 / Crocin (Paracetamol)", "dosage": "500-650mg", "frequency": "Every 4-6 hours", "max_daily": "4000mg", "category": "Analgesic", "warning": "Avoid alcohol, liver damage risk"},
            {"name": "Brufen / Combiflam (Ibuprofen)", "dosage": "200-400mg", "frequency": "Every 6-8 hours", "max_daily": "1200mg OTC", "category": "NSAID", "warning": "Take with food, avoid if kidney issues"},
            {"name": "Disprin / Ecosprin (Aspirin)", "dosage": "325-650mg", "frequency": "Every 4-6 hours", "max_daily": "4000mg", "category": "NSAID", "warning": "Not for children, bleeding risk"},
            {"name": "Naprosyn / Naxdom (Naproxen)", "dosage": "220-440mg", "frequency": "Every 8-12 hours", "max_daily": "660mg OTC", "category": "NSAID", "warning": "Take with food"},
            {"name": "Voveran / Diclomol (Diclofenac)", "dosage": "50mg", "frequency": "Every 8 hours", "max_daily": "150mg", "category": "NSAID", "warning": "Prescription in some countries"},
        ],
        "moderate_to_severe": [
            {"name": "Tramadol", "dosage": "50-100mg", "frequency": "Every 4-6 hours", "max_daily": "400mg", "category": "Opioid", "warning": "Prescription only, habit forming"},
            {"name": "Codeine", "dosage": "15-60mg", "frequency": "Every 4-6 hours", "max_daily": "240mg", "category": "Opioid", "warning": "Prescription only, constipation"},
        ],
        "topical": [
            {"name": "Diclofenac Gel", "dosage": "Apply thin layer", "frequency": "3-4 times daily", "category": "Topical NSAID", "warning": "External use only"},
            {"name": "Capsaicin Cream", "dosage": "Apply thin layer", "frequency": "3-4 times daily", "category": "Topical", "warning": "Wash hands after, avoid eyes"},
            {"name": "Methyl Salicylate Cream", "dosage": "Apply locally", "frequency": "3-4 times daily", "category": "Topical", "warning": "Do not use with heating pad"},
            {"name": "Lidocaine Patch", "dosage": "1 patch", "frequency": "12 hours on, 12 hours off", "category": "Local Anesthetic", "warning": "Prescription may be needed"},
        ]
    },

    # ==========================================
    # ANTIPYRETICS (Fever Reducers)
    # ==========================================
    "fever": {
        "adults": [
            {"name": "Dolo 650 / Calpol (Paracetamol)", "dosage": "500-650mg", "frequency": "Every 4-6 hours", "max_daily": "4000mg", "category": "Antipyretic", "warning": "Stay hydrated"},
            {"name": "Brufen / Ibugesic (Ibuprofen)", "dosage": "200-400mg", "frequency": "Every 6-8 hours", "max_daily": "1200mg", "category": "NSAID/Antipyretic", "warning": "Take with food"},
            {"name": "Disprin (Aspirin)", "dosage": "325-650mg", "frequency": "Every 4-6 hours", "category": "NSAID/Antipyretic", "warning": "Not for viral infections in children"},
        ],
        "children": [
            {"name": "Calpol / Crocin DS Syrup (Paracetamol)", "dosage": "10-15mg/kg", "frequency": "Every 4-6 hours", "category": "Pediatric Antipyretic", "warning": "Use dosing syringe"},
            {"name": "Ibugesic Plus / Brufen Syrup (Ibuprofen)", "dosage": "5-10mg/kg", "frequency": "Every 6-8 hours", "category": "Pediatric NSAID", "warning": "Not for infants <6 months"},
        ]
    },

    # ==========================================
    # ANTIHISTAMINES (Allergy)
    # ==========================================
    "allergy": {
        "non_sedating": [
            {"name": "Cetzine / Alerid (Cetirizine)", "dosage": "10mg", "frequency": "Once daily", "category": "2nd Gen Antihistamine", "warning": "May cause mild drowsiness"},
            {"name": "Lorfast / Claritin (Loratadine)", "dosage": "10mg", "frequency": "Once daily", "category": "2nd Gen Antihistamine", "warning": "Non-drowsy"},
            {"name": "Allegra / Fexova (Fexofenadine)", "dosage": "180mg", "frequency": "Once daily", "category": "2nd Gen Antihistamine", "warning": "Avoid fruit juice"},
            {"name": "Deslor (Desloratadine)", "dosage": "5mg", "frequency": "Once daily", "category": "2nd Gen Antihistamine", "warning": "Non-drowsy"},
            {"name": "Xyzal / Levocet (Levocetirizine)", "dosage": "5mg", "frequency": "Once daily", "category": "2nd Gen Antihistamine", "warning": "Evening dose preferred"},
        ],
        "sedating": [
            {"name": "Diphenhydramine (Benadryl)", "dosage": "25-50mg", "frequency": "Every 6-8 hours", "category": "1st Gen Antihistamine", "warning": "Causes drowsiness"},
            {"name": "Chlorpheniramine", "dosage": "4mg", "frequency": "Every 4-6 hours", "category": "1st Gen Antihistamine", "warning": "Causes drowsiness"},
            {"name": "Promethazine", "dosage": "25mg", "frequency": "Every 6-8 hours", "category": "1st Gen Antihistamine", "warning": "Very sedating"},
        ],
        "nasal_sprays": [
            {"name": "Fluticasone (Flonase)", "dosage": "1-2 sprays each nostril", "frequency": "Once daily", "category": "Nasal Corticosteroid", "warning": "Regular use needed"},
            {"name": "Budesonide (Rhinocort)", "dosage": "1-2 sprays each nostril", "frequency": "Once daily", "category": "Nasal Corticosteroid", "warning": "May take days to work"},
            {"name": "Oxymetazoline (Afrin)", "dosage": "2-3 sprays each nostril", "frequency": "Every 12 hours", "category": "Decongestant", "warning": "Max 3 days use"},
            {"name": "Azelastine", "dosage": "1-2 sprays each nostril", "frequency": "Twice daily", "category": "Antihistamine Spray", "warning": "Bitter taste"},
        ],
        "eye_drops": [
            {"name": "Ketotifen (Zaditor)", "dosage": "1 drop each eye", "frequency": "Twice daily", "category": "Antihistamine Eye Drop", "warning": "Remove contacts first"},
            {"name": "Olopatadine (Patanol)", "dosage": "1 drop each eye", "frequency": "Twice daily", "category": "Antihistamine Eye Drop", "warning": "Prescription"},
        ]
    },

    # ==========================================
    # GASTROINTESTINAL
    # ==========================================
    "gastric": {
        "antacids": [
            {"name": "Aluminum Hydroxide + Magnesium Hydroxide (Maalox)", "dosage": "10-20ml", "frequency": "After meals & bedtime", "category": "Antacid", "warning": "May cause constipation/diarrhea"},
            {"name": "Calcium Carbonate (Tums)", "dosage": "500-1000mg", "frequency": "As needed", "max_daily": "7500mg", "category": "Antacid", "warning": "May cause constipation"},
            {"name": "Sodium Bicarbonate", "dosage": "1/2 tsp in water", "frequency": "As needed", "category": "Antacid", "warning": "High sodium, short-term only"},
        ],
        "h2_blockers": [
            {"name": "Famotidine (Pepcid)", "dosage": "20-40mg", "frequency": "Once or twice daily", "category": "H2 Blocker", "warning": "Take before meals"},
            {"name": "Ranitidine (Zantac)", "dosage": "150mg", "frequency": "Twice daily", "category": "H2 Blocker", "warning": "Recalled in some countries"},
            {"name": "Cimetidine (Tagamet)", "dosage": "200-400mg", "frequency": "Twice daily", "category": "H2 Blocker", "warning": "Drug interactions"},
        ],
        "ppi": [
            {"name": "Omeprazole (Prilosec)", "dosage": "20mg", "frequency": "Once daily before breakfast", "category": "PPI", "warning": "Long-term use concerns"},
            {"name": "Esomeprazole (Nexium)", "dosage": "20-40mg", "frequency": "Once daily", "category": "PPI", "warning": "Take on empty stomach"},
            {"name": "Lansoprazole (Prevacid)", "dosage": "15-30mg", "frequency": "Once daily", "category": "PPI", "warning": "Before meals"},
            {"name": "Pantoprazole (Protonix)", "dosage": "20-40mg", "frequency": "Once daily", "category": "PPI", "warning": "Prescription strength available"},
            {"name": "Rabeprazole (Aciphex)", "dosage": "20mg", "frequency": "Once daily", "category": "PPI", "warning": "Prescription"},
        ],
        "antidiarrheal": [
            {"name": "Eldoper / Imodium (Loperamide)", "dosage": "2mg initially, then 1mg after each stool", "frequency": "As needed", "max_daily": "8mg", "category": "Antidiarrheal", "warning": "Not for bacterial diarrhea"},
            {"name": "Pepto-Bismol (Bismuth Subsalicylate)", "dosage": "30ml or 2 tablets", "frequency": "Every 30-60 min", "max_daily": "8 doses", "category": "Antidiarrheal", "warning": "Black stool is normal"},
            {"name": "Electral / ORS (Oral Rehydration Salts)", "dosage": "1 packet in 1L water", "frequency": "Throughout day", "category": "Rehydration", "warning": "Essential for diarrhea"},
            {"name": "Norflox TZ / Oflox OZ (Ofloxacin+Ornidazole)", "dosage": "1 tablet", "frequency": "Twice daily", "category": "Antibiotic", "warning": "For infectious diarrhea only, prescription required"},
            {"name": "Metrogyl / Flagyl (Metronidazole)", "dosage": "400mg", "frequency": "Three times daily", "category": "Antibiotic", "warning": "For amoebic dysentery, avoid alcohol"},
            {"name": "Racecadotril (Redotil)", "dosage": "100mg", "frequency": "Three times daily", "category": "Antisecretory", "warning": "Reduces fluid loss"},
        ],
        "laxatives": [
            {"name": "Polyethylene Glycol (Miralax)", "dosage": "17g in 8oz liquid", "frequency": "Once daily", "category": "Osmotic Laxative", "warning": "Gentle, may take 1-3 days"},
            {"name": "Bisacodyl (Dulcolax)", "dosage": "5-15mg", "frequency": "Once daily", "category": "Stimulant Laxative", "warning": "Works in 6-12 hours"},
            {"name": "Senna (Senokot)", "dosage": "15-30mg", "frequency": "Once daily at bedtime", "category": "Stimulant Laxative", "warning": "Works in 6-12 hours"},
            {"name": "Psyllium (Metamucil)", "dosage": "1 tsp in 8oz water", "frequency": "1-3 times daily", "category": "Bulk-Forming Laxative", "warning": "Drink plenty of water"},
            {"name": "Docusate (Colace)", "dosage": "100-300mg", "frequency": "Once daily", "category": "Stool Softener", "warning": "Gentle, for prevention"},
            {"name": "Lactulose", "dosage": "15-30ml", "frequency": "Once daily", "category": "Osmotic Laxative", "warning": "May cause gas"},
        ],
        "antiemetics": [
            {"name": "Ondansetron (Zofran)", "dosage": "4-8mg", "frequency": "Every 8 hours", "category": "5-HT3 Antagonist", "warning": "Prescription, very effective"},
            {"name": "Domperidone (Motilium)", "dosage": "10mg", "frequency": "Before meals", "category": "Prokinetic", "warning": "Not available in USA"},
            {"name": "Metoclopramide (Reglan)", "dosage": "10mg", "frequency": "Before meals", "category": "Prokinetic", "warning": "Short-term use only"},
            {"name": "Dimenhydrinate (Dramamine)", "dosage": "50-100mg", "frequency": "Every 4-6 hours", "category": "Antiemetic", "warning": "Causes drowsiness"},
            {"name": "Meclizine (Bonine)", "dosage": "25-50mg", "frequency": "Once daily", "category": "Antiemetic", "warning": "For motion sickness"},
            {"name": "Promethazine (Phenergan)", "dosage": "12.5-25mg", "frequency": "Every 4-6 hours", "category": "Antiemetic", "warning": "Very sedating"},
        ],
        "antispasmodics": [
            {"name": "Dicyclomine (Bentyl)", "dosage": "10-20mg", "frequency": "3-4 times daily", "category": "Antispasmodic", "warning": "For IBS cramps"},
            {"name": "Hyoscine Butylbromide (Buscopan)", "dosage": "10-20mg", "frequency": "3-4 times daily", "category": "Antispasmodic", "warning": "For abdominal cramps"},
            {"name": "Mebeverine", "dosage": "135mg", "frequency": "3 times daily before meals", "category": "Antispasmodic", "warning": "For IBS"},
        ]
    },

    # ==========================================
    # RESPIRATORY
    # ==========================================
    "respiratory": {
        "cough_suppressants": [
            {"name": "Dextromethorphan (DM)", "dosage": "10-20mg", "frequency": "Every 4 hours", "max_daily": "120mg", "category": "Antitussive", "warning": "For dry cough only"},
            {"name": "Codeine", "dosage": "10-20mg", "frequency": "Every 4-6 hours", "category": "Opioid Antitussive", "warning": "Prescription, habit-forming"},
            {"name": "Benzonatate (Tessalon)", "dosage": "100-200mg", "frequency": "3 times daily", "category": "Antitussive", "warning": "Swallow whole, prescription"},
        ],
        "expectorants": [
            {"name": "Guaifenesin (Mucinex)", "dosage": "200-400mg", "frequency": "Every 4 hours", "max_daily": "2400mg", "category": "Expectorant", "warning": "Drink plenty of water"},
            {"name": "Ambroxol", "dosage": "30mg", "frequency": "2-3 times daily", "category": "Mucolytic", "warning": "For productive cough"},
            {"name": "Bromhexine", "dosage": "8mg", "frequency": "3 times daily", "category": "Mucolytic", "warning": "Thins mucus"},
            {"name": "Acetylcysteine (NAC)", "dosage": "200mg", "frequency": "3 times daily", "category": "Mucolytic", "warning": "Effervescent tablets available"},
        ],
        "decongestants": [
            {"name": "Pseudoephedrine (Sudafed)", "dosage": "60mg", "frequency": "Every 4-6 hours", "max_daily": "240mg", "category": "Decongestant", "warning": "May raise BP, behind counter"},
            {"name": "Phenylephrine", "dosage": "10mg", "frequency": "Every 4 hours", "category": "Decongestant", "warning": "Less effective than pseudoephedrine"},
            {"name": "Xylometazoline Nasal Spray", "dosage": "2-3 sprays each nostril", "frequency": "Every 8-10 hours", "category": "Nasal Decongestant", "warning": "Max 5-7 days"},
        ],
        "bronchodilators": [
            {"name": "Salbutamol/Albuterol Inhaler", "dosage": "1-2 puffs", "frequency": "Every 4-6 hours as needed", "category": "SABA", "warning": "Rescue inhaler"},
            {"name": "Ipratropium (Atrovent)", "dosage": "2 puffs", "frequency": "4 times daily", "category": "Anticholinergic", "warning": "Prescription"},
            {"name": "Theophylline", "dosage": "100-300mg", "frequency": "Twice daily", "category": "Methylxanthine", "warning": "Narrow therapeutic window"},
        ],
        "corticosteroid_inhalers": [
            {"name": "Budesonide Inhaler (Pulmicort)", "dosage": "200-400mcg", "frequency": "Twice daily", "category": "ICS", "warning": "Controller, rinse mouth after"},
            {"name": "Fluticasone Inhaler (Flovent)", "dosage": "88-440mcg", "frequency": "Twice daily", "category": "ICS", "warning": "Controller medication"},
            {"name": "Beclomethasone", "dosage": "80-160mcg", "frequency": "Twice daily", "category": "ICS", "warning": "Regular use needed"},
        ]
    },

    # ==========================================
    # ANTIBIOTICS (Prescription - For Reference)
    # ==========================================
    "antibiotics": {
        "penicillins": [
            {"name": "Amoxicillin", "dosage": "500mg", "frequency": "Every 8 hours", "duration": "7-10 days", "category": "Penicillin", "warning": "Complete full course"},
            {"name": "Amoxicillin-Clavulanate (Augmentin)", "dosage": "625mg", "frequency": "Every 8 hours", "category": "Penicillin + Beta-lactamase inhibitor", "warning": "Take with food"},
            {"name": "Ampicillin", "dosage": "500mg", "frequency": "Every 6 hours", "category": "Penicillin", "warning": "Take on empty stomach"},
        ],
        "cephalosporins": [
            {"name": "Cephalexin (Keflex)", "dosage": "500mg", "frequency": "Every 6-12 hours", "category": "1st Gen Cephalosporin", "warning": "Complete course"},
            {"name": "Cefuroxime (Ceftin)", "dosage": "250-500mg", "frequency": "Twice daily", "category": "2nd Gen Cephalosporin", "warning": "Take with food"},
            {"name": "Cefixime (Suprax)", "dosage": "400mg", "frequency": "Once daily", "category": "3rd Gen Cephalosporin", "warning": "Broad spectrum"},
            {"name": "Ceftriaxone", "dosage": "1-2g", "frequency": "Once daily IV/IM", "category": "3rd Gen Cephalosporin", "warning": "Hospital use"},
        ],
        "macrolides": [
            {"name": "Azithromycin (Zithromax)", "dosage": "500mg day 1, then 250mg", "frequency": "Once daily for 5 days", "category": "Macrolide", "warning": "Z-pack, take on empty stomach"},
            {"name": "Clarithromycin (Biaxin)", "dosage": "500mg", "frequency": "Twice daily", "category": "Macrolide", "warning": "Drug interactions"},
            {"name": "Erythromycin", "dosage": "250-500mg", "frequency": "Every 6 hours", "category": "Macrolide", "warning": "GI upset common"},
        ],
        "fluoroquinolones": [
            {"name": "Ciprofloxacin (Cipro)", "dosage": "500mg", "frequency": "Twice daily", "category": "Fluoroquinolone", "warning": "Avoid dairy, tendon risk"},
            {"name": "Levofloxacin (Levaquin)", "dosage": "500-750mg", "frequency": "Once daily", "category": "Fluoroquinolone", "warning": "Tendon rupture risk"},
            {"name": "Moxifloxacin (Avelox)", "dosage": "400mg", "frequency": "Once daily", "category": "Fluoroquinolone", "warning": "QT prolongation"},
            {"name": "Ofloxacin", "dosage": "200-400mg", "frequency": "Twice daily", "category": "Fluoroquinolone", "warning": "Broad spectrum"},
        ],
        "tetracyclines": [
            {"name": "Doxycycline", "dosage": "100mg", "frequency": "Twice daily", "category": "Tetracycline", "warning": "Avoid sun, dairy, antacids"},
            {"name": "Minocycline", "dosage": "100mg", "frequency": "Twice daily", "category": "Tetracycline", "warning": "Dizziness possible"},
        ],
        "sulfonamides": [
            {"name": "Trimethoprim-Sulfamethoxazole (Bactrim)", "dosage": "1 DS tablet", "frequency": "Twice daily", "category": "Sulfonamide", "warning": "Allergies common, drink water"},
        ],
        "others": [
            {"name": "Metronidazole (Flagyl)", "dosage": "500mg", "frequency": "Every 8 hours", "category": "Nitroimidazole", "warning": "No alcohol"},
            {"name": "Clindamycin", "dosage": "300mg", "frequency": "Every 6 hours", "category": "Lincosamide", "warning": "C. diff risk"},
            {"name": "Nitrofurantoin (Macrobid)", "dosage": "100mg", "frequency": "Twice daily", "category": "Nitrofuran", "warning": "For UTI only, take with food"},
        ]
    },

    # ==========================================
    # ANTIFUNGALS
    # ==========================================
    "antifungal": {
        "topical": [
            {"name": "Clotrimazole (Lotrimin)", "dosage": "Apply thin layer", "frequency": "Twice daily", "duration": "2-4 weeks", "category": "Azole Antifungal", "warning": "Continue 1-2 weeks after clearing"},
            {"name": "Miconazole (Monistat)", "dosage": "Apply locally", "frequency": "Twice daily", "category": "Azole Antifungal", "warning": "For yeast infections"},
            {"name": "Terbinafine Cream (Lamisil)", "dosage": "Apply thin layer", "frequency": "Once or twice daily", "duration": "1-2 weeks", "category": "Allylamine", "warning": "Effective for athlete's foot"},
            {"name": "Ketoconazole Cream", "dosage": "Apply locally", "frequency": "Once or twice daily", "category": "Azole Antifungal", "warning": "For dandruff, tinea"},
            {"name": "Nystatin Cream", "dosage": "Apply locally", "frequency": "2-3 times daily", "category": "Polyene", "warning": "For candida"},
        ],
        "oral": [
            {"name": "Fluconazole (Diflucan)", "dosage": "150mg single dose or 50-200mg", "frequency": "Daily for systemic", "category": "Azole Antifungal", "warning": "Prescription, liver monitoring"},
            {"name": "Itraconazole (Sporanox)", "dosage": "100-200mg", "frequency": "Once or twice daily", "category": "Azole Antifungal", "warning": "Take with food"},
            {"name": "Terbinafine Tablets", "dosage": "250mg", "frequency": "Once daily", "duration": "6-12 weeks", "category": "Allylamine", "warning": "For nail fungus, liver monitoring"},
            {"name": "Griseofulvin", "dosage": "500mg", "frequency": "Once daily", "category": "Antifungal", "warning": "Take with fatty food"},
        ]
    },

    # ==========================================
    # ANTIVIRALS
    # ==========================================
    "antiviral": {
        "herpes": [
            {"name": "Acyclovir (Zovirax)", "dosage": "400mg", "frequency": "3 times daily", "duration": "5-10 days", "category": "Nucleoside Analog", "warning": "Start early for best effect"},
            {"name": "Valacyclovir (Valtrex)", "dosage": "500mg-1g", "frequency": "Twice daily", "category": "Nucleoside Analog", "warning": "Better absorption than acyclovir"},
            {"name": "Famciclovir", "dosage": "250-500mg", "frequency": "3 times daily", "category": "Nucleoside Analog", "warning": "Alternative to valacyclovir"},
        ],
        "influenza": [
            {"name": "Oseltamivir (Tamiflu)", "dosage": "75mg", "frequency": "Twice daily for 5 days", "category": "Neuraminidase Inhibitor", "warning": "Start within 48 hours of symptoms"},
            {"name": "Zanamivir (Relenza)", "dosage": "10mg inhaled", "frequency": "Twice daily for 5 days", "category": "Neuraminidase Inhibitor", "warning": "Inhaled, not for asthmatics"},
        ],
        "hepatitis": [
            {"name": "Entecavir", "dosage": "0.5-1mg", "frequency": "Once daily", "category": "HBV Antiviral", "warning": "For Hepatitis B"},
            {"name": "Tenofovir", "dosage": "300mg", "frequency": "Once daily", "category": "HBV Antiviral", "warning": "Kidney monitoring needed"},
            {"name": "Sofosbuvir", "dosage": "400mg", "frequency": "Once daily", "category": "HCV Antiviral", "warning": "For Hepatitis C, expensive"},
        ]
    },

    # ==========================================
    # CARDIOVASCULAR
    # ==========================================
    "cardiovascular": {
        "antihypertensives": [
            {"name": "Amlodipine", "dosage": "5-10mg", "frequency": "Once daily", "category": "Calcium Channel Blocker", "warning": "Ankle swelling possible"},
            {"name": "Lisinopril", "dosage": "10-40mg", "frequency": "Once daily", "category": "ACE Inhibitor", "warning": "Dry cough side effect"},
            {"name": "Losartan", "dosage": "50-100mg", "frequency": "Once daily", "category": "ARB", "warning": "Monitor potassium"},
            {"name": "Metoprolol", "dosage": "25-100mg", "frequency": "Once or twice daily", "category": "Beta Blocker", "warning": "Don't stop suddenly"},
            {"name": "Atenolol", "dosage": "25-100mg", "frequency": "Once daily", "category": "Beta Blocker", "warning": "Don't stop suddenly"},
            {"name": "Hydrochlorothiazide", "dosage": "12.5-25mg", "frequency": "Once daily", "category": "Thiazide Diuretic", "warning": "Monitor potassium"},
        ],
        "cholesterol": [
            {"name": "Atorvastatin (Lipitor)", "dosage": "10-80mg", "frequency": "Once daily", "category": "Statin", "warning": "Take at night, muscle pain possible"},
            {"name": "Rosuvastatin (Crestor)", "dosage": "5-40mg", "frequency": "Once daily", "category": "Statin", "warning": "Most potent statin"},
            {"name": "Simvastatin (Zocor)", "dosage": "10-40mg", "frequency": "Once daily at night", "category": "Statin", "warning": "Drug interactions"},
            {"name": "Pravastatin", "dosage": "10-80mg", "frequency": "Once daily", "category": "Statin", "warning": "Fewer interactions"},
            {"name": "Ezetimibe (Zetia)", "dosage": "10mg", "frequency": "Once daily", "category": "Cholesterol Absorption Inhibitor", "warning": "Often combined with statin"},
        ],
        "anticoagulants": [
            {"name": "Aspirin (low dose)", "dosage": "75-100mg", "frequency": "Once daily", "category": "Antiplatelet", "warning": "For heart protection"},
            {"name": "Clopidogrel (Plavix)", "dosage": "75mg", "frequency": "Once daily", "category": "Antiplatelet", "warning": "After stent or stroke"},
            {"name": "Warfarin (Coumadin)", "dosage": "Variable", "frequency": "Once daily", "category": "Vitamin K Antagonist", "warning": "INR monitoring needed"},
            {"name": "Rivaroxaban (Xarelto)", "dosage": "10-20mg", "frequency": "Once daily", "category": "DOAC", "warning": "No monitoring needed"},
            {"name": "Apixaban (Eliquis)", "dosage": "5mg", "frequency": "Twice daily", "category": "DOAC", "warning": "Safer bleeding profile"},
        ]
    },

    # ==========================================
    # DIABETES
    # ==========================================
    "diabetes": {
        "oral": [
            {"name": "Metformin", "dosage": "500-2000mg", "frequency": "With meals", "category": "Biguanide", "warning": "GI upset initially, take with food"},
            {"name": "Glimepiride", "dosage": "1-4mg", "frequency": "Once daily with breakfast", "category": "Sulfonylurea", "warning": "Hypoglycemia risk"},
            {"name": "Gliclazide", "dosage": "40-320mg", "frequency": "Once or twice daily", "category": "Sulfonylurea", "warning": "Take with meals"},
            {"name": "Sitagliptin (Januvia)", "dosage": "100mg", "frequency": "Once daily", "category": "DPP-4 Inhibitor", "warning": "Can combine with metformin"},
            {"name": "Empagliflozin (Jardiance)", "dosage": "10-25mg", "frequency": "Once daily", "category": "SGLT2 Inhibitor", "warning": "UTI risk, hydrate well"},
            {"name": "Pioglitazone", "dosage": "15-45mg", "frequency": "Once daily", "category": "Thiazolidinedione", "warning": "Weight gain, edema"},
        ],
        "insulin": [
            {"name": "Insulin Glargine (Lantus)", "dosage": "Variable", "frequency": "Once daily", "category": "Long-acting Insulin", "warning": "Basal insulin"},
            {"name": "Insulin Lispro (Humalog)", "dosage": "Variable", "frequency": "Before meals", "category": "Rapid-acting Insulin", "warning": "Mealtime insulin"},
            {"name": "NPH Insulin", "dosage": "Variable", "frequency": "Once or twice daily", "category": "Intermediate Insulin", "warning": "Mix gently, don't shake"},
        ]
    },

    # ==========================================
    # MENTAL HEALTH
    # ==========================================
    "mental_health": {
        "antidepressants_ssri": [
            {"name": "Serta / Zoloft (Sertraline)", "dosage": "50-200mg", "frequency": "Once daily", "category": "SSRI", "warning": "May take 2-4 weeks to work, prescription required"},
            {"name": "Nexito / Stalopam (Escitalopram)", "dosage": "10-20mg", "frequency": "Once daily", "category": "SSRI", "warning": "Well tolerated, prescription required"},
            {"name": "Fludac / Prozac (Fluoxetine)", "dosage": "20-80mg", "frequency": "Once daily", "category": "SSRI", "warning": "Long half-life, prescription required"},
            {"name": "Paxidep (Paroxetine)", "dosage": "20-50mg", "frequency": "Once daily", "category": "SSRI", "warning": "Withdrawal symptoms if stopped abruptly"},
        ],
        "antidepressants_snri": [
            {"name": "Venlor / Effexor (Venlafaxine)", "dosage": "75-225mg", "frequency": "Once daily XR", "category": "SNRI", "warning": "May raise BP, prescription required"},
            {"name": "Dulane / Cymbalta (Duloxetine)", "dosage": "30-60mg", "frequency": "Once daily", "category": "SNRI", "warning": "Also for pain, prescription required"},
        ],
        "antidepressants_other": [
            {"name": "Bupron (Bupropion)", "dosage": "150-300mg", "frequency": "Once or twice daily", "category": "NDRI", "warning": "No sexual side effects, seizure risk"},
            {"name": "Mirtaz (Mirtazapine)", "dosage": "15-45mg", "frequency": "At bedtime", "category": "NaSSA", "warning": "Weight gain, sedating"},
            {"name": "Trazodone", "dosage": "50-150mg", "frequency": "At bedtime", "category": "SARI", "warning": "Often for sleep"},
        ],
        "anxiolytics": [
            {"name": "Buspin (Buspirone)", "dosage": "5-15mg", "frequency": "2-3 times daily", "category": "Anxiolytic", "warning": "Takes 2-4 weeks, non-habit forming"},
            {"name": "Atarax (Hydroxyzine)", "dosage": "25-50mg", "frequency": "3-4 times daily", "category": "Antihistamine/Anxiolytic", "warning": "Sedating, prescription required"},
        ],
        "benzodiazepines": [
            {"name": "Alprax / Anxit (Alprazolam)", "dosage": "0.25-0.5mg", "frequency": "3 times daily", "category": "Benzodiazepine", "warning": "Short-term only, addictive, prescription required"},
            {"name": "Ativan / Lopez (Lorazepam)", "dosage": "0.5-2mg", "frequency": "2-3 times daily", "category": "Benzodiazepine", "warning": "Short-term only, prescription required"},
            {"name": "Clonotril / Lonazep (Clonazepam)", "dosage": "0.5-2mg", "frequency": "Twice daily", "category": "Benzodiazepine", "warning": "Longer acting, prescription required"},
            {"name": "Valium / Calmpose (Diazepam)", "dosage": "2-10mg", "frequency": "2-4 times daily", "category": "Benzodiazepine", "warning": "Long half-life, prescription required"},
        ],
        "otc_stress_relief": [
            {"name": "Ashwagandha (Ashvagandha)", "dosage": "300-600mg", "frequency": "Once or twice daily", "category": "Herbal Adaptogen", "warning": "OTC, may take 2-4 weeks for full effect"},
            {"name": "Brahmi (Bacopa)", "dosage": "300-450mg", "frequency": "Once daily", "category": "Herbal Nootropic", "warning": "OTC, helps with memory and stress"},
            {"name": "L-Theanine", "dosage": "100-200mg", "frequency": "As needed", "category": "Amino Acid", "warning": "OTC, promotes relaxation without drowsiness"},
            {"name": "Magnesium Glycinate", "dosage": "200-400mg", "frequency": "At bedtime", "category": "Mineral Supplement", "warning": "OTC, helps with relaxation and sleep"},
            {"name": "Himalaya Stress Care / Tentex Forte", "dosage": "As directed", "frequency": "Twice daily", "category": "Herbal Supplement", "warning": "OTC, Ayurvedic stress relief"},
        ],
        "sleep": [
            {"name": "Zolfresh / Ambien (Zolpidem)", "dosage": "5-10mg", "frequency": "At bedtime", "category": "Z-Drug", "warning": "Short-term only, complex behaviors, prescription required"},
            {"name": "Lunesta (Eszopiclone)", "dosage": "1-3mg", "frequency": "At bedtime", "category": "Z-Drug", "warning": "Metallic taste, prescription required"},
            {"name": "Melatonin", "dosage": "0.5-5mg", "frequency": "30-60 min before bed", "category": "Hormone", "warning": "OTC, start low"},
            {"name": "Benadryl / Avil (Diphenhydramine)", "dosage": "25-50mg", "frequency": "At bedtime", "category": "Antihistamine", "warning": "OTC, tolerance develops"},
        ]
    },

    # ==========================================
    # DERMATOLOGY
    # ==========================================
    "skin": {
        "corticosteroids": [
            {"name": "Hydrocortisone 1% Cream", "dosage": "Apply thin layer", "frequency": "2-3 times daily", "category": "Mild Corticosteroid", "warning": "OTC, not for face long-term"},
            {"name": "Triamcinolone Cream", "dosage": "Apply thin layer", "frequency": "2-3 times daily", "category": "Medium Corticosteroid", "warning": "Prescription"},
            {"name": "Betamethasone Cream", "dosage": "Apply thin layer", "frequency": "1-2 times daily", "category": "Strong Corticosteroid", "warning": "Not for face"},
            {"name": "Clobetasol Cream", "dosage": "Apply thin layer", "frequency": "Twice daily", "category": "Super Potent Corticosteroid", "warning": "Max 2 weeks"},
        ],
        "antifungal_skin": [
            {"name": "Clotrimazole Cream", "dosage": "Apply locally", "frequency": "Twice daily", "category": "Antifungal", "warning": "For ringworm, athlete's foot"},
            {"name": "Terbinafine Cream", "dosage": "Apply locally", "frequency": "Once or twice daily", "category": "Antifungal", "warning": "Very effective"},
            {"name": "Ketoconazole Shampoo", "dosage": "Apply to scalp", "frequency": "Twice weekly", "category": "Antifungal", "warning": "For dandruff, seborrhea"},
        ],
        "antibacterial_skin": [
            {"name": "Mupirocin (Bactroban)", "dosage": "Apply locally", "frequency": "3 times daily", "category": "Topical Antibiotic", "warning": "For impetigo, MRSA"},
            {"name": "Fusidic Acid Cream", "dosage": "Apply locally", "frequency": "3 times daily", "category": "Topical Antibiotic", "warning": "For skin infections"},
            {"name": "Neosporin", "dosage": "Apply locally", "frequency": "1-3 times daily", "category": "Triple Antibiotic", "warning": "OTC, for minor wounds"},
        ],
        "acne": [
            {"name": "Benzoyl Peroxide", "dosage": "Apply thin layer", "frequency": "Once or twice daily", "category": "Keratolytic", "warning": "Start 2.5%, may bleach fabrics"},
            {"name": "Salicylic Acid", "dosage": "Apply locally", "frequency": "1-2 times daily", "category": "Keratolytic", "warning": "OTC, for mild acne"},
            {"name": "Adapalene (Differin)", "dosage": "Apply thin layer", "frequency": "Once daily at night", "category": "Retinoid", "warning": "OTC, irritation initially"},
            {"name": "Tretinoin (Retin-A)", "dosage": "Apply pea-size amount", "frequency": "Once daily at night", "category": "Retinoid", "warning": "Prescription, sun sensitivity"},
            {"name": "Clindamycin Gel", "dosage": "Apply locally", "frequency": "Twice daily", "category": "Topical Antibiotic", "warning": "For inflammatory acne"},
        ],
        "moisturizers": [
            {"name": "Petroleum Jelly (Vaseline)", "dosage": "Apply as needed", "frequency": "Multiple times daily", "category": "Occlusive", "warning": "Best for very dry skin"},
            {"name": "Cerave Moisturizer", "dosage": "Apply liberally", "frequency": "Twice daily", "category": "Ceramide-based", "warning": "For eczema-prone skin"},
            {"name": "Aquaphor", "dosage": "Apply as needed", "frequency": "Multiple times daily", "category": "Occlusive", "warning": "For healing, very dry skin"},
        ],
        "antipruritic": [
            {"name": "Calamine Lotion", "dosage": "Apply locally", "frequency": "As needed", "category": "Antipruritic", "warning": "For itching, rashes"},
            {"name": "Pramoxine Cream", "dosage": "Apply locally", "frequency": "3-4 times daily", "category": "Local Anesthetic", "warning": "For itch relief"},
            {"name": "Menthol Cream", "dosage": "Apply locally", "frequency": "As needed", "category": "Counter-irritant", "warning": "Cooling sensation"},
        ]
    },

    # ==========================================
    # HEADACHE & MIGRAINE
    # ==========================================
    "headache": {
        "acute": [
            {"name": "Paracetamol", "dosage": "1000mg", "frequency": "Every 4-6 hours", "category": "Analgesic", "warning": "Max 4g/day"},
            {"name": "Ibuprofen", "dosage": "400-600mg", "frequency": "Every 6-8 hours", "category": "NSAID", "warning": "Take with food"},
            {"name": "Aspirin", "dosage": "900-1000mg", "frequency": "Every 4-6 hours", "category": "NSAID", "warning": "Effervescent works faster"},
            {"name": "Naproxen", "dosage": "500mg", "frequency": "Every 12 hours", "category": "NSAID", "warning": "Longer lasting"},
            {"name": "Excedrin (Aspirin+Paracetamol+Caffeine)", "dosage": "2 tablets", "frequency": "Every 6 hours", "category": "Combination", "warning": "Contains caffeine"},
        ],
        "migraine_acute": [
            {"name": "Sumatriptan (Imitrex)", "dosage": "50-100mg", "frequency": "May repeat in 2 hours", "max_daily": "200mg", "category": "Triptan", "warning": "Not for cardiac patients"},
            {"name": "Rizatriptan (Maxalt)", "dosage": "5-10mg", "frequency": "May repeat in 2 hours", "category": "Triptan", "warning": "Fast acting"},
            {"name": "Zolmitriptan (Zomig)", "dosage": "2.5-5mg", "frequency": "May repeat in 2 hours", "category": "Triptan", "warning": "Nasal spray available"},
            {"name": "Eletriptan (Relpax)", "dosage": "40mg", "frequency": "May repeat in 2 hours", "category": "Triptan", "warning": "High efficacy"},
        ],
        "migraine_prevention": [
            {"name": "Propranolol", "dosage": "40-160mg", "frequency": "Daily in divided doses", "category": "Beta Blocker", "warning": "Don't stop suddenly"},
            {"name": "Topiramate (Topamax)", "dosage": "50-100mg", "frequency": "Daily", "category": "Anticonvulsant", "warning": "Weight loss, cognitive effects"},
            {"name": "Amitriptyline", "dosage": "10-50mg", "frequency": "At bedtime", "category": "TCA", "warning": "Start low, sedating"},
            {"name": "Valproate", "dosage": "500-1000mg", "frequency": "Daily", "category": "Anticonvulsant", "warning": "Not in pregnancy"},
            {"name": "Magnesium", "dosage": "400-600mg", "frequency": "Daily", "category": "Supplement", "warning": "May cause diarrhea"},
            {"name": "Riboflavin (B2)", "dosage": "400mg", "frequency": "Daily", "category": "Vitamin", "warning": "Yellow urine is normal"},
            {"name": "CoQ10", "dosage": "100-300mg", "frequency": "Daily", "category": "Supplement", "warning": "May take months"},
        ]
    },

    # ==========================================
    # MUSCULOSKELETAL
    # ==========================================
    "muscle_joint": {
        "muscle_relaxants": [
            {"name": "Cyclobenzaprine (Flexeril)", "dosage": "5-10mg", "frequency": "3 times daily", "category": "Muscle Relaxant", "warning": "Sedating, short-term use"},
            {"name": "Methocarbamol (Robaxin)", "dosage": "750-1500mg", "frequency": "3-4 times daily", "category": "Muscle Relaxant", "warning": "Less sedating"},
            {"name": "Tizanidine (Zanaflex)", "dosage": "2-4mg", "frequency": "Every 6-8 hours", "category": "Muscle Relaxant", "warning": "Low BP, sedating"},
            {"name": "Baclofen", "dosage": "5-20mg", "frequency": "3 times daily", "category": "Muscle Relaxant", "warning": "Don't stop suddenly"},
            {"name": "Carisoprodol (Soma)", "dosage": "350mg", "frequency": "3 times daily", "category": "Muscle Relaxant", "warning": "Abuse potential"},
        ],
        "gout": [
            {"name": "Colchicine", "dosage": "0.6mg", "frequency": "1-2 times daily for acute", "category": "Anti-gout", "warning": "GI side effects, low dose"},
            {"name": "Indomethacin", "dosage": "50mg", "frequency": "3 times daily", "category": "NSAID", "warning": "Very effective for gout"},
            {"name": "Allopurinol", "dosage": "100-300mg", "frequency": "Once daily", "category": "Xanthine Oxidase Inhibitor", "warning": "For prevention, not acute"},
            {"name": "Febuxostat (Uloric)", "dosage": "40-80mg", "frequency": "Once daily", "category": "Xanthine Oxidase Inhibitor", "warning": "Alternative to allopurinol"},
        ],
        "osteoporosis": [
            {"name": "Alendronate (Fosamax)", "dosage": "70mg", "frequency": "Once weekly", "category": "Bisphosphonate", "warning": "Take upright, 30 min before food"},
            {"name": "Risedronate (Actonel)", "dosage": "35mg", "frequency": "Once weekly", "category": "Bisphosphonate", "warning": "Similar to alendronate"},
            {"name": "Calcium + Vitamin D", "dosage": "1000mg Ca + 800IU D", "frequency": "Daily", "category": "Supplement", "warning": "Essential for bone health"},
        ],
        "arthritis": [
            {"name": "Methotrexate", "dosage": "7.5-25mg", "frequency": "Once weekly", "category": "DMARD", "warning": "Folic acid needed, liver monitoring"},
            {"name": "Hydroxychloroquine (Plaquenil)", "dosage": "200-400mg", "frequency": "Daily", "category": "DMARD", "warning": "Eye exams needed"},
            {"name": "Sulfasalazine", "dosage": "500-1000mg", "frequency": "Twice daily", "category": "DMARD", "warning": "GI side effects"},
            {"name": "Glucosamine + Chondroitin", "dosage": "1500mg + 1200mg", "frequency": "Daily", "category": "Supplement", "warning": "May take months to work"},
        ]
    },

    # ==========================================
    # EYE
    # ==========================================
    "eye": {
        "dry_eye": [
            {"name": "Artificial Tears (Systane)", "dosage": "1-2 drops", "frequency": "As needed", "category": "Lubricant", "warning": "Multiple times daily OK"},
            {"name": "Refresh Tears", "dosage": "1-2 drops", "frequency": "As needed", "category": "Lubricant", "warning": "Preservative-free available"},
            {"name": "Cyclosporine Eye Drops (Restasis)", "dosage": "1 drop each eye", "frequency": "Twice daily", "category": "Immunomodulator", "warning": "Prescription, takes weeks"},
        ],
        "allergy": [
            {"name": "Ketotifen Eye Drops (Zaditor)", "dosage": "1 drop each eye", "frequency": "Twice daily", "category": "Antihistamine", "warning": "OTC"},
            {"name": "Olopatadine (Patanol)", "dosage": "1 drop each eye", "frequency": "Twice daily", "category": "Antihistamine", "warning": "Prescription"},
        ],
        "infection": [
            {"name": "Tobramycin Eye Drops", "dosage": "1-2 drops", "frequency": "Every 4 hours", "category": "Antibiotic", "warning": "For bacterial conjunctivitis"},
            {"name": "Ciprofloxacin Eye Drops", "dosage": "1-2 drops", "frequency": "Every 2-4 hours", "category": "Antibiotic", "warning": "Broad spectrum"},
            {"name": "Erythromycin Eye Ointment", "dosage": "0.5 inch ribbon", "frequency": "2-4 times daily", "category": "Antibiotic", "warning": "Blurs vision temporarily"},
        ],
        "glaucoma": [
            {"name": "Latanoprost (Xalatan)", "dosage": "1 drop each eye", "frequency": "Once daily at night", "category": "Prostaglandin Analog", "warning": "May darken iris"},
            {"name": "Timolol Eye Drops", "dosage": "1 drop each eye", "frequency": "Twice daily", "category": "Beta Blocker", "warning": "Caution in asthma"},
            {"name": "Brimonidine (Alphagan)", "dosage": "1 drop each eye", "frequency": "3 times daily", "category": "Alpha Agonist", "warning": "May cause drowsiness"},
        ]
    },

    # ==========================================
    # HORMONAL
    # ==========================================
    "hormonal": {
        "thyroid": [
            {"name": "Levothyroxine (Synthroid)", "dosage": "25-200mcg", "frequency": "Once daily, empty stomach", "category": "Thyroid Hormone", "warning": "Take 30-60 min before food"},
            {"name": "Liothyronine (Cytomel)", "dosage": "5-25mcg", "frequency": "Once daily", "category": "Thyroid Hormone", "warning": "T3, short-acting"},
            {"name": "Methimazole", "dosage": "5-30mg", "frequency": "Daily", "category": "Antithyroid", "warning": "For hyperthyroidism"},
            {"name": "Propylthiouracil (PTU)", "dosage": "100-150mg", "frequency": "3 times daily", "category": "Antithyroid", "warning": "Liver monitoring needed"},
        ],
        "corticosteroids_systemic": [
            {"name": "Prednisone", "dosage": "5-60mg", "frequency": "Once daily in morning", "category": "Corticosteroid", "warning": "Don't stop suddenly, many side effects"},
            {"name": "Methylprednisolone (Medrol)", "dosage": "4-48mg", "frequency": "Daily", "category": "Corticosteroid", "warning": "Dose pack available"},
            {"name": "Dexamethasone", "dosage": "0.5-10mg", "frequency": "Daily", "category": "Corticosteroid", "warning": "Very potent"},
            {"name": "Hydrocortisone", "dosage": "20-240mg", "frequency": "Daily in divided doses", "category": "Corticosteroid", "warning": "Shorter acting"},
        ],
        "contraceptives": [
            {"name": "Combined Oral Contraceptive", "dosage": "1 tablet", "frequency": "Daily at same time", "category": "Contraceptive", "warning": "Many brands, see doctor"},
            {"name": "Progestin-only Pill", "dosage": "1 tablet", "frequency": "Daily at same time", "category": "Contraceptive", "warning": "Must take same time daily"},
            {"name": "Emergency Contraception (Plan B)", "dosage": "1.5mg levonorgestrel", "frequency": "Single dose ASAP", "category": "Emergency Contraceptive", "warning": "Within 72 hours"},
        ]
    },

    # ==========================================
    # URINARY
    # ==========================================
    "urinary": {
        "uti": [
            {"name": "Nitrofurantoin (Macrobid)", "dosage": "100mg", "frequency": "Twice daily for 5-7 days", "category": "Antibiotic", "warning": "Take with food"},
            {"name": "Trimethoprim-Sulfamethoxazole", "dosage": "1 DS tablet", "frequency": "Twice daily for 3 days", "category": "Antibiotic", "warning": "Allergies common"},
            {"name": "Fosfomycin (Monurol)", "dosage": "3g packet", "frequency": "Single dose", "category": "Antibiotic", "warning": "One-time dose"},
            {"name": "Phenazopyridine (Pyridium)", "dosage": "200mg", "frequency": "3 times daily", "category": "Urinary Analgesic", "warning": "Orange urine, max 2 days"},
        ],
        "bph": [
            {"name": "Tamsulosin (Flomax)", "dosage": "0.4mg", "frequency": "Once daily", "category": "Alpha Blocker", "warning": "Dizziness, take at bedtime"},
            {"name": "Finasteride (Proscar)", "dosage": "5mg", "frequency": "Once daily", "category": "5-alpha Reductase Inhibitor", "warning": "Takes months, sexual side effects"},
            {"name": "Dutasteride (Avodart)", "dosage": "0.5mg", "frequency": "Once daily", "category": "5-alpha Reductase Inhibitor", "warning": "Similar to finasteride"},
        ],
        "overactive_bladder": [
            {"name": "Oxybutynin", "dosage": "5mg", "frequency": "2-3 times daily", "category": "Anticholinergic", "warning": "Dry mouth, constipation"},
            {"name": "Tolterodine (Detrol)", "dosage": "2mg", "frequency": "Twice daily", "category": "Anticholinergic", "warning": "LA version once daily"},
            {"name": "Solifenacin (Vesicare)", "dosage": "5-10mg", "frequency": "Once daily", "category": "Anticholinergic", "warning": "Constipation"},
            {"name": "Mirabegron (Myrbetriq)", "dosage": "25-50mg", "frequency": "Once daily", "category": "Beta-3 Agonist", "warning": "Different mechanism, fewer side effects"},
        ]
    },
}
