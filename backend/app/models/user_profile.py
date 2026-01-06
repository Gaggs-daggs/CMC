"""
User Profile Model
Persistent storage for user medical profiles

Stores:
- Basic info (phone, name, age, etc.)
- Medical history (conditions, allergies, medications)
- Previous symptoms and consultations
- AI context for personalized responses
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


class MedicalCondition(BaseModel):
    """A medical condition the user has"""
    name: str
    diagnosed_date: Optional[str] = None
    severity: Optional[str] = None  # mild, moderate, severe
    notes: Optional[str] = None
    is_active: bool = True


class Allergy(BaseModel):
    """User allergy information"""
    allergen: str  # e.g., "Penicillin", "Peanuts", "Dust"
    severity: str = "moderate"  # mild, moderate, severe
    reaction: Optional[str] = None  # e.g., "Rash", "Anaphylaxis"


class CurrentMedication(BaseModel):
    """Medication the user is currently taking"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    prescribed_for: Optional[str] = None
    start_date: Optional[str] = None


class PastConsultation(BaseModel):
    """Record of a past consultation/session"""
    session_id: str
    date: datetime
    symptoms: List[str]
    urgency_level: str
    ai_response_summary: Optional[str] = None
    conditions_suggested: List[str] = []
    medications_suggested: List[str] = []
    follow_up_needed: bool = False


class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str
    relationship: str
    phone: str


