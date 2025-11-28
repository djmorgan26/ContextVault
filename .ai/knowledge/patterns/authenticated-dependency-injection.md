---
type: pattern
name: Authenticated Dependency Injection with Key Derivation
status: implemented
created: 2025-11-28
updated: 2025-11-28
files:
  - backend/app/api/vault.py:34-78
  - backend/app/core/security.py:23-45
  - backend/app/core/encryption.py:45-72
related:
  - .ai/knowledge/features/vault-item-management.md
tags: [fastapi, authentication, jwt, encryption, dependency-injection]
---

# Authenticated Dependency Injection Pattern

## What It Does

Provides a reusable FastAPI dependency that authenticates JWT bearer tokens, retrieves the user from the database, derives the user's encryption master key, and returns both for use in route handlers. This pattern ensures every protected endpoint receives a validated user context and encryption key in a single, consistent way.

## Pattern Overview

```
HTTP Request (Authorization: Bearer <JWT>)
    ↓
get_current_user() Dependency
    ↓
├─ Extract and validate JWT
├─ Retrieve User from database
├─ Derive master encryption key from User's salt
└─ Return (User, MasterKey)
    ↓
Route Handler receives (user, master_key)
    ↓
Service Layer processes request with encryption context
```

## Implementation

### Base Pattern (Minimal)

**Location:** `backend/app/api/vault.py:34-78`

```python
async def get_current_user(
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> tuple[User, bytes]:
    """
    Dependency: Get current user from JWT and derive encryption key.

    Returns:
        tuple: (User object, master encryption key bytes)

    Raises:
        HTTPException(401): If token missing, invalid, or user not found
    """
    # Step 1: Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )

    # Step 2: Extract token
    token = authorization.replace("Bearer ", "")

    # Step 3: Verify JWT signature and extract payload
    try:
        payload = verify_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Step 4: Retrieve user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Step 5: Derive master encryption key
    try:
        encryption_salt = bytes.fromhex(user.encryption_salt)
        master_key = derive_master_key(user.google_id, encryption_salt)
    except (ValueError, EncryptionError):
        raise HTTPException(status_code=500, detail="Failed to derive encryption key")

    return user, master_key
```

### Usage in Route Handler

```python
@router.post("/items", response_model=VaultItemResponse, status_code=201)
async def create_vault_item(
    item_data: VaultItemCreate,
    authorization: Optional[str] = None,  # ← Passed via header
    db: AsyncSession = Depends(get_db),    # ← FastAPI injects DB session
):
    """Create a vault item."""
    # Dependency injected automatically
    user, master_key = await get_current_user(authorization, db)

    # Use user and master_key in service
    service = VaultService(db, user.id, master_key)
    return service.create_item(item_data)
```

## Key Components

### 1. JWT Verification

**Function:** `verify_access_token(token: str) → dict`

**Location:** `backend/app/core/security.py:23-45`

**Does:**
- Validates JWT signature using app's secret key
- Extracts and returns token payload (claims)
- Raises exception if expired or signature invalid

**Example payload:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1700000000,
  "iat": 1699996400,
  "sub": "google_id_12345"
}
```

### 2. User Retrieval

**Query:** SQLAlchemy async select

```python
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

**Why async?** FastAPI's async routes shouldn't block on I/O. Async database operations preserve async/await chains.

**What it retrieves:**
- User record including `encryption_salt` (hex string)
- User's `google_id` (used in key derivation)

### 3. Key Derivation

**Function:** `derive_master_key(google_id: str, salt: bytes) → bytes`

**Location:** `backend/app/core/encryption.py:45-72`

**Algorithm:**
- PBKDF2-HMAC-SHA256
- 100,000 iterations
- Input: user's Google ID + salt
- Output: 32-byte (256-bit) encryption key

**Why on-demand?** Never storing keys on server reduces attack surface. Each request derives a fresh key.

**Time cost:** ~100ms on modern hardware (acceptable for crypto operation)

## Error Handling Strategy

### Layered Error Handling

```python
# Layer 1: Header validation
if not authorization or not authorization.startswith("Bearer "):
    raise HTTPException(401, "Missing or invalid authorization header")

# Layer 2: Token validation
try:
    payload = verify_access_token(token)
except Exception:
    raise HTTPException(401, "Invalid or expired token")

# Layer 3: User lookup
if not user:
    raise HTTPException(401, "User not found")

# Layer 4: Key derivation
try:
    master_key = derive_master_key(google_id, encryption_salt)
except (ValueError, EncryptionError):
    raise HTTPException(500, "Failed to derive encryption key")
```

### Why Not Return None?

This pattern raises HTTPException immediately rather than returning None. This:
- Fails fast with clear error to client
- Prevents passing invalid context to service layer
- Avoids defensive null-checks in route handlers

## Advanced Usage Variations

### Variation 1: Optional Authentication (Public Endpoints)

