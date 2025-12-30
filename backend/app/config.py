from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # Application
    APP_NAME: str = "Multilingual Health AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/health_ai"
    DATABASE_ECHO: bool = False
    
    # Legacy MongoDB (deprecated)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "health_ai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # MQTT for IoT
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_PREFIX: str = "vitals"
    
    # API Keys (should be set via environment variables)
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Model Paths
    MODELS_DIR: str = str(BASE_DIR / "data" / "models")
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    INDICBERT_MODEL: str = "ai4bharat/indic-bert"
    
    # Language Configuration
    SUPPORTED_LANGUAGES: list = [
        "en", "hi", "bn", "ta", "te", "mr", 
        "gu", "kn", "ml", "pa", "or", "as"
    ]
    DEFAULT_LANGUAGE: str = "en"
    
    # Audio Processing
    AUDIO_SAMPLE_RATE: int = 16000
    MAX_AUDIO_DURATION: int = 60  # seconds
    
    # Inference
    MAX_INFERENCE_TIME: float = 2.0  # seconds
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Offline Mode
    OFFLINE_MODE_ENABLED: bool = True
    TFLITE_MODELS_DIR: str = str(BASE_DIR / "data" / "models" / "tflite")
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001
    
    # Medical Knowledge
    KNOWLEDGE_GRAPH_PATH: str = str(BASE_DIR / "data" / "medical_knowledge" / "knowledge_graph.json")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
