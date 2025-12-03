from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timezone

from ..database import get_db
from ..models.civitas import (
    Ticket as TicketModel,
    TicketStatus,
    TicketPriority,
    CivitasUser as UserModel,
    SupportCrew as CrewModel,
    Label as LabelModel,
    TicketComment as CommentModel,
    TicketUpdateLog as UpdateLogModel,
)
from ..schemas.civitas import (
    Ticket,
    TicketWithRelations,
    TicketCreate,
    TicketUpdate,
    TicketComment,
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentWithUser,
    TicketUpdateLog,
    TicketUpdateLogCreate,
    TicketUpdateLogWithUser,
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
    ticket = (
        db.query(TicketModel)
        .options(
            selectinload(TicketModel.user_assignees),
            selectinload(TicketModel.crew_assignees),
            selectinload(TicketModel.reporter),
            selectinload(TicketModel.labels)
        )
        .filter(TicketModel.ticket_id == ticket_id)
        .first()
    )

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
    priority: Optional[TicketPriority] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated tickets ordered by last update time (most recent first).

    Args:
        skip: Number of tickets to skip (for pagination)
        limit: Maximum number of tickets to return (default 100, max 100)
        status: Optional filter by ticket status
        priority: Optional filter by ticket priority
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

    # Filter by priority if provided
    if priority is not None:
        query = query.filter(TicketModel.priority == priority)

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


@router.post("/", response_model=Ticket, status_code=201)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new ticket.

    Args:
        ticket_data: The ticket data
        db: Database session

    Returns:
        Created ticket

    Raises:
        HTTPException: 400 if reporter not found or invalid assignee IDs
    """
    # Verify reporter exists if provided
    if ticket_data.reporter_id is not None:
        reporter = db.query(UserModel).filter(UserModel.user_id == ticket_data.reporter_id).first()
        if reporter is None:
            raise HTTPException(status_code=400, detail="Reporter user not found")

    # Create ticket
    ticket = TicketModel(
        ticket_subject=ticket_data.ticket_subject,
        ticket_body=ticket_data.ticket_body,
        origin=ticket_data.origin,
        status=ticket_data.status,
        priority=ticket_data.priority,
        reporter_id=ticket_data.reporter_id,
        location_coordinates=deserialize_location(ticket_data.location_coordinates),
        meta_data=ticket_data.meta_data,
    )

    # Add user assignees if provided
    if ticket_data.user_assignee_ids:
        users = db.query(UserModel).filter(UserModel.user_id.in_(ticket_data.user_assignee_ids)).all()
        if len(users) != len(ticket_data.user_assignee_ids):
            raise HTTPException(status_code=400, detail="One or more user assignees not found")
        ticket.user_assignees = users

    # Add crew assignees if provided
    if ticket_data.crew_assignee_ids:
        crews = db.query(CrewModel).filter(CrewModel.team_id.in_(ticket_data.crew_assignee_ids)).all()
        if len(crews) != len(ticket_data.crew_assignee_ids):
            raise HTTPException(status_code=400, detail="One or more crew assignees not found")
        ticket.crew_assignees = crews

    # Add labels if provided
    if ticket_data.label_ids:
        labels = db.query(LabelModel).filter(LabelModel.label_id.in_(ticket_data.label_ids)).all()
        if len(labels) != len(ticket_data.label_ids):
            raise HTTPException(status_code=400, detail="One or more labels not found")
        ticket.labels = labels

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Serialize the location coordinates
    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }

    return ticket_dict


@router.patch("/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: UUID,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a ticket.

    Args:
        ticket_id: The UUID of the ticket to update
        ticket_data: The updated ticket data
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket not found, 400 if invalid references
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update basic fields
    if ticket_data.ticket_subject is not None:
        ticket.ticket_subject = ticket_data.ticket_subject
    if ticket_data.ticket_body is not None:
        ticket.ticket_body = ticket_data.ticket_body
    if ticket_data.origin is not None:
        ticket.origin = ticket_data.origin
    if ticket_data.status is not None:
        ticket.status = ticket_data.status
    if ticket_data.priority is not None:
        ticket.priority = ticket_data.priority
    if ticket_data.reporter_id is not None:
        reporter = db.query(UserModel).filter(UserModel.user_id == ticket_data.reporter_id).first()
        if reporter is None:
            raise HTTPException(status_code=400, detail="Reporter user not found")
        ticket.reporter_id = ticket_data.reporter_id
    if ticket_data.location_coordinates is not None:
        ticket.location_coordinates = deserialize_location(ticket_data.location_coordinates)
    if ticket_data.meta_data is not None:
        ticket.meta_data = ticket_data.meta_data

    # Update user assignees if provided
    if ticket_data.user_assignee_ids is not None:
        users = db.query(UserModel).filter(UserModel.user_id.in_(ticket_data.user_assignee_ids)).all()
        if len(users) != len(ticket_data.user_assignee_ids):
            raise HTTPException(status_code=400, detail="One or more user assignees not found")
        ticket.user_assignees = users

    # Update crew assignees if provided
    if ticket_data.crew_assignee_ids is not None:
        crews = db.query(CrewModel).filter(CrewModel.team_id.in_(ticket_data.crew_assignee_ids)).all()
        if len(crews) != len(ticket_data.crew_assignee_ids):
            raise HTTPException(status_code=400, detail="One or more crew assignees not found")
        ticket.crew_assignees = crews

    # Update labels if provided
    if ticket_data.label_ids is not None:
        labels = db.query(LabelModel).filter(LabelModel.label_id.in_(ticket_data.label_ids)).all()
        if len(labels) != len(ticket_data.label_ids):
            raise HTTPException(status_code=400, detail="One or more labels not found")
        ticket.labels = labels

    db.commit()
    db.refresh(ticket)

    # Serialize the location coordinates
    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }

    return ticket_dict


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


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a ticket.

    Args:
        ticket_id: The UUID of the ticket to delete
        db: Database session

    Raises:
        HTTPException: 404 if ticket not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()

    return None


# ============================================================================
# Ticket Assignment Endpoints
# ============================================================================

class AssignUserRequest(BaseModel):
    """Schema for assigning users to a ticket."""
    user_ids: List[UUID]


class AssignCrewRequest(BaseModel):
    """Schema for assigning crews to a ticket."""
    crew_ids: List[UUID]


@router.post("/{ticket_id}/assign-users", response_model=Ticket)
def assign_users_to_ticket(
    ticket_id: UUID,
    assignment: AssignUserRequest,
    db: Session = Depends(get_db)
):
    """
    Assign users to a ticket (replaces existing user assignees).

    Args:
        ticket_id: The UUID of the ticket
        assignment: User IDs to assign
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket not found, 400 if users not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    users = db.query(UserModel).filter(UserModel.user_id.in_(assignment.user_ids)).all()
    if len(users) != len(assignment.user_ids):
        raise HTTPException(status_code=400, detail="One or more users not found")

    ticket.user_assignees = users
    db.commit()
    db.refresh(ticket)

    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }
    return ticket_dict


