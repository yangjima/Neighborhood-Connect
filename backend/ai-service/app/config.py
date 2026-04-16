from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TEMPERATURE: float = 0.0

    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "neighborhood_db"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 300  # 5 minutes

    # Service URLs
    RENTAL_SERVICE_URL: str = "http://localhost:8001"
    TRADE_SERVICE_URL: str = "http://localhost:8002"

    # AI Configuration
    AI_TIMEOUT: int = 10
    AI_MAX_RETRIES: int = 3
    AI_ENABLE_CACHE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
