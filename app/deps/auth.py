"""Authentication and authorization dependencies.

This module provides authentication context and dependency injection
for securing JSON-RPC methods.
"""

from typing import List, Optional

from fastapi import Header, HTTPException, status
from pydantic import BaseModel, Field


class AuthContext(BaseModel):
    """Authentication context for RPC methods.
    
    Contains user information and permissions for the current request.
    
    Attributes:
        user_id: Unique identifier for the authenticated user
        scopes: List of permission scopes granted to the user
    """
    
    user_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the authenticated user"
    )
    scopes: List[str] = Field(
        default_factory=list,
        description="List of permission scopes granted to the user"
    )
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated.
        
        Returns:
            bool: True if user_id is not None
        """
        return self.user_id is not None
    
    def has_scope(self, required_scope: str) -> bool:
        """Check if user has the required permission scope.
        
        Args:
            required_scope: The scope to check for
            
        Returns:
            bool: True if user has the scope
        """
        return required_scope in self.scopes or "*" in self.scopes


async def auth_dependency(
    authorization: Optional[str] = Header(
        None, 
        description="Authorization header with Bearer token"
    )
) -> AuthContext:
    """FastAPI dependency for extracting authentication context.
    
    This is a simplified implementation for demonstration. In production,
    this should validate JWT tokens, API keys, or other authentication methods.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        AuthContext: Authentication context for the request
        
    Raises:
        HTTPException: If authentication fails
    """
    # Handle missing authorization header
    if authorization is None:
        return AuthContext(user_id=None, scopes=[])
    
    # Simple token validation (replace with proper implementation)
    if authorization == "Bearer devtoken":
        return AuthContext(
            user_id="dev_user",
            scopes=["rpc:all", "admin"]
        )
    elif authorization == "Bearer usertoken":
        return AuthContext(
            user_id="regular_user",
            scopes=["rpc:read"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
