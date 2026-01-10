"""
Enhanced Medicine Service
=========================
Comprehensive medicine enrichment using ALL available databases:

1. WHO ATC Classification - Drug classification system (local, fast)
2. RxNorm (NIH) - Drug normalization, generic/brand names, ingredients
3. DailyMed (FDA) - Safety labels, warnings, contraindications
4. Local Indian Medicine DB - Indian brand names, compositions, prices
5. Remedies Database - Natural remedies and alternatives

This service enriches any medication recommendation with:
- Verified composition from multiple sources
- Official drug classification
- Safety warnings and contraindications
- Alternative medicines
- Indian brand names and prices
- OTC/Prescription status
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import all available database services
try:
    from .medical_databases import (
        drug_info_service,
        rxnorm_service,
        dailymed_service,
        atc_classification,
        is_otc,
        get_drug_class
    )
    HAS_MEDICAL_DATABASES = True
except ImportError as e:
    logger.warning(f"Medical databases not available: {e}")
    HAS_MEDICAL_DATABASES = False

# Import local Indian medicine database
try:
    from .medicine_database import DISEASE_MEDICINE_DB, SYMPTOM_KEYWORDS, match_symptoms_to_diseases
    HAS_LOCAL_DB = True
except ImportError as e:
    logger.warning(f"Local medicine database not available: {e}")
    HAS_LOCAL_DB = False

# Import comprehensive drug database
try:
    from app.data.medical_database import DRUG_DATABASE
    from app.data.remedies_database import get_remedies_for_condition, NATURAL_REMEDIES
    HAS_COMPREHENSIVE_DB = True
except ImportError as e:
    logger.warning(f"Comprehensive drug database not available: {e}")
    HAS_COMPREHENSIVE_DB = False


@dataclass
class EnrichedMedicine:
    """Fully enriched medicine with data from all sources"""
    # Basic info
    name: str
    generic_name: Optional[str] = None
    brand_names: List[str] = field(default_factory=list)
    
    # Composition
    composition: List[Dict] = field(default_factory=list)
    active_ingredients: List[str] = field(default_factory=list)
    
    # Classification
    drug_class: Optional[str] = None
    therapeutic_group: Optional[str] = None
    atc_code: Optional[str] = None
    category: Optional[str] = None
    
    # Dosage & Administration
    dosage: str = ""
    frequency: str = ""
    administration: str = ""
    typical_dosage: str = ""
    
    # Safety
    is_otc: bool = True
    requires_prescription: bool = False
    warnings: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    do_not_use_if: List[str] = field(default_factory=list)
    pregnancy_warning: str = ""
    interactions_warning: str = ""
    
    # Alternatives
    alternatives: List[str] = field(default_factory=list)
    indian_brands: List[str] = field(default_factory=list)
    
    # Pricing (India)
    approximate_price: str = ""
    
    # Metadata
    verified: bool = False
    sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    # Required disclaimer
    disclaimer: str = "Always consult a healthcare provider before taking any medication."
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "generic_name": self.generic_name,
            "brand_names": self.brand_names,
            "composition": self.composition,
            "active_ingredients": self.active_ingredients,
            "drug_class": self.drug_class,
            "therapeutic_group": self.therapeutic_group,
            "atc_code": self.atc_code,
            "category": self.category,
            "dosage": self.dosage or self.typical_dosage,
            "frequency": self.frequency,
            "administration": self.administration,
            "typical_dosage": self.typical_dosage,
            "is_otc": self.is_otc,
            "requires_prescription": self.requires_prescription,
            "warnings": self.warnings,
            "contraindications": self.contraindications,
            "side_effects": self.side_effects,
            "do_not_use_if": self.do_not_use_if,
            "pregnancy_warning": self.pregnancy_warning,
            "interactions_warning": self.interactions_warning,
            "alternatives": self.alternatives,
            "indian_brands": self.indian_brands,
            "approximate_price": self.approximate_price,
            "verified": self.verified,
            "sources": self.sources,
            "confidence_score": self.confidence_score,
            "disclaimer": self.disclaimer
        }


class EnhancedMedicineService:
    """
    Enhanced medicine service that combines ALL available databases
    to provide comprehensive, verified medicine information.
    """
    
    def __init__(self):
        self._cache: Dict[str, EnrichedMedicine] = {}
        self._indian_medicine_index: Dict[str, Dict] = {}
        self._build_indian_medicine_index()
        
        # Log available databases
        available = []
        if HAS_MEDICAL_DATABASES:
            available.append("RxNorm/DailyMed/ATC")
        if HAS_LOCAL_DB:
            available.append("Indian Medicine DB")
        if HAS_COMPREHENSIVE_DB:
            available.append("Comprehensive Drug DB")
        
        logger.info(f"🏥 Enhanced Medicine Service initialized with: {', '.join(available)}")
    
    def _build_indian_medicine_index(self):
        """Build an index of Indian medicines for fast lookup"""
        if not HAS_LOCAL_DB:
            return
        
        for disease, data in DISEASE_MEDICINE_DB.items():
            for medicine in data.get("medicines", []):
                # Index by brand name
                brand_name = medicine.get("brand_name", "").lower()
                if brand_name:
                    self._indian_medicine_index[brand_name] = medicine
                
                # Index by generic name
                generic_name = medicine.get("generic_name", "").lower()
                if generic_name:
                    self._indian_medicine_index[generic_name] = medicine
                
                # Index by individual ingredients
                for comp in medicine.get("composition", []):
                    ingredient = comp.get("ingredient", "").lower()
                    if ingredient and ingredient not in self._indian_medicine_index:
                        self._indian_medicine_index[ingredient] = medicine
    
    def _find_in_indian_db(self, drug_name: str) -> Optional[Dict]:
        """Find medicine in Indian database"""
        if not HAS_LOCAL_DB:
            return None
        
        drug_lower = drug_name.lower().strip()
        
        # Direct lookup
        if drug_lower in self._indian_medicine_index:
            return self._indian_medicine_index[drug_lower]
        
        # Partial match
        for key, medicine in self._indian_medicine_index.items():
            if drug_lower in key or key in drug_lower:
                return medicine
        
        return None
    
    def _find_in_comprehensive_db(self, drug_name: str, symptom: str = None) -> Optional[Dict]:
        """Find medicine in comprehensive drug database"""
        if not HAS_COMPREHENSIVE_DB:
            return None
        
        drug_lower = drug_name.lower().strip()
        
        for category, subcategories in DRUG_DATABASE.items():
            if isinstance(subcategories, dict):
                for subcat, drugs in subcategories.items():
                    if isinstance(drugs, list):
                        for drug in drugs:
                            if drug.get("name", "").lower() == drug_lower:
                                return drug
            elif isinstance(subcategories, list):
                for drug in subcategories:
                    if drug.get("name", "").lower() == drug_lower:
                        return drug
        
        return None
    
    async def enrich_medicine(
        self,
        medicine: Dict[str, Any],
        include_safety: bool = True,
        user_allergies: List[str] = None
    ) -> EnrichedMedicine:
        """
        Enrich a single medicine with data from all available databases.
        
        Args:
            medicine: Basic medicine dict with at least 'name' field
            include_safety: Whether to fetch FDA safety info (slower)
            user_allergies: List of user's known allergies for warnings
        
        Returns:
            EnrichedMedicine with comprehensive information
        """
        drug_name = medicine.get("name", "")
        if not drug_name:
            return EnrichedMedicine(name="Unknown")
        
        # Check cache
        cache_key = f"{drug_name.lower()}:{include_safety}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # Add allergy warnings if applicable
            if user_allergies:
                cached = self._add_allergy_warnings(cached, user_allergies)
            return cached
        
        # Start with basic info from input
        enriched = EnrichedMedicine(
            name=drug_name,
            dosage=medicine.get("dosage", ""),
            frequency=medicine.get("frequency", ""),
            warnings=[medicine.get("warning", "")] if medicine.get("warning") else []
        )
        
        sources = []
        
        # ========== SOURCE 1: Indian Medicine Database (Local, Fast) ==========
        indian_data = self._find_in_indian_db(drug_name)
        if indian_data:
            enriched.generic_name = indian_data.get("generic_name")
            enriched.composition = indian_data.get("composition", [])
            enriched.active_ingredients = [c.get("ingredient", "") for c in enriched.composition]
            enriched.drug_class = indian_data.get("drug_class")
            enriched.typical_dosage = indian_data.get("typical_dosage", "")
            enriched.administration = indian_data.get("administration", "")
            enriched.side_effects = indian_data.get("common_side_effects", [])
            enriched.contraindications = indian_data.get("contraindications", [])
            enriched.alternatives = indian_data.get("alternatives", [])
            enriched.approximate_price = indian_data.get("approximate_price", "")
            enriched.is_otc = indian_data.get("otc_status", "OTC") == "OTC"
            enriched.requires_prescription = not enriched.is_otc
            enriched.indian_brands = indian_data.get("alternatives", [])
            sources.append("Indian Medicine DB")
            enriched.verified = True
        
        # ========== SOURCE 2: Comprehensive Drug Database (Local, Fast) ==========
        comp_data = self._find_in_comprehensive_db(drug_name)
        if comp_data:
            if not enriched.drug_class:
                enriched.drug_class = comp_data.get("category", "")
            if not enriched.dosage:
                enriched.dosage = comp_data.get("dosage", "")
            if not enriched.warnings:
                enriched.warnings = [comp_data.get("warning", "")] if comp_data.get("warning") else []
            if not enriched.frequency:
                enriched.frequency = comp_data.get("frequency", "")
            sources.append("Comprehensive Drug DB")
            enriched.verified = True
        
        # ========== SOURCE 3: WHO ATC Classification (Local, Fast) ==========
        if HAS_MEDICAL_DATABASES:
            try:
                atc_info = atc_classification.classify_drug(drug_name)
                if atc_info:
                    enriched.atc_code = atc_info.get("atc_code")
                    if not enriched.drug_class:
                        enriched.drug_class = atc_info.get("classification")
                    enriched.therapeutic_group = atc_info.get("therapeutic_group")
                    enriched.category = atc_info.get("category")
                    
                    # Override OTC status with official classification
                    if atc_info.get("otc") is not None:
                        enriched.is_otc = atc_info.get("otc")
                        enriched.requires_prescription = not enriched.is_otc
                    
                    sources.append("WHO ATC/DDD")
                    enriched.verified = True
            except Exception as e:
                logger.warning(f"ATC lookup failed for {drug_name}: {e}")
        
        # ========== SOURCE 4: RxNorm (NIH) - API Call ==========
        if HAS_MEDICAL_DATABASES:
            try:
                rxnorm_info = await rxnorm_service.get_drug_info(drug_name)
                if rxnorm_info and rxnorm_info.get("rxcui"):
                    if not enriched.generic_name:
                        enriched.generic_name = rxnorm_info.get("generic_name")
                    if rxnorm_info.get("brand_names"):
                        enriched.brand_names = rxnorm_info.get("brand_names", [])
                    if rxnorm_info.get("ingredients"):
                        for ingredient in rxnorm_info.get("ingredients", []):
                            if ingredient not in enriched.active_ingredients:
                                enriched.active_ingredients.append(ingredient)
                    sources.append("RxNorm (NIH)")
                    enriched.verified = True
            except Exception as e:
                logger.warning(f"RxNorm lookup failed for {drug_name}: {e}")
        
        # ========== SOURCE 5: DailyMed (FDA) - API Call (Safety Info) ==========
        if HAS_MEDICAL_DATABASES and include_safety:
            try:
                safety_info = await dailymed_service.get_drug_safety_info(drug_name)
                if safety_info and safety_info.get("found"):
                    # Merge warnings
                    for warning in safety_info.get("warnings", []):
                        if warning and warning not in enriched.warnings:
                            enriched.warnings.append(warning)
                    
                    # Merge contraindications
                    for contra in safety_info.get("do_not_use_if", []):
                        if contra and contra not in enriched.contraindications:
                            enriched.contraindications.append(contra)
                    
                    # Merge side effects
                    for effect in safety_info.get("side_effects", []):
                        if effect and effect not in enriched.side_effects:
                            enriched.side_effects.append(effect)
                    
                    enriched.do_not_use_if = safety_info.get("do_not_use_if", [])
                    enriched.pregnancy_warning = safety_info.get("pregnancy_warning", "")
                    enriched.interactions_warning = safety_info.get("interactions_warning", "")
                    
                    sources.append("DailyMed (FDA)")
                    enriched.verified = True
            except Exception as e:
                logger.warning(f"DailyMed lookup failed for {drug_name}: {e}")
        
        # ========== Calculate Confidence Score ==========
        enriched.sources = sources
        enriched.confidence_score = min(1.0, len(sources) * 0.25)  # 0.25 per source, max 1.0
        
        # ========== Add Allergy Warnings ==========
        if user_allergies:
            enriched = self._add_allergy_warnings(enriched, user_allergies)
        
        # Cache the result
        self._cache[cache_key] = enriched
        
        logger.info(f"💊 Enriched {drug_name}: {len(sources)} sources, confidence={enriched.confidence_score}")
        
        return enriched
    
    def _add_allergy_warnings(
        self,
        medicine: EnrichedMedicine,
        user_allergies: List[str]
    ) -> EnrichedMedicine:
        """Add warnings if medicine matches user allergies"""
        if not user_allergies:
            return medicine
        
        allergens_lower = [a.lower() for a in user_allergies]
        
        # Check medicine name
        name_lower = medicine.name.lower()
        for allergen in allergens_lower:
            if allergen in name_lower:
                warning = f"⚠️ ALLERGY WARNING: This medication contains or is related to {allergen}"
                if warning not in medicine.warnings:
                    medicine.warnings.insert(0, warning)
        
        # Check ingredients
        for ingredient in medicine.active_ingredients:
            ingredient_lower = ingredient.lower()
            for allergen in allergens_lower:
                if allergen in ingredient_lower:
                    warning = f"⚠️ ALLERGY WARNING: Contains {ingredient} - you may be allergic"
                    if warning not in medicine.warnings:
                        medicine.warnings.insert(0, warning)
        
        # Check drug class for common allergies
        if medicine.drug_class:
            class_lower = medicine.drug_class.lower()
            allergy_classes = {
                "nsaid": ["aspirin", "ibuprofen", "nsaid"],
                "penicillin": ["penicillin", "amoxicillin", "ampicillin"],
                "sulfa": ["sulfa", "sulfonamide", "sulfamethoxazole"],
                "antibiotic": ["antibiotic", "penicillin", "amoxicillin"]
            }
            
            for drug_class, related_allergens in allergy_classes.items():
                if drug_class in class_lower:
                    for allergen in related_allergens:
                        if allergen in allergens_lower:
                            warning = f"⚠️ ALLERGY WARNING: You have a {allergen} allergy - this is a {medicine.drug_class}"
                            if warning not in medicine.warnings:
                                medicine.warnings.insert(0, warning)
        
        return medicine
    
    async def enrich_medications_batch(
        self,
        medications: List[Dict[str, Any]],
        include_safety: bool = True,
        user_allergies: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Enrich multiple medications in parallel.
        
        Args:
            medications: List of medication dicts
            include_safety: Whether to include FDA safety info
            user_allergies: User's known allergies
        
        Returns:
            List of enriched medication dicts
        """
        if not medications:
            return []
        
        # Enrich all medications in parallel
        tasks = [
            self.enrich_medicine(med, include_safety, user_allergies)
            for med in medications
        ]
        
        enriched_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert to dicts, handling any exceptions
        results = []
        for i, enriched in enumerate(enriched_list):
            if isinstance(enriched, Exception):
                logger.error(f"Error enriching medication {i}: {enriched}")
                # Return original with minimal enrichment
                results.append({
                    **medications[i],
                    "verified": False,
                    "sources": [],
                    "disclaimer": "Always consult a healthcare provider."
                })
            else:
                results.append(enriched.to_dict())
        
        return results
    
    def get_medicines_for_symptoms(
        self,
        symptoms: List[str],
        max_per_symptom: int = 2,
        user_allergies: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get medicines for symptoms from local databases (fast, synchronous).
        Use this for quick lookups without API calls.
        
        Args:
            symptoms: List of symptoms
            max_per_symptom: Maximum medicines per symptom
            user_allergies: User's known allergies to filter
        
        Returns:
            List of medicine dicts
        """
        medicines = []
        seen_names = set()
        allergens_lower = [a.lower() for a in (user_allergies or [])]
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # Search Indian medicine database
            if HAS_LOCAL_DB:
                matches = match_symptoms_to_diseases([symptom])
                for match in matches[:2]:
                    for med in match.get("data", {}).get("medicines", [])[:max_per_symptom]:
                        if med.get("brand_name") not in seen_names:
                            # Check for allergens
                            is_safe = True
                            for allergen in allergens_lower:
                                if allergen in med.get("generic_name", "").lower():
                                    is_safe = False
                                    break
                            
                            if is_safe:
                                medicines.append({
                                    "name": med.get("brand_name"),
                                    "generic_name": med.get("generic_name"),
                                    "composition": med.get("composition"),
                                    "dosage": med.get("typical_dosage"),
                                    "drug_class": med.get("drug_class"),
                                    "is_otc": med.get("otc_status") == "OTC",
                                    "side_effects": med.get("common_side_effects"),
                                    "contraindications": med.get("contraindications"),
                                    "alternatives": med.get("alternatives"),
                                    "approximate_price": med.get("approximate_price"),
                                    "source": "Indian Medicine DB",
                                    "for_symptom": symptom
                                })
                                seen_names.add(med.get("brand_name"))
            
            # Add natural remedies
            if HAS_COMPREHENSIVE_DB:
                try:
                    remedies = get_remedies_for_condition(symptom_lower, max_remedies=1)
                    for remedy in remedies:
                        if remedy.get("name") not in seen_names:
                            medicines.append({
                                **remedy,
                                "is_natural": True,
                                "for_symptom": symptom
                            })
                            seen_names.add(remedy.get("name"))
                except:
                    pass
        
        return medicines
    
    def get_alternatives(self, drug_name: str) -> List[str]:
        """Get alternative medicines for a drug (fast, local lookup)"""
        alternatives = []
        
        # Check Indian database
        indian_data = self._find_in_indian_db(drug_name)
        if indian_data:
            alternatives.extend(indian_data.get("alternatives", []))
        
        # Check comprehensive database
        comp_data = self._find_in_comprehensive_db(drug_name)
        if comp_data:
            # Look for similar drugs in same category
            pass
        
        return list(set(alternatives))
    
    async def close(self):
        """Close API connections"""
        if HAS_MEDICAL_DATABASES:
            await rxnorm_service.close()
            await dailymed_service.close()


# Singleton instance
enhanced_medicine_service = EnhancedMedicineService()


# Convenience functions
async def enrich_medicine(medicine: Dict, include_safety: bool = True) -> Dict:
    """Enrich a single medicine with all available data"""
    enriched = await enhanced_medicine_service.enrich_medicine(medicine, include_safety)
    return enriched.to_dict()


async def enrich_medications(medications: List[Dict], include_safety: bool = True) -> List[Dict]:
    """Enrich multiple medications"""
    return await enhanced_medicine_service.enrich_medications_batch(medications, include_safety)


def get_quick_medicines(symptoms: List[str], user_allergies: List[str] = None) -> List[Dict]:
    """Quick lookup of medicines for symptoms (no API calls)"""
    return enhanced_medicine_service.get_medicines_for_symptoms(symptoms, user_allergies=user_allergies)
