"""JSON-RPC 2.0 transport layer implementation.

This module handles the HTTP transport for JSON-RPC requests and responses,
including request parsing, method dispatch, and error handling.
"""

from typing import Any, Dict, List, Optional, Union
import inspect
import logging
import traceback

from fastapi import APIRouter, Request as HttpRequest
from pydantic import BaseModel, ValidationError

from app.rpc.constants import LogMessages
from app.rpc.exceptions import (
    InternalError,
    InvalidParamsError,
    InvalidRequestError,
    JsonRpcError,
    MethodNotFoundError,
    ParseError,
)
from app.rpc.registry import registry
from app.rpc.schema import Error as RpcError
from app.rpc.schema import Request as RpcRequest
from app.rpc.schema import Response as RpcResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def create_error_response(
    request_id: Optional[Union[str, int]], 
    error: JsonRpcError
) -> RpcResponse:
    """Create a JSON-RPC error response.
    
    Args:
        request_id: The ID from the original request (None for parse errors)
        error: The JsonRpcError that occurred
        
    Returns:
        RpcResponse with error details
    """
    rpc_error = RpcError(
        code=error.code,
        message=error.message,
        data=error.data
    )
    return RpcResponse(error=rpc_error, id=request_id)


def _get_method_signature(func: Any) -> inspect.Signature:
    """Get the signature of a method for parameter inspection."""
    return inspect.signature(func)


def _is_single_pydantic_parameter(signature: inspect.Signature) -> tuple[bool, Optional[type]]:
    """Check if method expects a single Pydantic BaseModel parameter.
    
    Returns:
        Tuple of (is_single_pydantic, model_class)
    """
    parameters = list(signature.parameters.values())
    if len(parameters) != 1:
        return False, None
        
    param = parameters[0]
    annotation = param.annotation
    
    if (
        annotation is not inspect._empty
        and isinstance(annotation, type)
        and issubclass(annotation, BaseModel)
    ):
        return True, annotation
        
    return False, None


def _call_method_with_params(
    method: Any, 
    params: Optional[Union[List[Any], Dict[str, Any]]]
) -> Any:
    """Call a method with the appropriate parameter mapping.
    
    Args:
        method: The method to call
        params: Parameters from the JSON-RPC request
        
    Returns:
        The result of the method call
        
    Raises:
        InvalidParamsError: If parameters are invalid
        ValidationError: If Pydantic validation fails
    """
    if params is None:
        return method()
        
    if isinstance(params, list):
        return method(*params)
        
    if isinstance(params, dict):
        signature = _get_method_signature(method)
        is_single_pydantic, model_class = _is_single_pydantic_parameter(signature)
        
        if is_single_pydantic:
            model_instance = model_class.model_validate(params)
            return method(model_instance)
        else:
            return method(**params)
    
    raise InvalidParamsError("Parameters must be an array, object, or null")


def handle_rpc_call(request: RpcRequest) -> Optional[RpcResponse]:
    """Handle a single JSON-RPC method call.
    
    Args:
        request: The validated JSON-RPC request
        
    Returns:
        RpcResponse for regular calls, None for notifications
    """
    is_notification = request.id is None
    
    try:
        # Get the method from registry
        try:
            method = registry.get(request.method)
        except KeyError:
            error = MethodNotFoundError(request.method)
            if is_notification:
                logger.warning(LogMessages.METHOD_NOT_REGISTERED, extra={"method": request.method})
                return None
            return create_error_response(request.id, error)
        
        # Execute the method
        try:
            result = _call_method_with_params(method, request.params)
            
            if is_notification:
                logger.info(LogMessages.NOTIFICATION_RECEIVED, extra={"method": request.method})
                return None
                
            return RpcResponse(result=result, id=request.id)
            
        except ValidationError as validation_error:
            error = InvalidParamsError(data=validation_error.errors())
            if is_notification:
                logger.warning(
                    LogMessages.PARAMETER_VALIDATION_FAILED, 
                    extra={"method": request.method, "errors": validation_error.errors()}
                )
                return None
            return create_error_response(request.id, error)
            
    except Exception as unexpected_error:
        logger.exception(
            LogMessages.RPC_METHOD_ERROR,
            extra={"method": request.method, "request_id": request.id}
        )
        
        error_data = {
            "type": type(unexpected_error).__name__,
            "details": str(unexpected_error)
        }
        
        # Include traceback in debug mode only
        # TODO: Add debug mode check from settings
        error_data["traceback"] = traceback.format_exc()
        
        error = InternalError(data=error_data)
        
        if is_notification:
            return None
            
        return create_error_response(request.id, error)


