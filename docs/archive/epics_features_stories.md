# ContextVault - Epics, Features & User Stories

> Product backlog organized by epic → feature → user story
> Priority: P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Low)

---

## Epic 1: Foundation & Infrastructure [P0]

**Goal:** Establish production-ready backend foundation with development tooling

**Timeline:** Days 1-3 (Week 1)

### Feature 1.1: Project Structure & Tooling

**User Story 1.1.1:** As a developer, I need a well-organized backend directory structure so that code is maintainable and follows best practices

- **Acceptance Criteria:**
  - Backend directory with app/, models/, schemas/, services/, api/, core/ structure
  - migrations/ directory for Alembic
  - tests/ directory with unit/ and integration/ subdirectories
  - All directories have proper `__init__.py` files
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Backend Structure)

**User Story 1.1.2:** As a developer, I need automated code formatting and linting so that code quality is consistent

- **Acceptance Criteria:**
  - `pyproject.toml` with Ruff configuration (100 char line length)
  - Pre-commit hooks configured to auto-format on commit
  - Makefile with `make format` and `make lint` commands
  - Ruff checks pass with no errors
- **Priority:** P0
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/deployment.md` (Section: Development Setup)

**User Story 1.1.3:** As a developer, I need a convenient way to run common tasks so that development is efficient

- **Acceptance Criteria:**
  - Makefile with commands: install, dev, test, lint, format, migrate
  - `make dev` starts uvicorn with hot reload
  - `make test` runs pytest with coverage report
  - `make install` sets up virtual environment and dependencies
- **Priority:** P0
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/deployment.md` (Section: Development Setup)

**User Story 1.1.4:** As a developer, I need all required dependencies installed so that I can build features

- **Acceptance Criteria:**
  - `requirements.txt` includes: fastapi, sqlalchemy, alembic, pydantic, cryptography, httpx, pytest
  - Dependencies install without conflicts
  - Versions pinned for reproducibility
- **Priority:** P0
- **Estimate:** 30 minutes
- **Status:** Not Started
- **Reference Docs:**
  - `docs/deployment.md` (Section: Dependencies)

### Feature 1.2: Configuration Management

**User Story 1.2.1:** As a developer, I need centralized configuration loading so that settings are consistent across the app

- **Acceptance Criteria:**
  - `app/core/config.py` with Pydantic Settings class
  - Loads from `.env` file automatically
  - Includes: DATABASE_URL, APP_SECRET_KEY, JWT_SECRET_KEY, OAuth credentials, Epic credentials, Ollama settings
  - Type validation on all settings
  - Provides helpful error messages if required vars missing
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Configuration Management)
  - `docs/deployment.md` (Section: Environment Variables)

### Feature 1.3: Database Setup

**User Story 1.3.1:** As a developer, I need async database connection pooling so that the app can handle concurrent requests efficiently

- **Acceptance Criteria:**
  - `app/core/database.py` with SQLAlchemy 2.0 async engine
  - Connection pool configured (pool_size=10, max_overflow=20)
  - `get_db()` FastAPI dependency for injecting database sessions
  - Proper session cleanup (close after request)
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Database Layer)

**User Story 1.3.2:** As a developer, I need database migration management so that schema changes are version controlled

- **Acceptance Criteria:**
  - Alembic initialized in `migrations/` directory
  - `alembic.ini` configured to use DATABASE_URL from settings
  - `make migrate` command runs pending migrations
  - Can generate new migrations with `alembic revision --autogenerate`
- **Priority:** P0
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Database Migrations)
  - `docs/deployment.md` (Section: Database Setup)

---

## Epic 2: Security & Encryption [P0]

**Goal:** Implement bulletproof encryption and security foundation

**Timeline:** Days 4-5 (Week 1)

### Feature 2.1: Encryption Service

**User Story 2.1.1:** As a user, I need my vault data encrypted with my own key so that even if the database is breached, my data is safe

- **Acceptance Criteria:**
  - `app/core/encryption.py` with `derive_master_key()` function
  - Uses PBKDF2-HMAC-SHA256 with 100,000 iterations
  - Derives key from: user's google_id + APP_SECRET_KEY + user's encryption_salt
  - Key derivation takes ~100ms (acceptable UX)
  - Master key is NEVER stored, always derived on-demand
- **Priority:** P0 - CRITICAL
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Encryption at Rest)

**User Story 2.1.2:** As a user, I need my vault content encrypted with industry-standard encryption so that it cannot be decrypted without my key

- **Acceptance Criteria:**
  - `encrypt_content()` function using AES-256-GCM
  - Generates unique 12-byte nonce for each encryption
  - Returns base64-encoded: nonce || ciphertext || auth_tag
  - Authentication tag prevents tampering
  - Encrypted output is different each time (due to unique nonce)
- **Priority:** P0 - CRITICAL
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Encryption at Rest)

**User Story 2.1.3:** As a user, I need tamper detection on my encrypted data so that any modification is detected

- **Acceptance Criteria:**
  - `decrypt_content()` function verifies auth tag before decrypting
  - Raises `EncryptionError` if auth tag verification fails
  - Raises `EncryptionError` if decryption fails with wrong key
  - Returns plaintext only if all checks pass
- **Priority:** P0 - CRITICAL
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Encryption at Rest)

