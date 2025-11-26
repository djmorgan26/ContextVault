# Context Vault - Database Schema

## Database Configuration

**Provider:** Railway Postgres
**Host:** `dpg-d4j00bvgi27c73eto9j0-a.ohio-postgres.render.com`
**Database:** `contextvaultdb`
**Port:** 5432
**SSL Mode:** require

## Entity Relationship Diagram

```
┌──────────────────┐
│     users        │
├──────────────────┤
│ id (PK)          │◄──┐
│ google_id        │   │
│ email            │   │
│ name             │   │
│ encryption_salt  │   │
│ preferences      │   │
│ created_at       │   │
│ updated_at       │   │
└──────────────────┘   │
                       │
                       │ 1:N
                       │
┌──────────────────┐   │
│   vault_items    │   │
├──────────────────┤   │
│ id (PK)          │   │
│ user_id (FK)     │───┘
│ type             │
│ title            │
│ content_enc      │◄───┐
│ metadata_enc     │    │ Encrypted with
│ file_path        │    │ user's master key
│ source           │    │
│ source_id        │────┘
│ created_at       │
│ updated_at       │
│ deleted_at       │
└──────────────────┘
        │ M:N
        │
        ├────────────────────┐
        │                    │
        ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│vault_item_tags   │  │      tags        │
├──────────────────┤  ├──────────────────┤
│ vault_item_id(FK)│  │ id (PK)          │
│ tag_id (FK)      │  │ user_id (FK)     │
│ created_at       │  │ name             │
└──────────────────┘  │ color            │
                      │ created_at       │
                      └──────────────────┘

┌──────────────────┐
│  integrations    │
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │───┐
│ provider         │   │
│ status           │   │
│ metadata         │   │
│ last_sync_at     │   │
│ created_at       │   │
│ updated_at       │   │
└──────────────────┘   │
        │              │
        │ 1:N          │
        ▼              │
┌──────────────────┐   │
│integration_tokens│   │
├──────────────────┤   │
│ id (PK)          │   │
│ integration_id   │───┘
│ token_type       │
│ access_token_enc │
│ refresh_token_enc│
│ expires_at       │
│ created_at       │
└──────────────────┘

┌──────────────────┐
│    sessions      │
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ refresh_token    │  ← Hashed
│ expires_at       │
│ user_agent       │
│ ip_address       │
│ created_at       │
└──────────────────┘
```

## Table Definitions

### users

Stores user identity and authentication information from Google OAuth.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    picture_url TEXT,
    encryption_salt VARCHAR(64) NOT NULL,  -- Random salt for key derivation
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);
```

**Fields:**
- `id`: Primary key, UUID v4
- `google_id`: Google's unique user identifier (from OAuth)
- `email`: User's email from Google
- `name`: Display name from Google profile
- `picture_url`: Profile picture URL from Google
- `encryption_salt`: Random 32-byte salt (hex encoded) for PBKDF2 key derivation
- `preferences`: JSON object for user settings (theme, default model, etc.)
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update

**Encryption:**
- `encryption_salt` is used to derive the user's master encryption key
- Master key = PBKDF2(google_id + APP_SECRET_KEY, salt, 100k iterations)

**Indexes:**
- `google_id` for OAuth lookups
- `email` for user search

### vault_items

Stores all user data: notes, files, medical records, preferences.

```sql
CREATE TYPE vault_item_type AS ENUM (
    'note',
    'file',
    'medical_record',
    'preference',
    'measurement',
    'other'
);

CREATE TYPE vault_item_source AS ENUM (
    'manual',
    'epic',
    'fitbit',
    'apple_health',
    'import'
);

CREATE TABLE vault_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type vault_item_type NOT NULL DEFAULT 'note',
    title VARCHAR(500),
    content_encrypted TEXT NOT NULL,  -- Base64 encoded: nonce||ciphertext||tag
    metadata_encrypted TEXT,          -- Encrypted JSON (file info, FHIR data, etc.)
    file_path TEXT,                   -- Path to encrypted file if type='file'
    source vault_item_source DEFAULT 'manual',
    source_id VARCHAR(255),           -- External ID (Epic FHIR resource ID, etc.)
    embedding VECTOR(384),            -- For semantic search (future, pgvector)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

