"""Analytics models."""
from pydantic import BaseModel, Field


class AnalyticsStats(BaseModel):
    """Analytics statistics."""

    completed_this_week: int = Field(default=0, description="Actions completed this week")
    pending_actions: int = Field(default=0, description="Number of pending actions")
    overdue_count: int = Field(default=0, description="Number of overdue actions")
    active_team_members: int = Field(default=0, description="Number of active team members")


class TeamMemberStats(BaseModel):
    """Statistics for a team member."""

    name: str = Field(..., description="Team member name")
    initials: str = Field(..., description="Team member initials")
    completed: int = Field(default=0, description="Number of completed actions")
    total: int = Field(default=0, description="Total assigned actions")
    completion_percentage: float = Field(
        default=0.0, description="Completion percentage (0-100)"
    )


class WeeklyTrend(BaseModel):
    """Weekly completion trend data point."""

    week: str = Field(..., description="Week label (e.g., 'W1', 'Jan 1')")
    completed: int = Field(default=0, description="Number of completed actions")


class PendingActionItem(BaseModel):
    """Pending action item for analytics."""

    id: int = Field(..., description="Action item ID")
    title: str = Field(..., description="Action item title")
    assignee: str | None = Field(None, description="Assigned team member name")
    due_date: str | None = Field(None, description="Due date")
    overdue: bool = Field(default=False, description="Whether item is overdue")


class AnalyticsResponse(BaseModel):
    """Complete analytics response."""

    stats: AnalyticsStats = Field(default_factory=AnalyticsStats)
    pending_items: list[PendingActionItem] = Field(
        default_factory=list, description="List of pending action items"
    )
    leaderboard: list[TeamMemberStats] = Field(
        default_factory=list, description="Team leaderboard sorted by completion"
    )
    weekly_trend: list[WeeklyTrend] = Field(
        default_factory=list, description="Weekly completion trend"
    )
