"""
Medical Database Integrations
- RxNorm: Drug name normalization (NIH)
- DailyMed: FDA drug labels and safety info
- WHO ATC: Drug classification system

Usage:
    from app.services.medical_databases import drug_info_service
    
    # Get comprehensive drug info
    info = await drug_info_service.get_drug_info("ibuprofen")
    
    # Quick checks (no API call)
    is_otc = drug_info_service.is_otc("ibuprofen")  # True
    drug_class = drug_info_service.get_drug_class("ibuprofen")  # "NSAID"
"""

from .rxnorm_service import RxNormService, rxnorm_service
from .dailymed_service import DailyMedService, dailymed_service
from .atc_classification import ATCClassification, atc_classification
from .drug_info_service import (
    DrugInfoService, 
    drug_info_service,
    DrugInformation,
    get_drug_info,
    get_drug_safety,
    is_otc,
    get_drug_class
)

__all__ = [
    # Main service (use this)
    "DrugInfoService",
    "drug_info_service",
    "DrugInformation",
    
    # Convenience functions
    "get_drug_info",
    "get_drug_safety",
    "is_otc",
    "get_drug_class",
    
    # Individual services (advanced use)
    "RxNormService",
    "rxnorm_service",
    "DailyMedService", 
    "dailymed_service",
    "ATCClassification",
    "atc_classification",
]

