"""
Medical Data Module
===================
Comprehensive medical and pharmaceutical databases for CMC Health
"""

from .medical_database import DRUG_DATABASE
from .remedies_database import NATURAL_REMEDIES, get_remedies_for_condition

__all__ = ['DRUG_DATABASE', 'NATURAL_REMEDIES', 'get_remedies_for_condition']
