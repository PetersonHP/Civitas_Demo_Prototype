from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from ..models.civitas import (
    UserStatus,
    TicketOrigin,
    TicketStatus,
    TicketPriority,
    SupportCrewType,
    SupportCrewStatus,
)


# ============================================================================
# CivitasRole Schemas
# ============================================================================

class CivitasRoleBase(BaseModel):
    """Base schema for CivitasRole."""
    role_name: str = Field(..., min_length=1, max_length=255)


class CivitasRoleCreate(CivitasRoleBase):
    """Schema for creating a new role."""
    pass


class CivitasRoleUpdate(BaseModel):
    """Schema for updating a role."""
    role_name: Optional[str] = Field(None, min_length=1, max_length=255)


class CivitasRole(CivitasRoleBase):
    """Schema for role response."""
    role_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CivitasUser Schemas
# ============================================================================

class CivitasUserBase(BaseModel):
    """Base schema for CivitasUser."""
    firstname: str = Field(..., min_length=1, max_length=255)
    lastname: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    status: UserStatus = UserStatus.ACTIVE
    google_id: Optional[str] = Field(None, max_length=255)
    google_email: Optional[str] = Field(None, max_length=255)
    google_avatar_url: Optional[str] = Field(None, max_length=500)
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CivitasUserCreate(CivitasUserBase):
    """Schema for creating a new user."""
    role_ids: List[UUID] = Field(default_factory=list)


class CivitasUserUpdate(BaseModel):
    """Schema for updating a user."""
    firstname: Optional[str] = Field(None, min_length=1, max_length=255)
    lastname: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    status: Optional[UserStatus] = None
    google_id: Optional[str] = Field(None, max_length=255)
    google_email: Optional[str] = Field(None, max_length=255)
    google_avatar_url: Optional[str] = Field(None, max_length=500)
    meta_data: Optional[Dict[str, Any]] = None
    role_ids: Optional[List[UUID]] = None


class CivitasUser(CivitasUserBase):
    """Schema for user response."""
    user_id: UUID
    time_created: datetime
    time_updated: Optional[datetime] = None
    time_last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CivitasUserWithRoles(CivitasUser):
    """Schema for user response with roles included."""
    roles: List[CivitasRole] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Label Schemas
# ============================================================================

class LabelBase(BaseModel):
    """Base schema for Label."""
    label_name: str = Field(..., min_length=1, max_length=255)
    label_description: Optional[str] = None
    color_hex: str = Field(default="#808080", pattern=r"^#[0-9A-Fa-f]{6}$")
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LabelCreate(LabelBase):
    """Schema for creating a new label."""
    pass


class LabelUpdate(BaseModel):
    """Schema for updating a label."""
    label_name: Optional[str] = Field(None, min_length=1, max_length=255)
    label_description: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    meta_data: Optional[Dict[str, Any]] = None


class Label(LabelBase):
    """Schema for label response."""
    label_id: UUID
    time_created: datetime
    time_updated: Optional[datetime] = None
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Ticket Schemas
# ============================================================================