@router.post("/{ticket_id}/assign-crews", response_model=Ticket)
def assign_crews_to_ticket(
    ticket_id: UUID,
    assignment: AssignCrewRequest,
    db: Session = Depends(get_db)
):
    """
    Assign crews to a ticket (replaces existing crew assignees).

    Args:
        ticket_id: The UUID of the ticket
        assignment: Crew IDs to assign
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket not found, 400 if crews not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    crews = db.query(CrewModel).filter(CrewModel.team_id.in_(assignment.crew_ids)).all()
    if len(crews) != len(assignment.crew_ids):
        raise HTTPException(status_code=400, detail="One or more crews not found")

    ticket.crew_assignees = crews
    db.commit()
    db.refresh(ticket)

    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }
    return ticket_dict


@router.delete("/{ticket_id}/unassign-user/{user_id}", response_model=Ticket)
def unassign_user_from_ticket(
    ticket_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Remove a user assignee from a ticket.

    Args:
        ticket_id: The UUID of the ticket
        user_id: The UUID of the user to unassign
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket or user not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user in ticket.user_assignees:
        ticket.user_assignees.remove(user)
        db.commit()
        db.refresh(ticket)

    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }
    return ticket_dict


@router.delete("/{ticket_id}/unassign-crew/{crew_id}", response_model=Ticket)
def unassign_crew_from_ticket(
    ticket_id: UUID,
    crew_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Remove a crew assignee from a ticket.

    Args:
        ticket_id: The UUID of the ticket
        crew_id: The UUID of the crew to unassign
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket or crew not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    crew = db.query(CrewModel).filter(CrewModel.team_id == crew_id).first()
    if crew is None:
        raise HTTPException(status_code=404, detail="Crew not found")

    if crew in ticket.crew_assignees:
        ticket.crew_assignees.remove(crew)
        db.commit()
        db.refresh(ticket)

    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }
    return ticket_dict


# ============================================================================
# Ticket Comment Endpoints
# ============================================================================

@router.get("/{ticket_id}/comments", response_model=List[TicketCommentWithUser])
def get_ticket_comments(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all comments for a ticket.

    Args:
        ticket_id: The UUID of the ticket
        db: Database session

    Returns:
        List of comments with commenter details

    Raises:
        HTTPException: 404 if ticket not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    comments = db.query(CommentModel).filter(
        CommentModel.ticket_id == ticket_id
    ).order_by(CommentModel.time_created).all()

    return comments


@router.post("/{ticket_id}/comments", response_model=TicketCommentWithUser, status_code=201)
def create_ticket_comment(
    ticket_id: UUID,
    comment_data: TicketCommentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a ticket.

    Args:
        ticket_id: The UUID of the ticket
        comment_data: The comment data
        db: Database session

    Returns:
        Created comment

    Raises:
        HTTPException: 404 if ticket not found, 400 if commenter not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Verify commenter exists
    commenter = db.query(UserModel).filter(UserModel.user_id == comment_data.commenter).first()
    if commenter is None:
        raise HTTPException(status_code=400, detail="Commenter user not found")

    comment = CommentModel(
        comment_body=comment_data.comment_body,
        commenter=comment_data.commenter,
        ticket_id=ticket_id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.patch("/comments/{comment_id}", response_model=TicketCommentWithUser)
def update_ticket_comment(
    comment_id: UUID,
    comment_data: TicketCommentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a ticket comment.

    Args:
        comment_id: The UUID of the comment
        comment_data: The updated comment data
        db: Database session

    Returns:
        Updated comment

    Raises:
        HTTPException: 404 if comment not found
    """
    comment = db.query(CommentModel).filter(CommentModel.comment_id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment_data.comment_body is not None:
        comment.comment_body = comment_data.comment_body
        comment.is_edited = True
        comment.time_edited = datetime.now(timezone.utc)

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_ticket_comment(
    comment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a ticket comment.

    Args:
        comment_id: The UUID of the comment
        db: Database session

    Raises:
        HTTPException: 404 if comment not found
    """
    comment = db.query(CommentModel).filter(CommentModel.comment_id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return None


# ============================================================================
# Ticket Label Endpoints
# ============================================================================

class ManageLabelsRequest(BaseModel):
    """Schema for managing labels on a ticket."""
    label_ids: List[UUID]


@router.post("/{ticket_id}/labels", response_model=Ticket)
def set_ticket_labels(
    ticket_id: UUID,
    labels_data: ManageLabelsRequest,
    db: Session = Depends(get_db)
):
    """
    Set labels on a ticket (replaces existing labels).

    Args:
        ticket_id: The UUID of the ticket
        labels_data: Label IDs to set
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket not found, 400 if labels not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    labels = db.query(LabelModel).filter(LabelModel.label_id.in_(labels_data.label_ids)).all()
    if len(labels) != len(labels_data.label_ids):
        raise HTTPException(status_code=400, detail="One or more labels not found")

    ticket.labels = labels
    db.commit()
    db.refresh(ticket)

    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }
    return ticket_dict


@router.delete("/{ticket_id}/labels/{label_id}", response_model=Ticket)
def remove_label_from_ticket(
    ticket_id: UUID,
    label_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Remove a label from a ticket.

    Args:
        ticket_id: The UUID of the ticket
        label_id: The UUID of the label to remove
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: 404 if ticket or label not found
    """
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    label = db.query(LabelModel).filter(LabelModel.label_id == label_id).first()
    if label is None:
        raise HTTPException(status_code=404, detail="Label not found")

    if label in ticket.labels:
        ticket.labels.remove(label)
        db.commit()
        db.refresh(ticket)

    ticket_dict = {
        **ticket.__dict__,
        "location_coordinates": serialize_location(ticket.location_coordinates)
    }
    return ticket_dict
