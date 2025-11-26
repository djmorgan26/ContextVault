# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Context Vault** is a privacy-first personal intelligence system combining secure local data storage with AI capabilities. The core security principle: user data is encrypted at rest and AI processing happens in ephemeral containers that are destroyed after each use.

**Current State:** Early MVP - Epic SMART on FHIR integration implemented in standalone FastAPI app (`fastapi_epic_smart.py`). Full backend/frontend architecture documented but not yet built.

## Development Commands

### Running the MVP

```bash
# Start the Epic SMART integration server
python fastapi_epic_smart.py
# Runs on http://localhost:8000
# API docs: http://localhost:8000/docs

# With Ollama (for future AI chat features)
ollama serve  # In separate terminal
ollama pull llama3.1:8b
```

### Docker Compose (Future - when backend/frontend exist)

```bash
# Start all services
docker-compose up

# Rebuild after changes
docker-compose up --build

# View logs
docker-compose logs -f backend
```

### Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Code Quality

```bash
# Format Python code
ruff format .

# Lint
ruff check .
```

## Architecture

### Current (MVP)
- **Single file FastAPI app** (`fastapi_epic_smart.py`)
- **Epic SMART on FHIR OAuth2 + PKCE flow** for medical records
- **In-memory state storage** (replace with DB in production)
- **Environment-based configuration** (`.env` file)

### Target Architecture (Documented, Not Built)
```
React Frontend (Vercel) ←→ FastAPI Backend (Render) ←→ PostgreSQL (Railway)
                                    ↓
                          Ephemeral Ollama Containers
                          (RAM-only, destroyed after use)
```

