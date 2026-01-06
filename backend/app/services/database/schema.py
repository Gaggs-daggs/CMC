"""
PostgreSQL Database Schema
Creates tables for user profiles, medical data, and autocomplete suggestions
"""

SCHEMA_SQL = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USER PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    age INTEGER,
    gender VARCHAR(20),
    blood_type VARCHAR(10),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    preferred_language VARCHAR(10) DEFAULT 'en',
    location VARCHAR(255),
    smoking BOOLEAN,
    alcohol VARCHAR(20),
    exercise_frequency VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_consultation TIMESTAMP,
    total_consultations INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_profiles_phone ON user_profiles(phone_number);

-- ============================================
-- USER ALLERGIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_allergies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    allergen VARCHAR(255) NOT NULL,
    severity VARCHAR(20) DEFAULT 'moderate',
    reaction VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_allergies_user ON user_allergies(user_id);

-- ============================================
-- USER MEDICAL CONDITIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    condition_name VARCHAR(255) NOT NULL,
    diagnosed_date DATE,
    severity VARCHAR(20),
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conditions_user ON user_conditions(user_id);

-- ============================================
-- USER CURRENT MEDICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    prescribed_for VARCHAR(255),
    start_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_medications_user ON user_medications(user_id);

-- ============================================
-- CONSULTATION HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    symptoms TEXT[],
    urgency_level VARCHAR(50),
    conditions_suggested TEXT[],
    medications_suggested TEXT[],
    ai_response_summary TEXT,
    follow_up_needed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_consultations_user ON consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_consultations_date ON consultations(created_at);

-- ============================================
-- EMERGENCY CONTACTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_emergency_user ON emergency_contacts(user_id);

-- ============================================
-- FAMILY HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS family_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    condition VARCHAR(255) NOT NULL,
    relation VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MASTER DATA: ALLERGENS (for autocomplete)
-- ============================================
CREATE TABLE IF NOT EXISTS master_allergens (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    common_reactions TEXT,
    severity_typical VARCHAR(20)
);

-- ============================================
-- MASTER DATA: MEDICAL CONDITIONS (for autocomplete)
-- ============================================
CREATE TABLE IF NOT EXISTS master_conditions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    icd10_code VARCHAR(20),
    description TEXT
);

-- ============================================
-- MASTER DATA: MEDICATIONS (for autocomplete)
-- ============================================
CREATE TABLE IF NOT EXISTS master_medications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    generic_name VARCHAR(255),
    drug_class VARCHAR(100),
    common_dosages TEXT
);

-- Create text search indexes for autocomplete
CREATE INDEX IF NOT EXISTS idx_allergens_search ON master_allergens USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_conditions_search ON master_conditions USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_medications_search ON master_medications USING gin(to_tsvector('english', name));

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

