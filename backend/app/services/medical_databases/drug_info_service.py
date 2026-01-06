"""
DrugInfo Service - Main Entry Point
Combines RxNorm, DailyMed, and ATC classification

This is the PRIMARY service for drug information in the app.
It safely combines data from multiple official sources.

SAFETY RULES (DO NOT VIOLATE):
1. NEVER provide dosage information
2. NEVER prescribe Rx drugs - always say "prescription required"
3. NEVER say a drug "will cure" anything
4. NEVER replace professional medical advice
5. ALWAYS include disclaimer
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .rxnorm_service import rxnorm_service, RxNormService
from .dailymed_service import dailymed_service, DailyMedService
from .atc_classification import atc_classification, ATCClassification

logger = logging.getLogger(__name__)


@dataclass
class DrugInformation:
    """Structured drug information result"""
    drug_name: str
    generic_name: Optional[str] = None
    brand_names: List[str] = field(default_factory=list)
    
    # Classification
    drug_class: Optional[str] = None
    category: Optional[str] = None
    atc_code: Optional[str] = None
    anatomical_target: Optional[str] = None
    
    # What it's for
    indications: List[str] = field(default_factory=list)
    what_its_for: str = ""
    
    # Safety information
    is_otc: Optional[bool] = None
    warnings: List[str] = field(default_factory=list)
    do_not_use_if: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    interactions_warning: str = ""
    pregnancy_warning: str = ""
    
    # Metadata
    sources: List[str] = field(default_factory=list)
    found: bool = False
    
    # Required disclaimers
    disclaimer: str = "This is general drug information only. Always consult a healthcare provider before taking any medication."
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "drug_name": self.drug_name,
            "generic_name": self.generic_name,
            "brand_names": self.brand_names,
            "drug_class": self.drug_class,
            "category": self.category,
            "atc_code": self.atc_code,
            "anatomical_target": self.anatomical_target,
            "indications": self.indications,
            "what_its_for": self.what_its_for,
            "is_otc": self.is_otc,
            "requires_prescription": not self.is_otc if self.is_otc is not None else None,
            "warnings": self.warnings,
            "do_not_use_if": self.do_not_use_if,
            "side_effects": self.side_effects,
            "interactions_warning": self.interactions_warning,
            "pregnancy_warning": self.pregnancy_warning,
            "sources": self.sources,
            "found": self.found,
            "disclaimer": self.disclaimer
        }


class DrugInfoService:
    """
    Main Drug Information Service
    
    Combines:
    - RxNorm (NIH) - Drug normalization and identification
    - DailyMed (FDA) - Safety labels and warnings
    - WHO ATC - Drug classification
    
    Use this service for all drug information lookups.
    """
    
    def __init__(self):
        self.rxnorm = rxnorm_service
        self.dailymed = dailymed_service
        self.atc = atc_classification
        
        # Cache for combined lookups
        self._cache: Dict[str, DrugInformation] = {}
    
    async def get_drug_info(self, drug_name: str, include_safety: bool = True) -> DrugInformation:
        """
        Get comprehensive drug information
        
        Args:
            drug_name: Name of the drug (brand or generic)
            include_safety: Whether to fetch FDA safety info (slower)
        
        Returns:
            DrugInformation object with all available data
        """
        # Check cache
        cache_key = f"{drug_name.lower()}:{include_safety}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = DrugInformation(drug_name=drug_name)
        
        try:
            # Parallel lookup from all sources
            tasks = [
                self._get_rxnorm_info(drug_name),
                self._get_atc_info(drug_name),
            ]
            
            if include_safety:
                tasks.append(self._get_dailymed_info(drug_name))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process RxNorm results
            rxnorm_data = results[0] if not isinstance(results[0], Exception) else None
            atc_data = results[1] if not isinstance(results[1], Exception) else None
            dailymed_data = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None
            
            # Merge data
            if rxnorm_data:
                result.found = True
                result.generic_name = rxnorm_data.get("generic_name")
                result.brand_names = rxnorm_data.get("brand_names", [])
                result.sources.append("RxNorm (NIH)")
            
            if atc_data:
                result.found = True
                result.drug_class = atc_data.get("classification")
                result.category = atc_data.get("category")
                result.atc_code = atc_data.get("atc_code")
                result.anatomical_target = atc_data.get("anatomical_target")
                result.is_otc = atc_data.get("otc")
                result.sources.append("WHO ATC/DDD")
            
            if dailymed_data and dailymed_data.get("found"):
                result.found = True
                result.what_its_for = dailymed_data.get("what_its_for", "")
                result.indications = dailymed_data.get("indications", [])
                result.warnings = dailymed_data.get("warnings", [])
                result.do_not_use_if = dailymed_data.get("do_not_use_if", [])
                result.side_effects = dailymed_data.get("side_effects", [])
                result.interactions_warning = dailymed_data.get("interactions_warning", "")
                result.pregnancy_warning = dailymed_data.get("pregnancy_warning", "")
                result.sources.append("DailyMed (FDA)")
            
            # Cache result
            self._cache[cache_key] = result
            
        except Exception as e:
            logger.error(f"Error getting drug info for {drug_name}: {e}")
        
        return result
    
    async def _get_rxnorm_info(self, drug_name: str) -> Optional[Dict]:
        """Get data from RxNorm"""
        try:
            return await self.rxnorm.get_drug_info(drug_name)
        except Exception as e:
            logger.warning(f"RxNorm lookup failed for {drug_name}: {e}")
            return None
    
    async def _get_atc_info(self, drug_name: str) -> Optional[Dict]:
        """Get data from ATC classification"""
        try:
            return self.atc.classify_drug(drug_name)
        except Exception as e:
            logger.warning(f"ATC lookup failed for {drug_name}: {e}")
            return None
    
    async def _get_dailymed_info(self, drug_name: str) -> Optional[Dict]:
        """Get safety data from DailyMed"""
        try:
            return await self.dailymed.get_drug_safety_info(drug_name)
        except Exception as e:
            logger.warning(f"DailyMed lookup failed for {drug_name}: {e}")
            return None
    
    async def get_drug_summary(self, drug_name: str) -> Dict[str, Any]:
        """
        Get a brief summary of a drug
        Suitable for display in UI
        """
        info = await self.get_drug_info(drug_name, include_safety=False)
        
        summary = {
            "name": drug_name,
            "found": info.found,
            "generic_name": info.generic_name,
            "drug_class": info.drug_class or info.category,
            "is_otc": info.is_otc,
            "requires_prescription": not info.is_otc if info.is_otc is not None else None,
            "disclaimer": "Consult a healthcare provider before use."
        }
        
        return summary
    
    async def get_drug_safety(self, drug_name: str) -> Dict[str, Any]:
        """
        Get only safety information for a drug
        For displaying warnings
        """
        info = await self.get_drug_info(drug_name, include_safety=True)
        
        safety = {
            "name": drug_name,
            "found": info.found,
            "warnings": info.warnings[:3],  # Top 3 warnings
            "do_not_use_if": info.do_not_use_if[:3],  # Top 3 contraindications
            "side_effects": info.side_effects[:5],  # Top 5 side effects
            "pregnancy_warning": info.pregnancy_warning,
            "requires_prescription": not info.is_otc if info.is_otc is not None else None,
            "disclaimer": info.disclaimer
        }
        
        return safety
    
    async def search_drugs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for drugs by name
        Returns list of matching drugs with basic info
        """
        results = []
        
        # Search RxNorm
        try:
            rxnorm_results = await self.rxnorm.search_drugs(query)
            for drug in rxnorm_results[:limit]:
                atc_info = self.atc.classify_drug(drug.get("name", ""))
                results.append({
                    "name": drug.get("name"),
                    "rxcui": drug.get("rxcui"),
                    "drug_class": atc_info.get("classification") if atc_info else None,
                    "is_otc": atc_info.get("otc") if atc_info else None
                })
        except Exception as e:
            logger.warning(f"Drug search failed: {e}")
        
        return results
    
    def is_otc(self, drug_name: str) -> Optional[bool]:
        """
        Quick check if a drug is OTC
        Uses local ATC database (no API call)
        """
        return self.atc.is_otc(drug_name)
    
    def get_drug_class(self, drug_name: str) -> Optional[str]:
        """
        Quick lookup of drug class
        Uses local ATC database (no API call)
        """
        info = self.atc.classify_drug(drug_name)
        if info:
            return info.get("classification") or info.get("drug_class")
        return None
    
    async def enrich_medication(self, medication: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a medication dict with official database info
        Used by the AI service to add verified info to recommendations
        """
        drug_name = medication.get("name", "")
        
        # Get classification (fast, local)
        atc_info = self.atc.classify_drug(drug_name)
        
        if atc_info:
            medication["verified"] = True
            medication["drug_class"] = atc_info.get("classification")
            medication["atc_code"] = atc_info.get("atc_code")
            medication["is_otc"] = atc_info.get("otc")
            medication["requires_prescription"] = not atc_info.get("otc", True)
            medication["source"] = "WHO ATC/DDD"
        else:
            medication["verified"] = False
        
        # Add disclaimer
        medication["disclaimer"] = "Always consult a healthcare provider."
        
        return medication
    
    async def enrich_medications_batch(self, medications: List[Dict]) -> List[Dict]:
        """
        Enrich multiple medications at once
        """
        return [await self.enrich_medication(med) for med in medications]
    
    async def close(self):
        """Close all API connections"""
        await self.rxnorm.close()
        await self.dailymed.close()


# Singleton instance
drug_info_service = DrugInfoService()


# Convenience functions for direct use
async def get_drug_info(drug_name: str) -> Dict[str, Any]:
    """Get comprehensive drug information"""
    info = await drug_info_service.get_drug_info(drug_name)
    return info.to_dict()


async def get_drug_safety(drug_name: str) -> Dict[str, Any]:
    """Get drug safety information"""
    return await drug_info_service.get_drug_safety(drug_name)


def is_otc(drug_name: str) -> Optional[bool]:
    """Check if drug is OTC (fast, local lookup)"""
    return drug_info_service.is_otc(drug_name)


def get_drug_class(drug_name: str) -> Optional[str]:
    """Get drug classification (fast, local lookup)"""
    return drug_info_service.get_drug_class(drug_name)
