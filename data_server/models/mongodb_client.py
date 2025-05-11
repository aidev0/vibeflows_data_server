"""
MongoDB client for data server.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure, OperationFailure

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
            "messages": self.db.messages
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
            self.collections["chats"].create_index([("created_at", DESCENDING)])
            
            # Messages collection indexes
            self.collections["messages"].create_index([("chat_id", ASCENDING)])
            self.collections["messages"].create_index([("sender_id", ASCENDING)])
            self.collections["messages"].create_index([("timestamp", DESCENDING)])
            self.collections["messages"].create_index([("created_at", DESCENDING)])
            
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