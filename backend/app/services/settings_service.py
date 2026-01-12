"""Service for managing settings and team members."""
from app.config import settings as app_settings
from app.models import (
    TeamMember,
    TeamMemberCreate,
    TeamMemberUpdate,
    UserSettings,
    ReminderSettings,
    NotificationSettings,
    DefaultSettings,
    IntegrationStatus,
)


class SettingsService:
    """Service for managing user settings and team members."""

    def __init__(self):
        """Initialize the settings service."""
        self._settings = UserSettings(
            reminders=ReminderSettings(),
            notifications=NotificationSettings(),
            defaults=DefaultSettings(),
        )
        self._team_members: list[TeamMember] = []
        self._next_member_id = 1

    def get_settings(self) -> UserSettings:
        """Get the current user settings.

        Returns:
            UserSettings object with current settings.
        """
        return self._settings

    def update_settings(self, new_settings: UserSettings) -> UserSettings:
        """Update user settings.

        Args:
            new_settings: New settings to apply.

        Returns:
            Updated UserSettings object.
        """
        self._settings = new_settings
        return self._settings

    def get_team_members(self) -> list[TeamMember]:
        """Get all team members.

        Returns:
            List of TeamMember objects.
        """
        return self._team_members

    def get_team_member(self, member_id: int) -> TeamMember | None:
        """Get a team member by ID.

        Args:
            member_id: The member's ID.

        Returns:
            TeamMember if found, None otherwise.
        """
        for member in self._team_members:
            if member.id == member_id:
                return member
        return None

    def add_team_member(self, data: TeamMemberCreate) -> TeamMember:
        """Add a new team member.

        Args:
            data: TeamMemberCreate data.

        Returns:
            Created TeamMember object.
        """
        # Auto-generate initials if not provided
        initials = data.initials
        if not initials:
            name_parts = data.name.split()
            initials = "".join(part[0].upper() for part in name_parts if part)

        member = TeamMember(
            id=self._next_member_id,
            name=data.name,
            initials=initials,
            slack_id=data.slack_id,
            jira_account_id=data.jira_account_id,
            email=data.email,
        )

        self._team_members.append(member)
        self._next_member_id += 1

        return member

    def update_team_member(
        self, member_id: int, data: TeamMemberUpdate
    ) -> TeamMember | None:
        """Update a team member.

        Args:
            member_id: The member's ID.
            data: TeamMemberUpdate with fields to update.

        Returns:
            Updated TeamMember if found, None otherwise.
        """
        index = self._find_member_index(member_id)
        if index is None:
            return None

        member = self._team_members[index]
        update_fields = data.model_dump(exclude_unset=True)
        updated_data = {**member.model_dump(), **update_fields}

        updated_member = TeamMember(**updated_data)
        self._team_members[index] = updated_member
        return updated_member

    def _find_member_index(self, member_id: int) -> int | None:
        """Find the index of a team member by ID."""
        for i, member in enumerate(self._team_members):
            if member.id == member_id:
                return i
        return None

    def delete_team_member(self, member_id: int) -> bool:
        """Delete a team member.

        Args:
            member_id: The member's ID.

        Returns:
            True if deleted, False if not found.
        """
        index = self._find_member_index(member_id)
        if index is None:
            return False

        del self._team_members[index]
        return True

    def get_integration_status(self) -> IntegrationStatus:
        """Get the status of external integrations.

        Returns:
            IntegrationStatus with current connection states.
        """
        # Check if API keys are configured
        jira_connected = bool(
            app_settings.jira_base_url
            and app_settings.jira_email
            and app_settings.jira_api_token
        )
        slack_connected = bool(app_settings.slack_bot_token)

        return IntegrationStatus(
            jira_connected=jira_connected,
            slack_connected=slack_connected,
            jira_project=app_settings.jira_default_project if jira_connected else None,
            slack_workspace=None,  # Would need API call to get workspace name
        )


# Global service instance
_settings_service = SettingsService()


def get_settings() -> UserSettings:
    """Get the current user settings."""
    return _settings_service.get_settings()


def update_settings(new_settings: UserSettings) -> UserSettings:
    """Update user settings."""
    return _settings_service.update_settings(new_settings)


def get_team_members() -> list[TeamMember]:
    """Get all team members."""
    return _settings_service.get_team_members()


def add_team_member(data: TeamMemberCreate) -> TeamMember:
    """Add a new team member."""
    return _settings_service.add_team_member(data)


def update_team_member(member_id: int, data: TeamMemberUpdate) -> TeamMember | None:
    """Update a team member."""
    return _settings_service.update_team_member(member_id, data)


def delete_team_member(member_id: int) -> bool:
    """Delete a team member."""
    return _settings_service.delete_team_member(member_id)


def get_integration_status() -> IntegrationStatus:
    """Get integration status."""
    return _settings_service.get_integration_status()
