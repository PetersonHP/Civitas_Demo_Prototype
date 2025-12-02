from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid
import enum


# Enums
class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TicketOrigin(str, enum.Enum):
    PHONE = "phone"
    WEB_FORM = "web form"
    TEXT = "text"


class TicketStatus(str, enum.Enum):
    AWAITING_RESPONSE = "awaiting response"
    RESPONSE_IN_PROGRESS = "response in progress"
    RESOLVED = "resolved"


class TicketPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SupportCrewType(str, enum.Enum):
    POTHOLE_CREW = "pothole crew"
    DRAIN_CREW = "drain crew"
    TREE_CREW = "tree crew"
    SIGN_CREW = "sign crew"
    SNOW_CREW = "snow crew"
    SANITATION_CREW = "sanitation crew"


class SupportCrewStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# Association Tables for Many-to-Many relationships

# User <-> Role
user_roles_association = Table(
    'user_roles_association',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('civitas_role.role_id', ondelete='CASCADE'), primary_key=True)
)

# Ticket <-> User Assignees
ticket_user_assignees_association = Table(
    'ticket_user_assignees_association',
    Base.metadata,
    Column('ticket_id', UUID(as_uuid=True), ForeignKey('ticket.ticket_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='CASCADE'), primary_key=True)
)

# Ticket <-> Crew Assignees
ticket_crew_assignees_association = Table(
    'ticket_crew_assignees_association',
    Base.metadata,
    Column('ticket_id', UUID(as_uuid=True), ForeignKey('ticket.ticket_id', ondelete='CASCADE'), primary_key=True),
    Column('team_id', UUID(as_uuid=True), ForeignKey('support_crew.team_id', ondelete='CASCADE'), primary_key=True)
)

# Ticket <-> Labels
ticket_labels_association = Table(
    'ticket_labels_association',
    Base.metadata,
    Column('ticket_id', UUID(as_uuid=True), ForeignKey('ticket.ticket_id', ondelete='CASCADE'), primary_key=True),
    Column('label_id', UUID(as_uuid=True), ForeignKey('label.label_id', ondelete='CASCADE'), primary_key=True)
)

# Support Crew <-> Crew Members
crew_members_association = Table(
    'crew_members_association',
    Base.metadata,
    Column('team_id', UUID(as_uuid=True), ForeignKey('support_crew.team_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='CASCADE'), primary_key=True)
)

# Support Crew <-> Crew Leads
crew_leads_association = Table(
    'crew_leads_association',
    Base.metadata,
    Column('team_id', UUID(as_uuid=True), ForeignKey('support_crew.team_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='CASCADE'), primary_key=True)
)


class CivitasRole(Base):
    """Role model for user permissions."""

    __tablename__ = "civitas_role"

    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String, nullable=False, unique=True, index=True)

    # Relationships
    users = relationship("CivitasUser", secondary=user_roles_association, back_populates="roles")


class CivitasUser(Base):
    """User model for city admins and citizens."""

    __tablename__ = "civitas_user"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_last_login = Column(DateTime(timezone=True))
    email = Column(String, nullable=True, unique=True, index=True)
    phone_number = Column(String, nullable=True, index=True)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    google_id = Column(String, nullable=True, unique=True, index=True)
    google_email = Column(String, nullable=True)
    google_avatar_url = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True, default=dict)

    # Relationships
    roles = relationship("CivitasRole", secondary=user_roles_association, back_populates="users")
    assigned_tickets = relationship("Ticket", secondary=ticket_user_assignees_association, back_populates="user_assignees")
    reported_tickets = relationship("Ticket", back_populates="reporter", foreign_keys="Ticket.reporter_id")
    created_labels = relationship("Label", back_populates="creator", foreign_keys="Label.created_by")
    comments = relationship("TicketComment", back_populates="commenter_user", foreign_keys="TicketComment.commenter")
    update_logs = relationship("TicketUpdateLog", back_populates="origin_user", foreign_keys="TicketUpdateLog.user_of_origin")
    crew_memberships = relationship("SupportCrew", secondary=crew_members_association, back_populates="members")
    crew_lead_positions = relationship("SupportCrew", secondary=crew_leads_association, back_populates="leads")


class Ticket(Base):
    """Ticket model for support requests."""

    __tablename__ = "ticket"

    ticket_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ticket_subject = Column(String, nullable=False)
    ticket_body = Column(Text, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    origin = Column(SQLEnum(TicketOrigin), nullable=False)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.AWAITING_RESPONSE)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='SET NULL'), nullable=True, index=True)
    location_coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    meta_data = Column(JSON, nullable=True, default=dict)

    # Relationships
    user_assignees = relationship("CivitasUser", secondary=ticket_user_assignees_association, back_populates="assigned_tickets")
    crew_assignees = relationship("SupportCrew", secondary=ticket_crew_assignees_association, back_populates="assigned_tickets")
    reporter = relationship("CivitasUser", back_populates="reported_tickets", foreign_keys=[reporter_id])
    labels = relationship("Label", secondary=ticket_labels_association, back_populates="tickets")
    comments = relationship("TicketComment", back_populates="ticket", foreign_keys="TicketComment.ticket_id")
    update_logs = relationship("TicketUpdateLog", back_populates="ticket", foreign_keys="TicketUpdateLog.ticket_id")


class Label(Base):
    """Label model for categorizing tickets."""

    __tablename__ = "label"

    label_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    label_name = Column(String, nullable=False, unique=True, index=True)
    label_description = Column(Text, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='SET NULL'), nullable=True, index=True)
    color_hex = Column(String, nullable=False, default="#808080")
    meta_data = Column(JSON, nullable=True, default=dict)

    # Relationships
    creator = relationship("CivitasUser", back_populates="created_labels", foreign_keys=[created_by])
    tickets = relationship("Ticket", secondary=ticket_labels_association, back_populates="labels")


class TicketComment(Base):
    """Comment model for ticket discussions."""

    __tablename__ = "ticket_comment"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    comment_body = Column(Text, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_edited = Column(Boolean, nullable=False, default=False)
    time_edited = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    commenter = Column(UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='SET NULL'), nullable=True, index=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey('ticket.ticket_id', ondelete='CASCADE'), nullable=False, index=True)

    # Relationships
    commenter_user = relationship("CivitasUser", back_populates="comments", foreign_keys=[commenter])
    ticket = relationship("Ticket", back_populates="comments", foreign_keys=[ticket_id])


class TicketUpdateLog(Base):
    """Log model for tracking ticket updates."""

    __tablename__ = "ticket_update_log"

    update_log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey('ticket.ticket_id', ondelete='CASCADE'), nullable=False, index=True)
    user_of_origin = Column(UUID(as_uuid=True), ForeignKey('civitas_user.user_id', ondelete='SET NULL'), nullable=True, index=True)
    meta_data = Column(JSON, nullable=True, default=dict)

    # Relationships
    ticket = relationship("Ticket", back_populates="update_logs", foreign_keys=[ticket_id])
    origin_user = relationship("CivitasUser", back_populates="update_logs", foreign_keys=[user_of_origin])


class SupportCrew(Base):
    """Support crew model for managing work teams."""

    __tablename__ = "support_crew"

    team_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    team_name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    crew_type = Column(SQLEnum(SupportCrewType), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_edited = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(SQLEnum(SupportCrewStatus), nullable=False, default=SupportCrewStatus.ACTIVE)
    location_coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    meta_data = Column(JSON, nullable=True, default=dict)

    # Relationships
    assigned_tickets = relationship("Ticket", secondary=ticket_crew_assignees_association, back_populates="crew_assignees")
    members = relationship("CivitasUser", secondary=crew_members_association, back_populates="crew_memberships")
    leads = relationship("CivitasUser", secondary=crew_leads_association, back_populates="crew_lead_positions")
