---
type: pattern
name: Multi-Layer Environment Configuration
status: implemented
created: 2025-11-28
updated: 2025-11-28
files:
  - .env
  - backend/.env
  - frontend/.env
  - backend/app/core/config.py
related:
  - .ai/knowledge/features/google-oauth-authentication.md
tags: [configuration, environment-variables, pydantic, secrets]
---

# Multi-Layer Environment Configuration

## What It Is

A three-layer environment variable structure separating shared secrets, backend config, and frontend config into separate `.env` files with clear responsibilities.

## How It Works

### File Structure

```
├── .env                    # Root: Shared secrets
├── .env.example            # Root: Template (no secrets)
├── backend/
│   ├── .env                # Backend: App-specific config
│   └── .env.example        # Backend: Template
└── frontend/
    ├── .env                # Frontend: App-specific config
    └── .env.example        # Frontend: Template
```

### Layer 1: Root `.env` (Shared Secrets)

**Purpose**: Store sensitive secrets shared across backend, frontend, and scripts

**Contents**:
- Security keys (APP_SECRET_KEY, JWT_SECRET_KEY)
- Database credentials (DATABASE_URL, Supabase keys)
- OAuth secrets (GOOGLE_OAUTH_CLIENT_SECRET, EPIC_CLIENT_ID)
- API tokens (JIRA_API_TOKEN)

**Why**: Single source of truth for secrets, easier to rotate, prevents duplication

### Layer 2: Backend `.env` (Backend Config)

**Purpose**: Backend-specific configuration (no secrets)

**Contents**:
- App settings (APP_NAME, DEBUG, ENVIRONMENT)
- Service URLs (OLLAMA_HOST, EPIC_REDIRECT_URI)
- Feature flags (CORS_ORIGINS, MAX_UPLOAD_SIZE_MB)
- Algorithm choices (JWT_ALGORITHM, PBKDF2_ITERATIONS)

**Loading**: Pydantic Settings loads from both root and backend `.env`:
```python
model_config = SettingsConfigDict(
    env_file=("../.env", ".env"),  # Root first, then backend
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)
```

### Layer 3: Frontend `.env` (Frontend Config)

**Purpose**: Frontend-specific configuration

**Contents**:
- Public environment variables (prefixed with `NEXT_PUBLIC_` or `VITE_`)
- API base URL (NEXT_PUBLIC_API_URL)
- Feature flags (NEXT_PUBLIC_DEBUG_MODE)

**Why separate**: Frontend has different build process, needs public vs private separation

## Important Decisions

**Why three layers instead of one?**
- **Separation of concerns**: Secrets vs config vs public variables
- **Security**: Easier to audit what's committed (only .example files)
- **Deployment**: Different .env files for different services (Vercel, Render, Railway)

**Why Pydantic Settings?**
- **Type validation**: Catches missing/invalid env vars at startup
- **Auto-loading**: Automatically reads .env files
- **Defaults**: Provides sensible defaults for optional vars
- **IDE support**: Type hints enable autocomplete

**Why load root + backend in order?**
- Backend .env can override root values if needed
- Secrets in root, config in backend - clear hierarchy
- Avoids circular dependencies

## Usage Example

### Root `.env` (Secrets)
```bash
APP_SECRET_KEY=Rf44YnyzBCWM/9bPLvd+mgCaFzM4XuR9oMtdPSCHatc=
JWT_SECRET_KEY=9P9IBPM1K096x8xK5mXnDNMxJBefmqUuMnPP760wptc=
DATABASE_URL=postgres://user:pass@host:5432/db
GOOGLE_OAUTH_CLIENT_ID=693092401672-xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxx
```

### Backend `.env` (Config)
```bash
APP_NAME=ContextVault
DEBUG=True
ENVIRONMENT=development
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:5173
OLLAMA_HOST=http://localhost:11434
```

### Frontend `.env` (Config)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEBUG_MODE=false
```

### Backend Config Loading
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),  # Load both
    )

    # From root .env
    APP_SECRET_KEY: str
    DATABASE_URL: str

    # From backend .env
    APP_NAME: str = "ContextVault"
    DEBUG: bool = False

settings = Settings()  # Auto-loads from both files
```

## Validation Patterns

### Comma-Separated Lists

**Problem**: Pydantic tries to parse `list[str]` as JSON, fails on comma-separated strings

**Solution**: Use property pattern
```python
# Store as string, parse to list
_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

@property
def CORS_ORIGINS(self) -> list[str]:
    return [origin.strip() for origin in self._CORS_ORIGINS.split(",")]
```

### Database URL Conversion

**Problem**: Supabase uses `postgres://` but asyncpg needs `postgresql+asyncpg://`

**Solution**: Transform on load
```python
database_url = settings.get_database_url()
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
```

## Configuration Best Practices

### DO:
- ✅ Keep secrets in root .env (never commit)
- ✅ Keep .env.example files updated (commit these)
- ✅ Use environment-specific values (dev vs prod)
- ✅ Validate required variables at startup
- ✅ Provide sensible defaults for optional vars

### DON'T:
- ❌ Commit .env files (add to .gitignore)
- ❌ Store secrets in .env.example files
- ❌ Hardcode secrets in source code
- ❌ Use same secrets for dev and prod
- ❌ Mix frontend and backend env vars

## Environment-Specific Config

### Development
```bash
# backend/.env
DEBUG=True
ENVIRONMENT=development
_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:5173
```

### Production
```bash
# backend/.env
DEBUG=False
ENVIRONMENT=production
_CORS_ORIGINS=https://contextvault.vercel.app
GOOGLE_OAUTH_REDIRECT_URI=https://api.contextvault.com/api/auth/google/callback
```

## Common Issues

### Issue: "Field required" error on startup
**Cause**: Missing required environment variable
**Solution**: Check root .env and backend .env have all required vars

### Issue: Frontend can't access backend env vars
**Cause**: Trying to use non-public vars in Next.js
**Solution**: Prefix with NEXT_PUBLIC_ or move to backend API

### Issue: CORS_ORIGINS parsing fails
**Cause**: Trying to parse as JSON instead of comma-separated string
**Solution**: Use property pattern (see Validation Patterns above)

## Security Checklist

- [ ] .env files in .gitignore
- [ ] .env.example has no real secrets
- [ ] Production secrets different from dev
- [ ] APP_SECRET_KEY is 256-bit random (openssl rand -base64 32)
- [ ] JWT_SECRET_KEY is 256-bit random
- [ ] DATABASE_URL includes SSL mode (sslmode=require)
- [ ] Rotate secrets annually or on breach

## Related Knowledge

- [Google OAuth Authentication](../features/google-oauth-authentication.md) - Uses OAuth credentials
- [Encryption Service](../components/encryption-service.md) - Uses APP_SECRET_KEY

## Future Improvements

- [ ] Add .env.test for testing environment
- [ ] Implement secret rotation scripts
- [ ] Add vault support (HashiCorp Vault, AWS Secrets Manager)
- [ ] Environment variable validation on deploy
- [ ] Automated .env.example generation from .env
