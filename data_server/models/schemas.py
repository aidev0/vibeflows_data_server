"""
Schema models for request/response validation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator

class BaseDocument(BaseModel):
    """Base document model."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    creator_id: str  # ID of the user who created this document
    team_id: Optional[str] = None  # ID of the team this document belongs to

    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v, values):
        """Set updated_at to current time if not provided."""
        return v or datetime.utcnow()

class Identity(BaseModel):
    """User identity model."""
    provider: str
    user_id: str
    connection: str
    isSocial: bool = True

class User(BaseDocument):
    """User model."""
    user_id: str
    email: EmailStr
    email_verified: bool = False
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    identities: List[Identity] = Field(default_factory=list)
    name: str
    nickname: str
    picture: Optional[HttpUrl] = None
    last_ip: Optional[str] = None
    last_login: Optional[datetime] = None
    logins_count: int = 0
    blocked_for: List[str] = Field(default_factory=list)
    guardian_authenticators: List[str] = Field(default_factory=list)
    passkeys: List[str] = Field(default_factory=list)

    @validator('last_login', pre=True)
    def validate_last_login(cls, v):
        """Validate last_login timestamp."""
        if v and not isinstance(v, datetime):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid datetime format for last_login')
        return v

class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    name: str
    nickname: str
    picture: Optional[HttpUrl] = None

class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    email_verified: Optional[bool] = None
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    picture: Optional[HttpUrl] = None
    blocked_for: Optional[List[str]] = None

class Team(BaseDocument):
    """Team model."""
    name: str
    description: Optional[str] = None
    users: List[str] = Field(default_factory=list)  # List of user_ids in the team
    owner_id: str  # ID of the team owner
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TeamCreate(BaseModel):
    """Team creation model."""
    name: str
    description: Optional[str] = None
    users: List[str] = Field(default_factory=list)
    owner_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TeamUpdate(BaseModel):
    """Team update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    users: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class Chat(BaseDocument):
    """Chat model."""
    user_id: str
    session_id: str
    title: Optional[str] = None
    access_users: List[str] = Field(default_factory=list)  # List of user_ids that have access to this chat
    team_id: Optional[str] = None  # ID of the team this chat belongs to
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatCreate(BaseModel):
    """Chat creation model."""
    user_id: str
    session_id: str
    title: Optional[str] = None
    access_users: List[str] = Field(default_factory=list)
    team_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatUpdate(BaseModel):
    """Chat update model."""
    title: Optional[str] = None
    access_users: Optional[List[str]] = None
    team_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Session(BaseDocument):
    """Session model."""
    chat_id: str
    user_id: str
    timestamp: datetime
    device_id: str
    ip: str
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not isinstance(v, datetime):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid datetime format for timestamp')
        return v

class SessionCreate(BaseModel):
    """Session creation model."""
    chat_id: str
    user_id: str
    device_id: str
    ip: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SessionUpdate(BaseModel):
    """Session update model."""
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Message(BaseDocument):
    """Message model."""
    sender_id: str
    chat_id: str
    session_id: str
    timestamp: datetime
    text: str
    url: Optional[str] = None
    json: Optional[Dict[str, Any]] = None
    type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not isinstance(v, datetime):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid datetime format for timestamp')
        return v

    @validator('type')
    def validate_type(cls, v):
        """Validate message type."""
        valid_types = ['text', 'image', 'file', 'json', 'system']
        if v not in valid_types:
            raise ValueError(f'Invalid message type. Must be one of: {", ".join(valid_types)}')
        return v

class MessageCreate(BaseModel):
    """Message creation model."""
    sender_id: str
    chat_id: str
    session_id: str
    text: str
    url: Optional[str] = None
    json: Optional[Dict[str, Any]] = None
    type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('type')
    def validate_type(cls, v):
        """Validate message type."""
        valid_types = ['text', 'image', 'file', 'json', 'system']
        if v not in valid_types:
            raise ValueError(f'Invalid message type. Must be one of: {", ".join(valid_types)}')
        return v

class MessageUpdate(BaseModel):
    """Message update model."""
    text: Optional[str] = None
    url: Optional[str] = None
    json: Optional[Dict[str, Any]] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('type')
    def validate_type(cls, v):
        """Validate message type."""
        if v is not None:
            valid_types = ['text', 'image', 'file', 'json', 'system']
            if v not in valid_types:
                raise ValueError(f'Invalid message type. Must be one of: {", ".join(valid_types)}')
        return v

class Workflow(BaseDocument):
    """Workflow model."""
    user_id: str
    chat_id: str
    graph: Dict[str, Any]
    timestamp: datetime
    name: str
    version: str
    description: Optional[str] = None
    tech_spec: Optional[Dict[str, Any]] = None
    status: str = "draft"  # draft, active, completed, archived
    team_id: Optional[str] = None  # ID of the team this workflow belongs to
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not isinstance(v, datetime):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid datetime format for timestamp')
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate workflow status."""
        valid_statuses = ['draft', 'active', 'completed', 'archived']
        if v not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Version must be in semantic versioning format (e.g., 1.0.0)')
        return v

