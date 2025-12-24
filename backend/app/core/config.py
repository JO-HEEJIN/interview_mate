"""
Application configuration using Pydantic Settings
Enhanced with production-ready configurations
"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "InterviewMate"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Database
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: Optional[str] = None
    
    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # ZhipuAI (GLM-4.6)
    ZHIPUAI_API_KEY: str = ""
    GLM_MODEL: str = "glm-4-flashx"  # glm-4-flashx, glm-4-airx, glm-4-plus
    LLM_SERVICE: str = "hybrid"  # "claude" or "glm" or "hybrid"

    # JWT
    JWT_SECRET: str = "development-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""

    # Lemon Squeezy
    LEMON_SQUEEZY_API_KEY: str = ""
    LEMON_SQUEEZY_STORE_ID: str = ""
    LEMON_SQUEEZY_WEBHOOK_SECRET: str = ""
    # Product variant IDs (set after creating products in Lemon Squeezy dashboard)
    LEMON_SQUEEZY_VARIANT_CREDITS_4: str = ""
    LEMON_SQUEEZY_VARIANT_CREDITS_10: str = ""
    LEMON_SQUEEZY_VARIANT_CREDITS_15: str = ""
    LEMON_SQUEEZY_VARIANT_AI_GENERATOR: str = ""
    LEMON_SQUEEZY_VARIANT_QA_MANAGEMENT: str = ""

    # Payment processor selection
    PAYMENT_PROCESSOR: str = "lemon_squeezy"  # "stripe" or "lemon_squeezy"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://interviewmate.tech",
        "https://www.interviewmate.tech"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Security
    SECRET_KEY: str = "development-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    
    # Audio Processing
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    AUDIO_CHUNK_SIZE: int = 1024
    AUDIO_BUFFER_DURATION: float = 2.0  # seconds
    AUDIO_PROCESSING_TIMEOUT: float = 5.0  # seconds
    
    # AI Services
    WHISPER_MODEL: str = "whisper-1"
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7

    # Deepgram (Transcription)
    DEEPGRAM_API_KEY: str = ""
    TRANSCRIPTION_SERVICE: str = "deepgram"  # "deepgram" or "whisper"
    DEEPGRAM_MODEL: str = "flux"  # "flux" or "nova-3"

    # Qdrant (Vector Search)
    QDRANT_URL: str = ""  # e.g., "http://qdrant:6333" (Railway internal) or "https://qdrant.railway.app"
    QDRANT_API_KEY: Optional[str] = None  # Optional for local/Railway internal
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".wav", ".mp3", ".m4a", ".pdf", ".docx"]
    
    # Monitoring
    ENABLE_METRICS: bool = False
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    
    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # seconds
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    @property
    def is_development(self) -> bool:
        return self.APP_ENV.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() == "testing"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return self.DATABASE_URL
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get complete CORS configuration"""
        return {
            "allow_origins": self.cors_origins_list,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "allow_methods": self.CORS_ALLOW_METHODS,
            "allow_headers": self.CORS_ALLOW_HEADERS,
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT,
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.LOG_LEVEL,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console"],
            },
            "loggers": {
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "fastapi": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "websockets": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
        
        # Add file handler if log file is specified
        if self.LOG_FILE:
            log_dir = Path(self.LOG_FILE).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": self.LOG_LEVEL,
                "formatter": "detailed",
                "filename": self.LOG_FILE,
                "maxBytes": self.LOG_MAX_BYTES,
                "backupCount": self.LOG_BACKUP_COUNT,
            }
            config["root"]["handlers"].append("file")
        
        return config
    
    def validate_required_settings(self) -> None:
        """Validate that required settings are present"""
        required_settings = []

        if self.is_production:
            required_settings.extend([
                "SECRET_KEY",
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
            ])

        missing_settings = []
        for setting in required_settings:
            if not getattr(self, setting):
                missing_settings.append(setting)

        if missing_settings:
            raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    settings.validate_required_settings()
    return settings


# Global settings instance
settings = get_settings()
