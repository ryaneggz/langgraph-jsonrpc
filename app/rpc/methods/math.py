"""Mathematical operation RPC methods.

This module provides basic mathematical operations through JSON-RPC.
"""

from pydantic import BaseModel, Field
from app.rpc.registry import registry


class AddParams(BaseModel):
    """Parameters for the add operation.
    
    Attributes:
        a: First number to add
        b: Second number to add
    """
    
    a: float = Field(
        ...,
        description="First number to add",
        examples=[1.0, 2.5, -3.14]
    )
    b: float = Field(
        ...,
        description="Second number to add",
        examples=[1.0, 2.5, -3.14]
    )


class SubtractParams(BaseModel):
    """Parameters for the subtract operation.
    
    Attributes:
        a: Number to subtract from (minuend)
        b: Number to subtract (subtrahend)
    """
    
    a: float = Field(
        ...,
        description="Number to subtract from (minuend)",
        examples=[10.0, 5.5, 100.0]
    )
    b: float = Field(
        ...,
        description="Number to subtract (subtrahend)",
        examples=[3.0, 2.5, 25.0]
    )


class MultiplyParams(BaseModel):
    """Parameters for the multiply operation.
    
    Attributes:
        a: First number to multiply
        b: Second number to multiply
    """
    
    a: float = Field(
        ...,
        description="First number to multiply",
        examples=[2.0, 3.5, -4.0]
    )
    b: float = Field(
        ...,
        description="Second number to multiply",
        examples=[5.0, 2.0, -3.0]
    )


@registry.method(
    name="math.add",
    description="Add two numbers and return the result"
)
def add(params: AddParams) -> float:
    """Add two numbers.
    
    Args:
        params: AddParams containing the two numbers to add
        
    Returns:
        float: The sum of the two numbers
        
    Example:
        Request: {
            "jsonrpc": "2.0",
            "method": "math.add",
            "params": {"a": 2.0, "b": 3.0},
            "id": 1
        }
        Response: {"jsonrpc": "2.0", "result": 5.0, "id": 1}
    """
    return params.a + params.b


@registry.method(
    name="math.subtract",
    description="Subtract two numbers and return the result"
)
def subtract(params: SubtractParams) -> float:
    """Subtract two numbers.
    
    Args:
        params: SubtractParams containing the numbers for subtraction
        
    Returns:
        float: The difference (a - b)
        
    Example:
        Request: {
            "jsonrpc": "2.0",
            "method": "math.subtract",
            "params": {"a": 10.0, "b": 3.0},
            "id": 1
        }
        Response: {"jsonrpc": "2.0", "result": 7.0, "id": 1}
    """
    return params.a - params.b


@registry.method(
    name="math.multiply",
    description="Multiply two numbers and return the result"
)
def multiply(params: MultiplyParams) -> float:
    """Multiply two numbers.
    
    Args:
        params: MultiplyParams containing the two numbers to multiply
        
    Returns:
        float: The product of the two numbers
        
    Example:
        Request: {
            "jsonrpc": "2.0",
            "method": "math.multiply",
            "params": {"a": 4.0, "b": 5.0},
            "id": 1
        }
        Response: {"jsonrpc": "2.0", "result": 20.0, "id": 1}
    """
    return params.a * params.b
