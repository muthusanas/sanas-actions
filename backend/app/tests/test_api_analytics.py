"""Tests for analytics API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import save_action_item


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAnalyticsEndpoint:
    """Tests for GET /api/analytics endpoint."""

    def test_get_analytics_success(self, client):
        """Test getting analytics returns expected structure."""
        response = client.get("/api/analytics")

        assert response.status_code == 200
        data = response.json()

        # Check stats structure
        assert "stats" in data
        assert "completed_this_week" in data["stats"]
        assert "pending_actions" in data["stats"]
        assert "overdue_count" in data["stats"]
        assert "active_team_members" in data["stats"]

        # Check pending_items structure
        assert "pending_items" in data
        assert isinstance(data["pending_items"], list)

        # Check leaderboard structure
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)

        # Check weekly_trend structure
        assert "weekly_trend" in data
        assert isinstance(data["weekly_trend"], list)

    def test_get_analytics_with_pending_items(self, client):
        """Test analytics with pending items."""
        # Create test action items
        save_action_item("Test Task 1", "John Smith", "2025-01-15", True, False)
        save_action_item("Test Task 2", "Sarah Lee", None, True, True)  # Overdue

        response = client.get("/api/analytics")

        assert response.status_code == 200
        data = response.json()

        assert data["stats"]["pending_actions"] >= 2
        assert data["stats"]["overdue_count"] >= 1

    def test_get_analytics_weekly_trend_structure(self, client):
        """Test weekly trend has correct day names."""
        response = client.get("/api/analytics")

        assert response.status_code == 200
        data = response.json()

        days = [t["week"] for t in data["weekly_trend"]]
        expected_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        assert days == expected_days

    def test_get_analytics_leaderboard_structure(self, client):
        """Test leaderboard item structure when items exist."""
        # Create action items to generate leaderboard
        save_action_item("Task 1", "John Smith", None, True, False)

        response = client.get("/api/analytics")

        assert response.status_code == 200
        data = response.json()

        if data["leaderboard"]:
            item = data["leaderboard"][0]
            assert "name" in item
            assert "initials" in item
            assert "completed" in item
            assert "total" in item
            assert "completion_percentage" in item

    def test_get_analytics_pending_items_structure(self, client):
        """Test pending items have correct structure."""
        save_action_item("Task to Check", "John Smith", "2025-01-20", True, False)

        response = client.get("/api/analytics")

        assert response.status_code == 200
        data = response.json()

        if data["pending_items"]:
            item = data["pending_items"][0]
            assert "id" in item
            assert "title" in item
            assert "assignee" in item
            assert "due_date" in item
            assert "overdue" in item
