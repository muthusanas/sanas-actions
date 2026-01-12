"""Service for creating Jira tickets."""
import base64
from typing import Any

import httpx

from app.config import settings
from app.models import (
    ActionItem,
    JiraConfig,
    CreatedTicket,
    TicketCreateResponse,
)


class JiraService:
    """Service for interacting with Jira API."""

    def __init__(
        self,
        base_url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
    ):
        """Initialize the Jira service."""
        self.base_url = (base_url or settings.jira_base_url).rstrip("/")
        self.email = email or settings.jira_email
        self.api_token = api_token or settings.jira_api_token
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Build authentication headers for Jira API."""
        credentials = f"{self.email}:{self.api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=30.0,
            )
        return self._client

    async def _make_request(
        self, method: str, endpoint: str, json_data: dict | None = None
    ) -> dict[str, Any]:
        """Make an HTTP request to Jira API."""
        response = await self.client.request(method, endpoint, json=json_data)
        response.raise_for_status()
        return response.json()

    def _build_issue_payload(
        self, action_item: ActionItem, config: JiraConfig
    ) -> dict[str, Any]:
        """Build the Jira issue payload."""
        payload = {
            "fields": {
                "project": {"key": config.project},
                "issuetype": {"name": config.issue_type},
                "summary": action_item.title,
                "labels": [config.label],
            }
        }

        # Add description with assignee and due date info
        description_parts = []
        if action_item.assignee:
            description_parts.append(f"Assigned to: {action_item.assignee}")
        if action_item.due_date:
            description_parts.append(f"Due: {action_item.due_date}")

        if description_parts:
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "\n".join(description_parts)}
                        ],
                    }
                ],
            }

        return payload

    async def create_ticket(
        self, action_item: ActionItem, config: JiraConfig
    ) -> CreatedTicket:
        """Create a single Jira ticket.

        Args:
            action_item: The action item to create a ticket for.
            config: Jira configuration for the ticket.

        Returns:
            CreatedTicket with the new ticket details.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        payload = self._build_issue_payload(action_item, config)
        response = await self._make_request("POST", "/rest/api/3/issue", json_data=payload)

        ticket_key = response["key"]
        return CreatedTicket(
            key=ticket_key,
            assignee=action_item.assignee,
            url=f"{self.base_url}/browse/{ticket_key}",
        )

    async def create_tickets(
        self, action_items: list[ActionItem], config: JiraConfig
    ) -> TicketCreateResponse:
        """Create multiple Jira tickets.

        Args:
            action_items: List of action items to create tickets for.
            config: Jira configuration for the tickets.

        Returns:
            TicketCreateResponse with created tickets and any failures.
        """
        if not action_items:
            return TicketCreateResponse(tickets=[], failed=[])

        created_tickets = []
        failed_ids = []

        for item in action_items:
            try:
                ticket = await self.create_ticket(item, config)
                created_tickets.append(ticket)
            except Exception:
                failed_ids.append(item.id)

        return TicketCreateResponse(tickets=created_tickets, failed=failed_ids)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


async def create_jira_tickets(
    action_items: list[ActionItem], config: JiraConfig
) -> TicketCreateResponse:
    """Helper function to create Jira tickets.

    Args:
        action_items: List of action items.
        config: Jira configuration.

    Returns:
        TicketCreateResponse with results.
    """
    service = JiraService()
    try:
        return await service.create_tickets(action_items, config)
    finally:
        await service.close()
