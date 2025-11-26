# Context Vault - API Endpoints Documentation

## Base URLs

**Development:** `http://localhost:8000`
**Production:** `https://contextvault-api.onrender.com`

## Authentication

All endpoints except `/auth/google/*` and `/health` require authentication.

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Access Token:**
- JWT signed with HS256
- Expires in 30 minutes
- Payload: `{user_id, email, exp, iat}`

**Refresh Token:**
- Opaque token, 32 bytes random
- Expires in 30 days
- Stored hashed in database

## Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/expired token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate resource) |
| 422 | Unprocessable Entity (validation error) |
| 500 | Internal Server Error |

## Error Response Format

```json
{
  "detail": "Error message here",
  "error_code": "INVALID_TOKEN",
  "timestamp": "2025-01-25T10:30:00Z"
}
```

---

## Authentication Endpoints

### POST /api/auth/google/login

Initiate Google OAuth flow.

**Request:**
```http
POST /api/auth/google/login
```

**Response:** 302 Redirect to Google OAuth consent screen

**Query Parameters (after redirect back):**
- `redirect_uri` (optional): Frontend URL to redirect after successful auth

---

### GET /api/auth/google/callback

OAuth callback endpoint (handled automatically by Google).

**Request:**
```http
GET /api/auth/google/callback?code={auth_code}&state={state}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "a1b2c3d4e5f6...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "picture_url": "https://..."
  }
}
```

---

### POST /api/auth/refresh

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "a1b2c3d4e5f6..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- 401: Invalid or expired refresh token

---

### POST /api/auth/logout

Invalidate current session.

**Request:**
```json
{
  "refresh_token": "a1b2c3d4e5f6..."
}
```

**Response:** 204 No Content

---

### GET /api/auth/me

Get current user profile.

