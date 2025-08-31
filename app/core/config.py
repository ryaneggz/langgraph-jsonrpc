"""Application configuration management.

This module provides configuration settings using Pydantic BaseSettings
for environment variable management and validation.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    All settings can be overridden by environment variables with the same name.
    For example, APP_NAME can be set with the APP_NAME environment variable.
    """
    
    APP_NAME: str = Field(
        default="JSON-RPC 2.0 Server",
        description="Application name displayed in OpenAPI docs"
    )
    
    RPC_PATH: str = Field(
        default="/rpc",
        description="URL path for the JSON-RPC endpoint"
    )
    
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode with detailed error information"
    )
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()