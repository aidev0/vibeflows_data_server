"""
Configuration settings for the data server (no Pydantic, just os.environ).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        # MongoDB settings
        self.MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "workflow_automation")
        self.DATA_CUT_OFF_DAYS = int(os.getenv("DATA_CUT_OFF_DAYS", "30"))
        # API settings
        self.API_KEY = os.getenv("DATA_SERVER_API_KEY", "changeme")
        self.ADMIN_ID = os.getenv("ADMIN_ID", "admin")
        # Server settings
        self.HOST = os.getenv("API_HOST", "0.0.0.0")
        self.PORT = int(os.getenv("API_PORT", "5000"))
        self.DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
        # Add any other settings as needed

def get_settings() -> Settings:
    return Settings() 