"""Constants for JSON-RPC 2.0 implementation.

This module contains all magic numbers, strings, and constants used
throughout the JSON-RPC implementation to improve maintainability.
"""

# JSON-RPC Protocol Constants
JSONRPC_VERSION = "2.0"

# Standard JSON-RPC Error Codes
class ErrorCodes:
    """Standard JSON-RPC 2.0 error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # Server error range (reserved for implementation-defined server errors)
    SERVER_ERROR_MIN = -32099
    SERVER_ERROR_MAX = -32000


# HTTP Related Constants
class HttpConstants:
    """HTTP-related constants for the RPC transport."""
    DEFAULT_TIMEOUT_SECONDS = 30
    MAX_REQUEST_SIZE_BYTES = 1024 * 1024  # 1MB
    

# Logging Constants
class LogMessages:
    """Standardized log messages."""
    RPC_METHOD_ERROR = "Error executing RPC method"
    INVALID_JSON_PAYLOAD = "Invalid JSON payload received"
    METHOD_NOT_REGISTERED = "Method not found in registry"
    PARAMETER_VALIDATION_FAILED = "Parameter validation failed"
    BATCH_REQUEST_PROCESSED = "Batch request processed"
    NOTIFICATION_RECEIVED = "Notification received (no response expected)"