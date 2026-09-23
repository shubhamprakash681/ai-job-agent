import urllib.parse
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def sanitize_database_url(url: str) -> str:
    """
    Ensure the password in a database URL is properly percent-encoded.
    Prevents characters like '@', ':', '/', or '?' in passwords from breaking URL parsing.
    """
    if not url or "://" not in url:
        return url
    try:
        prefix, remainder = url.split("://", 1)
        if "@" not in remainder:
            return url
        path_parts = remainder.split("/", 1)
        netloc = path_parts[0]
        path_suffix = "/" + path_parts[1] if len(path_parts) > 1 else ""
        
        last_at_idx = netloc.rfind("@")
        creds = netloc[:last_at_idx]
        host_port = netloc[last_at_idx + 1:]
        
        if ":" in creds:
            username, password = creds.split(":", 1)
            encoded_password = urllib.parse.quote(urllib.parse.unquote(password), safe="")
            netloc = f"{username}:{encoded_password}@{host_port}"
        
        return f"{prefix}://{netloc}{path_suffix}"
    except Exception:
        return url


class Settings(BaseSettings):
    APP_NAME: str = "AI Job Agent"
    ENVIRONMENT: str = "production"
    APP_DEBUG: bool = False
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        return sanitize_database_url(v)
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