**User Story 2.1.4:** As a developer, I need 100% test coverage on encryption so that I'm confident in the security implementation

- **Acceptance Criteria:**
  - Test: encrypt → decrypt returns original plaintext
  - Test: decryption with wrong key raises error
  - Test: key derivation is deterministic (same inputs = same key)
  - Test: different users get different keys (different salts)
  - Test: nonces are unique across multiple encryptions
  - Test: tampering with ciphertext fails decryption
  - 100% code coverage on encryption module
- **Priority:** P0 - CRITICAL
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Encryption at Rest)

### Feature 2.2: JWT Authentication

**User Story 2.2.1:** As a user, I need secure access tokens so that my API requests are authenticated

- **Acceptance Criteria:**
  - `app/core/security.py` with `create_access_token()` function
  - Uses HS256 algorithm with JWT_SECRET_KEY
  - Includes claims: user_id, exp (30 min expiry), iat
  - Returns signed JWT string
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: JWT Authentication)

**User Story 2.2.2:** As a developer, I need token validation as a FastAPI dependency so that routes can require authentication

- **Acceptance Criteria:**
  - `verify_access_token()` function decodes and validates JWT
  - Checks signature, expiration, required claims
  - `get_current_user()` FastAPI dependency that returns User model
  - Raises HTTPException 401 if token invalid/expired
  - Can be used with `Depends(get_current_user)` on routes
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: JWT Authentication)

**User Story 2.2.3:** As a user, I need refresh tokens so that I don't have to log in every 30 minutes

- **Acceptance Criteria:**
  - Refresh tokens stored in sessions table as SHA-256 hash
  - Never store refresh tokens in plaintext
  - Refresh tokens expire after 30 days
  - `hash_refresh_token()` function for secure storage
- **Priority:** P0
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Session Management)

---

## Epic 3: Database Schema [P0]

**Goal:** Create complete database schema matching documentation

**Timeline:** Days 5-6 (Week 1)

### Feature 3.1: Database Models

**User Story 3.1.1:** As a developer, I need SQLAlchemy models for all entities so that I can interact with the database

- **Acceptance Criteria:**
  - `app/models/user.py`: User model with google_id, email, encryption_salt (32 bytes)
  - `app/models/vault_item.py`: VaultItem with content_encrypted, metadata_encrypted, soft delete
  - `app/models/tag.py`: Tag model with name, color, user relationship
  - `app/models/integration.py`: Integration and IntegrationToken models
  - `app/models/session.py`: Session model with refresh_token_hash
  - All models have proper relationships (ForeignKey, back_populates)
  - All models have created_at, updated_at timestamps
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/database_schema.md` (Section: Complete Schema)

**User Story 3.1.2:** As a developer, I need Pydantic schemas for API validation so that requests are validated

- **Acceptance Criteria:**
  - `app/schemas/vault.py`: VaultItemCreate, VaultItemUpdate, VaultItemResponse
  - `app/schemas/auth.py`: UserResponse, TokenResponse
  - `app/schemas/integration.py`: IntegrationStatus, EpicConnectionResponse
  - All schemas have proper field validation (max lengths, required fields)
  - Response schemas exclude sensitive fields (encrypted content in list views)
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/database_schema.md` (Section: Complete Schema)

### Feature 3.2: Initial Migration

**User Story 3.2.1:** As a developer, I need the initial database migration so that the schema is created in Railway Postgres

