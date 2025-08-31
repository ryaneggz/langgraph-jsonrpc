from fastapi import APIRouter
from app.rpc.methods.math import AddParams
from app.rpc.registry import registry

router = APIRouter(prefix="/api", tags=["JSON-RPC Methods"])

@router.post("/ping", response_model=str, summary="Ping Method", description="Returns 'pong' to verify service is alive")
def ping_endpoint() -> str:
    fn = registry.get("ping")
    return fn()

@router.post("/math/add", response_model=float, summary="Math Add", description="Adds two numbers and returns the result")
def math_add_endpoint(params: AddParams) -> float:
    fn = registry.get("math.add")
    return fn(params)