**Request:**
```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "picture_url": "https://...",
  "preferences": {
    "theme": "dark",
    "default_model": "llama3.1:8b"
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

## Vault Endpoints

### GET /api/vault/items

List user's vault items with pagination and filtering.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `per_page` (int, default: 50, max: 100): Items per page
- `type` (string, optional): Filter by type (note, file, medical_record, etc.)
- `source` (string, optional): Filter by source (manual, epic, fitbit, etc.)
- `tags` (string[], optional): Filter by tag names (comma-separated)
- `search` (string, optional): Full-text search in titles
- `sort` (string, default: created_at): Sort field
- `order` (string, default: desc): Sort order (asc/desc)

**Request:**
```http
GET /api/vault/items?page=1&per_page=20&tags=medical,important&search=blood%20pressure
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "medical_record",
      "title": "Blood Pressure Reading - Jan 20",
      "source": "epic",
      "tags": ["medical", "important"],
      "created_at": "2025-01-20T14:30:00Z",
      "updated_at": "2025-01-20T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 145,
    "total_pages": 8
  }
}
```

**Notes:**
- `content` not included in list view (performance)
- Use GET /api/vault/items/{id} to fetch full content

---

### POST /api/vault/items

Create new vault item.

**Request:**
```json
{
  "type": "note",
  "title": "My grocery list",
  "content": "Milk, eggs, bread...",
  "tags": ["personal", "shopping"],
  "metadata": {
    "custom_field": "value"
  }
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "type": "note",
  "title": "My grocery list",
  "source": "manual",
  "tags": ["personal", "shopping"],
  "created_at": "2025-01-25T10:30:00Z",
  "updated_at": "2025-01-25T10:30:00Z"
}
```

**Validation:**
- `title`: Max 500 characters
- `content`: Required, max 1MB
- `tags`: Max 10 tags per item
- `type`: Must be valid enum value

---

### GET /api/vault/items/{id}

Get single vault item with full content (decrypted).

**Request:**
```http
GET /api/vault/items/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "note",
  "title": "My grocery list",
  "content": "Milk, eggs, bread, butter, cheese",
  "source": "manual",
  "tags": ["personal", "shopping"],
  "metadata": {
    "custom_field": "value"
  },
  "created_at": "2025-01-25T10:30:00Z",
  "updated_at": "2025-01-25T10:30:00Z"
}
```

**Errors:**
- 404: Vault item not found or doesn't belong to user

---

### PUT /api/vault/items/{id}

Update vault item.

**Request:**
```json
{
  "title": "Updated title",
  "content": "Updated content",
  "tags": ["new", "tags"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "type": "note",
  "title": "Updated title",
  "content": "Updated content",
  "tags": ["new", "tags"],
  "updated_at": "2025-01-25T11:00:00Z"
}
```

**Notes:**
- Partial updates supported (only send changed fields)
- `type` and `source` cannot be changed

---

### DELETE /api/vault/items/{id}

Soft delete vault item.

**Request:**
```http
DELETE /api/vault/items/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

**Notes:**
- Soft delete (sets `deleted_at` timestamp)
- Item recoverable for 90 days
- Use `DELETE /api/vault/items/{id}?permanent=true` for hard delete

---

### POST /api/vault/upload

Upload file to vault (PDF, image, text).

**Request:**
```http
POST /api/vault/upload
Content-Type: multipart/form-data
Authorization: Bearer {access_token}

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="medical_report.pdf"
Content-Type: application/pdf

[binary data]
------WebKitFormBoundary
Content-Disposition: form-data; name="title"

Medical Report - Jan 2025
------WebKitFormBoundary
Content-Disposition: form-data; name="tags"

medical,important
------WebKitFormBoundary--
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "type": "file",
  "title": "Medical Report - Jan 2025",
  "source": "manual",
  "tags": ["medical", "important"],
  "metadata": {
    "original_filename": "medical_report.pdf",
    "file_size": 245678,
    "mime_type": "application/pdf",
    "extracted_text_preview": "Patient Name: John Doe..."
  },
  "created_at": "2025-01-25T10:30:00Z"
}
```

**Supported File Types:**
- PDF (text extraction via PyPDF2)
- Images: JPG, PNG, GIF (OCR via Tesseract)
- Text: TXT, MD, CSV

**Limits:**
- Max file size: 10MB
- Max 100 files per day per user

---

### GET /api/vault/search

Full-text search across vault items.

**Query Parameters:**
- `q` (string, required): Search query
- `type` (string[], optional): Filter by types
- `source` (string[], optional): Filter by sources
- `limit` (int, default: 20): Max results

**Request:**
```http
GET /api/vault/search?q=blood+pressure&type=medical_record&limit=10
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "type": "medical_record",
      "title": "Blood Pressure Reading - Jan 20",
      "content_snippet": "...systolic 120, diastolic 80...",
      "source": "epic",
      "relevance_score": 0.92,
      "created_at": "2025-01-20T14:30:00Z"
    }
  ],
  "total": 5,
  "query": "blood pressure"
}
```

**Notes:**
- Searches titles (plain text) and content (decrypted on-the-fly)
- Results ranked by relevance
- Snippet shows context around match

---

### GET /api/vault/tags

Get user's tags with usage counts.

**Request:**
```http
GET /api/vault/tags
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "tags": [
    {
      "id": "uuid",
      "name": "medical",
      "color": "#FF5733",
      "item_count": 45,
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": "uuid",
      "name": "personal",
      "color": "#3498DB",
      "item_count": 23,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

### POST /api/vault/tags

Create new tag.

**Request:**
```json
{
  "name": "work",
  "color": "#2ECC71"
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "name": "work",
  "color": "#2ECC71",
  "created_at": "2025-01-25T10:30:00Z"
}
```

**Errors:**
- 409: Tag name already exists for this user

---

### DELETE /api/vault/tags/{id}

Delete tag and remove from all vault items.

**Request:**
```http
DELETE /api/vault/tags/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

---

### GET /api/vault/export

Export all user data (GDPR compliance).

**Request:**
```http
GET /api/vault/export
Authorization: Bearer {access_token}
```

**Response:** JSON file download
```json
{
  "user": {
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "vault_items": [...],
  "tags": [...],
  "integrations": [...]
}
```

**Notes:**
- All vault items decrypted
- Files included as base64
- Can take 30+ seconds for large vaults

---

## Chat Endpoints

### POST /api/chat

Send message to AI with vault context.

**Request:**
```json
{
  "message": "What were my blood pressure readings last month?",
  "context_tags": ["medical"],
  "model": "llama3.1:8b"
}
```

**Response:** Server-Sent Events (SSE) stream

```
event: message
data: {"chunk": "Based on your ", "done": false}

event: message
data: {"chunk": "medical records, ", "done": false}

event: message
data: {"chunk": "your blood pressure...", "done": false}

event: context
data: {"vault_items": ["uuid1", "uuid2"], "count": 2}

event: message
data: {"chunk": "", "done": true}

event: done
data: {"total_tokens": 145, "duration_ms": 2340}
```

**SSE Event Types:**
- `message`: Streaming text chunks
- `context`: Vault items used as context
- `done`: Stream complete with metadata

**Request Fields:**
- `message` (required): User's chat message
- `context_tags` (optional): Limit context to specific tags
- `model` (optional): Override default model

---

### GET /api/chat/history

Get recent chat conversations (if history enabled).

**Query Parameters:**
- `limit` (int, default: 10): Number of conversations

**Request:**
```http
GET /api/chat/history?limit=5
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Blood pressure discussion",
      "messages": [
        {
          "role": "user",
          "content": "What were my readings?",
          "timestamp": "2025-01-25T10:30:00Z"
        },
        {
          "role": "assistant",
          "content": "Your readings were...",
          "timestamp": "2025-01-25T10:30:05Z"
        }
      ],
      "created_at": "2025-01-25T10:30:00Z"
    }
  ]
}
```

**Notes:**
- Chat history optional (off by default for privacy)
- Enable in user preferences

---

### DELETE /api/chat/history

Clear all chat history.

**Request:**
```http
DELETE /api/chat/history
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

---

## Integration Endpoints

### GET /api/integrations

List all integrations with status.

**Request:**
```http
GET /api/integrations
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "integrations": [
    {
      "id": "uuid",
      "provider": "epic",
      "status": "connected",
      "last_sync_at": "2025-01-25T08:00:00Z",
      "metadata": {
        "patient_id": "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB",
        "records_synced": 45
      },
      "created_at": "2025-01-20T14:00:00Z"
    },
    {
      "id": "uuid",
      "provider": "fitbit",
      "status": "disconnected",
      "last_sync_at": null,
      "created_at": "2025-01-22T10:00:00Z"
    }
  ]
}
```

---

### POST /api/integrations/epic/connect

Start Epic SMART on FHIR OAuth flow.

**Request:**
```http
POST /api/integrations/epic/connect
Authorization: Bearer {access_token}
```

**Response:** 302 Redirect to Epic OAuth

**Query Parameters (after redirect):**
- `iss`: FHIR base URL (Epic's server)
- `launch`: Launch context (from Epic)

---

### GET /api/integrations/epic/callback

Epic OAuth callback (handled automatically).

**Request:**
```http
GET /api/integrations/epic/callback?code={code}&state={state}
```

**Response:** 302 Redirect to frontend with success

**Side Effects:**
- Stores encrypted tokens in database
- Queues background sync job

---

### POST /api/integrations/epic/sync

Manually trigger Epic data sync.

**Request:**
```http
POST /api/integrations/epic/sync
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "syncing",
  "job_id": "uuid"
}
```

**Notes:**
- Async operation (background job)
- Use GET /api/integrations/epic/status?job_id={id} to check progress

---

### GET /api/integrations/epic/status

Check sync job status.

**Query Parameters:**
- `job_id` (required): Job ID from sync request

**Request:**
```http
GET /api/integrations/epic/status?job_id=uuid
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "completed",
  "progress": 100,
  "records_synced": 23,
  "errors": [],
  "completed_at": "2025-01-25T10:35:00Z"
}
```

**Status Values:**
- `queued`: Waiting to start
- `syncing`: In progress
- `completed`: Success
- `failed`: Error occurred

---

### DELETE /api/integrations/epic

Disconnect Epic integration.

**Request:**
```http
DELETE /api/integrations/epic
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

