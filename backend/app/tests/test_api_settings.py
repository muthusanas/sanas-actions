"""Tests for settings API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import UserSettings, ReminderSettings, NotificationSettings, DefaultSettings


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestSettingsEndpoints:
    """Tests for settings endpoints."""

    def test_get_settings(self, client):
        """Test getting current settings."""
        response = client.get("/api/settings")

        assert response.status_code == 200
        data = response.json()
        assert "reminders" in data
        assert "notifications" in data
        assert "defaults" in data

    def test_update_settings(self, client):
        """Test updating settings."""
        new_settings = {
            "reminders": {
                "enabled": False,
                "frequency": "Daily",
                "day": "Tuesday",
                "time": "10:00 AM",
            },
            "notifications": {
                "on_create": False,
                "overdue_warnings": False,
            },
            "defaults": {
                "project": "INFRA",
                "issue_type": "Bug",
            },
        }

        response = client.put("/api/settings", json=new_settings)

        assert response.status_code == 200
        data = response.json()
        assert data["reminders"]["enabled"] is False
        assert data["defaults"]["project"] == "INFRA"


class TestTeamEndpoints:
    """Tests for team management endpoints."""

    def test_get_team_members(self, client):
        """Test getting team members list."""
        response = client.get("/api/team")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_team_member(self, client):
        """Test creating a new team member."""
        new_member = {
            "name": "Test User",
            "initials": "TU",
            "slack_id": "UTEST123",
            "email": "test@example.com",
        }

        response = client.post("/api/team", json=new_member)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert "id" in data

    def test_create_team_member_auto_initials(self, client):
        """Test creating member auto-generates initials."""
        new_member = {"name": "Jane Doe"}

        response = client.post("/api/team", json=new_member)

        assert response.status_code == 201
        data = response.json()
        assert data["initials"] == "JD"

    def test_get_team_member_not_found(self, client):
        """Test getting non-existent team member."""
        response = client.get("/api/team/99999")

        assert response.status_code == 404

    def test_update_team_member(self, client):
        """Test updating a team member."""
        # First create a member
        new_member = {"name": "Update Test"}
        create_response = client.post("/api/team", json=new_member)
        member_id = create_response.json()["id"]

        # Then update
        update_data = {"name": "Updated Name", "slack_id": "UNEW123"}
        response = client.patch(f"/api/team/{member_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["slack_id"] == "UNEW123"

    def test_update_team_member_not_found(self, client):
        """Test updating non-existent member."""
        response = client.patch("/api/team/99999", json={"name": "Test"})

        assert response.status_code == 404

    def test_delete_team_member(self, client):
        """Test deleting a team member."""
        # First create a member
        new_member = {"name": "Delete Test"}
        create_response = client.post("/api/team", json=new_member)
        member_id = create_response.json()["id"]

        # Then delete
        response = client.delete(f"/api/team/{member_id}")

        assert response.status_code == 204

    def test_delete_team_member_not_found(self, client):
        """Test deleting non-existent member."""
        response = client.delete("/api/team/99999")

        assert response.status_code == 404


class TestIntegrationStatusEndpoint:
    """Tests for integration status endpoint."""

    def test_get_integration_status(self, client):
        """Test getting integration status."""
        response = client.get("/api/integrations/status")

        assert response.status_code == 200
        data = response.json()
        assert "jira_connected" in data
        assert "slack_connected" in data
