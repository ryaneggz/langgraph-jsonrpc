from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.rpc.transport import router as rpc_router
from app.docs.swagger import router as docs_router
import app.rpc.methods

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title=settings.APP_NAME,
        description="FastAPI JSON-RPC 2.0 Service with Swagger Documentation",
        version="0.1.0"
    )
    app.include_router(rpc_router, prefix=settings.RPC_PATH)
    app.include_router(docs_router)
    return app

app = create_app()
