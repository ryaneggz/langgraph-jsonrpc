"""Method registry for JSON-RPC 2.0 implementation.

This module provides a registry system for RPC methods, allowing for
decorative method registration and optional authentication integration.
"""

from typing import Any, Callable, Dict, List, Optional, Set
import logging
from functools import wraps

from fastapi import Depends
from app.deps.auth import AuthContext, auth_dependency

logger = logging.getLogger(__name__)

# Type alias for RPC method functions
RpcMethod = Callable[..., Any]
MethodDecorator = Callable[[RpcMethod], RpcMethod]


class MethodRegistry:
    """Registry for JSON-RPC 2.0 methods.
    
    Provides method registration, lookup, and metadata management
    for RPC methods with optional authentication support.
    """
    
    def __init__(self) -> None:
        """Initialize the method registry."""
        self._methods: Dict[str, RpcMethod] = {}
        self._method_metadata: Dict[str, Dict[str, Any]] = {}
        self._protected_methods: Set[str] = set()
    
    def method(
        self, 
        name: Optional[str] = None, 
        *, 
        description: Optional[str] = None,
        require_auth: bool = False
    ) -> MethodDecorator:
        """Decorator to register an RPC method.
        
        Args:
            name: Method name (defaults to function name)
            description: Method description for introspection
            require_auth: Whether method requires authentication
            
        Returns:
            Method decorator function
            
        Example:
            @registry.method("math.add", description="Add two numbers")
            def add(a: float, b: float) -> float:
                return a + b
        """
        def decorator(func: RpcMethod) -> RpcMethod:
            method_name = name or func.__name__
            
            if method_name in self._methods:
                logger.warning(f"Method '{method_name}' is being overridden")
            
            # Store method and metadata
            self._methods[method_name] = func
            self._method_metadata[method_name] = {
                "description": description or func.__doc__ or "No description available",
                "require_auth": require_auth,
                "function_name": func.__name__,
                "module": func.__module__
            }
            
            if require_auth:
                self._protected_methods.add(method_name)
            
            logger.debug(f"Registered RPC method: {method_name}")
            return func
        
        return decorator
    
    def get(self, name: str) -> RpcMethod:
        """Get a registered method by name.
        
        Args:
            name: Method name to look up
            
        Returns:
            The registered method function
            
        Raises:
            KeyError: If method is not registered
        """
        if name not in self._methods:
            available_methods = ", ".join(self._methods.keys()) or "none"
            raise KeyError(
                f"Method '{name}' not found. Available methods: {available_methods}"
            )
        
        return self._methods[name]
    
    def is_registered(self, name: str) -> bool:
        """Check if a method is registered.
        
        Args:
            name: Method name to check
            
        Returns:
            True if method is registered, False otherwise
        """
        return name in self._methods
    
    def requires_auth(self, name: str) -> bool:
        """Check if a method requires authentication.
        
        Args:
            name: Method name to check
            
        Returns:
            True if method requires auth, False otherwise
        """
        return name in self._protected_methods
    
    def get_method_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a registered method.
        
        Args:
            name: Method name
            
        Returns:
            Method metadata dictionary
            
        Raises:
            KeyError: If method is not registered
        """
        if name not in self._method_metadata:
            raise KeyError(f"No metadata found for method '{name}'")
        
        return self._method_metadata[name].copy()
    
    def list_methods(self) -> List[str]:
        """Get list of all registered method names.
        
        Returns:
            List of method names
        """
        return list(self._methods.keys())
    
    def get_methods_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered methods.
        
        Returns:
            Dictionary mapping method names to their metadata
        """
        return {
            name: metadata.copy() 
            for name, metadata in self._method_metadata.items()
        }
    
    def unregister(self, name: str) -> bool:
        """Unregister a method.
        
        Args:
            name: Method name to unregister
            
        Returns:
            True if method was unregistered, False if it wasn't registered
        """
        if name not in self._methods:
            return False
        
        del self._methods[name]
        del self._method_metadata[name]
        self._protected_methods.discard(name)
        
        logger.debug(f"Unregistered RPC method: {name}")
        return True
    
    def clear(self) -> None:
        """Clear all registered methods."""
        method_count = len(self._methods)
        self._methods.clear()
        self._method_metadata.clear()
        self._protected_methods.clear()
        
        logger.info(f"Cleared {method_count} registered methods")


def with_auth(func: RpcMethod) -> RpcMethod:
    """Decorator to inject authentication context into RPC methods.
    
    This decorator can be used with methods that need access to authentication
    context without requiring the registry to handle authentication directly.
    
    Args:
        func: The RPC method to wrap
        
    Returns:
        Wrapped method with auth context injection
        
    Example:
        @with_auth
        @registry.method("protected.action")
        def protected_action(data: str, auth: AuthContext) -> str:
            if not auth.user_id:
                raise PermissionError("Authentication required")
            return f"Hello, {auth.user_id}!"
    """
    @wraps(func)
    def wrapper(*args, auth: AuthContext = Depends(auth_dependency), **kwargs):
        return func(*args, auth=auth, **kwargs)
    
    return wrapper


# Global registry instance
registry = MethodRegistry()