- **Acceptance Criteria:**
  - `migrations/versions/001_initial_schema.py` creates all 7 tables
  - Creates 5 enum types: vault_item_type, vault_item_source, integration_provider, integration_status, token_type
  - Creates all foreign key constraints
  - Creates indexes: idx_vault_items_user_id, idx_vault_items_created_at, idx_vault_items_title_fts, idx_sessions_refresh_token_hash
  - Migration runs successfully against Railway Postgres
  - `make migrate` applies migration
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/database_schema.md` (Section: Complete Schema)

---

## Epic 4: Authentication System [P0]

**Goal:** Implement Google OAuth login and session management

**Timeline:** Days 7-8 (Week 2)

### Feature 4.1: Google OAuth Flow

**User Story 4.1.1:** As a user, I want to log in with my Google account so that I don't need to create a new password

- **Acceptance Criteria:**
  - POST `/api/auth/google/login` endpoint returns Google OAuth URL
  - URL includes state parameter for CSRF protection
  - URL includes correct redirect_uri, client_id, scopes
  - State stored temporarily (Redis or in-memory with 5min TTL)
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: OAuth 2.0 Flows)
  - `docs/api_endpoints.md` (Section: Authentication Endpoints)

**User Story 4.1.2:** As a user, when I approve Google OAuth, I want to be redirected back with a session so that I'm logged in

- **Acceptance Criteria:**
  - GET `/api/auth/google/callback` endpoint handles OAuth return
  - Validates state parameter (CSRF protection)
  - Exchanges authorization code for access_token + id_token
  - Verifies id_token signature using Google's JWKS
  - Extracts google_id and email from id_token claims
  - Creates new user if google_id doesn't exist (generates random 32-byte encryption_salt)
  - Creates session with refresh_token (stored as SHA-256 hash)
  - Returns access_token + refresh_token in response
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: OAuth 2.0 Flows)
  - `docs/api_endpoints.md` (Section: Authentication Endpoints)

**User Story 4.1.3:** As a user, I want to refresh my access token so that I stay logged in without re-authenticating

- **Acceptance Criteria:**
  - POST `/api/auth/refresh` endpoint accepts refresh_token in body
  - Validates refresh_token by checking SHA-256 hash in sessions table
  - Checks session expiration (30 days)
  - Issues new access_token (30 min expiry)
  - Optionally rotates refresh_token for security
  - Returns new access_token
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Session Management)
  - `docs/api_endpoints.md` (Section: Authentication Endpoints)

**User Story 4.1.4:** As a user, I want to log out so that my session is invalidated

- **Acceptance Criteria:**
  - POST `/api/auth/logout` endpoint requires authentication
  - Deletes session from database
  - Returns 200 OK
  - Subsequent requests with old access_token fail after expiry
- **Priority:** P1
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Authentication Endpoints)

**User Story 4.1.5:** As a user, I want to view my profile so that I can see my account information

- **Acceptance Criteria:**
  - GET `/api/auth/me` endpoint requires authentication
  - Returns user profile: email, google_id, created_at, preferences
  - Does NOT return encryption_salt (security)
- **Priority:** P1
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Authentication Endpoints)

### Feature 4.2: Authentication Service Layer

**User Story 4.2.1:** As a developer, I need authentication business logic separated from API routes so that code is testable

- **Acceptance Criteria:**
  - `app/services/auth_service.py` with AuthService class
  - Methods: initiate_google_oauth(), handle_google_callback(), refresh_access_token()
  - Service handles all OAuth logic, token exchange, user creation
  - API routes are thin wrappers around service methods
  - Service methods are unit testable
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Service Layer)
  - `docs/security_architecture.md` (Section: OAuth 2.0 Flows)

---

## Epic 5: Vault Management [P0]

**Goal:** Core vault CRUD operations with encryption

**Timeline:** Days 9-11 (Week 2)

### Feature 5.1: Vault Item CRUD

**User Story 5.1.1:** As a user, I want to create a vault item so that I can securely store my notes and data

- **Acceptance Criteria:**
  - POST `/api/vault/items` endpoint requires authentication
  - Request body: title, content, metadata (optional), tags (optional), type
  - Content and metadata are encrypted before database storage
  - Returns created vault item with decrypted content
  - Associates tags (creates new tags if they don't exist)
  - Sets source=manual, user_id=current_user
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints)
  - `docs/architecture.md` (Section: Vault Service)

**User Story 5.1.2:** As a user, I want to view a specific vault item so that I can read my stored data

- **Acceptance Criteria:**
  - GET `/api/vault/items/{item_id}` endpoint requires authentication
  - Verifies item belongs to current user (403 if not)
  - Decrypts content and metadata before returning
  - Returns full vault item with decrypted content, tags, metadata
  - Returns 404 if item doesn't exist or is soft-deleted
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints)
  - `docs/architecture.md` (Section: Vault Service)

**User Story 5.1.3:** As a user, I want to list my vault items so that I can browse my data

- **Acceptance Criteria:**
  - GET `/api/vault/items` endpoint requires authentication
  - Supports pagination: page, limit (default 50)
  - Supports filters: type, tags[], search (full-text on title)
  - Returns items WITHOUT decrypted content (performance)
  - Returns total count, page info
  - Excludes soft-deleted items
  - Orders by created_at DESC
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints)
  - `docs/architecture.md` (Section: Vault Service)

**User Story 5.1.4:** As a user, I want to update a vault item so that I can modify my stored data

- **Acceptance Criteria:**
  - PUT `/api/vault/items/{item_id}` endpoint requires authentication
  - Verifies ownership (403 if not owner)
  - Accepts partial updates: title, content, metadata, tags
  - Re-encrypts content/metadata if changed
  - Updates updated_at timestamp
  - Returns updated item with decrypted content
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints)
  - `docs/architecture.md` (Section: Vault Service)

**User Story 5.1.5:** As a user, I want to delete a vault item so that I can remove unwanted data

- **Acceptance Criteria:**
  - DELETE `/api/vault/items/{item_id}` endpoint requires authentication
  - Verifies ownership
  - Soft delete: sets deleted_at timestamp (not hard delete)
  - Item no longer appears in list queries
  - Can be restored by clearing deleted_at (future feature)
  - Returns 204 No Content
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints)
  - `docs/architecture.md` (Section: Vault Service)

### Feature 5.2: Vault Service Layer

**User Story 5.2.1:** As a developer, I need vault business logic separated so that encryption is handled consistently

- **Acceptance Criteria:**
  - `app/services/vault_service.py` with VaultService class
  - Methods: create_item(), get_item(), list_items(), update_item(), delete_item()
  - Service handles all encryption/decryption transparently
  - Derives master key from current user on each request
  - API routes delegate to service
  - Service is unit testable (mock encryption)
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Service Layer - Vault Service)

### Feature 5.3: Tag Management

**User Story 5.3.1:** As a user, I want to create tags so that I can organize my vault items

- **Acceptance Criteria:**
  - POST `/api/vault/tags` endpoint requires authentication
  - Request body: name, color (hex code, optional)
  - Enforces uniqueness: user cannot create duplicate tag names
  - Returns created tag
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints - Tags)

**User Story 5.3.2:** As a user, I want to list my tags so that I can see available organization options

- **Acceptance Criteria:**
  - GET `/api/vault/tags` endpoint requires authentication
  - Returns all tags for current user
  - Includes count of vault items per tag
  - Orders by name alphabetically
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints - Tags)

**User Story 5.3.3:** As a user, I want to rename or delete tags so that I can reorganize my vault

- **Acceptance Criteria:**
  - PUT `/api/vault/tags/{tag_id}` allows renaming tag
  - Updates all vault items with this tag automatically
  - DELETE `/api/vault/tags/{tag_id}` removes tag
  - Warns if tag has vault items (confirmation required)
  - Deleting tag removes from all associated vault items
- **Priority:** P2
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints - Tags)

**User Story 5.3.4:** As a user, I want to filter vault items by tags so that I can find related content

- **Acceptance Criteria:**
  - GET `/api/vault/items?tags[]=work&tags[]=medical` supports multiple tags
  - Returns items that have ALL specified tags (AND logic)
  - Works with pagination and other filters
- **Priority:** P1
- **Estimate:** 2 hours (part of list_items)
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints - Tags)

### Feature 5.4: File Upload

**User Story 5.4.1:** As a user, I want to upload PDF files so that I can store documents in my vault

- **Acceptance Criteria:**
  - POST `/api/vault/upload` endpoint requires authentication
  - Accepts multipart/form-data with file
  - Validates file type (PDF only for MVP)
  - Max file size: 10MB
  - Extracts text from PDF using PyPDF2
  - Encrypts file content before storage
  - Stores encrypted file at `/data/uploads/{user_id}/{file_id}.enc`
  - Creates vault item with type=file, content=extracted text
  - Returns created vault item
- **Priority:** P1
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Vault Endpoints - File Upload)
  - `docs/architecture.md` (Section: File Upload and Parsing)

---

## Epic 6: Epic MyChart Integration [P0]

**Goal:** Sync medical records from Epic MyChart

**Timeline:** Days 12-14 (Week 2-3)

### Feature 6.1: Epic OAuth Connection

**User Story 6.1.1:** As a user, I want to connect my Epic MyChart account so that I can import my medical records

- **Acceptance Criteria:**
  - POST `/api/integrations/epic/connect` endpoint requires authentication
  - Generates PKCE code_verifier and code_challenge
  - Stores state + code_verifier temporarily (5min TTL)
  - Returns Epic authorization URL with:
    - response_type=code, client_id, redirect_uri
    - scope: openid profile patient/Patient.read patient/Observation.read offline_access
    - state, code_challenge, code_challenge_method=S256
    - aud=EPIC_FHIR_BASE
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Complete
- **Reference Docs:**
  - `docs/architecture.md` (Section: FHIR Integration)
  - `docs/api_endpoints.md` (Section: Integration Endpoints - Epic)

**User Story 6.1.2:** As a user, when I approve Epic OAuth, I want my tokens stored securely so that the app can sync my data

- **Acceptance Criteria:**
  - GET `/api/integrations/epic/callback` handles Epic redirect
  - Validates state parameter
  - Exchanges authorization code for tokens using code_verifier (PKCE)
  - Receives: access_token, refresh_token, id_token
  - Validates id_token signature using Epic's JWKS
  - Encrypts access_token and refresh_token before database storage
  - Creates/updates integration record (provider=epic, status=connected)
  - Stores encrypted tokens in integration_tokens table
  - Queues background sync job
  - Returns integration status
  - Error if Epic returns invalid tokens (set status=error)
  - Retry logic on network failures (3 attempts with exponential backoff)
  - Store integration status=error if callback fails
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** In Progress
- **Reference Docs:**
  - `docs/architecture.md` (Section: FHIR Integration)
  - `docs/api_endpoints.md` (Section: Integration Endpoints - Epic)

**User Story 6.1.3:** As a user, I want to disconnect Epic so that my tokens are removed

- **Acceptance Criteria:**
  - DELETE `/api/integrations/epic` endpoint requires authentication
  - Deletes integration_tokens records
  - Deletes integration record (or sets status=disconnected)
  - Does NOT delete vault items previously synced from Epic
  - Returns 204 No Content
- **Priority:** P1
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Integration Endpoints - Epic)

### Feature 6.2: FHIR Data Sync

**User Story 6.2.1:** As a user, I want my Epic medical records automatically synced to my vault so that I can access them privately

- **Acceptance Criteria:**
  - Background job triggered after Epic connection
  - Fetches FHIR Patient resource
  - Fetches FHIR Observation resources (patient/{id}/Observation?\_count=1000)
  - Transforms each FHIR resource to vault item:
    - Extract human-readable summary for content
    - Store full FHIR JSON in metadata_encrypted
    - Set type=medical_record, source=epic, source_id=resource.id
  - Checks for duplicates using source_id (skip if exists)
  - Creates vault items with encryption
  - Updates integration.last_sync_at timestamp
  - Handles pagination if > 1000 observations
- **Priority:** P0
- **Estimate:** 8 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: FHIR Integration)
  - `docs/api_endpoints.md` (Section: Integration Endpoints - Epic)

**User Story 6.2.2:** As a user, I want to manually trigger Epic sync so that I can get the latest data on demand

- **Acceptance Criteria:**
  - POST `/api/integrations/epic/sync` endpoint requires authentication
  - Verifies Epic integration is connected
  - Queues background sync job
  - Returns job_id for status tracking
  - Returns 400 if Epic not connected
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Integration Endpoints - Epic)

**User Story 6.2.3:** As a user, I want to see my Epic sync status so that I know when my data is updated

- **Acceptance Criteria:**
  - GET `/api/integrations/epic/status` endpoint requires authentication
  - Returns: status (connected/disconnected/syncing), last_sync_at, current_job_status
  - If syncing: returns progress (items_processed, estimated_remaining)
  - Returns 404 if Epic not connected
- **Priority:** P1
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/api_endpoints.md` (Section: Integration Endpoints - Epic)

