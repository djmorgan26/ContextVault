---
type: feature
name: Vault Item Management (CRUD + Encryption)
status: implemented
created: 2025-11-28
updated: 2025-11-28
files:
  - backend/app/schemas/vault.py:1-100
  - backend/app/services/vault.py:1-510
  - backend/app/api/vault.py:1-434
  - backend/app/models/vault.py (referenced)
related:
  - .ai/knowledge/components/encryption-service.md
  - .ai/knowledge/patterns/jwt-authentication.md
  - .ai/knowledge/patterns/async-database-operations.md
tags: [vault, encryption, crud, api, security]
---

# Vault Item Management

## What It Does

Provides complete CRUD (Create, Read, Update, Delete) operations for encrypted personal vault items. Users can create, organize, and manage encrypted notes, files, medical records, preferences, and measurements with full-text search and tag-based organization. All vault content is encrypted with AES-256-GCM using the user's master key derived from their Google ID.

## Architecture Overview

```
User Request (JWT Bearer Token)
    ↓
API Endpoint (vault.py)
    ↓
get_current_user() → Verify JWT, Retrieve User, Derive Master Key
    ↓
VaultService / TagService
    ↓
Encryption/Decryption (app/core/encryption.py)
    ↓
Database (SQLAlchemy async ORM)
```

## How It Works

### 1. Authentication Flow

**Location:** `backend/app/api/vault.py:34-78`

```python
async def get_current_user(
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> tuple[User, bytes]:
    # Extract Bearer token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")

    token = authorization.replace("Bearer ", "")

    # Verify JWT
    payload = verify_access_token(token)
    user_id = payload.get("user_id")

    # Retrieve user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # Derive master encryption key
    encryption_salt = bytes.fromhex(user.encryption_salt)
    master_key = derive_master_key(user.google_id, encryption_salt)

    return user, master_key
```

**Key points:**
- All endpoints require `Authorization: Bearer <JWT>`
- Master key is derived on-demand (never stored)
- Key derivation uses user's Google ID + encryption salt + PBKDF2 (100k iterations)
- Returns both User object and decryption key for service layer

### 2. Item Creation

**Location:** `backend/app/api/vault.py:86-114`

**Request:**
```json
{
  "type": "note",
  "title": "My Health Note",
  "content": "Detailed health information...",
  "tags": ["health", "important"],
  "metadata": {"condition": "diabetes"},
  "source": "manual",
  "source_id": null
}
```

**Service method:** `VaultService.create_item()` (line 102-142)

**Flow:**
1. Encrypt content with `encrypt_content(content, master_key)` → AES-256-GCM
2. Create VaultItem record with encrypted content
3. Auto-create or link tags (OR logic if multiple)
4. Return decrypted response

**Database state:**
```
VaultItem {
  id: UUID,
  user_id: UUID,
  type: "note",
  title: "My Health Note",
  content_encrypted: "VGhpcyBpcyBlbmNyeXB0ZWQgZGF0YQo=",  # Base64
  metadata: {...},
  source: "manual",
  deleted_at: null,
  created_at: 2025-11-28T13:00:00Z,
  updated_at: 2025-11-28T13:00:00Z
}

VaultItemTag {
  vault_item_id: UUID,
  tag_id: UUID  (auto-created if needed)
}
```

### 3. Item Retrieval & Decryption

**Location:** `backend/app/api/vault.py:117-148`

**Service method:** `VaultService.get_item()` (line 145-165)

