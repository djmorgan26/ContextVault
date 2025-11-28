"""
Vault service for managing encrypted vault items.

Handles encryption/decryption of vault items and tag management.
"""

import json
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from app.models.vault_item import VaultItem, VaultItemType, VaultItemSource
from app.models.tag import Tag, vault_item_tags
from app.models.user import User
from app.core.encryption import encrypt_content, decrypt_content, EncryptionError
from app.schemas.vault import (
    VaultItemCreate,
    VaultItemUpdate,
    VaultItemResponse,
    TagCreate,
    TagUpdate,
    TagResponse,
)


class VaultService:
    """Service for vault item operations."""

    def __init__(self, db: Session, user_id: UUID, master_key: bytes):
        """
        Initialize vault service.

        Args:
            db: Database session
            user_id: Authenticated user's ID
            master_key: User's master encryption key (derived from Google ID)
        """
        self.db = db
        self.user_id = user_id
        self.master_key = master_key

    def create_item(self, item_data: VaultItemCreate) -> VaultItemResponse:
        """
        Create a new vault item with encrypted content.

        Args:
            item_data: Vault item creation data

        Returns:
            Created vault item (decrypted)

        Raises:
            EncryptionError: If encryption fails
        """
        # Encrypt content
        try:
            encrypted_content = encrypt_content(item_data.content, self.master_key)
        except EncryptionError as e:
            raise Exception(f"Failed to encrypt vault item: {str(e)}")

        # Encrypt metadata if provided
        encrypted_metadata = None
        if item_data.metadata:
            try:
                metadata_json = json.dumps(item_data.metadata)
                encrypted_metadata = encrypt_content(metadata_json, self.master_key)
            except EncryptionError as e:
                raise Exception(f"Failed to encrypt metadata: {str(e)}")

        # Create vault item
        vault_item = VaultItem(
            user_id=self.user_id,
            type=item_data.type,
            title=item_data.title,
            content_encrypted=encrypted_content,
            metadata_encrypted=encrypted_metadata,
            source=item_data.source,
            source_id=item_data.source_id,
        )

        self.db.add(vault_item)
        self.db.flush()  # Get the ID

        # Add tags
        if item_data.tags:
            self._add_tags_to_item(vault_item, item_data.tags)

        self.db.commit()

        return self._vault_item_to_response(vault_item)

    def get_item(self, item_id: UUID) -> Optional[VaultItemResponse]:
        """
        Retrieve and decrypt a vault item.

        Args:
            item_id: ID of vault item

        Returns:
            Decrypted vault item or None if not found

        Raises:
            EncryptionError: If decryption fails
        """
        vault_item = self.db.query(VaultItem).filter(
            and_(
                VaultItem.id == item_id,
                VaultItem.user_id == self.user_id,
                VaultItem.deleted_at.is_(None)
            )
        ).first()

        if not vault_item:
            return None

        return self._vault_item_to_response(vault_item)

    def list_items(
        self,
        page: int = 1,
        page_size: int = 50,
        item_type: Optional[VaultItemType] = None,
        source: Optional[VaultItemSource] = None,
        tag_names: Optional[List[str]] = None,
        search_title: Optional[str] = None,
    ) -> dict:
        """
        List user's vault items with filtering and pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            item_type: Filter by item type
            source: Filter by source
            tag_names: Filter by tag names (OR logic)
            search_title: Search in title (full-text)

        Returns:
            Paginated list of decrypted vault items
        """
        # Build query
        query = self.db.query(VaultItem).filter(
            and_(
                VaultItem.user_id == self.user_id,
                VaultItem.deleted_at.is_(None)
            )
        )

        # Apply filters
        if item_type:
            query = query.filter(VaultItem.type == item_type)

        if source:
            query = query.filter(VaultItem.source == source)

        if search_title:
            query = query.filter(
                VaultItem.title.ilike(f"%{search_title}%")
            )

        if tag_names:
            # Filter by tags (OR logic: item has any of these tags)
            tags = self.db.query(Tag).filter(
                and_(
                    Tag.user_id == self.user_id,
                    Tag.name.in_(tag_names)
                )
            ).all()
            if tags:
                tag_ids = [t.id for t in tags]
                query = query.filter(
                    VaultItem.tags.any(Tag.id.in_(tag_ids))
                )

        # Sort by creation date (newest first)
        query = query.order_by(VaultItem.created_at.desc())

        # Get total count
        total = query.count()

        # Paginate
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        # Decrypt items
        decrypted_items = [self._vault_item_to_response(item) for item in items]

        return {
            "items": decrypted_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (offset + page_size) < total,
        }

    def update_item(self, item_id: UUID, update_data: VaultItemUpdate) -> Optional[VaultItemResponse]:
        """
        Update a vault item.

        Args:
            item_id: ID of vault item
            update_data: Fields to update

        Returns:
            Updated vault item or None if not found

        Raises:
            EncryptionError: If encryption fails
        """
        vault_item = self.db.query(VaultItem).filter(
            and_(
                VaultItem.id == item_id,
                VaultItem.user_id == self.user_id,
                VaultItem.deleted_at.is_(None)
            )
        ).first()

        if not vault_item:
            return None

        # Update fields
        if update_data.title is not None:
            vault_item.title = update_data.title

        if update_data.type is not None:
            vault_item.type = update_data.type

        if update_data.content is not None:
            try:
                vault_item.content_encrypted = encrypt_content(
                    update_data.content, self.master_key
                )
            except EncryptionError as e:
                raise Exception(f"Failed to encrypt vault item: {str(e)}")

        if update_data.metadata is not None:
            try:
                metadata_json = json.dumps(update_data.metadata)
                vault_item.metadata_encrypted = encrypt_content(
                    metadata_json, self.master_key
                )
            except EncryptionError as e:
                raise Exception(f"Failed to encrypt metadata: {str(e)}")

        if update_data.tags is not None:
            # Replace tags
            vault_item.tags.clear()
            self._add_tags_to_item(vault_item, update_data.tags)

        self.db.commit()

        return self._vault_item_to_response(vault_item)

    def delete_item(self, item_id: UUID) -> Optional[datetime]:
        """
        Soft-delete a vault item.

        Args:
            item_id: ID of vault item

        Returns:
            Deletion timestamp or None if not found
        """
        vault_item = self.db.query(VaultItem).filter(
            and_(
                VaultItem.id == item_id,
                VaultItem.user_id == self.user_id,
                VaultItem.deleted_at.is_(None)
            )
        ).first()

        if not vault_item:
            return None

        vault_item.deleted_at = datetime.utcnow()
        self.db.commit()

        return vault_item.deleted_at

    def _vault_item_to_response(self, vault_item: VaultItem) -> VaultItemResponse:
        """
        Convert database vault item to response (decrypt content).

        Args:
            vault_item: Database model

        Returns:
            Decrypted vault item response

        Raises:
            EncryptionError: If decryption fails
        """
        # Decrypt content
        try:
            content = decrypt_content(
                vault_item.content_encrypted, self.master_key
            )
        except EncryptionError as e:
            raise Exception(f"Failed to decrypt vault item: {str(e)}")

        # Decrypt metadata
        metadata = None
        if vault_item.metadata_encrypted:
            try:
                metadata_json = decrypt_content(
                    vault_item.metadata_encrypted, self.master_key
                )
                metadata = json.loads(metadata_json)
            except (EncryptionError, json.JSONDecodeError) as e:
                raise Exception(f"Failed to decrypt metadata: {str(e)}")

        # Get tags
        tag_names = [tag.name for tag in vault_item.tags]

        return VaultItemResponse(
            id=str(vault_item.id),
            type=vault_item.type,
            title=vault_item.title,
            content=content,
            metadata=metadata,
            tags=tag_names,
            source=vault_item.source,
            source_id=vault_item.source_id,
            created_at=vault_item.created_at,
            updated_at=vault_item.updated_at,
        )

    def _add_tags_to_item(self, vault_item: VaultItem, tag_names: List[str]):
        """
        Add or create tags for a vault item.

        Args:
            vault_item: Vault item to tag
            tag_names: List of tag names
        """
        for tag_name in tag_names:
            # Get or create tag
            tag = self.db.query(Tag).filter(
                and_(
                    Tag.user_id == self.user_id,
                    Tag.name == tag_name
                )
            ).first()

            if not tag:
                tag = Tag(user_id=self.user_id, name=tag_name)
                self.db.add(tag)
                self.db.flush()

            # Add to item if not already added
            if tag not in vault_item.tags:
                vault_item.tags.append(tag)


