"""
RxNorm API Integration
National Library of Medicine (NIH) drug database
- Drug name normalization (generic ↔ brand)
- Ingredient lookup
- Drug concept identification
- Avoiding duplicate medications

API Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Optional
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

class RxNormService:
    """
    RxNorm API client for drug normalization
    FREE, Hospital Standard, AI-Safe
    """
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    # Cache for frequently accessed drugs
    _drug_cache: Dict[str, Any] = {}
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make async request to RxNorm API"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/{endpoint}"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"RxNorm API error: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error("RxNorm API timeout")
            return None
        except Exception as e:
            logger.error(f"RxNorm API error: {e}")
            return None
    
    async def get_rxcui(self, drug_name: str) -> Optional[str]:
        """
        Get RxCUI (RxNorm Concept Unique Identifier) for a drug name
        This is the backbone ID for cross-referencing
        """
        # Check cache first
        cache_key = f"rxcui:{drug_name.lower()}"
        if cache_key in self._drug_cache:
            return self._drug_cache[cache_key]
        
        data = await self._make_request("rxcui.json", {"name": drug_name})
        
        if data and "idGroup" in data:
            rxcui_list = data["idGroup"].get("rxnormId", [])
            if rxcui_list:
                rxcui = rxcui_list[0]
                self._drug_cache[cache_key] = rxcui
                return rxcui
        return None
    
    async def get_drug_info(self, drug_name: str) -> Dict[str, Any]:
        """
        Get comprehensive drug information from RxNorm
        Returns: generic name, brand names, ingredients, drug class
        """
        result = {
            "query": drug_name,
            "rxcui": None,
            "generic_name": None,
            "brand_names": [],
            "ingredients": [],
            "drug_class": None,
            "normalized_name": None,
            "is_otc": None,
            "source": "RxNorm (NIH)"
        }
        
        # First get the RxCUI
        rxcui = await self.get_rxcui(drug_name)
        if not rxcui:
            # Try approximate match
            rxcui = await self._approximate_match(drug_name)
        
        if not rxcui:
            return result
        
        result["rxcui"] = rxcui
        
        # Get all properties
        properties = await self._get_all_properties(rxcui)
        if properties:
            result.update(properties)
        
        # Get related drugs (brand/generic)
        related = await self._get_related_drugs(rxcui)
        if related:
            result["brand_names"] = related.get("brands", [])
            if related.get("generic"):
                result["generic_name"] = related["generic"]
        
        # Get ingredients
        ingredients = await self._get_ingredients(rxcui)
        if ingredients:
            result["ingredients"] = ingredients
        
        return result
    
    async def _approximate_match(self, drug_name: str) -> Optional[str]:
        """Use approximate matching for misspelled drug names"""
        data = await self._make_request("approximateTerm.json", {
            "term": drug_name,
            "maxEntries": 1
        })
        
        if data and "approximateGroup" in data:
            candidates = data["approximateGroup"].get("candidate", [])
            if candidates:
                return candidates[0].get("rxcui")
        return None
    
    async def _get_all_properties(self, rxcui: str) -> Dict[str, Any]:
        """Get all properties for a drug concept"""
        data = await self._make_request(f"rxcui/{rxcui}/allProperties.json", {
            "prop": "all"
        })
        
        result = {}
        if data and "propConceptGroup" in data:
            for group in data["propConceptGroup"].get("propConcept", []):
                prop_name = group.get("propName", "")
                prop_value = group.get("propValue", "")
                
                if prop_name == "RxNorm Name":
                    result["normalized_name"] = prop_value
                elif prop_name == "TTY":
                    result["term_type"] = prop_value
        
        return result
    
    async def _get_related_drugs(self, rxcui: str) -> Dict[str, Any]:
        """Get related brand and generic names"""
        data = await self._make_request(f"rxcui/{rxcui}/related.json", {
            "tty": "BN+IN+MIN+PIN+SBD+SCD"  # Brand names, ingredients, etc.
        })
        
        result = {"brands": [], "generic": None}
        
        if data and "relatedGroup" in data:
            for concept_group in data["relatedGroup"].get("conceptGroup", []):
                tty = concept_group.get("tty", "")
                concepts = concept_group.get("conceptProperties", [])
                
                for concept in concepts:
                    name = concept.get("name", "")
                    if tty == "BN":  # Brand Name
                        result["brands"].append(name)
                    elif tty == "IN":  # Ingredient
                        result["generic"] = name
        
        return result
    
    async def _get_ingredients(self, rxcui: str) -> List[str]:
        """Get active ingredients"""
        data = await self._make_request(f"rxcui/{rxcui}/related.json", {
            "tty": "IN+MIN+PIN"  # Ingredients
        })
        
        ingredients = []
        if data and "relatedGroup" in data:
            for concept_group in data["relatedGroup"].get("conceptGroup", []):
                concepts = concept_group.get("conceptProperties", [])
                for concept in concepts:
                    name = concept.get("name", "")
                    if name and name not in ingredients:
                        ingredients.append(name)
        
        return ingredients
    
    async def check_drug_interaction(self, drug_list: List[str]) -> Dict[str, Any]:
        """
        Check for potential drug interactions
        Returns interaction severity and description
        """
        result = {
            "has_interactions": False,
            "interactions": [],
            "severity": "none",
            "disclaimer": "Consult a healthcare provider for complete interaction analysis"
        }
        
        # Get RxCUIs for all drugs
        rxcuis = []
        for drug in drug_list:
            rxcui = await self.get_rxcui(drug)
            if rxcui:
                rxcuis.append(rxcui)
        
        if len(rxcuis) < 2:
            return result
        
        # Check interactions
        rxcui_string = "+".join(rxcuis)
        data = await self._make_request(f"interaction/list.json", {
            "rxcuis": rxcui_string
        })
        
        if data and "fullInteractionTypeGroup" in data:
            for group in data["fullInteractionTypeGroup"]:
                for interaction_type in group.get("fullInteractionType", []):
                    for pair in interaction_type.get("interactionPair", []):
                        result["has_interactions"] = True
                        result["interactions"].append({
                            "drugs": [c.get("minConceptItem", {}).get("name") 
                                     for c in pair.get("interactionConcept", [])],
                            "description": pair.get("description", ""),
                            "severity": pair.get("severity", "unknown")
                        })
                        
                        # Update overall severity
                        sev = pair.get("severity", "").lower()
                        if "high" in sev or "severe" in sev:
                            result["severity"] = "high"
                        elif "moderate" in sev and result["severity"] != "high":
                            result["severity"] = "moderate"
        
        return result
    
    async def normalize_drug_name(self, drug_name: str) -> str:
        """
        Normalize drug name to standard RxNorm name
        Useful for deduplication and consistency
        """
        info = await self.get_drug_info(drug_name)
        return info.get("normalized_name") or info.get("generic_name") or drug_name
    
    async def search_drugs(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for drugs by partial name
        Returns list of matching drugs with RxCUI
        """
        data = await self._make_request("drugs.json", {"name": query})
        
        results = []
        if data and "drugGroup" in data:
            for concept_group in data["drugGroup"].get("conceptGroup", []):
                concepts = concept_group.get("conceptProperties", [])
                for concept in concepts[:limit]:
                    results.append({
                        "rxcui": concept.get("rxcui"),
                        "name": concept.get("name"),
                        "synonym": concept.get("synonym", "")
                    })
        
        return results[:limit]


# Singleton instance
rxnorm_service = RxNormService()