**Flow:**
1. Query vault item by ID (only if user owns it via user_id FK)
2. Skip if soft-deleted (`deleted_at IS NOT NULL`)
3. Decrypt content with `decrypt_content(encrypted_content, master_key)` → AES-256-GCM
4. Return VaultItemResponse with decrypted plaintext

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "note",
  "title": "My Health Note",
  "content": "Detailed health information...",
  "metadata": {"condition": "diabetes"},
  "tags": ["health", "important"],
  "source": "manual",
  "source_id": null,
  "created_at": "2025-11-28T13:00:00Z",
  "updated_at": "2025-11-28T13:00:00Z"
}
```

### 4. List with Filtering & Pagination

**Location:** `backend/app/api/vault.py:151-204`

**Query parameters:**
- `page` (default 1, ≥1): Page number
- `page_size` (default 50, 1-200): Items per page
- `type` (optional): Filter by VaultItemType enum
- `source` (optional): Filter by source (manual, epic, fitbit, apple_health, import)
- `tags` (optional): List of tag names (OR logic - any match)
- `search` (optional): Substring search in title

**Service method:** `VaultService.list_items()` (line 168-230)

**Database queries:**
```sql
SELECT vi.* FROM vault_items vi
LEFT JOIN vault_item_tags vit ON vi.id = vit.vault_item_id
LEFT JOIN tags t ON vit.tag_id = t.id
WHERE vi.user_id = ?
  AND vi.deleted_at IS NULL
  AND (vi.type = ? OR ? IS NULL)
  AND (vi.source = ? OR ? IS NULL)
  AND (t.name IN (?, ?, ...) OR ? IS NULL)
  AND (vi.title ILIKE ? OR ? IS NULL)
ORDER BY vi.created_at DESC
LIMIT ? OFFSET ?
```

**Response:**
```json
{
  "items": [
    { "id": "...", "type": "note", ... },
    { "id": "...", "type": "file", ... }
  ],
  "total": 42,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

### 5. Item Update

**Location:** `backend/app/api/vault.py:207-240`

**Service method:** `VaultService.update_item()` (line 232-271)

**Supported fields:**
- `title`: Updated directly
- `content`: Re-encrypted with AES-256-GCM
- `type`: Updated directly
- `metadata`: Merged or replaced
- `tags`: Tags replaced (not merged)

**Flow:**
1. Retrieve vault item (401 if not owned, 404 if not found/deleted)
2. If content provided: decrypt old, validate, encrypt new
3. Update fields selectively
4. Re-link tags (delete old associations, create new)
5. Return updated decrypted item

### 6. Item Deletion (Soft)

**Location:** `backend/app/api/vault.py:243-272`

**Service method:** `VaultService.delete_item()` (line 273-287)

**Pattern:** Soft-delete with `deleted_at` timestamp

**Database update:**
```sql
UPDATE vault_items
SET deleted_at = NOW()
WHERE id = ? AND user_id = ?
```

**Rationale:**
- Preserves user data for recovery/audits
- Excludes from list/search queries (checked in WHERE clauses)
- Physical deletion possible in future data retention policies

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "deleted_at": "2025-11-28T13:05:00Z"
}
```

## Tag Management

### Create Tag

**Location:** `backend/app/api/vault.py:280-308`

**Service method:** `TagService.create_tag()` (line 29-45)

**Constraints:**
- Tag name must be unique per user (composite unique constraint)
- Returns 409 Conflict if tag already exists
- Optional color (hex format validation: `#RRGGBB`)

**Database:**
```sql
INSERT INTO tags (id, user_id, name, color)
VALUES (uuid_generate_v4(), ?, ?, ?)
ON CONFLICT (user_id, name) DO NOTHING
```

### List Tags

**Location:** `backend/app/api/vault.py:345-369`

**Service method:** `TagService.list_tags()` (line 70-80)

**Query:**
```sql
SELECT * FROM tags
WHERE user_id = ?
ORDER BY name ASC
```

### Update Tag

**Location:** `backend/app/api/vault.py:372-405`

**Service method:** `TagService.update_tag()` (line 82-105)

**Supported updates:**
- `name`: Enforces uniqueness (409 if conflict)
- `color`: Optional hex validation

### Delete Tag

**Location:** `backend/app/api/vault.py:408-434`

**Service method:** `TagService.delete_tag()` (line 107-120)

**Cascade:** Tag deletion removes all associations in `vault_item_tags` (CASCADE FK)

## Key Design Decisions

### Decision 1: Master Key Derivation On-Demand

**Why:** Never storing decryption keys on the server, even temporarily, reduces attack surface. Each request derives the key fresh from user's Google ID + stored salt.

**Trade-off:** Slight performance cost (PBKDF2 iteration) vs significant security benefit.

**Implementation:** `backend/app/core/encryption.py:derive_master_key()`

### Decision 2: Soft Deletes with deleted_at Timestamp

**Why:** Allows data recovery, supports auditing, complies with privacy regulations, enables future data retention policies.

