# Context Vault - Project Overview

## Vision

A **privacy-first personal intelligence system** where users can:
- Securely store personal data (medical records, notes, files)
- Chat with AI about their data
- Never worry about data being leaked or misused

**Core Privacy Principle:** User data is encrypted at rest (AES-256-GCM) and AI processing happens in ephemeral containers that are destroyed immediately after use.

## Current Status (MVP)

**What exists:**
- `fastapi_epic_smart.py` - Epic SMART on FHIR OAuth2 + PKCE integration
- OAuth flow: `/login` → Epic auth → `/callback` → token exchange
- FHIR queries: `/patient`, `/observations`
- Comprehensive documentation in `docs/`

**What's planned:**
- Full FastAPI backend with encrypted vault storage
- React frontend (Vercel deployment)
- Google OAuth for primary authentication
- Ollama integration for local AI chat
- File uploads (PDF, images) with parsing

## Key Integrations

### Epic MyChart (SMART on FHIR)
- Sandbox: `open.epic.com` (currently configured)
- Production: Requires Epic App Orchard approval
- Scopes: `patient/Patient.read`, `patient/Observation.read`, `offline_access`
- OAuth: Authorization Code + PKCE (no client secret in public clients)

### Ollama (Local LLM)
- Model: `llama3.1:8b` (recommended for MVP)
- Deployment: Ephemeral Docker containers
- Security: tmpfs mounts (RAM-only), no persistent storage
- Access: `http://host.docker.internal:11434` from backend container

### Google OAuth
- Primary user authentication
- User's Google ID used in encryption key derivation (PBKDF2, 100k iterations)
- No Google has access to vault data

## Security Model

**Encryption:**
- All vault data: AES-256-GCM with user-specific keys
- Keys derived on-demand: `PBKDF2(Google_ID + APP_SECRET_KEY, 100k iterations)`
- Keys never stored, always ephemeral

**Threat Protection:**
- ✅ Database breach (data encrypted)
- ✅ Compromised backend (no keys stored)
- ✅ Container escape (no persistent data)
- ✅ Network sniffing (HTTPS/TLS 1.3)
- ✅ Token theft (30-min expiry + rotation)

**Out of Scope:**
- ❌ Compromised user device
- ❌ Compromised Google account
- ❌ Malicious code updates (trust required)

## Architecture Roadmap

### MVP
```
fastapi_epic_smart.py (standalone)
       ↓
Epic MyChart Sandbox
```

### Target
```
React Frontend (Vercel) ←→ FastAPI Backend (Render) ←→ PostgreSQL (Railway)
                                    ↓
                          Ephemeral Ollama Containers
```

## Development Principles

1. **Privacy First** - Always encrypt user data before storage
2. **Ephemeral Processing** - AI sees data in memory only, never persisted
3. **Minimal Trust** - Backend cannot decrypt without user session
4. **Standards-Based** - SMART on FHIR, OAuth2, OIDC, FHIR R4
5. **Developer Experience** - Clear docs, simple setup, fast iteration
