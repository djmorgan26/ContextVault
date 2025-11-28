"""
Tag model for organizing vault items.
"""

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


# Many-to-many association table
vault_item_tags = Table(
    "vault_item_tags",
    Base.metadata,
    Column("vault_item_id", UUID(as_uuid=True), ForeignKey("vault_items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
    Index("idx_vault_item_tags_tag_id", "tag_id"),
)


class Tag(Base):
    """
    Tag model for organizing vault items.

    Tags are user-defined labels with optional colors.
    """

    __tablename__ = "tags"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Tag properties
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code, e.g., #FF5733

    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="tags")
    vault_items = relationship("VaultItem", secondary=vault_item_tags, back_populates="tags")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag_name"),
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"
