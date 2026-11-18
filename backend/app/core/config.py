import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartHire"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database (Defaults to SQLite for instant zero-config startup, Postgres when configured)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smarthire.db")
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_smarthire_jwt_key_change_in_production_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # External APIs
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    LINKEDIN_API_KEY: str = os.getenv("LINKEDIN_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Ranking Weights
    BM25_WEIGHT: float = float(os.getenv("BM25_WEIGHT", "0.45"))
    COSINE_WEIGHT: float = float(os.getenv("COSINE_WEIGHT", "0.55"))
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    # Upload limits
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="allow")

settings = Settings()
