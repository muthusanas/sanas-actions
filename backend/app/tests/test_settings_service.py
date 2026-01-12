"""Tests for settings and team management service."""
import pytest
from unittest.mock import MagicMock

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
from app.services.settings_service import (
    SettingsService,
    get_settings,
    update_settings,
    get_team_members,
    add_team_member,
    update_team_member,
    delete_team_member,
    get_integration_status,
)


class TestSettingsService:
    """Tests for SettingsService class."""

    @pytest.fixture
    def service(self):
        """Create a SettingsService instance."""
        return SettingsService()

    def test_service_initialization(self, service):
        """Test service initializes with defaults."""
        assert service is not None

    def test_get_settings_returns_user_settings(self, service):
        """Test getting settings returns UserSettings object."""
        settings = service.get_settings()

        assert isinstance(settings, UserSettings)
        assert isinstance(settings.reminders, ReminderSettings)
        assert isinstance(settings.notifications, NotificationSettings)
        assert isinstance(settings.defaults, DefaultSettings)

    def test_get_settings_default_values(self, service):
        """Test default settings values."""
        settings = service.get_settings()

        assert settings.reminders.enabled is True
        assert settings.reminders.frequency == "Weekly"
        assert settings.notifications.on_create is True
        assert settings.defaults.project == "SANAS"

    def test_update_reminder_settings(self, service):
        """Test updating reminder settings."""
        new_reminders = ReminderSettings(
            enabled=False,
            frequency="Daily",
            day="Tuesday",
            time="10:00 AM",
        )

        service.update_settings(
            UserSettings(
                reminders=new_reminders,
                notifications=NotificationSettings(),
                defaults=DefaultSettings(),
            )
        )

        settings = service.get_settings()
        assert settings.reminders.enabled is False
        assert settings.reminders.frequency == "Daily"

    def test_update_notification_settings(self, service):
        """Test updating notification settings."""
        new_notifications = NotificationSettings(
            on_create=False,
            overdue_warnings=False,
        )

        service.update_settings(
            UserSettings(
                reminders=ReminderSettings(),
                notifications=new_notifications,
                defaults=DefaultSettings(),
            )
        )

        settings = service.get_settings()
        assert settings.notifications.on_create is False
        assert settings.notifications.overdue_warnings is False

    def test_update_default_settings(self, service):
        """Test updating default settings."""
        new_defaults = DefaultSettings(
            project="INFRA",
            issue_type="Bug",
        )

        service.update_settings(
            UserSettings(
                reminders=ReminderSettings(),
                notifications=NotificationSettings(),
                defaults=new_defaults,
            )
        )

        settings = service.get_settings()
        assert settings.defaults.project == "INFRA"
        assert settings.defaults.issue_type == "Bug"


class TestTeamMemberManagement:
    """Tests for team member management."""

    @pytest.fixture
    def service(self):
        """Create a SettingsService instance with empty team."""
        service = SettingsService()
        service._team_members = []
        return service

    def test_get_team_members_empty(self, service):
        """Test getting empty team members list."""
        members = service.get_team_members()
        assert members == []

    def test_add_team_member(self, service):
        """Test adding a new team member."""
        new_member = TeamMemberCreate(
            name="John Smith",
            initials="JS",
            slack_id="U123",
            jira_account_id="jira-js",
            email="john@example.com",
        )

        member = service.add_team_member(new_member)

        assert member.name == "John Smith"
        assert member.initials == "JS"
        assert member.id is not None

    def test_add_team_member_auto_generates_initials(self, service):
        """Test adding member auto-generates initials if not provided."""
        new_member = TeamMemberCreate(
            name="John Smith",
        )

        member = service.add_team_member(new_member)

        assert member.initials == "JS"

    def test_add_team_member_generates_unique_id(self, service):
        """Test adding members generates unique IDs."""
        member1 = service.add_team_member(TeamMemberCreate(name="John Smith"))
        member2 = service.add_team_member(TeamMemberCreate(name="Sarah Lee"))

        assert member1.id != member2.id

    def test_get_team_member_by_id(self, service):
        """Test getting a team member by ID."""
        created = service.add_team_member(TeamMemberCreate(name="John Smith"))
        member = service.get_team_member(created.id)

        assert member is not None
        assert member.name == "John Smith"

    def test_get_team_member_not_found(self, service):
        """Test getting non-existent member returns None."""
        member = service.get_team_member(999)
        assert member is None

    def test_update_team_member(self, service):
        """Test updating a team member."""
        created = service.add_team_member(TeamMemberCreate(name="John Smith"))

        updated = service.update_team_member(
            created.id, TeamMemberUpdate(name="John Doe", slack_id="U999")
        )

        assert updated is not None
        assert updated.name == "John Doe"
        assert updated.slack_id == "U999"

    def test_update_team_member_partial(self, service):
        """Test partial update only changes specified fields."""
        created = service.add_team_member(
            TeamMemberCreate(name="John Smith", slack_id="U123")
        )

        updated = service.update_team_member(
            created.id, TeamMemberUpdate(email="john@example.com")
        )

        assert updated.name == "John Smith"  # Unchanged
        assert updated.slack_id == "U123"  # Unchanged
        assert updated.email == "john@example.com"  # Changed

    def test_update_team_member_not_found(self, service):
        """Test updating non-existent member returns None."""
        result = service.update_team_member(999, TeamMemberUpdate(name="Test"))
        assert result is None

    def test_delete_team_member(self, service):
        """Test deleting a team member."""
        created = service.add_team_member(TeamMemberCreate(name="John Smith"))

        result = service.delete_team_member(created.id)

        assert result is True
        assert service.get_team_member(created.id) is None

    def test_delete_team_member_not_found(self, service):
        """Test deleting non-existent member returns False."""
        result = service.delete_team_member(999)
        assert result is False

    def test_find_member_index_found(self, service):
        """Test _find_member_index returns correct index."""
        service.add_team_member(TeamMemberCreate(name="John Smith"))
        member2 = service.add_team_member(TeamMemberCreate(name="Sarah Lee"))

        index = service._find_member_index(member2.id)

        assert index == 1

    def test_find_member_index_not_found(self, service):
        """Test _find_member_index returns None for non-existent ID."""
        index = service._find_member_index(999)

        assert index is None

    def test_update_preserves_unset_fields(self, service):
        """Test update only changes fields that are explicitly set."""
        created = service.add_team_member(
            TeamMemberCreate(
                name="John Smith",
                initials="JS",
                slack_id="U123",
                email="john@example.com",
            )
        )

        # Only update name, leave others unchanged
        updated = service.update_team_member(
            created.id, TeamMemberUpdate(name="John Doe")
        )

        assert updated.name == "John Doe"
        assert updated.initials == "JS"
        assert updated.slack_id == "U123"
        assert updated.email == "john@example.com"


