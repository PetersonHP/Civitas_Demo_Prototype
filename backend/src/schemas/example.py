from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ItemBase(BaseModel):
    """Base schema for Item."""

    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """Schema for creating a new Item."""

    pass


class ItemUpdate(ItemBase):
    """Schema for updating an Item."""

    name: Optional[str] = None


class Item(ItemBase):
    """Schema for Item response."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
