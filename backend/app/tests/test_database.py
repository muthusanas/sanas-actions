"""Tests for SQLite database module."""
import pytest
from pathlib import Path

import app.database as database
from app.database import (
    init_db,
    get_all_team_members,
    get_team_member_by_id,
    create_team_member,
    update_team_member,
    delete_team_member,
    get_user_settings,
    save_user_settings,
    save_action_item,
    get_pending_action_items,
    mark_action_item_completed,
    get_analytics_data,
    DEFAULT_SETTINGS,
    DEFAULT_TEAM_MEMBERS,
)


class TestDatabaseInitialization:
    """Tests for database initialization."""

    def test_init_db_creates_tables(self, isolated_test_db):
        """Test init_db creates necessary tables."""
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}

        assert "team_members" in tables
        assert "settings" in tables
        assert "action_items" in tables

    def test_init_db_seeds_default_team_members(self, isolated_test_db):
        """Test init_db seeds default team members."""
        members = get_all_team_members()
        assert len(members) == len(DEFAULT_TEAM_MEMBERS)

    def test_init_db_seeds_default_settings(self, isolated_test_db):
        """Test init_db seeds default settings."""
        settings = get_user_settings()
        assert settings == DEFAULT_SETTINGS


class TestTeamMemberOperations:
    """Tests for team member CRUD operations."""

    def test_get_all_team_members(self, isolated_test_db):
        """Test getting all team members."""
        members = get_all_team_members()
        assert len(members) == 4
        assert all("name" in m for m in members)
        assert all("initials" in m for m in members)

    def test_get_team_member_by_id(self, isolated_test_db):
        """Test getting team member by ID."""
        members = get_all_team_members()
        first_member = members[0]

        result = get_team_member_by_id(first_member["id"])

        assert result is not None
        assert result["name"] == first_member["name"]

    def test_get_team_member_by_id_not_found(self, isolated_test_db):
        """Test getting non-existent team member returns None."""
        result = get_team_member_by_id(9999)
        assert result is None

    def test_create_team_member(self, isolated_test_db):
        """Test creating a team member."""
        result = create_team_member(
            name="Test User",
            initials="TU",
            slack_id="U123",
            jira_account_id="JIRA-999",
            email="test@example.com",
        )

        assert result["name"] == "Test User"
        assert result["initials"] == "TU"
        assert result["id"] is not None

    def test_create_team_member_auto_initials(self, isolated_test_db):
        """Test creating team member auto-generates initials."""
        result = create_team_member(
            name="Alice Bob",
            initials=None,
            slack_id=None,
            jira_account_id=None,
            email=None,
        )

        assert result["initials"] == "AB"

    def test_update_team_member(self, isolated_test_db):
        """Test updating team member."""
        members = get_all_team_members()
        member_id = members[0]["id"]

        result = update_team_member(member_id, name="Updated Name")

        assert result["name"] == "Updated Name"

    def test_update_team_member_partial(self, isolated_test_db):
        """Test partial update preserves other fields."""
        created = create_team_member(
            name="Original",
            initials="OR",
            slack_id="U123",
            jira_account_id=None,
            email="orig@example.com",
        )

        result = update_team_member(created["id"], name="New Name")

        assert result["name"] == "New Name"
        assert result["slack_id"] == "U123"
        assert result["email"] == "orig@example.com"

    def test_update_team_member_not_found(self, isolated_test_db):
        """Test updating non-existent member returns None."""
        result = update_team_member(9999, name="Test")
        assert result is None

    def test_delete_team_member(self, isolated_test_db):
        """Test deleting team member."""
        created = create_team_member(
            name="To Delete",
            initials="TD",
            slack_id=None,
            jira_account_id=None,
            email=None,
        )

        result = delete_team_member(created["id"])

        assert result is True
        assert get_team_member_by_id(created["id"]) is None

    def test_delete_team_member_not_found(self, isolated_test_db):
        """Test deleting non-existent member returns False."""
        result = delete_team_member(9999)
        assert result is False


class TestSettingsOperations:
    """Tests for settings operations."""

    def test_get_user_settings_returns_defaults(self, isolated_test_db):
        """Test getting settings returns defaults."""
        settings = get_user_settings()

        assert settings["reminders"]["enabled"] is True
        assert settings["reminders"]["frequency"] == "Weekly"
        assert settings["notifications"]["on_create"] is True
        assert settings["defaults"]["project"] == "SANAS"

    def test_save_user_settings(self, isolated_test_db):
        """Test saving user settings."""
        new_settings = {
            "reminders": {"enabled": False, "frequency": "Daily", "day": "Tuesday", "time": "10:00 AM"},
            "notifications": {"on_create": False, "overdue_warnings": True},
            "defaults": {"project": "INFRA", "issue_type": "Bug"},
        }

        save_user_settings(new_settings)
        result = get_user_settings()

        assert result["reminders"]["enabled"] is False
        assert result["defaults"]["project"] == "INFRA"


class TestActionItemOperations:
    """Tests for action item operations."""

    def test_save_action_item(self, isolated_test_db):
        """Test saving an action item."""
        result = save_action_item(
            title="Test Task",
            assignee="John Smith",
            due_date="2025-01-15",
            selected=True,
            overdue=False,
        )

        assert result["title"] == "Test Task"
        assert result["assignee"] == "John Smith"
        assert result["id"] is not None

    def test_get_pending_action_items(self, isolated_test_db):
        """Test getting pending action items."""
        save_action_item("Task 1", "John", None, True, False)
        save_action_item("Task 2", "Sarah", None, True, False)

        pending = get_pending_action_items()

        assert len(pending) == 2

    def test_mark_action_item_completed(self, isolated_test_db):
        """Test marking action item as completed."""
        item = save_action_item("Complete Me", "John", None, True, False)

        result = mark_action_item_completed(item["id"], "SANAS-123")

        assert result is True

        pending = get_pending_action_items()
        assert all(p["id"] != item["id"] for p in pending)


class TestAnalyticsData:
    """Tests for analytics data retrieval."""

    def test_get_analytics_data_empty(self, isolated_test_db):
        """Test analytics with no action items."""
        data = get_analytics_data()

        assert data["completed_this_week"] == 0
        assert data["pending_count"] == 0
        assert data["overdue_count"] == 0
        assert data["team_stats"] == []

    def test_get_analytics_data_with_items(self, isolated_test_db):
        """Test analytics with action items."""
        save_action_item("Task 1", "John", None, True, False)
        save_action_item("Task 2", "John", None, True, True)  # Overdue
        save_action_item("Task 3", "Sarah", None, True, False)

        data = get_analytics_data()

        assert data["pending_count"] == 3
        assert data["overdue_count"] == 1
        assert len(data["team_stats"]) == 2
