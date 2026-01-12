# Sanas Backend

FastAPI backend for the Sanas Action Items Tracker - Extract action items from meeting notes and create Jira tickets.

## Features

- **Action Item Extraction**: Use Claude AI to extract action items from meeting notes (text or file upload)
- **Jira Integration**: Create Jira tickets from extracted action items
- **Slack Notifications**: Send notifications to team members when tickets are created
- **Team Management**: Manage team members with Slack/Jira mappings
- **Settings Management**: Configure reminders, notifications, and defaults

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Copy the environment example file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Claude API
ANTHROPIC_API_KEY=your-key

# Jira
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-token
JIRA_DEFAULT_PROJECT=SANAS

# Slack
SLACK_BOT_TOKEN=xoxb-your-token
```

## Running the Server

Development mode with auto-reload:
```bash
uv run python main.py
```

Or using uvicorn directly:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Actions
- `POST /api/actions/extract` - Extract action items from text
- `POST /api/actions/extract-file` - Extract action items from uploaded file
- `POST /api/actions/tickets` - Create Jira tickets

### Notifications
- `POST /api/notifications/send` - Send Slack notification
- `POST /api/notifications/reminders` - Send bulk reminders

### Settings
- `GET /api/settings` - Get user settings
- `PUT /api/settings` - Update user settings

### Team
- `GET /api/team` - List team members
- `POST /api/team` - Create team member
- `GET /api/team/{id}` - Get team member
- `PATCH /api/team/{id}` - Update team member
- `DELETE /api/team/{id}` - Delete team member

### Integrations
- `GET /api/integrations/status` - Get integration status

### Health
- `GET /health` - Health check

## Running Tests

Run all tests:
```bash
uv run pytest
```

Run with coverage:
```bash
uv run pytest --cov=app --cov-report=term-missing
```

Run specific test file:
```bash
uv run pytest app/tests/test_extraction_service.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── actions.py    # Action item endpoints
│   │   ├── settings.py   # Settings endpoints
│   │   └── dependencies.py
│   ├── models/           # Pydantic models
│   │   ├── action_item.py
│   │   ├── ticket.py
│   │   ├── notification.py
│   │   ├── settings.py
│   │   └── analytics.py
│   ├── services/         # Business logic
│   │   ├── extraction_service.py  # Claude AI integration
│   │   ├── jira_service.py        # Jira API integration
│   │   ├── slack_service.py       # Slack API integration
│   │   └── settings_service.py    # Settings management
│   ├── tests/            # Test files
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── main.py               # Entry point
├── pyproject.toml        # Project configuration
└── .env.example          # Environment template
```

## Development

The codebase follows TDD (Test-Driven Development) principles. All services have comprehensive test coverage.

### Adding a New Feature

1. Write tests first in `app/tests/`
2. Implement the feature to pass tests
3. Run `uv run pytest` to verify
4. Add API endpoints if needed

### Code Style

- Use type hints throughout
- Follow PEP 8 conventions
- Use async/await for I/O operations
