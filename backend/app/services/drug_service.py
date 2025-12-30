"""
Drug & Medication Service
- OTC medication suggestions based on symptoms
- Drug interaction checker
- Dosage guidelines
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Common OTC medications database
OTC_MEDICATIONS = {
    "headache": [
        {
            "name": "Paracetamol (Crocin/Dolo)",
            "generic": "Acetaminophen",
            "dosage": "500-650mg every 4-6 hours",
            "max_daily": "4000mg (4g)",
            "warnings": ["Avoid with liver disease", "Don't mix with alcohol"],
            "suitable_for": ["Adults", "Children (adjusted dose)"]
        },
        {
            "name": "Ibuprofen (Brufen/Advil)",
            "generic": "Ibuprofen",
            "dosage": "200-400mg every 4-6 hours",
            "max_daily": "1200mg",
            "warnings": ["Take with food", "Avoid if stomach ulcer", "Not for asthma patients"],
            "suitable_for": ["Adults"]
        }
    ],
    "fever": [
        {
            "name": "Paracetamol (Crocin/Dolo)",
            "generic": "Acetaminophen",
            "dosage": "500-650mg every 4-6 hours",
            "max_daily": "4000mg",
            "warnings": ["Avoid with liver disease"],
            "suitable_for": ["Adults", "Children", "Pregnancy (safe)"]
        }
    ],
    "cold": [
        {
            "name": "Cetirizine (Zyrtec/Cetzine)",
            "generic": "Cetirizine",
            "dosage": "10mg once daily",
            "max_daily": "10mg",
            "warnings": ["May cause drowsiness", "Avoid driving"],
            "suitable_for": ["Adults", "Children 6+"]
        },
        {
            "name": "Sinarest/Vicks Action 500",
            "generic": "Paracetamol + Phenylephrine + Chlorpheniramine",
            "dosage": "1 tablet every 6-8 hours",
            "max_daily": "4 tablets",
            "warnings": ["May cause drowsiness", "Not for high BP patients"],
            "suitable_for": ["Adults"]
        }
    ],
    "cough": [
        {
            "name": "Benadryl Cough Syrup",
            "generic": "Diphenhydramine + Ammonium Chloride",
            "dosage": "10ml every 6-8 hours",
            "max_daily": "40ml",
            "warnings": ["Causes drowsiness", "Don't drive"],
            "suitable_for": ["Adults", "Children 6+"]
        },
        {
            "name": "Honitus/Dabur Honitus",
            "generic": "Herbal (Honey-based)",
            "dosage": "10ml 3-4 times daily",
            "max_daily": "40ml",
            "warnings": ["Contains honey - not for diabetics"],
            "suitable_for": ["Adults", "Children 2+"]
        }
    ],
    "stomach pain": [
        {
            "name": "Pantoprazole (Pan/Pantocid)",
            "generic": "Pantoprazole",
            "dosage": "40mg once daily before breakfast",
            "max_daily": "40mg",
            "warnings": ["Take 30 min before food"],
            "suitable_for": ["Adults"]
        },
        {
            "name": "Digene/Gelusil",
            "generic": "Aluminum Hydroxide + Magnesium Hydroxide",
            "dosage": "1-2 tablets after meals",
            "max_daily": "8 tablets",
            "warnings": ["May cause constipation or diarrhea"],
            "suitable_for": ["Adults", "Children 12+"]
        }
    ],
    "acidity": [
        {
            "name": "Omeprazole (Omez)",
            "generic": "Omeprazole",
            "dosage": "20mg once daily before breakfast",
            "max_daily": "20mg",
            "warnings": ["Take 30 min before food", "Long-term use needs monitoring"],
            "suitable_for": ["Adults"]
        },
        {
            "name": "Eno/Hajmola",
            "generic": "Sodium Bicarbonate",
            "dosage": "1 sachet in water as needed",
            "max_daily": "3 sachets",
            "warnings": ["High sodium - avoid in BP"],
            "suitable_for": ["Adults"]
        }
    ],
    "diarrhea": [
        {
            "name": "ORS (Electral/Pedialyte)",
            "generic": "Oral Rehydration Salts",
            "dosage": "After each loose stool",
            "max_daily": "As needed",
            "warnings": ["Dissolve properly in clean water"],
            "suitable_for": ["All ages"]
        },
        {
            "name": "Loperamide (Imodium/Eldoper)",
            "generic": "Loperamide",
            "dosage": "4mg initially, then 2mg after each loose stool",
            "max_daily": "16mg",
            "warnings": ["Not for bloody diarrhea", "Not for children under 2"],
            "suitable_for": ["Adults", "Children 6+"]
        }
    ],
    "allergy": [
        {
            "name": "Cetirizine (Zyrtec/Cetzine)",
            "generic": "Cetirizine",
            "dosage": "10mg once daily",
            "max_daily": "10mg",
            "warnings": ["May cause drowsiness"],
            "suitable_for": ["Adults", "Children 6+"]
        },
        {
            "name": "Loratadine (Claritin/Lorfast)",
            "generic": "Loratadine",
            "dosage": "10mg once daily",
            "max_daily": "10mg",
            "warnings": ["Non-drowsy option"],
            "suitable_for": ["Adults", "Children 6+"]
        }
    ],
    "pain": [
        {
            "name": "Diclofenac (Voveran/Voltaren)",
            "generic": "Diclofenac",
            "dosage": "50mg 2-3 times daily",
            "max_daily": "150mg",
            "warnings": ["Take with food", "Not for heart patients", "Avoid long-term"],
            "suitable_for": ["Adults"]
        }
    ],
    "nausea": [
        {
            "name": "Domperidone (Domstal/Motilium)",
            "generic": "Domperidone",
            "dosage": "10mg before meals",
            "max_daily": "30mg",
            "warnings": ["Not for heart arrhythmia"],
            "suitable_for": ["Adults"]
        },
        {
            "name": "Ondansetron (Emeset/Vomikind)",
            "generic": "Ondansetron",
            "dosage": "4-8mg as needed",
            "max_daily": "24mg",
            "warnings": ["May cause headache"],
            "suitable_for": ["Adults", "Children 4+"]
        }
    ],
    "skin rash": [
        {
            "name": "Calamine Lotion",
            "generic": "Calamine + Zinc Oxide",
            "dosage": "Apply to affected area 2-3 times daily",
            "max_daily": "As needed",
            "warnings": ["External use only"],
            "suitable_for": ["All ages"]
        },
        {
            "name": "Betnovate-N Cream",
            "generic": "Betamethasone + Neomycin",
            "dosage": "Apply thin layer twice daily",
            "max_daily": "Twice daily for max 2 weeks",
            "warnings": ["Not for face", "Don't use long-term", "Prescription recommended"],
            "suitable_for": ["Adults"]
        }
    ],
    "sleep": [
        {
            "name": "Melatonin",
            "generic": "Melatonin",
            "dosage": "3-5mg 30 minutes before bed",
            "max_daily": "10mg",
            "warnings": ["Start with low dose", "Not for long-term"],
            "suitable_for": ["Adults"]
        }
    ],
    "anxiety": [
        {
            "name": "Ashwagandha (Stress Relief)",
            "generic": "Withania somnifera",
            "dosage": "300-600mg daily with meals",
            "max_daily": "600mg",
            "warnings": ["Herbal supplement", "May interact with thyroid meds", "Consult if pregnant"],
            "suitable_for": ["Adults"]
        },
        {
            "name": "Chamomile Tea / Tablets",
            "generic": "Matricaria chamomilla",
            "dosage": "1-2 cups tea or 400mg tablet daily",
            "max_daily": "3 cups or 1200mg",
            "warnings": ["May cause drowsiness", "Avoid if allergic to ragweed"],
            "suitable_for": ["Adults", "Children 6+"]
        },
        {
            "name": "L-Theanine",
            "generic": "L-Theanine (from Green Tea)",
            "dosage": "100-200mg 1-2 times daily",
            "max_daily": "400mg",
            "warnings": ["May enhance effects of blood pressure meds"],
            "suitable_for": ["Adults"]
        }
    ]
}

# Drug interactions database
DRUG_INTERACTIONS = {
    ("ibuprofen", "aspirin"): {
        "severity": "moderate",
        "effect": "Reduced cardioprotective effect of aspirin",
        "recommendation": "Take aspirin 30 min before ibuprofen or use paracetamol instead"
    },
    ("ibuprofen", "blood thinner"): {
        "severity": "severe",
        "effect": "Increased bleeding risk",
        "recommendation": "Avoid combination. Consult doctor."
    },
    ("paracetamol", "alcohol"): {
        "severity": "severe",
        "effect": "Increased liver damage risk",
        "recommendation": "Avoid alcohol while taking paracetamol"
    },
    ("cetirizine", "alcohol"): {
        "severity": "moderate",
        "effect": "Increased drowsiness",
        "recommendation": "Avoid alcohol or use non-drowsy alternative"
    },
    ("omeprazole", "clopidogrel"): {
        "severity": "severe",
        "effect": "Reduced effectiveness of clopidogrel",
        "recommendation": "Use pantoprazole instead. Consult cardiologist."
    },
    ("metformin", "alcohol"): {
        "severity": "severe",
        "effect": "Risk of lactic acidosis",
        "recommendation": "Limit alcohol intake significantly"
    }
}

# Symptom to keyword mapping
SYMPTOM_KEYWORDS = {
    "headache": ["headache", "head pain", "migraine", "head ache", "सिरदर्द", "head hurts"],
    "fever": ["fever", "temperature", "बुखार", "high temperature", "feeling hot"],
    "cold": ["cold", "runny nose", "sneezing", "सर्दी", "जुकाम", "blocked nose", "stuffy"],
    "cough": ["cough", "coughing", "खांसी", "throat pain", "sore throat"],
    "stomach pain": ["stomach pain", "stomach ache", "abdominal pain", "पेट दर्द", "tummy ache", "stomach"],
    "acidity": ["acidity", "heartburn", "gas", "bloating", "एसिडिटी", "acid reflux", "burning"],
    "diarrhea": ["diarrhea", "loose motion", "loose stool", "दस्त", "watery stool"],
    "allergy": ["allergy", "allergic", "itching", "hives", "एलर्जी", "allergies"],
    "pain": ["pain", "body pain", "joint pain", "दर्द", "muscle pain", "aching"],
    "nausea": ["nausea", "vomiting", "उल्टी", "मतली", "feel sick", "throwing up"],
    "skin rash": ["rash", "skin rash", "redness", "चकत्ते", "skin problem"],
    "sleep": ["sleep", "insomnia", "can't sleep", "नींद नहीं", "sleepless", "cannot sleep"],
    "anxiety": ["anxiety", "anxious", "stressed", "चिंता", "nervous", "worried", "panic", "scared"]
}


class DrugService:
    def __init__(self):
        self.medications = OTC_MEDICATIONS
        self.interactions = DRUG_INTERACTIONS
        self.symptom_keywords = SYMPTOM_KEYWORDS
    
    def identify_symptoms(self, text: str) -> List[str]:
        """Identify symptoms from user text"""
        text_lower = text.lower()
        found_symptoms = []
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    if symptom not in found_symptoms:
                        found_symptoms.append(symptom)
                    break
        
        return found_symptoms
    
    def get_medications_for_symptoms(self, symptoms: List[str]) -> Dict[str, Any]:
        """Get medication suggestions for identified symptoms"""
        result = {
            "symptoms": symptoms,
            "medications": [],
            "general_advice": [],
            "when_to_see_doctor": []
        }
        
        for symptom in symptoms:
            if symptom in self.medications:
                for med in self.medications[symptom]:
                    med_info = {
                        **med,
                        "for_symptom": symptom
                    }
                    # Avoid duplicates
                    if not any(m["name"] == med["name"] for m in result["medications"]):
                        result["medications"].append(med_info)
        
        # Add general advice
        if symptoms:
            result["general_advice"] = [
                "Stay hydrated - drink plenty of water",
                "Get adequate rest",
                "Monitor symptoms for 24-48 hours",
                "Avoid self-medicating for more than 3 days"
            ]
            
            result["when_to_see_doctor"] = [
                "Symptoms persist beyond 3-5 days",
                "High fever (>102°F / 39°C) for more than 2 days",
                "Severe pain or difficulty breathing",
                "Symptoms worsen despite medication"
            ]
        
        return result
    
    def check_interactions(self, medications: List[str], current_meds: List[str] = None) -> List[Dict]:
        """Check for drug interactions"""
        interactions_found = []
        
        all_meds = medications + (current_meds or [])
        all_meds_lower = [m.lower() for m in all_meds]
        
        for (drug1, drug2), info in self.interactions.items():
            drug1_found = any(drug1 in m for m in all_meds_lower)
            drug2_found = any(drug2 in m for m in all_meds_lower)
            
            if drug1_found and drug2_found:
                interactions_found.append({
                    "drugs": [drug1, drug2],
                    **info
                })
        
        return interactions_found
    
    def get_prescription_response(self, user_message: str, current_medications: List[str] = None) -> Dict[str, Any]:
        """
        Main method to get medication suggestions from user symptoms
        """
        # Identify symptoms
        symptoms = self.identify_symptoms(user_message)
        
        if not symptoms:
            return {
                "found_symptoms": False,
                "message": "I couldn't identify specific symptoms. Please describe your symptoms clearly (e.g., 'I have a headache and fever')."
            }
        
        # Get medications
        med_info = self.get_medications_for_symptoms(symptoms)
        
        # Check interactions
        suggested_meds = [m["generic"].lower() for m in med_info["medications"]]
        interactions = self.check_interactions(suggested_meds, current_medications)
        
        return {
            "found_symptoms": True,
            "symptoms": symptoms,
            "medications": med_info["medications"],
            "interactions": interactions,
            "general_advice": med_info["general_advice"],
            "when_to_see_doctor": med_info["when_to_see_doctor"],
            "disclaimer": "These are OTC suggestions only. For prescription medications, consult a licensed doctor."
        }
    
    def format_prescription_text(self, prescription: Dict) -> str:
        """Format prescription data into readable text"""
        if not prescription.get("found_symptoms"):
            return prescription.get("message", "No symptoms identified.")
        
        lines = []
        lines.append(f"📋 **Symptoms Identified:** {', '.join(prescription['symptoms'])}\n")
        
        lines.append("💊 **Suggested OTC Medications:**\n")
        for med in prescription["medications"][:4]:  # Limit to 4 meds
            lines.append(f"• **{med['name']}** ({med['generic']})")
            lines.append(f"  - Dosage: {med['dosage']}")
            lines.append(f"  - Max daily: {med['max_daily']}")
            if med['warnings']:
                lines.append(f"  - ⚠️ {', '.join(med['warnings'][:2])}")
            lines.append("")
        
        if prescription.get("interactions"):
            lines.append("⚠️ **Drug Interactions Warning:**")
            for interaction in prescription["interactions"]:
                lines.append(f"• {interaction['drugs'][0]} + {interaction['drugs'][1]}: {interaction['effect']}")
            lines.append("")
        
        lines.append("🏥 **See a Doctor If:**")
        for advice in prescription["when_to_see_doctor"][:3]:
            lines.append(f"• {advice}")
        
        lines.append("\n⚕️ *This is general guidance only. Consult a healthcare professional for proper diagnosis and prescription.*")
        
        return "\n".join(lines)


# Global instance
drug_service = DrugService()
