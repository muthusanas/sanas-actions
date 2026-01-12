"""API routes for action items and related operations."""
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models import (
    ExtractActionItemsRequest,
    ExtractActionItemsResponse,
    TicketCreateRequest,
    TicketCreateResponse,
    SlackNotificationRequest,
    ReminderRequest,
    NotificationResponse,
    BulkNotificationResponse,
    ActionItem,
    JiraConfig,
)
from app.services import (
    extract_action_items_from_text,
    create_jira_tickets,
    send_slack_notification,
    send_reminders,
)
from app.api.dependencies import get_team_members, get_action_items_store, get_next_action_id

router = APIRouter(prefix="/api", tags=["actions"])

# Allowed file types for upload
ALLOWED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# File size constants
BYTES_PER_MB = 1024 * 1024
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * BYTES_PER_MB


def _store_action_items(action_items: list[ActionItem]) -> None:
    """Store action items in the global store for later ticket creation."""
    store = get_action_items_store()
    for item in action_items:
        store[item.id] = item


@router.post("/actions/extract", response_model=ExtractActionItemsResponse)
async def extract_actions(request: ExtractActionItemsRequest):
    """Extract action items from meeting notes text.

    Args:
        request: Request containing input type and content.

    Returns:
        List of extracted action items.

    Raises:
        HTTPException: If content is missing for text type.
    """
    if request.input_type == "text":
        if not request.content:
            raise HTTPException(
                status_code=400,
                detail="Content is required for text input type",
            )

        action_items = await extract_action_items_from_text(
            request.content, id_generator=get_next_action_id
        )
        _store_action_items(action_items)

        return ExtractActionItemsResponse(
            action_items=action_items,
            raw_text=request.content,
        )

    raise HTTPException(status_code=400, detail="Invalid input type")


@router.post("/actions/extract-file", response_model=ExtractActionItemsResponse)
async def extract_actions_from_file(file: UploadFile = File(...)):
    """Extract action items from an uploaded file.

    Args:
        file: Uploaded file containing meeting notes.

    Returns:
        List of extracted action items.

    Raises:
        HTTPException: If file type is not supported.
    """
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # Read file content with size limit
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB",
        )

    # For text files, decode directly
    if file.content_type in {"text/plain", "text/markdown"}:
        text_content = content.decode("utf-8")
    else:
        # For PDF and DOCX, we would need specialized parsing
        # For now, we'll try to decode as text or return an error
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Could not parse file content. Please use a text file.",
            )

    action_items = await extract_action_items_from_text(
        text_content, id_generator=get_next_action_id
    )
    _store_action_items(action_items)

    return ExtractActionItemsResponse(
        action_items=action_items,
        raw_text=text_content,
    )


@router.post("/actions/tickets", response_model=TicketCreateResponse)
async def create_tickets(request: TicketCreateRequest):
    """Create Jira tickets for selected action items.

    Args:
        request: Request containing action IDs and Jira config.

    Returns:
        Created tickets and any failures.

    Raises:
        HTTPException: If no action IDs provided.
    """
    if not request.action_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one action ID is required",
        )

    # Get action items from store
    store = get_action_items_store()
    action_items = []
    for action_id in request.action_ids:
        if action_id in store:
            action_items.append(store[action_id])
        else:
            # Create a placeholder if not found
            action_items.append(
                ActionItem(
                    id=action_id,
                    title=f"Action Item {action_id}",
                    assignee=None,
                    due_date=None,
                    selected=True,
                    overdue=False,
                )
            )

    result = await create_jira_tickets(action_items, request.config)

    return TicketCreateResponse(
        tickets=[
            {
                "key": t.key,
                "assignee": t.assignee,
                "url": t.url,
            }
            for t in result.tickets
        ],
        failed=result.failed,
    )


@router.post("/notifications/send", response_model=NotificationResponse)
async def send_notification(request: SlackNotificationRequest):
    """Send a Slack notification to a team member.

    Args:
        request: Request containing assignee and message.

    Returns:
        Notification result.
    """
    team_members = get_team_members()

    result = await send_slack_notification(
        assignee=request.assignee,
        message=request.message,
        team_members=team_members,
        ticket_key=request.ticket_key,
    )

    return NotificationResponse(
        success=result.success,
        message=result.message,
        recipients=result.recipients,
    )


@router.post("/notifications/reminders", response_model=BulkNotificationResponse)
async def send_reminder_notifications(request: ReminderRequest):
    """Send reminder notifications to multiple team members.

    Args:
        request: Request containing action IDs and assignees.

    Returns:
        Bulk notification result.

    Raises:
        HTTPException: If no assignees provided.
    """
    if not request.assignees:
        raise HTTPException(
            status_code=400,
            detail="At least one assignee is required",
        )

    team_members = get_team_members()

    # Build reminder message
    message = (
        "📋 *Reminder: You have pending action items*\n\n"
        "Please review and complete your assigned tasks."
    )

    result = await send_reminders(
        assignees=request.assignees,
        message=message,
        team_members=team_members,
    )

    return BulkNotificationResponse(
        total_sent=result.total_sent,
        total_failed=result.total_failed,
        failed_recipients=result.failed_recipients,
    )