class WorkflowCreate(BaseModel):
    """Workflow creation model."""
    user_id: str
    chat_id: str
    graph: Dict[str, Any]
    name: str
    version: str
    description: Optional[str] = None
    tech_spec: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Version must be in semantic versioning format (e.g., 1.0.0)')
        return v

class WorkflowUpdate(BaseModel):
    """Workflow update model."""
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    tech_spec: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    graph: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        if v is not None:
            import re
            if not re.match(r'^\d+\.\d+\.\d+$', v):
                raise ValueError('Version must be in semantic versioning format (e.g., 1.0.0)')
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate workflow status."""
        if v is not None:
            valid_statuses = ['draft', 'active', 'completed', 'archived']
            if v not in valid_statuses:
                raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return v

class Agent(BaseDocument):
    """Agent model."""
    user_id: str
    name: str
    description: Optional[str] = None
    type: str  # e.g., "workflow_creator", "problem_understanding", "task_executor"
    version: str
    config: Dict[str, Any]
    system_message: str  # System message for the agent
    src: str  # Source code or implementation
    command: str  # Command to run the agent
    status: str = "active"  # active, inactive, archived
    capabilities: List[str] = Field(default_factory=list)
    team_id: Optional[str] = None  # ID of the team this agent belongs to
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_active: Optional[datetime] = None
    performance_metrics: Optional[Dict[str, Any]] = None

    @validator('type')
    def validate_type(cls, v):
        """Validate agent type."""
        valid_types = [
            "workflow_creator",
            "problem_understanding",
            "task_executor",
            "code_generator",
            "data_processor",
            "system"
        ]
        if v not in valid_types:
            raise ValueError(f'Invalid agent type. Must be one of: {", ".join(valid_types)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate agent status."""
        valid_statuses = ['active', 'inactive', 'archived']
        if v not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Version must be in semantic versioning format (e.g., 1.0.0)')
        return v

    @validator('last_active', pre=True)
    def validate_last_active(cls, v):
        """Validate last_active timestamp."""
        if v and not isinstance(v, datetime):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid datetime format for last_active')
        return v

class AgentCreate(BaseModel):
    """Agent creation model."""
    user_id: str
    name: str
    description: Optional[str] = None
    type: str
    version: str
    config: Dict[str, Any]
    system_message: str
    src: str
    command: str
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('type')
    def validate_type(cls, v):
        """Validate agent type."""
        valid_types = [
            "workflow_creator",
            "problem_understanding",
            "task_executor",
            "code_generator",
            "data_processor",
            "system"
        ]
        if v not in valid_types:
            raise ValueError(f'Invalid agent type. Must be one of: {", ".join(valid_types)}')
        return v

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Version must be in semantic versioning format (e.g., 1.0.0)')
        return v

class AgentUpdate(BaseModel):
    """Agent update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    system_message: Optional[str] = None
    src: Optional[str] = None
    command: Optional[str] = None
    status: Optional[str] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

    @validator('type')
    def validate_type(cls, v):
        """Validate agent type."""
        if v is not None:
            valid_types = [
                "workflow_creator",
                "problem_understanding",
                "task_executor",
                "code_generator",
                "data_processor",
                "system"
            ]
            if v not in valid_types:
                raise ValueError(f'Invalid agent type. Must be one of: {", ".join(valid_types)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate agent status."""
        if v is not None:
            valid_statuses = ['active', 'inactive', 'archived']
            if v not in valid_statuses:
                raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        if v is not None:
            import re
            if not re.match(r'^\d+\.\d+\.\d+$', v):
                raise ValueError('Version must be in semantic versioning format (e.g., 1.0.0)')
        return v 