### Feature 6.3: FHIR Transformations

**User Story 6.3.1:** As a developer, I need FHIR Observation resources transformed to readable vault items so that users can understand their medical data

- **Acceptance Criteria:**
  - Blood Pressure → "Blood Pressure: 120/80 mmHg on 2025-01-20"
  - Lab results → "Glucose: 95 mg/dL (Normal) on 2025-01-15"
  - Vital signs → "Heart Rate: 72 bpm on 2025-01-20"
  - Full FHIR JSON stored in metadata for reference
  - Extracts: observation code, value, unit, effective date, reference ranges
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: FHIR Integration - Transformations)

**User Story 6.3.2:** As a developer, I need Patient resources transformed so that demographic data is stored

- **Acceptance Criteria:**
  - Creates vault item: "Patient Demographics"
  - Content: "Name: John Doe, DOB: 1990-05-15, Gender: Male, MRN: 12345"
  - Metadata includes: full FHIR Patient JSON, primary care provider
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: FHIR Integration - Transformations)

### Feature 6.4: Token Refresh

**User Story 6.4.1:** As a user, I want my Epic tokens automatically refreshed so that sync doesn't break

- **Acceptance Criteria:**
  - Before making FHIR API calls, check access_token expiry
  - If expired, use refresh_token to get new access_token
  - POST to Epic token endpoint with grant_type=refresh_token
  - Decrypt old refresh_token, send to Epic
  - Receive new access_token (and possibly new refresh_token)
  - Encrypt and update tokens in database
  - Retry original FHIR request with new token
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: FHIR Integration - Token Refresh)