class UserProfile(BaseModel):
    """
    Complete User Profile
    Stored persistently for returning users
    """
    # Unique identifier
    phone_number: str = Field(..., description="Primary identifier - phone number")
    user_id: str = Field(default="", description="Internal user ID")
    
    # Basic Information
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = BloodType.UNKNOWN
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    
    # Location (for emergency services)
    preferred_language: str = "en"
    location: Optional[str] = None
    
    # Medical History
    medical_conditions: List[MedicalCondition] = []
    allergies: List[Allergy] = []
    current_medications: List[CurrentMedication] = []
    
    # Family History (important for risk assessment)
    family_history: List[str] = []  # e.g., ["diabetes", "heart disease"]
    
    # Lifestyle factors
    smoking: Optional[bool] = None
    alcohol: Optional[str] = None  # none, occasional, regular
    exercise_frequency: Optional[str] = None  # none, occasional, regular, daily
    
    # Past consultations with CMC Health
    consultation_history: List[PastConsultation] = []
    
    # Symptom patterns (for AI context)
    recurring_symptoms: List[str] = []  # Symptoms that appear frequently
    symptom_frequency: Dict[str, int] = {}  # symptom -> count
    
    # Emergency contact
    emergency_contact: Optional[EmergencyContact] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_consultation: Optional[datetime] = None
    total_consultations: int = 0
    
    # Profile completeness (0-100)
    profile_completeness: int = 0
    
    def calculate_completeness(self) -> int:
        """Calculate how complete the profile is"""
        score = 0
        max_score = 100
        
        # Basic info (40 points)
        if self.name: score += 10
        if self.age: score += 10
        if self.gender: score += 5
        if self.blood_type and self.blood_type != BloodType.UNKNOWN: score += 5
        if self.height_cm: score += 5
        if self.weight_kg: score += 5
        
        # Medical history (30 points)
        if len(self.medical_conditions) > 0 or self.medical_conditions == []: score += 10
        if len(self.allergies) > 0 or self.allergies == []: score += 10
        if len(self.current_medications) > 0 or self.current_medications == []: score += 10
        
        # Emergency (15 points)
        if self.emergency_contact: score += 15
        
        # Lifestyle (15 points)
        if self.smoking is not None: score += 5
        if self.alcohol: score += 5
        if self.exercise_frequency: score += 5
        
        self.profile_completeness = min(score, max_score)
        return self.profile_completeness
    
    def get_ai_context(self) -> str:
        """
        Generate context string for AI to understand the user
        This is passed to the AI for personalized responses
        """
        context_parts = []
        
        # Basic info
        if self.name:
            context_parts.append(f"Patient name: {self.name}")
        if self.age:
            context_parts.append(f"Age: {self.age} years")
        if self.gender:
            context_parts.append(f"Gender: {self.gender.value}")
        
        # Medical conditions
        if self.medical_conditions:
            active_conditions = [c.name for c in self.medical_conditions if c.is_active]
            if active_conditions:
                context_parts.append(f"Known conditions: {', '.join(active_conditions)}")
        
        # Allergies (IMPORTANT for medication suggestions)
        if self.allergies:
            allergy_list = [f"{a.allergen} ({a.severity})" for a in self.allergies]
            context_parts.append(f"⚠️ ALLERGIES: {', '.join(allergy_list)}")
        
        # Current medications (for interaction warnings)
        if self.current_medications:
            med_list = [m.name for m in self.current_medications]
            context_parts.append(f"Current medications: {', '.join(med_list)}")
        
        # Family history
        if self.family_history:
            context_parts.append(f"Family history: {', '.join(self.family_history)}")
        
        # Recurring symptoms
        if self.recurring_symptoms:
            context_parts.append(f"Recurring symptoms: {', '.join(self.recurring_symptoms)}")
        
        # Previous consultations summary
        if self.consultation_history:
            recent = self.consultation_history[-3:]  # Last 3 consultations
            recent_symptoms = []
            for c in recent:
                recent_symptoms.extend(c.symptoms)
            if recent_symptoms:
                context_parts.append(f"Recent symptoms reported: {', '.join(set(recent_symptoms))}")
        
        # Lifestyle factors
        lifestyle = []
        if self.smoking:
            lifestyle.append("smoker")
        if self.alcohol == "regular":
            lifestyle.append("regular alcohol use")
        if lifestyle:
            context_parts.append(f"Lifestyle factors: {', '.join(lifestyle)}")
        
        return "\n".join(context_parts) if context_parts else "No medical history on file."
    
    def add_consultation(self, session_id: str, symptoms: List[str], 
                        urgency_level: str, conditions: List[str] = [],
                        medications: List[str] = [], summary: str = ""):
        """Add a consultation to history"""
        consultation = PastConsultation(
            session_id=session_id,
            date=datetime.utcnow(),
            symptoms=symptoms,
            urgency_level=urgency_level,
            conditions_suggested=conditions,
            medications_suggested=medications,
            ai_response_summary=summary
        )
        self.consultation_history.append(consultation)
        self.last_consultation = datetime.utcnow()
        self.total_consultations += 1
        
        # Update symptom frequency
        for symptom in symptoms:
            self.symptom_frequency[symptom] = self.symptom_frequency.get(symptom, 0) + 1
            
            # Mark as recurring if appears 3+ times
            if self.symptom_frequency[symptom] >= 3 and symptom not in self.recurring_symptoms:
                self.recurring_symptoms.append(symptom)
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API"""
        return {
            "phone_number": self.phone_number,
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender.value if self.gender else None,
            "blood_type": self.blood_type.value if self.blood_type else None,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "preferred_language": self.preferred_language,
            "location": self.location,
            "medical_conditions": [c.model_dump() for c in self.medical_conditions],
            "allergies": [a.model_dump() for a in self.allergies],
            "current_medications": [m.model_dump() for m in self.current_medications],
            "family_history": self.family_history,
            "smoking": self.smoking,
            "alcohol": self.alcohol,
            "exercise_frequency": self.exercise_frequency,
            "recurring_symptoms": self.recurring_symptoms,
            "symptom_frequency": self.symptom_frequency,
            "emergency_contact": self.emergency_contact.model_dump() if self.emergency_contact else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_consultation": self.last_consultation.isoformat() if self.last_consultation else None,
            "total_consultations": self.total_consultations,
            "profile_completeness": self.calculate_completeness(),
            "consultation_count": len(self.consultation_history)
        }


class ProfileCreateRequest(BaseModel):
    """Request to create a new profile"""
    phone_number: str
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    preferred_language: str = "en"
    allergies: Optional[List[str]] = None  # List of allergy names
    chronic_conditions: Optional[List[str]] = None  # List of condition names


class ProfileUpdateRequest(BaseModel):
    """Request to update profile"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    location: Optional[str] = None
    preferred_language: Optional[str] = None
    smoking: Optional[bool] = None
    alcohol: Optional[str] = None
    exercise_frequency: Optional[str] = None
    family_history: Optional[List[str]] = None


class AddAllergyRequest(BaseModel):
    """Request to add an allergy"""
    allergen: str
    severity: str = "moderate"
    reaction: Optional[str] = None


class AddConditionRequest(BaseModel):
    """Request to add a medical condition"""
    name: str
    diagnosed_date: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class AddMedicationRequest(BaseModel):
    """Request to add current medication"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    prescribed_for: Optional[str] = None
