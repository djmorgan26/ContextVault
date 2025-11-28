"""
User model for authentication and encryption key management.
"""

from sqlalchemy import Column, String, TIMESTAMP, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class User(Base):
    """
    User model representing authenticated users.

    Users authenticate via Google OAuth. Each user has a unique encryption_salt
    used to derive their master encryption key.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Google OAuth identity
    google_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture_url = Column(String, nullable=True)

    # Encryption salt for PBKDF2 key derivation (hex-encoded 32 bytes)
    encryption_salt = Column(String(64), nullable=False)

    # User preferences (JSON)
    preferences = Column(JSON, default={}, nullable=False)

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
    vault_items = relationship("VaultItem", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
