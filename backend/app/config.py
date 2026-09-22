from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Job Agent"
    ENVIRONMENT: str = "production"
    APP_DEBUG: bool = False
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    DRY_RUN: bool = True
    HUMAN_APPROVAL_REQUIRED: bool = True
    DAILY_APPLICATION_LIMIT: int = 10
    MINIMUM_JOB_SCORE: int = 60
    AUTO_SUBMIT_ENABLED: bool = False
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_ENABLED: bool = False
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_ENABLED: bool = False
    LOCAL_LLM_BASE_URL: str = ""
    LOCAL_LLM_MODEL: str = ""
    LOCAL_LLM_ENABLED: bool = False
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    CANDIDATE_DATA_DIR: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
