# Data Server Schema Documentation

## Overview
This document describes the data models and schemas used in the Workflow Automation Data Server.

## Models

### User
- `user_id`: Unique identifier for the user
- `email`: User's email address
- `email_verified`: Whether the email is verified
- `name`: Full name
- `nickname`: Display name
- `picture`: Profile picture URL
- `last_login`: Last login timestamp
- `logins_count`: Number of logins
- `blocked_for`: List of reasons for blocking
- `guardian_authenticators`: List of guardian authenticators
- `passkeys`: List of passkeys

### Chat
- `user_id`: Owner of the chat
- `session_id`: Associated session
- `title`: Chat title
- `access_users`: List of user IDs with access to this chat
- `metadata`: Additional chat metadata

### Session
- `chat_id`: Associated chat
- `user_id`: Session owner
- `timestamp`: Session timestamp
- `device_id`: Device identifier
- `ip`: IP address
- `status`: Session status (active/inactive)
- `metadata`: Additional session metadata

### Message
- `sender_id`: Message sender
- `chat_id`: Associated chat
- `session_id`: Associated session
- `timestamp`: Message timestamp
- `text`: Message content
- `url`: Optional URL
- `json`: Optional JSON data
- `type`: Message type (text/image/file/json/system)
- `metadata`: Additional message metadata

### Workflow
- `user_id`: Workflow owner
- `chat_id`: Associated chat
- `graph`: Workflow graph
- `timestamp`: Workflow timestamp
- `name`: Workflow name
- `version`: Semantic version
- `description`: Workflow description
- `tech_spec`: Technical specifications
- `status`: Workflow status (draft/active/completed/archived)
- `metadata`: Additional workflow metadata

### Agent
- `user_id`: Agent owner
- `name`: Agent name
- `type`: Agent type (workflow_creator/problem_understanding/task_executor/code_generator/data_processor/system)
- `version`: Semantic version
- `config`: Agent configuration
- `system_message`: System message for the agent
- `src`: Source code or implementation
- `command`: Command to run the agent
- `status`: Agent status (active/inactive/archived)
- `capabilities`: List of agent capabilities
- `metadata`: Additional agent metadata
- `last_active`: Last activity timestamp
- `performance_metrics`: Agent performance metrics

## Access Control
- Regular users can only access their own data
- Users can access chats where they are either the owner or in the `access_users` list
- Admin users have full access to all data
- All API endpoints (except root) require API key authentication 