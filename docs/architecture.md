# Context Vault - System Architecture

## Overview

Context Vault is a privacy-first personal intelligence system that combines secure local data storage with AI capabilities. The core principle: **user data never enters persistent storage in third-party systems**.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Browser                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  React Frontend (Vercel)                              │ │
│  │  - shadcn/ui components                               │ │
│  │  - Client-side encryption for vault data              │ │
│  │  - PWA for mobile access                              │ │
│  └─────────────────────┬─────────────────────────────────┘ │
└────────────────────────┼───────────────────────────────────┘
                         │ HTTPS/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (Render)                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  API Layer                                            │ │
│  │  - Google OAuth authentication                        │ │
│  │  - Epic SMART on FHIR integration                     │ │
│  │  - Fitbit & Apple Health adapters                     │ │
│  │  - Ephemeral LLM orchestration                        │ │
│  └─────────────────────┬─────────────────────────────────┘ │
└────────────────────────┼───────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌─────────────┐ ┌──────────────────┐
│   PostgreSQL  │ │   Ollama    │ │  File Storage    │
│   (Railway)   │ │  (Ephemeral │ │  (Encrypted S3   │
│               │ │  Containers)│ │   or Local)      │
│  Encrypted    │ │  RAM-only   │ │  Per-user keys   │
│  vault items  │ │  No persist │ │  AES-256-GCM     │
└───────────────┘ └─────────────┘ └──────────────────┘
```

## Core Components

### 1. Frontend (React + Vite)

**Technology Stack:**
- React 18+ with TypeScript
- Vite for build tooling
- shadcn/ui component library
- TailwindCSS for styling
- Zustand or React Context for state
- React Query for API data fetching

**Key Features:**
- Responsive design (desktop, tablet, mobile)
- Progressive Web App (PWA) capabilities
- Client-side encryption helpers
- Offline-capable vault viewing
- Real-time chat interface with streaming

**Deployment:** Vercel (free tier)
- URL: `contextvault.vercel.app`
- Auto-deploy from `main` branch
- Environment variables managed in Vercel dashboard

### 2. Backend (FastAPI)

**Technology Stack:**
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- Pydantic v2 (validation)
- httpx (async HTTP client)
- python-jose (JWT)
- cryptography (encryption)

**Core Services:**

**Authentication Service:**
- Google OAuth 2.0 flow
- JWT access tokens (30 min expiry)
- Refresh tokens (30 day expiry)
- Session management

**Vault Service:**
- CRUD operations on vault items
- Tag-based organization
- Full-text search
- File upload with parsing (PDF, images)
- Encryption/decryption layer

**Integration Services:**
- Epic SMART on FHIR OAuth + data sync
- Fitbit OAuth + API polling
- Apple Health XML parser

**Ephemeral LLM Service:**
- Docker container orchestration
- Context retrieval from vault
- Streaming chat responses
- Container lifecycle management

**Deployment:** Render (free tier)
- URL: `contextvault-api.onrender.com`
- Auto-deploy from `main` branch
- Spins down after inactivity (cold starts ~30s)

### 3. Database (PostgreSQL on Railway)

**Schema Overview:**
- `users` - Authentication and encryption keys
- `vault_items` - Encrypted user data
- `tags` - User-defined categories
- `vault_item_tags` - Many-to-many relationship
- `integrations` - Connection status
- `integration_tokens` - Encrypted OAuth tokens
- `sessions` - Refresh token tracking

**Encryption Strategy:**
- Database connection over SSL
- Sensitive fields encrypted at application layer
- Per-user encryption keys derived from Google ID + app secret

**Connection:**
- External URL for backend: `dpg-d4j00bvgi27c73eto9j0-a.ohio-postgres.render.com:5432`
- SSL mode: `require`
- Connection pooling via SQLAlchemy

### 4. Ephemeral LLM Containers (Ollama)

**Privacy Architecture:**

The key innovation: **vault data never persists in LLM containers**.

**Container Lifecycle:**
```
User sends message
    ↓
Backend retrieves relevant vault items (tags/embeddings)
    ↓
Backend builds prompt: system instructions + vault context + user query
    ↓
Spin up fresh Docker container with Ollama
    ↓
Container loads model into RAM (tmpfs mount, no disk writes)
    ↓
Process single request with context
    ↓
Stream response back to user
    ↓
