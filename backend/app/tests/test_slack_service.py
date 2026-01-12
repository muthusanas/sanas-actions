"""Tests for the Slack notification service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import (
    SlackNotificationRequest,
    ReminderRequest,
    NotificationResponse,
    BulkNotificationResponse,
    TeamMember,
)
from app.services.slack_service import (
    SlackService,
    send_slack_notification,
    send_reminders,
)


class TestSlackService:
    """Tests for SlackService class."""

    @pytest.fixture
    def service(self):
        """Create a SlackService instance with test config."""
        return SlackService(bot_token="xoxb-test-token")

    @pytest.fixture
    def team_members(self):
        """Sample team members."""
        return [
            TeamMember(
                id=1,
                name="John Smith",
                initials="JS",
                slack_id="U123456",
                jira_account_id="jira-js",
            ),
            TeamMember(
                id=2,
                name="Sarah Lee",
                initials="SL",
                slack_id="U234567",
                jira_account_id="jira-sl",
            ),
        ]

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert service.bot_token == "xoxb-test-token"

    def test_service_builds_auth_header(self, service):
        """Test service builds correct auth header."""
        headers = service._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer xoxb-test-token"
        assert "Content-Type" in headers

    @pytest.mark.asyncio
    async def test_send_message_success(self, service):
        """Test sending a message successfully."""
        mock_response = {
            "ok": True,
            "channel": "U123456",
            "ts": "1234567890.123456",
        }

        with patch.object(
            service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.send_message("U123456", "Hello, world!")

        assert result.success is True

    @pytest.mark.asyncio
    async def test_send_message_failure(self, service):
        """Test handling message send failure."""
        mock_response = {
            "ok": False,
            "error": "channel_not_found",
        }

        with patch.object(
            service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.send_message("invalid", "Hello")

        assert result.success is False

    @pytest.mark.asyncio
    async def test_send_message_api_error(self, service):
        """Test handling API errors."""
        with patch.object(
            service,
            "_make_request",
            new_callable=AsyncMock,
            side_effect=Exception("API Error"),
        ):
            result = await service.send_message("U123456", "Hello")

        assert result.success is False
        assert "error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_send_notification_to_user(self, service, team_members):
        """Test sending notification to a specific user."""
        mock_response = {"ok": True, "channel": "U123456", "ts": "1234"}

        with patch.object(
            service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.send_notification(
                assignee="John Smith",
                message="You have a new task!",
                team_members=team_members,
            )

        assert result.success is True
        assert "John Smith" in result.recipients

    @pytest.mark.asyncio
    async def test_send_notification_user_not_found(self, service, team_members):
        """Test sending notification when user not found in team."""
        result = await service.send_notification(
            assignee="Unknown Person",
            message="Hello",
            team_members=team_members,
        )

        assert result.success is False
        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_send_notification_user_no_slack_id(self, service):
        """Test sending notification when user has no Slack ID."""
        team_members = [
            TeamMember(
                id=1,
                name="John Smith",
                initials="JS",
                slack_id=None,  # No Slack ID
                jira_account_id="jira-js",
            )
        ]

        result = await service.send_notification(
            assignee="John Smith",
            message="Hello",
            team_members=team_members,
        )

        assert result.success is False
        assert "slack" in result.message.lower()

    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self, service, team_members):
        """Test sending notifications to multiple users."""
        mock_response = {"ok": True, "channel": "test", "ts": "1234"}

        with patch.object(
            service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.send_bulk_notifications(
                assignees=["John Smith", "Sarah Lee"],
                message="Team reminder!",
                team_members=team_members,
            )

        assert result.total_sent == 2
        assert result.total_failed == 0

    @pytest.mark.asyncio
    async def test_send_bulk_notifications_partial_failure(self, service, team_members):
        """Test bulk notifications with some failures."""
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"ok": True, "channel": "test", "ts": "1234"}
            return {"ok": False, "error": "user_not_found"}

        with patch.object(service, "_make_request", side_effect=mock_request):
            result = await service.send_bulk_notifications(
                assignees=["John Smith", "Sarah Lee"],
                message="Reminder",
                team_members=team_members,
            )

        assert result.total_sent == 1
        assert result.total_failed == 1

    @pytest.mark.asyncio
    async def test_send_bulk_notifications_empty_list(self, service, team_members):
        """Test bulk notifications with empty assignee list."""
        result = await service.send_bulk_notifications(
            assignees=[],
            message="Hello",
            team_members=team_members,
        )

        assert result.total_sent == 0
        assert result.total_failed == 0

    @pytest.mark.asyncio
    async def test_send_ticket_notification(self, service, team_members):
        """Test sending ticket creation notification."""
        mock_response = {"ok": True, "channel": "U123456", "ts": "1234"}

        with patch.object(
            service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.send_ticket_notification(
                assignee="John Smith",
                ticket_key="SANAS-456",
                ticket_url="https://jira.example.com/SANAS-456",
                team_members=team_members,
            )

        assert result.success is True


class TestSlackNotificationHelpers:
    """Tests for helper functions."""

    @pytest.fixture
    def team_members(self):
        """Sample team members."""
        return [
            TeamMember(
                id=1,
                name="John Smith",
                initials="JS",
                slack_id="U123456",
            ),
        ]

    @pytest.mark.asyncio
    async def test_send_slack_notification_helper(self, team_members):
        """Test send_slack_notification helper function."""
        with patch("app.services.slack_service.SlackService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.send_notification = AsyncMock(
                return_value=NotificationResponse(
                    success=True,
                    message="Sent",
                    recipients=["John Smith"],
                )
            )
            mock_instance.close = AsyncMock()

            result = await send_slack_notification(
                assignee="John Smith",
                message="Hello",
                team_members=team_members,
            )

            mock_instance.send_notification.assert_called_once()
            assert result.success is True

    @pytest.mark.asyncio
    async def test_send_reminders_helper(self, team_members):
        """Test send_reminders helper function."""
        with patch("app.services.slack_service.SlackService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.send_bulk_notifications = AsyncMock(
                return_value=BulkNotificationResponse(
                    total_sent=1,
                    total_failed=0,
                    failed_recipients=[],
                )
            )
            mock_instance.close = AsyncMock()

            result = await send_reminders(
                assignees=["John Smith"],
                message="Reminder",
                team_members=team_members,
            )

            mock_instance.send_bulk_notifications.assert_called_once()
            assert result.total_sent == 1


class TestNotificationModels:
    """Tests for notification models."""

    def test_slack_notification_request(self):
        """Test SlackNotificationRequest model."""
        request = SlackNotificationRequest(
            assignee="John Smith",
            message="You have a task",
            ticket_key="SANAS-456",
        )
        assert request.assignee == "John Smith"
        assert request.message == "You have a task"
        assert request.ticket_key == "SANAS-456"

    def test_reminder_request(self):
        """Test ReminderRequest model."""
        request = ReminderRequest(
            action_ids=[1, 2, 3],
            assignees=["John Smith", "Sarah Lee"],
        )
        assert len(request.action_ids) == 3
        assert len(request.assignees) == 2

    def test_notification_response(self):
        """Test NotificationResponse model."""
        response = NotificationResponse(
            success=True,
            message="Notification sent",
            recipients=["John Smith"],
        )
        assert response.success is True
        assert "John Smith" in response.recipients

    def test_bulk_notification_response(self):
        """Test BulkNotificationResponse model."""
        response = BulkNotificationResponse(
            total_sent=5,
            total_failed=2,
            failed_recipients=["User1", "User2"],
        )
        assert response.total_sent == 5
        assert response.total_failed == 2
        assert len(response.failed_recipients) == 2