class TestIntegrationStatus:
    """Tests for integration status."""

    @pytest.fixture
    def service(self):
        """Create a SettingsService instance."""
        return SettingsService()

    def test_get_integration_status(self, service):
        """Test getting integration status."""
        status = service.get_integration_status()

        assert isinstance(status, IntegrationStatus)

    def test_integration_status_defaults(self, service):
        """Test default integration status."""
        status = service.get_integration_status()

        # By default, no integrations are connected
        assert status.jira_connected is False
        assert status.slack_connected is False


class TestSettingsModels:
    """Tests for settings models."""

    def test_reminder_settings_defaults(self):
        """Test ReminderSettings default values."""
        settings = ReminderSettings()

        assert settings.enabled is True
        assert settings.frequency == "Weekly"
        assert settings.day == "Monday"
        assert settings.time == "9:00 AM"

    def test_notification_settings_defaults(self):
        """Test NotificationSettings default values."""
        settings = NotificationSettings()

        assert settings.on_create is True
        assert settings.overdue_warnings is True

    def test_default_settings_defaults(self):
        """Test DefaultSettings default values."""
        settings = DefaultSettings()

        assert settings.project == "SANAS"
        assert settings.issue_type == "Task"

    def test_user_settings_composition(self):
        """Test UserSettings composes sub-settings."""
        settings = UserSettings(
            reminders=ReminderSettings(enabled=False),
            notifications=NotificationSettings(on_create=False),
            defaults=DefaultSettings(project="INFRA"),
        )

        assert settings.reminders.enabled is False
        assert settings.notifications.on_create is False
        assert settings.defaults.project == "INFRA"

    def test_team_member_create(self):
        """Test TeamMemberCreate model."""
        member = TeamMemberCreate(
            name="John Smith",
            initials="JS",
            slack_id="U123",
        )

        assert member.name == "John Smith"
        assert member.initials == "JS"

    def test_team_member_update_all_optional(self):
        """Test TeamMemberUpdate fields are all optional."""
        update = TeamMemberUpdate()

        assert update.name is None
        assert update.slack_id is None

    def test_integration_status_model(self):
        """Test IntegrationStatus model."""
        status = IntegrationStatus(
            jira_connected=True,
            slack_connected=True,
            jira_project="SANAS",
            slack_workspace="My Workspace",
        )

        assert status.jira_connected is True
        assert status.slack_connected is True
        assert status.jira_project == "SANAS"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_settings_helper(self):
        """Test get_settings helper function."""
        settings = get_settings()
        assert isinstance(settings, UserSettings)

    def test_update_settings_helper(self):
        """Test update_settings helper function."""
        new_settings = UserSettings(
            reminders=ReminderSettings(enabled=False),
            notifications=NotificationSettings(),
            defaults=DefaultSettings(),
        )

        result = update_settings(new_settings)
        assert result.reminders.enabled is False

    def test_get_team_members_helper(self):
        """Test get_team_members helper function."""
        members = get_team_members()
        assert isinstance(members, list)

    def test_get_integration_status_helper(self):
        """Test get_integration_status helper function."""
        status = get_integration_status()
        assert isinstance(status, IntegrationStatus)
