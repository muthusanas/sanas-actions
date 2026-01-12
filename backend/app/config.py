"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Sanas Action Items Tracker API"
    debug: bool = False

    # Claude API configuration
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # Jira configuration
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_default_project: str = "SANAS"

    # Slack configuration
    slack_bot_token: str = ""
    slack_webhook_url: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
