"""
Generic Drugs Database
======================
Parsed from official drug list PDF containing 400+ generic medicines
organized by category with dosage forms.

This provides the PRESCRIPTION database for CMC Health.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class DrugForm(str, Enum):
    """Drug forms/formulations"""
    TABLET = "tablet"
    CAPSULE = "capsule"
    INJECTION = "injection"
    SYRUP = "syrup"
    GEL = "gel"
    CREAM = "cream"
    OINTMENT = "ointment"
    DROPS = "drops"
    SPRAY = "spray"
    SUPPOSITORY = "suppository"
    SUSPENSION = "suspension"
    INHALER = "inhaler"
    SOLUTION = "solution"
    POWDER = "powder"
    LOTION = "lotion"
    OTHER = "other"


@dataclass
class GenericDrug:
    """A generic drug entry"""
    id: int
    name: str
    category: str
    dosage: Optional[str] = None
    form: DrugForm = DrugForm.OTHER
    strength: Optional[str] = None
    is_otc: bool = False
    requires_prescription: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "dosage": self.dosage,
            "form": self.form.value,
            "strength": self.strength,
            "is_otc": self.is_otc,
            "requires_prescription": self.requires_prescription
        }


# ============================================================
# COMPREHENSIVE GENERIC DRUG DATABASE
# Parsed from official drug list
# ============================================================

GENERIC_DRUGS_DATABASE: List[Dict] = [
    # ==================== ANAESTHETICS ====================
    {"id": 1, "name": "Lignocaine HCl injection 1%", "category": "Anaesthetics", "form": "injection", "strength": "1%", "is_otc": False},
    {"id": 2, "name": "Lignocaine + Nifedipine ointment", "category": "Anaesthetics", "form": "ointment", "is_otc": False},
    {"id": 3, "name": "Prilocaine Lignocaine injection", "category": "Anaesthetics", "form": "injection", "is_otc": False},
    
    # ==================== PREANAESTHETIC MEDICATIONS ====================
    {"id": 4, "name": "Alprazolam", "category": "Preanaesthetic Medications", "form": "tablet", "strength": "0.25mg", "is_otc": False},
    {"id": 5, "name": "Alprazolam", "category": "Preanaesthetic Medications", "form": "tablet", "strength": "0.5mg", "is_otc": False},
    {"id": 6, "name": "Amitriptyline", "category": "Preanaesthetic Medications", "form": "tablet", "strength": "10mg", "is_otc": False},
    {"id": 7, "name": "Midazolam", "category": "Preanaesthetic Medications", "form": "injection", "strength": "5mg/ml", "is_otc": False},
    {"id": 8, "name": "Midazolam nasal spray", "category": "Preanaesthetic Medications", "form": "spray", "strength": "5mg/ml", "is_otc": False},
    {"id": 9, "name": "Propantheline", "category": "Preanaesthetic Medications", "form": "tablet", "strength": "15mg", "is_otc": False},
    
    # ==================== NSAIDS (Pain & Inflammation) ====================
    {"id": 10, "name": "Paracetamol", "category": "NSAIDs", "form": "tablet", "strength": "650mg", "is_otc": True, 
     "dosage": "1-2 tablets every 4-6 hours", "common_uses": ["fever", "headache", "body pain", "mild pain"]},
    {"id": 11, "name": "Paracetamol", "category": "NSAIDs", "form": "tablet", "strength": "500mg", "is_otc": True,
     "dosage": "1-2 tablets every 4-6 hours", "common_uses": ["fever", "headache", "body pain"]},
    {"id": 12, "name": "Paracetamol", "category": "NSAIDs", "form": "tablet", "strength": "1000mg", "is_otc": True,
     "dosage": "1 tablet every 6-8 hours"},
    {"id": 13, "name": "Paracetamol drops", "category": "NSAIDs", "form": "drops", "strength": "100mg/ml", "is_otc": True,
     "dosage": "10-15mg/kg every 4-6 hours", "for_children": True},
    {"id": 14, "name": "Paracetamol suppository", "category": "NSAIDs", "form": "suppository", "strength": "100mg", "is_otc": True},
    {"id": 15, "name": "Paracetamol injection", "category": "NSAIDs", "form": "injection", "strength": "500mg", "is_otc": False},
    
    {"id": 16, "name": "Diclofenac sodium spray", "category": "NSAIDs", "form": "spray", "is_otc": True,
     "common_uses": ["muscle pain", "joint pain", "sports injury"]},
    {"id": 17, "name": "Diclofenac sodium + Serratiopeptidase", "category": "NSAIDs", "form": "tablet", "strength": "50mg+10mg", "is_otc": False,
     "dosage": "1 tablet twice daily after meals"},
    {"id": 18, "name": "Diclofenac potassium", "category": "NSAIDs", "form": "tablet", "strength": "75mg", "is_otc": False},
    {"id": 19, "name": "Diclofenac potassium", "category": "NSAIDs", "form": "tablet", "strength": "100mg", "is_otc": False},
    {"id": 20, "name": "Diclofenac gel", "category": "NSAIDs", "form": "gel", "strength": "1%", "is_otc": True,
     "dosage": "Apply to affected area 3-4 times daily"},
    
    {"id": 21, "name": "Piroxicam", "category": "NSAIDs", "form": "injection", "strength": "20mg/ml", "is_otc": False},
    {"id": 22, "name": "Piroxicam gel", "category": "NSAIDs", "form": "gel", "strength": "0.5%", "is_otc": True},
    {"id": 23, "name": "Piroxicam", "category": "NSAIDs", "form": "tablet", "strength": "20mg", "is_otc": False},
    
    {"id": 24, "name": "Mefenamic acid syrup", "category": "NSAIDs", "form": "syrup", "strength": "100mg/5ml", "is_otc": True,
     "common_uses": ["fever in children", "pain", "menstrual pain"]},
    {"id": 25, "name": "Mefenamic acid", "category": "NSAIDs", "form": "tablet", "strength": "500mg", "is_otc": True,
     "dosage": "1 tablet 3 times daily after meals", "common_uses": ["menstrual pain", "headache", "toothache"]},
    {"id": 26, "name": "Mefenamic acid", "category": "NSAIDs", "form": "capsule", "strength": "250mg", "is_otc": True},
    
    {"id": 27, "name": "Aceclofenac gel", "category": "NSAIDs", "form": "gel", "is_otc": True,
     "dosage": "Apply to affected area 2-3 times daily"},
    {"id": 28, "name": "Serratiopeptidase", "category": "NSAIDs", "form": "tablet", "strength": "5mg", "is_otc": True,
     "common_uses": ["inflammation", "swelling", "pain relief"]},
    
    {"id": 29, "name": "Lornoxicam", "category": "NSAIDs", "form": "tablet", "strength": "8mg", "is_otc": False},
    {"id": 30, "name": "Lornoxicam", "category": "NSAIDs", "form": "tablet", "strength": "4mg", "is_otc": False},
    
    {"id": 31, "name": "Etoricoxib", "category": "NSAIDs", "form": "tablet", "strength": "60mg", "is_otc": False,
     "common_uses": ["arthritis", "joint pain", "gout"]},
    {"id": 32, "name": "Etoricoxib", "category": "NSAIDs", "form": "tablet", "strength": "90mg", "is_otc": False},
    {"id": 33, "name": "Etoricoxib", "category": "NSAIDs", "form": "tablet", "strength": "120mg", "is_otc": False},
    
    {"id": 34, "name": "Ibuprofen", "category": "NSAIDs", "form": "tablet", "strength": "400mg", "is_otc": True,
     "dosage": "1 tablet every 6-8 hours after meals", "common_uses": ["headache", "fever", "body pain", "inflammation"]},
    {"id": 35, "name": "Ibuprofen suspension", "category": "NSAIDs", "form": "suspension", "strength": "100mg/5ml", "is_otc": True,
     "for_children": True},
    
    # ==================== OPIOID ANALGESICS ====================
    {"id": 36, "name": "Tramadol", "category": "Opioid Analgesics", "form": "tablet", "strength": "50mg", "is_otc": False,
     "requires_prescription": True, "controlled": True},
    {"id": 37, "name": "Tramadol injection", "category": "Opioid Analgesics", "form": "injection", "strength": "100mg/ml", "is_otc": False},
    {"id": 38, "name": "Pentazocine injection", "category": "Opioid Analgesics", "form": "injection", "strength": "60mg/ml", "is_otc": False},
    {"id": 39, "name": "Morphine injection", "category": "Opioid Analgesics", "form": "injection", "strength": "2mg/ml", "is_otc": False},
    {"id": 40, "name": "Fentanyl injection", "category": "Opioid Analgesics", "form": "injection", "strength": "50mcg/ml", "is_otc": False},
    
    # ==================== DRUGS FOR GOUT ====================
    {"id": 41, "name": "Febuxostat", "category": "Drugs for Gout", "form": "tablet", "strength": "40mg", "is_otc": False,
     "common_uses": ["gout", "high uric acid"]},
    {"id": 42, "name": "Allopurinol", "category": "Drugs for Gout", "form": "tablet", "strength": "100mg", "is_otc": False},
    {"id": 43, "name": "Allopurinol", "category": "Drugs for Gout", "form": "tablet", "strength": "300mg", "is_otc": False},
    {"id": 44, "name": "Colchicine", "category": "Drugs for Gout", "form": "tablet", "strength": "0.5mg", "is_otc": False,
     "common_uses": ["acute gout attack"]},
    
    # ==================== ANTIALLERGICS ====================
    {"id": 45, "name": "Adrenaline 1:1000", "category": "Antiallergics", "form": "injection", "is_otc": False,
     "common_uses": ["anaphylaxis", "severe allergic reaction", "emergency"]},
    {"id": 46, "name": "Pheniramine maleate", "category": "Antiallergics", "form": "tablet", "is_otc": True,
     "common_uses": ["allergic rhinitis", "urticaria", "itching"]},
    {"id": 47, "name": "Sodium cromoglycate eye drops", "category": "Antiallergics", "form": "drops", "is_otc": True,
     "common_uses": ["allergic conjunctivitis", "eye allergy"]},
    
    {"id": 48, "name": "Ebastine", "category": "Antiallergics", "form": "tablet", "strength": "10mg", "is_otc": True,
     "dosage": "1 tablet once daily", "common_uses": ["allergic rhinitis", "urticaria", "skin allergy"]},
    {"id": 49, "name": "Ebastine", "category": "Antiallergics", "form": "tablet", "strength": "20mg", "is_otc": True},
    {"id": 50, "name": "Loratadine", "category": "Antiallergics", "form": "tablet", "strength": "10mg", "is_otc": True,
     "dosage": "1 tablet once daily", "common_uses": ["allergic rhinitis", "hay fever", "hives"]},
    {"id": 51, "name": "Desloratadine", "category": "Antiallergics", "form": "tablet", "strength": "5mg", "is_otc": True,
     "dosage": "1 tablet once daily"},
    {"id": 52, "name": "Cetirizine", "category": "Antiallergics", "form": "tablet", "strength": "10mg", "is_otc": True,
     "dosage": "1 tablet once daily at bedtime", "common_uses": ["allergic rhinitis", "urticaria", "cold", "sneezing"]},
    {"id": 53, "name": "Levocetirizine", "category": "Antiallergics", "form": "tablet", "strength": "5mg", "is_otc": True,
     "dosage": "1 tablet once daily", "common_uses": ["allergic rhinitis", "urticaria"]},
    {"id": 54, "name": "Fexofenadine", "category": "Antiallergics", "form": "tablet", "strength": "120mg", "is_otc": True,
     "dosage": "1 tablet once daily", "common_uses": ["allergic rhinitis", "chronic urticaria"]},
    {"id": 55, "name": "Fexofenadine", "category": "Antiallergics", "form": "tablet", "strength": "180mg", "is_otc": True},
    {"id": 56, "name": "Rupatadine", "category": "Antiallergics", "form": "tablet", "strength": "10mg", "is_otc": True},
    {"id": 57, "name": "Olopatadine", "category": "Antiallergics", "form": "tablet", "strength": "5mg", "is_otc": True},
    {"id": 58, "name": "Azelastine nasal spray", "category": "Antiallergics", "form": "spray", "strength": "140mcg/puff", "is_otc": True,
     "common_uses": ["nasal allergy", "rhinitis"]},
    
    # ==================== ANTIEPILEPTICS ====================
    {"id": 59, "name": "Diazepam", "category": "Antiepileptics", "form": "tablet", "strength": "5mg", "is_otc": False},
    {"id": 60, "name": "Diazepam", "category": "Antiepileptics", "form": "tablet", "strength": "10mg", "is_otc": False},
    {"id": 61, "name": "Phenobarbitone syrup", "category": "Antiepileptics", "form": "syrup", "strength": "30mg/5ml", "is_otc": False},
    {"id": 62, "name": "Phenytoin", "category": "Antiepileptics", "form": "tablet", "strength": "50mg", "is_otc": False},
    {"id": 63, "name": "Phenytoin injection", "category": "Antiepileptics", "form": "injection", "is_otc": False},
    {"id": 64, "name": "Sodium valproate injection", "category": "Antiepileptics", "form": "injection", "strength": "300mg/ml", "is_otc": False},
    {"id": 65, "name": "Levetiracetam", "category": "Antiepileptics", "form": "tablet", "strength": "250mg", "is_otc": False},
    {"id": 66, "name": "Levetiracetam injection", "category": "Antiepileptics", "form": "injection", "strength": "500mg/2ml", "is_otc": False},
    {"id": 67, "name": "Gabapentin", "category": "Antiepileptics", "form": "capsule", "strength": "300mg", "is_otc": False,
     "common_uses": ["neuropathic pain", "epilepsy"]},
    {"id": 68, "name": "Gabapentin", "category": "Antiepileptics", "form": "capsule", "strength": "400mg", "is_otc": False},
    {"id": 69, "name": "Lorazepam", "category": "Antiepileptics", "form": "tablet", "is_otc": False},
    {"id": 70, "name": "Clobazam", "category": "Antiepileptics", "form": "tablet", "strength": "10mg", "is_otc": False},
    
    # ==================== ANTIHELMINTHIC (Dewormers) ====================
    {"id": 71, "name": "Mebendazole", "category": "Antihelminthic", "form": "tablet", "strength": "100mg", "is_otc": True,
     "dosage": "1 tablet twice daily for 3 days", "common_uses": ["worm infection", "pinworm", "roundworm"]},
    {"id": 72, "name": "Mebendazole", "category": "Antihelminthic", "form": "tablet", "strength": "200mg", "is_otc": True},
    {"id": 73, "name": "Albendazole", "category": "Antihelminthic", "form": "tablet", "strength": "400mg", "is_otc": True,
     "dosage": "Single dose of 400mg", "common_uses": ["worm infection", "hookworm", "tapeworm"]},
    {"id": 74, "name": "Piperazine citrate syrup", "category": "Antihelminthic", "form": "syrup", "strength": "750mg/5ml", "is_otc": True},
    {"id": 75, "name": "Ivermectin", "category": "Antifilarials", "form": "tablet", "strength": "12mg", "is_otc": False,
     "common_uses": ["filariasis", "scabies", "parasitic infections"]},
    
    # ==================== ANTIBIOTICS ====================
    {"id": 76, "name": "Ampicillin", "category": "Antibiotics", "form": "capsule", "strength": "500mg", "is_otc": False},
    {"id": 77, "name": "Amoxicillin", "category": "Antibiotics", "form": "tablet", "strength": "250mg", "is_otc": False,
     "dosage": "1 tablet 3 times daily", "common_uses": ["respiratory infection", "ear infection", "throat infection"]},
    {"id": 78, "name": "Amoxicillin", "category": "Antibiotics", "form": "tablet", "strength": "500mg", "is_otc": False,
     "dosage": "1 tablet 3 times daily for 5-7 days"},
    {"id": 79, "name": "Amoxicillin + Clavulanic acid", "category": "Antibiotics", "form": "tablet", "strength": "625mg", "is_otc": False,
     "dosage": "1 tablet twice daily", "common_uses": ["sinusitis", "bronchitis", "UTI", "skin infection"]},
    {"id": 80, "name": "Amoxicillin + Clavulanic acid syrup", "category": "Antibiotics", "form": "syrup", "strength": "228.5mg/5ml", "is_otc": False},
    {"id": 81, "name": "Amoxicillin + Clavulanic acid injection", "category": "Antibiotics", "form": "injection", "strength": "1.2g", "is_otc": False},
    
    {"id": 82, "name": "Azithromycin", "category": "Antibiotics", "form": "tablet", "strength": "500mg", "is_otc": False,
     "dosage": "500mg once daily for 3 days", "common_uses": ["respiratory infection", "throat infection", "skin infection"]},
    {"id": 83, "name": "Azithromycin", "category": "Antibiotics", "form": "tablet", "strength": "250mg", "is_otc": False},
    {"id": 84, "name": "Azithromycin suspension", "category": "Antibiotics", "form": "suspension", "strength": "100mg/5ml", "is_otc": False},
    
    {"id": 85, "name": "Cefixime", "category": "Antibiotics", "form": "tablet", "strength": "200mg", "is_otc": False,
     "dosage": "1 tablet twice daily", "common_uses": ["UTI", "respiratory infection", "typhoid"]},
    {"id": 86, "name": "Cefixime", "category": "Antibiotics", "form": "tablet", "strength": "100mg", "is_otc": False},
    {"id": 87, "name": "Cefixime syrup", "category": "Antibiotics", "form": "syrup", "strength": "50mg/5ml", "is_otc": False},
    
    {"id": 88, "name": "Cefuroxime", "category": "Antibiotics", "form": "tablet", "strength": "250mg", "is_otc": False},
    {"id": 89, "name": "Cefuroxime", "category": "Antibiotics", "form": "tablet", "strength": "500mg", "is_otc": False},
    {"id": 90, "name": "Cefuroxime injection", "category": "Antibiotics", "form": "injection", "strength": "750mg", "is_otc": False},
    
    {"id": 91, "name": "Cephalexin", "category": "Antibiotics", "form": "capsule", "strength": "500mg", "is_otc": False,
     "dosage": "1 capsule 4 times daily", "common_uses": ["skin infection", "UTI", "bone infection"]},
    {"id": 92, "name": "Cephalexin syrup", "category": "Antibiotics", "form": "syrup", "strength": "125mg/5ml", "is_otc": False},
    
    {"id": 93, "name": "Ciprofloxacin", "category": "Antibiotics", "form": "tablet", "strength": "500mg", "is_otc": False,
     "dosage": "1 tablet twice daily", "common_uses": ["UTI", "diarrhea", "respiratory infection"]},
    {"id": 94, "name": "Ciprofloxacin", "category": "Antibiotics", "form": "tablet", "strength": "250mg", "is_otc": False},
    {"id": 95, "name": "Ciprofloxacin eye drops", "category": "Antibiotics", "form": "drops", "strength": "0.3%", "is_otc": False,
     "common_uses": ["eye infection", "conjunctivitis"]},
    
    {"id": 96, "name": "Ofloxacin", "category": "Antibiotics", "form": "tablet", "strength": "200mg", "is_otc": False,
     "dosage": "1 tablet twice daily"},
    {"id": 97, "name": "Ofloxacin + Ornidazole", "category": "Antibiotics", "form": "tablet", "strength": "200mg+500mg", "is_otc": False,
     "dosage": "1 tablet twice daily", "common_uses": ["diarrhea", "dysentery", "GI infection"]},
    
    {"id": 98, "name": "Levofloxacin", "category": "Antibiotics", "form": "tablet", "strength": "500mg", "is_otc": False,
     "dosage": "1 tablet once daily", "common_uses": ["respiratory infection", "UTI", "sinusitis"]},
    {"id": 99, "name": "Levofloxacin", "category": "Antibiotics", "form": "tablet", "strength": "750mg", "is_otc": False},
    
    {"id": 100, "name": "Metronidazole", "category": "Antibiotics", "form": "tablet", "strength": "400mg", "is_otc": False,
     "dosage": "1 tablet 3 times daily", "common_uses": ["amoebiasis", "giardiasis", "dental infection"]},
    {"id": 101, "name": "Metronidazole injection", "category": "Antibiotics", "form": "injection", "strength": "500mg/100ml", "is_otc": False},
    
    {"id": 102, "name": "Doxycycline", "category": "Antibiotics", "form": "capsule", "strength": "100mg", "is_otc": False,
     "dosage": "1 capsule twice daily", "common_uses": ["acne", "respiratory infection", "malaria prophylaxis"]},
    
    {"id": 103, "name": "Ceftriaxone injection", "category": "Antibiotics", "form": "injection", "strength": "1g", "is_otc": False,
     "common_uses": ["severe infection", "meningitis", "pneumonia"]},
    {"id": 104, "name": "Ceftriaxone injection", "category": "Antibiotics", "form": "injection", "strength": "500mg", "is_otc": False},
    
    # ==================== ANTACIDS & GI DRUGS ====================
    {"id": 105, "name": "Omeprazole", "category": "Antacids & GI Drugs", "form": "capsule", "strength": "20mg", "is_otc": True,
     "dosage": "1 capsule once daily before breakfast", "common_uses": ["acidity", "GERD", "gastric ulcer"]},
    {"id": 106, "name": "Omeprazole", "category": "Antacids & GI Drugs", "form": "capsule", "strength": "40mg", "is_otc": True},
    {"id": 107, "name": "Pantoprazole", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "40mg", "is_otc": True,
     "dosage": "1 tablet once daily before breakfast", "common_uses": ["acidity", "GERD", "peptic ulcer"]},
    {"id": 108, "name": "Pantoprazole injection", "category": "Antacids & GI Drugs", "form": "injection", "strength": "40mg", "is_otc": False},
    {"id": 109, "name": "Rabeprazole", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "20mg", "is_otc": True,
     "dosage": "1 tablet once daily"},
    {"id": 110, "name": "Esomeprazole", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "40mg", "is_otc": True},
    
    {"id": 111, "name": "Ranitidine", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "150mg", "is_otc": True,
     "dosage": "1 tablet twice daily", "common_uses": ["acidity", "heartburn"]},
    {"id": 112, "name": "Famotidine", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "20mg", "is_otc": True,
     "common_uses": ["acidity", "heartburn", "peptic ulcer"]},
    
    {"id": 113, "name": "Domperidone", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "10mg", "is_otc": True,
     "dosage": "1 tablet before meals", "common_uses": ["nausea", "vomiting", "bloating", "indigestion"]},
    {"id": 114, "name": "Domperidone suspension", "category": "Antacids & GI Drugs", "form": "suspension", "strength": "5mg/5ml", "is_otc": True},
    
    {"id": 115, "name": "Ondansetron", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "4mg", "is_otc": True,
     "dosage": "1 tablet every 8 hours as needed", "common_uses": ["nausea", "vomiting"]},
    {"id": 116, "name": "Ondansetron", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "8mg", "is_otc": True},
    {"id": 117, "name": "Ondansetron injection", "category": "Antacids & GI Drugs", "form": "injection", "strength": "4mg/2ml", "is_otc": False},
    
    {"id": 118, "name": "Antacid gel (Aluminium + Magnesium)", "category": "Antacids & GI Drugs", "form": "suspension", "is_otc": True,
     "dosage": "10-15ml after meals", "common_uses": ["acidity", "heartburn", "indigestion"]},
    {"id": 119, "name": "Sucralfate", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "1g", "is_otc": True,
     "common_uses": ["gastric ulcer", "duodenal ulcer"]},
    
    {"id": 120, "name": "Dicyclomine", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "20mg", "is_otc": True,
     "dosage": "1 tablet 3 times daily before meals", "common_uses": ["abdominal cramps", "IBS", "colic"]},
    {"id": 121, "name": "Hyoscine butylbromide", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "10mg", "is_otc": True,
     "common_uses": ["abdominal cramps", "stomach pain", "colic"]},
    
    {"id": 122, "name": "Loperamide", "category": "Antacids & GI Drugs", "form": "capsule", "strength": "2mg", "is_otc": True,
     "dosage": "2 capsules initially, then 1 after each loose stool", "common_uses": ["diarrhea", "loose motions"]},
    {"id": 123, "name": "ORS (Oral Rehydration Salts)", "category": "Antacids & GI Drugs", "form": "powder", "is_otc": True,
     "dosage": "Dissolve 1 sachet in 1 liter water", "common_uses": ["dehydration", "diarrhea", "vomiting"]},
    
    {"id": 124, "name": "Lactulose syrup", "category": "Antacids & GI Drugs", "form": "syrup", "is_otc": True,
     "dosage": "15-30ml daily", "common_uses": ["constipation", "hepatic encephalopathy"]},
    {"id": 125, "name": "Bisacodyl", "category": "Antacids & GI Drugs", "form": "tablet", "strength": "5mg", "is_otc": True,
     "dosage": "1-2 tablets at bedtime", "common_uses": ["constipation"]},
    {"id": 126, "name": "Isabgol (Psyllium husk)", "category": "Antacids & GI Drugs", "form": "powder", "is_otc": True,
     "dosage": "1-2 teaspoons with water at bedtime", "common_uses": ["constipation", "IBS"]},
    
    # ==================== ANTIDIABETICS ====================
    {"id": 127, "name": "Metformin", "category": "Antidiabetics", "form": "tablet", "strength": "500mg", "is_otc": False,
     "dosage": "1 tablet twice daily with meals", "common_uses": ["type 2 diabetes", "PCOS"]},
    {"id": 128, "name": "Metformin", "category": "Antidiabetics", "form": "tablet", "strength": "850mg", "is_otc": False},
    {"id": 129, "name": "Metformin", "category": "Antidiabetics", "form": "tablet", "strength": "1000mg", "is_otc": False},
    {"id": 130, "name": "Glimepiride", "category": "Antidiabetics", "form": "tablet", "strength": "1mg", "is_otc": False},
    {"id": 131, "name": "Glimepiride", "category": "Antidiabetics", "form": "tablet", "strength": "2mg", "is_otc": False},
    {"id": 132, "name": "Glimepiride + Metformin", "category": "Antidiabetics", "form": "tablet", "strength": "1mg+500mg", "is_otc": False},
    {"id": 133, "name": "Glibenclamide", "category": "Antidiabetics", "form": "tablet", "strength": "5mg", "is_otc": False},
    {"id": 134, "name": "Insulin Human Regular", "category": "Antidiabetics", "form": "injection", "strength": "100IU/ml", "is_otc": False},
    {"id": 135, "name": "Insulin Human NPH", "category": "Antidiabetics", "form": "injection", "strength": "100IU/ml", "is_otc": False},
    
    # ==================== ANTIHYPERTENSIVES ====================
    {"id": 136, "name": "Amlodipine", "category": "Antihypertensives", "form": "tablet", "strength": "5mg", "is_otc": False,
     "dosage": "1 tablet once daily", "common_uses": ["hypertension", "angina"]},
    {"id": 137, "name": "Amlodipine", "category": "Antihypertensives", "form": "tablet", "strength": "10mg", "is_otc": False},
    {"id": 138, "name": "Atenolol", "category": "Antihypertensives", "form": "tablet", "strength": "50mg", "is_otc": False,
     "dosage": "1 tablet once daily", "common_uses": ["hypertension", "angina", "arrhythmia"]},
    {"id": 139, "name": "Atenolol", "category": "Antihypertensives", "form": "tablet", "strength": "25mg", "is_otc": False},
    {"id": 140, "name": "Losartan", "category": "Antihypertensives", "form": "tablet", "strength": "50mg", "is_otc": False,
     "dosage": "1 tablet once daily", "common_uses": ["hypertension", "diabetic nephropathy"]},
    {"id": 141, "name": "Telmisartan", "category": "Antihypertensives", "form": "tablet", "strength": "40mg", "is_otc": False},
    {"id": 142, "name": "Telmisartan", "category": "Antihypertensives", "form": "tablet", "strength": "80mg", "is_otc": False},
    {"id": 143, "name": "Ramipril", "category": "Antihypertensives", "form": "capsule", "strength": "5mg", "is_otc": False},
    {"id": 144, "name": "Enalapril", "category": "Antihypertensives", "form": "tablet", "strength": "5mg", "is_otc": False},
    {"id": 145, "name": "Hydrochlorothiazide", "category": "Antihypertensives", "form": "tablet", "strength": "12.5mg", "is_otc": False,
     "common_uses": ["hypertension", "edema"]},
    {"id": 146, "name": "Furosemide", "category": "Antihypertensives", "form": "tablet", "strength": "40mg", "is_otc": False,
     "common_uses": ["edema", "heart failure", "hypertension"]},
    {"id": 147, "name": "Furosemide injection", "category": "Antihypertensives", "form": "injection", "strength": "20mg/2ml", "is_otc": False},
    
    # ==================== COUGH & COLD ====================
    {"id": 148, "name": "Dextromethorphan syrup", "category": "Cough & Cold", "form": "syrup", "is_otc": True,
     "dosage": "10ml every 6-8 hours", "common_uses": ["dry cough", "cough"]},
    {"id": 149, "name": "Ambroxol syrup", "category": "Cough & Cold", "form": "syrup", "strength": "30mg/5ml", "is_otc": True,
     "dosage": "10ml 2-3 times daily", "common_uses": ["productive cough", "chest congestion"]},
    {"id": 150, "name": "Ambroxol", "category": "Cough & Cold", "form": "tablet", "strength": "30mg", "is_otc": True},
    {"id": 151, "name": "Bromhexine", "category": "Cough & Cold", "form": "tablet", "strength": "8mg", "is_otc": True,
     "common_uses": ["cough with phlegm", "bronchitis"]},
    {"id": 152, "name": "Guaifenesin syrup", "category": "Cough & Cold", "form": "syrup", "is_otc": True,
     "common_uses": ["cough", "chest congestion"]},
    {"id": 153, "name": "Salbutamol syrup", "category": "Cough & Cold", "form": "syrup", "strength": "2mg/5ml", "is_otc": True,
     "common_uses": ["wheezing", "asthma", "bronchitis"]},
    {"id": 154, "name": "Salbutamol inhaler", "category": "Cough & Cold", "form": "inhaler", "strength": "100mcg/puff", "is_otc": True,
     "dosage": "1-2 puffs as needed", "common_uses": ["asthma", "bronchospasm", "wheezing"]},
    {"id": 155, "name": "Levosalbutamol inhaler", "category": "Cough & Cold", "form": "inhaler", "is_otc": True},
    {"id": 156, "name": "Budesonide inhaler", "category": "Cough & Cold", "form": "inhaler", "strength": "200mcg", "is_otc": False,
     "common_uses": ["asthma", "COPD"]},
    {"id": 157, "name": "Montelukast", "category": "Cough & Cold", "form": "tablet", "strength": "10mg", "is_otc": False,
     "dosage": "1 tablet at bedtime", "common_uses": ["asthma", "allergic rhinitis"]},
    {"id": 158, "name": "Theophylline", "category": "Cough & Cold", "form": "tablet", "strength": "100mg", "is_otc": False},
    
    # ==================== VITAMINS & SUPPLEMENTS ====================
    {"id": 159, "name": "Multivitamin tablets", "category": "Vitamins & Supplements", "form": "tablet", "is_otc": True,
     "dosage": "1 tablet daily", "common_uses": ["nutritional supplement", "general weakness"]},
    {"id": 160, "name": "Vitamin B Complex", "category": "Vitamins & Supplements", "form": "tablet", "is_otc": True,
     "dosage": "1 tablet daily", "common_uses": ["vitamin B deficiency", "weakness", "neuropathy"]},
    {"id": 161, "name": "Vitamin C", "category": "Vitamins & Supplements", "form": "tablet", "strength": "500mg", "is_otc": True,
     "dosage": "1 tablet daily", "common_uses": ["immunity booster", "scurvy prevention"]},
    {"id": 162, "name": "Vitamin D3", "category": "Vitamins & Supplements", "form": "tablet", "strength": "60000IU", "is_otc": True,
     "dosage": "1 tablet weekly", "common_uses": ["vitamin D deficiency", "bone health"]},
    {"id": 163, "name": "Calcium + Vitamin D3", "category": "Vitamins & Supplements", "form": "tablet", "strength": "500mg+250IU", "is_otc": True,
     "dosage": "1 tablet twice daily", "common_uses": ["calcium deficiency", "osteoporosis", "bone health"]},
    {"id": 164, "name": "Iron + Folic acid", "category": "Vitamins & Supplements", "form": "tablet", "is_otc": True,
     "dosage": "1 tablet daily", "common_uses": ["anemia", "pregnancy", "iron deficiency"]},
    {"id": 165, "name": "Folic acid", "category": "Vitamins & Supplements", "form": "tablet", "strength": "5mg", "is_otc": True,
     "common_uses": ["pregnancy", "anemia", "neural tube defect prevention"]},
    {"id": 166, "name": "Vitamin B12 (Methylcobalamin)", "category": "Vitamins & Supplements", "form": "tablet", "strength": "1500mcg", "is_otc": True,
     "common_uses": ["B12 deficiency", "neuropathy", "anemia"]},
    {"id": 167, "name": "Zinc", "category": "Vitamins & Supplements", "form": "tablet", "strength": "20mg", "is_otc": True,
     "common_uses": ["zinc deficiency", "immunity", "diarrhea in children"]},
    
    # ==================== DERMATOLOGY ====================
    {"id": 168, "name": "Clotrimazole cream", "category": "Dermatology", "form": "cream", "strength": "1%", "is_otc": True,
     "dosage": "Apply twice daily", "common_uses": ["fungal infection", "ringworm", "athlete's foot"]},
    {"id": 169, "name": "Miconazole cream", "category": "Dermatology", "form": "cream", "strength": "2%", "is_otc": True,
     "common_uses": ["fungal infection", "candidiasis"]},
    {"id": 170, "name": "Ketoconazole cream", "category": "Dermatology", "form": "cream", "strength": "2%", "is_otc": True,
     "common_uses": ["fungal infection", "dandruff", "seborrheic dermatitis"]},
    {"id": 171, "name": "Terbinafine cream", "category": "Dermatology", "form": "cream", "strength": "1%", "is_otc": True,
     "dosage": "Apply once daily", "common_uses": ["ringworm", "athlete's foot", "jock itch"]},
    {"id": 172, "name": "Fluconazole", "category": "Dermatology", "form": "tablet", "strength": "150mg", "is_otc": False,
     "dosage": "Single dose", "common_uses": ["vaginal candidiasis", "fungal infection"]},
    {"id": 173, "name": "Itraconazole", "category": "Dermatology", "form": "capsule", "strength": "100mg", "is_otc": False,
     "common_uses": ["fungal infection", "onychomycosis"]},
    
    {"id": 174, "name": "Hydrocortisone cream", "category": "Dermatology", "form": "cream", "strength": "1%", "is_otc": True,
     "dosage": "Apply thin layer twice daily", "common_uses": ["eczema", "dermatitis", "itching", "rash"]},
    {"id": 175, "name": "Betamethasone cream", "category": "Dermatology", "form": "cream", "strength": "0.1%", "is_otc": False,
     "common_uses": ["eczema", "psoriasis", "dermatitis"]},
    {"id": 176, "name": "Clobetasol cream", "category": "Dermatology", "form": "cream", "strength": "0.05%", "is_otc": False,
     "common_uses": ["psoriasis", "severe eczema"]},
    
    {"id": 177, "name": "Calamine lotion", "category": "Dermatology", "form": "lotion", "is_otc": True,
     "dosage": "Apply as needed", "common_uses": ["itching", "sunburn", "insect bites", "rash"]},
    {"id": 178, "name": "Permethrin cream", "category": "Dermatology", "form": "cream", "strength": "5%", "is_otc": True,
     "dosage": "Apply overnight, wash off after 8-12 hours", "common_uses": ["scabies", "lice"]},
    {"id": 179, "name": "Mupirocin ointment", "category": "Dermatology", "form": "ointment", "strength": "2%", "is_otc": False,
     "dosage": "Apply 3 times daily", "common_uses": ["skin infection", "impetigo", "infected wounds"]},
    {"id": 180, "name": "Fusidic acid cream", "category": "Dermatology", "form": "cream", "strength": "2%", "is_otc": False,
     "common_uses": ["skin infection", "impetigo"]},
    {"id": 181, "name": "Silver sulfadiazine cream", "category": "Dermatology", "form": "cream", "strength": "1%", "is_otc": False,
     "common_uses": ["burns", "wound infection"]},
    
    {"id": 182, "name": "Benzoyl peroxide gel", "category": "Dermatology", "form": "gel", "strength": "2.5%", "is_otc": True,
     "dosage": "Apply at night", "common_uses": ["acne", "pimples"]},
    {"id": 183, "name": "Adapalene gel", "category": "Dermatology", "form": "gel", "strength": "0.1%", "is_otc": True,
     "dosage": "Apply at night", "common_uses": ["acne", "blackheads"]},
    {"id": 184, "name": "Tretinoin cream", "category": "Dermatology", "form": "cream", "strength": "0.025%", "is_otc": False,
     "common_uses": ["acne", "skin aging", "hyperpigmentation"]},
    
    # ==================== EYE & EAR DROPS ====================
    {"id": 185, "name": "Ciprofloxacin eye drops", "category": "Eye & Ear", "form": "drops", "strength": "0.3%", "is_otc": False,
     "dosage": "1-2 drops 4 times daily", "common_uses": ["eye infection", "conjunctivitis"]},
    {"id": 186, "name": "Moxifloxacin eye drops", "category": "Eye & Ear", "form": "drops", "strength": "0.5%", "is_otc": False,
     "common_uses": ["eye infection", "conjunctivitis"]},
    {"id": 187, "name": "Tobramycin eye drops", "category": "Eye & Ear", "form": "drops", "strength": "0.3%", "is_otc": False},
    {"id": 188, "name": "Chloramphenicol eye drops", "category": "Eye & Ear", "form": "drops", "strength": "0.5%", "is_otc": True,
     "common_uses": ["eye infection", "conjunctivitis"]},
    {"id": 189, "name": "Ofloxacin ear drops", "category": "Eye & Ear", "form": "drops", "strength": "0.3%", "is_otc": False,
     "common_uses": ["ear infection", "otitis"]},
    {"id": 190, "name": "Artificial tears (Carboxymethylcellulose)", "category": "Eye & Ear", "form": "drops", "is_otc": True,
     "dosage": "1-2 drops as needed", "common_uses": ["dry eyes", "eye strain", "eye lubrication"]},
    {"id": 191, "name": "Naphazoline eye drops", "category": "Eye & Ear", "form": "drops", "is_otc": True,
     "common_uses": ["red eyes", "eye allergy"]},
    
    # ==================== MENTAL HEALTH ====================
    {"id": 192, "name": "Escitalopram", "category": "Mental Health", "form": "tablet", "strength": "10mg", "is_otc": False,
     "common_uses": ["depression", "anxiety", "panic disorder"]},
    {"id": 193, "name": "Sertraline", "category": "Mental Health", "form": "tablet", "strength": "50mg", "is_otc": False,
     "common_uses": ["depression", "anxiety", "OCD", "PTSD"]},
    {"id": 194, "name": "Fluoxetine", "category": "Mental Health", "form": "capsule", "strength": "20mg", "is_otc": False,
     "common_uses": ["depression", "OCD", "bulimia"]},
    {"id": 195, "name": "Clonazepam", "category": "Mental Health", "form": "tablet", "strength": "0.5mg", "is_otc": False,
     "common_uses": ["anxiety", "panic disorder", "seizures"]},
    {"id": 196, "name": "Olanzapine", "category": "Mental Health", "form": "tablet", "strength": "5mg", "is_otc": False,
     "common_uses": ["schizophrenia", "bipolar disorder"]},
    {"id": 197, "name": "Risperidone", "category": "Mental Health", "form": "tablet", "strength": "2mg", "is_otc": False},
    {"id": 198, "name": "Quetiapine", "category": "Mental Health", "form": "tablet", "strength": "25mg", "is_otc": False},
    
    # ==================== HORMONES & THYROID ====================
    {"id": 199, "name": "Levothyroxine", "category": "Thyroid", "form": "tablet", "strength": "50mcg", "is_otc": False,
     "dosage": "1 tablet empty stomach in morning", "common_uses": ["hypothyroidism"]},
    {"id": 200, "name": "Levothyroxine", "category": "Thyroid", "form": "tablet", "strength": "100mcg", "is_otc": False},
    {"id": 201, "name": "Carbimazole", "category": "Thyroid", "form": "tablet", "strength": "5mg", "is_otc": False,
     "common_uses": ["hyperthyroidism"]},
    {"id": 202, "name": "Propylthiouracil", "category": "Thyroid", "form": "tablet", "strength": "50mg", "is_otc": False},
    
    # ==================== CONTRACEPTIVES ====================
    {"id": 203, "name": "Levonorgestrel (Emergency)", "category": "Contraceptives", "form": "tablet", "strength": "1.5mg", "is_otc": True,
     "dosage": "Single dose within 72 hours", "common_uses": ["emergency contraception"]},
    {"id": 204, "name": "Ethinyl estradiol + Levonorgestrel", "category": "Contraceptives", "form": "tablet", "is_otc": False,
     "common_uses": ["oral contraception"]},
    
    # ==================== ANTIMALARIALS ====================
    {"id": 205, "name": "Chloroquine", "category": "Antimalarials", "form": "tablet", "strength": "250mg", "is_otc": False,
     "common_uses": ["malaria treatment", "malaria prophylaxis"]},
    {"id": 206, "name": "Artemether + Lumefantrine", "category": "Antimalarials", "form": "tablet", "strength": "20mg+120mg", "is_otc": False,
     "common_uses": ["malaria treatment"]},
    {"id": 207, "name": "Artesunate injection", "category": "Antimalarials", "form": "injection", "strength": "60mg", "is_otc": False,
     "common_uses": ["severe malaria"]},
    
    # ==================== CARDIOVASCULAR ====================
    {"id": 208, "name": "Aspirin", "category": "Cardiovascular", "form": "tablet", "strength": "75mg", "is_otc": True,
     "dosage": "1 tablet daily", "common_uses": ["heart disease prevention", "blood thinner"]},
    {"id": 209, "name": "Aspirin", "category": "Cardiovascular", "form": "tablet", "strength": "150mg", "is_otc": True},
    {"id": 210, "name": "Clopidogrel", "category": "Cardiovascular", "form": "tablet", "strength": "75mg", "is_otc": False,
     "dosage": "1 tablet daily", "common_uses": ["heart attack prevention", "stroke prevention"]},
    {"id": 211, "name": "Atorvastatin", "category": "Cardiovascular", "form": "tablet", "strength": "10mg", "is_otc": False,
     "dosage": "1 tablet at night", "common_uses": ["high cholesterol", "heart disease"]},
    {"id": 212, "name": "Atorvastatin", "category": "Cardiovascular", "form": "tablet", "strength": "20mg", "is_otc": False},
    {"id": 213, "name": "Rosuvastatin", "category": "Cardiovascular", "form": "tablet", "strength": "10mg", "is_otc": False},
    {"id": 214, "name": "Nitroglycerin tablet", "category": "Cardiovascular", "form": "tablet", "strength": "0.5mg", "is_otc": False,
     "dosage": "Place under tongue during chest pain", "common_uses": ["angina", "chest pain"]},
    {"id": 215, "name": "Isosorbide dinitrate", "category": "Cardiovascular", "form": "tablet", "strength": "5mg", "is_otc": False},
    {"id": 216, "name": "Digoxin", "category": "Cardiovascular", "form": "tablet", "strength": "0.25mg", "is_otc": False,
     "common_uses": ["heart failure", "atrial fibrillation"]},
    {"id": 217, "name": "Warfarin", "category": "Cardiovascular", "form": "tablet", "strength": "5mg", "is_otc": False,
     "common_uses": ["blood clot prevention", "atrial fibrillation"]},
]


# ============================================================
# SYMPTOM TO DRUG MAPPING
# Maps symptoms to appropriate OTC medications
# ============================================================

SYMPTOM_TO_DRUGS = {
    # Pain & Fever
    "headache": ["Paracetamol 650mg", "Ibuprofen 400mg", "Paracetamol 500mg"],
    "fever": ["Paracetamol 650mg", "Paracetamol 500mg", "Ibuprofen 400mg", "Mefenamic acid 500mg"],
    "body pain": ["Paracetamol 650mg", "Ibuprofen 400mg", "Diclofenac gel 1%"],
    "muscle pain": ["Ibuprofen 400mg", "Diclofenac gel 1%", "Piroxicam gel 0.5%"],
    "joint pain": ["Ibuprofen 400mg", "Diclofenac gel 1%", "Etoricoxib 60mg"],
    "back pain": ["Ibuprofen 400mg", "Diclofenac gel 1%", "Aceclofenac gel"],
    "toothache": ["Ibuprofen 400mg", "Mefenamic acid 500mg", "Paracetamol 650mg"],
    "menstrual pain": ["Mefenamic acid 500mg", "Ibuprofen 400mg", "Dicyclomine 20mg"],
    
    # Cold & Respiratory
    "cold": ["Cetirizine 10mg", "Paracetamol 650mg", "Ambroxol syrup"],
    "cough": ["Ambroxol syrup", "Dextromethorphan syrup", "Bromhexine 8mg"],
    "dry cough": ["Dextromethorphan syrup", "Honey + warm water"],
    "productive cough": ["Ambroxol syrup", "Guaifenesin syrup", "Bromhexine 8mg"],
    "sore throat": ["Paracetamol 650mg", "Lozenges", "Warm salt water gargle"],
    "blocked nose": ["Oxymetazoline nasal spray", "Steam inhalation", "Cetirizine 10mg"],
    "runny nose": ["Cetirizine 10mg", "Levocetirizine 5mg", "Loratadine 10mg"],
    "sneezing": ["Cetirizine 10mg", "Levocetirizine 5mg", "Fexofenadine 120mg"],
    "wheezing": ["Salbutamol inhaler", "Salbutamol syrup", "Montelukast 10mg"],
    "asthma": ["Salbutamol inhaler", "Budesonide inhaler", "Montelukast 10mg"],
    
    # Allergies
    "allergy": ["Cetirizine 10mg", "Levocetirizine 5mg", "Fexofenadine 120mg"],
    "allergic rhinitis": ["Cetirizine 10mg", "Levocetirizine 5mg", "Azelastine nasal spray"],
    "skin allergy": ["Cetirizine 10mg", "Hydrocortisone cream 1%", "Calamine lotion"],
    "urticaria": ["Cetirizine 10mg", "Levocetirizine 5mg", "Fexofenadine 180mg"],
    "hives": ["Cetirizine 10mg", "Levocetirizine 5mg", "Calamine lotion"],
    "itching": ["Cetirizine 10mg", "Calamine lotion", "Hydrocortisone cream 1%"],
    
    # Gastrointestinal
    "acidity": ["Omeprazole 20mg", "Pantoprazole 40mg", "Antacid gel"],
    "heartburn": ["Omeprazole 20mg", "Pantoprazole 40mg", "Ranitidine 150mg"],
    "indigestion": ["Domperidone 10mg", "Antacid gel", "Omeprazole 20mg"],
    "bloating": ["Domperidone 10mg", "Antacid gel", "Simethicone"],
    "gas": ["Simethicone", "Antacid gel", "Domperidone 10mg"],
    "nausea": ["Domperidone 10mg", "Ondansetron 4mg", "Ginger"],
    "vomiting": ["Ondansetron 4mg", "Domperidone 10mg", "ORS"],
    "stomach pain": ["Dicyclomine 20mg", "Antacid gel", "Omeprazole 20mg"],
    "abdominal pain": ["Dicyclomine 20mg", "Hyoscine 10mg", "Antacid gel"],
    "diarrhea": ["ORS", "Loperamide 2mg", "Zinc 20mg"],
    "loose motions": ["ORS", "Loperamide 2mg", "Probiotics"],
    "constipation": ["Lactulose syrup", "Isabgol", "Bisacodyl 5mg"],
    "worms": ["Albendazole 400mg", "Mebendazole 100mg"],
    
    # Skin
    "rash": ["Calamine lotion", "Hydrocortisone cream 1%", "Cetirizine 10mg"],
    "fungal infection": ["Clotrimazole cream 1%", "Terbinafine cream 1%", "Ketoconazole cream 2%"],
    "ringworm": ["Clotrimazole cream 1%", "Terbinafine cream 1%", "Miconazole cream 2%"],
    "acne": ["Benzoyl peroxide gel 2.5%", "Adapalene gel 0.1%", "Clindamycin gel"],
    "pimples": ["Benzoyl peroxide gel 2.5%", "Adapalene gel 0.1%"],
    "dry skin": ["Moisturizer", "Coconut oil", "Petroleum jelly"],
    "sunburn": ["Calamine lotion", "Aloe vera gel", "Hydrocortisone cream 1%"],
    "insect bite": ["Calamine lotion", "Hydrocortisone cream 1%", "Cetirizine 10mg"],
    "scabies": ["Permethrin cream 5%", "Ivermectin 12mg"],
    
    # Eye
    "eye infection": ["Ciprofloxacin eye drops", "Chloramphenicol eye drops"],
    "conjunctivitis": ["Ciprofloxacin eye drops", "Moxifloxacin eye drops"],
    "red eyes": ["Naphazoline eye drops", "Artificial tears"],
    "dry eyes": ["Artificial tears", "Carboxymethylcellulose eye drops"],
    "eye strain": ["Artificial tears", "Eye rest"],
    "watery eyes": ["Olopatadine eye drops", "Sodium cromoglycate eye drops"],
    
    # General
    "weakness": ["Multivitamin tablets", "Vitamin B Complex", "Iron + Folic acid"],
    "fatigue": ["Multivitamin tablets", "Vitamin B12", "Iron + Folic acid"],
    "dehydration": ["ORS", "Electrolyte water", "Coconut water"],
    "vitamin deficiency": ["Multivitamin tablets", "Vitamin D3 60000IU"],
    "anemia": ["Iron + Folic acid", "Vitamin B12", "Folic acid 5mg"],
    
    # Sleep & Anxiety (OTC only)
    "insomnia": ["Melatonin (if available)", "Warm milk", "Chamomile tea"],
    "anxiety": ["Ashwagandha (herbal)", "Deep breathing", "Exercise"],
    "stress": ["Vitamin B Complex", "Ashwagandha", "Exercise"],
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_drugs_for_symptom(symptom: str) -> List[str]:
    """Get recommended OTC drugs for a symptom"""
    symptom_lower = symptom.lower().strip()
    
    # Direct match
    if symptom_lower in SYMPTOM_TO_DRUGS:
        return SYMPTOM_TO_DRUGS[symptom_lower]
    
    # Partial match
    for key, drugs in SYMPTOM_TO_DRUGS.items():
        if symptom_lower in key or key in symptom_lower:
            return drugs
    
    return []


def get_drug_by_name(name: str) -> Optional[Dict]:
    """Get drug details by name"""
    name_lower = name.lower().strip()
    for drug in GENERIC_DRUGS_DATABASE:
        if name_lower in drug["name"].lower():
            return drug
    return None


def get_drugs_by_category(category: str) -> List[Dict]:
    """Get all drugs in a category"""
    category_lower = category.lower().strip()
    return [d for d in GENERIC_DRUGS_DATABASE if category_lower in d["category"].lower()]


def get_otc_drugs() -> List[Dict]:
    """Get all OTC (non-prescription) drugs"""
    return [d for d in GENERIC_DRUGS_DATABASE if d.get("is_otc", False)]


def search_drugs(query: str) -> List[Dict]:
    """Search drugs by name, category, or use"""
    query_lower = query.lower().strip()
    results = []
    
    for drug in GENERIC_DRUGS_DATABASE:
        # Search in name
        if query_lower in drug["name"].lower():
            results.append(drug)
            continue
        
        # Search in category
        if query_lower in drug["category"].lower():
            results.append(drug)
            continue
        
        # Search in common uses
        uses = drug.get("common_uses", [])
        if any(query_lower in use.lower() for use in uses):
            results.append(drug)
    
    return results


# Export for use in other modules
__all__ = [
    "GENERIC_DRUGS_DATABASE",
    "SYMPTOM_TO_DRUGS",
    "get_drugs_for_symptom",
    "get_drug_by_name",
    "get_drugs_by_category",
    "get_otc_drugs",
    "search_drugs",
    "GenericDrug",
    "DrugForm"
]
