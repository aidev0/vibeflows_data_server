# Data Server

A FastAPI-based data server for managing workflow automation data with MongoDB.

## Features

- MongoDB integration for data persistence
- RESTful API endpoints for managing:
  - Chats
  - Sessions
  - Messages
  - Workflows
- Automatic data cleanup
- Health check endpoint
- CORS support
- Environment-based configuration

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
cp .env.template .env
```

4. Configure your environment variables in `.env`:
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=workflow_automation
DATA_CUT_OFF_DAYS=30

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Running the Server

Start the server:
```bash
uvicorn data_server.api.server:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative Documentation: http://localhost:8000/redoc

## API Endpoints

### Root
- `GET /`: API information

### Health Check
- `GET /health`: Service health status

### Chats
- `POST /chats/`: Create a new chat
- `GET /chats/{chat_id}`: Get a chat by ID
- `GET /chats/`: List chats with optional filtering

### Sessions
- `POST /sessions/`: Create a new session
- `GET /sessions/{session_id}`: Get a session by ID
- `GET /sessions/`: List sessions with optional filtering

### Messages
- `POST /messages/`: Create a new message
- `GET /messages/`: Get messages for a chat

### Workflows
- `POST /workflows/`: Create a new workflow
- `GET /workflows/{workflow_id}`: Get a workflow by ID
- `GET /workflows/`: List workflows for a user

### Cleanup
- `POST /cleanup/`: Clean up old data

## Development

### Project Structure
```
data_server/
├── api/
│   ├── routes.py
│   └── server.py
├── models/
│   └── mongodb_client.py
├── utils/
├── .env.template
├── README.md
└── requirements.txt
```

### Adding New Features

1. Add new models in `models/`
2. Add new routes in `api/routes.py`
3. Update environment variables in `.env.template`
4. Update documentation in `README.md`

## License

MIT 