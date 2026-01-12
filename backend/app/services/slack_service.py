"""Service for sending Slack notifications."""
from typing import Any

import httpx

from app.config import settings
from app.models import (
    TeamMember,
    NotificationResponse,
    BulkNotificationResponse,
)


class SlackService:
    """Service for interacting with Slack API."""

    SLACK_API_BASE = "https://slack.com/api"

    def __init__(self, bot_token: str | None = None):
        """Initialize the Slack service."""
        self.bot_token = bot_token or settings.slack_bot_token
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Build authentication headers for Slack API."""
        return {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json",
        }

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.SLACK_API_BASE,
                headers=self._get_headers(),
                timeout=30.0,
            )
        return self._client

    async def _make_request(
        self, method: str, endpoint: str, json_data: dict | None = None
    ) -> dict[str, Any]:
        """Make an HTTP request to Slack API."""
        response = await self.client.request(method, endpoint, json=json_data)
        response.raise_for_status()
        return response.json()

    def _find_team_member(
        self, name: str, team_members: list[TeamMember]
    ) -> TeamMember | None:
        """Find a team member by name."""
        for member in team_members:
            if member.name.lower() == name.lower():
                return member
        return None

    async def send_message(
        self, channel: str, text: str, blocks: list[dict] | None = None
    ) -> NotificationResponse:
        """Send a message to a Slack channel or user.

        Args:
            channel: Channel ID or user ID to send to.
            text: Message text.
            blocks: Optional Slack blocks for rich formatting.

        Returns:
            NotificationResponse indicating success/failure.
        """
        try:
            payload = {
                "channel": channel,
                "text": text,
            }
            if blocks:
                payload["blocks"] = blocks

            response = await self._make_request(
                "POST", "/chat.postMessage", json_data=payload
            )

            if response.get("ok"):
                return NotificationResponse(
                    success=True,
                    message="Message sent successfully",
                    recipients=[channel],
                )
            else:
                return NotificationResponse(
                    success=False,
                    message=f"Failed to send message: {response.get('error', 'Unknown error')}",
                    recipients=[],
                )
        except Exception as e:
            return NotificationResponse(
                success=False,
                message=f"Error sending message: {str(e)}",
                recipients=[],
            )

    async def send_notification(
        self,
        assignee: str,
        message: str,
        team_members: list[TeamMember],
        ticket_key: str | None = None,
    ) -> NotificationResponse:
        """Send a notification to a specific team member.

        Args:
            assignee: Name of the team member to notify.
            message: Notification message.
            team_members: List of team members to look up Slack ID.
            ticket_key: Optional associated Jira ticket key.

        Returns:
            NotificationResponse indicating success/failure.
        """
        member = self._find_team_member(assignee, team_members)

        if not member:
            return NotificationResponse(
                success=False,
                message=f"Team member '{assignee}' not found",
                recipients=[],
            )

        if not member.slack_id:
            return NotificationResponse(
                success=False,
                message=f"Team member '{assignee}' has no Slack ID configured",
                recipients=[],
            )

        # Build message with ticket info if provided
        full_message = message
        if ticket_key:
            full_message = f"{message}\n\nTicket: {ticket_key}"

        result = await self.send_message(member.slack_id, full_message)

        if result.success:
            return NotificationResponse(
                success=True,
                message="Notification sent successfully",
                recipients=[assignee],
            )
        return result

    async def send_ticket_notification(
        self,
        assignee: str,
        ticket_key: str,
        ticket_url: str,
        team_members: list[TeamMember],
    ) -> NotificationResponse:
        """Send a ticket creation notification.

        Args:
            assignee: Name of the assignee.
            ticket_key: Jira ticket key.
            ticket_url: URL to the ticket.
            team_members: List of team members.

        Returns:
            NotificationResponse indicating success/failure.
        """
        message = (
            f"🎫 A new Jira ticket has been assigned to you!\n\n"
            f"*<{ticket_url}|{ticket_key}>*\n\n"
            f"Please review and take action."
        )
        return await self.send_notification(
            assignee=assignee,
            message=message,
            team_members=team_members,
            ticket_key=ticket_key,
        )

    async def send_bulk_notifications(
        self,
        assignees: list[str],
        message: str,
        team_members: list[TeamMember],
    ) -> BulkNotificationResponse:
        """Send notifications to multiple team members.

        Args:
            assignees: List of team member names.
            message: Notification message.
            team_members: List of team members for lookup.

        Returns:
            BulkNotificationResponse with success/failure counts.
        """
        if not assignees:
            return BulkNotificationResponse(
                total_sent=0,
                total_failed=0,
                failed_recipients=[],
            )

        sent_count = 0
        failed_count = 0
        failed_recipients = []

        for assignee in assignees:
            result = await self.send_notification(
                assignee=assignee,
                message=message,
                team_members=team_members,
            )

            if result.success:
                sent_count += 1
            else:
                failed_count += 1
                failed_recipients.append(assignee)

        return BulkNotificationResponse(
            total_sent=sent_count,
            total_failed=failed_count,
            failed_recipients=failed_recipients,
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


async def send_slack_notification(
    assignee: str,
    message: str,
    team_members: list[TeamMember],
    ticket_key: str | None = None,
) -> NotificationResponse:
    """Helper function to send a Slack notification.

    Args:
        assignee: Name of the team member.
        message: Notification message.
        team_members: List of team members.
        ticket_key: Optional ticket key.

    Returns:
        NotificationResponse with result.
    """
    service = SlackService()
    try:
        return await service.send_notification(
            assignee=assignee,
            message=message,
            team_members=team_members,
            ticket_key=ticket_key,
        )
    finally:
        await service.close()


async def send_reminders(
    assignees: list[str],
    message: str,
    team_members: list[TeamMember],
) -> BulkNotificationResponse:
    """Helper function to send reminders to multiple users.

    Args:
        assignees: List of team member names.
        message: Reminder message.
        team_members: List of team members.

    Returns:
        BulkNotificationResponse with results.
    """
    service = SlackService()
    try:
        return await service.send_bulk_notifications(
            assignees=assignees,
            message=message,
            team_members=team_members,
        )
    finally:
        await service.close()
