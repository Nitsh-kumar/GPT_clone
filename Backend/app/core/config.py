from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Chatbot API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Tevathiya@12345"
    DB_NAME: str = "chatbot_db"
    
    # Constructed DATABASE_URL
    @property
    def DATABASE_URL(self) -> str:
        # URL encode the password to handle special characters
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD.strip('"'))
        return f"mysql+pymysql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()