### Feature 6.5: Epic Service Layer

**User Story 6.5.1:** As a developer, I need Epic integration logic separated so that it's testable and maintainable

- **Acceptance Criteria:**
  - `app/services/epic_service.py` with EpicService class
  - Methods: initiate_oauth(), handle_callback(), sync_patient_data(), refresh_epic_token()
  - Service handles FHIR transformations
  - Service handles token encryption/decryption
  - API routes delegate to service
  - Service is unit testable with mocked FHIR responses
- **Priority:** P0
- **Estimate:** 8 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: Service Layer - Epic Service)
  - `docs/architecture.md` (Section: FHIR Integration)

---

## Epic 7: AI Chat Integration [P0]

**Goal:** Chat with AI using vault context

**Timeline:** Days 15-16 (Week 3)

### Feature 7.1: Chat API

**User Story 7.1.1:** As a user, I want to chat with an AI that understands my vault data so that I can ask questions about my information

- **Acceptance Criteria:**
  - POST `/api/chat` endpoint requires authentication
  - Request body: message, tags (optional filter)
  - Retrieves relevant vault items as context (max 5 items)
  - Sends context event with vault_item IDs
  - Builds prompt: system instructions + vault context + user message
  - Streams response from Ollama using Server-Sent Events (SSE)
  - Sends message events with chunks as they arrive
  - Sends done event when complete
  - Returns streaming response (text/event-stream)
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Ephemeral LLM Containers)
  - `docs/architecture.md` (Section: LLM Integration)

**User Story 7.1.2:** As a user, I want relevant vault items automatically included in chat context so that the AI has accurate information

- **Acceptance Criteria:**
  - Context retrieval searches vault items by keyword matching
  - Searches in item titles (full-text search)
  - Filters by tags if specified in request
  - Limits to top 5 most recent matching items
  - Decrypts content before sending to LLM
  - LLM must NOT receive metadata_encrypted (privacy protection)
  - Context item previews truncated (e.g., 200 chars per item for performance)
  - Future: Vector embeddings for semantic search
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: LLM Integration - Context Retrieval)

### Feature 7.2: Ollama Integration

**User Story 7.2.1:** As a developer, I need Ollama client for streaming responses so that chat is interactive

- **Acceptance Criteria:**
  - `app/services/ollama_service.py` with OllamaService class
  - `generate_stream()` method streams from `POST {OLLAMA_HOST}/api/generate`
  - Uses httpx async streaming
  - Yields response chunks as they arrive
  - Handles timeouts gracefully (60 sec timeout)
  - Model configurable (default: llama3.1:8b)
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: LLM Integration - Ollama)

**User Story 7.2.2:** As a user, I want the AI to use my vault data responsibly so that my privacy is maintained

