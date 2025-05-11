"""
Configuration settings for the data server.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Admin user ID
ADMIN_ID = os.getenv("ADMIN_ID", "admin")

# MongoDB settings
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is required")

MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "workflow_automation")

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))
API_DEBUG = False

# Security settings
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Default agent settings
DEFAULT_AGENT_CONFIG: Dict[str, Any] = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
}

# Gemini agent settings
GEMINI_CONFIG: Dict[str, Any] = {
    "model": "gemini-2.5-pro-preview-05-06",
    "temperature": 0.7,
    "max_tokens": 4000,
    "top_p": 0.95,
    "top_k": 40,
    "safety_settings": {
        "harassment": "block_none",
        "hate_speech": "block_none",
        "sexually_explicit": "block_none",
        "dangerous_content": "block_none"
    },
    "generation_config": {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 4000,
        "candidate_count": 1
    },
    "model_config": {
        "version": "gemini-2.5-pro-preview-05-06",
        "type": "pro",
        "preview": True
    }
}

# Valid agent types
VALID_AGENT_TYPES = [
    "workflow_creator",
    "problem_understanding",
    "task_executor",
    "code_generator",
    "data_processor",
    "system",
    "gemini"
]

# Valid workflow statuses
VALID_WORKFLOW_STATUSES = [
    "draft",
    "active",
    "completed",
    "archived"
]

# Valid message types
VALID_MESSAGE_TYPES = [
    "text",
    "image",
    "file",
    "json",
    "system"
]

# Agent type configurations
AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "gemini": GEMINI_CONFIG,
    "default": DEFAULT_AGENT_CONFIG
}

class Settings:
    def __init__(self):
        self.ADMIN_ID = ADMIN_ID
        self.MONGODB_URI = MONGODB_URI
        self.MONGODB_DATABASE = MONGODB_DATABASE
        self.API_HOST = API_HOST
        self.API_PORT = API_PORT
        self.API_DEBUG = API_DEBUG
        self.JWT_SECRET = JWT_SECRET
        self.JWT_ALGORITHM = JWT_ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        self.DEFAULT_AGENT_CONFIG = DEFAULT_AGENT_CONFIG
        self.GEMINI_CONFIG = GEMINI_CONFIG
        self.VALID_AGENT_TYPES = VALID_AGENT_TYPES
        self.VALID_WORKFLOW_STATUSES = VALID_WORKFLOW_STATUSES
        self.VALID_MESSAGE_TYPES = VALID_MESSAGE_TYPES
        self.AGENT_CONFIGS = AGENT_CONFIGS
        self.DATA_CUT_OFF_DAYS = int(os.getenv("DATA_CUT_OFF_DAYS", "30"))

def get_settings():
    return Settings() 