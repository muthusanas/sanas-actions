"""Service for managing settings and team members using SQLite."""
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
from app.database import (
    get_all_team_members,
    get_team_member_by_id,
    create_team_member as db_create_team_member,
    update_team_member as db_update_team_member,
    delete_team_member as db_delete_team_member,
    get_user_settings,
    save_user_settings,
    init_db,
)

# Initialize database on module load
init_db()


class SettingsService:
    """Service for managing user settings and team members using SQLite."""

    def get_settings(self) -> UserSettings:
        """Get the current user settings from database.

        Returns:
            UserSettings object with current settings.
        """
        data = get_user_settings()
        return UserSettings(
            reminders=ReminderSettings(**data.get("reminders", {})),
            notifications=NotificationSettings(**data.get("notifications", {})),
            defaults=DefaultSettings(**data.get("defaults", {})),
        )

    def update_settings(self, new_settings: UserSettings) -> UserSettings:
        """Update user settings in database.

        Args:
            new_settings: New settings to apply.

        Returns:
            Updated UserSettings object.
        """
        data = {
            "reminders": new_settings.reminders.model_dump(),
            "notifications": new_settings.notifications.model_dump(),
            "defaults": new_settings.defaults.model_dump(),
        }
        save_user_settings(data)
        return new_settings

    def get_team_members(self) -> list[TeamMember]:
        """Get all team members from database.

        Returns:
            List of TeamMember objects.
        """
        rows = get_all_team_members()
        return [TeamMember(**row) for row in rows]

    def get_team_member(self, member_id: int) -> TeamMember | None:
        """Get a team member by ID.

        Args:
            member_id: The member's ID.

        Returns:
            TeamMember if found, None otherwise.
        """
        row = get_team_member_by_id(member_id)
        return TeamMember(**row) if row else None

    def add_team_member(self, data: TeamMemberCreate) -> TeamMember:
        """Add a new team member to database.

        Args:
            data: TeamMemberCreate data.

        Returns:
            Created TeamMember object.
        """
        row = db_create_team_member(
            name=data.name,
            initials=data.initials,
            slack_id=data.slack_id,
            jira_account_id=data.jira_account_id,
            email=data.email,
        )
        return TeamMember(**row)

    def update_team_member(
        self, member_id: int, data: TeamMemberUpdate
    ) -> TeamMember | None:
        """Update a team member in database.

        Args:
            member_id: The member's ID.
            data: TeamMemberUpdate with fields to update.

        Returns:
            Updated TeamMember if found, None otherwise.
        """
        update_fields = data.model_dump(exclude_unset=True)
        row = db_update_team_member(member_id, **update_fields)
        return TeamMember(**row) if row else None

    def delete_team_member(self, member_id: int) -> bool:
        """Delete a team member from database.

        Args:
            member_id: The member's ID.

        Returns:
            True if deleted, False if not found.
        """
        return db_delete_team_member(member_id)

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


def get_team_member(member_id: int) -> TeamMember | None:
    """Get a team member by ID."""
    return _settings_service.get_team_member(member_id)


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
