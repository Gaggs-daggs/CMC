"""
DailyMed API Integration
FDA Drug Labels and Safety Information

- What a drug is used for (indications)
- Warnings & contraindications
- When NOT to use a drug
- Side effects and adverse reactions

API Docs: https://dailymed.nlm.nih.gov/dailymed/webservices-help/v2/spls_api.cfm
"""

import aiohttp
import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

class DailyMedService:
    """
    DailyMed API client for FDA drug safety information
    Official FDA labels - Legal safety layer
    """
    
    BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
    
    # Cache for drug labels
    _label_cache: Dict[str, Any] = {}
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15)
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make async request to DailyMed API"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/{endpoint}"
            
            # DailyMed returns JSON by default
            headers = {"Accept": "application/json"}
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"DailyMed API error: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error("DailyMed API timeout")
            return None
        except Exception as e:
            logger.error(f"DailyMed API error: {e}")
            return None
    
    async def search_drug(self, drug_name: str) -> List[Dict[str, Any]]:
        """
        Search for drug labels by name
        Returns list of matching SPL (Structured Product Labeling) documents
        """
        data = await self._make_request("spls.json", {
            "drug_name": drug_name,
            "pagesize": 5
        })
        
        results = []
        if data and "data" in data:
            for item in data["data"]:
                results.append({
                    "setid": item.get("setid"),
                    "title": item.get("title", ""),
                    "published_date": item.get("published_date"),
                    "labeler": item.get("labeler")
                })
        
        return results
    
    async def get_drug_label(self, setid: str) -> Optional[Dict[str, Any]]:
        """
        Get full drug label by SPL setid
        Parses important safety sections
        """
        cache_key = f"label:{setid}"
        if cache_key in self._label_cache:
            return self._label_cache[cache_key]
        
        data = await self._make_request(f"spls/{setid}.json")
        
        if not data:
            return None
        
        # Parse the structured label
        label = {
            "setid": setid,
            "title": data.get("title", ""),
            "labeler": data.get("labeler", ""),
            "indications": [],
            "warnings": [],
            "contraindications": [],
            "adverse_reactions": [],
            "drug_interactions": [],
            "use_in_pregnancy": None,
            "pediatric_use": None,
            "geriatric_use": None,
            "source": "DailyMed (FDA)"
        }
        
        # Get sections from the label
        sections = data.get("sections", [])
        for section in sections:
            section_name = section.get("name", "").lower()
            section_text = self._clean_text(section.get("text", ""))
            
            if "indication" in section_name or "usage" in section_name:
                label["indications"].append(section_text)
            elif "warning" in section_name:
                label["warnings"].append(section_text)
            elif "contraindication" in section_name:
                label["contraindications"].append(section_text)
            elif "adverse" in section_name or "side effect" in section_name:
                label["adverse_reactions"].append(section_text)
            elif "drug interaction" in section_name:
                label["drug_interactions"].append(section_text)
            elif "pregnancy" in section_name:
                label["use_in_pregnancy"] = section_text
            elif "pediatric" in section_name:
                label["pediatric_use"] = section_text
            elif "geriatric" in section_name:
                label["geriatric_use"] = section_text
        
        self._label_cache[cache_key] = label
        return label
    
    async def get_drug_safety_info(self, drug_name: str) -> Dict[str, Any]:
        """
        Get safety information for a drug
        Main method for safety lookups
        """
        result = {
            "drug_name": drug_name,
            "found": False,
            "indications": [],
            "what_its_for": "",
            "warnings": [],
            "do_not_use_if": [],
            "side_effects": [],
            "interactions_warning": "",
            "pregnancy_warning": "",
            "age_restrictions": {
                "pediatric": None,
                "geriatric": None
            },
            "source": "DailyMed (FDA)",
            "disclaimer": "This is official FDA label information. Always consult a healthcare provider."
        }
        
        # Search for the drug
        search_results = await self.search_drug(drug_name)
        
        if not search_results:
            return result
        
        # Get the first (most relevant) label
        setid = search_results[0].get("setid")
        if not setid:
            return result
        
        label = await self.get_drug_label(setid)
        if not label:
            return result
        
        result["found"] = True
        result["title"] = label.get("title", "")
        
        # Process indications
        if label["indications"]:
            result["indications"] = label["indications"]
            result["what_its_for"] = self._summarize_indications(label["indications"])
        
        # Process warnings
        result["warnings"] = label.get("warnings", [])
        
        # Process contraindications
        result["do_not_use_if"] = self._extract_contraindications(
            label.get("contraindications", [])
        )
        
        # Process side effects
        result["side_effects"] = self._extract_side_effects(
            label.get("adverse_reactions", [])
        )
        
        # Interaction warning
        if label.get("drug_interactions"):
            result["interactions_warning"] = "May interact with other medications. " + \
                self._truncate_text(label["drug_interactions"][0], 200)
        
        # Pregnancy warning
        if label.get("use_in_pregnancy"):
            result["pregnancy_warning"] = self._truncate_text(
                label["use_in_pregnancy"], 150
            )
        
        # Age restrictions
        if label.get("pediatric_use"):
            result["age_restrictions"]["pediatric"] = self._truncate_text(
                label["pediatric_use"], 100
            )
        if label.get("geriatric_use"):
            result["age_restrictions"]["geriatric"] = self._truncate_text(
                label["geriatric_use"], 100
            )
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML/XML tags and excessive whitespace"""
        if not text:
            return ""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _summarize_indications(self, indications: List[str]) -> str:
        """Create a brief summary of what the drug is for"""
        if not indications:
            return ""
        
        full_text = " ".join(indications)
        # Extract first sentence or first 200 chars
        sentences = full_text.split('.')
        if sentences:
            summary = sentences[0].strip()
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary
        return self._truncate_text(full_text, 200)
    
    def _extract_contraindications(self, contraindications: List[str]) -> List[str]:
        """Extract key contraindication points"""
        result = []
        
        for text in contraindications:
            # Look for bullet points or common patterns
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:
                    # Clean and add
                    clean_line = self._truncate_text(line, 150)
                    if clean_line not in result:
                        result.append(clean_line)
                        if len(result) >= 5:  # Max 5 points
                            break
        
        return result
    
    def _extract_side_effects(self, adverse_reactions: List[str]) -> List[str]:
        """Extract common side effects"""
        result = []
        common_effects = [
            "nausea", "vomiting", "diarrhea", "headache", "dizziness",
            "drowsiness", "fatigue", "rash", "itching", "constipation",
            "dry mouth", "insomnia", "anxiety", "stomach pain", "heartburn"
        ]
        
        full_text = " ".join(adverse_reactions).lower()
        
        for effect in common_effects:
            if effect in full_text:
                result.append(effect.title())
                if len(result) >= 8:  # Max 8 side effects
                    break
        
        return result


# Singleton instance
dailymed_service = DailyMedService()
