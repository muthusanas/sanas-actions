"""Shared dependencies for API routes."""
import itertools

from app.models import TeamMember, ActionItem

# In-memory store for action items (would be a database in production)
_action_items_store: dict[int, ActionItem] = {}

# Counter for unique action item IDs
_action_id_counter = itertools.count(1)

# Default team members (would come from database in production)
_team_members: list[TeamMember] = [
    TeamMember(
        id=1,
        name="John Smith",
        initials="JS",
        slack_id="U123JS",
        jira_account_id="john.smith",
        email="john.smith@example.com",
    ),
    TeamMember(
        id=2,
        name="Sarah Lee",
        initials="SL",
        slack_id="U456SL",
        jira_account_id="sarah.lee",
        email="sarah.lee@example.com",
    ),
    TeamMember(
        id=3,
        name="Muthu K",
        initials="MK",
        slack_id="U789MK",
        jira_account_id="muthu.k",
        email="muthu.k@example.com",
    ),
    TeamMember(
        id=4,
        name="Anita Patel",
        initials="AP",
        slack_id="U012AP",
        jira_account_id="anita.patel",
        email="anita.patel@example.com",
    ),
    TeamMember(
        id=5,
        name="Raj Kumar",
        initials="RK",
        slack_id="U345RK",
        jira_account_id="raj.kumar",
        email="raj.kumar@example.com",
    ),
]


def get_team_members() -> list[TeamMember]:
    """Get the list of team members."""
    return _team_members


def get_action_items_store() -> dict[int, ActionItem]:
    """Get the action items store."""
    return _action_items_store


def clear_action_items_store():
    """Clear the action items store."""
    _action_items_store.clear()


def get_next_action_id() -> int:
    """Get the next unique action item ID."""
    return next(_action_id_counter)