- **Acceptance Criteria:**
  - System prompt instructs AI: "You are a helpful assistant with access to the user's personal vault. Do not share or repeat sensitive information unless directly asked."
  - Vault context clearly labeled in prompt
  - User message separated from context
  - LLM sees decrypted content in memory only (ephemeral)
  - No conversation history stored (future: optional encrypted history)
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/security_architecture.md` (Section: Ephemeral LLM Containers)

### Feature 7.3: Context Retrieval Service

**User Story 7.3.1:** As a developer, I need context retrieval logic separated so that it can be improved over time

- **Acceptance Criteria:**
  - `app/services/context_service.py` with ContextService class
  - `retrieve_context()` method returns relevant vault items
  - `build_prompt()` method formats context + user message for LLM
  - MVP: Simple keyword + tag matching
  - Future-ready: Can swap to vector embeddings (pgvector)
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/architecture.md` (Section: LLM Integration - Context Retrieval)

---

## Epic 8: Testing & Quality Assurance [P0]

**Goal:** Comprehensive test coverage and CI/CD pipeline

**Timeline:** Days 17-18 (Week 3)

### Feature 8.1: Unit Tests

**User Story 8.1.1:** As a developer, I need 100% test coverage on encryption so that I'm confident in security

- **Acceptance Criteria:**
  - `tests/unit/test_encryption.py` with 10+ tests
  - Tests: round-trip, wrong key fails, deterministic key derivation, unique nonces, tamper detection
  - 100% code coverage on encryption module
  - All tests pass
- **Priority:** P0 - CRITICAL
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Unit Testing)

**User Story 8.1.2:** As a developer, I need comprehensive tests on JWT authentication so that auth is reliable

- **Acceptance Criteria:**
  - `tests/unit/test_security.py` with tests for JWT creation, validation, expiry, refresh token hashing
  - 100% code coverage on security module
  - All tests pass
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Unit Testing)

### Feature 8.2: Integration Tests

**User Story 8.2.1:** As a developer, I need integration tests for vault API so that end-to-end flows work correctly

- **Acceptance Criteria:**
  - `tests/integration/test_vault_api.py` tests all vault endpoints
  - Tests: create → retrieve (content decrypted), cannot access other users' items, soft delete, tag filtering, pagination
  - Uses test database (separate from dev/prod)
  - 80%+ coverage on vault routes
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Integration Testing)

**User Story 8.2.2:** As a developer, I need integration tests for Epic API so that OAuth and sync work

- **Acceptance Criteria:**
  - `tests/integration/test_epic_api.py` tests Epic endpoints
  - Tests: OAuth redirect, callback creates integration, tokens encrypted in DB, sync creates vault items
  - Mocks Epic FHIR API responses
  - 70%+ coverage on Epic routes
- **Priority:** P1
- **Estimate:** 6 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Integration Testing)

### Feature 8.3: Test Infrastructure

**User Story 8.3.1:** As a developer, I need test fixtures and utilities so that writing tests is easy

- **Acceptance Criteria:**
  - `tests/conftest.py` with fixtures: db_session, test_user, auth_headers, test_vault_item
  - Test database automatically created and torn down
  - Migrations run before tests
  - Factory functions for creating test data
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Test Infrastructure)

**User Story 8.3.2:** As a developer, I need pytest configuration so that tests run consistently

- **Acceptance Criteria:**
  - `pytest.ini` with asyncio_mode=auto, testpaths, coverage config
  - `make test` runs all tests with coverage report
  - HTML coverage report generated
  - Overall target: 75%+ coverage
- **Priority:** P0
- **Estimate:** 1 hour
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Test Infrastructure)

### Feature 8.4: CI/CD Pipeline

**User Story 8.4.1:** As a developer, I need automated linting on every push so that code quality is enforced

- **Acceptance Criteria:**
  - `.github/workflows/backend-ci.yml` with lint job
  - Runs `ruff check` and `ruff format --check`
  - Fails pipeline if linting errors
  - Runs on push to main/develop and all PRs
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: CI/CD Pipeline)

**User Story 8.4.2:** As a developer, I need automated tests on every push so that bugs are caught early

- **Acceptance Criteria:**
  - CI workflow has test job with Postgres service
  - Runs all pytest tests with coverage
  - Uploads coverage report to Codecov (optional)
  - Fails pipeline if tests fail or coverage < 70%
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: CI/CD Pipeline)

**User Story 8.4.3:** As a developer, I need security scanning so that vulnerabilities are detected

- **Acceptance Criteria:**
  - CI workflow includes safety check (dependency vulnerabilities)
  - Optional: Bandit for SAST (static analysis)
  - Fails pipeline on high-severity vulnerabilities
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started
- **Reference Docs:**
  - `docs/testing_strategy.md` (Section: Security Scanning)

---

## Epic 9: Developer Experience Enhancements [P2]

**Goal:** Polish developer experience and documentation

**Timeline:** Post-MVP

### Feature 9.1: Docker Development

**User Story 9.1.1:** As a developer, I want to run the entire stack with docker-compose so that setup is simple

- **Acceptance Criteria:**
  - `backend/Dockerfile` builds backend image
  - `docker-compose.yml` starts backend + postgres + redis + ollama
  - `docker-compose up` starts all services
  - Hot reload works for backend code changes
  - Environment variables passed from `.env`
- **Priority:** P2
- **Estimate:** 4 hours
- **Status:** Not Started

### Feature 9.2: API Documentation

**User Story 9.2.1:** As a frontend developer, I want interactive API documentation so that I know how to call endpoints

- **Acceptance Criteria:**
  - FastAPI auto-generates OpenAPI docs at `/docs`
  - All endpoints documented with descriptions, request/response schemas
  - Try-it-out functionality works
  - Authentication flows documented
