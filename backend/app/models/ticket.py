"""Jira ticket models."""
from pydantic import BaseModel, Field


class JiraConfig(BaseModel):
    """Jira configuration for ticket creation."""

    project: str = Field(default="SANAS", description="Jira project key")
    issue_type: str = Field(default="Task", description="Jira issue type")
    label: str = Field(default="meeting-action", description="Label to apply to tickets")


class TicketCreateRequest(BaseModel):
    """Request schema for creating Jira tickets."""

    action_ids: list[int] = Field(..., description="IDs of action items to create tickets for")
    config: JiraConfig = Field(default_factory=JiraConfig, description="Jira configuration")


class CreatedTicket(BaseModel):
    """Schema for a created Jira ticket."""

    key: str = Field(..., description="Jira ticket key (e.g., 'SANAS-456')")
    assignee: str | None = Field(None, description="Assigned team member name")
    url: str = Field(..., description="URL to the Jira ticket")


class TicketCreateResponse(BaseModel):
    """Response schema for ticket creation."""

    tickets: list[CreatedTicket] = Field(..., description="List of created tickets")
    failed: list[int] = Field(
        default_factory=list, description="IDs of action items that failed to create tickets"
    )