class TicketBase(BaseModel):
    """Base schema for Ticket."""
    ticket_subject: str = Field(..., min_length=1, max_length=500)
    ticket_body: str = Field(..., min_length=1)
    origin: TicketOrigin
    status: TicketStatus = TicketStatus.AWAITING_RESPONSE
    priority: TicketPriority = TicketPriority.MEDIUM
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TicketCreate(TicketBase):
    """Schema for creating a new ticket."""
    reporter_id: UUID
    user_assignee_ids: List[UUID] = Field(default_factory=list)
    crew_assignee_ids: List[UUID] = Field(default_factory=list)
    label_ids: List[UUID] = Field(default_factory=list)
    location_coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Coordinates as {lat: float, lng: float}"
    )

    @field_validator('location_coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if v is not None:
            if 'lat' not in v or 'lng' not in v:
                raise ValueError("Coordinates must contain 'lat' and 'lng' keys")
            if not (-90 <= v['lat'] <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= v['lng'] <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        return v


class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    ticket_subject: Optional[str] = Field(None, min_length=1, max_length=500)
    ticket_body: Optional[str] = Field(None, min_length=1)
    origin: Optional[TicketOrigin] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    reporter_id: Optional[UUID] = None
    user_assignee_ids: Optional[List[UUID]] = None
    crew_assignee_ids: Optional[List[UUID]] = None
    label_ids: Optional[List[UUID]] = None
    location_coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Coordinates as {lat: float, lng: float}"
    )
    meta_data: Optional[Dict[str, Any]] = None

    @field_validator('location_coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if v is not None:
            if 'lat' not in v or 'lng' not in v:
                raise ValueError("Coordinates must contain 'lat' and 'lng' keys")
            if not (-90 <= v['lat'] <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= v['lng'] <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        return v


class Ticket(TicketBase):
    """Schema for ticket response."""
    ticket_id: UUID
    time_created: datetime
    time_updated: Optional[datetime] = None
    reporter_id: Optional[UUID] = None
    location_coordinates: Optional[Dict[str, float]] = None

    model_config = ConfigDict(from_attributes=True)


class TicketWithRelations(Ticket):
    """Schema for ticket response with related entities."""
    user_assignees: List[CivitasUser] = Field(default_factory=list)
    crew_assignees: List["SupportCrew"] = Field(default_factory=list)
    reporter: Optional[CivitasUser] = None
    labels: List[Label] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TicketComment Schemas
# ============================================================================

class TicketCommentBase(BaseModel):
    """Base schema for TicketComment."""
    comment_body: str = Field(..., min_length=1)


class TicketCommentCreate(TicketCommentBase):
    """Schema for creating a new comment."""
    ticket_id: UUID
    commenter: UUID


class TicketCommentUpdate(BaseModel):
    """Schema for updating a comment."""
    comment_body: Optional[str] = Field(None, min_length=1)


class TicketComment(TicketCommentBase):
    """Schema for comment response."""
    comment_id: UUID
    time_created: datetime
    is_edited: bool = False
    time_edited: Optional[datetime] = None
    commenter: Optional[UUID] = None
    ticket_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TicketCommentWithUser(TicketComment):
    """Schema for comment response with commenter details."""
    commenter_user: Optional[CivitasUser] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TicketUpdateLog Schemas
# ============================================================================

class TicketUpdateLogBase(BaseModel):
    """Base schema for TicketUpdateLog."""
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TicketUpdateLogCreate(TicketUpdateLogBase):
    """Schema for creating a new update log."""
    ticket_id: UUID
    user_of_origin: UUID


class TicketUpdateLog(TicketUpdateLogBase):
    """Schema for update log response."""
    update_log_id: UUID
    time_created: datetime
    ticket_id: UUID
    user_of_origin: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class TicketUpdateLogWithUser(TicketUpdateLog):
    """Schema for update log response with user details."""
    origin_user: Optional[CivitasUser] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SupportCrew Schemas
# ============================================================================

class SupportCrewBase(BaseModel):
    """Base schema for SupportCrew."""
    team_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    crew_type: SupportCrewType
    status: SupportCrewStatus = SupportCrewStatus.ACTIVE
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SupportCrewCreate(SupportCrewBase):
    """Schema for creating a new support crew."""
    member_ids: List[UUID] = Field(default_factory=list)
    lead_ids: List[UUID] = Field(default_factory=list)
    location_coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Coordinates as {lat: float, lng: float}"
    )

    @field_validator('location_coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if v is not None:
            if 'lat' not in v or 'lng' not in v:
                raise ValueError("Coordinates must contain 'lat' and 'lng' keys")
            if not (-90 <= v['lat'] <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= v['lng'] <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        return v


class SupportCrewUpdate(BaseModel):
    """Schema for updating a support crew."""
    team_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    crew_type: Optional[SupportCrewType] = None
    status: Optional[SupportCrewStatus] = None
    member_ids: Optional[List[UUID]] = None
    lead_ids: Optional[List[UUID]] = None
    location_coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Coordinates as {lat: float, lng: float}"
    )
    meta_data: Optional[Dict[str, Any]] = None

    @field_validator('location_coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if v is not None:
            if 'lat' not in v or 'lng' not in v:
                raise ValueError("Coordinates must contain 'lat' and 'lng' keys")
            if not (-90 <= v['lat'] <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= v['lng'] <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        return v


class SupportCrew(SupportCrewBase):
    """Schema for support crew response."""
    team_id: UUID
    time_created: datetime
    time_edited: Optional[datetime] = None
    location_coordinates: Optional[Dict[str, float]] = None

    model_config = ConfigDict(from_attributes=True)


class SupportCrewWithMembers(SupportCrew):
    """Schema for support crew response with members and leads."""
    members: List[CivitasUser] = Field(default_factory=list)
    leads: List[CivitasUser] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Resolve forward references for circular dependencies
TicketWithRelations.model_rebuild()
