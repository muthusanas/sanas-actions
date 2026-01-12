"""Tests for the actions API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import json

from app.main import app
from app.models import ActionItem


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_action_items():
    """Sample action items for testing."""
    return [
        ActionItem(
            id=1,
            title="Review Q1 roadmap",
            assignee="John Smith",
            due_date="Jan 15",
            selected=True,
            overdue=False,
        ),
        ActionItem(
            id=2,
            title="Update documentation",
            assignee="Sarah Lee",
            due_date=None,
            selected=True,
            overdue=False,
        ),
    ]


class TestExtractActionsEndpoint:
    """Tests for POST /api/actions/extract endpoint."""

    def test_extract_from_text_success(self, client, sample_action_items):
        """Test extracting action items from text."""
        with patch(
            "app.api.actions.extract_action_items_from_text",
            new_callable=AsyncMock,
            return_value=sample_action_items,
        ):
            response = client.post(
                "/api/actions/extract",
                json={"input_type": "text", "content": "Meeting notes with tasks"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "action_items" in data
        assert len(data["action_items"]) == 2

    def test_extract_from_text_missing_content(self, client):
        """Test extraction fails when content is missing for text type."""
        response = client.post(
            "/api/actions/extract",
            json={"input_type": "text"},
        )

        assert response.status_code == 400

    def test_extract_invalid_input_type(self, client):
        """Test extraction fails with invalid input type."""
        response = client.post(
            "/api/actions/extract",
            json={"input_type": "invalid", "content": "test"},
        )

        assert response.status_code == 422  # Validation error

    def test_extract_empty_text_returns_error(self, client):
        """Test extraction with empty text returns error."""
        response = client.post(
            "/api/actions/extract",
            json={"input_type": "text", "content": ""},
        )

        # Empty content should be treated as missing content
        assert response.status_code == 400


class TestExtractFromFileEndpoint:
    """Tests for POST /api/actions/extract-file endpoint."""

    def test_extract_from_file_success(self, client, sample_action_items):
        """Test extracting action items from uploaded file."""
        with patch(
            "app.api.actions.extract_action_items_from_text",
            new_callable=AsyncMock,
            return_value=sample_action_items,
        ):
            response = client.post(
                "/api/actions/extract-file",
                files={"file": ("meeting.txt", b"Meeting notes content", "text/plain")},
            )

        assert response.status_code == 200
        data = response.json()
        assert "action_items" in data

    def test_extract_from_file_no_file(self, client):
        """Test extraction fails when no file provided."""
        response = client.post("/api/actions/extract-file")

        assert response.status_code == 422  # Validation error

    def test_extract_from_file_invalid_type(self, client):
        """Test extraction fails with invalid file type."""
        response = client.post(
            "/api/actions/extract-file",
            files={"file": ("script.exe", b"binary content", "application/x-executable")},
        )

        assert response.status_code == 400

    def test_extract_from_file_too_large(self, client):
        """Test extraction fails when file exceeds size limit."""
        # Create content larger than MAX_FILE_SIZE (10MB + 1 byte)
        large_content = b"x" * (10 * 1024 * 1024 + 1)

        response = client.post(
            "/api/actions/extract-file",
            files={"file": ("large.txt", large_content, "text/plain")},
        )

        assert response.status_code == 413
        assert "10MB" in response.json()["detail"]

    def test_extract_from_file_at_size_limit(self, client, sample_action_items):
        """Test extraction succeeds when file is at size limit."""
        # Create content exactly at MAX_FILE_SIZE (10MB)
        content_at_limit = b"x" * (10 * 1024 * 1024)

        with patch(
            "app.api.actions.extract_action_items_from_text",
            new_callable=AsyncMock,
            return_value=sample_action_items,
        ):
            response = client.post(
                "/api/actions/extract-file",
                files={"file": ("exact.txt", content_at_limit, "text/plain")},
            )

        assert response.status_code == 200


class TestCreateTicketsEndpoint:
    """Tests for POST /api/actions/tickets endpoint."""

    def test_create_tickets_success(self, client):
        """Test creating Jira tickets successfully."""
        mock_response = MagicMock()
        mock_response.tickets = [
            MagicMock(
                key="SANAS-456",
                assignee="John Smith",
                url="https://jira.example.com/SANAS-456",
            )
        ]
        mock_response.failed = []

        with patch(
            "app.api.actions.create_jira_tickets",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = client.post(
                "/api/actions/tickets",
                json={
                    "action_ids": [1, 2],
                    "config": {"project": "SANAS", "issue_type": "Task"},
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data

    def test_create_tickets_empty_ids(self, client):
        """Test creating tickets with empty action IDs."""
        response = client.post(
            "/api/actions/tickets",
            json={"action_ids": []},
        )

        assert response.status_code == 400

    def test_create_tickets_with_default_config(self, client):
        """Test creating tickets uses default config."""
        mock_response = MagicMock()
        mock_response.tickets = []
        mock_response.failed = []

        with patch(
            "app.api.actions.create_jira_tickets",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = client.post(
                "/api/actions/tickets",
                json={"action_ids": [1]},
            )

        assert response.status_code == 200


class TestSendNotificationEndpoint:
    """Tests for POST /api/notifications/send endpoint."""

    def test_send_notification_success(self, client):
        """Test sending notification successfully."""
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message = "Sent"
        mock_response.recipients = ["John Smith"]

        with patch(
            "app.api.actions.send_slack_notification",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = client.post(
                "/api/notifications/send",
                json={"assignee": "John Smith", "message": "Hello!"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_send_notification_missing_fields(self, client):
        """Test sending notification with missing fields."""
        response = client.post(
            "/api/notifications/send",
            json={"assignee": "John Smith"},  # Missing message
        )

        assert response.status_code == 422


class TestSendRemindersEndpoint:
    """Tests for POST /api/notifications/reminders endpoint."""

    def test_send_reminders_success(self, client):
        """Test sending reminders successfully."""
        mock_response = MagicMock()
        mock_response.total_sent = 2
        mock_response.total_failed = 0
        mock_response.failed_recipients = []

        with patch(
            "app.api.actions.send_reminders",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = client.post(
                "/api/notifications/reminders",
                json={
                    "action_ids": [1, 2],
                    "assignees": ["John Smith", "Sarah Lee"],
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_sent"] == 2

    def test_send_reminders_empty_assignees(self, client):
        """Test sending reminders with empty assignees."""
        response = client.post(
            "/api/notifications/reminders",
            json={"action_ids": [1], "assignees": []},
        )

        assert response.status_code == 400


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