- **Priority:** P2
- **Estimate:** 2 hours (mostly auto-generated)
- **Status:** Not Started

### Feature 9.3: Development Scripts

**User Story 9.3.1:** As a developer, I want database seeding scripts so that I can test with realistic data

- **Acceptance Criteria:**
  - `scripts/seed_db.py` creates sample users, vault items, tags
  - `make seed` command runs seeding
  - Idempotent (can run multiple times)
- **Priority:** P3
- **Estimate:** 3 hours
- **Status:** Not Started

---

## Epic 10: Production Readiness [P1]

**Goal:** Prepare for production deployment

**Timeline:** Week 4

### Feature 10.1: Error Handling

**User Story 10.1.1:** As a user, I want helpful error messages when something goes wrong so that I understand what happened

- **Acceptance Criteria:**
  - Custom exception classes: EncryptionError, AuthenticationError, IntegrationError
  - Exception handlers for 400, 401, 403, 404, 500
  - Errors return consistent JSON format: `{error: string, detail: string}`
  - Sensitive data NOT included in error responses
- **Priority:** P1
- **Estimate:** 4 hours
- **Status:** Not Started

**User Story 10.1.2:** As a developer, I want structured logging so that I can debug production issues

- **Acceptance Criteria:**
  - JSON-formatted logs (not plain text)
  - Log levels: DEBUG (dev), INFO (prod)
  - Request ID tracking across service boundaries
  - No sensitive data logged (decrypted content, tokens, keys)
- **Priority:** P1
- **Estimate:** 3 hours
- **Status:** Not Started

**User Story 10.1.3:** As a developer, I want audit logging for critical actions so I can debug user-specific incidents without exposing sensitive content

- **Acceptance Criteria:**
  - Logs: login, logout, create/delete vault item, Epic connect/disconnect
  - Never log decrypted content or tokens
  - Timestamped with user_id and action type
  - Queryable for security investigations
- **Priority:** P1
- **Estimate:** 3 hours
- **Status:** Not Started

### Feature 10.2: Security Hardening

**User Story 10.2.1:** As a user, I want my API protected from common attacks so that my data is safe

- **Acceptance Criteria:**
  - CORS configured with allowed origins from .env
  - Basic security headers: X-Frame-Options, X-Content-Type-Options
  - Input validation on all endpoints (max lengths, types)
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started

**User Story 10.2.2:** As a developer, I want per-route rate limiting rules so chat cannot be spammed or abused

- **Acceptance Criteria:**
  - 20/min chat endpoints
  - 100/min vault endpoints
  - 10/min auth endpoints
  - Global IP throttles for suspicious activity
  - 429 Too Many Requests response
- **Priority:** P1
- **Estimate:** 3 hours
- **Status:** Not Started

### Feature 10.3: Performance Optimization

**User Story 10.3.1:** As a user, I want fast API responses so that the app feels snappy

- **Acceptance Criteria:**
  - Database connection pooling (pool_size=10, max_overflow=20)
  - Pagination on all list endpoints (prevent loading 1000s of items)
  - Partial indexes on queries (e.g., WHERE deleted_at IS NULL)
  - Background tasks for slow operations (Epic sync)
- **Priority:** P1
- **Estimate:** 3 hours
- **Status:** Not Started

### Feature 10.4: Health Checks

**User Story 10.4.1:** As a DevOps engineer, I want health check endpoints so that I can monitor service status

- **Acceptance Criteria:**
  - GET `/health` returns 200 OK (basic liveness check)
  - GET `/health/db` checks database connectivity
  - Used by Render/Railway for health monitoring
- **Priority:** P1
- **Estimate:** 1 hour
- **Status:** Not Started

### Feature 10.5: Environment Management

**User Story 10.5.1:** As a developer, I want dev/prod environment variable separation so nothing breaks when deploying

- **Acceptance Criteria:**
  - `.env.local` for development
  - `.env.production` for production
  - Prevent accidental usage of dev OAuth credentials in production
  - Secure default values for all required variables
  - Validation on startup (fail fast if required vars missing)
- **Priority:** P0
- **Estimate:** 2 hours
- **Status:** Not Started

### Feature 10.6: Deployment Pipeline

**User Story 10.6.1:** As a developer, I need a pinned reproducible environment in prod so that deployment is predictable

- **Acceptance Criteria:**
  - Production-ready Dockerfile with pinned dependencies
  - Run migrations automatically on deploy
  - Verify health endpoint after deploy
  - Rollback mechanism if health check fails
- **Priority:** P1
- **Estimate:** 4 hours
- **Status:** Not Started

### Feature 10.7: Backup & Recovery

**User Story 10.7.1:** As a user, I want encrypted backups of my vault so I don't lose data

- **Acceptance Criteria:**
  - Daily automated backup of encrypted database (not plaintext)
  - Backups stored in Railway or S3
  - Recovery script to restore from backup
  - Must NOT decrypt anything during backup process
  - Test restore process monthly
- **Priority:** P1
- **Estimate:** 4 hours
- **Status:** Not Started

---

## Epic 11: Frontend Integration [P0]

**Goal:** Build minimal Next.js UI for authentication, vault management, and chat

**Timeline:** Week 4-5

### Feature 11.1: Authentication UI