Destroy container immediately (all RAM wiped)
```

**Implementation Options:**

**Option A: Pure Ephemeral (Maximum Privacy)**
- New container per request
- Lifetime: 3-5 seconds
- Pros: Zero data persistence risk
- Cons: Slower (~2-5s first token)

**Option B: Container Pool (Balanced) - RECOMMENDED FOR MVP**
- Maintain 2-3 warm containers
- Rotate/destroy every 10 requests
- Lifetime: ~10 minutes max per container
- Pros: Fast response (<1s), still private
- Cons: Slightly higher memory footprint

**Technical Specs:**
- Base image: `ollama/ollama:latest`
- Default model: `llama3.1:8b` (4.9GB)
- Memory limit: 4GB per container
- Mount: tmpfs (RAM-only, no disk persistence)
- Network: Isolated bridge network

### 5. File Storage

**MVP: Local Filesystem**
- Path: `/data/uploads/{user_id}/{file_id}.enc`
- Encryption: AES-256-GCM with per-user keys
- Metadata in database

**Production: Encrypted S3/R2**
- Cloudflare R2 (S3-compatible, cheaper egress)
- Files encrypted before upload
- Pre-signed URLs for download (decrypted client-side)

## Data Flow Examples

### User Uploads File to Vault

```
1. User selects PDF in browser
2. Frontend: POST /api/vault/upload (multipart/form-data)
3. Backend:
   a. Authenticate user (JWT)
   b. Parse file content (extract text from PDF)
   c. Encrypt file with user's key
   d. Save encrypted file to storage
   e. Create vault_item record (encrypted content + metadata)
   f. Return vault item ID
4. Frontend: Display new item in vault dashboard
```

### User Chats with AI About Medical Records

```
1. User types: "What were my blood pressure readings last month?"
2. Frontend: POST /api/chat with message
3. Backend:
   a. Search vault: tags=["medical", "blood_pressure"], date_range=last_month
   b. Retrieve relevant vault items (3 observations)
   c. Build prompt:
      System: You are a private AI assistant with access to user's medical data.
      Context: [3 FHIR observations with BP readings]
      User: What were my blood pressure readings last month?
   d. Spin up ephemeral container (or use warm container from pool)
   e. Send prompt to Ollama
   f. Stream response back to frontend (SSE)
   g. Destroy/recycle container
4. Frontend: Display AI response with context indicators
```

### Epic MyChart Sync

```
1. User clicks "Connect Epic" in Settings
2. Frontend: Redirect to /api/integrations/epic/connect
3. Backend:
   a. Generate PKCE code_verifier and code_challenge
   b. Store state in Redis (5 min TTL)
   c. Redirect to Epic OAuth: https://fhir.epic.com/oauth2/authorize
4. User logs into Epic MyChart, approves access
5. Epic redirects to: /api/integrations/epic/callback?code=...&state=...
6. Backend:
   a. Validate state (CSRF protection)
   b. Exchange code for tokens (PKCE flow)
   c. Validate id_token (JWKS)
   d. Encrypt and store tokens in database
   e. Create integration record
   f. Queue background sync job
7. Background worker:
   a. Fetch Patient resource from Epic
   b. Fetch Observations (last 2 years)
   c. Transform FHIR → vault_items
   d. Encrypt and store in database
8. Frontend: Show "X records synced" notification
```

## Security Architecture

### Authentication Flow

```
1. User clicks "Sign in with Google"
2. Backend: Redirect to Google OAuth
3. Google: User authorizes, redirects back with code
4. Backend:
   a. Exchange code for Google tokens
   b. Fetch user profile (email, name, google_id)
   c. Create or retrieve user from database
   d. Derive user encryption key: PBKDF2(google_id + app_secret, 100k iterations)
   e. Generate JWT access token (30 min) and refresh token (30 days)
   f. Store refresh token hash in sessions table