**Trade-off:** Requires checking `deleted_at IS NULL` in all queries.

**Impact:** All list/get/update endpoints filter deleted items. Hard deletion possible via separate admin endpoint (not implemented).

### Decision 3: AES-256-GCM for Encryption

**Why:** Authenticated encryption (includes integrity check), NIST-approved, hardware acceleration available (AES-NI).

**Alternative considered:** ChaCha20-Poly1305 (would work but less hardware support).

**Implementation:** `backend/app/core/encryption.py:encrypt_content()` / `decrypt_content()`

### Decision 4: Tag Auto-Creation

**Why:** Better UX - users can specify any tag names, tags auto-created if they don't exist. No separate tag creation step required in common case.

**Implementation:** `VaultService._add_tags_to_item()` (line 289-310)

```python
def _add_tags_to_item(self, vault_item, tag_names):
    for tag_name in tag_names:
        # Find or create tag
        tag = self.db.query(Tag).filter(
            Tag.user_id == self.user_id,
            Tag.name == tag_name
        ).first()

        if not tag:
            tag = Tag(user_id=self.user_id, name=tag_name)
            self.db.add(tag)

        vault_item.tags.append(tag)
```

### Decision 5: Pagination Required (No "Get All")

**Why:** Prevents DoS attacks where user requests 1M items. Enforces `page_size` limits (1-200).

**Implementation:** `VaultService.list_items()` always calculates offset/limit

## Validation & Error Handling

### Request Validation (Pydantic)

**Schemas:** `backend/app/schemas/vault.py`

- `title`: 1-500 characters
- `content`: No length limit (stored encrypted)
- `tags`: Optional list of strings
- `color`: Hex format `#RRGGBB` (regex pattern)
- `page_size`: 1-200 range

### Response Handling

**Standard HTTP codes:**
- 201: Resource created successfully
- 200: GET/PATCH successful
- 204: DELETE successful (no content)
- 400: Invalid input (validation error)
- 401: Unauthorized (missing/invalid token)
- 404: Resource not found or user doesn't own it
- 409: Conflict (tag name already exists)
- 500: Server error (encryption failure, DB error)

**Error response:**
```json
{
  "detail": "Vault item not found"
}
```

## Database Models

### VaultItem

**Location:** `backend/app/models/vault.py`

```python
class VaultItem(Base):
    __tablename__ = "vault_items"

    id: UUID
    user_id: UUID (FK → users.id)
    type: VaultItemType (enum)
    title: String(500)
    content_encrypted: Text (AES-256-GCM encrypted)
    metadata: JSON (optional, unencrypted)
    source: VaultItemSource (enum)
    source_id: String(255, nullable)
    deleted_at: TIMESTAMP (nullable, soft-delete)
    created_at: TIMESTAMP (server default now())
    updated_at: TIMESTAMP (server default now(), on update)
```

**Indexes:**
- Primary: `id`
- Foreign: `user_id`
- Search: `idx_vault_items_user_id`, `idx_vault_items_deleted_at`
- Full-text: GIN index on title

### VaultItemTag (Junction Table)

```python
class VaultItemTag(Base):
    __tablename__ = "vault_item_tags"

    vault_item_id: UUID (FK → vault_items.id, CASCADE delete)
    tag_id: UUID (FK → tags.id, CASCADE delete)
```

### Tag

```python
class Tag(Base):
    __tablename__ = "tags"

    id: UUID
    user_id: UUID (FK → users.id)
    name: String(50, unique per user)
    color: String(7, nullable) (hex format)
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
```

**Constraints:**
- Unique: `(user_id, name)` - prevents duplicate tag names per user

## Security Considerations

### 1. Encryption at Rest

- Content encrypted with AES-256-GCM
- Master key derived from user's Google ID + salt
- Nonce is 12 bytes (random, unique per encryption)
- Authentication tag prevents tampering

### 2. Access Control

