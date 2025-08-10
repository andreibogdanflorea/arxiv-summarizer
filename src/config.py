from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FRONTEND_ORIGIN: str = "*"
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 10
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 100

settings = Settings()