"""
MongoDB client for data server.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure, OperationFailure
from data_server.config import VALID_AGENT_TYPES, AGENT_CONFIGS

class MongoDBClient:
    """MongoDB client for data server."""
    
    def __init__(
        self,
        connection_string: str,
        database_name: str,
        cut_off_time: int = 30
    ):
        """Initialize MongoDB client.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Database name
            cut_off_time: Number of days to keep data
        """
        self.logger = logging.getLogger(__name__)
        self.connection_string = connection_string
        self.database_name = database_name
        self.cut_off_time = cut_off_time
        self.client = None
        self.db = None
        
        self._connect()
        self._initialize_collections()
        self._create_indexes()
        
    def _connect(self) -> None:
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.logger.info(f"Connected to MongoDB: {self.database_name}")
        except PyMongoError as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
            
    def _initialize_collections(self) -> None:
        """Initialize collections."""
        self.collections = {
            "users": self.db.users,
            "chats": self.db.chats,
            "sessions": self.db.sessions,
            "messages": self.db.messages,
            "workflows": self.db.workflows,
            "agents": self.db.agents,
            "teams": self.db.teams
        }
        
    def _create_indexes(self) -> None:
        """Create indexes for collections."""
        try:
            # Users collection indexes
            self.collections["users"].create_index([("email", ASCENDING)], unique=True)
            self.collections["users"].create_index([("user_id", ASCENDING)], unique=True)
            self.collections["users"].create_index([("created_at", DESCENDING)])
            
            # Chats collection indexes
            self.collections["chats"].create_index([("user_id", ASCENDING)])
            self.collections["chats"].create_index([("session_id", ASCENDING)])
            self.collections["chats"].create_index([("created_at", DESCENDING)])
            
            # Sessions collection indexes
            self.collections["sessions"].create_index([("user_id", ASCENDING)])
            self.collections["sessions"].create_index([("chat_id", ASCENDING)])
            self.collections["sessions"].create_index([("timestamp", DESCENDING)])
            self.collections["sessions"].create_index([("created_at", DESCENDING)])
            
            # Messages collection indexes
            self.collections["messages"].create_index([("chat_id", ASCENDING)])
            self.collections["messages"].create_index([("session_id", ASCENDING)])
            self.collections["messages"].create_index([("sender_id", ASCENDING)])
            self.collections["messages"].create_index([("timestamp", DESCENDING)])
            self.collections["messages"].create_index([("created_at", DESCENDING)])
            
            # Workflows collection indexes
            self.collections["workflows"].create_index([("user_id", ASCENDING)])
            self.collections["workflows"].create_index([("chat_id", ASCENDING)])
            self.collections["workflows"].create_index([("timestamp", DESCENDING)])
            self.collections["workflows"].create_index([("version", ASCENDING)])
            self.collections["workflows"].create_index([("status", ASCENDING)])
            self.collections["workflows"].create_index([("created_at", DESCENDING)])
            # Compound index for user_id and version
            self.collections["workflows"].create_index([
                ("user_id", ASCENDING),
                ("version", ASCENDING)
            ])
            # Compound index for chat_id and version
            self.collections["workflows"].create_index([
                ("chat_id", ASCENDING),
                ("version", ASCENDING)
            ])
            
            # Agents collection indexes
            self.collections["agents"].create_index([("user_id", ASCENDING)])
            self.collections["agents"].create_index([("name", ASCENDING)])
            self.collections["agents"].create_index([("type", ASCENDING)])
            self.collections["agents"].create_index([("version", ASCENDING)])
            self.collections["agents"].create_index([("status", ASCENDING)])
            self.collections["agents"].create_index([("last_active", DESCENDING)])
            self.collections["agents"].create_index([("created_at", DESCENDING)])
            # Compound index for user_id and type
            self.collections["agents"].create_index([
                ("user_id", ASCENDING),
                ("type", ASCENDING)
            ])
            # Compound index for user_id and version
            self.collections["agents"].create_index([
                ("user_id", ASCENDING),
                ("version", ASCENDING)
            ])
            # Compound index for type and status
            self.collections["agents"].create_index([
                ("type", ASCENDING),
                ("status", ASCENDING)
            ])
            
            # Teams collection indexes
            self.collections["teams"].create_index("owner_id")
            self.collections["teams"].create_index("users")
            
            self.logger.info("Created indexes for all collections")
        except PyMongoError as e:
            self.logger.error(f"Failed to create indexes: {str(e)}")
            raise
            
    def _convert_id(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB _id to string."""
        if document and "_id" in document:
            document["_id"] = str(document["_id"])
        return document
        
    def _convert_ids(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert MongoDB _id to string for multiple documents."""
        return [self._convert_id(doc) for doc in documents]
        
    def insert_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document into a collection.
        
        Args:
            collection: Collection name
            document: Document to insert
            
        Returns:
            Document ID
        """
        try:
            # Add timestamps if not present
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
            if "updated_at" not in document:
                document["updated_at"] = datetime.utcnow()
            if collection == "workflows" and "timestamp" not in document:
                document["timestamp"] = datetime.utcnow()
            if collection == "agents" and "last_active" not in document:
                document["last_active"] = datetime.utcnow()
                
            result = self.collections[collection].insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as e:
            self.logger.error(f"Failed to insert document: {str(e)}")
            raise
            
    def find_documents(
        self,
        collection: str,
        query: Dict[str, Any],
        user_id: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """Find documents in a collection.
        
        Args:
            collection: Collection name
            query: Query to find documents
            user_id: User ID for access control
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: Sort criteria
            
        Returns:
            List of documents
        """
        try:
            # Add access control based on user_id
            if user_id and user_id != "admin":
                if collection == "chats":
                    # For chats, return only user's chats or team chats
                    query["$or"] = [
                        {"user_id": user_id},
                        {"access_users": user_id},
                        {"team_id": {"$in": self._get_user_teams(user_id)}}
                    ]
                elif collection in ["workflows", "agents"]:
                    # For workflows and agents, return only user's data or team data
                    query["$or"] = [
                        {"user_id": user_id},
                        {"team_id": {"$in": self._get_user_teams(user_id)}}
                    ]
                elif collection in ["messages", "sessions"]:
                    # For messages and sessions, return only from user's chats or team chats
                    chat_ids = self._get_user_chat_ids(user_id)
                    query["chat_id"] = {"$in": chat_ids}
            
            cursor = self.collections[collection].find(query)
            
            if sort:
                cursor = cursor.sort(sort)
                
            cursor = cursor.skip(skip).limit(limit)
            return self._convert_ids(list(cursor))
        except PyMongoError as e:
            self.logger.error(f"Failed to find documents: {str(e)}")
            raise
            
    def update_document(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any]
    ) -> bool:
        """Update a document in a collection.
        
        Args:
            collection: Collection name
            query: Query to find document
            update: Update to apply
            
        Returns:
            True if document was updated
        """
        try:
            # Add updated_at timestamp
            update["$set"] = update.get("$set", {})
            update["$set"]["updated_at"] = datetime.utcnow()
            if collection == "workflows" and "timestamp" in update["$set"]:
                update["$set"]["timestamp"] = datetime.utcnow()
            if collection == "agents" and "last_active" in update["$set"]:
                update["$set"]["last_active"] = datetime.utcnow()
            
            result = self.collections[collection].update_one(query, update)
            return result.modified_count > 0
        except PyMongoError as e:
            self.logger.error(f"Failed to update document: {str(e)}")
            raise
            
    def delete_document(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a document from a collection.
        
        Args:
            collection: Collection name
            query: Query to find document
            
        Returns:
            True if document was deleted
        """
        try:
            result = self.collections[collection].delete_one(query)
            return result.deleted_count > 0
        except PyMongoError as e:
            self.logger.error(f"Failed to delete document: {str(e)}")
            raise
            
    def cleanup_old_data(self) -> None:
        """Clean up old data based on cut_off_time."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.cut_off_time)
            
            for collection in self.collections.values():
                result = collection.delete_many({"created_at": {"$lt": cutoff_date}})
                self.logger.info(f"Deleted {result.deleted_count} old documents from {collection.name}")
        except PyMongoError as e:
            self.logger.error(f"Failed to cleanup old data: {str(e)}")
            raise
            
    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.logger.info("Closed MongoDB connection")
            
    def register_agent(
        self,
        user_id: str,
        name: str,
        agent_type: str,
        version: str,
        config: Dict[str, Any],
        system_message: str,
        src: str,
        command: str,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new agent or update an existing one.
        
        This function handles both new agent registration and updates to existing agents.
        If an agent with the same name and type exists for the user, it will be updated
        with the new version and configuration.
        
        Args:
            user_id: User ID who owns the agent
            name: Agent name
            agent_type: Type of agent (e.g., "workflow_creator", "problem_understanding", "gemini")
            version: Agent version (must follow semantic versioning)
            config: Agent configuration
            system_message: System message for the agent
            src: Source code or implementation
            command: Command to run the agent
            description: Optional agent description
            capabilities: Optional list of agent capabilities
            metadata: Optional metadata about the agent
            
        Returns:
            Agent ID
            
        Raises:
            ValueError: If agent type is invalid or version format is incorrect
            PyMongoError: If database operation fails
        """
        try:
            # Validate agent type
            if agent_type not in VALID_AGENT_TYPES:
                raise ValueError(f"Invalid agent type. Must be one of: {', '.join(VALID_AGENT_TYPES)}")
            
            # Validate version format (semantic versioning)
            import re
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                raise ValueError("Version must be in semantic versioning format (e.g., 1.0.0)")
            
            # Merge default config with provided config based on agent type
            default_config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["default"])
            merged_config = {**default_config, **config}
            
            # Prepare agent document
            agent_doc = {
                "user_id": user_id,
                "name": name,
                "type": agent_type,
                "version": version,
                "config": merged_config,
                "system_message": system_message,
                "src": src,
                "command": command,
                "description": description,
                "capabilities": capabilities or [],
                "metadata": metadata or {},
                "status": "active",
                "last_active": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Check if agent already exists
            existing_agent = self.collections["agents"].find_one({
                "user_id": user_id,
                "name": name,
                "type": agent_type
            })
            
            if existing_agent:
                # Update existing agent
                self.logger.info(f"Updating existing agent: {name} ({agent_type})")
                result = self.collections["agents"].update_one(
                    {"_id": existing_agent["_id"]},
                    {
                        "$set": {
                            "version": version,
                            "config": merged_config,
                            "system_message": system_message,
                            "src": src,
                            "command": command,
                            "description": description,
                            "capabilities": capabilities or existing_agent.get("capabilities", []),
                            "metadata": metadata or existing_agent.get("metadata", {}),
                            "last_active": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                if result.modified_count > 0:
                    return str(existing_agent["_id"])
                else:
                    raise PyMongoError("Failed to update existing agent")
            else:
                # Insert new agent
                self.logger.info(f"Registering new agent: {name} ({agent_type})")
                result = self.collections["agents"].insert_one(agent_doc)
                return str(result.inserted_id)
                
        except DuplicateKeyError as e:
            self.logger.error(f"Duplicate agent registration: {str(e)}")
            raise ValueError("An agent with this name and type already exists for this user")
        except PyMongoError as e:
            self.logger.error(f"Failed to register agent: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during agent registration: {str(e)}")
            raise
            
    def get_agent_registration(
        self,
        user_id: str,
        name: str,
        agent_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get agent registration details.
        
        Args:
            user_id: User ID who owns the agent
            name: Agent name
            agent_type: Type of agent
            
        Returns:
            Agent document if found, None otherwise
        """
        try:
            agent = self.collections["agents"].find_one({
                "user_id": user_id,
                "name": name,
                "type": agent_type
            })
            return self._convert_id(agent) if agent else None
        except PyMongoError as e:
            self.logger.error(f"Failed to get agent registration: {str(e)}")
            raise
            
    def list_registered_agents(
        self,
        user_id: str,
        agent_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List registered agents for a user.
        
        Args:
            user_id: User ID
            agent_type: Optional filter by agent type
            status: Optional filter by agent status
            
        Returns:
            List of agent documents
        """
        try:
            query = {"user_id": user_id}
            if agent_type:
                query["type"] = agent_type
            if status:
                query["status"] = status
                
            return self._convert_ids(list(self.collections["agents"].find(
                query,
                sort=[("last_active", -1)]
            )))
        except PyMongoError as e:
            self.logger.error(f"Failed to list registered agents: {str(e)}")
            raise

    def _get_user_teams(self, user_id: str) -> List[str]:
        """Get list of team IDs that the user belongs to.
        
        Args:
            user_id: User ID
            
        Returns:
            List of team IDs
        """
        try:
            teams = self.collections["teams"].find(
                {"$or": [{"owner_id": user_id}, {"users": user_id}]},
                {"_id": 1}
            )
            return [team["_id"] for team in teams]
        except Exception as e:
            self.logger.error(f"Failed to get user teams: {str(e)}")
            return []

    def _get_user_chat_ids(self, user_id: str) -> List[str]:
        """Get list of chat IDs that the user has access to.
        
        Args:
            user_id: User ID
            
        Returns:
            List of chat IDs
        """
        try:
            # Get user's teams
            team_ids = self._get_user_teams(user_id)
            
            # Find chats where user is owner, has access, or is in team
            chats = self.collections["chats"].find(
                {
                    "$or": [
                        {"user_id": user_id},
                        {"access_users": user_id},
                        {"team_id": {"$in": team_ids}}
                    ]
                },
                {"_id": 1}
            )
            return [chat["_id"] for chat in chats]
        except Exception as e:
            self.logger.error(f"Failed to get user chat IDs: {str(e)}")
            return [] 