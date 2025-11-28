"""
Integration models for external service connections (Epic, Fitbit, etc.).
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Enum, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class IntegrationProvider(str, enum.Enum):
    """External service providers."""
    EPIC = "epic"
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"


class IntegrationStatus(str, enum.Enum):
    """Integration connection states."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SYNCING = "syncing"


class TokenType(str, enum.Enum):
    """OAuth token types."""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"


class Integration(Base):
    """
    Integration model tracking connections to external services.

    Each user can have one integration per provider.
    """

    __tablename__ = "integrations"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Integration properties
    provider = Column(Enum(IntegrationProvider), nullable=False)
    status = Column(Enum(IntegrationStatus), nullable=False, default=IntegrationStatus.CONNECTED)

    # Provider-specific metadata (JSON)
    provider_metadata = Column(JSON, default={}, nullable=False)

    # Sync tracking
    last_sync_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_sync_error = Column(Text, nullable=True)

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

    # Relationships
    user = relationship("User", back_populates="integrations")
    tokens = relationship("IntegrationToken", back_populates="integration", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_provider"),
        Index("idx_integrations_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Integration(id={self.id}, provider={self.provider}, status={self.status})>"


class IntegrationToken(Base):
    """
    IntegrationToken model storing encrypted OAuth tokens.

    Tokens are encrypted with the user's master key.
    """

    __tablename__ = "integration_tokens"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to integration
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Token properties
    token_type = Column(Enum(TokenType), nullable=False)
    token_encrypted = Column(Text, nullable=False)  # AES-256-GCM encrypted
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)

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

    # Relationships
    integration = relationship("Integration", back_populates="tokens")

    # Indexes
    __table_args__ = (
        Index("idx_integration_tokens_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<IntegrationToken(id={self.id}, type={self.token_type})>"
