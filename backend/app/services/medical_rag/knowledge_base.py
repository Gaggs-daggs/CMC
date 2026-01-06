"""
Medical Knowledge Base with RAG (Retrieval-Augmented Generation)
Prevents LLM hallucinations by grounding responses in verified medical sources

Sources: WHO, CDC, Mayo Clinic, SNOMED-CT, ICD-10 concepts
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class MedicalDocument:
    """Verified medical document/fact"""
    id: str
    content: str
    source: str  # WHO, CDC, Mayo Clinic, etc.
    category: str  # symptom, disease, treatment, drug, emergency
    confidence: float  # Source reliability score
    metadata: Dict


@dataclass
class RetrievalResult:
    """Result from knowledge base retrieval"""
    document: MedicalDocument
    relevance_score: float
    citation: str


# Comprehensive Medical Knowledge Base (Verified Facts Only)
VERIFIED_MEDICAL_KNOWLEDGE = {
    # ============= SYMPTOMS & CONDITIONS =============
    "headache": {
        "description": "Pain in any region of the head, ranging from sharp to dull, throbbing to constant",
        "common_causes": ["tension", "migraine", "dehydration", "stress", "eye strain", "sinusitis", "hypertension"],
        "red_flags": ["sudden severe onset", "fever with stiff neck", "after head injury", "vision changes", "confusion", "weakness"],
        "self_care": ["rest in dark room", "hydration", "OTC pain relievers", "cold/warm compress"],
        "seek_medical_if": ["worst headache of life", "fever > 103°F", "confusion", "neck stiffness", "after trauma"],
        "source": "Mayo Clinic, WHO Guidelines",
        "icd10": "R51"
    },
    "fever": {
        "description": "Body temperature above 100.4°F (38°C)",
        "common_causes": ["viral infection", "bacterial infection", "inflammatory conditions", "heat exhaustion"],
        "red_flags": ["temperature > 104°F", "seizures", "confusion", "difficulty breathing", "severe headache with neck stiffness"],
        "self_care": ["rest", "fluids", "light clothing", "acetaminophen/ibuprofen as directed"],
        "seek_medical_if": ["infant < 3 months with any fever", "fever > 104°F", "lasting > 3 days", "with severe symptoms"],
        "source": "CDC, American Academy of Pediatrics",
        "icd10": "R50.9"
    },
    "chest_pain": {
        "description": "Discomfort or pain in the chest area",
        "emergency_symptoms": ["crushing pressure", "pain radiating to arm/jaw", "shortness of breath", "sweating", "nausea"],
        "common_causes": ["musculoskeletal", "acid reflux", "anxiety", "cardiac", "pulmonary"],
        "immediate_action": "If cardiac symptoms suspected, call emergency services immediately (108 in India)",
        "self_care": "Only for clearly non-cardiac causes after medical evaluation",
        "source": "American Heart Association, WHO",
        "icd10": "R07.9",
        "is_emergency": True
    },
    "anxiety": {
        "description": "Feeling of worry, nervousness, or unease about something with uncertain outcome",
        "symptoms": ["restlessness", "rapid heartbeat", "sweating", "trembling", "difficulty concentrating", "sleep problems"],
        "coping_strategies": ["deep breathing (4-7-8 technique)", "grounding exercises", "physical activity", "limiting caffeine"],
        "when_to_seek_help": ["interferes with daily life", "panic attacks", "avoiding activities", "thoughts of self-harm"],
        "resources_india": ["iCALL: 9152987821", "Vandrevala Foundation: 1860-2662-345", "NIMHANS: 080-46110007"],
        "source": "WHO Mental Health Guidelines, NIMHANS",
        "icd10": "F41.9"
    },
    "depression": {
        "description": "Persistent feeling of sadness and loss of interest",
        "symptoms": ["persistent sadness", "loss of interest", "sleep changes", "fatigue", "difficulty concentrating", "appetite changes"],
        "warning_signs": ["thoughts of death/suicide", "giving away possessions", "saying goodbye", "sudden calmness after depression"],
        "immediate_help": "If having thoughts of self-harm, contact crisis helpline immediately",
        "resources_india": ["iCALL: 9152987821", "Vandrevala Foundation: 1860-2662-345", "AASRA: 9820466726"],
        "source": "WHO, NIMHANS India",
        "icd10": "F32.9"
    },
    "cough": {
        "description": "Sudden expulsion of air from lungs to clear airways",
        "types": ["dry cough", "wet/productive cough", "acute (<3 weeks)", "chronic (>8 weeks)"],
        "common_causes": ["viral infection", "allergies", "asthma", "GERD", "post-nasal drip"],
        "red_flags": ["blood in sputum", "difficulty breathing", "chest pain", "high fever", "weight loss"],
        "self_care": ["honey (adults/children >1yr)", "warm fluids", "humidifier", "cough drops"],
        "source": "CDC, American Lung Association",
        "icd10": "R05"
    },
    "stomach_pain": {
        "description": "Discomfort or pain in the abdominal area",
        "locations": {"upper": "gastritis, ulcer, gallbladder", "lower": "appendicitis, IBS, gynecological", "diffuse": "gastroenteritis, constipation"},
        "red_flags": ["severe sudden pain", "rigid abdomen", "blood in stool/vomit", "high fever", "unable to pass gas"],
        "emergency_signs": ["right lower quadrant pain with fever (appendicitis)", "severe upper abdominal pain radiating to back"],
        "self_care": ["clear fluids", "BRAT diet", "avoid spicy/fatty foods", "rest"],
        "source": "Mayo Clinic, American College of Gastroenterology",
        "icd10": "R10.9"
    },
    "breathing_difficulty": {
        "description": "Shortness of breath or labored breathing",
        "emergency_symptoms": ["cannot speak full sentences", "blue lips/fingertips", "chest pain", "confusion", "rapid decline"],
        "common_causes": ["asthma", "anxiety", "COPD", "pneumonia", "heart failure", "allergic reaction"],
        "immediate_action": "If severe, call emergency services (108 in India) immediately",
        "self_care": "Only for mild cases with known cause (e.g., mild asthma with prescribed inhaler)",
        "source": "WHO, American Thoracic Society",
        "icd10": "R06.0",
        "is_emergency": True
    },
    
    # ============= MEDICATIONS (OTC) =============
    "paracetamol": {
        "generic_name": "Acetaminophen/Paracetamol",
        "uses": ["fever", "mild to moderate pain", "headache"],
        "adult_dose": "500-1000mg every 4-6 hours, max 4000mg/day",
        "child_dose": "10-15mg/kg every 4-6 hours",
        "warnings": ["avoid with liver disease", "do not exceed max dose", "avoid alcohol"],
        "interactions": ["warfarin", "alcohol"],
        "source": "WHO Essential Medicines List",
        "otc": True
    },
    "ibuprofen": {
        "generic_name": "Ibuprofen",
        "uses": ["pain", "fever", "inflammation"],
        "adult_dose": "200-400mg every 4-6 hours, max 1200mg/day (OTC)",
        "warnings": ["take with food", "avoid with kidney disease", "avoid with stomach ulcers", "avoid in late pregnancy"],
        "interactions": ["aspirin", "blood thinners", "ACE inhibitors"],
        "source": "WHO Essential Medicines List",
        "otc": True
    },
    
    # ============= EMERGENCY PROTOCOLS =============
    "emergency_india": {
        "ambulance": "108",
        "police": "100",
        "fire": "101",
        "women_helpline": "181",
        "child_helpline": "1098",
        "mental_health": {
            "iCALL": "9152987821",
            "Vandrevala": "1860-2662-345",
            "NIMHANS": "080-46110007",
            "AASRA": "9820466726"
        },
        "poison_control": "1800-116-117",
        "source": "Government of India Emergency Services"
    }
}

# ICD-10 to symptom mapping
ICD10_MAPPING = {
    "R51": "headache",
    "R50.9": "fever",
    "R07.9": "chest_pain",
    "F41.9": "anxiety",
    "F32.9": "depression",
    "R05": "cough",
    "R10.9": "stomach_pain",
    "R06.0": "breathing_difficulty"
}

# SNOMED-CT concept mappings (simplified)
SNOMED_CONCEPTS = {
    "25064002": {"term": "headache", "category": "finding"},
    "386661006": {"term": "fever", "category": "finding"},
    "29857009": {"term": "chest_pain", "category": "finding"},
    "48694002": {"term": "anxiety", "category": "finding"},
    "35489007": {"term": "depression", "category": "disorder"},
    "49727002": {"term": "cough", "category": "finding"},
    "21522001": {"term": "abdominal_pain", "category": "finding"},
    "267036007": {"term": "dyspnea", "category": "finding"}
}


class MedicalKnowledgeBase:
    """
    Production-grade Medical Knowledge Base with RAG capabilities
    
    Features:
    - Verified medical facts from WHO, CDC, Mayo Clinic
    - ICD-10 and SNOMED-CT ontology mapping
    - Citation tracking for all information
    - Confidence scoring
    - Emergency detection
    """
    
    def __init__(self):
        self.knowledge = VERIFIED_MEDICAL_KNOWLEDGE
        self.icd10_map = ICD10_MAPPING
        self.snomed_map = SNOMED_CONCEPTS
        self._embedding_cache = {}
        logger.info("✅ Medical Knowledge Base initialized with verified sources")
    
    def retrieve(
        self, 
        query: str, 
        category: Optional[str] = None,
        top_k: int = 3
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant medical knowledge for a query
        
        Args:
            query: User query or symptom description
            category: Optional filter (symptom, drug, emergency)
            top_k: Number of results to return
        
        Returns:
            List of RetrievalResult with citations
        """
        query_lower = query.lower()
        results = []
        
        # Keyword matching (in production, use embeddings + vector search)
        for key, data in self.knowledge.items():
            relevance = self._calculate_relevance(query_lower, key, data)
            if relevance > 0.3:  # Threshold
                doc = MedicalDocument(
                    id=hashlib.md5(key.encode()).hexdigest()[:8],
                    content=json.dumps(data),
                    source=data.get("source", "Medical Database"),
                    category=self._get_category(key),
                    confidence=0.95,  # Verified source
                    metadata={"key": key, "icd10": data.get("icd10")}
                )
                results.append(RetrievalResult(
                    document=doc,
                    relevance_score=relevance,
                    citation=f"[{data.get('source', 'Medical Database')}]"
                ))
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
    
    def _calculate_relevance(self, query: str, key: str, data: dict) -> float:
        """Calculate relevance score between query and knowledge entry"""
        score = 0.0
        
        # Direct key match
        if key in query:
            score += 0.8
        
        # Check description
        desc = data.get("description", "").lower()
        if any(word in desc for word in query.split()):
            score += 0.3
        
        # Check symptoms/causes
        for field in ["common_causes", "symptoms", "uses"]:
            if field in data:
                items = data[field]
                if isinstance(items, list):
                    for item in items:
                        if item.lower() in query or query in item.lower():
                            score += 0.2
        
        return min(score, 1.0)
    
    def _get_category(self, key: str) -> str:
        """Determine category of knowledge entry"""
        if key in ["paracetamol", "ibuprofen"]:
            return "medication"
        if key == "emergency_india":
            return "emergency"
        if key in ["anxiety", "depression"]:
            return "mental_health"
        return "symptom"
    
    def get_symptom_info(self, symptom: str) -> Optional[Dict]:
        """Get detailed information about a symptom"""
        symptom_lower = symptom.lower().replace(" ", "_")
        return self.knowledge.get(symptom_lower)
    
    def get_medication_info(self, medication: str) -> Optional[Dict]:
        """Get verified medication information"""
        med_lower = medication.lower()
        return self.knowledge.get(med_lower)
    
    def check_emergency(self, symptoms: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Check if symptoms indicate emergency
        
        Returns:
            (is_emergency, reason)
        """
        emergency_keywords = [
            "chest pain", "difficulty breathing", "can't breathe",
            "unconscious", "seizure", "severe bleeding", "suicide",
            "self harm", "heart attack", "stroke", "poisoning"
        ]
        
        combined = " ".join(symptoms).lower()
        
        for keyword in emergency_keywords:
            if keyword in combined:
                return True, f"Emergency indicator detected: {keyword}"
        
        # Check red flags in knowledge base
        for symptom in symptoms:
            info = self.get_symptom_info(symptom)
            if info and info.get("is_emergency"):
                return True, f"Medical emergency: {symptom}"
        
        return False, None
    
    def get_red_flags(self, symptom: str) -> List[str]:
        """Get red flag symptoms that require immediate attention"""
        info = self.get_symptom_info(symptom)
        if info:
            return info.get("red_flags", [])
        return []
    
    def get_self_care(self, symptom: str) -> List[str]:
        """Get evidence-based self-care recommendations"""
        info = self.get_symptom_info(symptom)
        if info:
            return info.get("self_care", [])
        return []
    
    def get_citation(self, topic: str) -> str:
        """Get citation for medical information"""
        info = self.knowledge.get(topic.lower().replace(" ", "_"))
        if info:
            return info.get("source", "Medical Database")
        return "Medical Database"
    
    def format_rag_context(self, query: str, max_tokens: int = 500) -> str:
        """
        Format retrieved knowledge as context for LLM
        
        This is the key RAG function that provides grounded facts
        to the LLM to prevent hallucinations
        """
        results = self.retrieve(query, top_k=3)
        
        if not results:
            return ""
        
        context_parts = [
            "VERIFIED MEDICAL INFORMATION (cite these sources in your response):\n"
        ]
        
        for result in results:
            data = json.loads(result.document.content)
            source = result.citation
            
            # Format based on category
            if result.document.category == "symptom":
                context_parts.append(f"\n📋 {data.get('description', '')} {source}")
                if "common_causes" in data:
                    context_parts.append(f"Common causes: {', '.join(data['common_causes'][:5])}")
                if "self_care" in data:
                    context_parts.append(f"Evidence-based self-care: {', '.join(data['self_care'][:4])}")
                if "red_flags" in data:
                    context_parts.append(f"⚠️ Seek medical care if: {', '.join(data['red_flags'][:3])}")
            
            elif result.document.category == "medication":
                context_parts.append(f"\n💊 {data.get('generic_name', '')} {source}")
                context_parts.append(f"Uses: {', '.join(data.get('uses', []))}")
                context_parts.append(f"Adult dose: {data.get('adult_dose', 'Consult pharmacist')}")
                if data.get("warnings"):
                    context_parts.append(f"⚠️ Warnings: {', '.join(data['warnings'][:3])}")
            
            elif result.document.category == "mental_health":
                context_parts.append(f"\n🧠 {data.get('description', '')} {source}")
                if "coping_strategies" in data:
                    context_parts.append(f"Coping strategies: {', '.join(data['coping_strategies'][:3])}")
                if "resources_india" in data:
                    context_parts.append(f"Helplines: {', '.join(data['resources_india'][:2])}")
        
        return "\n".join(context_parts)[:max_tokens]
    
    def get_emergency_numbers(self) -> Dict:
        """Get emergency contact numbers for India"""
        return self.knowledge.get("emergency_india", {})


# Singleton instance
_knowledge_base: Optional[MedicalKnowledgeBase] = None

def get_knowledge_base() -> MedicalKnowledgeBase:
    """Get or create the medical knowledge base singleton"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = MedicalKnowledgeBase()
    return _knowledge_base
