"""Logging configuration for the JSON-RPC server.

This module provides structured JSON logging setup for consistent
log formatting across the application.
"""

import logging
from typing import Optional

from pythonjsonlogger import jsonlogger
from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> None:
    """Setup structured JSON logging.
    
    Configures the root logger with JSON formatting for structured logging.
    This ensures consistent log format across all modules.
    
    Args:
        level: Log level override (defaults to settings.LOG_LEVEL)
    """
    # Determine log level
    log_level = level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Setup handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Set third-party library log levels to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={"log_level": log_level, "debug_mode": settings.DEBUG}
    )