```python
async def get_current_user_optional(
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> tuple[Optional[User], Optional[bytes]]:
    """Like get_current_user but returns (None, None) if no token."""
    if not authorization:
        return None, None

    # ... rest of validation, return (None, None) on error instead of raising
    return user, master_key


@router.get("/public-endpoint")
async def public_endpoint(
    auth: tuple = Depends(get_current_user_optional)
):
    user, master_key = auth
    if user:
        # Authenticated request
        pass
    else:
        # Unauthenticated request
        pass
```

### Variation 2: Scoped Authentication (Role-Based)

```python
async def get_admin_user(
    auth: tuple[User, bytes] = Depends(get_current_user)
) -> tuple[User, bytes]:
    """Stricter dependency: user must be admin."""
    user, master_key = auth
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user, master_key


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin, master_key = Depends(get_admin_user)  # ← Enforces admin check
):
    # Only reachable if user is admin
    pass
```

### Variation 3: Dependency Composition

```python
async def get_vault_service(
    auth: tuple[User, bytes] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> VaultService:
    """Composite dependency: returns fully initialized service."""
    user, master_key = auth
    return VaultService(db, user.id, master_key)


@router.post("/items")
async def create_item(
    item_data: VaultItemCreate,
    service: VaultService = Depends(get_vault_service)  # ← Service pre-initialized
):
    return service.create_item(item_data)
```

This pattern is useful when multiple routes use the same service configuration.

## Testing This Pattern

### Unit Test: Mock Dependency

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test successful authentication."""
    mock_db = AsyncMock()
    mock_user = User(
        id="user-123",
        google_id="google-123",
        encryption_salt="deadbeef"
    )

    # Mock database query
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    # Mock JWT verification
    with patch('app.core.security.verify_access_token') as mock_verify:
        mock_verify.return_value = {"user_id": "user-123"}

        # Mock key derivation
        with patch('app.core.encryption.derive_master_key') as mock_derive:
            mock_key = b'32-byte-encryption-key-here-'
            mock_derive.return_value = mock_key

            user, key = await get_current_user("Bearer valid_token", mock_db)

            assert user.id == "user-123"
            assert key == mock_key


@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    """Test missing authorization header."""
    with pytest.raises(HTTPException) as exc:
        await get_current_user(None, AsyncMock())

    assert exc.value.status_code == 401
```

### Integration Test: Full Flow

```python
@pytest.mark.asyncio
async def test_vault_item_create_authenticated():
    """Test vault item creation with real auth flow."""
    # Start app with test database
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login to get token
        login_response = await client.get("/login", follow_redirects=False)
        token = extract_token_from_response(login_response)

        # Create vault item with token
        response = await client.post(
            "/api/vault/items",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "type": "note",
                "title": "Test",
                "content": "Secret"
            }
        )

        assert response.status_code == 201
        assert response.json()["title"] == "Test"
```

## Security Considerations

### 1. Token Validation

- **Never skip JWT verification** - always call `verify_access_token()`
- **Always check `user_id` in payload** - malformed tokens might have missing claims
- **Catch all exceptions** - validation library might raise different error types

### 2. User Lookup

- **Always fetch fresh from database** - token might be valid but user deleted
- **Check user exists** - handles race condition where user deleted between login and request

### 3. Key Derivation

- **Handle EncryptionError** - crypto library failures (rare but possible)
- **Always use stored salt** - never derive key with different salt (would decrypt to wrong data)

### 4. Header Extraction

- **Validate header format** - `"Bearer <token>"` not `"Bearer<token>"` or `"Token <token>"`
- **Case-sensitive "Bearer"** - don't accept "bearer" or "BEARER"

### 5. HTTP Codes

- **401 for auth failures** - invalid/expired token, user not found, missing header
- **403 for authorization failures** - valid auth but insufficient permissions (see Variation 2)
- **500 for system failures** - key derivation failure, database error (not client's fault)

## Performance Notes

### Cost Breakdown (Per Request)

| Operation | Time | Notes |
|-----------|------|-------|
| Header parsing | <1ms | String manipulation |
| JWT verification | 1-5ms | Signature validation |
| Database query | 5-50ms | Network round-trip to DB |
| Key derivation | 80-120ms | PBKDF2 with 100k iterations |
| **Total** | **~100-200ms** | Typical request |

### Optimization Opportunities

1. **Cache key derivation** per user per session (trades memory for speed)
2. **Pre-load user data** in JWT claims to skip DB query (trades payload size for speed)
3. **Reduce PBKDF2 iterations** (not recommended - security trade-off)

Current implementation prioritizes security over speed (acceptable for ~100ms cost per request).

## Related Patterns

- **Role-Based Access Control (RBAC)**: Extend with role checks
- **Token Refresh**: Combine with refresh token endpoint for long sessions
- **Multi-factor Authentication (MFA)**: Add second factor before key derivation
- **Audit Logging**: Log all auth attempts for security monitoring

