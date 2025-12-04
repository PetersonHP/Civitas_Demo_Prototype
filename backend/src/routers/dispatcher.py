from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from uuid import UUID
from pydantic import BaseModel

from ..database import get_db
from ..services.dispatcher_agent import dispatch_ticket_model
from ..config import get_settings
from ..models.civitas import Ticket as TicketModel

router = APIRouter(
    prefix="/dispatcher",
    tags=["dispatcher"],
)


class DispatchTicketResponse(BaseModel):
    """Schema for dispatcher agent output."""
    status: str
    priority: str
    user_assignees: List[str]
    crew_assignees: List[str]
    labels: List[str]
    comment: Dict[str, str]  # {"comment_body": str}
    justification: str  # Internal reasoning for priority and assignments


@router.post("/{ticket_id}/dispatch", response_model=DispatchTicketResponse)
def dispatch_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Process a ticket using the AI dispatcher agent.

    This endpoint takes a ticket ID, fetches the ticket from the database,
    and uses an AI agent to:
    - Assess priority (high/medium/low)
    - Assign appropriate crews based on location and issue type
    - Assign relevant staff members
    - Categorize with appropriate labels
    - Generate a response comment for the citizen

    Args:
        ticket_id: UUID of the ticket to process
        db: Database session

    Returns:
        Dispatcher recommendations including status, priority, assignees, labels, and comment

    Raises:
        HTTPException: 404 if ticket not found, 500 if AI agent fails or API key is missing
    """
    settings = get_settings()

    # Check if API key is configured
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=500,
            detail="Anthropic API key not configured. Set ANTHROPIC_API_KEY in environment."
        )

    # Fetch the ticket from the database
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        # Call the dispatcher agent with the ticket model
        result = dispatch_ticket_model(
            ticket_model=ticket,
            db=db,
            api_key=settings.anthropic_api_key
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dispatcher agent failed: {str(e)}"
        )
