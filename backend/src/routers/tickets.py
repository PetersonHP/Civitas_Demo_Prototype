from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from ..database import get_db
from ..models.civitas import Ticket as TicketModel, TicketStatus
from ..schemas.civitas import (
    Ticket,
    TicketWithRelations,
    TicketCreate,
    TicketUpdate,
)
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


def serialize_location(location):
    """Convert PostGIS geometry to dict."""
    if location is None:
        return None
    point = to_shape(location)
    return {"lat": point.y, "lng": point.x}


def deserialize_location(coords: dict) -> WKTElement:
    """Convert dict to PostGIS geometry."""
    if coords is None:
        return None
    return WKTElement(f"POINT({coords['lng']} {coords['lat']})", srid=4326)


@router.get("/{ticket_id}", response_model=TicketWithRelations)
def get_ticket_by_id(ticket_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific ticket by its ID with all related entities.

    Args:
        ticket_id: The UUID of the ticket to retrieve
        db: Database session

    Returns:
        Ticket with related user assignees, crew assignees, reporter, and labels

    Raises:
        HTTPException: 404 if ticket not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Serialize the location coordinates
    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }

    # Convert to response model
    return ticket_dict


@router.get("/", response_model=List[Ticket])
def get_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated tickets ordered by last update time (most recent first).

    Args:
        skip: Number of tickets to skip (for pagination)
        limit: Maximum number of tickets to return (default 100, max 100)
        status: Optional filter by ticket status
        db: Database session

    Returns:
        List of tickets ordered by time_updated (descending)
    """
    # Limit max page size
    if limit > 100:
        limit = 100

    query = db.query(TicketModel)

    # Filter by status if provided
    if status is not None:
        query = query.filter(TicketModel.status == status)

    # Order by time_updated (most recent first), falling back to time_created if null
    # SQLAlchemy handles the case where time_updated is null
    tickets = (
        query
        .order_by(desc(TicketModel.time_updated), desc(TicketModel.time_created))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Serialize location coordinates for each ticket
    result = []
    for ticket in tickets:
        ticket_dict = {
            **ticket.__dict__,
            "location_coordinates": serialize_location(ticket.location_coordinates)
        }
        result.append(ticket_dict)

    return result


class TicketStatusUpdate(BaseModel):
    """Schema for updating ticket status."""
    status: TicketStatus


@router.patch("/{ticket_id}/status", response_model=Ticket)
def update_ticket_status(
    ticket_id: UUID,
    status_update: TicketStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the status of a ticket.

    Args:
        ticket_id: The UUID of the ticket to update
        status_update: The new status for the ticket
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update the status
    ticket.status = status_update.status

    db.commit()
    db.refresh(ticket)

    # Serialize the location coordinates
    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }

    return ticket_dict
