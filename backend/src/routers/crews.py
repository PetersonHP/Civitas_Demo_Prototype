from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timezone

from ..database import get_db
from ..models.civitas import (
    SupportCrew as CrewModel,
    SupportCrewStatus,
    SupportCrewType,
    CivitasUser as UserModel,
)
from ..schemas.civitas import (
    SupportCrew,
    SupportCrewWithMembers,
)
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

router = APIRouter(
    prefix="/crews",
    tags=["crews"],
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


@router.get("/{team_id}", response_model=SupportCrewWithMembers)
def get_crew_by_id(team_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific crew by its ID with all related entities.

    Args:
        team_id: The UUID of the crew to retrieve
        db: Database session

    Returns:
        Crew with related members and leads

    Raises:
        HTTPException: 404 if crew not found
    """
    crew = (
        db.query(CrewModel)
        .options(
            selectinload(CrewModel.members),
            selectinload(CrewModel.leads),
        )
        .filter(CrewModel.team_id == team_id)
        .first()
    )

    if crew is None:
        raise HTTPException(status_code=404, detail="Crew not found")

    # Serialize the location coordinates
    crew_dict = {
        **crew.__dict__,
        "location_coordinates": serialize_location(crew.location_coordinates)
    }

    # Convert to response model
    return crew_dict


@router.get("/", response_model=List[SupportCrew])
def get_crews(
    skip: int = 0,
    limit: int = 100,
    status: Optional[SupportCrewStatus] = None,
    crew_type: Optional[SupportCrewType] = None,
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of crews with optional filtering.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Filter by crew status (active/inactive)
        crew_type: Filter by crew type
        db: Database session

    Returns:
        List of crews matching the filters

    Notes:
        - Results are ordered by creation time (newest first)
        - Location coordinates are serialized from PostGIS geometry
    """
    query = db.query(CrewModel)

    # Apply filters if provided
    if status:
        query = query.filter(CrewModel.status == status)
    if crew_type:
        query = query.filter(CrewModel.crew_type == crew_type)

    # Order by most recent first
    query = query.order_by(desc(CrewModel.time_created))

    # Apply pagination
    crews = query.offset(skip).limit(limit).all()

    # Serialize location coordinates for each crew
    result = []
    for crew in crews:
        crew_dict = {
            **crew.__dict__,
            "location_coordinates": serialize_location(crew.location_coordinates)
        }
        result.append(crew_dict)

    return result
