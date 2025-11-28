# Context Vault - AI Knowledge Index

**Project:** Context Vault
**Purpose:** Privacy-first personal intelligence system with encrypted vault + Epic MyChart integration
**Tech Stack:** Python (FastAPI), React (Next.js), PostgreSQL (Supabase), Ollama, Epic SMART on FHIR
**Knowledge Items**: 1 feature • 1 component • 1 pattern

---

## Recent Changes

> Last updated: 2025-11-28

### 2025-11-28
- ✅ **Added**: Backend foundation with async SQLAlchemy, Alembic migrations, models → [backend-setup](./knowledge/components/backend-foundation.md) (pending)
- ✅ **Added**: Google OAuth authentication with JWT tokens and sessions → [google-oauth-authentication](./knowledge/features/google-oauth-authentication.md)
- ✅ **Added**: Encryption service with AES-256-GCM and PBKDF2 key derivation → [encryption-service](./knowledge/components/encryption-service.md)
- 📝 **Added**: Multi-layer environment configuration pattern → [environment-configuration](./knowledge/patterns/environment-configuration.md)
- 🔧 **Fixed**: Backend startup issues (CORS parsing, database URL, NullPool config)

---

## Knowledge Base

### Features

- [Google OAuth Authentication](./knowledge/features/google-oauth-authentication.md) - User login with Google, JWT tokens, session management

### Components

- [Encryption Service](./knowledge/components/encryption-service.md) - AES-256-GCM encryption, PBKDF2 key derivation

### Patterns

- [Multi-Layer Environment Configuration](./knowledge/patterns/environment-configuration.md) - Three-layer .env structure for secrets and config

---

## Context Files

### Overview
- [.ai/context/overview.md](.ai/context/overview.md) - Project vision and architecture

### Decisions
- [.ai/context/decisions/](.ai/context/decisions/) - Technical decision records

---

## Quick Links

- Main docs: `docs/`
- Architecture: `docs/architecture.md`
- Security model: `docs/security_architecture.md`
- Database schema: `docs/database_schema.md`
- Current code: `fastapi_epic_smart.py` (MVP)
- Project guidance: `claude.md`

---

## How to Use This System

1. **Start here** - Read INDEX.md (this file) for recent changes
2. **Build features** - Follow patterns in `.ai/preferences/`
3. **Document work** - Run `/capture` after completing features
4. **Reference knowledge** - Check `.ai/knowledge/` before building similar features
