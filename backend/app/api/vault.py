"""
Vault API endpoints for creating, reading, updating, and deleting encrypted vault items.

All endpoints require authentication via JWT bearer token.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional, List

from app.core.database import get_db
from app.core.security import verify_access_token
from app.core.encryption import derive_master_key, EncryptionError
from app.models.user import User
from app.services.vault import VaultService, TagService
from app.schemas.vault import (
    VaultItemCreate,
    VaultItemUpdate,
    VaultItemResponse,
    VaultItemListResponse,
    VaultItemType,
    VaultItemSource,
    VaultItemDeleteResponse,
    TagCreate,
    TagUpdate,
    TagResponse,
)

router = APIRouter(prefix="/api/vault", tags=["vault"])


async def get_current_user(
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> tuple[User, bytes]:
    """
    Get current user from JWT token and return user + master encryption key.

    Args:
        authorization: Bearer token from Authorization header
        db: Database session

    Returns:
        tuple: (User object, master encryption key)

    Raises:
        HTTPException: 401 if token invalid or missing
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = verify_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Derive master key
    try:
        encryption_salt = bytes.fromhex(user.encryption_salt)
        master_key = derive_master_key(user.google_id, encryption_salt)
    except (ValueError, EncryptionError):
        raise HTTPException(status_code=500, detail="Failed to derive encryption key")

    return user, master_key


# ========================
# Vault Item Routes
# ========================


@router.post("/items", response_model=VaultItemResponse, status_code=201)
async def create_vault_item(
    item_data: VaultItemCreate,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new vault item with encrypted content.

    Args:
        item_data: Vault item data
        authorization: Bearer token
        db: Database session

    Returns:
        Created vault item (decrypted)

    Raises:
        HTTPException: 401 if unauthorized, 400 if invalid data
    """
    user, master_key = await get_current_user(authorization, db)

    try:
        service = VaultService(db, user.id, master_key)
        return service.create_item(item_data)
    except EncryptionError as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/items/{item_id}", response_model=VaultItemResponse)
async def get_vault_item(
    item_id: UUID,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve and decrypt a specific vault item.

    Args:
        item_id: Vault item ID
        authorization: Bearer token
        db: Database session

    Returns:
        Decrypted vault item

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found
    """
    user, master_key = await get_current_user(authorization, db)

    try:
        service = VaultService(db, user.id, master_key)
        item = service.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Vault item not found")
        return item
    except EncryptionError as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items", response_model=VaultItemListResponse)
async def list_vault_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    type: Optional[VaultItemType] = Query(None),
    source: Optional[VaultItemSource] = Query(None),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List user's vault items with filtering and pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page (1-200)
        type: Filter by item type
        source: Filter by source
        tags: Filter by tag names (comma-separated, OR logic)
        search: Search in title
        authorization: Bearer token
        db: Database session

    Returns:
        Paginated list of vault items

    Raises:
        HTTPException: 401 if unauthorized
    """
    user, master_key = await get_current_user(authorization, db)

    try:
        service = VaultService(db, user.id, master_key)
        result = service.list_items(
            page=page,
            page_size=page_size,
            item_type=type,
            source=source,
            tag_names=tags,
            search_title=search,
        )

        return VaultItemListResponse(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            has_more=result["has_more"],
        )
    except EncryptionError as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/items/{item_id}", response_model=VaultItemResponse)
async def update_vault_item(
    item_id: UUID,
    update_data: VaultItemUpdate,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a vault item.

    Args:
        item_id: Vault item ID
        update_data: Fields to update
        authorization: Bearer token
        db: Database session

    Returns:
        Updated vault item

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found
    """
    user, master_key = await get_current_user(authorization, db)

    try:
        service = VaultService(db, user.id, master_key)
        item = service.update_item(item_id, update_data)
        if not item:
            raise HTTPException(status_code=404, detail="Vault item not found")
        return item
    except EncryptionError as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{item_id}", response_model=VaultItemDeleteResponse)
async def delete_vault_item(
    item_id: UUID,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Soft-delete a vault item.

    Args:
        item_id: Vault item ID
        authorization: Bearer token
        db: Database session

    Returns:
        Deletion confirmation

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found
    """
    user, master_key = await get_current_user(authorization, db)

    try:
        service = VaultService(db, user.id, master_key)
        deleted_at = service.delete_item(item_id)
        if not deleted_at:
            raise HTTPException(status_code=404, detail="Vault item not found")
        return VaultItemDeleteResponse(id=str(item_id), deleted_at=deleted_at)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================
# Tag Routes
# ========================


@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(
    tag_data: TagCreate,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new tag.

    Args:
        tag_data: Tag data
        authorization: Bearer token
        db: Database session

    Returns:
        Created tag

    Raises:
        HTTPException: 401 if unauthorized, 409 if tag already exists
    """
    user, _ = await get_current_user(authorization, db)

    try:
        service = TagService(db, user.id)
        return service.create_tag(tag_data)
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific tag.

    Args:
        tag_id: Tag ID
        authorization: Bearer token
        db: Database session

    Returns:
        Tag details

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found
    """
    user, _ = await get_current_user(authorization, db)

    try:
        service = TagService(db, user.id)
        tag = service.get_tag(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all tags for the user.

    Args:
        authorization: Bearer token
        db: Database session

    Returns:
        List of tags

    Raises:
        HTTPException: 401 if unauthorized
    """
    user, _ = await get_current_user(authorization, db)

    try:
        service = TagService(db, user.id)
        return service.list_tags()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    update_data: TagUpdate,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a tag.

    Args:
        tag_id: Tag ID
        update_data: Fields to update
        authorization: Bearer token
        db: Database session

    Returns:
        Updated tag

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found, 409 if name conflict
    """
    user, _ = await get_current_user(authorization, db)

    try:
        service = TagService(db, user.id)
        tag = service.update_tag(tag_id, update_data)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: UUID,
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a tag.

    Args:
        tag_id: Tag ID
        authorization: Bearer token
        db: Database session

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found
    """
    user, _ = await get_current_user(authorization, db)

    try:
        service = TagService(db, user.id)
        if not service.delete_tag(tag_id):
            raise HTTPException(status_code=404, detail="Tag not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
