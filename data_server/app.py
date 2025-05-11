"""
Run the data server from the root directory.
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from data_server.api.routes import DataServerAPI
from data_server.models.mongodb_client import MongoDBClient
from data_server.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Initialize MongoDB client
mongodb_client = MongoDBClient(
    connection_string=settings.MONGODB_URI,
    database_name=settings.MONGODB_DATABASE,
    cut_off_time=settings.DATA_CUT_OFF_DAYS
)

# Initialize FastAPI app
app = FastAPI(
    title="Workflow Automation Data Server",
    description="API for managing workflow automation data",
    version="1.0.0"
)

# Initialize API
api = DataServerAPI(mongodb_client, app)

# Get the FastAPI app instance
app = api.get_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port) 