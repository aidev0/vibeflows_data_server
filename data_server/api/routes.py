"""
API routes for the data server.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

from fastapi import FastAPI, HTTPException, Query, status, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from data_server.models.mongodb_client import MongoDBClient
from data_server.models.schemas import (
    User, UserCreate, UserUpdate,
    Chat, ChatCreate, ChatUpdate,
    Session, SessionCreate, SessionUpdate,
    Message, MessageCreate, MessageUpdate,
    Workflow, WorkflowCreate, WorkflowUpdate,
    Agent, AgentCreate, AgentUpdate,
    Team, TeamCreate, TeamUpdate
)
from data_server.api.security import verify_api_key, get_user_data

class DataServerAPI:
    """API endpoints for data server."""
    
    def __init__(
        self,
        mongodb_client: MongoDBClient,
        app: Optional[FastAPI] = None
    ):
        """Initialize API.
        
        Args:
            mongodb_client: MongoDB client instance
            app: Optional FastAPI app instance
        """
        self.logger = logging.getLogger(__name__)
        self.mongodb = mongodb_client
        self.app = app or FastAPI(
            title="Workflow Automation Data Server",
            description="API for managing workflow automation data",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.router = APIRouter(prefix="/api/v1")
        self._setup_routes()
        
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        # Root endpoint
        @self.app.get("/")
        async def root() -> Dict[str, Any]:
            """Root endpoint with API documentation."""
            try:
                # Get schema documentation from models
                schema_docs = {
                    "User": User.__doc__,
                    "Chat": Chat.__doc__,
                    "Session": Session.__doc__,
                    "Message": Message.__doc__,
                    "Workflow": Workflow.__doc__,
                    "Agent": Agent.__doc__,
                    "Team": Team.__doc__
                }
                
                return {
                    "name": "Workflow Automation Data Server",
                    "version": "1.0.0",
                    "status": "running",
                    "schemas": schema_docs,
                    "endpoints": {
                        "users": "/users/",
                        "chats": "/chats/",
                        "sessions": "/sessions/",
                        "messages": "/messages/",
                        "workflows": "/workflows/",
                        "agents": "/agents/",
                        "teams": "/teams/",
                        "docs": "/docs",
                        "redoc": "/redoc"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to get schema documentation: {str(e)}")
                return {
                    "name": "Workflow Automation Data Server",
                    "version": "1.0.0",
                    "status": "running",
                    "error": "Failed to load schema documentation",
                    "endpoints": {
                        "users": "/users/",
                        "chats": "/chats/",
                        "sessions": "/sessions/",
                        "messages": "/messages/",
                        "workflows": "/workflows/",
                        "agents": "/agents/",
                        "teams": "/teams/",
                        "docs": "/docs",
                        "redoc": "/redoc"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        # Health check endpoint
        @self.app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """Health check endpoint."""
            try:
                # Test MongoDB connection
                self.mongodb.db.command("ping")
                return {
                    "status": "healthy",
                    "database": "connected",
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service unhealthy: {str(e)}"
                )

        # User routes
        @self.router.get("/users/{user_id}", response_model=User, dependencies=[Depends(verify_api_key)])
        async def get_user(user_id: str):
            user = await self.mongodb.get_user(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

        @self.app.get("/users/", response_model=List[User])
        async def get_users(
            user_id: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """Get users. If user_id is admin_id, return all users; otherwise, return only the user's own info."""
            try:
                if user_id == os.environ.get("ADMIN_ID"):
                    # Admin can see all users
                    return self.mongodb.find_documents("users", {})
                else:
                    # Non-admin users only see their own info
                    return self.mongodb.find_documents("users", {"user_id": user_id})
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Team routes
        @self.router.get("/teams/{team_id}", response_model=Team, dependencies=[Depends(verify_api_key)])
        async def get_team(team_id: str, user_id: str):
            team = await self.mongodb.get_team(team_id)
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")
            return await get_user_data(user_id, team)

        @self.router.get("/teams", response_model=List[Team], dependencies=[Depends(verify_api_key)])
        async def get_teams(user_id: str):
            teams = await self.mongodb.get_teams()
            return await get_user_data(user_id, teams)

        # Chat routes
        @self.router.get("/chats/{chat_id}", response_model=Chat, dependencies=[Depends(verify_api_key)])
        async def get_chat(chat_id: str, user_id: str):
            chat = await self.mongodb.get_chat(chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            return await get_user_data(user_id, chat)

        @self.router.get("/chats", response_model=List[Chat], dependencies=[Depends(verify_api_key)])
        async def get_chats(user_id: str):
            chats = await self.mongodb.get_chats()
            return await get_user_data(user_id, chats)

        # Message routes
        @self.router.get("/messages/{message_id}", response_model=Message, dependencies=[Depends(verify_api_key)])
        async def get_message(message_id: str, user_id: str):
            message = await self.mongodb.get_message(message_id)
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")
            return await get_user_data(user_id, message)

        @self.router.get("/messages", response_model=List[Message], dependencies=[Depends(verify_api_key)])
        async def get_messages(user_id: str):
            messages = await self.mongodb.get_messages()
            return await get_user_data(user_id, messages)

        # Workflow routes
        @self.router.get("/workflows/{workflow_id}", response_model=Workflow, dependencies=[Depends(verify_api_key)])
        async def get_workflow(workflow_id: str, user_id: str):
            workflow = await self.mongodb.get_workflow(workflow_id)
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return await get_user_data(user_id, workflow)

        @self.router.get("/workflows", response_model=List[Workflow], dependencies=[Depends(verify_api_key)])
        async def get_workflows(user_id: str):
            workflows = await self.mongodb.get_workflows()
            return await get_user_data(user_id, workflows)

        # Agent routes
        @self.router.get("/agents/{agent_id}", response_model=Agent, dependencies=[Depends(verify_api_key)])
        async def get_agent(agent_id: str, user_id: str):
            agent = await self.mongodb.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
            return await get_user_data(user_id, agent)

        @self.router.get("/agents", response_model=List[Agent], dependencies=[Depends(verify_api_key)])
        async def get_agents(user_id: str):
            agents = await self.mongodb.get_agents()
            return await get_user_data(user_id, agents)

        # Add the router to the app
        self.app.include_router(self.router)
        
        # User endpoints
        @self.app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
        async def create_user(
            user: UserCreate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Create a new user."""
            try:
                user_data = user.dict()
                user_id = self.mongodb.insert_document("users", user_data)
                return {"id": user_id, **user_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/users/{user_id}", response_model=User)
        async def update_user(
            user_id: str,
            user: UserUpdate,
            user_id_dep: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Update a user."""
            try:
                update_data = user.dict(exclude_unset=True)
                if not update_data:
                    raise HTTPException(status_code=400, detail="No update data provided")
                
                result = self.mongodb.update_document("users", {"_id": user_id}, update_data)
                if not result:
                    raise HTTPException(status_code=404, detail="User not found")
                
                return self.mongodb.find_documents("users", {"_id": user_id})[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user(
            user_id: str,
            user_id_dep: str = Depends(verify_api_key)
        ) -> None:
            """Delete a user."""
            try:
                result = self.mongodb.delete_document("users", {"_id": user_id})
                if not result:
                    raise HTTPException(status_code=404, detail="User not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Chat endpoints
        @self.app.post("/chats/", response_model=Chat, status_code=status.HTTP_201_CREATED)
        async def create_chat(
            chat: ChatCreate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Create a new chat."""
            try:
                chat_data = chat.dict()
                chat_id = self.mongodb.insert_document("chats", chat_data)
                return {"id": chat_id, **chat_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.put("/chats/{chat_id}", response_model=Chat)
        async def update_chat(
            chat_id: str,
            chat: ChatUpdate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Update a chat."""
            try:
                update_data = chat.dict(exclude_unset=True)
                if not update_data:
                    raise HTTPException(status_code=400, detail="No update data provided")
                
                result = self.mongodb.update_document("chats", {"_id": chat_id}, update_data)
                if not result:
                    raise HTTPException(status_code=404, detail="Chat not found")
                
                return self.mongodb.find_documents("chats", {"_id": chat_id})[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_chat(
            chat_id: str,
            user_id: str = Depends(verify_api_key)
        ) -> None:
            """Delete a chat."""
            try:
                result = self.mongodb.delete_document("chats", {"_id": chat_id})
                if not result:
                    raise HTTPException(status_code=404, detail="Chat not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/chats/", response_model=List[Chat])
        async def list_chats(
            user_id: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """List chats with optional filtering."""
            try:
                query = {}
                return self.mongodb.find_documents(
                    "chats",
                    query,
                    user_id=user_id,
                    sort=[("created_at", -1)]
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # Session endpoints
        @self.app.post("/sessions/", response_model=Session, status_code=status.HTTP_201_CREATED)
        async def create_session(
            session: SessionCreate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Create a new session."""
            try:
                session_data = session.dict()
                session_data["timestamp"] = datetime.utcnow()
                session_id = self.mongodb.insert_document("sessions", session_data)
                return {"id": session_id, **session_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/sessions/{session_id}", response_model=Session)
        async def get_session(
            session_id: str,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Get a session by ID."""
            try:
                sessions = self.mongodb.find_documents("sessions", {"_id": session_id})
                if not sessions:
                    raise HTTPException(status_code=404, detail="Session not found")
                return sessions[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/sessions/{session_id}", response_model=Session)
        async def update_session(
            session_id: str,
            session: SessionUpdate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Update a session."""
            try:
                update_data = session.dict(exclude_unset=True)
                if not update_data:
                    raise HTTPException(status_code=400, detail="No update data provided")
                
                result = self.mongodb.update_document("sessions", {"_id": session_id}, update_data)
                if not result:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                return self.mongodb.find_documents("sessions", {"_id": session_id})[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_session(
            session_id: str,
            user_id: str = Depends(verify_api_key)
        ) -> None:
            """Delete a session."""
            try:
                result = self.mongodb.delete_document("sessions", {"_id": session_id})
                if not result:
                    raise HTTPException(status_code=404, detail="Session not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/sessions/", response_model=List[Session])
        async def list_sessions(
            user_id: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """List sessions with optional filtering."""
            try:
                query = {}
                return self.mongodb.find_documents(
                    "sessions",
                    query,
                    user_id=user_id,
                    sort=[("timestamp", -1)]
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # Message endpoints
        @self.app.post("/messages/", response_model=Message, status_code=status.HTTP_201_CREATED)
        async def create_message(
            message: MessageCreate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Create a new message."""
            try:
                message_data = message.dict()
                message_data["timestamp"] = datetime.utcnow()
                message_id = self.mongodb.insert_document("messages", message_data)
                return {"id": message_id, **message_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.put("/messages/{message_id}", response_model=Message)
        async def update_message(
            message_id: str,
            message: MessageUpdate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Update a message."""
            try:
                update_data = message.dict(exclude_unset=True)
                if not update_data:
                    raise HTTPException(status_code=400, detail="No update data provided")
                
                result = self.mongodb.update_document("messages", {"_id": message_id}, update_data)
                if not result:
                    raise HTTPException(status_code=404, detail="Message not found")
                
                return self.mongodb.find_documents("messages", {"_id": message_id})[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_message(
            message_id: str,
            user_id: str = Depends(verify_api_key)
        ) -> None:
            """Delete a message."""
            try:
                result = self.mongodb.delete_document("messages", {"_id": message_id})
                if not result:
                    raise HTTPException(status_code=404, detail="Message not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/messages/", response_model=List[Message])
        async def list_messages(
            user_id: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """List messages with optional filtering."""
            try:
                query = {}
                return self.mongodb.find_documents(
                    "messages",
                    query,
                    user_id=user_id,
                    sort=[("timestamp", -1)]
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # Workflow endpoints
        @self.app.post("/workflows/", response_model=Workflow, status_code=status.HTTP_201_CREATED)
        async def create_workflow(
            workflow: WorkflowCreate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Create a new workflow."""
            try:
                workflow_data = workflow.dict()
                workflow_id = self.mongodb.insert_document("workflows", workflow_data)
                return {"id": workflow_id, **workflow_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.put("/workflows/{workflow_id}", response_model=Workflow)
        async def update_workflow(
            workflow_id: str,
            workflow: WorkflowUpdate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Update a workflow."""
            try:
                update_data = workflow.dict(exclude_unset=True)
                if not update_data:
                    raise HTTPException(status_code=400, detail="No update data provided")
                
                result = self.mongodb.update_document("workflows", {"_id": workflow_id}, update_data)
                if not result:
                    raise HTTPException(status_code=404, detail="Workflow not found")
                
                return self.mongodb.find_documents("workflows", {"_id": workflow_id})[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_workflow(
            workflow_id: str,
            user_id: str = Depends(verify_api_key)
        ) -> None:
            """Delete a workflow."""
            try:
                result = self.mongodb.delete_document("workflows", {"_id": workflow_id})
                if not result:
                    raise HTTPException(status_code=404, detail="Workflow not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/workflows/", response_model=List[Workflow])
        async def list_workflows(
            user_id: str,
            status: Optional[str] = None,
            limit: int = Query(100, ge=1, le=1000),
            skip: int = Query(0, ge=0),
            user_id_dep: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """List workflows with optional filtering."""
            try:
                query = {}
                if status:
                    query["status"] = status
                return self.mongodb.find_documents(
                    "workflows",
                    query,
                    user_id=user_id,
                    limit=limit,
                    skip=skip,
                    sort=[("timestamp", -1)]
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # Agent endpoints
        @self.app.post("/agents/", response_model=Agent, status_code=status.HTTP_201_CREATED)
        async def create_agent(
            agent: AgentCreate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Create a new agent."""
            try:
                agent_data = agent.dict()
                agent_id = self.mongodb.insert_document("agents", agent_data)
                return {"id": agent_id, **agent_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.put("/agents/{agent_id}", response_model=Agent)
        async def update_agent(
            agent_id: str,
            agent: AgentUpdate,
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Update an agent."""
            try:
                update_data = agent.dict(exclude_unset=True)
                if not update_data:
                    raise HTTPException(status_code=400, detail="No update data provided")
                
                result = self.mongodb.update_document("agents", {"_id": agent_id}, update_data)
                if not result:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                return self.mongodb.find_documents("agents", {"_id": agent_id})[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_agent(
            agent_id: str,
            user_id: str = Depends(verify_api_key)
        ) -> None:
            """Delete an agent."""
            try:
                result = self.mongodb.delete_document("agents", {"_id": agent_id})
                if not result:
                    raise HTTPException(status_code=404, detail="Agent not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/agents/", response_model=List[Agent])
        async def list_agents(
            user_id: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """List agents with optional filtering."""
            try:
                query = {}
                return self.mongodb.find_documents(
                    "agents",
                    query,
                    user_id=user_id,
                    sort=[("last_active", -1)]
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # Agent registration endpoint
        @self.app.post("/agents/register/", response_model=Agent, status_code=status.HTTP_201_CREATED)
        async def register_agent(
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
            metadata: Optional[Dict[str, Any]] = None,
            user_id_dep: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Register a new agent or update an existing one."""
            try:
                agent_id = self.mongodb.register_agent(
                    user_id=user_id,
                    name=name,
                    agent_type=agent_type,
                    version=version,
                    config=config,
                    system_message=system_message,
                    src=src,
                    command=command,
                    description=description,
                    capabilities=capabilities,
                    metadata=metadata
                )
                
                # Get the registered agent
                agent = self.mongodb.get_agent_registration(user_id, name, agent_type)
                if not agent:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to retrieve registered agent"
                    )
                    
                return agent
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.logger.error(f"Failed to register agent: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/agents/register/{user_id}/{name}/{agent_type}", response_model=Agent)
        async def get_agent_registration(
            user_id: str,
            name: str,
            agent_type: str,
            user_id_dep: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Get agent registration details."""
            try:
                agent = self.mongodb.get_agent_registration(user_id, name, agent_type)
                if not agent:
                    raise HTTPException(status_code=404, detail="Agent registration not found")
                return agent
            except Exception as e:
                self.logger.error(f"Failed to get agent registration: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/agents/register/{user_id}", response_model=List[Agent])
        async def list_registered_agents(
            user_id: str,
            agent_type: Optional[str] = None,
            status: Optional[str] = None,
            user_id_dep: str = Depends(verify_api_key)
        ) -> List[Dict[str, Any]]:
            """List registered agents for a user."""
            try:
                return self.mongodb.list_registered_agents(
                    user_id=user_id,
                    agent_type=agent_type,
                    status=status
                )
            except Exception as e:
                self.logger.error(f"Failed to list registered agents: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        # Cleanup endpoint
        @self.app.post("/cleanup/")
        async def cleanup_old_data(
            user_id: str = Depends(verify_api_key)
        ) -> Dict[str, Any]:
            """Clean up old data."""
            try:
                self.mongodb.cleanup_old_data()
                return {
                    "status": "success",
                    "message": "Cleanup completed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # Team endpoints
        @self.app.post("/teams", response_model=Team)
        async def create_team(
            team: TeamCreate,
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> Team:
            """Create a new team."""
            try:
                # Set owner_id to current user
                team_data = team.dict()
                team_data["owner_id"] = user_id
                team_data["created_at"] = datetime.utcnow()
                team_data["updated_at"] = datetime.utcnow()
                
                # Add owner to users list if not already present
                if user_id not in team_data["users"]:
                    team_data["users"].append(user_id)
                
                result = db.collections["teams"].insert_one(team_data)
                team_data["_id"] = result.inserted_id
                
                return Team(**team_data)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/teams", response_model=List[Team])
        async def list_teams(
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> List[Team]:
            """List teams that the user is a member of."""
            try:
                teams = db.find_documents(
                    "teams",
                    {"$or": [{"owner_id": user_id}, {"users": user_id}]},
                    user_id=user_id
                )
                return [Team(**team) for team in teams]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/teams/{team_id}", response_model=Team)
        async def get_team(
            team_id: str,
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> Team:
            """Get team details."""
            try:
                team = db.collections["teams"].find_one({"_id": team_id})
                if not team:
                    raise HTTPException(status_code=404, detail="Team not found")
                
                # Check if user has access to team
                if user_id != "admin" and user_id not in team["users"] and user_id != team["owner_id"]:
                    raise HTTPException(status_code=403, detail="Not authorized to access this team")
                
                return Team(**team)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/teams/{team_id}", response_model=Team)
        async def update_team(
            team_id: str,
            team_update: TeamUpdate,
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> Team:
            """Update team details."""
            try:
                # Check if team exists and user is owner
                team = db.collections["teams"].find_one({"_id": team_id})
                if not team:
                    raise HTTPException(status_code=404, detail="Team not found")
                
                if user_id != "admin" and user_id != team["owner_id"]:
                    raise HTTPException(status_code=403, detail="Only team owner can update team")
                
                # Update team
                update_data = team_update.dict(exclude_unset=True)
                update_data["updated_at"] = datetime.utcnow()
                
                result = db.collections["teams"].update_one(
                    {"_id": team_id},
                    {"$set": update_data}
                )
                
                if result.modified_count == 0:
                    raise HTTPException(status_code=400, detail="No changes made to team")
                
                # Get updated team
                updated_team = db.collections["teams"].find_one({"_id": team_id})
                return Team(**updated_team)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/teams/{team_id}")
        async def delete_team(
            team_id: str,
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> dict:
            """Delete a team."""
            try:
                # Check if team exists and user is owner
                team = db.collections["teams"].find_one({"_id": team_id})
                if not team:
                    raise HTTPException(status_code=404, detail="Team not found")
                
                if user_id != "admin" and user_id != team["owner_id"]:
                    raise HTTPException(status_code=403, detail="Only team owner can delete team")
                
                # Delete team
                result = db.collections["teams"].delete_one({"_id": team_id})
                if result.deleted_count == 0:
                    raise HTTPException(status_code=400, detail="Failed to delete team")
                
                return {"message": "Team deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/teams/{team_id}/users/{member_id}")
        async def add_team_member(
            team_id: str,
            member_id: str,
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> dict:
            """Add a user to a team."""
            try:
                # Check if team exists and user is owner
                team = db.collections["teams"].find_one({"_id": team_id})
                if not team:
                    raise HTTPException(status_code=404, detail="Team not found")
                
                if user_id != "admin" and user_id != team["owner_id"]:
                    raise HTTPException(status_code=403, detail="Only team owner can add members")
                
                # Add user to team
                result = db.collections["teams"].update_one(
                    {"_id": team_id},
                    {"$addToSet": {"users": member_id}}
                )
                
                if result.modified_count == 0:
                    raise HTTPException(status_code=400, detail="User already in team or failed to add")
                
                return {"message": "User added to team successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/teams/{team_id}/users/{member_id}")
        async def remove_team_member(
            team_id: str,
            member_id: str,
            user_id: str = Depends(verify_api_key),
            db: MongoDBClient = Depends()
        ) -> dict:
            """Remove a user from a team."""
            try:
                # Check if team exists and user is owner
                team = db.collections["teams"].find_one({"_id": team_id})
                if not team:
                    raise HTTPException(status_code=404, detail="Team not found")
                
                if user_id != "admin" and user_id != team["owner_id"]:
                    raise HTTPException(status_code=403, detail="Only team owner can remove members")
                
                # Don't allow removing the owner
                if member_id == team["owner_id"]:
                    raise HTTPException(status_code=400, detail="Cannot remove team owner")
                
                # Remove user from team
                result = db.collections["teams"].update_one(
                    {"_id": team_id},
                    {"$pull": {"users": member_id}}
                )
                
                if result.modified_count == 0:
                    raise HTTPException(status_code=400, detail="User not in team or failed to remove")
                
                return {"message": "User removed from team successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance."""
        return self.app 