**Query Parameters:**
- `delete_data` (bool, default: false): Also delete synced vault items

**Notes:**
- Deletes tokens from database
- Optionally soft-deletes all vault items with source='epic'

---

### POST /api/integrations/fitbit/connect

Start Fitbit OAuth flow.

**Request:**
```http
POST /api/integrations/fitbit/connect
Authorization: Bearer {access_token}
```

**Response:** 302 Redirect to Fitbit OAuth

---

### GET /api/integrations/fitbit/callback

Fitbit OAuth callback.

**Request:**
```http
GET /api/integrations/fitbit/callback?code={code}&state={state}
```

**Response:** 302 Redirect to frontend

---

### POST /api/integrations/fitbit/sync

Trigger Fitbit data sync.

**Request:**
```http
POST /api/integrations/fitbit/sync
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "syncing",
  "job_id": "uuid"
}
```

---

### DELETE /api/integrations/fitbit

Disconnect Fitbit.

**Request:**
```http
DELETE /api/integrations/fitbit
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

---

### POST /api/integrations/apple-health/upload

Upload Apple Health XML export.

**Request:**
```http
POST /api/integrations/apple-health/upload
Content-Type: multipart/form-data
Authorization: Bearer {access_token}

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="export.xml"
Content-Type: application/xml

