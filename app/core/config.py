from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from typing import Optional, List, Any
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Book Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost", "http://localhost:3000", "http://localhost:8000"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            else:
                return [i.strip() for i in v.split(",")]
        return v

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "bookdb")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"

    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"

    @property
    def TEST_DATABASE_URL(self) -> Optional[str]:
        if self.TESTING:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/test_{self.POSTGRES_DB}"
        return None

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()