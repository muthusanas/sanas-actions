"""Service for extracting action items from meeting notes using Claude."""
import json
import re
from collections.abc import Callable
from typing import Any

from anthropic import AsyncAnthropic

from app.config import settings
from app.models import ActionItem


EXTRACTION_PROMPT = """You are an assistant that extracts action items from meeting notes.

Analyze the following meeting notes and extract all action items. For each action item, identify:
1. The task/action that needs to be done (title)
2. The person assigned to do it (assignee) - if mentioned
3. The due date (due_date) - if mentioned, format as "Jan 15" style

Return ONLY a JSON array with no additional text. Each item should have these fields:
- "title": string (required) - the action item description
- "assignee": string or null - the person's name
- "due_date": string or null - the due date in "Mon DD" format

Example output:
[
    {"title": "Review the Q1 roadmap", "assignee": "John Smith", "due_date": "Jan 15"},
    {"title": "Update documentation", "assignee": "Sarah Lee", "due_date": null}
]

If no action items are found, return an empty array: []

Meeting notes:
"""


class ExtractionService:
    """Service for extracting action items from text using Claude AI."""

    def __init__(self, api_key: str | None = None):
        """Initialize the extraction service."""
        self.api_key = api_key or settings.anthropic_api_key
        self.model = settings.claude_model
        self._client: AsyncAnthropic | None = None

    @property
    def client(self) -> AsyncAnthropic:
        """Get or create the Anthropic client."""
        if self._client is None:
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def _call_claude(self, prompt: str) -> Any:
        """Call Claude API with the given prompt."""
        return await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

    async def extract_from_text(
        self, text: str, id_generator: Callable[[], int] | None = None
    ) -> list[ActionItem]:
        """Extract action items from meeting notes text.

        Args:
            text: The meeting notes text to extract action items from.
            id_generator: Optional callable that returns unique IDs.

        Returns:
            A list of ActionItem objects.

        Raises:
            Exception: If the Claude API call fails.
        """
        if not text or not text.strip():
            return []

        prompt = EXTRACTION_PROMPT + text
        response = await self._call_claude(prompt)

        # Extract the text content from the response
        response_text = response.content[0].text
        parsed_items = parse_claude_response(response_text)

        # Convert to ActionItem objects with unique IDs
        action_items = []
        for i, item in enumerate(parsed_items, start=1):
            item_id = id_generator() if id_generator else i
            action_items.append(
                ActionItem(
                    id=item_id,
                    title=item.get("title", ""),
                    assignee=item.get("assignee"),
                    due_date=item.get("due_date"),
                    selected=True,
                    overdue=False,
                )
            )

        return action_items


def parse_claude_response(response_text: str | None) -> list[dict]:
    """Parse Claude's response text into a list of action item dicts.

    Args:
        response_text: The raw response text from Claude.

    Returns:
        A list of dictionaries representing action items.
    """
    if not response_text:
        return []

    # Try to extract JSON from markdown code block
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response_text)
    if code_block_match:
        json_text = code_block_match.group(1).strip()
    else:
        json_text = response_text.strip()

    try:
        parsed = json.loads(json_text)
        if isinstance(parsed, list):
            return parsed
        return []
    except json.JSONDecodeError:
        return []


async def extract_action_items_from_text(
    text: str, id_generator: Callable[[], int] | None = None
) -> list[ActionItem]:
    """Helper function to extract action items from text.

    Args:
        text: The meeting notes text.
        id_generator: Optional callable that returns unique IDs.

    Returns:
        A list of ActionItem objects.
    """
    service = ExtractionService()
    return await service.extract_from_text(text, id_generator)