[XML data]
------WebKitFormBoundary--
```

**Response:**
```json
{
  "status": "processing",
  "job_id": "uuid",
  "file_size": 5242880,
  "estimated_records": 12000
}
```

**Notes:**
- Large XML files processed in background
- Can take several minutes

---

## Ollama Management Endpoints

### GET /api/ollama/status

Check if Ollama is available.

**Request:**
```http
GET /api/ollama/status
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "available": true,
  "version": "0.1.17",
  "models_count": 4
}
```

**Errors:**
- 503: Ollama not available

---

### GET /api/ollama/models

List available models on Ollama.

**Request:**
```http
GET /api/ollama/models
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.1:8b",
      "size": 4900000000,
      "size_gb": 4.9,
      "modified_at": "2025-01-15T10:00:00Z"
    },
    {
      "name": "mistral:7b",
      "size": 4400000000,
      "size_gb": 4.4,
      "modified_at": "2025-01-10T14:00:00Z"
    }
  ]
}
```

---

### POST /api/ollama/models/pull

Download a model via Ollama.

**Request:**
```json
{
  "model": "llama3.1:8b"
}
```

**Response:** Server-Sent Events (SSE) stream

```
event: progress
data: {"status": "pulling manifest", "progress": 0}

event: progress
data: {"status": "downloading", "completed": 1200000000, "total": 4900000000, "progress": 24}

event: progress
data: {"status": "downloading", "completed": 4900000000, "total": 4900000000, "progress": 100}

event: done
data: {"status": "success", "model": "llama3.1:8b"}
```

**Notes:**
- Can take 5-10 minutes for large models
- Client should show progress bar

---

### GET /api/ollama/models/current

Get user's selected model preference.

**Request:**
```http
GET /api/ollama/models/current
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "model": "llama3.1:8b"
}
```

---

### PUT /api/ollama/models/current

Set user's default model.

**Request:**
```json
{
  "model": "mistral:7b"
}
```

**Response:**
```json
{
  "model": "mistral:7b",
  "updated_at": "2025-01-25T10:30:00Z"
}
```

---

## Health Check Endpoints

### GET /health

Basic health check.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-25T10:30:00Z"
}
```

---

### GET /health/db

Database connectivity check.

**Request:**
```http
GET /health/db
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "latency_ms": 12
}
```

**Errors:**
- 503: Database unavailable

---

### GET /health/ollama

Ollama availability check.

**Request:**
```http
GET /health/ollama
```

**Response:**
```json
{
  "status": "healthy",
  "ollama": "available",
  "version": "0.1.17"
}
```

**Errors:**
- 503: Ollama unavailable

---

## Rate Limiting

**Limits:**
- Authentication: 10 requests/minute
- Vault CRUD: 100 requests/minute
- Chat: 20 requests/minute
- File upload: 10 requests/minute
- Integration sync: 5 requests/hour

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1643125800
```

**Error Response (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds.",
  "retry_after": 45
}
```

---

## Pagination

**Query Parameters:**
- `page` (int, default: 1): Page number (1-indexed)
- `per_page` (int, default: 50): Items per page

**Response Headers:**
```
X-Total-Count: 145
X-Page: 1
X-Per-Page: 50
X-Total-Pages: 3
Link: <...?page=2>; rel="next", <...?page=3>; rel="last"
```

---

## Webhooks (Future)

**Epic Real-Time Sync:**
- Epic can send webhooks when patient data changes
- Endpoint: POST /api/webhooks/epic
- Requires HMAC signature verification

**Fitbit Subscriptions:**
- Real-time activity updates
- Endpoint: POST /api/webhooks/fitbit

---

## API Versioning (Future)

**Current:** All endpoints implicitly v1
**Future:** `/api/v2/...` for breaking changes

**Deprecation Policy:**
- 6 months notice before removing v1 endpoints
- `Sunset` header: `Sunset: Sat, 31 Dec 2025 23:59:59 GMT`

---

**Next Steps:**
1. Implement authentication (Google OAuth + JWT)
2. Build vault CRUD endpoints
3. Add Epic integration endpoints
4. Implement chat streaming with Ollama
