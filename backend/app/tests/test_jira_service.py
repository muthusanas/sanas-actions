"""Tests for the Jira ticket creation service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.models import (
    ActionItem,
    JiraConfig,
    CreatedTicket,
)
from app.services.jira_service import (
    JiraService,
    create_jira_tickets,
)


class TestJiraService:
    """Tests for JiraService class."""

    @pytest.fixture
    def service(self):
        """Create a JiraService instance with test config."""
        return JiraService(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test-token",
        )

    @pytest.fixture
    def action_items(self):
        """Sample action items for testing."""
        return [
            ActionItem(
                id=1,
                title="Review the Q1 roadmap",
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

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert service.base_url == "https://test.atlassian.net"
        assert service.email == "test@example.com"

    def test_service_builds_auth_header(self, service):
        """Test service builds correct auth header."""
        headers = service._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_create_ticket_success(self, service, action_items):
        """Test creating a single ticket successfully."""
        mock_response = {
            "id": "12345",
            "key": "SANAS-456",
            "self": "https://test.atlassian.net/rest/api/3/issue/12345",
        }

        with patch.object(
            service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.create_ticket(
                action_items[0], JiraConfig(project="SANAS", issue_type="Task")
            )

        assert isinstance(result, CreatedTicket)
        assert result.key == "SANAS-456"
        assert result.assignee == "John Smith"

    @pytest.mark.asyncio
    async def test_create_ticket_builds_correct_payload(self, service, action_items):
        """Test that create_ticket builds correct API payload."""
        config = JiraConfig(project="SANAS", issue_type="Task", label="meeting-action")

        with patch.object(service, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"key": "SANAS-1"}
            await service.create_ticket(action_items[0], config)

            call_args = mock_request.call_args
            payload = call_args[1]["json_data"]

            assert payload["fields"]["project"]["key"] == "SANAS"
            assert payload["fields"]["issuetype"]["name"] == "Task"
            assert payload["fields"]["summary"] == "Review the Q1 roadmap"
            assert "meeting-action" in payload["fields"]["labels"]

    @pytest.mark.asyncio
    async def test_create_tickets_batch(self, service, action_items):
        """Test creating multiple tickets."""
        mock_responses = [
            {"key": "SANAS-456"},
            {"key": "SANAS-457"},
        ]

        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            result = mock_responses[call_count]
            call_count += 1
            return result

        with patch.object(service, "_make_request", side_effect=mock_request):
            result = await service.create_tickets(
                action_items, JiraConfig(project="SANAS")
            )

        assert len(result.tickets) == 2
        assert result.tickets[0].key == "SANAS-456"
        assert result.tickets[1].key == "SANAS-457"
        assert len(result.failed) == 0

    @pytest.mark.asyncio
    async def test_create_tickets_handles_partial_failure(self, service, action_items):
        """Test handling partial failures in batch creation."""
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"key": "SANAS-456"}
            raise Exception("API Error")

        with patch.object(service, "_make_request", side_effect=mock_request):
            result = await service.create_tickets(
                action_items, JiraConfig(project="SANAS")
            )

        assert len(result.tickets) == 1
        assert result.tickets[0].key == "SANAS-456"
        assert len(result.failed) == 1
        assert result.failed[0] == 2  # ID of failed item

    @pytest.mark.asyncio
    async def test_create_ticket_with_empty_assignee(self, service):
        """Test creating ticket without assignee."""
        item = ActionItem(
            id=1,
            title="Unassigned task",
            assignee=None,
            due_date=None,
            selected=True,
            overdue=False,
        )

        with patch.object(service, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"key": "SANAS-1"}
            result = await service.create_ticket(item, JiraConfig())

        assert result.assignee is None

    @pytest.mark.asyncio
    async def test_create_tickets_with_empty_list(self, service):
        """Test creating tickets with empty list returns empty response."""
        result = await service.create_tickets([], JiraConfig())

        assert len(result.tickets) == 0
        assert len(result.failed) == 0


class TestCreateJiraTicketsHelper:
    """Tests for create_jira_tickets helper function."""

    @pytest.fixture
    def action_items(self):
        """Sample action items."""
        return [
            ActionItem(
                id=1,
                title="Test task",
                assignee="John",
                due_date=None,
                selected=True,
                overdue=False,
            )
        ]

    @pytest.mark.asyncio
    async def test_helper_delegates_to_service(self, action_items):
        """Test that helper creates service and calls create_tickets."""
        with patch("app.services.jira_service.JiraService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.create_tickets = AsyncMock(
                return_value=MagicMock(
                    tickets=[
                        CreatedTicket(
                            key="SANAS-1",
                            assignee="John",
                            url="https://test.atlassian.net/browse/SANAS-1",
                        )
                    ],
                    failed=[],
                )
            )
            mock_instance.close = AsyncMock()

            result = await create_jira_tickets(action_items, JiraConfig())

            mock_instance.create_tickets.assert_called_once()
            assert len(result.tickets) == 1


class TestJiraConfig:
    """Tests for JiraConfig model."""

    def test_default_values(self):
        """Test JiraConfig has correct defaults."""
        config = JiraConfig()
        assert config.project == "SANAS"
        assert config.issue_type == "Task"
        assert config.label == "meeting-action"

    def test_custom_values(self):
        """Test JiraConfig with custom values."""
        config = JiraConfig(project="INFRA", issue_type="Bug", label="sprint-planning")
        assert config.project == "INFRA"
        assert config.issue_type == "Bug"
        assert config.label == "sprint-planning"


class TestCreatedTicket:
    """Tests for CreatedTicket model."""

    def test_ticket_with_all_fields(self):
        """Test creating ticket with all fields."""
        ticket = CreatedTicket(
            key="SANAS-456",
            assignee="John Smith",
            url="https://test.atlassian.net/browse/SANAS-456",
        )
        assert ticket.key == "SANAS-456"
        assert ticket.assignee == "John Smith"
        assert ticket.url == "https://test.atlassian.net/browse/SANAS-456"

    def test_ticket_with_null_assignee(self):
        """Test creating ticket without assignee."""
        ticket = CreatedTicket(
            key="SANAS-456",
            assignee=None,
            url="https://test.atlassian.net/browse/SANAS-456",
        )
        assert ticket.assignee is None
