"""
VaultItem model for storing encrypted user data.
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class VaultItemType(str, enum.Enum):
    """Types of vault items."""
    NOTE = "note"
    FILE = "file"
    MEDICAL_RECORD = "medical_record"
    PREFERENCE = "preference"
    MEASUREMENT = "measurement"
    OTHER = "other"


class VaultItemSource(str, enum.Enum):
    """Sources where vault items originate."""
    MANUAL = "manual"
    EPIC = "epic"
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    IMPORT = "import"


class VaultItem(Base):
    """
    VaultItem model representing encrypted user data.

    Content and metadata are encrypted using the user's master key.
    Title is stored in plaintext for search functionality.
    """

    __tablename__ = "vault_items"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Item type and source
    type = Column(Enum(VaultItemType), nullable=False, default=VaultItemType.NOTE)
    source = Column(Enum(VaultItemSource), nullable=False, default=VaultItemSource.MANUAL)
    source_id = Column(String(255), nullable=True)  # External ID for deduplication

    # Content (plaintext title for search, encrypted content)
    title = Column(String(500), nullable=True)
    content_encrypted = Column(Text, nullable=False)
    metadata_encrypted = Column(Text, nullable=True)

    # File path for uploaded files
    file_path = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)  # Soft delete

    # Relationships
    user = relationship("User", back_populates="vault_items")
    tags = relationship("Tag", secondary="vault_item_tags", back_populates="vault_items")

    # Indexes
    __table_args__ = (
        Index("idx_vault_items_user_id", "user_id", postgresql_where=(deleted_at.is_(None))),
        Index("idx_vault_items_type", "type", postgresql_where=(deleted_at.is_(None))),
        Index("idx_vault_items_source", "source", postgresql_where=(deleted_at.is_(None))),
        Index("idx_vault_items_created_at", "created_at", postgresql_where=(deleted_at.is_(None))),
        Index("idx_vault_items_source_id", "source", "source_id", postgresql_where=(deleted_at.is_(None))),
    )

    def __repr__(self) -> str:
        return f"<VaultItem(id={self.id}, type={self.type}, title={self.title})>"

    @property
    def is_deleted(self) -> bool:
        """Check if item is soft-deleted."""
        return self.deleted_at is not None
