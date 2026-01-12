"""SQLite database setup and operations."""
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

# Database file path
DB_PATH = Path(__file__).parent.parent / "data" / "sanas.db"

# Default settings - single source of truth
DEFAULT_SETTINGS = {
    "reminders": {
        "enabled": True,
        "frequency": "Weekly",
        "day": "Monday",
        "time": "9:00 AM"
    },
    "notifications": {
        "on_create": True,
        "overdue_warnings": True
    },
    "defaults": {
        "project": "SANAS",
        "issue_type": "Task"
    }
}

# Default team members for initial setup
DEFAULT_TEAM_MEMBERS = [
    ("John Smith", "JS", "@john.smith", "JIRA-123", "john.smith@example.com"),
    ("Sarah Lee", "SL", "@sarah.lee", "JIRA-456", "sarah.lee@example.com"),
    ("Muthu K", "MK", "@muthu.k", "JIRA-789", "muthu.k@example.com"),
    ("Anita Patel", "AP", "@anita.patel", "JIRA-101", "anita.patel@example.com"),
]


def ensure_db_directory():
    """Ensure the database directory exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    ensure_db_directory()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _create_tables(cursor: sqlite3.Cursor) -> None:
    """Create database tables if they don't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            initials TEXT NOT NULL,
            slack_id TEXT,
            jira_account_id TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            assignee TEXT,
            due_date TEXT,
            selected INTEGER DEFAULT 1,
            overdue INTEGER DEFAULT 0,
            ticket_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)


def _seed_default_data(cursor: sqlite3.Cursor) -> None:
    """Seed default settings and team members if empty."""
    cursor.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("user_settings", json.dumps(DEFAULT_SETTINGS))
    )

    cursor.execute("SELECT COUNT(*) FROM team_members")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO team_members (name, initials, slack_id, jira_account_id, email) VALUES (?, ?, ?, ?, ?)",
            DEFAULT_TEAM_MEMBERS
        )


def init_db():
    """Initialize the database schema and seed default data."""
    ensure_db_directory()

    with get_db() as conn:
        cursor = conn.cursor()
        _create_tables(cursor)
        _seed_default_data(cursor)


# Team members operations
def get_all_team_members() -> list[dict]:
    """Get all team members from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM team_members ORDER BY name")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_team_member_by_id(member_id: int) -> dict | None:
    """Get a team member by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM team_members WHERE id = ?", (member_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_team_member(name: str, initials: str | None, slack_id: str | None,
                       jira_account_id: str | None, email: str | None) -> dict:
    """Create a new team member."""
    if not initials:
        name_parts = name.split()
        initials = "".join(part[0].upper() for part in name_parts if part)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO team_members (name, initials, slack_id, jira_account_id, email) VALUES (?, ?, ?, ?, ?)",
            (name, initials, slack_id, jira_account_id, email)
        )
        member_id = cursor.lastrowid

    return get_team_member_by_id(member_id)


def update_team_member(member_id: int, **updates) -> dict | None:
    """Update a team member."""
    # Filter out None values and empty updates
    valid_fields = {"name", "initials", "slack_id", "jira_account_id", "email"}
    updates = {k: v for k, v in updates.items() if k in valid_fields and v is not None}

    if not updates:
        return get_team_member_by_id(member_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [member_id]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE team_members SET {set_clause} WHERE id = ?", values)
        if cursor.rowcount == 0:
            return None

    return get_team_member_by_id(member_id)


def delete_team_member(member_id: int) -> bool:
    """Delete a team member."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM team_members WHERE id = ?", (member_id,))
        return cursor.rowcount > 0


# Settings operations
def get_user_settings() -> dict:
    """Get user settings from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", ("user_settings",))
        row = cursor.fetchone()
        if row:
            return json.loads(row["value"])
        return DEFAULT_SETTINGS.copy()


def save_user_settings(settings: dict) -> dict:
    """Save user settings to database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("user_settings", json.dumps(settings))
        )
    return settings


# Action items operations
def save_action_item(title: str, assignee: str | None, due_date: str | None,
                     selected: bool = True, overdue: bool = False) -> dict:
    """Save an action item to database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO action_items (title, assignee, due_date, selected, overdue)
               VALUES (?, ?, ?, ?, ?)""",
            (title, assignee, due_date, int(selected), int(overdue))
        )
        item_id = cursor.lastrowid
        cursor.execute("SELECT * FROM action_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row)


def get_pending_action_items() -> list[dict]:
    """Get all pending (not completed) action items."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM action_items WHERE completed_at IS NULL ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]


def mark_action_item_completed(item_id: int, ticket_key: str | None = None) -> bool:
    """Mark an action item as completed."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE action_items SET completed_at = CURRENT_TIMESTAMP, ticket_key = ? WHERE id = ?",
            (ticket_key, item_id)
        )
        return cursor.rowcount > 0


def get_analytics_data() -> dict:
    """Get analytics data for dashboard."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Completed this week
        cursor.execute("""
            SELECT COUNT(*) FROM action_items
            WHERE completed_at IS NOT NULL
            AND completed_at >= date('now', '-7 days')
        """)
        completed_this_week = cursor.fetchone()[0]

        # Pending actions
        cursor.execute("SELECT COUNT(*) FROM action_items WHERE completed_at IS NULL")
        pending_count = cursor.fetchone()[0]

        # Overdue count
        cursor.execute("""
            SELECT COUNT(*) FROM action_items
            WHERE completed_at IS NULL AND overdue = 1
        """)
        overdue_count = cursor.fetchone()[0]

        # Active team members (those with assignments)
        cursor.execute("""
            SELECT COUNT(DISTINCT assignee) FROM action_items
            WHERE assignee IS NOT NULL AND completed_at IS NULL
        """)
        active_members = cursor.fetchone()[0]

        # Team member stats (using SQLite-compatible CASE/SUM instead of FILTER)
        cursor.execute("""
            SELECT assignee,
                   SUM(CASE WHEN completed_at IS NOT NULL AND completed_at >= date('now', '-7 days') THEN 1 ELSE 0 END) as completed,
                   COUNT(*) as total
            FROM action_items
            WHERE assignee IS NOT NULL
            GROUP BY assignee
            ORDER BY completed DESC
        """)

        team_stats = []
        for row in cursor.fetchall():
            completion_rate = (row[1] / row[2] * 100) if row[2] > 0 else 0
            team_stats.append({
                "assignee": row[0],
                "completed_this_week": row[1],
                "total": row[2],
                "completion_rate": round(completion_rate)
            })

        return {
            "completed_this_week": completed_this_week,
            "pending_count": pending_count,
            "overdue_count": overdue_count,
            "active_members": active_members,
            "team_stats": team_stats
        }
