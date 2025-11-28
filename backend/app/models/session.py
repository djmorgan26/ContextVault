"""
Session model for refresh token management.
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Session(Base):
    """
    Session model tracking user sessions for refresh token management.

    Refresh tokens are stored as SHA-256 hashes for security.
    """

    __tablename__ = "sessions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Refresh token (SHA-256 hash, not plaintext)
    refresh_token_hash = Column(String(128), nullable=False, index=True)

    # Session expiration
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)

    # Client information (for security auditing)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(INET, nullable=True)

    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id})>"

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
