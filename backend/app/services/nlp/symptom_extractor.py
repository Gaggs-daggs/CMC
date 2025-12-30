import logging
import json
import re
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from thefuzz import process, fuzz

from app.config import settings
from app.models.schemas import ExtractedSymptom

logger = logging.getLogger(__name__)


class SymptomExtractor:
    """Extract medical symptoms from text using hybrid approach (Rule-based + Fuzzy + Lab Parsing)"""
    
    def __init__(self):
        self.knowledge_graph = self._load_knowledge_graph()
        self.symptom_patterns = self._build_symptom_patterns()
        self.symptom_synonyms = self._build_synonym_map()
        
        self.duration_patterns = [
            r'(\d+)\s*(day|days|week|weeks|hour|hours|minute|minutes|month|months|year|years)',
            r'since\s+(\w+)',
            r'for\s+(\d+\s*\w+)',
            r'(yesterday|today|morning|evening|night|last night)',
        ]
        
        self.severity_keywords = {
            'mild': ['mild', 'slight', 'little', 'minor', 'low', 'थोड़ा', 'हल्का'],
            'moderate': ['moderate', 'medium', 'average', 'मध्यम'],
            'severe': ['severe', 'intense', 'bad', 'terrible', 'unbearable', 'extreme', 'high', 'very', 
                      'तीव्र', 'बहुत', 'गंभीर', 'अधिक', 'dying', 'killing', 'worst']
        }
        
        # Emergency keywords that trigger immediate high urgency
        self.emergency_keywords = [
            'dying', 'dieing', 'death', 'kill me', 'suicide', 'heart attack', 'stroke', 
            'unconscious', 'not breathing', 'can\'t breathe', 'cant breathe', 'choking', 
            'blue', 'collapsed', 'fainted', 'chest pain', 'severe bleeding', 'accident', 
            'trauma', 'poison', 'poisoning', 'burned', 'burnt'
        ]
        
        # Lab result patterns
        self.lab_patterns = {
            'cbc': [
                r'cbc\s*(?:count)?\s*(?:is|of|are)?\s*(?:over|above|below|under|around)?\s*(\d+)', 
                r'wbc\s*(?:count)?\s*(?:is|of|are)?\s*(?:over|above|below|under|around)?\s*(\d+)'
            ],
            'platelets': [
                r'platelet\s*(?:count)?\s*(?:is|of|are)?\s*(?:over|above|below|under|around)?\s*(\d+)', 
                r'platelets\s*(?:are)?\s*(?:over|above|below|under|around)?\s*(\d+)'
            ],
            'hemoglobin': [r'hemoglobin\s*(?:is|of)?\s*(?:over|above|below|under|around)?\s*(\d+(?:\.\d+)?)', r'hb\s*(?:is|of)?\s*(\d+(?:\.\d+)?)'],
            'sugar': [r'sugar\s*(?:level)?\s*(?:is|of)?\s*(?:over|above|below|under|around)?\s*(\d+)', r'glucose\s*(?:level)?\s*(?:is|of)?\s*(\d+)'],
            'bp': [r'bp\s*(?:is|of)?\s*(\d+/\d+)', r'blood pressure\s*(?:is|of)?\s*(\d+/\d+)']
        }

    def _load_knowledge_graph(self) -> dict:
        """Load medical knowledge graph"""
        try:
            kg_path = Path(settings.KNOWLEDGE_GRAPH_PATH)
            if kg_path.exists():
                with open(kg_path, 'r', encoding='utf-8') as f:
                    kg = json.load(f)
                logger.info(f"Loaded knowledge graph with {len(kg.get('symptoms', {}))} symptoms")
                return kg
            else:
                logger.warning(f"Knowledge graph not found at {kg_path}")
                return {"symptoms": {}, "conditions": {}}
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            return {"symptoms": {}, "conditions": {}}
    
    def _build_symptom_patterns(self) -> dict:
        """Build regex patterns for symptom matching"""
        patterns = {}
        for symptom_name, symptom_data in self.knowledge_graph.get('symptoms', {}).items():
            translations = symptom_data.get('translations', {})
            terms = list(translations.values())
            # Add the key itself as a term
            terms.append(symptom_name.replace('_', ' '))
            
            if terms:
                # Create case-insensitive pattern
                # Sort by length descending to match longest phrases first
                terms.sort(key=len, reverse=True)
                pattern = '|'.join(re.escape(term) for term in terms)
                patterns[symptom_name] = re.compile(f'({pattern})', re.IGNORECASE | re.UNICODE)
        return patterns

    def _build_synonym_map(self) -> Dict[str, str]:
        """Build a flat map of 'term' -> 'symptom_key' for fuzzy matching"""
        synonym_map = {}
        for symptom_name, symptom_data in self.knowledge_graph.get('symptoms', {}).items():
            # Add canonical name
            synonym_map[symptom_name] = symptom_name
            synonym_map[symptom_name.replace('_', ' ')] = symptom_name
            
            # Add translations
            for lang, term in symptom_data.get('translations', {}).items():
                synonym_map[term.lower()] = symptom_name
        return synonym_map
    
    def extract_symptoms(self, text: str, language: str = "en") -> List[ExtractedSymptom]:
        """
        Extract symptoms from text using multiple strategies
        """
        if not text or not text.strip():
            return []
        
        text_lower = text.lower()
        extracted = []
        extracted_names = set()

        # 1. Check for Emergency Intent
        emergency_symptom = self._detect_emergency_intent(text_lower)
        if emergency_symptom:
            extracted.append(emergency_symptom)
            extracted_names.add(emergency_symptom.name)
            logger.warning(f"Emergency intent detected: {emergency_symptom.name}")

        # 2. Parse Lab Results
        lab_symptoms = self._extract_lab_results(text_lower)
        for sym in lab_symptoms:
            if sym.name not in extracted_names:
                extracted.append(sym)
                extracted_names.add(sym.name)

        # 3. Direct Pattern Matching
        for symptom_name, pattern in self.symptom_patterns.items():
            if symptom_name in extracted_names:
                continue
                
            matches = pattern.findall(text)
            if matches:
                logger.info(f"Direct match found for {symptom_name}: {matches}")
                severity = self._extract_severity(text_lower)
                duration = self._extract_duration(text_lower)
                body_part = self._extract_body_part(text_lower, symptom_name)
                
                symptom = ExtractedSymptom(
                    name=symptom_name,
                    body_part=body_part,
                    severity=severity,
                    duration=duration,
                    confidence=0.9
                )
                extracted.append(symptom)
                extracted_names.add(symptom_name)

        # 4. Fuzzy Matching (if we haven't found much, or to catch typos)
        # We scan the input text against our synonym map
        if not extracted or len(text.split()) < 10: # Only do fuzzy if short text or no matches
            logger.info(f"Attempting fuzzy match for: {text_lower}")
            fuzzy_symptoms = self._fuzzy_symptom_match(text_lower)
            for sym in fuzzy_symptoms:
                if sym.name not in extracted_names:
                    extracted.append(sym)
                    extracted_names.add(sym.name)
        
        logger.info(f"Total extracted symptoms: {len(extracted)}")
        return extracted
    
    def _detect_emergency_intent(self, text: str) -> Optional[ExtractedSymptom]:
        """Detect emergency keywords and return a generic emergency symptom"""
        for keyword in self.emergency_keywords:
            # Simple substring check for now, could be regex
            if keyword in text:
                return ExtractedSymptom(
                    name="emergency_condition", # Special symptom key to handle in analyzer
                    severity="severe",
                    confidence=1.0,
                    duration="acute"
                )
        return None

    def _extract_lab_results(self, text: str) -> List[ExtractedSymptom]:
        """Extract lab results and convert to symptoms if abnormal"""
        symptoms = []
        
        # CBC / WBC
        for pattern in self.lab_patterns['cbc']:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if value > 11000: # High WBC
                    symptoms.append(ExtractedSymptom(name="infection", severity="moderate", confidence=0.95))
                elif value < 4000: # Low WBC
                    symptoms.append(ExtractedSymptom(name="weakness", severity="moderate", confidence=0.95))
        
        # Platelets
        for pattern in self.lab_patterns['platelets']:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if value < 150000:
                    symptoms.append(ExtractedSymptom(name="low_platelets", severity="severe", confidence=0.95))
        
        return symptoms

    def _extract_severity(self, text: str) -> Optional[str]:
        """Extract severity from text"""
        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return severity
        return None
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract duration from text"""
        for pattern in self.duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _extract_body_part(self, text: str, symptom_name: str) -> Optional[str]:
        """Extract body part from text"""
        body_parts = {
            'head': ['head', 'सिर'],
            'stomach': ['stomach', 'belly', 'abdomen', 'पेट'],
            'chest': ['chest', 'छाती'],
            'throat': ['throat', 'गला'],
            'back': ['back', 'पीठ'],
            'leg': ['leg', 'पैर'],
            'arm': ['arm', 'हाथ'],
        }
        for part, keywords in body_parts.items():
            for keyword in keywords:
                if keyword in text:
                    return part
        return None
    
    def _fuzzy_symptom_match(self, text: str) -> List[ExtractedSymptom]:
        """
        Fuzzy matching using Levenshtein distance
        """
        extracted = []
        
        # Split text into chunks/words to match against synonyms
        # This is expensive but effective for short texts
        words = text.split()
        
        # Also try matching the whole phrase if it's short
        candidates = words + [text] if len(words) > 1 else words
        
        for candidate in candidates:
            if len(candidate) < 3: continue # Skip short words
            
            # Find best match in synonym map
            # limit=1 returns top 1 match as list of tuples: [(match, score, index)]
            # process.extractOne returns (match, score) or (match, score, key)
            best_match = process.extractOne(candidate, list(self.symptom_synonyms.keys()), scorer=fuzz.ratio)
            
            if best_match:
                match_term, score = best_match[0], best_match[1]
                if score >= 85: # High threshold to avoid false positives
                    symptom_key = self.symptom_synonyms[match_term]
                    
                    # Avoid duplicates
                    if not any(s.name == symptom_key for s in extracted):
                        extracted.append(ExtractedSymptom(
                            name=symptom_key,
                            confidence=score/100.0,
                            severity='moderate' # Default
                        ))
                        logger.info(f"Fuzzy matched '{candidate}' -> '{symptom_key}' (score: {score})")

        return extracted
    
    def get_symptom_info(self, symptom_name: str, language: str = "en") -> dict:
        """Get detailed information about a symptom"""
        symptom_data = self.knowledge_graph.get('symptoms', {}).get(symptom_name, {})
        if not symptom_data:
            return {}
        return {
            "name": symptom_data.get('translations', {}).get(language, symptom_name),
            "severity_levels": symptom_data.get('severity_levels', []),
            "related_conditions": symptom_data.get('related_conditions', []),
            "urgency_factors": symptom_data.get('urgency_factors', {})
        }
    
    def get_all_symptoms(self) -> List[str]:
        """Get list of all known symptoms"""
        return list(self.knowledge_graph.get('symptoms', {}).keys())


# Global instance
symptom_extractor = SymptomExtractor()
