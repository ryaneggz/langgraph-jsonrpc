"""FastAPI application factory for JSON-RPC 2.0 server.

This module creates and configures the FastAPI application instance
with JSON-RPC routing and logging setup.
"""

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.rpc.transport import router as rpc_router

# Import to register methods
import app.rpc.methods  # noqa: F401


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Sets up logging, creates the FastAPI instance with proper configuration,
    and includes the JSON-RPC router.
    
    Returns:
        FastAPI: Configured application instance
    """
    setup_logging()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="JSON-RPC 2.0 server implementation with FastAPI",
        version="1.0.0"
    )
    
    # Include the RPC router
    app.include_router(rpc_router, prefix=settings.RPC_PATH)
    
    return app


# Create the application instance
app = create_app()