**Key architectural decisions:**
- **Backend location:** `backend/` directory (doesn't exist yet)
  - `app/api/` - API routes
  - `app/core/` - Config, security, database
  - `app/models/` - SQLAlchemy ORM models
  - `app/services/` - Business logic (encryption, Epic sync, LLM orchestration)
  - `app/schemas/` - Pydantic validation models

- **Frontend location:** `frontend/` directory (doesn't exist yet)
  - React + Vite + TypeScript
  - shadcn/ui components
  - Client-side encryption helpers

## Security Architecture

### Encryption Model
- **AES-256-GCM** for all vault data at rest
- **PBKDF2 key derivation** (100k iterations) from user's Google ID + app secret
- **User-specific keys** - backend derives keys on-demand, never stores them
- **Ephemeral LLM containers** - data passed in RAM only, destroyed immediately

### Critical Security Rules
1. **Never store decryption keys** - always derive on-demand
2. **Always encrypt vault items** before storing in database
3. **Validate all Epic FHIR data** before storing (potential PHI)
4. **Use PKCE for OAuth flows** (already implemented in `fastapi_epic_smart.py`)
5. **Short-lived tokens:** JWT access tokens expire in 30 min

### OAuth Flows

**Epic SMART on FHIR (Implemented):**
- Flow: Authorization Code + PKCE
- Entry: `GET /login` → redirects to Epic auth
- Callback: `GET /callback` → exchanges code for tokens
- OIDC validation: id_token validated against Epic's JWKS
- Refresh: `POST /refresh` with refresh_token

**Google OAuth (Documented, Not Implemented):**
- Used for primary authentication
- Scopes: `openid profile email`
- User's Google ID becomes part of encryption key derivation

## Epic Integration Details

### Environment Variables (Required)
```bash
EPIC_CLIENT_ID=          # From open.epic.com sandbox or App Orchard
EPIC_REDIRECT_URI=       # Default: http://localhost:8000/callback
EPIC_ISSUER=             # Default: https://fhir.epic.com/interconnect-fhir-oauth/oauth2
EPIC_FHIR_BASE=          # Default: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
```

### FHIR Resource Access
- **Patient data:** `GET /patient?access_token=...&patient_id=...`
- **Observations:** `GET /observations?access_token=...&patient_id=...`
- **Future:** Medications, Immunizations, Conditions

### State Management
- `STATE_STORE` dict maps OAuth state → PKCE verifier + nonce
- **Replace with Redis or DB** for production (multi-instance support)

## Database Schema (Documented, Not Implemented)

See `docs/database_schema.md` for full ERD. Key tables:
- `users` - Google OAuth user info
- `vault_items` - Encrypted personal data (notes, files, preferences)
- `epic_connections` - Epic OAuth tokens (encrypted)
- `fhir_data` - Cached medical records (encrypted)
- `tags` - Tag-based organization

## File Upload & Parsing (Future)

Planned support for:
- **PDF:** PyPDF2 or pdfplumber to extract text
- **Images:** OCR with Tesseract
- **Apple Health:** XML parser for export.xml
- All content stored encrypted in `vault_items` table

## LLM Integration (Future)

**Ephemeral Container Pattern:**
1. User sends chat message
2. Backend fetches relevant vault items (decrypt in memory)
3. Spin up Docker container: `ollama run llama3.1:8b`
4. Pass context + query via stdin/tmpfs mount (RAM only)
5. Stream response to user
6. Destroy container immediately
7. No persistent data in container filesystem

## Testing

### Manual Testing Epic Flow
1. Start app: `python fastapi_epic_smart.py`
2. Navigate: `http://localhost:8000/login`
3. Redirects to Epic MyChart sandbox
4. Use test patient from open.epic.com
5. Callback receives tokens
6. Test FHIR queries: `/patient?access_token=...&patient_id=...`

### Automated Tests (Not Implemented Yet)
- **Backend:** pytest with coverage (`pytest tests/ --cov=app`)
- **Frontend:** Vitest (`npm test`)
- **E2E:** Playwright (`npx playwright test`)

## Deployment

### Production Targets
- **Backend:** Render.com (auto-deploy from `main`)
- **Frontend:** Vercel (auto-deploy from `main`)
- **Database:** Railway Postgres (already set up)

### Environment Variables (Production)
Backend needs:
- `DATABASE_URL` - Railway Postgres connection string
- `APP_SECRET_KEY` - For encryption key derivation (openssl rand -base64 32)
- `JWT_SECRET_KEY` - For signing JWTs (openssl rand -base64 32)
- `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET`
- `EPIC_CLIENT_ID` / `_SECRET`
- `OLLAMA_HOST` - URL to Ollama service

Frontend needs:
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_GOOGLE_OAUTH_CLIENT_ID`

## Documentation

Comprehensive docs in `docs/`:
- `architecture.md` - Full system design
- `security_architecture.md` - Threat model and encryption details
- `database_schema.md` - Complete ERD
- `api_endpoints.md` - REST API spec
- `deployment.md` - Production deployment guide

## Common Pitfalls

1. **Don't commit `.env`** - already in `.gitignore`, but verify
2. **STATE_STORE is in-memory** - will lose OAuth state on restart (use DB in prod)
3. **Epic tokens expire** - implement refresh_token flow for long-running sessions
4. **FHIR data is PHI** - always encrypt before storing
5. **Ollama runs separately** - must start `ollama serve` before testing AI features
6. **Docker host networking** - backend uses `host.docker.internal:11434` to reach Ollama

## Project Management with Jira

ContextVault uses Jira as the single source of truth for project management.

### Jira Project Details
- **Project Key:** KAN
- **Project URL:** https://davidjmorgan26.atlassian.net/jira/software/c/projects/KAN
- **Board:** KAN Scrum Board
- **GitHub Integration:** Enabled (commits with KAN-XX auto-link)

### Issue Hierarchy
- **Epics:** Large features spanning multiple sprints (11 epics)
- **Stories:** User-facing functionality (100+ stories)

### Common Jira Commands

**Migration (One-Time):**
```bash
python scripts/jira_migrate.py --dry-run  # Validate first
python scripts/jira_migrate.py            # Full migration
```

**Daily Queries:**
```bash
python scripts/jira_query.py --current-sprint    # See current sprint
python scripts/jira_query.py --backlog           # See backlog
python scripts/jira_query.py --epic KAN-1        # See epic stories
```

**Backup:**
```bash
python scripts/jira_export.py --output docs/archive/jira_backup.md
```

### Git Commit Convention

Link commits to Jira issues using issue key:
```bash
git commit -m "KAN-42: Add encryption service"
```

GitHub integration will automatically:
- Link commit to Jira issue KAN-42
- Show commit in issue activity
- Update issue status if using smart commits

### Smart Commits (Optional)
```bash
# Add comment to issue
git commit -m "KAN-42 #comment Fixed validation bug"

# Transition issue
git commit -m "KAN-42 #done Completed feature"
```

### Historical Documentation

**Archived (historical reference only):**
- `docs/archive/epics_features_stories.md` - Original planning (migrated 2025-01-26)
- `docs/archive/sprint_plan.md` - Original sprint plan (migrated 2025-01-26)

These files are frozen. All project management happens in Jira.

---

## Project Roadmap

### MVP (Current)
- [x] Epic SMART on FHIR OAuth + PKCE
- [x] Basic FHIR resource fetching (Patient, Observation)
- [ ] Google OAuth authentication
- [ ] Encrypted vault storage
- [ ] Local Ollama chat

### Phase 2
- [ ] File upload (PDF, images)
- [ ] Fitbit integration
- [ ] Apple Health import
- [ ] Vector embeddings for context retrieval

### Phase 3
- [ ] Mobile apps (React Native)
- [ ] End-to-end encryption (zero-knowledge)
- [ ] P2P device sync
