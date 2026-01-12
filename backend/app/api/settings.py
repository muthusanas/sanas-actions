"""API routes for settings and team management."""
from fastapi import APIRouter, HTTPException

from app.models import (
    TeamMember,
    TeamMemberCreate,
    TeamMemberUpdate,
    UserSettings,
    IntegrationStatus,
    AnalyticsResponse,
    AnalyticsStats,
    TeamMemberStats,
    PendingActionItem,
    WeeklyTrend,
)
from app.database import get_pending_action_items, get_all_team_members, get_analytics_data
from app.services import (
    get_settings as service_get_settings,
    update_settings as service_update_settings,
    get_team_members as service_get_team_members,
    get_team_member as service_get_team_member,
    add_team_member as service_add_team_member,
    update_team_member as service_update_team_member,
    delete_team_member as service_delete_team_member,
    get_integration_status as service_get_integration_status,
)

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings", response_model=UserSettings)
async def get_settings():
    """Get current user settings.

    Returns:
        Current UserSettings.
    """
    return service_get_settings()


@router.put("/settings", response_model=UserSettings)
async def update_settings(settings: UserSettings):
    """Update user settings.

    Args:
        settings: New settings to apply.

    Returns:
        Updated UserSettings.
    """
    return service_update_settings(settings)


@router.get("/team", response_model=list[TeamMember])
async def get_team_members():
    """Get all team members.

    Returns:
        List of TeamMember objects.
    """
    return service_get_team_members()


@router.get("/team/{member_id}", response_model=TeamMember)
async def get_team_member(member_id: int):
    """Get a specific team member.

    Args:
        member_id: The team member's ID.

    Returns:
        TeamMember if found.

    Raises:
        HTTPException: If member not found.
    """
    member = service_get_team_member(member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return member


@router.post("/team", response_model=TeamMember, status_code=201)
async def create_team_member(member: TeamMemberCreate):
    """Create a new team member.

    Args:
        member: TeamMemberCreate data.

    Returns:
        Created TeamMember.
    """
    return service_add_team_member(member)


@router.patch("/team/{member_id}", response_model=TeamMember)
async def update_team_member(member_id: int, data: TeamMemberUpdate):
    """Update a team member.

    Args:
        member_id: The team member's ID.
        data: Fields to update.

    Returns:
        Updated TeamMember.

    Raises:
        HTTPException: If member not found.
    """
    result = service_update_team_member(member_id, data)

    if not result:
        raise HTTPException(status_code=404, detail="Team member not found")

    return result


@router.delete("/team/{member_id}", status_code=204)
async def delete_team_member(member_id: int):
    """Delete a team member.

    Args:
        member_id: The team member's ID.

    Raises:
        HTTPException: If member not found.
    """
    if not service_delete_team_member(member_id):
        raise HTTPException(status_code=404, detail="Team member not found")

    return None


@router.get("/integrations/status", response_model=IntegrationStatus)
async def get_integration_status():
    """Get the status of external integrations.

    Returns:
        IntegrationStatus with current connection states.
    """
    return service_get_integration_status()


def _get_initials(name: str) -> str:
    """Extract initials from a name."""
    return "".join(p[0].upper() for p in name.split() if p)[:2]


def _build_pending_items(items_data: list[dict]) -> list[PendingActionItem]:
    """Convert raw pending items data to PendingActionItem models."""
    return [
        PendingActionItem(
            id=item["id"],
            title=item["title"],
            assignee=item["assignee"],
            due_date=item["due_date"],
            overdue=bool(item["overdue"]),
        )
        for item in items_data
    ]


def _build_leaderboard(
    team_stats: list[dict], team_member_map: dict[str, str]
) -> list[TeamMemberStats]:
    """Build leaderboard from team stats with initials lookup."""
    return [
        TeamMemberStats(
            name=stat["assignee"],
            initials=team_member_map.get(stat["assignee"], _get_initials(stat["assignee"])),
            completed=stat["completed_this_week"],
            total=stat["total"],
            completion_percentage=float(stat["completion_rate"]),
        )
        for stat in team_stats
    ]


# Placeholder weekly trend data (would be computed from historical data in production)
WEEKLY_TREND_PLACEHOLDER = [
    WeeklyTrend(week="Mon", completed=4),
    WeeklyTrend(week="Tue", completed=6),
    WeeklyTrend(week="Wed", completed=5),
    WeeklyTrend(week="Thu", completed=8),
    WeeklyTrend(week="Fri", completed=10),
    WeeklyTrend(week="Sat", completed=2),
    WeeklyTrend(week="Sun", completed=1),
]


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get analytics data for dashboard.

    Returns:
        AnalyticsResponse with stats, pending items, and leaderboard.
    """
    pending_items = _build_pending_items(get_pending_action_items())
    team_members = get_all_team_members()
    team_member_map = {m["name"]: m["initials"] for m in team_members}
    analytics = get_analytics_data()

    return AnalyticsResponse(
        stats=AnalyticsStats(
            completed_this_week=analytics.get("completed_this_week", 0),
            pending_actions=len(pending_items),
            overdue_count=sum(1 for item in pending_items if item.overdue),
            active_team_members=analytics.get("active_members", len(team_members)),
        ),
        pending_items=pending_items,
        leaderboard=_build_leaderboard(analytics.get("team_stats", []), team_member_map),
        weekly_trend=WEEKLY_TREND_PLACEHOLDER,
    )