**User Story 11.1.1:** As a user, I want a "Sign In with Google" button that sends me through the OAuth flow so I can log in easily

- **Acceptance Criteria:**
  - Button redirects to backend `/api/auth/google/login` endpoint
  - Handles OAuth callback and stores access_token + refresh_token securely
  - Stores tokens in memory or HttpOnly cookies (not localStorage for XSS protection)
  - Calls `/api/auth/me` to verify session and load user profile
  - Redirects to vault dashboard after successful login
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started

**User Story 11.1.2:** As a user, I want automatic refresh of my access token so I stay logged in without interruption

- **Acceptance Criteria:**
  - Frontend service detects 401 Unauthorized responses
  - Automatically calls `/api/auth/refresh` with refresh_token
  - Retries original request with new access_token
  - Logs out cleanly if refresh fails (redirect to login)
  - No flash of login screen during valid refresh
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started

**User Story 11.1.3:** As a user, I want to log out so that my session ends

- **Acceptance Criteria:**
  - Logout button calls `/api/auth/logout`
  - Clears all tokens from memory/cookies
  - Redirects to login page
  - Displays confirmation message
- **Priority:** P1
- **Estimate:** 1 hour
- **Status:** Not Started

### Feature 11.2: Vault UI

**User Story 11.2.1:** As a user, I want a simple UI to create, view, and edit vault items

- **Acceptance Criteria:**
  - List view shows vault items (title, type, tags, created_at)
  - List view does NOT show decrypted content (performance)
  - Create button opens editor modal
  - Click item to view full decrypted content
  - Edit button opens editor with existing content
  - Delete with confirmation dialog
  - Snappy pagination (50 items per page)
- **Priority:** P0
- **Estimate:** 8 hours
- **Status:** Not Started

**User Story 11.2.2:** As a user, I want a clean editor for vault content

- **Acceptance Criteria:**
  - Markdown or plaintext editor
  - Title field (required)
  - Content field (textarea or markdown editor)
  - Tag selector (multi-select with create new option)
  - Type selector (note, password, file, medical_record)
  - Save button persists to backend
  - Shows updated_at timestamp after save
  - Auto-save draft every 30 seconds (optional)
- **Priority:** P0
- **Estimate:** 6 hours
- **Status:** Not Started

**User Story 11.2.3:** As a user, I want to filter vault items by tags and type so that I can find related content

- **Acceptance Criteria:**
  - Tag filter dropdown (multi-select)
  - Type filter dropdown (single select)
  - Search bar for title full-text search
  - Filters apply in real-time (debounced)
  - Clear filters button
  - Filter state preserved in URL query params
- **Priority:** P1
- **Estimate:** 4 hours
- **Status:** Not Started

### Feature 11.3: Chat UI

**User Story 11.3.1:** As a user, I want a chat UI that streams responses from the backend so that the chat feels real-time

- **Acceptance Criteria:**
  - Chat input box at bottom
  - Send button triggers POST `/api/chat` with SSE streaming
  - Display vault context excerpts used (with vault_item IDs)
  - Stream message chunks as they arrive from backend
  - Display partial messages during streaming
  - Show "AI is typing..." indicator
  - Final message displayed when `done` event received
  - Chat history displayed (user messages + AI responses)
- **Priority:** P0
- **Estimate:** 8 hours
- **Status:** Not Started

**User Story 11.3.2:** As a user, I want to filter which vault items are used as chat context

- **Acceptance Criteria:**
  - Tag filter dropdown in chat UI
  - Selected tags sent with chat request
  - Context event shows which items were used
  - Clear indication when no context found for query
- **Priority:** P1
- **Estimate:** 2 hours
- **Status:** Not Started

### Feature 11.4: Frontend Infrastructure

**User Story 11.4.1:** As a developer, I need a Next.js + TypeScript project (App Router) with shadcn/ui components

- **Acceptance Criteria:**
  - Next.js project initialized in `frontend/` directory
  - TypeScript configured with strict mode
  - shadcn/ui installed and configured
  - API client service for backend calls (axios or fetch)
  - Environment variables: `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID`
  - Hot reload works for local development
- **Priority:** P0
- **Estimate:** 3 hours
- **Status:** Not Started

**User Story 11.4.2:** As a developer, I need Next.js auth state management so that protected routes work

- **Acceptance Criteria:**
  - Auth context provider (Next.js client context or Zustand)
  - Protected route wrapper (redirects to login if not authenticated)
  - Token refresh logic in API interceptor
  - User profile state globally accessible
- **Priority:** P0
- **Estimate:** 4 hours
- **Status:** Not Started

---

## Summary

**Total Epics:** 11
**Total Features:** 37
**Total User Stories:** 100+

**Critical Path (Week 1-5):**

1. Epic 1: Foundation (3 days)
2. Epic 2: Security (2 days)
3. Epic 3: Database (1 day)
4. Epic 4: Authentication (2 days)
5. Epic 5: Vault (3 days)
6. Epic 6: Epic Integration (3 days)
7. Epic 7: Chat (2 days)
8. Epic 8: Testing (2 days)
9. Epic 11: Frontend (4 days)

**Post-MVP:** 9. Epic 9: Developer Experience 10. Epic 10: Production Readiness

**Estimated Total:** 22 days (4.5 weeks) for core features + frontend + testing