# Comprehensive allergen data
ALLERGENS_DATA = """
INSERT INTO master_allergens (name, category, common_reactions, severity_typical) VALUES
-- Drug Allergies (Antibiotics)
('Penicillin', 'Drug - Antibiotic', 'Rash, hives, anaphylaxis', 'severe'),
('Amoxicillin', 'Drug - Antibiotic', 'Rash, hives, swelling', 'moderate'),
('Ampicillin', 'Drug - Antibiotic', 'Rash, itching', 'moderate'),
('Cephalosporins', 'Drug - Antibiotic', 'Rash, breathing difficulty', 'severe'),
('Cefixime', 'Drug - Antibiotic', 'Rash, diarrhea', 'moderate'),
('Ceftriaxone', 'Drug - Antibiotic', 'Rash, anaphylaxis', 'severe'),
('Sulfonamides', 'Drug - Antibiotic', 'Rash, Stevens-Johnson syndrome', 'severe'),
('Sulfamethoxazole', 'Drug - Antibiotic', 'Rash, fever', 'moderate'),
('Trimethoprim', 'Drug - Antibiotic', 'Rash, nausea', 'mild'),
('Erythromycin', 'Drug - Antibiotic', 'Nausea, rash', 'mild'),
('Azithromycin', 'Drug - Antibiotic', 'Rash, diarrhea', 'mild'),
('Clarithromycin', 'Drug - Antibiotic', 'Nausea, taste changes', 'mild'),
('Ciprofloxacin', 'Drug - Antibiotic', 'Rash, tendon problems', 'moderate'),
('Levofloxacin', 'Drug - Antibiotic', 'Rash, dizziness', 'moderate'),
('Metronidazole', 'Drug - Antibiotic', 'Nausea, metallic taste', 'mild'),
('Tetracycline', 'Drug - Antibiotic', 'Photosensitivity, nausea', 'moderate'),
('Doxycycline', 'Drug - Antibiotic', 'Photosensitivity, esophagitis', 'moderate'),
('Vancomycin', 'Drug - Antibiotic', 'Red man syndrome, rash', 'moderate'),
('Gentamicin', 'Drug - Antibiotic', 'Kidney damage, hearing loss', 'severe'),
('Clindamycin', 'Drug - Antibiotic', 'Diarrhea, rash', 'moderate'),

-- Pain Medications
('Aspirin', 'Drug - NSAID', 'Stomach bleeding, asthma', 'moderate'),
('Ibuprofen', 'Drug - NSAID', 'Stomach upset, rash', 'moderate'),
('Naproxen', 'Drug - NSAID', 'Stomach bleeding, rash', 'moderate'),
('Diclofenac', 'Drug - NSAID', 'Stomach upset, rash', 'moderate'),
('Indomethacin', 'Drug - NSAID', 'Headache, GI bleeding', 'moderate'),
('Celecoxib', 'Drug - NSAID', 'Rash, cardiovascular', 'moderate'),
('Acetaminophen', 'Drug - Analgesic', 'Rash, liver damage (overdose)', 'mild'),
('Paracetamol', 'Drug - Analgesic', 'Rash, liver damage (overdose)', 'mild'),
('Tramadol', 'Drug - Opioid', 'Nausea, seizures', 'moderate'),
('Codeine', 'Drug - Opioid', 'Respiratory depression, constipation', 'severe'),
('Morphine', 'Drug - Opioid', 'Respiratory depression, nausea', 'severe'),
('Oxycodone', 'Drug - Opioid', 'Respiratory depression, constipation', 'severe'),

-- Anesthetics
('Lidocaine', 'Drug - Anesthetic', 'Numbness, dizziness', 'mild'),
('Novocaine', 'Drug - Anesthetic', 'Allergic reaction, numbness', 'moderate'),
('Benzocaine', 'Drug - Anesthetic', 'Methemoglobinemia', 'moderate'),
('Propofol', 'Drug - Anesthetic', 'Hypotension, apnea', 'severe'),

-- Cardiovascular Drugs
('ACE Inhibitors', 'Drug - Cardiovascular', 'Cough, angioedema', 'moderate'),
('Lisinopril', 'Drug - Cardiovascular', 'Cough, angioedema', 'moderate'),
('Enalapril', 'Drug - Cardiovascular', 'Cough, dizziness', 'moderate'),
('Beta Blockers', 'Drug - Cardiovascular', 'Bradycardia, fatigue', 'moderate'),
('Metoprolol', 'Drug - Cardiovascular', 'Fatigue, bradycardia', 'moderate'),
('Atenolol', 'Drug - Cardiovascular', 'Fatigue, cold extremities', 'moderate'),
('Statins', 'Drug - Cardiovascular', 'Muscle pain, liver issues', 'moderate'),
('Atorvastatin', 'Drug - Cardiovascular', 'Muscle pain, rash', 'moderate'),
('Simvastatin', 'Drug - Cardiovascular', 'Muscle pain, nausea', 'moderate'),

-- Other Drugs
('Insulin', 'Drug - Hormone', 'Hypoglycemia, injection site reaction', 'moderate'),
('Metformin', 'Drug - Diabetes', 'GI upset, lactic acidosis', 'moderate'),
('Contrast Dye', 'Drug - Diagnostic', 'Anaphylaxis, kidney damage', 'severe'),
('Iodine', 'Drug - Antiseptic', 'Rash, anaphylaxis', 'moderate'),
('Latex', 'Material', 'Rash, anaphylaxis', 'severe'),
('Heparin', 'Drug - Anticoagulant', 'Bleeding, HIT', 'severe'),
('Warfarin', 'Drug - Anticoagulant', 'Bleeding', 'severe'),

-- Food Allergies
('Peanuts', 'Food - Legume', 'Anaphylaxis, hives, swelling', 'severe'),
('Tree Nuts', 'Food - Nut', 'Anaphylaxis, hives', 'severe'),
('Almonds', 'Food - Nut', 'Hives, swelling', 'severe'),
('Cashews', 'Food - Nut', 'Anaphylaxis, hives', 'severe'),
('Walnuts', 'Food - Nut', 'Anaphylaxis, swelling', 'severe'),
('Pistachios', 'Food - Nut', 'Hives, GI symptoms', 'severe'),
('Hazelnuts', 'Food - Nut', 'Oral allergy, hives', 'moderate'),
('Milk', 'Food - Dairy', 'Hives, GI symptoms, anaphylaxis', 'moderate'),
('Dairy', 'Food - Dairy', 'GI symptoms, skin reactions', 'moderate'),
('Lactose', 'Food - Dairy', 'GI symptoms, bloating', 'mild'),
('Eggs', 'Food - Protein', 'Hives, GI symptoms', 'moderate'),
('Wheat', 'Food - Grain', 'Hives, GI symptoms, anaphylaxis', 'moderate'),
('Gluten', 'Food - Protein', 'GI symptoms, fatigue', 'moderate'),
('Soy', 'Food - Legume', 'Hives, GI symptoms', 'moderate'),
('Fish', 'Food - Seafood', 'Anaphylaxis, hives', 'severe'),
('Shellfish', 'Food - Seafood', 'Anaphylaxis, hives', 'severe'),
('Shrimp', 'Food - Seafood', 'Anaphylaxis, hives', 'severe'),
('Crab', 'Food - Seafood', 'Anaphylaxis, hives', 'severe'),
('Lobster', 'Food - Seafood', 'Anaphylaxis, hives', 'severe'),
('Sesame', 'Food - Seed', 'Anaphylaxis, hives', 'severe'),
('Mustard', 'Food - Condiment', 'Hives, anaphylaxis', 'moderate'),
('Celery', 'Food - Vegetable', 'Anaphylaxis, oral symptoms', 'moderate'),
('Corn', 'Food - Grain', 'Hives, GI symptoms', 'mild'),
('Banana', 'Food - Fruit', 'Oral allergy, latex cross-reaction', 'mild'),
('Avocado', 'Food - Fruit', 'Oral allergy, latex cross-reaction', 'mild'),
('Kiwi', 'Food - Fruit', 'Oral allergy, anaphylaxis', 'moderate'),
('Mango', 'Food - Fruit', 'Contact dermatitis', 'mild'),
('Strawberry', 'Food - Fruit', 'Hives, oral symptoms', 'mild'),
('Tomato', 'Food - Vegetable', 'Oral allergy, GI symptoms', 'mild'),
('Citrus', 'Food - Fruit', 'Oral symptoms, heartburn', 'mild'),
('Chocolate', 'Food - Confection', 'Headache, hives', 'mild'),
('Caffeine', 'Food - Stimulant', 'Palpitations, anxiety', 'mild'),
('Alcohol', 'Food - Beverage', 'Flushing, headache', 'mild'),
('MSG', 'Food - Additive', 'Headache, flushing', 'mild'),
('Sulfites', 'Food - Preservative', 'Asthma, hives', 'moderate'),
('Food Coloring', 'Food - Additive', 'Hyperactivity, hives', 'mild'),
('Aspartame', 'Food - Sweetener', 'Headache, dizziness', 'mild'),

-- Environmental Allergies
('Dust Mites', 'Environmental', 'Sneezing, runny nose, asthma', 'moderate'),
('Pollen', 'Environmental', 'Sneezing, itchy eyes, congestion', 'moderate'),
('Grass Pollen', 'Environmental', 'Hay fever, sneezing', 'moderate'),
('Tree Pollen', 'Environmental', 'Hay fever, itchy eyes', 'moderate'),
('Ragweed', 'Environmental', 'Sneezing, congestion', 'moderate'),
('Mold', 'Environmental', 'Sneezing, asthma, skin rash', 'moderate'),
('Pet Dander', 'Environmental', 'Sneezing, itchy eyes, asthma', 'moderate'),
('Cat Dander', 'Environmental', 'Sneezing, hives, asthma', 'moderate'),
('Dog Dander', 'Environmental', 'Sneezing, congestion', 'moderate'),
('Cockroach', 'Environmental', 'Asthma, sneezing', 'moderate'),
('Feathers', 'Environmental', 'Sneezing, skin irritation', 'mild'),

-- Insect Allergies
('Bee Venom', 'Insect', 'Anaphylaxis, swelling', 'severe'),
('Wasp Venom', 'Insect', 'Anaphylaxis, swelling', 'severe'),
('Hornet Venom', 'Insect', 'Anaphylaxis, swelling', 'severe'),
('Fire Ant', 'Insect', 'Pustules, anaphylaxis', 'severe'),
('Mosquito', 'Insect', 'Swelling, itching', 'mild'),

-- Contact Allergies
('Nickel', 'Contact', 'Contact dermatitis, rash', 'mild'),
('Cobalt', 'Contact', 'Contact dermatitis', 'mild'),
('Chromium', 'Contact', 'Contact dermatitis', 'mild'),
('Fragrance', 'Contact', 'Contact dermatitis, headache', 'mild'),
('Formaldehyde', 'Contact', 'Contact dermatitis, respiratory', 'moderate'),
('Lanolin', 'Contact', 'Contact dermatitis', 'mild'),
('Neomycin', 'Contact - Antibiotic', 'Contact dermatitis', 'mild'),
('Bacitracin', 'Contact - Antibiotic', 'Contact dermatitis', 'mild'),
('Hair Dye', 'Contact', 'Contact dermatitis, swelling', 'moderate'),
('Poison Ivy', 'Plant', 'Contact dermatitis', 'moderate'),
('Poison Oak', 'Plant', 'Contact dermatitis', 'moderate'),
('Sunscreen', 'Contact', 'Contact dermatitis, photosensitivity', 'mild')
ON CONFLICT (name) DO NOTHING;
"""