5. Frontend: Store tokens in memory (not localStorage)
6. All API requests: Authorization: Bearer {access_token}
7. On access token expiry: POST /api/auth/refresh with refresh_token
```

### Encryption Layers

**Layer 1: Transport (TLS)**
- All communication over HTTPS
- Certificate managed by Vercel/Render

**Layer 2: Database Connection**
- PostgreSQL SSL mode: require
- Encrypted connection to Railway

**Layer 3: Application-Level Encryption**
- Vault item content: AES-256-GCM
- OAuth tokens: AES-256-GCM
- Files: AES-256-GCM
- Key derivation: PBKDF2 with 100k iterations

**Layer 4: Ephemeral Containers**
- No disk writes (tmpfs only)
- Containers destroyed after use
- No logging of vault content

### Key Management

**User Master Key:**
```python
# Derived per-user, never stored directly
master_key = PBKDF2(
    password=user.google_id + settings.APP_SECRET_KEY,
    salt=user.id,  # UUID
    iterations=100000,
    algorithm='sha256',
    key_length=32  # 256 bits
)
```

**Per-Item Encryption:**
- Each vault item encrypted with unique nonce
- AES-256-GCM (authenticated encryption)
- Format: `nonce (12 bytes) || ciphertext || auth_tag (16 bytes)`

### Threat Model

**What we protect against:**
- ✅ Compromised backend server (data encrypted, attacker can't decrypt)
- ✅ Malicious admin (no access to user encryption keys)
- ✅ Database breach (encrypted vault items useless without keys)
- ✅ Container escape (no persistent data to steal)
- ✅ Network sniffing (TLS everywhere)

**What we don't protect against (out of scope for MVP):**
- ❌ Compromised user device (client-side malware could intercept)
- ❌ Compromised Google account (attacker could OAuth in as user)
- ❌ Quantum computing attacks (AES-256 is quantum-resistant for now)

## Scalability Considerations

### MVP (0-1000 users)

**Current Setup:**
- Render free tier: 512MB RAM, spins down after inactivity
- Railway free tier: Shared Postgres (1GB storage)
- Ollama: User's local machine or single hosted instance

**Bottlenecks:**
- Render cold starts (~30s)
- Single Ollama instance (can't handle concurrent users)
- No CDN for frontend assets

### Phase 2 (1000-10,000 users)

**Upgrades:**
- Render: Upgrade to $7/mo plan (always-on, 512MB → 2GB RAM)
- Railway: Upgrade to $5/mo (dedicated Postgres, 1GB → 8GB storage)
- Ollama: Container pool with 5-10 warm containers
- Redis: Add caching layer for vault search
- CDN: Cloudflare in front of Vercel

### Phase 3 (10,000+ users)

**Architecture Changes:**
- Backend: Horizontal scaling with load balancer
- Database: Read replicas for vault queries
- Ollama: Kubernetes cluster with auto-scaling
- File Storage: Move to Cloudflare R2
- Message Queue: Celery + Redis for background jobs

## Technology Choices - Rationale

### Why FastAPI?
- Best-in-class async support (critical for streaming chat)
- Automatic OpenAPI docs
- Pydantic validation (type safety)
- Easy CORS and middleware
- Existing Epic integration code already uses it

### Why PostgreSQL over SQLite?
- Render/Railway offer free hosted Postgres (easier deployment)
- Better concurrency handling
- Full-text search built-in
- JSON column support for flexible metadata
- Migration path for scaling

### Why Ollama over llama.cpp?
- Simpler API (REST instead of bindings)
- Model management built-in
- Better documentation
- Docker image available
- Multi-model support

### Why shadcn/ui over Material-UI?
- Modern, professional aesthetic
- Headless + customizable
- TailwindCSS integration
- Smaller bundle size
- Active development

### Why Vercel over Netlify?
- Better Next.js support (future migration path)
- Edge functions (faster cold starts)
- Superior developer experience
- Free tier sufficient for MVP

## Deployment Environments

### Local Development

```bash
# Frontend
cd frontend && npm run dev  # http://localhost:5173

# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload  # http://localhost:8000

# Ollama (separate terminal)
ollama serve  # http://localhost:11434

# Database
# Uses Railway hosted Postgres (no local setup needed)
```

### Staging (Future)

- Frontend: Vercel preview deployments (auto per PR)
- Backend: Render preview instances
- Database: Separate Railway database

### Production

- Frontend: `contextvault.vercel.app`
- Backend: `contextvault-api.onrender.com`
- Database: Railway Postgres (Ohio region)

## Monitoring & Observability

### Logging

**Backend:**
- Structured JSON logs via `structlog`
- Log levels: DEBUG (dev), INFO (prod)
- NO logging of vault content or sensitive data
- Redact: tokens, encryption keys, user data

**Frontend:**
- Console errors in dev
- Production: Silent (no console logs)

### Metrics to Track (Future)

- API response times (p50, p95, p99)
- Ephemeral container lifecycle (creation, duration, errors)
- Epic sync success rate
- Chat message latency (first token, full response)
- Database query performance

### Health Checks

- `GET /health` - Basic liveness check
- `GET /health/db` - Database connectivity
- `GET /health/ollama` - Ollama availability

## Disaster Recovery

### Backup Strategy

**Database:**
- Railway automated daily backups (7 day retention)
- Manual export script: `pg_dump` to S3 weekly

**Files:**
- Encrypted files in S3 (versioning enabled)
- Cross-region replication (future)

**User Data Export:**
- API endpoint: `GET /api/vault/export`
- Returns JSON of all vault items (decrypted)
- User-initiated only (GDPR compliance)

### Recovery Scenarios

**Database Corruption:**
1. Restore from Railway backup
2. Point app to restored instance
3. Verify data integrity

**Backend Deployment Failure:**
1. Render auto-rollback to previous version
2. Manual rollback via Render dashboard
3. Fix issue, redeploy

**Ollama Service Outage:**
1. Chat feature temporarily unavailable
2. Vault access still works
3. Fallback: Show "AI temporarily unavailable" message

## Future Architecture Enhancements

### Phase 2 Features

- **Vector Embeddings:** Better context retrieval (via Ollama embed model)
- **Background Sync:** Scheduled Epic/Fitbit data pulls
- **Multi-Model Support:** User chooses model per conversation
- **Chat History:** Store encrypted conversations for continuity

### Phase 3 Features

- **Mobile Apps:** React Native with on-device LLM (MLX/llama.cpp)
- **End-to-End Encryption:** Zero-knowledge architecture
- **P2P Sync:** Cross-device sync without cloud storage
- **Federated Deployment:** User-owned servers with central discovery

## Conclusion

This architecture prioritizes **privacy, simplicity, and developer velocity** for MVP while maintaining a clear path to scale. The ephemeral container model is the core innovation that enables "ChatGPT-level functionality without surveillance."

---

**Next Steps:**
1. Review database schema (see `database_schema.md`)
2. Review API endpoints (see `api_endpoints.md`)
3. Set up local development environment (see `setup_guide.md`)
