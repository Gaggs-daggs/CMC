"""
Natural Remedies, Home Treatments, and Ayurvedic/Traditional Medicine Database
"""

# ========================================
# NATURAL REMEDIES DATABASE
# ========================================

NATURAL_REMEDIES = {
    # ==========================================
    # RESPIRATORY CONDITIONS
    # ==========================================
    "cold_flu": [
        {"name": "Ginger Tea", "preparation": "Boil fresh ginger slices in water for 10 min, add honey", "frequency": "3-4 times daily", "benefits": "Anti-inflammatory, soothes throat", "category": "Herbal"},
        {"name": "Honey + Lemon", "preparation": "1 tbsp honey + juice of half lemon in warm water", "frequency": "2-3 times daily", "benefits": "Soothes throat, vitamin C", "category": "Traditional"},
        {"name": "Turmeric Milk (Golden Milk)", "preparation": "1 tsp turmeric + pepper in warm milk", "frequency": "Once daily at night", "benefits": "Anti-inflammatory, immune boost", "category": "Ayurvedic"},
        {"name": "Steam Inhalation", "preparation": "Hot water in bowl, add eucalyptus/menthol, inhale steam", "frequency": "2-3 times daily", "benefits": "Clears congestion", "category": "Traditional"},
        {"name": "Garlic", "preparation": "1-2 raw cloves crushed, or in food", "frequency": "Daily", "benefits": "Natural antibiotic, immune support", "category": "Traditional"},
        {"name": "Elderberry Syrup", "preparation": "Follow product directions", "frequency": "As directed", "benefits": "Antiviral properties", "category": "Herbal"},
        {"name": "Tulsi (Holy Basil) Tea", "preparation": "Steep fresh leaves in hot water", "frequency": "2-3 times daily", "benefits": "Respiratory support, adaptogen", "category": "Ayurvedic"},
        {"name": "Chicken Soup", "preparation": "Homemade with vegetables", "frequency": "1-2 bowls daily", "benefits": "Hydration, anti-inflammatory", "category": "Traditional"},
        {"name": "Apple Cider Vinegar", "preparation": "1-2 tbsp in warm water with honey", "frequency": "2-3 times daily", "benefits": "Alkalizing, antimicrobial", "category": "Traditional"},
        {"name": "Eucalyptus Oil", "preparation": "Add to diffuser or steam", "frequency": "As needed", "benefits": "Decongestant", "category": "Aromatherapy"},
    ],
    
    "cough": [
        {"name": "Honey", "preparation": "1-2 tsp raw honey, let it coat throat", "frequency": "Every few hours", "benefits": "Natural cough suppressant", "category": "Traditional", "note": "Not for children under 1"},
        {"name": "Licorice Root Tea", "preparation": "Steep 1 tsp dried root in hot water", "frequency": "2-3 times daily", "benefits": "Soothes throat, expectorant", "category": "Herbal"},
        {"name": "Thyme Tea", "preparation": "Steep fresh or dried thyme in hot water", "frequency": "2-3 times daily", "benefits": "Antispasmodic, antimicrobial", "category": "Herbal"},
        {"name": "Marshmallow Root", "preparation": "Tea or lozenges", "frequency": "As needed", "benefits": "Mucilaginous, soothes throat", "category": "Herbal"},
        {"name": "Peppermint Tea", "preparation": "Steep fresh or dried leaves", "frequency": "2-3 times daily", "benefits": "Menthol soothes throat", "category": "Herbal"},
        {"name": "Salt Water Gargle", "preparation": "1/2 tsp salt in warm water", "frequency": "Every 2-3 hours", "benefits": "Reduces inflammation, kills bacteria", "category": "Traditional"},
        {"name": "Ginger + Honey", "preparation": "Fresh ginger juice with honey", "frequency": "2-3 times daily", "benefits": "Anti-inflammatory", "category": "Ayurvedic"},
        {"name": "Black Pepper + Honey", "preparation": "1/4 tsp pepper in 1 tsp honey", "frequency": "2-3 times daily", "benefits": "Breaks up mucus", "category": "Ayurvedic"},
    ],
    
    "sore_throat": [
        {"name": "Salt Water Gargle", "preparation": "1/2-1 tsp salt in 8oz warm water", "frequency": "Every 2-3 hours", "benefits": "Reduces swelling, kills bacteria", "category": "Traditional"},
        {"name": "Honey + Lemon Tea", "preparation": "Honey and lemon in warm water", "frequency": "Multiple times daily", "benefits": "Soothing, antibacterial", "category": "Traditional"},
        {"name": "Slippery Elm", "preparation": "Lozenges or tea", "frequency": "As needed", "benefits": "Coats and soothes throat", "category": "Herbal"},
        {"name": "Chamomile Tea", "preparation": "Steep chamomile flowers", "frequency": "2-3 times daily", "benefits": "Anti-inflammatory, relaxing", "category": "Herbal"},
        {"name": "Sage Gargle", "preparation": "Steep sage, cool, gargle", "frequency": "Several times daily", "benefits": "Antiseptic", "category": "Herbal"},
        {"name": "Turmeric Gargle", "preparation": "1/2 tsp turmeric + salt in warm water", "frequency": "2-3 times daily", "benefits": "Anti-inflammatory, antimicrobial", "category": "Ayurvedic"},
        {"name": "Clove", "preparation": "Chew whole clove or clove tea", "frequency": "As needed", "benefits": "Natural anesthetic", "category": "Traditional"},
    ],

    # ==========================================
    # DIGESTIVE CONDITIONS
    # ==========================================
    "indigestion_acidity": [
        {"name": "Ginger", "preparation": "Fresh ginger tea or chew small piece", "frequency": "After meals", "benefits": "Aids digestion, reduces nausea", "category": "Traditional"},
        {"name": "Baking Soda", "preparation": "1/2 tsp in glass of water", "frequency": "As needed", "benefits": "Neutralizes acid quickly", "category": "Traditional", "warning": "Not for regular use"},
        {"name": "Fennel Seeds (Saunf)", "preparation": "Chew 1 tsp after meals or make tea", "frequency": "After meals", "benefits": "Reduces gas, aids digestion", "category": "Ayurvedic"},
        {"name": "Ajwain (Carom Seeds)", "preparation": "Chew with salt or in water", "frequency": "After meals", "benefits": "Relieves gas, bloating", "category": "Ayurvedic"},
        {"name": "Jeera (Cumin) Water", "preparation": "Boil 1 tsp cumin in water, strain", "frequency": "2-3 times daily", "benefits": "Digestive, reduces acidity", "category": "Ayurvedic"},
        {"name": "Cold Milk", "preparation": "1 glass cold milk", "frequency": "When acidic", "benefits": "Neutralizes acid", "category": "Traditional"},
        {"name": "Banana", "preparation": "Eat ripe banana", "frequency": "Daily", "benefits": "Natural antacid", "category": "Food"},
        {"name": "Aloe Vera Juice", "preparation": "2 tbsp pure aloe juice", "frequency": "Before meals", "benefits": "Soothes stomach lining", "category": "Herbal"},
        {"name": "Mint Tea", "preparation": "Fresh mint leaves in hot water", "frequency": "After meals", "benefits": "Relieves indigestion", "category": "Herbal"},
        {"name": "Apple Cider Vinegar", "preparation": "1 tbsp in water before meals", "frequency": "Before meals", "benefits": "Balances stomach acid", "category": "Traditional"},
    ],
    
    "constipation": [
        {"name": "Warm Water with Lemon", "preparation": "Juice of half lemon in warm water", "frequency": "First thing in morning", "benefits": "Stimulates digestion", "category": "Traditional"},
        {"name": "Prunes/Prune Juice", "preparation": "4-5 prunes or 1/2 cup juice", "frequency": "Daily", "benefits": "Natural laxative, fiber", "category": "Food"},
        {"name": "Psyllium Husk (Isabgol)", "preparation": "1-2 tsp in water or milk", "frequency": "At bedtime", "benefits": "Bulk-forming fiber", "category": "Ayurvedic"},
        {"name": "Flaxseeds", "preparation": "1 tbsp ground flaxseeds in water", "frequency": "Daily", "benefits": "Fiber and healthy fats", "category": "Food"},
        {"name": "Triphala", "preparation": "1/2-1 tsp powder in warm water", "frequency": "At bedtime", "benefits": "Gentle laxative, digestive tonic", "category": "Ayurvedic"},
        {"name": "Castor Oil", "preparation": "1-2 tsp on empty stomach", "frequency": "Occasional use only", "benefits": "Strong laxative", "category": "Traditional"},
        {"name": "Figs (Anjeer)", "preparation": "Soak 2-3 figs overnight, eat in morning", "frequency": "Daily", "benefits": "High fiber", "category": "Food"},
        {"name": "Olive Oil", "preparation": "1 tbsp on empty stomach", "frequency": "Morning", "benefits": "Lubricates intestines", "category": "Traditional"},
        {"name": "Papaya", "preparation": "1 cup fresh papaya", "frequency": "Daily", "benefits": "Digestive enzymes, fiber", "category": "Food"},
    ],
    
    "diarrhea": [
        {"name": "ORS (Homemade)", "preparation": "6 tsp sugar + 1/2 tsp salt in 1L water", "frequency": "Throughout day", "benefits": "Rehydration", "category": "Essential"},
        {"name": "BRAT Diet", "preparation": "Bananas, Rice, Applesauce, Toast", "frequency": "Until better", "benefits": "Binding, easy to digest", "category": "Diet"},
        {"name": "Ginger Tea", "preparation": "Fresh ginger in hot water", "frequency": "2-3 times daily", "benefits": "Reduces inflammation", "category": "Herbal"},
        {"name": "Pomegranate Juice", "preparation": "Fresh pomegranate juice", "frequency": "2-3 times daily", "benefits": "Astringent, binding", "category": "Ayurvedic"},
        {"name": "Curd/Yogurt", "preparation": "Plain yogurt with banana", "frequency": "2-3 times daily", "benefits": "Probiotics, binding", "category": "Food"},
        {"name": "Chamomile Tea", "preparation": "Steep chamomile", "frequency": "2-3 times daily", "benefits": "Antispasmodic", "category": "Herbal"},
        {"name": "Fenugreek Seeds", "preparation": "1 tsp with yogurt", "frequency": "2-3 times daily", "benefits": "Mucilaginous, binding", "category": "Ayurvedic"},
        {"name": "Raw Banana", "preparation": "Boiled raw banana", "frequency": "As meals", "benefits": "Binding effect", "category": "Food"},
    ],
    
    "nausea_vomiting": [
        {"name": "Ginger", "preparation": "Ginger tea, ginger ale, or fresh ginger", "frequency": "As needed", "benefits": "Anti-nausea", "category": "Traditional"},
        {"name": "Peppermint", "preparation": "Tea or inhale peppermint oil", "frequency": "As needed", "benefits": "Calms stomach", "category": "Herbal"},
        {"name": "Lemon", "preparation": "Smell fresh lemon or drink lemon water", "frequency": "As needed", "benefits": "Reduces nausea", "category": "Traditional"},
        {"name": "Crackers", "preparation": "Plain crackers", "frequency": "Small amounts frequently", "benefits": "Settles stomach", "category": "Food"},
        {"name": "Fennel Tea", "preparation": "Steep fennel seeds", "frequency": "2-3 times daily", "benefits": "Digestive, anti-nausea", "category": "Herbal"},
        {"name": "Clove", "preparation": "Chew or make tea", "frequency": "As needed", "benefits": "Reduces nausea", "category": "Traditional"},
        {"name": "Cardamom", "preparation": "Chew seeds or in tea", "frequency": "As needed", "benefits": "Settles stomach", "category": "Ayurvedic"},
    ],

    # ==========================================
    # PAIN & INFLAMMATION
    # ==========================================
    "headache": [
        {"name": "Peppermint Oil", "preparation": "Apply diluted to temples", "frequency": "As needed", "benefits": "Cooling, pain relief", "category": "Aromatherapy"},
        {"name": "Lavender Oil", "preparation": "Inhale or apply to temples", "frequency": "As needed", "benefits": "Relaxing, reduces tension", "category": "Aromatherapy"},
        {"name": "Ginger Tea", "preparation": "Fresh ginger in hot water", "frequency": "2-3 times daily", "benefits": "Anti-inflammatory", "category": "Herbal"},
        {"name": "Caffeine", "preparation": "Cup of coffee or tea", "frequency": "At onset", "benefits": "Constricts blood vessels", "category": "Traditional"},
        {"name": "Cold/Hot Compress", "preparation": "Ice pack or warm cloth on head/neck", "frequency": "15-20 minutes", "benefits": "Reduces inflammation", "category": "Physical"},
        {"name": "Feverfew", "preparation": "Supplement or tea", "frequency": "Daily for prevention", "benefits": "Migraine prevention", "category": "Herbal"},
        {"name": "Magnesium", "preparation": "Supplement or magnesium-rich foods", "frequency": "Daily", "benefits": "Muscle relaxation", "category": "Supplement"},
        {"name": "Butterbur", "preparation": "Supplement (PA-free)", "frequency": "As directed", "benefits": "Migraine prevention", "category": "Herbal"},
        {"name": "Clove Oil", "preparation": "Apply diluted to temples", "frequency": "As needed", "benefits": "Analgesic", "category": "Ayurvedic"},
    ],
    
    "joint_muscle_pain": [
        {"name": "Turmeric", "preparation": "1 tsp daily in milk or food", "frequency": "Daily", "benefits": "Powerful anti-inflammatory", "category": "Ayurvedic"},
        {"name": "Ginger", "preparation": "Tea or in food", "frequency": "Daily", "benefits": "Reduces inflammation", "category": "Traditional"},
        {"name": "Epsom Salt Bath", "preparation": "2 cups in warm bath", "frequency": "2-3 times weekly", "benefits": "Muscle relaxation, magnesium", "category": "Traditional"},
        {"name": "Massage with Sesame Oil", "preparation": "Warm oil massage", "frequency": "Daily", "benefits": "Improves circulation, reduces pain", "category": "Ayurvedic"},
        {"name": "Hot/Cold Therapy", "preparation": "Alternate hot and cold packs", "frequency": "Several times daily", "benefits": "Reduces inflammation and pain", "category": "Physical"},
        {"name": "Arnica", "preparation": "Topical cream or gel", "frequency": "2-3 times daily", "benefits": "Reduces bruising, pain", "category": "Homeopathic"},
        {"name": "Capsaicin", "preparation": "Topical cream", "frequency": "3-4 times daily", "benefits": "Pain relief", "category": "Herbal"},
        {"name": "Boswellia (Shallaki)", "preparation": "Supplement", "frequency": "As directed", "benefits": "Anti-inflammatory", "category": "Ayurvedic"},
        {"name": "Willow Bark", "preparation": "Tea or supplement", "frequency": "As needed", "benefits": "Natural aspirin", "category": "Herbal"},
        {"name": "Eucalyptus Oil", "preparation": "Dilute and massage into area", "frequency": "2-3 times daily", "benefits": "Pain relief, anti-inflammatory", "category": "Aromatherapy"},
    ],
    
    "back_pain": [
        {"name": "Heat Therapy", "preparation": "Hot water bottle or heating pad", "frequency": "20 min, several times daily", "benefits": "Relaxes muscles", "category": "Physical"},
        {"name": "Ice Pack", "preparation": "Ice wrapped in cloth", "frequency": "20 min, first 48 hours", "benefits": "Reduces inflammation", "category": "Physical"},
        {"name": "Gentle Stretching", "preparation": "Cat-cow, child's pose, knee-to-chest", "frequency": "Several times daily", "benefits": "Relieves tension", "category": "Exercise"},
        {"name": "Turmeric + Black Pepper", "preparation": "In milk or supplement", "frequency": "Daily", "benefits": "Anti-inflammatory", "category": "Ayurvedic"},
        {"name": "Mustard Oil Massage", "preparation": "Warm mustard oil massage", "frequency": "Daily", "benefits": "Increases blood flow", "category": "Ayurvedic"},
        {"name": "Epsom Salt Bath", "preparation": "2 cups in warm bath", "frequency": "2-3 times weekly", "benefits": "Muscle relaxation", "category": "Traditional"},
        {"name": "Devil's Claw", "preparation": "Supplement", "frequency": "As directed", "benefits": "Anti-inflammatory, pain relief", "category": "Herbal"},
        {"name": "Walking", "preparation": "Gentle walking", "frequency": "Daily", "benefits": "Keeps spine mobile", "category": "Exercise"},
    ],

    # ==========================================
    # SKIN CONDITIONS
    # ==========================================
    "acne": [
        {"name": "Tea Tree Oil", "preparation": "Dilute with carrier oil, apply to spots", "frequency": "1-2 times daily", "benefits": "Antibacterial", "category": "Herbal"},
        {"name": "Aloe Vera", "preparation": "Fresh gel or pure aloe", "frequency": "Daily", "benefits": "Soothing, healing", "category": "Herbal"},
        {"name": "Honey Mask", "preparation": "Apply raw honey, leave 20 min", "frequency": "2-3 times weekly", "benefits": "Antibacterial, moisturizing", "category": "Traditional"},
        {"name": "Turmeric Paste", "preparation": "Turmeric + honey or yogurt", "frequency": "2-3 times weekly", "benefits": "Anti-inflammatory", "category": "Ayurvedic"},
        {"name": "Neem", "preparation": "Neem paste or neem water", "frequency": "Daily", "benefits": "Antibacterial, antifungal", "category": "Ayurvedic"},
        {"name": "Apple Cider Vinegar Toner", "preparation": "1 part ACV : 3 parts water", "frequency": "Once daily", "benefits": "Balances pH", "category": "Traditional"},
        {"name": "Green Tea", "preparation": "Cooled tea as toner or in face mask", "frequency": "Daily", "benefits": "Antioxidant, reduces sebum", "category": "Herbal"},
        {"name": "Zinc Supplement", "preparation": "15-30mg daily", "frequency": "Daily with food", "benefits": "Reduces inflammation", "category": "Supplement"},
        {"name": "Multani Mitti (Fuller's Earth)", "preparation": "Paste with rose water", "frequency": "1-2 times weekly", "benefits": "Absorbs oil, cleanses", "category": "Ayurvedic"},
    ],
    
    "eczema_dry_skin": [
        {"name": "Coconut Oil", "preparation": "Apply virgin coconut oil", "frequency": "Several times daily", "benefits": "Moisturizing, antimicrobial", "category": "Traditional"},
        {"name": "Oatmeal Bath", "preparation": "Colloidal oatmeal in lukewarm bath", "frequency": "Daily or as needed", "benefits": "Soothes itching", "category": "Traditional"},
        {"name": "Aloe Vera", "preparation": "Fresh gel or pure aloe", "frequency": "2-3 times daily", "benefits": "Soothing, healing", "category": "Herbal"},
        {"name": "Sunflower Seed Oil", "preparation": "Apply topically", "frequency": "Twice daily", "benefits": "Barrier repair", "category": "Traditional"},
        {"name": "Evening Primrose Oil", "preparation": "Topical or supplement", "frequency": "Daily", "benefits": "GLA for skin health", "category": "Herbal"},
        {"name": "Shea Butter", "preparation": "Apply pure shea butter", "frequency": "As needed", "benefits": "Deep moisturizing", "category": "Traditional"},
        {"name": "Chamomile", "preparation": "Cooled tea compress or in cream", "frequency": "2-3 times daily", "benefits": "Anti-inflammatory", "category": "Herbal"},
        {"name": "Honey", "preparation": "Apply raw honey to affected areas", "frequency": "Leave 20 min, rinse", "benefits": "Healing, antimicrobial", "category": "Traditional"},
    ],
    
    "wound_healing": [
        {"name": "Honey (Manuka)", "preparation": "Apply to clean wound", "frequency": "Change dressing daily", "benefits": "Antibacterial, promotes healing", "category": "Traditional"},
        {"name": "Aloe Vera", "preparation": "Fresh gel on minor wounds", "frequency": "2-3 times daily", "benefits": "Promotes healing", "category": "Herbal"},
        {"name": "Turmeric Paste", "preparation": "Turmeric + water or coconut oil", "frequency": "Apply to wound", "benefits": "Antiseptic, healing", "category": "Ayurvedic"},
        {"name": "Neem Paste", "preparation": "Neem leaves paste", "frequency": "Apply to wound", "benefits": "Antibacterial", "category": "Ayurvedic"},
        {"name": "Calendula", "preparation": "Calendula cream or oil", "frequency": "2-3 times daily", "benefits": "Promotes healing", "category": "Herbal"},
        {"name": "Tea Tree Oil", "preparation": "Diluted, apply to wound", "frequency": "2-3 times daily", "benefits": "Antiseptic", "category": "Herbal"},
        {"name": "Vitamin E Oil", "preparation": "Apply to healing wound", "frequency": "Once daily", "benefits": "Reduces scarring", "category": "Supplement"},
    ],

    # ==========================================
    # MENTAL HEALTH & STRESS
    # ==========================================
    "anxiety_stress": [
        {"name": "Chamomile Tea", "preparation": "Steep 2-3 tsp dried flowers", "frequency": "2-3 times daily", "benefits": "Calming, reduces anxiety", "category": "Herbal"},
        {"name": "Lavender", "preparation": "Aromatherapy or tea", "frequency": "As needed", "benefits": "Relaxing", "category": "Aromatherapy"},
        {"name": "Ashwagandha", "preparation": "300-600mg supplement", "frequency": "Daily", "benefits": "Adaptogen, reduces cortisol", "category": "Ayurvedic"},
        {"name": "Brahmi", "preparation": "Supplement or fresh juice", "frequency": "Daily", "benefits": "Cognitive support, calming", "category": "Ayurvedic"},
        {"name": "Valerian Root", "preparation": "Tea or supplement", "frequency": "At bedtime", "benefits": "Calming, aids sleep", "category": "Herbal"},
        {"name": "Passionflower", "preparation": "Tea or supplement", "frequency": "1-2 times daily", "benefits": "Reduces anxiety", "category": "Herbal"},
        {"name": "Lemon Balm", "preparation": "Tea", "frequency": "2-3 times daily", "benefits": "Calming, improves mood", "category": "Herbal"},
        {"name": "Deep Breathing", "preparation": "4-7-8 technique", "frequency": "When anxious", "benefits": "Activates parasympathetic", "category": "Technique"},
        {"name": "Meditation", "preparation": "10-20 minutes", "frequency": "Daily", "benefits": "Reduces stress hormones", "category": "Practice"},
        {"name": "Magnesium", "preparation": "200-400mg supplement", "frequency": "Daily", "benefits": "Muscle relaxation, calming", "category": "Supplement"},
        {"name": "Jatamansi", "preparation": "Supplement or oil massage", "frequency": "Daily", "benefits": "Calming, promotes sleep", "category": "Ayurvedic"},
    ],
    
    "insomnia": [
        {"name": "Chamomile Tea", "preparation": "Strong brew before bed", "frequency": "30-60 min before sleep", "benefits": "Mild sedative", "category": "Herbal"},
        {"name": "Valerian Root", "preparation": "300-600mg or tea", "frequency": "30-60 min before bed", "benefits": "Improves sleep quality", "category": "Herbal"},
        {"name": "Lavender", "preparation": "Pillow spray or diffuser", "frequency": "At bedtime", "benefits": "Promotes relaxation", "category": "Aromatherapy"},
        {"name": "Warm Milk", "preparation": "Warm milk with nutmeg", "frequency": "Before bed", "benefits": "Tryptophan, tradition", "category": "Traditional"},
        {"name": "Ashwagandha", "preparation": "300mg with warm milk", "frequency": "At bedtime", "benefits": "Reduces cortisol", "category": "Ayurvedic"},
        {"name": "Melatonin", "preparation": "0.5-3mg supplement", "frequency": "30-60 min before bed", "benefits": "Regulates sleep cycle", "category": "Supplement"},
        {"name": "Tart Cherry Juice", "preparation": "8oz", "frequency": "Twice daily", "benefits": "Natural melatonin", "category": "Food"},
        {"name": "Magnesium", "preparation": "200-400mg glycinate", "frequency": "At bedtime", "benefits": "Muscle relaxation", "category": "Supplement"},
        {"name": "GABA", "preparation": "250-500mg supplement", "frequency": "At bedtime", "benefits": "Calming neurotransmitter", "category": "Supplement"},
        {"name": "Sleep Hygiene", "preparation": "Cool room, no screens, routine", "frequency": "Nightly", "benefits": "Natural sleep promotion", "category": "Practice"},
    ],
    
    "depression_low_mood": [
        {"name": "St. John's Wort", "preparation": "300mg 3x daily (standardized)", "frequency": "Daily for weeks", "benefits": "Mild-moderate depression", "category": "Herbal", "warning": "Drug interactions, photosensitivity"},
        {"name": "SAMe", "preparation": "400-1600mg daily", "frequency": "Daily", "benefits": "Mood support", "category": "Supplement"},
        {"name": "Omega-3 Fatty Acids", "preparation": "1-2g EPA+DHA", "frequency": "Daily", "benefits": "Brain health, mood", "category": "Supplement"},
        {"name": "Vitamin D", "preparation": "1000-4000 IU", "frequency": "Daily", "benefits": "Mood regulation", "category": "Supplement"},
        {"name": "Exercise", "preparation": "30 min moderate activity", "frequency": "Daily", "benefits": "Releases endorphins", "category": "Lifestyle"},
        {"name": "Saffron", "preparation": "30mg supplement", "frequency": "Daily", "benefits": "Mood enhancement", "category": "Herbal"},
        {"name": "Rhodiola", "preparation": "200-400mg", "frequency": "Daily", "benefits": "Adaptogen, energy", "category": "Herbal"},
        {"name": "Sunlight Exposure", "preparation": "15-30 min morning sun", "frequency": "Daily", "benefits": "Vitamin D, circadian rhythm", "category": "Lifestyle"},
        {"name": "Social Connection", "preparation": "Time with loved ones", "frequency": "Regularly", "benefits": "Emotional support", "category": "Lifestyle"},
    ],

    # ==========================================
    # IMMUNITY & PREVENTION
    # ==========================================
    "immunity_boost": [
        {"name": "Vitamin C", "preparation": "500-1000mg or citrus fruits", "frequency": "Daily", "benefits": "Immune support", "category": "Supplement"},
        {"name": "Vitamin D", "preparation": "1000-4000 IU", "frequency": "Daily", "benefits": "Immune modulation", "category": "Supplement"},
        {"name": "Zinc", "preparation": "15-30mg", "frequency": "Daily", "benefits": "Immune function", "category": "Supplement"},
        {"name": "Elderberry", "preparation": "Syrup or supplement", "frequency": "Daily during cold season", "benefits": "Antiviral", "category": "Herbal"},
        {"name": "Echinacea", "preparation": "Tea or supplement", "frequency": "At first sign of cold", "benefits": "Immune stimulant", "category": "Herbal"},
        {"name": "Astragalus", "preparation": "Supplement or tea", "frequency": "Daily for prevention", "benefits": "Immune tonic", "category": "Herbal"},
        {"name": "Chyawanprash", "preparation": "1-2 tsp", "frequency": "Daily", "benefits": "Ayurvedic immunity tonic", "category": "Ayurvedic"},
        {"name": "Giloy (Guduchi)", "preparation": "Juice or supplement", "frequency": "Daily", "benefits": "Immunomodulator", "category": "Ayurvedic"},
        {"name": "Amla (Indian Gooseberry)", "preparation": "Fresh, juice, or powder", "frequency": "Daily", "benefits": "High vitamin C, antioxidant", "category": "Ayurvedic"},
        {"name": "Probiotics", "preparation": "Supplement or fermented foods", "frequency": "Daily", "benefits": "Gut-immune connection", "category": "Supplement"},
        {"name": "Garlic", "preparation": "1-2 cloves raw or cooked", "frequency": "Daily", "benefits": "Antimicrobial, immune boost", "category": "Food"},
        {"name": "Turmeric", "preparation": "1 tsp daily with pepper", "frequency": "Daily", "benefits": "Anti-inflammatory, antioxidant", "category": "Ayurvedic"},
    ],

    # ==========================================
    # WOMEN'S HEALTH
    # ==========================================
    "menstrual_cramps": [
        {"name": "Heat Therapy", "preparation": "Hot water bottle on abdomen", "frequency": "As needed", "benefits": "Muscle relaxation", "category": "Physical"},
        {"name": "Ginger Tea", "preparation": "Fresh ginger tea", "frequency": "3-4 times daily", "benefits": "Anti-inflammatory, reduces cramps", "category": "Herbal"},
        {"name": "Raspberry Leaf Tea", "preparation": "Steep dried leaves", "frequency": "2-3 times daily", "benefits": "Uterine tonic", "category": "Herbal"},
        {"name": "Cramp Bark", "preparation": "Tea or tincture", "frequency": "As needed", "benefits": "Antispasmodic", "category": "Herbal"},
        {"name": "Evening Primrose Oil", "preparation": "500-1000mg", "frequency": "Daily", "benefits": "Hormonal balance", "category": "Supplement"},
        {"name": "Magnesium", "preparation": "200-400mg", "frequency": "Daily, especially before period", "benefits": "Muscle relaxation", "category": "Supplement"},
        {"name": "Omega-3", "preparation": "1-2g", "frequency": "Daily", "benefits": "Reduces inflammation", "category": "Supplement"},
        {"name": "Ajwain Water", "preparation": "Boil ajwain in water", "frequency": "During cramps", "benefits": "Antispasmodic", "category": "Ayurvedic"},
    ],
    
    "pms": [
        {"name": "Vitex (Chasteberry)", "preparation": "400-500mg", "frequency": "Daily", "benefits": "Hormonal balance", "category": "Herbal"},
        {"name": "Evening Primrose Oil", "preparation": "1000-2000mg", "frequency": "Daily", "benefits": "GLA for hormones", "category": "Supplement"},
        {"name": "Calcium", "preparation": "1000-1200mg", "frequency": "Daily", "benefits": "Reduces PMS symptoms", "category": "Supplement"},
        {"name": "Vitamin B6", "preparation": "50-100mg", "frequency": "Daily", "benefits": "Mood, water retention", "category": "Supplement"},
        {"name": "Magnesium", "preparation": "200-400mg", "frequency": "Daily", "benefits": "Mood, cramps", "category": "Supplement"},
        {"name": "Shatavari", "preparation": "Supplement", "frequency": "Daily", "benefits": "Women's tonic", "category": "Ayurvedic"},
        {"name": "Dong Quai", "preparation": "Supplement", "frequency": "Daily", "benefits": "Hormonal balance", "category": "Herbal"},
        {"name": "St. John's Wort", "preparation": "300mg 3x daily", "frequency": "Daily", "benefits": "Mood support", "category": "Herbal"},
    ],

    # ==========================================
    # ENERGY & FATIGUE
    # ==========================================
    "fatigue_energy": [
        {"name": "Ashwagandha", "preparation": "300-600mg", "frequency": "Daily", "benefits": "Adaptogen, energy", "category": "Ayurvedic"},
        {"name": "Rhodiola", "preparation": "200-400mg", "frequency": "Morning", "benefits": "Fatigue reduction", "category": "Herbal"},
        {"name": "Ginseng", "preparation": "200-400mg", "frequency": "Morning", "benefits": "Energy, mental clarity", "category": "Herbal"},
        {"name": "Maca", "preparation": "1.5-3g powder", "frequency": "Daily", "benefits": "Energy, hormonal balance", "category": "Herbal"},
        {"name": "B-Complex Vitamins", "preparation": "As directed", "frequency": "Daily with food", "benefits": "Energy metabolism", "category": "Supplement"},
        {"name": "Iron", "preparation": "If deficient, as directed", "frequency": "Daily", "benefits": "Oxygen transport", "category": "Supplement"},
        {"name": "CoQ10", "preparation": "100-200mg", "frequency": "Daily", "benefits": "Cellular energy", "category": "Supplement"},
        {"name": "Green Tea", "preparation": "1-2 cups", "frequency": "Morning/afternoon", "benefits": "Gentle caffeine, L-theanine", "category": "Herbal"},
        {"name": "Shilajit", "preparation": "Purified supplement", "frequency": "Daily", "benefits": "Mineral-rich, energy", "category": "Ayurvedic"},
    ],

    # ==========================================
    # HAIR & SCALP
    # ==========================================
    "hair_loss": [
        {"name": "Coconut Oil Massage", "preparation": "Warm coconut oil scalp massage", "frequency": "2-3 times weekly", "benefits": "Nourishes scalp", "category": "Traditional"},
        {"name": "Onion Juice", "preparation": "Apply fresh onion juice to scalp", "frequency": "2-3 times weekly", "benefits": "Stimulates growth", "category": "Traditional"},
        {"name": "Biotin", "preparation": "2500-5000mcg", "frequency": "Daily", "benefits": "Hair protein synthesis", "category": "Supplement"},
        {"name": "Iron", "preparation": "If deficient", "frequency": "Daily", "benefits": "Hair follicle health", "category": "Supplement"},
        {"name": "Bhringraj Oil", "preparation": "Oil massage", "frequency": "2-3 times weekly", "benefits": "Ayurvedic hair tonic", "category": "Ayurvedic"},
        {"name": "Amla Oil", "preparation": "Oil massage", "frequency": "2-3 times weekly", "benefits": "Strengthens hair", "category": "Ayurvedic"},
        {"name": "Rosemary Oil", "preparation": "Add to carrier oil, massage scalp", "frequency": "2-3 times weekly", "benefits": "Stimulates growth", "category": "Aromatherapy"},
        {"name": "Saw Palmetto", "preparation": "160-320mg", "frequency": "Daily", "benefits": "DHT blocker", "category": "Herbal"},
        {"name": "Pumpkin Seed Oil", "preparation": "Supplement", "frequency": "Daily", "benefits": "DHT blocker", "category": "Supplement"},
    ],
    
    "dandruff": [
        {"name": "Tea Tree Oil Shampoo", "preparation": "Add few drops to shampoo", "frequency": "2-3 times weekly", "benefits": "Antifungal", "category": "Herbal"},
        {"name": "Apple Cider Vinegar Rinse", "preparation": "1 part ACV : 1 part water, rinse", "frequency": "After shampoo", "benefits": "Balances pH", "category": "Traditional"},
        {"name": "Coconut Oil + Lemon", "preparation": "Warm coconut oil with lemon juice", "frequency": "30 min before wash", "benefits": "Antifungal, moisturizing", "category": "Traditional"},
        {"name": "Neem Oil", "preparation": "Add to carrier oil, apply to scalp", "frequency": "2-3 times weekly", "benefits": "Antifungal", "category": "Ayurvedic"},
        {"name": "Aloe Vera", "preparation": "Apply gel to scalp", "frequency": "Before wash", "benefits": "Soothing, antifungal", "category": "Herbal"},
        {"name": "Fenugreek Seeds", "preparation": "Soak overnight, make paste, apply", "frequency": "Weekly", "benefits": "Antifungal", "category": "Ayurvedic"},
        {"name": "Yogurt + Lemon", "preparation": "Apply to scalp", "frequency": "Weekly", "benefits": "Probiotics, pH balance", "category": "Traditional"},
    ],
}

