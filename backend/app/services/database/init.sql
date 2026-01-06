-- ===========================================
-- CMC Health Database Initialization Script
-- ===========================================
-- This script is automatically run when the PostgreSQL container starts

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

-- ============================================
-- INSERT MASTER DATA: ALLERGENS
-- ============================================
INSERT INTO master_allergens (name, category, common_reactions, severity_typical) VALUES
-- Drug Allergies (Antibiotics)
('Penicillin', 'Drug - Antibiotic', 'Rash, hives, anaphylaxis', 'severe'),
('Amoxicillin', 'Drug - Antibiotic', 'Rash, hives, swelling', 'moderate'),
('Ampicillin', 'Drug - Antibiotic', 'Rash, itching', 'moderate'),
('Cephalosporins', 'Drug - Antibiotic', 'Rash, breathing difficulty', 'severe'),
('Sulfonamides', 'Drug - Antibiotic', 'Rash, Stevens-Johnson syndrome', 'severe'),
('Erythromycin', 'Drug - Antibiotic', 'Nausea, rash', 'mild'),
('Azithromycin', 'Drug - Antibiotic', 'Rash, diarrhea', 'mild'),
('Ciprofloxacin', 'Drug - Antibiotic', 'Rash, tendon problems', 'moderate'),
('Metronidazole', 'Drug - Antibiotic', 'Nausea, metallic taste', 'mild'),
('Tetracycline', 'Drug - Antibiotic', 'Photosensitivity, nausea', 'moderate'),
('Doxycycline', 'Drug - Antibiotic', 'Photosensitivity, esophagitis', 'moderate'),
-- Pain Medications
('Aspirin', 'Drug - NSAID', 'Stomach bleeding, asthma', 'moderate'),
('Ibuprofen', 'Drug - NSAID', 'Stomach upset, rash', 'moderate'),
('Naproxen', 'Drug - NSAID', 'Stomach bleeding, rash', 'moderate'),
('Diclofenac', 'Drug - NSAID', 'Stomach upset, rash', 'moderate'),
('Acetaminophen', 'Drug - Analgesic', 'Rash, liver damage (overdose)', 'mild'),
('Paracetamol', 'Drug - Analgesic', 'Rash, liver damage (overdose)', 'mild'),
('Tramadol', 'Drug - Opioid', 'Nausea, seizures', 'moderate'),
('Codeine', 'Drug - Opioid', 'Respiratory depression, constipation', 'severe'),
('Morphine', 'Drug - Opioid', 'Respiratory depression, nausea', 'severe'),
-- Anesthetics
('Lidocaine', 'Drug - Anesthetic', 'Numbness, dizziness', 'mild'),
('Novocaine', 'Drug - Anesthetic', 'Allergic reaction, numbness', 'moderate'),
-- Cardiovascular Drugs
('ACE Inhibitors', 'Drug - Cardiovascular', 'Cough, angioedema', 'moderate'),
('Lisinopril', 'Drug - Cardiovascular', 'Cough, angioedema', 'moderate'),
('Beta Blockers', 'Drug - Cardiovascular', 'Bradycardia, fatigue', 'moderate'),
('Statins', 'Drug - Cardiovascular', 'Muscle pain, liver issues', 'moderate'),
-- Other Drugs
('Insulin', 'Drug - Hormone', 'Hypoglycemia, injection site reaction', 'moderate'),
('Metformin', 'Drug - Diabetes', 'GI upset, lactic acidosis', 'moderate'),
('Contrast Dye', 'Drug - Diagnostic', 'Anaphylaxis, kidney damage', 'severe'),
('Iodine', 'Drug - Antiseptic', 'Rash, anaphylaxis', 'moderate'),
('Latex', 'Material', 'Rash, anaphylaxis', 'severe'),
-- Food Allergies
('Peanuts', 'Food - Legume', 'Anaphylaxis, hives, swelling', 'severe'),
('Tree Nuts', 'Food - Nut', 'Anaphylaxis, hives', 'severe'),
('Almonds', 'Food - Nut', 'Hives, swelling', 'severe'),
('Cashews', 'Food - Nut', 'Anaphylaxis, hives', 'severe'),
('Walnuts', 'Food - Nut', 'Anaphylaxis, swelling', 'severe'),
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
('Sesame', 'Food - Seed', 'Anaphylaxis, hives', 'severe'),
-- Environmental Allergies
('Dust Mites', 'Environmental', 'Sneezing, runny nose, asthma', 'moderate'),
('Pollen', 'Environmental', 'Sneezing, itchy eyes, congestion', 'moderate'),
('Mold', 'Environmental', 'Sneezing, asthma, skin rash', 'moderate'),
('Pet Dander', 'Environmental', 'Sneezing, itchy eyes, asthma', 'moderate'),
('Cat Dander', 'Environmental', 'Sneezing, hives, asthma', 'moderate'),
('Dog Dander', 'Environmental', 'Sneezing, congestion', 'moderate'),
-- Insect Allergies
('Bee Venom', 'Insect', 'Anaphylaxis, swelling', 'severe'),
('Wasp Venom', 'Insect', 'Anaphylaxis, swelling', 'severe'),
-- Contact Allergies
('Nickel', 'Contact', 'Contact dermatitis, rash', 'mild'),
('Fragrance', 'Contact', 'Contact dermatitis, headache', 'mild'),
('Poison Ivy', 'Plant', 'Contact dermatitis', 'moderate')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- INSERT MASTER DATA: MEDICAL CONDITIONS
-- ============================================
INSERT INTO master_conditions (name, category, icd10_code, description) VALUES
-- Cardiovascular
('Hypertension', 'Cardiovascular', 'I10', 'High blood pressure'),
('High Blood Pressure', 'Cardiovascular', 'I10', 'Elevated arterial blood pressure'),
('Coronary Artery Disease', 'Cardiovascular', 'I25.1', 'Narrowing of coronary arteries'),
('Heart Disease', 'Cardiovascular', 'I51.9', 'General heart condition'),
('Congestive Heart Failure', 'Cardiovascular', 'I50.9', 'Heart cannot pump effectively'),
('Atrial Fibrillation', 'Cardiovascular', 'I48.91', 'Irregular rapid heart rhythm'),
('Arrhythmia', 'Cardiovascular', 'I49.9', 'Irregular heartbeat'),
('Angina', 'Cardiovascular', 'I20.9', 'Chest pain from reduced blood flow'),
('Heart Attack', 'Cardiovascular', 'I21.9', 'Blocked blood flow to heart'),
('Stroke', 'Cardiovascular', 'I63.9', 'Brain blood flow interruption'),
('Deep Vein Thrombosis', 'Cardiovascular', 'I82.9', 'Blood clot in deep vein'),
-- Endocrine
('Diabetes Type 1', 'Endocrine', 'E10', 'Autoimmune diabetes'),
('Diabetes Type 2', 'Endocrine', 'E11', 'Insulin resistance diabetes'),
('Diabetes', 'Endocrine', 'E11.9', 'Blood sugar disorder'),
('Hypothyroidism', 'Endocrine', 'E03.9', 'Underactive thyroid'),
('Hyperthyroidism', 'Endocrine', 'E05.9', 'Overactive thyroid'),
('Thyroid Disease', 'Endocrine', 'E07.9', 'Thyroid gland disorder'),
('Obesity', 'Endocrine', 'E66', 'Excess body weight'),
('Metabolic Syndrome', 'Endocrine', 'E88.81', 'Cluster of metabolic conditions'),
-- Respiratory
('Asthma', 'Respiratory', 'J45.9', 'Chronic airway inflammation'),
('COPD', 'Respiratory', 'J44.9', 'Chronic obstructive pulmonary disease'),
('Chronic Bronchitis', 'Respiratory', 'J42', 'Persistent bronchial inflammation'),
('Emphysema', 'Respiratory', 'J43.9', 'Lung air sac damage'),
('Sleep Apnea', 'Respiratory', 'G47.33', 'Breathing interruption during sleep'),
('Allergic Rhinitis', 'Respiratory', 'J30.9', 'Nasal inflammation from allergens'),
('Sinusitis', 'Respiratory', 'J32.9', 'Sinus inflammation'),
-- Gastrointestinal
('GERD', 'Gastrointestinal', 'K21.0', 'Gastroesophageal reflux disease'),
('Acid Reflux', 'Gastrointestinal', 'K21.0', 'Stomach acid backflow'),
('Peptic Ulcer', 'Gastrointestinal', 'K27.9', 'Stomach or intestinal ulcer'),
('IBS', 'Gastrointestinal', 'K58.9', 'Irritable bowel syndrome'),
('Crohns Disease', 'Gastrointestinal', 'K50.9', 'Inflammatory bowel disease'),
('Ulcerative Colitis', 'Gastrointestinal', 'K51.9', 'Colon inflammation'),
('Celiac Disease', 'Gastrointestinal', 'K90.0', 'Gluten intolerance'),
('Fatty Liver Disease', 'Gastrointestinal', 'K76.0', 'Liver fat accumulation'),
('Hepatitis', 'Gastrointestinal', 'K75.9', 'Liver inflammation'),
('Cirrhosis', 'Gastrointestinal', 'K74.6', 'Liver scarring'),
('Gallstones', 'Gastrointestinal', 'K80.2', 'Gallbladder stones'),
-- Musculoskeletal
('Arthritis', 'Musculoskeletal', 'M13.9', 'Joint inflammation'),
('Rheumatoid Arthritis', 'Musculoskeletal', 'M06.9', 'Autoimmune joint disease'),
('Osteoarthritis', 'Musculoskeletal', 'M19.9', 'Degenerative joint disease'),
('Osteoporosis', 'Musculoskeletal', 'M81.0', 'Bone density loss'),
('Gout', 'Musculoskeletal', 'M10.9', 'Uric acid crystal arthritis'),
('Fibromyalgia', 'Musculoskeletal', 'M79.7', 'Widespread muscle pain'),
('Back Pain', 'Musculoskeletal', 'M54.5', 'Lower back pain'),
('Sciatica', 'Musculoskeletal', 'M54.3', 'Sciatic nerve pain'),
('Herniated Disc', 'Musculoskeletal', 'M51.2', 'Spinal disc displacement'),
-- Neurological
('Migraine', 'Neurological', 'G43.9', 'Severe recurring headaches'),
('Epilepsy', 'Neurological', 'G40.9', 'Seizure disorder'),
('Parkinsons Disease', 'Neurological', 'G20', 'Movement disorder'),
('Alzheimers Disease', 'Neurological', 'G30.9', 'Progressive dementia'),
('Multiple Sclerosis', 'Neurological', 'G35', 'Autoimmune nerve disease'),
('Neuropathy', 'Neurological', 'G62.9', 'Nerve damage'),
('Carpal Tunnel', 'Neurological', 'G56.0', 'Wrist nerve compression'),
-- Mental Health
('Depression', 'Mental Health', 'F32.9', 'Mood disorder'),
('Anxiety Disorder', 'Mental Health', 'F41.9', 'Anxiety condition'),
('Bipolar Disorder', 'Mental Health', 'F31.9', 'Mood swings disorder'),
('PTSD', 'Mental Health', 'F43.1', 'Post-traumatic stress'),
('OCD', 'Mental Health', 'F42.9', 'Obsessive-compulsive disorder'),
('ADHD', 'Mental Health', 'F90.9', 'Attention deficit disorder'),
('Insomnia', 'Mental Health', 'G47.0', 'Sleep difficulty'),
-- Kidney/Urological
('Chronic Kidney Disease', 'Kidney', 'N18.9', 'Progressive kidney damage'),
('Kidney Stones', 'Kidney', 'N20.0', 'Renal calculi'),
('UTI', 'Urological', 'N39.0', 'Urinary tract infection'),
('Benign Prostatic Hyperplasia', 'Urological', 'N40.0', 'Enlarged prostate'),
('Overactive Bladder', 'Urological', 'N32.81', 'Urinary urgency'),
-- Cancer
('Breast Cancer', 'Oncology', 'C50.9', 'Breast malignancy'),
('Lung Cancer', 'Oncology', 'C34.9', 'Lung malignancy'),
('Colon Cancer', 'Oncology', 'C18.9', 'Colon malignancy'),
('Prostate Cancer', 'Oncology', 'C61', 'Prostate malignancy'),
('Skin Cancer', 'Oncology', 'C44.9', 'Skin malignancy'),
('Leukemia', 'Oncology', 'C95.9', 'Blood cancer'),
('Lymphoma', 'Oncology', 'C85.9', 'Lymphatic cancer'),
-- Autoimmune
('Lupus', 'Autoimmune', 'M32.9', 'Systemic lupus erythematosus'),
('Psoriasis', 'Autoimmune', 'L40.9', 'Skin autoimmune condition'),
('Hashimotos Disease', 'Autoimmune', 'E06.3', 'Thyroid autoimmune'),
-- Other
('Anemia', 'Hematological', 'D64.9', 'Low red blood cell count'),
('High Cholesterol', 'Metabolic', 'E78.0', 'Elevated blood lipids'),
('Hyperlipidemia', 'Metabolic', 'E78.5', 'High blood fat levels'),
('HIV/AIDS', 'Infectious', 'B20', 'Human immunodeficiency virus'),
('Hepatitis B', 'Infectious', 'B18.1', 'Chronic liver infection'),
('Hepatitis C', 'Infectious', 'B18.2', 'Chronic liver infection'),
('Tuberculosis', 'Infectious', 'A15.9', 'TB infection'),
('Eczema', 'Dermatological', 'L30.9', 'Skin inflammation'),
('Acne', 'Dermatological', 'L70.9', 'Skin condition'),
('Glaucoma', 'Ophthalmological', 'H40.9', 'Eye pressure disorder'),
('Macular Degeneration', 'Ophthalmological', 'H35.30', 'Vision loss disorder'),
('Cataracts', 'Ophthalmological', 'H25.9', 'Lens clouding'),
('Tinnitus', 'Otological', 'H93.1', 'Ear ringing'),
('Hearing Loss', 'Otological', 'H91.9', 'Hearing impairment')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- INSERT MASTER DATA: MEDICATIONS
-- ============================================
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
('Aspirin Low Dose', 'Aspirin', 'Antiplatelet', '75mg, 81mg'),
('Clopidogrel', 'Clopidogrel', 'Antiplatelet', '75mg'),
('Warfarin', 'Warfarin', 'Anticoagulant', '1mg, 2mg, 5mg'),
-- Respiratory
('Salbutamol', 'Albuterol', 'Bronchodilator', '100mcg inhaler'),
('Montelukast', 'Montelukast', 'Leukotriene Inhibitor', '10mg'),
('Cetirizine', 'Cetirizine', 'Antihistamine', '10mg'),
('Loratadine', 'Loratadine', 'Antihistamine', '10mg'),
('Fexofenadine', 'Fexofenadine', 'Antihistamine', '120mg, 180mg'),
-- GI
('Omeprazole', 'Omeprazole', 'PPI', '20mg, 40mg'),
('Pantoprazole', 'Pantoprazole', 'PPI', '20mg, 40mg'),
('Domperidone', 'Domperidone', 'Prokinetic', '10mg'),
('Ondansetron', 'Ondansetron', 'Antiemetic', '4mg, 8mg'),
-- Mental Health
('Sertraline', 'Sertraline', 'SSRI', '25mg, 50mg, 100mg'),
('Escitalopram', 'Escitalopram', 'SSRI', '5mg, 10mg, 20mg'),
('Alprazolam', 'Alprazolam', 'Benzodiazepine', '0.25mg, 0.5mg'),
-- Thyroid
('Levothyroxine', 'Levothyroxine', 'Thyroid Hormone', '25mcg, 50mcg, 100mcg'),
-- Vitamins
('Vitamin D3', 'Cholecalciferol', 'Vitamin', '1000IU, 60000IU'),
('Vitamin B12', 'Methylcobalamin', 'Vitamin', '500mcg, 1500mcg'),
('Folic Acid', 'Folic Acid', 'Vitamin', '5mg'),
('Iron Supplement', 'Ferrous Sulfate', 'Iron Supplement', '200mg'),
('Calcium', 'Calcium Carbonate', 'Mineral', '500mg, 1000mg')
ON CONFLICT (name) DO NOTHING;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'CMC Health database initialized successfully!';
END $$;
