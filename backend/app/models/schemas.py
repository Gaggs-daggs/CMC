from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH = "en"
    HINDI = "hi"
    BENGALI = "bn"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ORIYA = "or"
    ASSAMESE = "as"


class UrgencyLevel(str, Enum):
    """Health urgency classification"""
    SELF_CARE = "self_care"
    DOCTOR_NEEDED = "doctor_needed"
    EMERGENCY = "emergency"


class EmotionState(str, Enum):
    """Detected emotion states"""
    CALM = "calm"
    STRESSED = "stressed"
    IN_PAIN = "in_pain"
    ANXIOUS = "anxious"


class VitalsReading(BaseModel):
    """IoT vitals sensor reading"""
    heart_rate: Optional[float] = Field(None, ge=30, le=250, description="Heart rate in BPM")
    spo2: Optional[float] = Field(None, ge=0, le=100, description="Blood oxygen saturation %")
    temperature: Optional[float] = Field(None, ge=90, le=110, description="Body temperature in °F")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "heart_rate": 78,
                "spo2": 98,
                "temperature": 98.6,
                "device_id": "sensor_001"
            }
        }


class ExtractedSymptom(BaseModel):
    """Extracted symptom from user input"""
    name: str
    body_part: Optional[str] = None
    severity: Optional[str] = None  # mild, moderate, severe
    duration: Optional[str] = None  # "2 days", "since morning"
    confidence: float = Field(ge=0, le=1)


class EmotionAnalysis(BaseModel):
    """Emotion detection results"""
    primary_emotion: EmotionState
    confidence: float = Field(ge=0, le=1)
    stress_level: float = Field(ge=0, le=1, description="0=calm, 1=highly stressed")
    pain_indicator: float = Field(ge=0, le=1, description="0=no pain, 1=severe pain")


class DiagnosisResult(BaseModel):
    """Health diagnosis and recommendation"""
    urgency_level: UrgencyLevel
    confidence: float = Field(ge=0, le=1)
    possible_conditions: List[str] = []
    recommendations: List[str] = []
    red_flags: List[str] = []  # Warning signs to watch for
    follow_up_timeline: Optional[str] = None  # "24 hours", "if symptoms worsen"
    emergency_contact: Optional[str] = None  # Emergency number if critical


class ConversationMessage(BaseModel):
    """Single conversation message"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    language: LanguageCode
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional analysis data
    extracted_symptoms: Optional[List[ExtractedSymptom]] = None
    vitals: Optional[VitalsReading] = None
    emotion: Optional[EmotionAnalysis] = None
    diagnosis: Optional[DiagnosisResult] = None


class UserProfile(BaseModel):
    """User profile information"""
    phone: str
    preferred_language: LanguageCode = LanguageCode.ENGLISH
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # {lat, lng}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """Conversation session"""
    session_id: str
    user_id: str
    conversation: List[ConversationMessage] = []
    status: str = "active"  # active, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response Models

class StartConversationRequest(BaseModel):
    """Start a new conversation session"""
    user_id: str
    language: Optional[LanguageCode] = LanguageCode.ENGLISH


class StartConversationResponse(BaseModel):
    """Response with session ID"""
    session_id: str
    greeting: str


class TextMessageRequest(BaseModel):
    """Send text message"""
    session_id: str
    message: str
    language: Optional[LanguageCode] = None


class VoiceMessageRequest(BaseModel):
    """Send voice message"""
    session_id: str
    # audio_file will be handled as UploadFile in endpoint


class MessageResponse(BaseModel):
    """Response to user message"""
    response_text: str
    response_language: LanguageCode
    response_audio_url: Optional[str] = None  # URL to generated audio
    
    # Analysis results
    extracted_symptoms: List[ExtractedSymptom] = []
    current_vitals: Optional[VitalsReading] = None
    emotion_detected: Optional[EmotionAnalysis] = None
    diagnosis: Optional[DiagnosisResult] = None
    
    # Metadata
    processing_time_ms: float
    confidence_score: float


class SubmitVitalsRequest(BaseModel):
    """Submit vitals reading"""
    user_id: str
    vitals: VitalsReading


class HealthCheckResponse(BaseModel):
    """Health check endpoint response"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]  # {service_name: status}
