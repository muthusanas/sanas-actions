"""API routes for settings and team management."""
from fastapi import APIRouter, HTTPException

from app.models import (
    TeamMember,
    TeamMemberCreate,
    TeamMemberUpdate,
    UserSettings,
    IntegrationStatus,
)
from app.services import (
    get_settings as service_get_settings,
    update_settings as service_update_settings,
    get_team_members as service_get_team_members,
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
    from app.services.settings_service import _settings_service

    member = _settings_service.get_team_member(member_id)

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
