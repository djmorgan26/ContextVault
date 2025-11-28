"""Schemas for vault items and tags."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class VaultItemType(str, Enum):
    """Type of vault item."""
    NOTE = "note"
    FILE = "file"
    MEDICAL_RECORD = "medical_record"
    PREFERENCE = "preference"
    MEASUREMENT = "measurement"
    OTHER = "other"


class VaultItemSource(str, Enum):
    """Source of vault item data."""
    MANUAL = "manual"
    EPIC = "epic"
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    IMPORT = "import"


class TagCreate(BaseModel):
    """Request to create a tag."""
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagUpdate(BaseModel):
    """Request to update a tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagResponse(BaseModel):
    """Tag response model."""
    id: str
    name: str
    color: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VaultItemCreate(BaseModel):
    """Request to create a vault item."""
    type: VaultItemType = VaultItemType.NOTE
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    tags: Optional[List[str]] = None  # Tag names
    metadata: Optional[dict] = None
    source: VaultItemSource = VaultItemSource.MANUAL
    source_id: Optional[str] = None


class VaultItemUpdate(BaseModel):
    """Request to update a vault item."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    type: Optional[VaultItemType] = None
    tags: Optional[List[str]] = None  # Tag names to replace
    metadata: Optional[dict] = None


class VaultItemResponse(BaseModel):
    """Vault item response model (decrypted)."""
    id: str
    type: VaultItemType
    title: str
    content: str
    metadata: Optional[dict] = None
    tags: List[str] = []
    source: VaultItemSource
    source_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VaultItemListResponse(BaseModel):
    """Paginated list of vault items."""
    items: List[VaultItemResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class VaultItemDeleteResponse(BaseModel):
    """Response from deleting a vault item."""
    id: str
    deleted_at: datetime
