from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Weather Query API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/weather_db"
    WEATHER_API_KEY: str
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"

    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW: int = 60
    CACHE_DURATION: int = 300
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file=".env")

settings = Settings()