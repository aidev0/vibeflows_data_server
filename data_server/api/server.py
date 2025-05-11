"""
Data server application.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseSettings

from ..models.mongodb_client import MongoDBClient
from .routes import DataServerAPI

class Settings(BaseSettings):
    """Application settings."""
    
    # MongoDB settings
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "workflow_automation"
    data_cut_off_days: int = 30
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        """Settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    """Get application settings."""
    # Try to load .env file from parent directory
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try to load from current directory
        load_dotenv()
    
    return Settings()

def create_app() -> FastAPI:
    """Create FastAPI application."""
    # Configure logging
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format=settings.log_format
    )
    logger = logging.getLogger(__name__)
    
    # Initialize MongoDB client
    mongodb_client = MongoDBClient(
        connection_string=settings.mongodb_uri,
        database_name=settings.mongodb_database,
        cut_off_time=settings.data_cut_off_days
    )
    
    # Create FastAPI app
    app = FastAPI(
        title="Workflow Automation Data Server",
        description="API for managing workflow automation data",
        version="1.0.0"
    )
    
    # Initialize API
    api = DataServerAPI(mongodb_client, app)
    
    logger.info(f"Server configured to run on {settings.host}:{settings.port}")
    return app

app = create_app()

def main():
    """Run the server."""
    settings = get_settings()
    uvicorn.run(
        "data_server.api.server:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

if __name__ == "__main__":
    main() 