# Comprehensive medical conditions data
CONDITIONS_DATA = """
INSERT INTO master_conditions (name, category, icd10_code, description) VALUES
-- Cardiovascular Conditions
('Hypertension', 'Cardiovascular', 'I10', 'High blood pressure'),
('High Blood Pressure', 'Cardiovascular', 'I10', 'Elevated arterial blood pressure'),
('Hypotension', 'Cardiovascular', 'I95', 'Low blood pressure'),
('Coronary Artery Disease', 'Cardiovascular', 'I25.1', 'Narrowing of coronary arteries'),
('Heart Disease', 'Cardiovascular', 'I51.9', 'General heart condition'),
('Congestive Heart Failure', 'Cardiovascular', 'I50.9', 'Heart cannot pump effectively'),
('Heart Failure', 'Cardiovascular', 'I50.9', 'Reduced heart pumping ability'),
('Arrhythmia', 'Cardiovascular', 'I49.9', 'Irregular heartbeat'),
('Atrial Fibrillation', 'Cardiovascular', 'I48.91', 'Irregular rapid heart rhythm'),
('Bradycardia', 'Cardiovascular', 'R00.1', 'Slow heart rate'),
('Tachycardia', 'Cardiovascular', 'R00.0', 'Fast heart rate'),
('Angina', 'Cardiovascular', 'I20.9', 'Chest pain from reduced blood flow'),
('Myocardial Infarction', 'Cardiovascular', 'I21.9', 'Heart attack'),
('Heart Attack', 'Cardiovascular', 'I21.9', 'Blocked blood flow to heart'),
('Stroke', 'Cardiovascular', 'I63.9', 'Brain blood flow interruption'),
('Peripheral Artery Disease', 'Cardiovascular', 'I73.9', 'Narrowed arteries in limbs'),
('Deep Vein Thrombosis', 'Cardiovascular', 'I82.9', 'Blood clot in deep vein'),
('Pulmonary Embolism', 'Cardiovascular', 'I26.9', 'Blood clot in lung'),
('Varicose Veins', 'Cardiovascular', 'I83.9', 'Enlarged twisted veins'),
('Aortic Aneurysm', 'Cardiovascular', 'I71.9', 'Bulge in aorta wall'),
('Cardiomyopathy', 'Cardiovascular', 'I42.9', 'Heart muscle disease'),
('Heart Murmur', 'Cardiovascular', 'R01.1', 'Abnormal heart sound'),
('Mitral Valve Prolapse', 'Cardiovascular', 'I34.1', 'Heart valve disorder'),
('Pericarditis', 'Cardiovascular', 'I30.9', 'Inflammation of heart lining'),
('Endocarditis', 'Cardiovascular', 'I33.9', 'Heart inner lining infection'),

-- Metabolic/Endocrine Conditions
('Diabetes Type 1', 'Endocrine', 'E10', 'Autoimmune diabetes'),
('Diabetes Type 2', 'Endocrine', 'E11', 'Insulin resistance diabetes'),
('Diabetes Mellitus', 'Endocrine', 'E11.9', 'High blood sugar condition'),
('Diabetes', 'Endocrine', 'E11.9', 'Blood sugar disorder'),
('Prediabetes', 'Endocrine', 'R73.03', 'Elevated blood sugar'),
('Gestational Diabetes', 'Endocrine', 'O24.4', 'Diabetes during pregnancy'),
('Hypoglycemia', 'Endocrine', 'E16.2', 'Low blood sugar'),
('Hypothyroidism', 'Endocrine', 'E03.9', 'Underactive thyroid'),
('Hyperthyroidism', 'Endocrine', 'E05.9', 'Overactive thyroid'),
('Thyroid Disease', 'Endocrine', 'E07.9', 'Thyroid gland disorder'),
('Goiter', 'Endocrine', 'E04.9', 'Enlarged thyroid'),
('Thyroid Nodules', 'Endocrine', 'E04.1', 'Lumps in thyroid'),
('Hashimotos Disease', 'Endocrine', 'E06.3', 'Autoimmune thyroiditis'),
('Graves Disease', 'Endocrine', 'E05.0', 'Autoimmune hyperthyroidism'),
('Obesity', 'Metabolic', 'E66.9', 'Excessive body weight'),
('Metabolic Syndrome', 'Metabolic', 'E88.81', 'Cluster of conditions'),
('High Cholesterol', 'Metabolic', 'E78.0', 'Elevated cholesterol levels'),
('Hyperlipidemia', 'Metabolic', 'E78.5', 'High blood lipids'),
('Gout', 'Metabolic', 'M10.9', 'Uric acid buildup'),
('Addisons Disease', 'Endocrine', 'E27.1', 'Adrenal insufficiency'),
('Cushings Syndrome', 'Endocrine', 'E24.9', 'Excess cortisol'),
('PCOS', 'Endocrine', 'E28.2', 'Polycystic ovary syndrome'),
('Polycystic Ovary Syndrome', 'Endocrine', 'E28.2', 'Hormonal disorder'),

-- Respiratory Conditions
('Asthma', 'Respiratory', 'J45.9', 'Chronic airway inflammation'),
('COPD', 'Respiratory', 'J44.9', 'Chronic obstructive pulmonary disease'),
('Chronic Bronchitis', 'Respiratory', 'J42', 'Long-term bronchial inflammation'),
('Emphysema', 'Respiratory', 'J43.9', 'Damaged air sacs'),
('Pulmonary Fibrosis', 'Respiratory', 'J84.1', 'Lung scarring'),
('Sleep Apnea', 'Respiratory', 'G47.3', 'Breathing stops during sleep'),
('Obstructive Sleep Apnea', 'Respiratory', 'G47.33', 'Blocked airway during sleep'),
('Pneumonia', 'Respiratory', 'J18.9', 'Lung infection'),
('Tuberculosis', 'Respiratory', 'A15.9', 'Bacterial lung infection'),
('Bronchiectasis', 'Respiratory', 'J47.9', 'Damaged bronchial tubes'),
('Cystic Fibrosis', 'Respiratory', 'E84.9', 'Genetic mucus disorder'),
('Pulmonary Hypertension', 'Respiratory', 'I27.0', 'High blood pressure in lungs'),
('Pleurisy', 'Respiratory', 'R09.1', 'Lung lining inflammation'),
('Sarcoidosis', 'Respiratory', 'D86.9', 'Inflammatory disease'),
('Allergic Rhinitis', 'Respiratory', 'J30.9', 'Nasal allergies'),
('Sinusitis', 'Respiratory', 'J32.9', 'Sinus inflammation'),
('Chronic Sinusitis', 'Respiratory', 'J32.9', 'Long-term sinus problems'),

-- Gastrointestinal Conditions
('GERD', 'Gastrointestinal', 'K21.0', 'Acid reflux disease'),
('Acid Reflux', 'Gastrointestinal', 'K21.0', 'Stomach acid backflow'),
('Gastritis', 'Gastrointestinal', 'K29.7', 'Stomach lining inflammation'),
('Peptic Ulcer', 'Gastrointestinal', 'K27.9', 'Stomach or intestinal sore'),
('Stomach Ulcer', 'Gastrointestinal', 'K25.9', 'Gastric ulcer'),
('Irritable Bowel Syndrome', 'Gastrointestinal', 'K58.9', 'Functional bowel disorder'),
('IBS', 'Gastrointestinal', 'K58.9', 'Irritable bowel syndrome'),
('Crohns Disease', 'Gastrointestinal', 'K50.9', 'Inflammatory bowel disease'),
('Ulcerative Colitis', 'Gastrointestinal', 'K51.9', 'Colon inflammation'),
('Inflammatory Bowel Disease', 'Gastrointestinal', 'K52.9', 'Chronic intestinal inflammation'),
('Celiac Disease', 'Gastrointestinal', 'K90.0', 'Gluten intolerance'),
('Diverticulitis', 'Gastrointestinal', 'K57.9', 'Inflamed intestinal pouches'),
('Gallstones', 'Gastrointestinal', 'K80.2', 'Gallbladder stones'),
('Pancreatitis', 'Gastrointestinal', 'K85.9', 'Pancreas inflammation'),
('Chronic Pancreatitis', 'Gastrointestinal', 'K86.1', 'Long-term pancreas inflammation'),
('Fatty Liver Disease', 'Gastrointestinal', 'K76.0', 'Fat in liver'),
('NAFLD', 'Gastrointestinal', 'K76.0', 'Non-alcoholic fatty liver'),
('Cirrhosis', 'Gastrointestinal', 'K74.6', 'Liver scarring'),
('Hepatitis B', 'Gastrointestinal', 'B18.1', 'Liver infection'),
('Hepatitis C', 'Gastrointestinal', 'B18.2', 'Chronic liver infection'),
('Constipation', 'Gastrointestinal', 'K59.0', 'Infrequent bowel movements'),
('Chronic Constipation', 'Gastrointestinal', 'K59.0', 'Long-term constipation'),
('Hemorrhoids', 'Gastrointestinal', 'K64.9', 'Swollen rectal veins'),
('Hiatal Hernia', 'Gastrointestinal', 'K44.9', 'Stomach through diaphragm'),
('Lactose Intolerance', 'Gastrointestinal', 'E73.9', 'Cannot digest lactose'),

-- Neurological Conditions
('Epilepsy', 'Neurological', 'G40.9', 'Seizure disorder'),
('Seizure Disorder', 'Neurological', 'G40.9', 'Recurrent seizures'),
('Migraine', 'Neurological', 'G43.9', 'Severe recurring headache'),
('Chronic Migraine', 'Neurological', 'G43.7', 'Frequent migraines'),
('Tension Headache', 'Neurological', 'G44.2', 'Stress-related headache'),
('Cluster Headache', 'Neurological', 'G44.0', 'Severe one-sided headache'),
('Parkinsons Disease', 'Neurological', 'G20', 'Movement disorder'),
('Alzheimers Disease', 'Neurological', 'G30.9', 'Progressive dementia'),
('Dementia', 'Neurological', 'F03.9', 'Cognitive decline'),
('Multiple Sclerosis', 'Neurological', 'G35', 'Autoimmune nerve disease'),
('MS', 'Neurological', 'G35', 'Multiple sclerosis'),
('ALS', 'Neurological', 'G12.21', 'Motor neuron disease'),
('Amyotrophic Lateral Sclerosis', 'Neurological', 'G12.21', 'Lou Gehrigs disease'),
('Neuropathy', 'Neurological', 'G62.9', 'Nerve damage'),
('Peripheral Neuropathy', 'Neurological', 'G62.9', 'Peripheral nerve damage'),
('Diabetic Neuropathy', 'Neurological', 'E11.4', 'Diabetes nerve damage'),
('Carpal Tunnel Syndrome', 'Neurological', 'G56.0', 'Wrist nerve compression'),
('Sciatica', 'Neurological', 'M54.3', 'Sciatic nerve pain'),
('Trigeminal Neuralgia', 'Neurological', 'G50.0', 'Facial nerve pain'),
('Bells Palsy', 'Neurological', 'G51.0', 'Facial paralysis'),
('Restless Leg Syndrome', 'Neurological', 'G25.81', 'Urge to move legs'),
('Essential Tremor', 'Neurological', 'G25.0', 'Involuntary shaking'),
('Vertigo', 'Neurological', 'R42', 'Spinning sensation'),
('Menieres Disease', 'Neurological', 'H81.0', 'Inner ear disorder'),
('Tinnitus', 'Neurological', 'H93.1', 'Ringing in ears'),

-- Mental Health Conditions
('Depression', 'Mental Health', 'F32.9', 'Depressive disorder'),
('Major Depression', 'Mental Health', 'F33.9', 'Recurrent depression'),
('Anxiety', 'Mental Health', 'F41.9', 'Anxiety disorder'),
('Generalized Anxiety Disorder', 'Mental Health', 'F41.1', 'Chronic anxiety'),
('Panic Disorder', 'Mental Health', 'F41.0', 'Recurrent panic attacks'),
('Social Anxiety', 'Mental Health', 'F40.1', 'Social phobia'),
('PTSD', 'Mental Health', 'F43.1', 'Post-traumatic stress disorder'),
('Post Traumatic Stress Disorder', 'Mental Health', 'F43.1', 'Trauma-related disorder'),
('OCD', 'Mental Health', 'F42.9', 'Obsessive-compulsive disorder'),
('Obsessive Compulsive Disorder', 'Mental Health', 'F42.9', 'Obsessions and compulsions'),
('Bipolar Disorder', 'Mental Health', 'F31.9', 'Mood swings disorder'),
('Schizophrenia', 'Mental Health', 'F20.9', 'Psychotic disorder'),
('ADHD', 'Mental Health', 'F90.9', 'Attention deficit hyperactivity'),
('Attention Deficit Disorder', 'Mental Health', 'F90.0', 'Attention disorder'),
('Eating Disorder', 'Mental Health', 'F50.9', 'Abnormal eating habits'),
('Anorexia Nervosa', 'Mental Health', 'F50.0', 'Restrictive eating'),
('Bulimia Nervosa', 'Mental Health', 'F50.2', 'Binge-purge disorder'),
('Insomnia', 'Mental Health', 'G47.0', 'Sleep difficulty'),
('Chronic Insomnia', 'Mental Health', 'F51.0', 'Long-term sleep problems'),
('Autism Spectrum Disorder', 'Mental Health', 'F84.0', 'Developmental disorder'),

-- Musculoskeletal Conditions
('Arthritis', 'Musculoskeletal', 'M19.9', 'Joint inflammation'),
('Osteoarthritis', 'Musculoskeletal', 'M15.9', 'Degenerative joint disease'),
('Rheumatoid Arthritis', 'Musculoskeletal', 'M06.9', 'Autoimmune joint disease'),
('Psoriatic Arthritis', 'Musculoskeletal', 'M07.3', 'Psoriasis-related arthritis'),
('Gout', 'Musculoskeletal', 'M10.9', 'Uric acid joint disease'),
('Osteoporosis', 'Musculoskeletal', 'M81.0', 'Bone density loss'),
('Osteopenia', 'Musculoskeletal', 'M85.8', 'Low bone density'),
('Fibromyalgia', 'Musculoskeletal', 'M79.7', 'Widespread pain'),
('Chronic Back Pain', 'Musculoskeletal', 'M54.5', 'Persistent back pain'),
('Lower Back Pain', 'Musculoskeletal', 'M54.5', 'Lumbar pain'),
('Herniated Disc', 'Musculoskeletal', 'M51.2', 'Spinal disc problem'),
('Spinal Stenosis', 'Musculoskeletal', 'M48.0', 'Narrowed spinal canal'),
('Scoliosis', 'Musculoskeletal', 'M41.9', 'Curved spine'),
('Kyphosis', 'Musculoskeletal', 'M40.2', 'Hunched back'),
('Tendinitis', 'Musculoskeletal', 'M77.9', 'Tendon inflammation'),
('Bursitis', 'Musculoskeletal', 'M71.9', 'Bursa inflammation'),
('Plantar Fasciitis', 'Musculoskeletal', 'M72.2', 'Heel pain'),
('Rotator Cuff Injury', 'Musculoskeletal', 'M75.1', 'Shoulder injury'),
('Tennis Elbow', 'Musculoskeletal', 'M77.1', 'Lateral epicondylitis'),
('Lupus', 'Musculoskeletal', 'M32.9', 'Autoimmune disease'),
('Systemic Lupus Erythematosus', 'Musculoskeletal', 'M32.9', 'SLE'),
('Ankylosing Spondylitis', 'Musculoskeletal', 'M45.9', 'Spinal arthritis'),
('Polymyalgia Rheumatica', 'Musculoskeletal', 'M35.3', 'Muscle pain disorder'),

-- Kidney/Urological Conditions
('Chronic Kidney Disease', 'Renal', 'N18.9', 'Progressive kidney damage'),
('CKD', 'Renal', 'N18.9', 'Chronic kidney disease'),
('Kidney Failure', 'Renal', 'N19', 'End-stage renal disease'),
('Kidney Stones', 'Renal', 'N20.0', 'Renal calculi'),
('Urinary Tract Infection', 'Urological', 'N39.0', 'UTI'),
('Recurrent UTI', 'Urological', 'N39.0', 'Repeated infections'),
('Interstitial Cystitis', 'Urological', 'N30.1', 'Painful bladder syndrome'),
('Overactive Bladder', 'Urological', 'N32.81', 'Urinary urgency'),
('Urinary Incontinence', 'Urological', 'N39.4', 'Bladder control loss'),
('Benign Prostatic Hyperplasia', 'Urological', 'N40.0', 'Enlarged prostate'),
('BPH', 'Urological', 'N40.0', 'Prostate enlargement'),
('Prostatitis', 'Urological', 'N41.9', 'Prostate inflammation'),
('Erectile Dysfunction', 'Urological', 'N52.9', 'ED'),

-- Skin Conditions
('Eczema', 'Dermatological', 'L30.9', 'Skin inflammation'),
('Atopic Dermatitis', 'Dermatological', 'L20.9', 'Chronic eczema'),
('Psoriasis', 'Dermatological', 'L40.9', 'Scaly skin patches'),
('Rosacea', 'Dermatological', 'L71.9', 'Facial redness'),
('Acne', 'Dermatological', 'L70.9', 'Skin breakouts'),
('Vitiligo', 'Dermatological', 'L80', 'Skin pigment loss'),
('Hives', 'Dermatological', 'L50.9', 'Urticaria'),
('Chronic Urticaria', 'Dermatological', 'L50.8', 'Chronic hives'),
('Contact Dermatitis', 'Dermatological', 'L25.9', 'Skin reaction'),
('Seborrheic Dermatitis', 'Dermatological', 'L21.9', 'Dandruff/skin flaking'),
('Alopecia', 'Dermatological', 'L63.9', 'Hair loss'),
('Skin Cancer', 'Dermatological', 'C44.9', 'Malignant skin growth'),
('Melanoma', 'Dermatological', 'C43.9', 'Skin cancer'),
('Shingles', 'Dermatological', 'B02.9', 'Herpes zoster'),

-- Eye Conditions
('Glaucoma', 'Ophthalmological', 'H40.9', 'Eye pressure damage'),
('Cataracts', 'Ophthalmological', 'H26.9', 'Cloudy eye lens'),
('Macular Degeneration', 'Ophthalmological', 'H35.3', 'Vision loss'),
('Diabetic Retinopathy', 'Ophthalmological', 'E11.3', 'Diabetes eye damage'),
('Dry Eye Syndrome', 'Ophthalmological', 'H04.1', 'Insufficient tears'),
('Conjunctivitis', 'Ophthalmological', 'H10.9', 'Pink eye'),

-- Blood Disorders
('Anemia', 'Hematological', 'D64.9', 'Low red blood cells'),
('Iron Deficiency Anemia', 'Hematological', 'D50.9', 'Low iron anemia'),
('Sickle Cell Disease', 'Hematological', 'D57.1', 'Abnormal hemoglobin'),
('Thalassemia', 'Hematological', 'D56.9', 'Inherited blood disorder'),
('Hemophilia', 'Hematological', 'D66', 'Clotting disorder'),
('Thrombocytopenia', 'Hematological', 'D69.6', 'Low platelets'),
('Leukemia', 'Hematological', 'C95.9', 'Blood cancer'),
('Lymphoma', 'Hematological', 'C85.9', 'Lymph system cancer'),
('Polycythemia Vera', 'Hematological', 'D45', 'Excess red blood cells'),

-- Immune/Autoimmune Conditions
('HIV', 'Immunological', 'B20', 'Human immunodeficiency virus'),
('AIDS', 'Immunological', 'B24', 'Advanced HIV'),
('Autoimmune Disease', 'Immunological', 'M35.9', 'Immune attacks body'),
('Sjogrens Syndrome', 'Immunological', 'M35.0', 'Dry eyes and mouth'),
('Celiac Disease', 'Immunological', 'K90.0', 'Gluten autoimmune'),
('Primary Immunodeficiency', 'Immunological', 'D84.9', 'Weak immune system'),
('Chronic Fatigue Syndrome', 'Immunological', 'G93.3', 'ME/CFS'),

-- Cancer
('Breast Cancer', 'Oncological', 'C50.9', 'Breast malignancy'),
('Lung Cancer', 'Oncological', 'C34.9', 'Lung malignancy'),
('Colon Cancer', 'Oncological', 'C18.9', 'Colorectal cancer'),
('Prostate Cancer', 'Oncological', 'C61', 'Prostate malignancy'),
('Thyroid Cancer', 'Oncological', 'C73', 'Thyroid malignancy'),
('Pancreatic Cancer', 'Oncological', 'C25.9', 'Pancreas malignancy'),
('Liver Cancer', 'Oncological', 'C22.9', 'Hepatocellular carcinoma'),
('Ovarian Cancer', 'Oncological', 'C56.9', 'Ovary malignancy'),
('Cervical Cancer', 'Oncological', 'C53.9', 'Cervix malignancy'),
('Bladder Cancer', 'Oncological', 'C67.9', 'Bladder malignancy'),
('Kidney Cancer', 'Oncological', 'C64.9', 'Renal cell carcinoma'),
('Brain Tumor', 'Oncological', 'C71.9', 'Brain neoplasm'),
('Cancer (General)', 'Oncological', 'C80.1', 'Malignant neoplasm'),
('Cancer Survivor', 'Oncological', 'Z85.9', 'History of cancer'),

-- Infectious Diseases
('Hepatitis A', 'Infectious', 'B15.9', 'Liver infection'),
('Hepatitis B', 'Infectious', 'B18.1', 'Chronic liver infection'),
('Hepatitis C', 'Infectious', 'B18.2', 'Chronic liver infection'),
('Herpes Simplex', 'Infectious', 'B00.9', 'HSV infection'),
('HPV', 'Infectious', 'B97.7', 'Human papillomavirus'),
('Lyme Disease', 'Infectious', 'A69.2', 'Tick-borne infection'),
('Malaria', 'Infectious', 'B54', 'Parasitic infection'),
('Dengue', 'Infectious', 'A90', 'Mosquito-borne infection'),
('COVID-19', 'Infectious', 'U07.1', 'Coronavirus disease'),
('Long COVID', 'Infectious', 'U09.9', 'Post-COVID condition'),

-- Womens Health
('Endometriosis', 'Gynecological', 'N80.9', 'Uterine tissue growth'),
('Uterine Fibroids', 'Gynecological', 'D25.9', 'Benign uterine tumors'),
('Menopause', 'Gynecological', 'N95.1', 'End of menstruation'),
('Premenstrual Syndrome', 'Gynecological', 'N94.3', 'PMS'),
('PMDD', 'Gynecological', 'N94.3', 'Severe PMS'),
('Infertility', 'Gynecological', 'N97.9', 'Cannot conceive'),
('Ovarian Cysts', 'Gynecological', 'N83.2', 'Cysts on ovaries'),
('Pelvic Inflammatory Disease', 'Gynecological', 'N73.9', 'Reproductive infection'),

-- Other Conditions
('Chronic Pain', 'Pain', 'G89.2', 'Persistent pain'),
('Chronic Fatigue', 'General', 'R53.8', 'Persistent tiredness'),
('Vitamin D Deficiency', 'Nutritional', 'E55.9', 'Low vitamin D'),
('B12 Deficiency', 'Nutritional', 'E53.8', 'Low vitamin B12'),
('Iron Deficiency', 'Nutritional', 'E61.1', 'Low iron'),
('Hearing Loss', 'Otological', 'H91.9', 'Reduced hearing'),
('Deafness', 'Otological', 'H91.9', 'Hearing impairment')
ON CONFLICT (name) DO NOTHING;
"""

