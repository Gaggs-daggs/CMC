"""
WHO ATC/DDD Classification Service
Anatomical Therapeutic Chemical Classification System

- Drug classification (painkiller, antibiotic, etc.)
- Therapeutic grouping
- Anatomical target (heart, brain, etc.)

ATC Structure:
- Level 1: Anatomical main group (A = Alimentary tract)
- Level 2: Therapeutic main group (A02 = Drugs for acid disorders)
- Level 3: Therapeutic subgroup (A02B = Drugs for peptic ulcer)
- Level 4: Chemical subgroup (A02BC = Proton pump inhibitors)
- Level 5: Chemical substance (A02BC01 = Omeprazole)
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ATCClassification:
    """
    ATC Drug Classification
    Based on WHO ATC/DDD system
    
    Note: WHO doesn't provide a public API, so we use a comprehensive
    local database of common drugs and their classifications.
    """
    
    # ATC Level 1 - Anatomical Main Groups
    ANATOMICAL_GROUPS = {
        "A": {"name": "Alimentary tract and metabolism", "target": "Digestive system"},
        "B": {"name": "Blood and blood forming organs", "target": "Blood"},
        "C": {"name": "Cardiovascular system", "target": "Heart and blood vessels"},
        "D": {"name": "Dermatologicals", "target": "Skin"},
        "G": {"name": "Genito-urinary system and sex hormones", "target": "Reproductive system"},
        "H": {"name": "Systemic hormonal preparations", "target": "Endocrine system"},
        "J": {"name": "Antiinfectives for systemic use", "target": "Infections"},
        "L": {"name": "Antineoplastic and immunomodulating agents", "target": "Cancer/Immune"},
        "M": {"name": "Musculo-skeletal system", "target": "Muscles and bones"},
        "N": {"name": "Nervous system", "target": "Brain and nerves"},
        "P": {"name": "Antiparasitic products", "target": "Parasites"},
        "R": {"name": "Respiratory system", "target": "Lungs and airways"},
        "S": {"name": "Sensory organs", "target": "Eyes and ears"},
        "V": {"name": "Various", "target": "General"}
    }
    
    # Common drugs with their ATC codes and classifications
    DRUG_DATABASE: Dict[str, Dict[str, Any]] = {
        # Analgesics and Antipyretics (N02)
        "paracetamol": {
            "atc_code": "N02BE01",
            "classification": "Analgesic/Antipyretic",
            "category": "Pain reliever and fever reducer",
            "therapeutic_group": "Other analgesics and antipyretics",
            "anatomical_target": "Nervous system",
            "drug_class": "Non-opioid analgesic",
            "otc": True
        },
        "acetaminophen": {
            "atc_code": "N02BE01",
            "classification": "Analgesic/Antipyretic",
            "category": "Pain reliever and fever reducer",
            "therapeutic_group": "Other analgesics and antipyretics",
            "anatomical_target": "Nervous system",
            "drug_class": "Non-opioid analgesic",
            "otc": True
        },
        "ibuprofen": {
            "atc_code": "M01AE01",
            "classification": "NSAID",
            "category": "Anti-inflammatory pain reliever",
            "therapeutic_group": "Propionic acid derivatives",
            "anatomical_target": "Musculo-skeletal system",
            "drug_class": "Non-steroidal anti-inflammatory",
            "otc": True
        },
        "aspirin": {
            "atc_code": "N02BA01",
            "classification": "NSAID/Antiplatelet",
            "category": "Pain reliever, fever reducer, blood thinner",
            "therapeutic_group": "Salicylic acid and derivatives",
            "anatomical_target": "Nervous system",
            "drug_class": "Salicylate",
            "otc": True
        },
        "naproxen": {
            "atc_code": "M01AE02",
            "classification": "NSAID",
            "category": "Anti-inflammatory pain reliever",
            "therapeutic_group": "Propionic acid derivatives",
            "anatomical_target": "Musculo-skeletal system",
            "drug_class": "Non-steroidal anti-inflammatory",
            "otc": True
        },
        
        # Gastrointestinal (A02-A07)
        "omeprazole": {
            "atc_code": "A02BC01",
            "classification": "Proton pump inhibitor",
            "category": "Acid reducer for stomach",
            "therapeutic_group": "Drugs for peptic ulcer and GORD",
            "anatomical_target": "Alimentary tract",
            "drug_class": "PPI",
            "otc": True
        },
        "pantoprazole": {
            "atc_code": "A02BC02",
            "classification": "Proton pump inhibitor",
            "category": "Acid reducer for stomach",
            "therapeutic_group": "Drugs for peptic ulcer and GORD",
            "anatomical_target": "Alimentary tract",
            "drug_class": "PPI",
            "otc": False
        },
        "ranitidine": {
            "atc_code": "A02BA02",
            "classification": "H2 receptor antagonist",
            "category": "Acid reducer",
            "therapeutic_group": "Drugs for peptic ulcer and GORD",
            "anatomical_target": "Alimentary tract",
            "drug_class": "H2 blocker",
            "otc": True
        },
        "famotidine": {
            "atc_code": "A02BA03",
            "classification": "H2 receptor antagonist",
            "category": "Acid reducer",
            "therapeutic_group": "Drugs for peptic ulcer and GORD",
            "anatomical_target": "Alimentary tract",
            "drug_class": "H2 blocker",
            "otc": True
        },
        "loperamide": {
            "atc_code": "A07DA03",
            "classification": "Antidiarrheal",
            "category": "Diarrhea relief",
            "therapeutic_group": "Intestinal antiinflammatory agents",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Opioid-like antidiarrheal",
            "otc": True
        },
        "bismuth subsalicylate": {
            "atc_code": "A02BX05",
            "classification": "Antacid/Antidiarrheal",
            "category": "Stomach upset and diarrhea relief",
            "therapeutic_group": "Other drugs for peptic ulcer",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Bismuth compound",
            "otc": True
        },
        
        # Antihistamines (R06)
        "cetirizine": {
            "atc_code": "R06AE07",
            "classification": "Antihistamine",
            "category": "Allergy relief",
            "therapeutic_group": "Piperazine derivatives",
            "anatomical_target": "Respiratory system",
            "drug_class": "Second-generation antihistamine",
            "otc": True
        },
        "loratadine": {
            "atc_code": "R06AX13",
            "classification": "Antihistamine",
            "category": "Allergy relief",
            "therapeutic_group": "Other antihistamines",
            "anatomical_target": "Respiratory system",
            "drug_class": "Second-generation antihistamine",
            "otc": True
        },
        "diphenhydramine": {
            "atc_code": "R06AA02",
            "classification": "Antihistamine",
            "category": "Allergy and sleep aid",
            "therapeutic_group": "Aminoalkyl ethers",
            "anatomical_target": "Respiratory system",
            "drug_class": "First-generation antihistamine",
            "otc": True
        },
        "fexofenadine": {
            "atc_code": "R06AX26",
            "classification": "Antihistamine",
            "category": "Non-drowsy allergy relief",
            "therapeutic_group": "Other antihistamines",
            "anatomical_target": "Respiratory system",
            "drug_class": "Second-generation antihistamine",
            "otc": True
        },
        
        # Respiratory (R05)
        "dextromethorphan": {
            "atc_code": "R05DA09",
            "classification": "Antitussive",
            "category": "Cough suppressant",
            "therapeutic_group": "Opium alkaloids and derivatives",
            "anatomical_target": "Respiratory system",
            "drug_class": "Cough suppressant",
            "otc": True
        },
        "guaifenesin": {
            "atc_code": "R05CA03",
            "classification": "Expectorant",
            "category": "Mucus loosener",
            "therapeutic_group": "Expectorants",
            "anatomical_target": "Respiratory system",
            "drug_class": "Expectorant",
            "otc": True
        },
        
        # Anxiolytics and Hypnotics (N05)
        "diazepam": {
            "atc_code": "N05BA01",
            "classification": "Benzodiazepine",
            "category": "Anti-anxiety medication",
            "therapeutic_group": "Benzodiazepine derivatives",
            "anatomical_target": "Nervous system",
            "drug_class": "Anxiolytic",
            "otc": False
        },
        "alprazolam": {
            "atc_code": "N05BA12",
            "classification": "Benzodiazepine",
            "category": "Anti-anxiety medication",
            "therapeutic_group": "Benzodiazepine derivatives",
            "anatomical_target": "Nervous system",
            "drug_class": "Anxiolytic",
            "otc": False
        },
        "melatonin": {
            "atc_code": "N05CH01",
            "classification": "Sleep aid",
            "category": "Natural sleep hormone",
            "therapeutic_group": "Melatonin receptor agonists",
            "anatomical_target": "Nervous system",
            "drug_class": "Sleep hormone",
            "otc": True
        },
        
        # Antibiotics (J01)
        "amoxicillin": {
            "atc_code": "J01CA04",
            "classification": "Antibiotic",
            "category": "Penicillin-type antibiotic",
            "therapeutic_group": "Penicillins with extended spectrum",
            "anatomical_target": "Antiinfectives",
            "drug_class": "Beta-lactam antibiotic",
            "otc": False
        },
        "azithromycin": {
            "atc_code": "J01FA10",
            "classification": "Antibiotic",
            "category": "Macrolide antibiotic",
            "therapeutic_group": "Macrolides",
            "anatomical_target": "Antiinfectives",
            "drug_class": "Macrolide antibiotic",
            "otc": False
        },
        "ciprofloxacin": {
            "atc_code": "J01MA02",
            "classification": "Antibiotic",
            "category": "Fluoroquinolone antibiotic",
            "therapeutic_group": "Fluoroquinolones",
            "anatomical_target": "Antiinfectives",
            "drug_class": "Fluoroquinolone",
            "otc": False
        },
        
        # Cardiovascular (C)
        "atorvastatin": {
            "atc_code": "C10AA05",
            "classification": "Statin",
            "category": "Cholesterol-lowering medication",
            "therapeutic_group": "HMG CoA reductase inhibitors",
            "anatomical_target": "Cardiovascular system",
            "drug_class": "Statin",
            "otc": False
        },
        "lisinopril": {
            "atc_code": "C09AA03",
            "classification": "ACE inhibitor",
            "category": "Blood pressure medication",
            "therapeutic_group": "ACE inhibitors",
            "anatomical_target": "Cardiovascular system",
            "drug_class": "ACE inhibitor",
            "otc": False
        },
        "metoprolol": {
            "atc_code": "C07AB02",
            "classification": "Beta blocker",
            "category": "Heart rate and blood pressure medication",
            "therapeutic_group": "Beta blocking agents",
            "anatomical_target": "Cardiovascular system",
            "drug_class": "Beta-1 selective blocker",
            "otc": False
        },
        "amlodipine": {
            "atc_code": "C08CA01",
            "classification": "Calcium channel blocker",
            "category": "Blood pressure medication",
            "therapeutic_group": "Dihydropyridine derivatives",
            "anatomical_target": "Cardiovascular system",
            "drug_class": "Calcium channel blocker",
            "otc": False
        },
        
        # Diabetes (A10)
        "metformin": {
            "atc_code": "A10BA02",
            "classification": "Antidiabetic",
            "category": "Blood sugar control medication",
            "therapeutic_group": "Biguanides",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Biguanide",
            "otc": False
        },
        
        # Muscle Relaxants (M03)
        "cyclobenzaprine": {
            "atc_code": "M03BX08",
            "classification": "Muscle relaxant",
            "category": "Muscle spasm relief",
            "therapeutic_group": "Other centrally acting agents",
            "anatomical_target": "Musculo-skeletal system",
            "drug_class": "Centrally acting muscle relaxant",
            "otc": False
        },
        
        # Laxatives (A06)
        "bisacodyl": {
            "atc_code": "A06AB02",
            "classification": "Laxative",
            "category": "Constipation relief",
            "therapeutic_group": "Contact laxatives",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Stimulant laxative",
            "otc": True
        },
        "polyethylene glycol": {
            "atc_code": "A06AD65",
            "classification": "Laxative",
            "category": "Osmotic laxative for constipation",
            "therapeutic_group": "Osmotically acting laxatives",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Osmotic laxative",
            "otc": True
        },
        "docusate": {
            "atc_code": "A06AA02",
            "classification": "Laxative",
            "category": "Stool softener",
            "therapeutic_group": "Softeners",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Stool softener",
            "otc": True
        },
        
        # Antispasmodics (A03)
        "dicyclomine": {
            "atc_code": "A03AA07",
            "classification": "Antispasmodic",
            "category": "Stomach and intestinal spasm relief",
            "therapeutic_group": "Synthetic anticholinergics",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Anticholinergic",
            "otc": False
        },
        "hyoscine": {
            "atc_code": "A03BB01",
            "classification": "Antispasmodic",
            "category": "Stomach cramp relief",
            "therapeutic_group": "Belladonna alkaloids",
            "anatomical_target": "Alimentary tract",
            "drug_class": "Anticholinergic",
            "otc": True
        },
        
        # Antiemetics (A04)
        "ondansetron": {
            "atc_code": "A04AA01",
            "classification": "Antiemetic",
            "category": "Nausea and vomiting relief",
            "therapeutic_group": "Serotonin antagonists",
            "anatomical_target": "Alimentary tract",
            "drug_class": "5-HT3 antagonist",
            "otc": False
        },
        "dimenhydrinate": {
            "atc_code": "R06AA52",
            "classification": "Antiemetic/Antihistamine",
            "category": "Motion sickness relief",
            "therapeutic_group": "Aminoalkyl ethers",
            "anatomical_target": "Respiratory system",
            "drug_class": "First-generation antihistamine",
            "otc": True
        },
        "meclizine": {
            "atc_code": "R06AE05",
            "classification": "Antiemetic/Antihistamine",
            "category": "Motion sickness and vertigo relief",
            "therapeutic_group": "Piperazine derivatives",
            "anatomical_target": "Respiratory system",
            "drug_class": "First-generation antihistamine",
            "otc": True
        }
    }
    
    def __init__(self):
        # Create lowercase lookup for case-insensitive matching
        self._lowercase_lookup = {
            k.lower(): k for k in self.DRUG_DATABASE.keys()
        }
    
    def classify_drug(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Get ATC classification for a drug
        Returns classification info or None if not found
        """
        # Normalize drug name
        drug_key = drug_name.lower().strip()
        
        # Try direct lookup
        if drug_key in self._lowercase_lookup:
            original_key = self._lowercase_lookup[drug_key]
            drug_info = self.DRUG_DATABASE[original_key].copy()
            drug_info["drug_name"] = drug_name
            drug_info["source"] = "WHO ATC/DDD"
            return drug_info
        
        # Try partial match
        for key, original_key in self._lowercase_lookup.items():
            if drug_key in key or key in drug_key:
                drug_info = self.DRUG_DATABASE[original_key].copy()
                drug_info["drug_name"] = drug_name
                drug_info["source"] = "WHO ATC/DDD"
                return drug_info
        
        return None
    
    def get_anatomical_group(self, atc_code: str) -> Optional[Dict[str, str]]:
        """
        Get anatomical main group from ATC code
        First character of ATC code
        """
        if not atc_code:
            return None
        
        first_char = atc_code[0].upper()
        return self.ANATOMICAL_GROUPS.get(first_char)
    
    def get_drugs_by_category(self, category: str) -> List[str]:
        """
        Get list of drugs by category/classification
        e.g., "NSAID", "Antihistamine", "Antibiotic"
        """
        category_lower = category.lower()
        matching_drugs = []
        
        for drug_name, info in self.DRUG_DATABASE.items():
            if (category_lower in info.get("classification", "").lower() or
                category_lower in info.get("drug_class", "").lower() or
                category_lower in info.get("category", "").lower()):
                matching_drugs.append(drug_name)
        
        return matching_drugs
    
    def get_otc_drugs(self) -> List[str]:
        """Get list of OTC (over-the-counter) drugs"""
        return [
            name for name, info in self.DRUG_DATABASE.items()
            if info.get("otc", False)
        ]
    
    def get_prescription_drugs(self) -> List[str]:
        """Get list of prescription-only drugs"""
        return [
            name for name, info in self.DRUG_DATABASE.items()
            if not info.get("otc", True)
        ]
    
    def is_otc(self, drug_name: str) -> Optional[bool]:
        """Check if a drug is OTC (over-the-counter)"""
        classification = self.classify_drug(drug_name)
        if classification:
            return classification.get("otc", None)
        return None


# Singleton instance
atc_classification = ATCClassification()