class TagService:
    """Service for tag operations."""

    def __init__(self, db: Session, user_id: UUID):
        """
        Initialize tag service.

        Args:
            db: Database session
            user_id: Authenticated user's ID
        """
        self.db = db
        self.user_id = user_id

    def create_tag(self, tag_data: TagCreate) -> TagResponse:
        """
        Create a new tag.

        Args:
            tag_data: Tag creation data

        Returns:
            Created tag

        Raises:
            Exception: If tag name already exists for this user
        """
        # Check if tag already exists
        existing = self.db.query(Tag).filter(
            and_(
                Tag.user_id == self.user_id,
                Tag.name == tag_data.name
            )
        ).first()

        if existing:
            raise Exception(f"Tag '{tag_data.name}' already exists")

        tag = Tag(
            user_id=self.user_id,
            name=tag_data.name,
            color=tag_data.color,
        )

        self.db.add(tag)
        self.db.commit()

        return TagResponse.from_orm(tag)

    def get_tag(self, tag_id: UUID) -> Optional[TagResponse]:
        """
        Get a tag by ID.

        Args:
            tag_id: Tag ID

        Returns:
            Tag or None if not found
        """
        tag = self.db.query(Tag).filter(
            and_(
                Tag.id == tag_id,
                Tag.user_id == self.user_id
            )
        ).first()

        if not tag:
            return None

        return TagResponse.from_orm(tag)

    def list_tags(self) -> List[TagResponse]:
        """
        List all tags for the user.

        Returns:
            List of tags
        """
        tags = self.db.query(Tag).filter(
            Tag.user_id == self.user_id
        ).order_by(Tag.name).all()

        return [TagResponse.from_orm(tag) for tag in tags]

    def update_tag(self, tag_id: UUID, update_data: TagUpdate) -> Optional[TagResponse]:
        """
        Update a tag.

        Args:
            tag_id: Tag ID
            update_data: Fields to update

        Returns:
            Updated tag or None if not found

        Raises:
            Exception: If new name conflicts with existing tag
        """
        tag = self.db.query(Tag).filter(
            and_(
                Tag.id == tag_id,
                Tag.user_id == self.user_id
            )
        ).first()

        if not tag:
            return None

        # Check name conflict
        if update_data.name:
            existing = self.db.query(Tag).filter(
                and_(
                    Tag.user_id == self.user_id,
                    Tag.name == update_data.name,
                    Tag.id != tag_id
                )
            ).first()

            if existing:
                raise Exception(f"Tag '{update_data.name}' already exists")

            tag.name = update_data.name

        if update_data.color is not None:
            tag.color = update_data.color

        self.db.commit()

        return TagResponse.from_orm(tag)

    def delete_tag(self, tag_id: UUID) -> bool:
        """
        Delete a tag.

        Args:
            tag_id: Tag ID

        Returns:
            True if tag was deleted, False if not found
        """
        tag = self.db.query(Tag).filter(
            and_(
                Tag.id == tag_id,
                Tag.user_id == self.user_id
            )
        ).first()

        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()

        return True
