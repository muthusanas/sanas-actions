"""Action item models."""
from datetime import date
from pydantic import BaseModel, Field


class ActionItemBase(BaseModel):
    """Base action item schema."""

    title: str = Field(..., min_length=1, description="Action item title")
    assignee: str | None = Field(None, description="Assigned team member name")
    due_date: str | None = Field(None, description="Due date in format 'Jan 15'")


class ActionItem(ActionItemBase):
    """Action item with ID and status flags."""

    id: int = Field(..., description="Unique identifier")
    selected: bool = Field(default=True, description="Whether item is selected")
    overdue: bool = Field(default=False, description="Whether item is overdue")


class ActionItemCreate(ActionItemBase):
    """Schema for creating action items."""

    pass


class ActionItemUpdate(BaseModel):
    """Schema for updating action items."""

    title: str | None = None
    assignee: str | None = None
    due_date: str | None = None
    selected: bool | None = None


class ExtractActionItemsRequest(BaseModel):
    """Request schema for extracting action items from meeting notes."""

    input_type: str = Field(
        ..., pattern="^(text|file)$", description="Type of input: 'text' or 'file'"
    )
    content: str | None = Field(None, description="Text content for text input type")


class ExtractActionItemsResponse(BaseModel):
    """Response schema for extracted action items."""

    action_items: list[ActionItem] = Field(..., description="List of extracted action items")
    raw_text: str = Field(..., description="Original text that was processed")
