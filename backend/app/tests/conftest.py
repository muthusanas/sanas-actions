"""Pytest configuration and fixtures."""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import app.database as database


@pytest.fixture(autouse=True)
def isolated_test_db(tmp_path):
    """Use an isolated test database for each test.

    This fixture automatically applies to all tests and ensures
    database state doesn't leak between tests.
    """
    # Store original DB path
    original_db_path = database.DB_PATH

    # Set up test database path
    test_db_path = tmp_path / "test_sanas.db"
    database.DB_PATH = test_db_path

    # Initialize the test database
    database.init_db()

    yield test_db_path

    # Restore original DB path
    database.DB_PATH = original_db_path


@pytest.fixture
def sample_meeting_notes():
    """Sample meeting notes for testing."""
    return """
    Weekly team standup - January 10, 2025

    Attendees: John Smith, Sarah Lee, Muthu K, Anita Patel

    Action Items:
    - John to review the Q1 roadmap by Friday (Jan 15)
    - Sarah will update the API documentation next week
    - Muthu to fix the login bug ASAP
    - Anita should prepare the demo for the client meeting on Jan 20

    Notes:
    - Sprint planning for next week
    - Code review backlog needs attention
    """


@pytest.fixture
def sample_action_items():
    """Sample extracted action items."""
    return [
        {
            "id": 1,
            "title": "Review the Q1 roadmap",
            "assignee": "John Smith",
            "due_date": "Jan 15",
            "selected": True,
            "overdue": False,
        },
        {
            "id": 2,
            "title": "Update the API documentation",
            "assignee": "Sarah Lee",
            "due_date": None,
            "selected": True,
            "overdue": False,
        },
        {
            "id": 3,
            "title": "Fix the login bug",
            "assignee": "Muthu K",
            "due_date": None,
            "selected": True,
            "overdue": False,
        },
        {
            "id": 4,
            "title": "Prepare the demo for the client meeting",
            "assignee": "Anita Patel",
            "due_date": "Jan 20",
            "selected": True,
            "overdue": False,
        },
    ]


@pytest.fixture
def team_members():
    """Sample team members."""
    return [
        {"id": 1, "name": "John Smith", "initials": "JS", "slack_id": "U123", "jira_account_id": "jira-js"},
        {"id": 2, "name": "Sarah Lee", "initials": "SL", "slack_id": "U456", "jira_account_id": "jira-sl"},
        {"id": 3, "name": "Muthu K", "initials": "MK", "slack_id": "U789", "jira_account_id": "jira-mk"},
        {"id": 4, "name": "Anita Patel", "initials": "AP", "slack_id": "U012", "jira_account_id": "jira-ap"},
        {"id": 5, "name": "Raj Kumar", "initials": "RK", "slack_id": "U345", "jira_account_id": "jira-rk"},
    ]


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock = MagicMock()
    mock.messages.create = AsyncMock()
    return mock


@pytest.fixture
def mock_jira_client():
    """Mock Jira client for testing."""
    mock = MagicMock()
    mock.create_issue = AsyncMock()
    return mock


@pytest.fixture
def mock_slack_client():
    """Mock Slack client for testing."""
    mock = MagicMock()
    mock.chat_postMessage = AsyncMock()
    return mock
