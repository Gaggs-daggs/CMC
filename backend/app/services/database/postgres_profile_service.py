"""
PostgreSQL Profile Service
Persistent storage for user profiles using PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
import uuid

from .postgres_config import db_config
from .schema import SCHEMA_SQL, ALLERGENS_DATA, CONDITIONS_DATA, MEDICATIONS_DATA

logger = logging.getLogger(__name__)


class PostgresProfileService:
    """
    PostgreSQL-based profile service for persistent user data storage
    """
    
    def __init__(self):
        self.connection_string = db_config.connection_string
        self._initialized = False
        self._init_database()
    
    def _get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(
            host=db_config.host,
            port=db_config.port,
            database=db_config.database,
            user=db_config.user,
            password=db_config.password
        )
    
    def _init_database(self):
        """Initialize database schema and seed data"""
        if self._initialized:
            return
            
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Create schema
            cur.execute(SCHEMA_SQL)
            conn.commit()
            logger.info("✅ Database schema created/verified")
            
            # Seed allergens data
            try:
                cur.execute(ALLERGENS_DATA)
                conn.commit()
                logger.info("✅ Allergens data seeded")
            except Exception as e:
                conn.rollback()
                logger.debug(f"Allergens data may already exist: {e}")
            
            # Seed conditions data
            try:
                cur.execute(CONDITIONS_DATA)
                conn.commit()
                logger.info("✅ Medical conditions data seeded")
            except Exception as e:
                conn.rollback()
                logger.debug(f"Conditions data may already exist: {e}")
            
            # Seed medications data
            try:
                cur.execute(MEDICATIONS_DATA)
                conn.commit()
                logger.info("✅ Medications data seeded")
            except Exception as e:
                conn.rollback()
                logger.debug(f"Medications data may already exist: {e}")
            
            cur.close()
            conn.close()
            self._initialized = True
            logger.info("🗄️ PostgreSQL Profile Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    # ==========================================
    # PROFILE CRUD OPERATIONS
    # ==========================================
    
    def phone_exists(self, phone_number: str) -> bool:
        """Check if a phone number already has a profile"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM user_profiles WHERE phone_number = %s",
                (phone_number,)
            )
            exists = cur.fetchone() is not None
            cur.close()
            conn.close()
            return exists
        except Exception as e:
            logger.error(f"Error checking phone: {e}")
            return False
    
    def get_or_create_profile(
        self,
        phone_number: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        preferred_language: str = "en"
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Get existing profile or create new one
        Returns (profile_dict, is_new)
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if exists
            cur.execute(
                "SELECT * FROM user_profiles WHERE phone_number = %s",
                (phone_number,)
            )
            existing = cur.fetchone()
            
            if existing:
                # Update last access
                cur.execute(
                    "UPDATE user_profiles SET updated_at = %s WHERE phone_number = %s",
                    (datetime.utcnow(), phone_number)
                )
                conn.commit()
                
                # Get full profile with related data
                profile = self._get_full_profile(cur, existing['id'])
                cur.close()
                conn.close()
                return profile, False
            
            # Create new profile
            user_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO user_profiles (id, phone_number, name, age, gender, preferred_language)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (user_id, phone_number, name, age, gender, preferred_language)
            )
            new_profile = cur.fetchone()
            conn.commit()
            
            profile = self._get_full_profile(cur, new_profile['id'])
            cur.close()
            conn.close()
            
            logger.info(f"🆕 New profile created: {phone_number}")
            return profile, True
            
        except Exception as e:
            logger.error(f"Error in get_or_create_profile: {e}")
            raise
    
    def _get_full_profile(self, cur, user_id: str) -> Dict[str, Any]:
        """Get complete profile with all related data"""
        # Get base profile
        cur.execute("SELECT * FROM user_profiles WHERE id = %s", (user_id,))
        profile = dict(cur.fetchone())
        
        # Get allergies
        cur.execute(
            "SELECT allergen, severity, reaction FROM user_allergies WHERE user_id = %s",
            (user_id,)
        )
        profile['allergies'] = [dict(row) for row in cur.fetchall()]
        
        # Get conditions
        cur.execute(
            "SELECT condition_name, severity, is_active FROM user_conditions WHERE user_id = %s AND is_active = true",
            (user_id,)
        )
        profile['medical_conditions'] = [dict(row) for row in cur.fetchall()]
        
        # Get medications
        cur.execute(
            "SELECT medication_name, dosage, frequency FROM user_medications WHERE user_id = %s AND is_active = true",
            (user_id,)
        )
        profile['current_medications'] = [dict(row) for row in cur.fetchall()]
        
        # Get consultation count
        cur.execute(
            "SELECT COUNT(*) as count FROM consultations WHERE user_id = %s",
            (user_id,)
        )
        profile['consultation_count'] = cur.fetchone()['count']
        
        return profile
    
    def get_profile(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get profile by phone number"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(
                "SELECT id FROM user_profiles WHERE phone_number = %s",
                (phone_number,)
            )
            result = cur.fetchone()
            
            if not result:
                cur.close()
                conn.close()
                return None
            
            profile = self._get_full_profile(cur, result['id'])
            cur.close()
            conn.close()
            return profile
            
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None
    
    def update_profile(self, phone_number: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update profile fields"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Build update query
            allowed_fields = [
                'name', 'age', 'gender', 'blood_type', 'height_cm', 'weight_kg',
                'preferred_language', 'location', 'smoking', 'alcohol', 'exercise_frequency'
            ]
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
            
            if not updates:
                cur.close()
                conn.close()
                return self.get_profile(phone_number)
            
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [phone_number]
            
            cur.execute(
                f"UPDATE user_profiles SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE phone_number = %s RETURNING id",
                values
            )
            result = cur.fetchone()
            conn.commit()
            
            if result:
                profile = self._get_full_profile(cur, result['id'])
                cur.close()
                conn.close()
                return profile
            
            cur.close()
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return None
    
    # ==========================================
    # ALLERGY OPERATIONS
    # ==========================================
    
    def add_allergy(
        self,
        phone_number: str,
        allergen: str,
        severity: str = "moderate",
        reaction: Optional[str] = None
    ) -> bool:
        """Add an allergy to user profile"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get user_id
            cur.execute("SELECT id FROM user_profiles WHERE phone_number = %s", (phone_number,))
            result = cur.fetchone()
            if not result:
                cur.close()
                conn.close()
                return False
            
            user_id = result['id']
            
            # Check if already exists
            cur.execute(
                "SELECT 1 FROM user_allergies WHERE user_id = %s AND LOWER(allergen) = LOWER(%s)",
                (user_id, allergen)
            )
            if cur.fetchone():
                cur.close()
                conn.close()
                return True  # Already exists
            
            # Insert
            cur.execute(
                "INSERT INTO user_allergies (user_id, allergen, severity, reaction) VALUES (%s, %s, %s, %s)",
                (user_id, allergen, severity, reaction)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding allergy: {e}")
            return False
    
    def remove_allergy(self, phone_number: str, allergen: str) -> bool:
        """Remove an allergy from user profile"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                """
                DELETE FROM user_allergies 
                WHERE user_id = (SELECT id FROM user_profiles WHERE phone_number = %s)
                AND LOWER(allergen) = LOWER(%s)
                """,
                (phone_number, allergen)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error removing allergy: {e}")
            return False
    
    # ==========================================
    # CONDITION OPERATIONS
    # ==========================================
    
    def add_condition(
        self,
        phone_number: str,
        condition_name: str,
        severity: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Add a medical condition to user profile"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get user_id
            cur.execute("SELECT id FROM user_profiles WHERE phone_number = %s", (phone_number,))
            result = cur.fetchone()
            if not result:
                cur.close()
                conn.close()
                return False
            
            user_id = result['id']
            
            # Check if already exists
            cur.execute(
                "SELECT 1 FROM user_conditions WHERE user_id = %s AND LOWER(condition_name) = LOWER(%s)",
                (user_id, condition_name)
            )
            if cur.fetchone():
                cur.close()
                conn.close()
                return True
            
            # Insert
            cur.execute(
                "INSERT INTO user_conditions (user_id, condition_name, severity, notes) VALUES (%s, %s, %s, %s)",
                (user_id, condition_name, severity, notes)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding condition: {e}")
            return False
    
    # ==========================================
    # MEDICATION OPERATIONS
    # ==========================================
    
    def add_medication(
        self,
        phone_number: str,
        medication_name: str,
        dosage: Optional[str] = None,
        frequency: Optional[str] = None
    ) -> bool:
        """Add a current medication to user profile"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("SELECT id FROM user_profiles WHERE phone_number = %s", (phone_number,))
            result = cur.fetchone()
            if not result:
                cur.close()
                conn.close()
                return False
            
            cur.execute(
                "INSERT INTO user_medications (user_id, medication_name, dosage, frequency) VALUES (%s, %s, %s, %s)",
                (result['id'], medication_name, dosage, frequency)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding medication: {e}")
            return False
    
    # ==========================================
    # CONSULTATION HISTORY
    # ==========================================
    
    def record_consultation(
        self,
        phone_number: str,
        session_id: str,
        symptoms: List[str],
        urgency_level: str,
        conditions_suggested: List[str] = [],
        medications_suggested: List[str] = [],
        summary: str = ""
    ) -> bool:
        """Record a consultation in history"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("SELECT id FROM user_profiles WHERE phone_number = %s", (phone_number,))
            result = cur.fetchone()
            if not result:
                cur.close()
                conn.close()
                return False
            
            user_id = result['id']
            
            cur.execute(
                """
                INSERT INTO consultations 
                (user_id, session_id, symptoms, urgency_level, conditions_suggested, medications_suggested, ai_response_summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, session_id, symptoms, urgency_level, conditions_suggested, medications_suggested, summary)
            )
            
            # Update consultation count
            cur.execute(
                "UPDATE user_profiles SET total_consultations = total_consultations + 1, last_consultation = %s WHERE id = %s",
                (datetime.utcnow(), user_id)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error recording consultation: {e}")
            return False
    
    def get_consultation_history(
        self,
        phone_number: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get consultation history for a user"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(
                """
                SELECT c.* FROM consultations c
                JOIN user_profiles p ON c.user_id = p.id
                WHERE p.phone_number = %s
                ORDER BY c.created_at DESC
                LIMIT %s
                """,
                (phone_number, limit)
            )
            consultations = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            return consultations
            
        except Exception as e:
            logger.error(f"Error getting consultations: {e}")
            return []
    
    # ==========================================
    # AI CONTEXT GENERATION
    # ==========================================
    
    def get_ai_context(self, phone_number: str) -> str:
        """Generate AI context string for personalized responses"""
        profile = self.get_profile(phone_number)
        if not profile:
            return "No medical history on file."
        
        context_parts = []
        
        # Basic info
        if profile.get('name'):
            context_parts.append(f"Patient name: {profile['name']}")
        if profile.get('age'):
            context_parts.append(f"Age: {profile['age']} years")
        if profile.get('gender'):
            context_parts.append(f"Gender: {profile['gender']}")
        if profile.get('blood_type'):
            context_parts.append(f"Blood type: {profile['blood_type']}")
        
        # CRITICAL: Allergies
        allergies = profile.get('allergies', [])
        if allergies:
            allergy_list = [f"{a['allergen']} ({a['severity']})" for a in allergies]
            context_parts.append(f"⚠️ ALLERGIES (IMPORTANT): {', '.join(allergy_list)}")
        
        # Medical conditions
        conditions = profile.get('medical_conditions', [])
        if conditions:
            condition_list = [c['condition_name'] for c in conditions]
            context_parts.append(f"Known conditions: {', '.join(condition_list)}")
        
        # Current medications
        medications = profile.get('current_medications', [])
        if medications:
            med_list = [m['medication_name'] for m in medications]
            context_parts.append(f"Current medications: {', '.join(med_list)}")
        
        # Previous consultations
        if profile.get('total_consultations', 0) > 0:
            context_parts.append(f"Previous consultations: {profile['total_consultations']}")
        
        return "\n".join(context_parts) if context_parts else "No medical history on file."
    
    # ==========================================
    # AUTOCOMPLETE SEARCH
    # ==========================================
    
    def search_allergens(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search allergens for autocomplete"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(
                """
                SELECT name, category, severity_typical 
                FROM master_allergens 
                WHERE LOWER(name) LIKE LOWER(%s)
                ORDER BY 
                    CASE WHEN LOWER(name) = LOWER(%s) THEN 0
                         WHEN LOWER(name) LIKE LOWER(%s) THEN 1
                         ELSE 2 END,
                    name
                LIMIT %s
                """,
                (f"%{query}%", query, f"{query}%", limit)
            )
            results = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching allergens: {e}")
            return []
    
    def search_conditions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search medical conditions for autocomplete"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(
                """
                SELECT name, category, icd10_code 
                FROM master_conditions 
                WHERE LOWER(name) LIKE LOWER(%s)
                ORDER BY 
                    CASE WHEN LOWER(name) = LOWER(%s) THEN 0
                         WHEN LOWER(name) LIKE LOWER(%s) THEN 1
                         ELSE 2 END,
                    name
                LIMIT %s
                """,
                (f"%{query}%", query, f"{query}%", limit)
            )
            results = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching conditions: {e}")
            return []
    
    def search_medications(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search medications for autocomplete"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(
                """
                SELECT name, generic_name, drug_class 
                FROM master_medications 
                WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(generic_name) LIKE LOWER(%s)
                ORDER BY 
                    CASE WHEN LOWER(name) = LOWER(%s) THEN 0
                         WHEN LOWER(name) LIKE LOWER(%s) THEN 1
                         ELSE 2 END,
                    name
                LIMIT %s
                """,
                (f"%{query}%", f"%{query}%", query, f"{query}%", limit)
            )
            results = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching medications: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            stats = {}
            cur.execute("SELECT COUNT(*) as count FROM user_profiles")
            stats['total_users'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM consultations")
            stats['total_consultations'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM master_allergens")
            stats['total_allergens'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM master_conditions")
            stats['total_conditions'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM master_medications")
            stats['total_medications'] = cur.fetchone()['count']
            
            cur.close()
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Global instance
postgres_profile_service = PostgresProfileService()
