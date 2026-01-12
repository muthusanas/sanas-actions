"""Notification models for Slack integration."""
from pydantic import BaseModel, Field


class SlackNotificationRequest(BaseModel):
    """Request schema for sending Slack notifications."""

    assignee: str = Field(..., description="Team member name to notify")
    message: str = Field(..., description="Notification message")
    ticket_key: str | None = Field(None, description="Associated Jira ticket key")


class ReminderRequest(BaseModel):
    """Request schema for sending reminders."""

    action_ids: list[int] = Field(..., description="IDs of action items to send reminders for")
    assignees: list[str] = Field(..., description="Team members to send reminders to")


class NotificationResponse(BaseModel):
    """Response schema for notification operations."""

    success: bool = Field(..., description="Whether the notification was sent successfully")
    message: str = Field(..., description="Status message")
    recipients: list[str] = Field(default_factory=list, description="List of notified recipients")


class BulkNotificationResponse(BaseModel):
    """Response schema for bulk notification operations."""

    total_sent: int = Field(..., description="Number of notifications sent successfully")
    total_failed: int = Field(..., description="Number of failed notifications")
    failed_recipients: list[str] = Field(
        default_factory=list, description="Recipients who failed to receive notifications"
    )