# Common medications for autocomplete
MEDICATIONS_DATA = """
INSERT INTO master_medications (name, generic_name, drug_class, common_dosages) VALUES
-- Pain/Fever
('Paracetamol', 'Acetaminophen', 'Analgesic', '500mg, 650mg'),
('Ibuprofen', 'Ibuprofen', 'NSAID', '200mg, 400mg'),
('Aspirin', 'Acetylsalicylic acid', 'NSAID/Antiplatelet', '75mg, 325mg'),
('Diclofenac', 'Diclofenac', 'NSAID', '50mg, 100mg'),
('Naproxen', 'Naproxen', 'NSAID', '250mg, 500mg'),
('Tramadol', 'Tramadol', 'Opioid', '50mg, 100mg'),

-- Antibiotics
('Amoxicillin', 'Amoxicillin', 'Penicillin Antibiotic', '250mg, 500mg'),
('Azithromycin', 'Azithromycin', 'Macrolide Antibiotic', '250mg, 500mg'),
('Ciprofloxacin', 'Ciprofloxacin', 'Fluoroquinolone', '250mg, 500mg'),
('Metronidazole', 'Metronidazole', 'Antibiotic', '400mg'),
('Doxycycline', 'Doxycycline', 'Tetracycline', '100mg'),
('Cefixime', 'Cefixime', 'Cephalosporin', '200mg, 400mg'),

-- Diabetes
('Metformin', 'Metformin', 'Biguanide', '500mg, 850mg, 1000mg'),
('Glimepiride', 'Glimepiride', 'Sulfonylurea', '1mg, 2mg, 4mg'),
('Sitagliptin', 'Sitagliptin', 'DPP-4 Inhibitor', '50mg, 100mg'),
('Insulin Glargine', 'Insulin', 'Long-acting Insulin', 'Various units'),
('Empagliflozin', 'Empagliflozin', 'SGLT2 Inhibitor', '10mg, 25mg'),

-- Blood Pressure
('Amlodipine', 'Amlodipine', 'Calcium Channel Blocker', '2.5mg, 5mg, 10mg'),
('Losartan', 'Losartan', 'ARB', '25mg, 50mg, 100mg'),
('Telmisartan', 'Telmisartan', 'ARB', '20mg, 40mg, 80mg'),
('Lisinopril', 'Lisinopril', 'ACE Inhibitor', '5mg, 10mg, 20mg'),
('Atenolol', 'Atenolol', 'Beta Blocker', '25mg, 50mg'),
('Metoprolol', 'Metoprolol', 'Beta Blocker', '25mg, 50mg, 100mg'),
('Hydrochlorothiazide', 'HCTZ', 'Diuretic', '12.5mg, 25mg'),

-- Cholesterol
('Atorvastatin', 'Atorvastatin', 'Statin', '10mg, 20mg, 40mg'),
('Rosuvastatin', 'Rosuvastatin', 'Statin', '5mg, 10mg, 20mg'),
('Simvastatin', 'Simvastatin', 'Statin', '10mg, 20mg, 40mg'),

-- Heart
('Aspirin (Low Dose)', 'Aspirin', 'Antiplatelet', '75mg, 81mg'),
('Clopidogrel', 'Clopidogrel', 'Antiplatelet', '75mg'),
('Warfarin', 'Warfarin', 'Anticoagulant', '1mg, 2mg, 5mg'),
('Rivaroxaban', 'Rivaroxaban', 'Anticoagulant', '10mg, 15mg, 20mg'),

-- Respiratory
('Salbutamol', 'Albuterol', 'Bronchodilator', '100mcg inhaler'),
('Montelukast', 'Montelukast', 'Leukotriene Inhibitor', '10mg'),
('Budesonide', 'Budesonide', 'Corticosteroid', '100mcg, 200mcg'),
('Cetirizine', 'Cetirizine', 'Antihistamine', '10mg'),
('Loratadine', 'Loratadine', 'Antihistamine', '10mg'),
('Fexofenadine', 'Fexofenadine', 'Antihistamine', '120mg, 180mg'),

-- GI
('Omeprazole', 'Omeprazole', 'PPI', '20mg, 40mg'),
('Pantoprazole', 'Pantoprazole', 'PPI', '20mg, 40mg'),
('Ranitidine', 'Ranitidine', 'H2 Blocker', '150mg'),
('Domperidone', 'Domperidone', 'Prokinetic', '10mg'),
('Ondansetron', 'Ondansetron', 'Antiemetic', '4mg, 8mg'),

-- Mental Health
('Sertraline', 'Sertraline', 'SSRI', '25mg, 50mg, 100mg'),
('Escitalopram', 'Escitalopram', 'SSRI', '5mg, 10mg, 20mg'),
('Fluoxetine', 'Fluoxetine', 'SSRI', '20mg, 40mg'),
('Alprazolam', 'Alprazolam', 'Benzodiazepine', '0.25mg, 0.5mg'),
('Clonazepam', 'Clonazepam', 'Benzodiazepine', '0.5mg, 1mg'),

-- Thyroid
('Levothyroxine', 'Levothyroxine', 'Thyroid Hormone', '25mcg, 50mcg, 100mcg'),
('Methimazole', 'Methimazole', 'Antithyroid', '5mg, 10mg'),

-- Vitamins/Supplements
('Vitamin D3', 'Cholecalciferol', 'Vitamin', '1000IU, 60000IU'),
('Vitamin B12', 'Methylcobalamin', 'Vitamin', '500mcg, 1500mcg'),
('Folic Acid', 'Folic Acid', 'Vitamin', '5mg'),
('Iron (Ferrous Sulfate)', 'Ferrous Sulfate', 'Iron Supplement', '200mg'),
('Calcium', 'Calcium Carbonate', 'Mineral', '500mg, 1000mg')
ON CONFLICT (name) DO NOTHING;
"""
