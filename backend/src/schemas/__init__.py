# Pydantic schemas
from .example import Item, ItemCreate, ItemUpdate
from .civitas import (
    # Role schemas
    CivitasRole,
    CivitasRoleCreate,
    CivitasRoleUpdate,
    # User schemas
    CivitasUser,
    CivitasUserCreate,
    CivitasUserUpdate,
    CivitasUserWithRoles,
    # Label schemas
    Label,
    LabelCreate,
    LabelUpdate,
    # Ticket schemas
    Ticket,
    TicketCreate,
    TicketUpdate,
    TicketWithRelations,
    # Comment schemas
    TicketComment,
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentWithUser,
    # Update log schemas
    TicketUpdateLog,
    TicketUpdateLogCreate,
    TicketUpdateLogWithUser,
    # Support crew schemas
    SupportCrew,
    SupportCrewCreate,
    SupportCrewUpdate,
    SupportCrewWithMembers,
)

__all__ = [
    "Item",
    "ItemCreate",
    "ItemUpdate",
    # Role schemas
    "CivitasRole",
    "CivitasRoleCreate",
    "CivitasRoleUpdate",
    # User schemas
    "CivitasUser",
    "CivitasUserCreate",
    "CivitasUserUpdate",
    "CivitasUserWithRoles",
    # Label schemas
    "Label",
    "LabelCreate",
    "LabelUpdate",
    # Ticket schemas
    "Ticket",
    "TicketCreate",
    "TicketUpdate",
    "TicketWithRelations",
    # Comment schemas
    "TicketComment",
    "TicketCommentCreate",
    "TicketCommentUpdate",
    "TicketCommentWithUser",
    # Update log schemas
    "TicketUpdateLog",
    "TicketUpdateLogCreate",
    "TicketUpdateLogWithUser",
    # Support crew schemas
    "SupportCrew",
    "SupportCrewCreate",
    "SupportCrewUpdate",
    "SupportCrewWithMembers",
]
