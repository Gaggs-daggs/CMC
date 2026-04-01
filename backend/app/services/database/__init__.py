"""
Database Services Module
PostgreSQL integration for CMC Health
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .postgres_config import db_config
    from .postgres_profile_service import postgres_profile_service
except Exception as e:
    logger.warning(f"⚠️ PostgreSQL services unavailable: {e}")
    db_config = None
    postgres_profile_service = None

__all__ = ['db_config', 'postgres_profile_service']
