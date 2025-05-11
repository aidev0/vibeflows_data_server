"""
Security module for API key authentication.
"""

import os
from dotenv import load_dotenv
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader

# Load environment variables
load_dotenv()

# Create API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Get API key from request header if provided."""
    return api_key if api_key else None 