- All endpoints require valid JWT
- `get_current_user()` verifies token and user ownership
- Vault items implicitly filtered by `user_id` (cannot access other users' data)

### 3. Metadata Not Encrypted

- `metadata` field stored as JSON plaintext
- Use for non-sensitive structured data (condition types, custom fields)
- Never store secrets in metadata

### 4. Token Expiration

- JWT access tokens expire in 30 minutes (configured in auth.py)
- Clients must refresh using refresh token
- Expired tokens cause 401 Unauthorized

### 5. HTTPS Required (Production)

- All endpoints require HTTPS to prevent token interception
- Bearer token visible in Authorization header (needs TLS)

## Testing Strategy

### Manual Testing

**Create item:**
```bash
curl -X POST http://localhost:8000/api/vault/items \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "note",
    "title": "Test Note",
    "content": "Secret content",
    "tags": ["test"]
  }'
```

**List items:**
```bash
curl -X GET "http://localhost:8000/api/vault/items?page=1&page_size=10" \
  -H "Authorization: Bearer <JWT>"
```

**Update item:**
```bash
curl -X PATCH http://localhost:8000/api/vault/items/{item_id} \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### Automated Tests (Not Yet Implemented)

Should cover:
- [ ] Authorization: 401 without token, 401 with expired token
- [ ] CRUD operations: Create, read (single + list), update, delete
- [ ] Filtering: By type, source, tags, search
- [ ] Pagination: Offset/limit correctness, has_more flag
- [ ] Soft deletes: Deleted items excluded from lists
- [ ] Encryption: Content encrypted in DB, decrypted in response
- [ ] Tag management: Create, auto-create, update, delete
- [ ] Error cases: Missing fields, invalid types, ownership violations
- [ ] Concurrency: Concurrent updates don't lose data

## Common Issues & Solutions

### Issue 1: "Invalid or expired token" on every request

**Cause:** Token expiration (30 min default) or invalid signature

**Solution:**
- Refresh token: `POST /api/auth/refresh`
- Or login again: `GET /login`

### Issue 2: Content appears encrypted in response

**Cause:** Encryption failed, content not properly decrypted

**Solution:**
- Check master key derivation (salt matches user's encryption_salt)
- Verify JWT payload contains valid user_id
- Check logs for decrypt error

### Issue 3: "Tag already exists" when creating tags

**Cause:** Tag name not unique per user

**Solution:**
- Either use existing tag or use different name
- Query `GET /api/vault/tags` to see existing tags

### Issue 4: Pagination shows incomplete results

**Cause:** Deleted items excluded from count

**Solution:**
- `total` field reflects non-deleted items only
- Page 2 might have fewer items if some deleted
- This is by design (soft deletes)

## Related Architecture

### Encryption Service

**File:** `backend/app/core/encryption.py`

- `encrypt_content(content: str, master_key: bytes) → str` (returns base64)
- `decrypt_content(encrypted_content: str, master_key: bytes) → str`
- `derive_master_key(google_id: str, salt: bytes) → bytes`

### JWT Authentication

**File:** `backend/app/api/auth.py`

- `POST /api/auth/login` - Google OAuth callback
- `POST /api/auth/refresh` - Refresh token
- `verify_access_token(token: str) → dict` - Extract and validate JWT

### Database Session

**File:** `backend/app/core/database.py`

- `get_db()` - FastAPI dependency for async session
- `AsyncSession` lifecycle managed by FastAPI

## Future Enhancements

- [ ] **Batch operations**: Delete multiple items, bulk tag assignment
- [ ] **Export functionality**: Download vault as encrypted backup
- [ ] **Search indexing**: Full-text search on decrypted content (would require decryption at query time)
- [ ] **Audit logging**: Track all vault access/modifications per user
- [ ] **Sharing**: Share specific items with other users (encrypted share links)
- [ ] **Versioning**: Keep history of item changes with rollback capability
- [ ] **Offline sync**: Mobile app sync of vault items to local storage
- [ ] **Attachment support**: Store encrypted files alongside vault items
- [ ] **Read receipts**: Track when shared items were viewed

## Files Modified

- `backend/app/api/vault.py` - 434 lines (NEW)
- `backend/app/services/vault.py` - 510 lines (NEW)
- `backend/app/schemas/vault.py` - 100 lines (NEW)
- `backend/app/main.py` - Added vault router include
- `backend/app/models/integration.py` - Fixed reserved keyword (metadata → provider_metadata)
- `backend/app/services/__init__.py` - Added exports

