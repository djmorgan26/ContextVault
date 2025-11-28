"""
Application configuration management using Pydantic Settings.

Loads configuration from environment variables with validation.
Loads from both root .env (shared secrets) and backend/.env (config)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        # Load from both root .env (secrets) and backend .env (config)
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "ContextVault"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security
    APP_SECRET_KEY: str  # Required for encryption key derivation
    JWT_SECRET_KEY: str  # Required for JWT signing
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str  # Required: postgresql://user:pass@host:port/db

    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Epic SMART on FHIR
    EPIC_CLIENT_ID: Optional[str] = None
    EPIC_CLIENT_SECRET: Optional[str] = None
    EPIC_REDIRECT_URI: str = "http://localhost:8000/api/integrations/epic/callback"
    EPIC_ISSUER: str = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2"
    EPIC_FHIR_BASE: str = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"

    # Fitbit OAuth (optional)
    FITBIT_CLIENT_ID: Optional[str] = None
    FITBIT_CLIENT_SECRET: Optional[str] = None
    FITBIT_REDIRECT_URI: str = "http://localhost:8000/api/integrations/fitbit/callback"

    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.1:8b"
    OLLAMA_TIMEOUT_SECONDS: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "/data/uploads"

    # Redis (optional, for caching and state)
    REDIS_URL: Optional[str] = None

    # Encryption
    PBKDF2_ITERATIONS: int = 100000
    AES_KEY_SIZE: int = 32  # 256 bits

    def get_database_url(self) -> str:
        """Get database URL, ensuring it's properly formatted."""
        return self.DATABASE_URL

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


# Global settings instance
settings = Settings()