CREATE INDEX idx_vault_items_user_id ON vault_items(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_vault_items_type ON vault_items(type) WHERE deleted_at IS NULL;
CREATE INDEX idx_vault_items_source ON vault_items(source) WHERE deleted_at IS NULL;
CREATE INDEX idx_vault_items_created_at ON vault_items(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_vault_items_source_id ON vault_items(source, source_id) WHERE deleted_at IS NULL;

-- Full-text search on title (decrypted titles stored, content stays encrypted)
CREATE INDEX idx_vault_items_title_fts ON vault_items USING gin(to_tsvector('english', title)) WHERE deleted_at IS NULL;
```

**Fields:**
- `id`: Primary key, UUID v4
- `user_id`: Owner of this vault item
- `type`: Category (note, file, medical_record, etc.)
- `title`: Plain text title (searchable, not sensitive)
- `content_encrypted`: AES-256-GCM encrypted content (Base64 encoded)
- `metadata_encrypted`: Encrypted JSON with extra data (file info, FHIR resource, etc.)
- `file_path`: Relative path to encrypted file (if type='file')
- `source`: Where this data came from
- `source_id`: External identifier (e.g., Epic FHIR Observation ID)
- `embedding`: Vector for semantic search (using pgvector extension, optional)
- `created_at`: When item was created
- `updated_at`: Last modification
- `deleted_at`: Soft delete timestamp (NULL = active)

**Encryption Format:**
```
content_encrypted = base64(nonce || ciphertext || auth_tag)
nonce: 12 bytes (random)
ciphertext: variable length
auth_tag: 16 bytes (GCM authentication tag)
```

**Indexes:**
- `user_id` for user's vault queries (with soft delete filter)
- `type` for filtering by category
- `source` for integration-specific queries
- `created_at` for chronological sorting
- `(source, source_id)` composite for deduplication during syncs
- Full-text search on `title` (GIN index)

**Soft Delete:**
- Never hard delete vault items (user data is precious)
- Set `deleted_at` timestamp instead
- Periodic cleanup job can purge after 90 days (configurable)

### tags

User-defined labels for organizing vault items.

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7),  -- Hex color code, e.g., #FF5733
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX idx_tags_user_id ON tags(user_id);
```

**Fields:**
- `id`: Primary key, UUID v4
- `user_id`: Tag owner
- `name`: Tag name (unique per user)
- `color`: Hex color for UI display
- `created_at`: Creation timestamp

**Constraints:**
- Unique(user_id, name): Users can't have duplicate tag names

### vault_item_tags

Many-to-many join table between vault_items and tags.

```sql
CREATE TABLE vault_item_tags (
    vault_item_id UUID NOT NULL REFERENCES vault_items(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (vault_item_id, tag_id)
);

CREATE INDEX idx_vault_item_tags_tag_id ON vault_item_tags(tag_id);
```

**Fields:**
- `vault_item_id`: Reference to vault item
- `tag_id`: Reference to tag
- `created_at`: When tag was applied

**Primary Key:**
- Composite: (vault_item_id, tag_id) prevents duplicate tag assignments

**Indexes:**
- `tag_id` for reverse lookup (all items with specific tag)

### integrations

Tracks connections to external services (Epic, Fitbit, Apple Health).

```sql
CREATE TYPE integration_provider AS ENUM (
    'epic',
    'fitbit',
    'apple_health'
);

CREATE TYPE integration_status AS ENUM (
    'connected',
    'disconnected',
    'error',
    'syncing'
);

CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider integration_provider NOT NULL,
    status integration_status DEFAULT 'connected',
    metadata JSONB DEFAULT '{}',  -- Provider-specific config (Epic tenant, Fitbit user ID, etc.)
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_sync_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, provider)
);

CREATE INDEX idx_integrations_user_id ON integrations(user_id);
CREATE INDEX idx_integrations_status ON integrations(status);
```

**Fields:**
- `id`: Primary key, UUID v4
- `user_id`: Integration owner
- `provider`: Service name (epic, fitbit, apple_health)
- `status`: Connection state
- `metadata`: JSON object with provider-specific data (Epic FHIR base URL, patient ID, etc.)
- `last_sync_at`: Timestamp of last successful data sync
- `last_sync_error`: Error message if sync failed
- `created_at`: When integration was connected
- `updated_at`: Last status change

**Constraints:**
- Unique(user_id, provider): User can only connect each provider once

**Metadata Examples:**
```json
// Epic
{
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "patient_id": "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB",
  "tenant": "open.epic.com"
}

// Fitbit
{
  "fitbit_user_id": "ABC123",
  "scopes": ["activity", "heartrate", "sleep"]
}

// Apple Health
{
  "last_import_date": "2025-01-15",
  "data_types": ["steps", "heart_rate", "sleep_analysis"]
}
```

### integration_tokens

Stores encrypted OAuth tokens for external services.

```sql
CREATE TYPE token_type AS ENUM (
    'access_token',
    'refresh_token',
    'id_token'
);

CREATE TABLE integration_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
    token_type token_type NOT NULL,
    token_encrypted TEXT NOT NULL,  -- Base64 encoded: nonce||ciphertext||tag
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_integration_tokens_integration_id ON integration_tokens(integration_id);
CREATE INDEX idx_integration_tokens_expires_at ON integration_tokens(expires_at);
```

**Fields:**
- `id`: Primary key, UUID v4
- `integration_id`: Reference to integration
- `token_type`: Type of OAuth token
- `token_encrypted`: AES-256-GCM encrypted token (same format as vault_items)
- `expires_at`: Token expiration (NULL for refresh tokens if they don't expire)
- `created_at`: When token was issued
- `updated_at`: When token was last refreshed

**Encryption:**
- Tokens encrypted with user's master key (same as vault items)
- Critical for security: compromised database doesn't expose API access

**Token Refresh Logic:**
- Background job checks `expires_at` every hour
- If access_token expires in <5 minutes, refresh it
- Update `token_encrypted` and `expires_at`

### sessions

Tracks user sessions for refresh token management.

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(128) NOT NULL,  -- SHA-256 hash
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_refresh_token_hash ON sessions(refresh_token_hash);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**Fields:**
- `id`: Primary key, UUID v4
- `user_id`: Session owner
- `refresh_token_hash`: SHA-256 hash of refresh token (not stored plain)
- `expires_at`: Session expiration (30 days default)
- `user_agent`: Browser/client info (for security auditing)
- `ip_address`: Client IP (for security auditing)
- `created_at`: Session start time

**Refresh Token Security:**
- Refresh tokens never stored in plain text
- Only SHA-256 hash stored in database
- On refresh: hash incoming token, look up session
- Prevents token theft from database breach

**Session Cleanup:**
- Periodic job deletes expired sessions (WHERE expires_at < NOW())

## Database Indexes Summary

| Table | Index | Purpose |
|-------|-------|---------|
| users | google_id | OAuth login lookup |
| users | email | User search |
| vault_items | user_id (WHERE deleted_at IS NULL) | User's vault queries |
| vault_items | type (WHERE deleted_at IS NULL) | Filter by category |
| vault_items | source (WHERE deleted_at IS NULL) | Integration queries |
| vault_items | created_at DESC (WHERE deleted_at IS NULL) | Chronological sort |
| vault_items | (source, source_id) (WHERE deleted_at IS NULL) | Deduplication |
| vault_items | title (GIN tsvector) | Full-text search |
| tags | user_id | User's tags |
| vault_item_tags | tag_id | Reverse tag lookup |
| integrations | user_id | User's integrations |
| integrations | status | Find errored integrations |
| integration_tokens | integration_id | Token lookup |
| integration_tokens | expires_at | Refresh token job |
| sessions | user_id | User's sessions |
| sessions | refresh_token_hash | Token validation |
| sessions | expires_at | Session cleanup |

## Encryption Strategy

### Master Key Derivation

```python
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_master_key(google_id: str, app_secret: str, salt: bytes) -> bytes:
    """
    Derive user's master encryption key from Google ID and app secret.

    Args:
        google_id: User's Google ID (from OAuth)
        app_secret: Application secret key (from env)
        salt: User's random salt (from users.encryption_salt)

    Returns:
        32-byte master key
    """
    password = (google_id + app_secret).encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashlib.sha256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password)
```

### Field Encryption (AES-256-GCM)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

def encrypt_field(plaintext: str, master_key: bytes) -> str:
    """
    Encrypt a field using AES-256-GCM.

    Args:
        plaintext: Data to encrypt
        master_key: 32-byte master key

    Returns:
        Base64-encoded string: nonce||ciphertext||tag
    """
    aesgcm = AESGCM(master_key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    plaintext_bytes = plaintext.encode('utf-8')

    # Encrypt and authenticate
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, associated_data=None)

    # Format: nonce (12 bytes) || ciphertext || auth_tag (16 bytes, included in ciphertext)
    encrypted = nonce + ciphertext

    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_field(encrypted_b64: str, master_key: bytes) -> str:
    """
    Decrypt a field using AES-256-GCM.

    Args:
        encrypted_b64: Base64-encoded encrypted data
        master_key: 32-byte master key

    Returns:
        Decrypted plaintext string

    Raises:
        InvalidTag: If authentication fails (tampering detected)
    """
    encrypted = base64.b64decode(encrypted_b64)
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]

    aesgcm = AESGCM(master_key)
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    return plaintext_bytes.decode('utf-8')
```

### Encrypted Fields

| Table | Field | Encryption |
|-------|-------|-----------|
| vault_items | content_encrypted | AES-256-GCM with user's master key |
| vault_items | metadata_encrypted | AES-256-GCM with user's master key |
| integration_tokens | token_encrypted | AES-256-GCM with user's master key |
| sessions | refresh_token_hash | SHA-256 hash (one-way) |

### Why Not Encrypt Everything?

**Encrypted:**
- Vault item content (sensitive user data)
- Vault item metadata (FHIR resources, file info)
- OAuth tokens (access to external services)

**Not Encrypted (Plain Text):**
- Vault item titles (needed for search)
- User email/name (needed for display)
- Tags (needed for filtering)
- Timestamps (needed for sorting)

**Rationale:**
- Full-database encryption would prevent searching, sorting, and filtering
- We encrypt the sensitive content, not the metadata needed for functionality
- PostgreSQL connection is encrypted (SSL) for transport security

## Migration Strategy

### Initial Schema (v1)

```bash
# Using Alembic for migrations
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Migration Script (`migrations/versions/001_initial_schema.py`):**
```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE vault_item_type AS ENUM ('note', 'file', 'medical_record', 'preference', 'measurement', 'other')")
    op.execute("CREATE TYPE vault_item_source AS ENUM ('manual', 'epic', 'fitbit', 'apple_health', 'import')")
    op.execute("CREATE TYPE integration_provider AS ENUM ('epic', 'fitbit', 'apple_health')")
    op.execute("CREATE TYPE integration_status AS ENUM ('connected', 'disconnected', 'error', 'syncing')")
    op.execute("CREATE TYPE token_type AS ENUM ('access_token', 'refresh_token', 'id_token')")

    # Create tables (see SQL above)
    # ...

def downgrade():
    # Drop tables and enums
    # ...
```

### Future Migrations

**Add Vector Search (v2):**
```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column
ALTER TABLE vault_items ADD COLUMN embedding VECTOR(384);

-- Create index for similarity search
CREATE INDEX idx_vault_items_embedding ON vault_items USING ivfflat (embedding vector_cosine_ops);
```

**Add Chat History (v3):**
```sql
CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content_encrypted TEXT NOT NULL,
    vault_item_refs UUID[],  -- Array of vault_item IDs used as context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Data Retention & Cleanup

### Soft Delete Policy

- Vault items: Soft delete (set `deleted_at`), purge after 90 days
- Users: Cascade delete all related data on account deletion
- Sessions: Hard delete expired sessions immediately
- Integration tokens: Hard delete when integration is disconnected

### Cleanup Jobs

**Daily:**
- Delete expired sessions (WHERE expires_at < NOW())
- Refresh expiring integration tokens

**Weekly:**
- Purge soft-deleted vault items (WHERE deleted_at < NOW() - INTERVAL '90 days')

**Monthly:**
- Vacuum database to reclaim space
- Reindex for performance

## Performance Optimization

### Query Patterns

**Most Common Queries:**

1. **Get user's vault items (paginated):**
```sql
SELECT id, type, title, source, created_at
FROM vault_items
WHERE user_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 50 OFFSET 0;
```
Covered by: `idx_vault_items_user_id`, `idx_vault_items_created_at`

2. **Search vault items by title:**
```sql
SELECT id, type, title, source, created_at
FROM vault_items
WHERE user_id = $1
  AND deleted_at IS NULL
  AND to_tsvector('english', title) @@ plainto_tsquery('english', $2)
ORDER BY created_at DESC;
```
Covered by: `idx_vault_items_title_fts`

3. **Get vault items by tags:**
```sql
SELECT vi.id, vi.type, vi.title, vi.created_at
FROM vault_items vi
JOIN vault_item_tags vit ON vi.id = vit.vault_item_id
JOIN tags t ON vit.tag_id = t.id
WHERE vi.user_id = $1
  AND t.name = ANY($2)  -- Array of tag names
  AND vi.deleted_at IS NULL
ORDER BY vi.created_at DESC;
```
Covered by: Multiple indexes, efficient join

4. **Get integration tokens:**
```sql
SELECT token_encrypted, expires_at
FROM integration_tokens it
JOIN integrations i ON it.integration_id = i.id
WHERE i.user_id = $1 AND i.provider = $2
  AND it.token_type = 'access_token';
```
Covered by: `idx_integrations_user_id`, `idx_integration_tokens_integration_id`

### Connection Pooling

```python
# SQLAlchemy config (app/core/database.py)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Max 10 connections in pool
    max_overflow=20,        # Allow 20 more connections if pool full
    pool_pre_ping=True,     # Verify connection before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False              # Don't log all SQL (use DEBUG mode)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Caching Strategy (Future)

**Redis cache for:**
- User's encryption salt (cache after first lookup)
- User's tags (invalidate on tag creation/deletion)
- Integration status (invalidate on status change)

**Cache keys:**
```
user:{user_id}:salt
user:{user_id}:tags
user:{user_id}:integrations
```

## Testing Data

### Seed Data for Development

```sql
-- Test user
INSERT INTO users (id, google_id, email, name, encryption_salt)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test-google-id-123',
    'test@example.com',
    'Test User',
    encode(gen_random_bytes(32), 'hex')
);

-- Test tags
INSERT INTO tags (user_id, name, color) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'medical', '#FF5733'),
('550e8400-e29b-41d4-a716-446655440000', 'personal', '#3498DB'),
('550e8400-e29b-41d4-a716-446655440000', 'work', '#2ECC71');

-- Test vault item (note: content must be encrypted in actual use)
INSERT INTO vault_items (user_id, type, title, content_encrypted, source)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'note',
    'My first note',
    'fake-encrypted-content-for-testing',
    'manual'
);
```

## Backup & Restore

### Automated Backups (Railway)

Railway provides automated daily backups with 7-day retention.

### Manual Backup

```bash
# Export full database
pg_dump -h dpg-d4j00bvgi27c73eto9j0-a.ohio-postgres.render.com \
        -U david \
        -d contextvaultdb \
        -F c \
        -f backup_$(date +%Y%m%d).dump

# Restore from backup
pg_restore -h dpg-d4j00bvgi27c73eto9j0-a.ohio-postgres.render.com \
           -U david \
           -d contextvaultdb \
           -c \
           backup_20250125.dump
```

### User Data Export (GDPR)

API endpoint: `GET /api/vault/export` returns JSON:

```json
{
  "user": {
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "vault_items": [
    {
      "id": "uuid",
      "type": "note",
      "title": "My note",
      "content": "Decrypted content here",
      "tags": ["personal", "important"],
      "created_at": "2025-01-20T14:22:00Z"
    }
  ],
  "integrations": [
    {
      "provider": "epic",
      "status": "connected",
      "last_sync": "2025-01-24T08:00:00Z"
    }
  ]
}
```

## Security Considerations

### SQL Injection Prevention

- All queries use parameterized statements (SQLAlchemy ORM)
- Never concatenate user input into SQL

### Encryption Key Management

- Master keys never stored in database
- Derived on-the-fly from user's Google ID + app secret
- App secret stored in environment variable (not in code)

### Token Security

- OAuth tokens encrypted at rest
- Refresh tokens hashed (SHA-256)
- Session tokens stored in HTTP-only cookies (frontend)

### Database Access Control

- Backend application: Full access (SELECT, INSERT, UPDATE, DELETE)
- No direct database access from frontend
- No admin users with decrypt capabilities (by design)

---

**Next Steps:**
1. Review API endpoints (see `api_endpoints.md`)
2. Set up database migrations (Alembic)
3. Implement encryption service (see `security_architecture.md`)
