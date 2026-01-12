"""Settings and team management models."""
from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    """Schema for a team member."""

    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., min_length=1, description="Team member name")
    initials: str = Field(..., min_length=1, max_length=3, description="Team member initials")
    slack_id: str | None = Field(None, description="Slack user ID")
    jira_account_id: str | None = Field(None, description="Jira account ID")
    email: str | None = Field(None, description="Email address")


class TeamMemberCreate(BaseModel):
    """Schema for creating a team member."""

    name: str = Field(..., min_length=1, description="Team member name")
    initials: str | None = Field(None, max_length=3, description="Team member initials")
    slack_id: str | None = None
    jira_account_id: str | None = None
    email: str | None = None


class TeamMemberUpdate(BaseModel):
    """Schema for updating a team member."""

    name: str | None = None
    initials: str | None = None
    slack_id: str | None = None
    jira_account_id: str | None = None
    email: str | None = None


class ReminderSettings(BaseModel):
    """Settings for reminders."""

    enabled: bool = Field(default=True, description="Whether reminders are enabled")
    frequency: str = Field(
        default="Weekly",
        description="Reminder frequency: 'Daily', 'Weekly', 'Bi-weekly'",
    )
    day: str = Field(default="Monday", description="Day of week for reminders")
    time: str = Field(default="9:00 AM", description="Time of day for reminders")


class NotificationSettings(BaseModel):
    """Settings for notifications."""

    on_create: bool = Field(default=True, description="Send notification on ticket creation")
    overdue_warnings: bool = Field(default=True, description="Highlight/notify overdue items")


class DefaultSettings(BaseModel):
    """Default values for ticket creation."""

    project: str = Field(default="SANAS", description="Default Jira project")
    issue_type: str = Field(default="Task", description="Default issue type")


class UserSettings(BaseModel):
    """Complete user settings."""

    reminders: ReminderSettings = Field(default_factory=ReminderSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    defaults: DefaultSettings = Field(default_factory=DefaultSettings)


class IntegrationStatus(BaseModel):
    """Status of external integrations."""

    jira_connected: bool = Field(default=False, description="Whether Jira is connected")
    slack_connected: bool = Field(default=False, description="Whether Slack is connected")
    jira_project: str | None = Field(None, description="Connected Jira project")
    slack_workspace: str | None = Field(None, description="Connected Slack workspace")
