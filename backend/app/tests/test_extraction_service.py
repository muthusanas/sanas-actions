"""Tests for the action extraction service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.models import ActionItem, ExtractActionItemsRequest
from app.services.extraction_service import (
    ExtractionService,
    extract_action_items_from_text,
    parse_claude_response,
)


class TestExtractionService:
    """Tests for ExtractionService class."""

    @pytest.fixture
    def service(self):
        """Create an ExtractionService instance."""
        return ExtractionService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None

    @pytest.mark.asyncio
    async def test_extract_from_text_returns_action_items(
        self, service, sample_meeting_notes
    ):
        """Test extracting action items from text."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text=json.dumps(
                    [
                        {
                            "title": "Review the Q1 roadmap",
                            "assignee": "John Smith",
                            "due_date": "Jan 15",
                        },
                        {
                            "title": "Update the API documentation",
                            "assignee": "Sarah Lee",
                            "due_date": None,
                        },
                    ]
                )
            )
        ]

        with patch.object(
            service, "_call_claude", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.extract_from_text(sample_meeting_notes)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(isinstance(item, ActionItem) for item in result)

    @pytest.mark.asyncio
    async def test_extract_from_text_assigns_unique_ids(self, service):
        """Test that extracted items have unique IDs."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text=json.dumps(
                    [
                        {"title": "Task 1", "assignee": "John", "due_date": None},
                        {"title": "Task 2", "assignee": "Sarah", "due_date": None},
                        {"title": "Task 3", "assignee": "Muthu", "due_date": None},
                    ]
                )
            )
        ]

        with patch.object(
            service, "_call_claude", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.extract_from_text("Some meeting notes")

        ids = [item.id for item in result]
        assert len(ids) == len(set(ids))  # All IDs are unique

    @pytest.mark.asyncio
    async def test_extract_from_text_sets_selected_true(self, service):
        """Test that extracted items have selected=True by default."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text=json.dumps(
                    [{"title": "Task 1", "assignee": "John", "due_date": None}]
                )
            )
        ]

        with patch.object(
            service, "_call_claude", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await service.extract_from_text("Some meeting notes")

        assert all(item.selected for item in result)

    @pytest.mark.asyncio
    async def test_extract_from_empty_text_returns_empty_list(self, service):
        """Test extracting from empty text returns empty list."""
        result = await service.extract_from_text("")
        assert result == []

    @pytest.mark.asyncio
    async def test_extract_from_text_handles_api_error(self, service):
        """Test handling API errors gracefully."""
        with patch.object(
            service,
            "_call_claude",
            new_callable=AsyncMock,
            side_effect=Exception("API Error"),
        ):
            with pytest.raises(Exception):
                await service.extract_from_text("Some notes")


class TestParseCludeResponse:
    """Tests for parse_claude_response function."""

    def test_parse_valid_json_array(self):
        """Test parsing a valid JSON array response."""
        response_text = json.dumps(
            [
                {"title": "Task 1", "assignee": "John", "due_date": "Jan 15"},
                {"title": "Task 2", "assignee": "Sarah", "due_date": None},
            ]
        )
        result = parse_claude_response(response_text)

        assert len(result) == 2
        assert result[0]["title"] == "Task 1"
        assert result[1]["assignee"] == "Sarah"

    def test_parse_json_with_markdown_code_block(self):
        """Test parsing JSON wrapped in markdown code block."""
        response_text = """```json
[
    {"title": "Task 1", "assignee": "John", "due_date": "Jan 15"}
]
```"""
        result = parse_claude_response(response_text)

        assert len(result) == 1
        assert result[0]["title"] == "Task 1"

    def test_parse_invalid_json_returns_empty_list(self):
        """Test parsing invalid JSON returns empty list."""
        result = parse_claude_response("This is not JSON")
        assert result == []

    def test_parse_empty_response(self):
        """Test parsing empty response returns empty list."""
        result = parse_claude_response("")
        assert result == []

    def test_parse_null_response(self):
        """Test parsing null response returns empty list."""
        result = parse_claude_response(None)
        assert result == []


class TestExtractActionItemsFromText:
    """Tests for the extract_action_items_from_text helper function."""

    @pytest.mark.asyncio
    async def test_function_delegates_to_service(self, sample_meeting_notes):
        """Test that the function creates a service and calls extract_from_text."""
        with patch(
            "app.services.extraction_service.ExtractionService"
        ) as MockService:
            mock_instance = MockService.return_value
            mock_instance.extract_from_text = AsyncMock(
                return_value=[
                    ActionItem(
                        id=1,
                        title="Test",
                        assignee="John",
                        due_date=None,
                        selected=True,
                        overdue=False,
                    )
                ]
            )

            result = await extract_action_items_from_text(sample_meeting_notes)

            mock_instance.extract_from_text.assert_called_once_with(
                sample_meeting_notes, None
            )
            assert len(result) == 1


class TestActionItemValidation:
    """Tests for action item validation."""

    def test_action_item_requires_title(self):
        """Test that action items require a title."""
        with pytest.raises(ValueError):
            ActionItem(
                id=1,
                title="",  # Empty title should fail
                assignee="John",
                due_date=None,
                selected=True,
                overdue=False,
            )

    def test_action_item_allows_null_assignee(self):
        """Test that action items allow null assignee."""
        item = ActionItem(
            id=1,
            title="Task without assignee",
            assignee=None,
            due_date=None,
            selected=True,
            overdue=False,
        )
        assert item.assignee is None

    def test_action_item_allows_null_due_date(self):
        """Test that action items allow null due date."""
        item = ActionItem(
            id=1,
            title="Task without due date",
            assignee="John",
            due_date=None,
            selected=True,
            overdue=False,
        )
        assert item.due_date is None

    def test_action_item_with_all_fields(self):
        """Test creating action item with all fields."""
        item = ActionItem(
            id=1,
            title="Complete the report",
            assignee="John Smith",
            due_date="Jan 15",
            selected=True,
            overdue=False,
        )
        assert item.id == 1
        assert item.title == "Complete the report"
        assert item.assignee == "John Smith"
        assert item.due_date == "Jan 15"
        assert item.selected is True
        assert item.overdue is False
