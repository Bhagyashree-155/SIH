from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "powergrid_tickets"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@powergrid.in"
    
    # Email Polling Configuration
    EMAIL_POLLING_INTERVAL: int = 300  # 5 minutes in seconds
    EMAIL_CREDENTIALS: List[dict] = [
        # Example format:
        # {
        #     "username": "support@powergrid.in",
        #     "password": "password",
        #     "imap_server": "imap.gmail.com"
        # }
    ]
    
    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # GLPI Integration
    GLPI_URL: str = ""
    GLPI_API_TOKEN: str = ""
    GLPI_APP_TOKEN: str = ""
    
    # Solman Integration
    SOLMAN_URL: str = ""
    SOLMAN_USERNAME: str = ""
    SOLMAN_PASSWORD: str = ""
    
    # AI/ML Configuration
    HUGGINGFACE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_PATH: str = "uploads/"
    UPLOAD_DIR: str = "uploads/"  # Alias for consistency with other code
    
    # Rasa Chatbot
    RASA_SERVER_URL: str = "http://localhost:5005"
    RASA_TOKEN: str = ""
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # SLA Defaults (in hours)
    DEFAULT_RESPONSE_TIME: int = 4
    DEFAULT_RESOLUTION_TIME: int = 24
    
    # Ticket settings
    TICKET_NUMBER_PREFIX: str = "PG"
    
    # Integration API Key for external systems
    INTEGRATION_API_KEY: str = "your-integration-api-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