# ========================================
# CONDITION TO REMEDY MAPPING
# ========================================

CONDITION_REMEDY_MAP = {
    # Map symptoms/conditions to relevant remedy categories
    "cold": ["cold_flu", "immunity_boost", "sore_throat", "cough"],
    "flu": ["cold_flu", "immunity_boost", "cough"],
    "cough": ["cough", "cold_flu", "sore_throat"],
    "fever": ["cold_flu", "immunity_boost"],
    "sore throat": ["sore_throat", "cold_flu", "cough"],
    "headache": ["headache"],
    "migraine": ["headache"],
    "stomach pain": ["indigestion_acidity", "nausea_vomiting"],
    "acidity": ["indigestion_acidity"],
    "gas": ["indigestion_acidity"],
    "bloating": ["indigestion_acidity"],
    "constipation": ["constipation"],
    "diarrhea": ["diarrhea"],
    "nausea": ["nausea_vomiting"],
    "vomiting": ["nausea_vomiting", "diarrhea"],
    "joint pain": ["joint_muscle_pain"],
    "muscle pain": ["joint_muscle_pain"],
    "back pain": ["back_pain", "joint_muscle_pain"],
    "body ache": ["joint_muscle_pain", "cold_flu"],
    "acne": ["acne"],
    "pimples": ["acne"],
    "dry skin": ["eczema_dry_skin"],
    "eczema": ["eczema_dry_skin"],
    "rash": ["eczema_dry_skin", "wound_healing"],
    "wound": ["wound_healing"],
    "cut": ["wound_healing"],
    "anxiety": ["anxiety_stress"],
    "stress": ["anxiety_stress"],
    "insomnia": ["insomnia"],
    "sleep": ["insomnia"],
    "depression": ["depression_low_mood", "anxiety_stress"],
    "low mood": ["depression_low_mood"],
    "fatigue": ["fatigue_energy", "immunity_boost"],
    "tired": ["fatigue_energy"],
    "weakness": ["fatigue_energy", "immunity_boost"],
    "period pain": ["menstrual_cramps"],
    "menstrual cramps": ["menstrual_cramps"],
    "pms": ["pms", "menstrual_cramps"],
    "hair loss": ["hair_loss"],
    "hair fall": ["hair_loss"],
    "dandruff": ["dandruff"],
    "immunity": ["immunity_boost"],
    "allergy": ["cold_flu"],  # Overlap with cold symptoms
}


def get_remedies_for_condition(condition: str, max_remedies: int = 5) -> list:
    """Get relevant natural remedies for a condition"""
    condition_lower = condition.lower()
    remedies = []
    
    # Find matching categories
    categories = []
    for key, cats in CONDITION_REMEDY_MAP.items():
        if key in condition_lower:
            categories.extend(cats)
    
    # Remove duplicates while preserving order
    categories = list(dict.fromkeys(categories))
    
    # Collect remedies from matching categories
    for category in categories:
        if category in NATURAL_REMEDIES:
            for remedy in NATURAL_REMEDIES[category]:
                if remedy not in remedies:
                    remedies.append(remedy)
                    if len(remedies) >= max_remedies:
                        return remedies
    
    return remedies
