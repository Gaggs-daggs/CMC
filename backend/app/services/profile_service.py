"""
User Profile Service
Manages persistent user profiles and medical history

Features:
- Create/retrieve profiles by phone number
- Store medical history, allergies, conditions
- Track consultation history
- Generate AI context from profile

Now uses PostgreSQL for persistent storage!
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, List, Any, Tuple
from pathlib import Path

from ..models.user_profile import (
    UserProfile, 
    MedicalCondition, 
    Allergy, 
    CurrentMedication,
    EmergencyContact,
    Gender,
    BloodType,
    PastConsultation
)

# Try to import PostgreSQL service
try:
    from .database.postgres_profile_service import postgres_profile_service
    POSTGRES_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ PostgreSQL profile service available")
except ImportError as e:
    POSTGRES_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ PostgreSQL not available, using in-memory storage: {e}")


class ProfileService:
    """
    User Profile Management Service
    
    Uses PostgreSQL for persistent storage with in-memory fallback
    
    Handles:
    - Profile creation and retrieval
    - Medical history management
    - AI context generation
    - Persistent storage
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize profile service
        
        Args:
            storage_path: Path to store profiles (for fallback JSON storage)
        """
        self.use_postgres = POSTGRES_AVAILABLE
        # In-memory cache for active profiles
        self._profiles: Dict[str, UserProfile] = {}
        
        # Persistent storage path
        if storage_path:
            self._storage_path = Path(storage_path)
        else:
            # Default to data directory
            self._storage_path = Path(__file__).parent.parent.parent / "data" / "user_profiles.json"
        
        # Load existing profiles
        self._load_profiles()
        
        logger.info(f"✅ Profile Service initialized with {len(self._profiles)} profiles")
    
    def _load_profiles(self):
        """Load profiles from persistent storage"""
        try:
            if self._storage_path.exists():
                with open(self._storage_path, 'r') as f:
                    data = json.load(f)
                    for phone, profile_data in data.items():
                        try:
                            # Convert stored data back to UserProfile
                            profile = self._dict_to_profile(profile_data)
                            self._profiles[phone] = profile
                        except Exception as e:
                            logger.warning(f"Failed to load profile {phone}: {e}")
                logger.info(f"Loaded {len(self._profiles)} profiles from storage")
        except Exception as e:
            logger.warning(f"Could not load profiles: {e}")
    
    def _save_profiles(self):
        """Save profiles to persistent storage"""
        try:
            # Ensure directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert profiles to serializable format
            data = {}
            for phone, profile in self._profiles.items():
                data[phone] = self._profile_to_dict(profile)
            
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug(f"Saved {len(self._profiles)} profiles to storage")
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def _profile_to_dict(self, profile: UserProfile) -> Dict:
        """Convert UserProfile to serializable dict"""
        return {
            "phone_number": profile.phone_number,
            "user_id": profile.user_id,
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender.value if profile.gender else None,
            "blood_type": profile.blood_type.value if profile.blood_type else None,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "preferred_language": profile.preferred_language,
            "location": profile.location,
            "medical_conditions": [c.model_dump() for c in profile.medical_conditions],
            "allergies": [a.model_dump() for a in profile.allergies],
            "current_medications": [m.model_dump() for m in profile.current_medications],
            "family_history": profile.family_history,
            "smoking": profile.smoking,
            "alcohol": profile.alcohol,
            "exercise_frequency": profile.exercise_frequency,
            "recurring_symptoms": profile.recurring_symptoms,
            "symptom_frequency": profile.symptom_frequency,
            "emergency_contact": profile.emergency_contact.model_dump() if profile.emergency_contact else None,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
            "last_consultation": profile.last_consultation.isoformat() if profile.last_consultation else None,
            "total_consultations": profile.total_consultations,
            "consultation_history": [
                {
                    "session_id": c.session_id,
                    "date": c.date.isoformat(),
                    "symptoms": c.symptoms,
                    "urgency_level": c.urgency_level,
                    "ai_response_summary": c.ai_response_summary,
                    "conditions_suggested": c.conditions_suggested,
                    "medications_suggested": c.medications_suggested,
                    "follow_up_needed": c.follow_up_needed
                }
                for c in profile.consultation_history[-20:]  # Keep last 20
            ]
        }
    
    def _dict_to_profile(self, data: Dict) -> UserProfile:
        """Convert dict back to UserProfile"""
        profile = UserProfile(
            phone_number=data["phone_number"],
            user_id=data.get("user_id", ""),
            name=data.get("name"),
            age=data.get("age"),
            gender=Gender(data["gender"]) if data.get("gender") else None,
            blood_type=BloodType(data["blood_type"]) if data.get("blood_type") else BloodType.UNKNOWN,
            height_cm=data.get("height_cm"),
            weight_kg=data.get("weight_kg"),
            preferred_language=data.get("preferred_language", "en"),
            location=data.get("location"),
            family_history=data.get("family_history", []),
            smoking=data.get("smoking"),
            alcohol=data.get("alcohol"),
            exercise_frequency=data.get("exercise_frequency"),
            recurring_symptoms=data.get("recurring_symptoms", []),
            symptom_frequency=data.get("symptom_frequency", {}),
            total_consultations=data.get("total_consultations", 0)
        )
        
        # Parse dates
        if data.get("created_at"):
            profile.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            profile.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("last_consultation"):
            profile.last_consultation = datetime.fromisoformat(data["last_consultation"])
        
        # Parse medical conditions
        for c in data.get("medical_conditions", []):
            profile.medical_conditions.append(MedicalCondition(**c))
        
        # Parse allergies
        for a in data.get("allergies", []):
            profile.allergies.append(Allergy(**a))
        
        # Parse medications
        for m in data.get("current_medications", []):
            profile.current_medications.append(CurrentMedication(**m))
        
        # Parse emergency contact
        if data.get("emergency_contact"):
            profile.emergency_contact = EmergencyContact(**data["emergency_contact"])
        
        # Parse consultation history
        for c in data.get("consultation_history", []):
            profile.consultation_history.append(PastConsultation(
                session_id=c["session_id"],
                date=datetime.fromisoformat(c["date"]),
                symptoms=c["symptoms"],
                urgency_level=c["urgency_level"],
                ai_response_summary=c.get("ai_response_summary"),
                conditions_suggested=c.get("conditions_suggested", []),
                medications_suggested=c.get("medications_suggested", []),
                follow_up_needed=c.get("follow_up_needed", False)
            ))
        
        return profile
    
    def _generate_user_id(self, phone: str) -> str:
        """Generate a unique user ID from phone number"""
        return hashlib.sha256(f"cmc_health_{phone}".encode()).hexdigest()[:16]
    
    # ==========================================
    # Public API
    # ==========================================
    
    def phone_exists(self, phone_number: str) -> bool:
        """Check if a phone number has an existing profile"""
        if self.use_postgres:
            return postgres_profile_service.phone_exists(phone_number)
        normalized = self._normalize_phone(phone_number)
        return normalized in self._profiles
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number (remove spaces, dashes, etc.)"""
        return ''.join(filter(str.isdigit, phone))[-10:]  # Last 10 digits
    
    def create_profile(self, phone_number: str, name: str = None, 
                      age: int = None, gender: str = None,
                      preferred_language: str = "en") -> UserProfile:
        """
        Create a new user profile
        
        Args:
            phone_number: User's phone number (unique identifier)
            name: Optional name
            age: Optional age
            gender: Optional gender
            preferred_language: Preferred language code
            
        Returns:
            Created UserProfile
        """
        if self.use_postgres:
            profile_dict, is_new = postgres_profile_service.get_or_create_profile(
                phone_number=phone_number,
                name=name,
                age=age,
                gender=gender,
                preferred_language=preferred_language
            )
            # Convert dict to UserProfile for compatibility
            return self._dict_to_profile_from_postgres(profile_dict)
        
        normalized_phone = self._normalize_phone(phone_number)
        
        # Check if already exists
        if normalized_phone in self._profiles:
            logger.info(f"Profile already exists for {normalized_phone}, returning existing")
            return self._profiles[normalized_phone]
        
        # Create new profile
        profile = UserProfile(
            phone_number=normalized_phone,
            user_id=self._generate_user_id(normalized_phone),
            name=name,
            age=age,
            gender=Gender(gender) if gender else None,
            preferred_language=preferred_language,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store and persist
        self._profiles[normalized_phone] = profile
        self._save_profiles()
        
        logger.info(f"✅ Created new profile for {normalized_phone}")
        return profile
    
    def get_profile(self, phone_number: str) -> Optional[UserProfile]:
        """
        Get user profile by phone number
        
        Args:
            phone_number: User's phone number
            
        Returns:
            UserProfile if found, None otherwise
        """
        if self.use_postgres:
            profile_dict = postgres_profile_service.get_profile(phone_number)
            if profile_dict:
                return self._dict_to_profile_from_postgres(profile_dict)
            return None
        normalized = self._normalize_phone(phone_number)
        return self._profiles.get(normalized)
    
    def _dict_to_profile_from_postgres(self, data: Dict) -> UserProfile:
        """Convert PostgreSQL dict to UserProfile"""
        profile = UserProfile(
            phone_number=data.get("phone_number", ""),
            user_id=str(data.get("id", "")),
            name=data.get("name"),
            age=data.get("age"),
            preferred_language=data.get("preferred_language", "en"),
            total_consultations=data.get("total_consultations", 0)
        )
        
        # Handle gender
        if data.get("gender"):
            try:
                profile.gender = Gender(data["gender"])
            except:
                pass
        
        # Handle blood type
        if data.get("blood_type"):
            try:
                profile.blood_type = BloodType(data["blood_type"])
            except:
                pass
        
        # Handle allergies
        for a in data.get("allergies", []):
            profile.allergies.append(Allergy(
                allergen=a.get("allergen", ""),
                severity=a.get("severity", "moderate"),
                reaction=a.get("reaction")
            ))
        
        # Handle conditions
        for c in data.get("medical_conditions", []):
            profile.medical_conditions.append(MedicalCondition(
                name=c.get("condition_name", ""),
                severity=c.get("severity"),
                is_active=c.get("is_active", True)
            ))
        
        # Handle medications
        for m in data.get("current_medications", []):
            profile.current_medications.append(CurrentMedication(
                name=m.get("medication_name", ""),
                dosage=m.get("dosage"),
                frequency=m.get("frequency")
            ))
        
        return profile
    
    def get_or_create_profile(self, phone_number: str, **kwargs) -> Tuple[UserProfile, bool]:
        """
        Get existing profile or create new one
        
        Returns:
            (profile, is_new) - The profile and whether it was newly created
        """
        if self.use_postgres:
            profile_dict, is_new = postgres_profile_service.get_or_create_profile(
                phone_number=phone_number,
                name=kwargs.get('name'),
                age=kwargs.get('age'),
                gender=kwargs.get('gender'),
                preferred_language=kwargs.get('preferred_language', 'en')
            )
            return self._dict_to_profile_from_postgres(profile_dict), is_new
        
        normalized = self._normalize_phone(phone_number)
        
        if normalized in self._profiles:
            return self._profiles[normalized], False
        else:
            profile = self.create_profile(phone_number, **kwargs)
            return profile, True
    
    def update_profile(self, phone_number: str, **updates) -> Optional[UserProfile]:
        """
        Update user profile
        
        Args:
            phone_number: User's phone number
            **updates: Fields to update
            
        Returns:
            Updated profile or None if not found
        """
        profile = self.get_profile(phone_number)
        if not profile:
            return None
        
        # Update allowed fields
        allowed_fields = [
            'name', 'age', 'height_cm', 'weight_kg', 'location',
            'preferred_language', 'smoking', 'alcohol', 'exercise_frequency',
            'family_history'
        ]
        
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(profile, field, value)
        
        # Handle gender and blood_type specially
        if 'gender' in updates and updates['gender']:
            profile.gender = Gender(updates['gender'])
        if 'blood_type' in updates and updates['blood_type']:
            profile.blood_type = BloodType(updates['blood_type'])
        
        profile.updated_at = datetime.utcnow()
        self._save_profiles()
        
        logger.info(f"Updated profile for {phone_number}")
        return profile
    
    def add_allergy(self, phone_number: str, allergen: str, 
                   severity: str = "moderate", reaction: str = None) -> Optional[UserProfile]:
        """Add an allergy to user profile"""
        if self.use_postgres:
            success = postgres_profile_service.add_allergy(phone_number, allergen, severity, reaction)
            if success:
                return self.get_profile(phone_number)
            return None
        
        profile = self.get_profile(phone_number)
        if not profile:
            return None
        
        # Check if already exists
        for a in profile.allergies:
            if a.allergen.lower() == allergen.lower():
                return profile  # Already has this allergy
        
        profile.allergies.append(Allergy(
            allergen=allergen,
            severity=severity,
            reaction=reaction
        ))
        profile.updated_at = datetime.utcnow()
        self._save_profiles()
        
        logger.info(f"Added allergy '{allergen}' for {phone_number}")
        return profile
    
    def add_condition(self, phone_number: str, name: str,
                     diagnosed_date: str = None, severity: str = None,
                     notes: str = None) -> Optional[UserProfile]:
        """Add a medical condition to user profile"""
        if self.use_postgres:
            success = postgres_profile_service.add_condition(phone_number, name, severity, notes)
            if success:
                return self.get_profile(phone_number)
            return None
        
        profile = self.get_profile(phone_number)
        if not profile:
            return None
        
        # Check if already exists
        for c in profile.medical_conditions:
            if c.name.lower() == name.lower():
                return profile  # Already has this condition
        
        profile.medical_conditions.append(MedicalCondition(
            name=name,
            diagnosed_date=diagnosed_date,
            severity=severity,
            notes=notes,
            is_active=True
        ))
        profile.updated_at = datetime.utcnow()
        self._save_profiles()
        
        logger.info(f"Added condition '{name}' for {phone_number}")
        return profile
    
    def add_medication(self, phone_number: str, name: str,
                      dosage: str = None, frequency: str = None,
                      prescribed_for: str = None) -> Optional[UserProfile]:
        """Add a current medication to user profile"""
        profile = self.get_profile(phone_number)
        if not profile:
            return None
        
        # Check if already exists
        for m in profile.current_medications:
            if m.name.lower() == name.lower():
                return profile  # Already has this medication
        
        profile.current_medications.append(CurrentMedication(
            name=name,
            dosage=dosage,
            frequency=frequency,
            prescribed_for=prescribed_for,
            start_date=datetime.utcnow().strftime("%Y-%m-%d")
        ))
        profile.updated_at = datetime.utcnow()
        self._save_profiles()
        
        logger.info(f"Added medication '{name}' for {phone_number}")
        return profile
    
    def set_emergency_contact(self, phone_number: str, name: str,
                             relationship: str, contact_phone: str) -> Optional[UserProfile]:
        """Set emergency contact for user"""
        profile = self.get_profile(phone_number)
        if not profile:
            return None
        
        profile.emergency_contact = EmergencyContact(
            name=name,
            relationship=relationship,
            phone=contact_phone
        )
        profile.updated_at = datetime.utcnow()
        self._save_profiles()
        
        logger.info(f"Set emergency contact for {phone_number}")
        return profile
    
    def record_consultation(self, phone_number: str, session_id: str,
                           symptoms: List[str], urgency_level: str,
                           conditions: List[str] = [],
                           medications: List[str] = [],
                           summary: str = "") -> Optional[UserProfile]:
        """Record a consultation in user's history"""
        # Save to PostgreSQL first (persistent storage)
        if self.use_postgres:
            try:
                postgres_profile_service.record_consultation(
                    phone_number=phone_number,
                    session_id=session_id,
                    symptoms=symptoms,
                    urgency_level=urgency_level,
                    conditions_suggested=conditions,
                    medications_suggested=medications,
                    summary=summary
                )
                logger.info(f"📝 PostgreSQL: Recorded consultation for {phone_number}")
            except Exception as e:
                logger.error(f"PostgreSQL consultation record failed: {e}")
        
        # Also update in-memory cache
        profile = self.get_profile(phone_number)
        if not profile:
            logger.warning(f"Cannot record consultation - no profile for {phone_number}")
            return None
        
        profile.add_consultation(
            session_id=session_id,
            symptoms=symptoms,
            urgency_level=urgency_level,
            conditions=conditions,
            medications=medications,
            summary=summary
        )
        self._save_profiles()
        
        logger.info(f"Recorded consultation for {phone_number}: {symptoms}")
        return profile
    
    def get_ai_context(self, phone_number: str) -> str:
        """
        Get AI context string for a user
        This is passed to the AI model for personalized responses
        """
        profile = self.get_profile(phone_number)
        if not profile:
            return "New user - no medical history on file."
        
        return profile.get_ai_context()
    
    def get_consultation_history(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """Get recent consultation history for a user"""
        # Use PostgreSQL if available (has the most complete data)
        if self.use_postgres:
            try:
                return postgres_profile_service.get_consultation_history(phone_number, limit)
            except Exception as e:
                logger.error(f"PostgreSQL get_consultation_history failed: {e}")
        
        # Fallback to in-memory
        profile = self.get_profile(phone_number)
        if not profile:
            return []
        
        history = []
        for c in profile.consultation_history[-limit:]:
            history.append({
                "session_id": c.session_id,
                "date": c.date.isoformat(),
                "symptoms": c.symptoms,
                "urgency_level": c.urgency_level,
                "conditions_suggested": c.conditions_suggested,
                "medications_suggested": c.medications_suggested
            })
        
        return history
    
    def get_profile_summary(self, phone_number: str) -> Optional[Dict]:
        """Get a summary of user's profile for display"""
        profile = self.get_profile(phone_number)
        if not profile:
            return None
        
        return profile.to_dict()
    
    def delete_profile(self, phone_number: str) -> bool:
        """Delete a user profile (for GDPR compliance etc.)"""
        normalized = self._normalize_phone(phone_number)
        if normalized in self._profiles:
            del self._profiles[normalized]
            self._save_profiles()
            logger.info(f"Deleted profile for {normalized}")
            return True
        return False
    
    def get_all_profiles_count(self) -> int:
        """Get total number of profiles"""
        return len(self._profiles)


# Singleton instance
profile_service = ProfileService()
