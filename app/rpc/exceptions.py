"""Custom exceptions for JSON-RPC 2.0 implementation.

This module defines JSON-RPC specific exceptions that map to the standard
error codes defined in the JSON-RPC 2.0 specification.
"""

from typing import Any, Optional


class JsonRpcError(Exception):
    """Base class for all JSON-RPC errors.
    
    Attributes:
        code: The JSON-RPC error code
        message: A human-readable error message
        data: Additional error data (optional)
    """
    
    def __init__(self, code: int, message: str, data: Optional[Any] = None) -> None:
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class ParseError(JsonRpcError):
    """Invalid JSON was received by the server."""
    
    def __init__(self, data: Optional[Any] = None) -> None:
        super().__init__(
            code=-32700,
            message="Parse error",
            data=data
        )


class InvalidRequestError(JsonRpcError):
    """The JSON sent is not a valid Request object."""
    
    def __init__(self, data: Optional[Any] = None) -> None:
        super().__init__(
            code=-32600,
            message="Invalid Request",
            data=data
        )


class MethodNotFoundError(JsonRpcError):
    """The method does not exist / is not available."""
    
    def __init__(self, method_name: str, data: Optional[Any] = None) -> None:
        super().__init__(
            code=-32601,
            message=f"Method '{method_name}' not found",
            data=data
        )


class InvalidParamsError(JsonRpcError):
    """Invalid method parameter(s)."""
    
    def __init__(self, details: Optional[str] = None, data: Optional[Any] = None) -> None:
        message = "Invalid params"
        if details:
            message += f": {details}"
        super().__init__(
            code=-32602,
            message=message,
            data=data
        )


class InternalError(JsonRpcError):
    """Internal JSON-RPC error."""
    
    def __init__(self, details: Optional[str] = None, data: Optional[Any] = None) -> None:
        message = "Internal error"
        if details:
            message += f": {details}"
        super().__init__(
            code=-32603,
            message=message,
            data=data
        )


class ServerError(JsonRpcError):
    """Server error in the range -32099 to -32000."""
    
    def __init__(self, code: int, message: str, data: Optional[Any] = None) -> None:
        if not (-32099 <= code <= -32000):
            raise ValueError("Server error codes must be in range -32099 to -32000")
        super().__init__(code, message, data)