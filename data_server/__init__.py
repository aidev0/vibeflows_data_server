"""
Data server package for workflow automation.
"""

from data_server.api.routes import DataServerAPI
from data_server.models.mongodb_client import MongoDBClient

__version__ = "0.1.0"
__all__ = ["DataServerAPI", "MongoDBClient"] 