async def _parse_json_payload(http_request: HttpRequest) -> Any:
    """Parse JSON payload from HTTP request.
    
    Args:
        http_request: The FastAPI HTTP request
        
    Returns:
        Parsed JSON payload
        
    Raises:
        ParseError: If JSON parsing fails
    """
    try:
        return await http_request.json()
    except Exception as parse_error:
        logger.warning(LogMessages.INVALID_JSON_PAYLOAD, extra={"error": str(parse_error)})
        raise ParseError(data=str(parse_error))


def _validate_rpc_request(payload: Any) -> RpcRequest:
    """Validate a single JSON-RPC request.
    
    Args:
        payload: Raw request payload
        
    Returns:
        Validated RpcRequest
        
    Raises:
        InvalidRequestError: If request validation fails
    """
    try:
        return RpcRequest.model_validate(payload)
    except ValidationError as validation_error:
        raise InvalidRequestError(data=validation_error.errors())


def _process_batch_requests(batch_payload: List[Any]) -> List[Dict[str, Any]]:
    """Process a batch of JSON-RPC requests.
    
    Args:
        batch_payload: List of request payloads
        
    Returns:
        List of response dictionaries (empty if all notifications)
    """
    responses = []
    
    for item in batch_payload:
        try:
            request = _validate_rpc_request(item)
            response = handle_rpc_call(request)
            
            if response is not None:
                responses.append(response.model_dump())
                
        except InvalidRequestError as invalid_request:
            # Try to extract ID for error response
            request_id = None
            if isinstance(item, dict):
                request_id = item.get("id")
                
            error_response = create_error_response(request_id, invalid_request)
            responses.append(error_response.model_dump())
    
    logger.info(LogMessages.BATCH_REQUEST_PROCESSED, extra={"count": len(batch_payload)})
    return responses


def _process_single_request(payload: Any) -> Optional[Dict[str, Any]]:
    """Process a single JSON-RPC request.
    
    Args:
        payload: Single request payload
        
    Returns:
        Response dictionary or None for notifications
    """
    try:
        request = _validate_rpc_request(payload)
        response = handle_rpc_call(request)
        return response.model_dump() if response is not None else None
        
    except InvalidRequestError as invalid_request:
        # Try to extract ID for error response
        request_id = None
        if isinstance(payload, dict):
            request_id = payload.get("id")
            
        error_response = create_error_response(request_id, invalid_request)
        return error_response.model_dump()


@router.post("")
async def rpc_endpoint(http_request: HttpRequest) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
    """Main JSON-RPC 2.0 endpoint handler.
    
    Handles both single requests and batch requests according to the
    JSON-RPC 2.0 specification.
    
    Args:
        http_request: The incoming HTTP request
        
    Returns:
        JSON-RPC response, batch response, or empty string for notifications
    """
    try:
        payload = await _parse_json_payload(http_request)
    except ParseError as parse_error:
        # Parse errors cannot include request ID (unknown)
        error_response = create_error_response(None, parse_error)
        return error_response.model_dump()
    
    # Handle batch requests
    if isinstance(payload, list):
        responses = _process_batch_requests(payload)
        # JSON-RPC spec: return empty string if all requests were notifications
        return responses if responses else ""
    
    # Handle single request
    response = _process_single_request(payload)
    return response if response is not None else ""