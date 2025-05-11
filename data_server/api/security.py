"""
Security module for API key verification and user data access.
"""

from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Any, Dict
from data_server.models.mongodb_client import MongoDBClient
from data_server.config import get_settings

settings = get_settings()
API_KEY_NAME = "X-Data-Server-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the request header.
    Returns the user ID associated with the API key.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    
    # In a real application, you would verify the API key against a database
    # For now, we'll use a simple check against the settings
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Return the user ID associated with this API key
    # In a real application, you would look this up in a database
    return "admin"  # For now, we'll just return "admin"

async def get_user_data(user_id: str, data: Any) -> Any:
    """
    Filter data based on user permissions.
    For now, we'll just return all data for admin users.
    """
    if user_id == "admin":
        return data
    
    # For non-admin users, filter the data based on their permissions
    # This is a placeholder for more sophisticated permission checking
    if isinstance(data, list):
        return [item for item in data if item.get("user_id") == user_id]
    elif isinstance(data, dict):
        return data if data.get("user_id") == user_id else None
    return data 