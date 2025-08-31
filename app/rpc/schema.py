"""Pydantic models for JSON-RPC 2.0 schema definitions.

This module contains the data models for JSON-RPC 2.0 requests, responses,
and errors according to the JSON-RPC 2.0 specification.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator
from app.rpc.constants import JSONRPC_VERSION

# Type alias for JSON-serializable values
JsonValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

# Type aliases for request/response IDs
RequestId = Union[str, int]
OptionalRequestId = Optional[RequestId]


class Error(BaseModel):
    """JSON-RPC 2.0 error object.
    
    Represents an error that occurred during request processing.
    
    Attributes:
        code: A number that indicates the error type
        message: A string providing a short description of the error
        data: A primitive or structured value with additional error information
    """
    
    code: int = Field(
        ...,
        description="A number that indicates the error type that occurred"
    )
    message: str = Field(
        ...,
        description="A string providing a short description of the error"
    )
    data: Optional[JsonValue] = Field(
        default=None,
        description="A primitive or structured value with additional error information"
    )


class Request(BaseModel):
    """JSON-RPC 2.0 request object.
    
    Represents a remote procedure call request.
    
    Attributes:
        jsonrpc: The JSON-RPC version (must be "2.0")
        method: The name of the method to be invoked
        params: Parameters to be passed to the method (optional)
        id: Request identifier. If None, this is a notification
    """
    
    jsonrpc: Literal["2.0"] = Field(
        default=JSONRPC_VERSION,
        description="The JSON-RPC version (must be exactly '2.0')"
    )
    method: str = Field(
        ...,
        min_length=1,
        description="The name of the method to be invoked"
    )
    params: Optional[Union[List[Any], Dict[str, Any]]] = Field(
        default=None,
        description="Parameters to be passed to the method (structured values)"
    )
    id: OptionalRequestId = Field(
        default=None,
        description="Request identifier. If omitted, this is a notification"
    )
    
    @model_validator(mode='after')
    def validate_request(self) -> 'Request':
        """Validate request structure including method name rules."""
        # Validate method name isn't empty (already handled by min_length)
        # Additional validation for reserved method names can go here
        if self.method.startswith('rpc.') and self.method not in {'rpc.ping', 'rpc.info'}:
            # Reserved namespace - could restrict or allow based on needs
            pass
        
        # Ensure jsonrpc field is exactly "2.0"
        if self.jsonrpc != "2.0":
            raise ValueError("JSON-RPC version must be '2.0'")
            
        return self


class Response(BaseModel):
    """JSON-RPC 2.0 response object.
    
    Represents the response to a remote procedure call.
    
    Attributes:
        jsonrpc: The JSON-RPC version (must be "2.0")
        result: The result of the method call (present on success)
        error: Error information (present on failure)
        id: The request identifier that this response corresponds to
    """
    
    jsonrpc: Literal["2.0"] = Field(
        default=JSONRPC_VERSION,
        description="The JSON-RPC version (must be exactly '2.0')"
    )
    result: Optional[JsonValue] = Field(
        default=None,
        description="The result of the method call if successful"
    )
    error: Optional[Error] = Field(
        default=None,
        description="Error information if the method call failed"
    )
    id: OptionalRequestId = Field(
        default=None,
        description="The request identifier that this response corresponds to"
    )
    
    @model_validator(mode='after')
    def validate_result_or_error(self) -> 'Response':
        """Ensure exactly one of result or error is present."""
        if self.result is not None and self.error is not None:
            raise ValueError("Response cannot have both result and error")
        if self.result is None and self.error is None:
            raise ValueError("Response must have either result or error")
        return self
    
    def model_dump(self, **kwargs) -> dict:
        """Serialize the response, excluding None fields."""
        data = super().model_dump(**kwargs)
        # Remove None fields to keep responses clean
        return {k: v for k, v in data.items() if v is not None}


# Type alias for batch requests
BatchRequest = List[Request]
BatchResponse = List[Response]