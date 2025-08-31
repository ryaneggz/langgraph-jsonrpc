"""Health check RPC methods.

This module provides basic health check and system status methods.
"""

from app.rpc.registry import registry


@registry.method(
    name="ping",
    description="Simple health check that responds with 'pong'"
)
def ping() -> str:
    """Health check method that returns 'pong'.
    
    This is a simple connectivity test method that requires no parameters
    and always returns the same response.
    
    Returns:
        str: Always returns "pong"
        
    Example:
        Request: {"jsonrpc": "2.0", "method": "ping", "id": 1}
        Response: {"jsonrpc": "2.0", "result": "pong", "id": 1}
    """
    return "pong"
