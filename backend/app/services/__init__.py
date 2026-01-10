"""
Services Package
================
Core AI and medical services for the health assistant.

Main Services:
- ai_orchestrator: Production AI orchestrator with RAG, safety, triage
- enhanced_medicine_service: Comprehensive drug enrichment using ALL databases
- medical_databases: RxNorm, DailyMed, WHO ATC integrations
- gemini_medicine_service: Gemini-powered medicine recommendations
"""

# Import convenience functions for enhanced medicine
try:
    from .enhanced_medicine_service import (
        enhanced_medicine_service,
        enrich_medicine,
        enrich_medications,
        get_quick_medicines
    )
except ImportError:
    pass
