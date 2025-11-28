---
type: feature
name: Google OAuth Authentication
status: implemented
created: 2025-11-28
updated: 2025-11-28
files:
  - backend/app/api/auth.py
  - backend/app/models/user.py
  - backend/app/models/session.py
  - backend/app/core/config.py
related:
  - .ai/knowledge/components/encryption-service.md
  - .ai/knowledge/patterns/environment-configuration.md
tags: [authentication, oauth, google, jwt, security]
---

# Google OAuth Authentication

## What It Does

Implements Google OAuth 2.0 authentication flow for user login and session management. Users sign in with their Google account, receive JWT access tokens and refresh tokens, and can maintain authenticated sessions across requests.

## How It Works

### Authentication Flow

1. **Login Initiation** (`/api/auth/google/login`)
   - Generates OAuth state parameter for CSRF protection
   - Redirects user to Google consent screen
   - Stores state temporarily for validation

2. **OAuth Callback** (`/api/auth/google/callback`)
   - Validates state parameter
   - Exchanges authorization code for Google tokens
   - Verifies id_token signature using Google's JWKS
   - Creates or retrieves user from database
   - Generates random 32-byte encryption_salt for new users
   - Creates session with hashed refresh_token
   - Returns access_token (30 min) and refresh_token (30 days)

3. **Token Refresh** (`/api/auth/refresh`)
   - Validates refresh_token hash in sessions table
   - Issues new access_token
   - Optionally rotates refresh_token for security

4. **User Profile** (`/api/auth/me`)
   - Validates Bearer token from Authorization header
   - Returns user profile (email, google_id, preferences)

5. **Logout** (`/api/auth/logout`)
   - Deletes session from database
   - Invalidates refresh_token

### Key Files

- `backend/app/api/auth.py:14` - FastAPI router with OAuth endpoints
- `backend/app/models/user.py:14` - User model with Google OAuth fields
- `backend/app/models/session.py:14` - Session model with refresh token hashing
- `backend/app/core/config.py:40` - Google OAuth configuration

### Database Schema

**Users Table:**
```python
id: UUID (primary key)
google_id: str (unique, indexed) - Google's user identifier
email: str (unique, indexed)
name: str (optional)
picture_url: str (optional)
encryption_salt: str (64 chars hex) - For deriving master encryption key
preferences: JSON - User settings
created_at, updated_at: timestamps
```

**Sessions Table:**
```python
id: UUID
user_id: UUID (foreign key to users)
refresh_token_hash: str (SHA-256 hash, indexed)
expires_at: timestamp (30 days default)
user_agent: str - Browser/client info
ip_address: inet - Client IP
created_at: timestamp
```

## Important Decisions

- **Why Google OAuth**: Eliminates password management, provides trusted identity verification, simplifies user onboarding
- **JWT for access tokens**: Stateless authentication, can be validated without database lookup, short-lived (30 min)
- **Hashed refresh tokens**: Never store refresh tokens in plaintext - protects against database breaches
- **Per-user encryption salt**: Each user gets unique random salt for PBKDF2 key derivation, generated on first login
- **Session tracking**: Enables multi-device logout, security auditing, and token rotation

## Usage Example

```python
# Frontend initiates login
window.location.href = "http://localhost:8000/api/auth/google/login"

# After OAuth callback, frontend receives tokens
const { access_token, refresh_token } = parseUrlParams()

# Use access token for API requests
const response = await fetch("/api/vault/items", {
  headers: {
    "Authorization": `Bearer ${access_token}`
  }
})

# Refresh when access token expires
const newToken = await fetch("/api/auth/refresh", {
  method: "POST",
  body: JSON.stringify({ refresh_token })
})
```

## Security Features

1. **CSRF Protection**: State parameter validation in OAuth callback
2. **Token Security**:
   - Access tokens expire in 30 minutes
   - Refresh tokens hashed with SHA-256
   - JWT signed with HS256 algorithm
3. **Encryption Salt**: Random 32-byte salt per user for vault encryption
4. **Session Auditing**: Stores user_agent and ip_address for security investigations
5. **JWKS Validation**: Verifies id_token signature against Google's public keys

## Environment Variables

```bash
# Required
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
```

## Testing

- Test files: `backend/tests/unit/test_auth.py` (planned)
- Integration tests: `backend/tests/integration/test_auth_api.py` (planned)
- Key test cases:
  - OAuth flow with valid state
  - OAuth flow with invalid state (CSRF)
  - Token refresh with valid/invalid refresh_token
  - Expired access token rejection
  - User profile retrieval
  - Logout invalidates session

## Common Issues

### Issue: "Invalid authorization header"
**Cause**: Missing "Bearer " prefix or malformed Authorization header
**Solution**: Ensure header format is `Authorization: Bearer <token>`

### Issue: Refresh token not found
**Cause**: Session was deleted (logout) or expired
**Solution**: Redirect user to login flow

### Issue: CORS errors on OAuth callback
**Cause**: Frontend URL not in CORS_ORIGINS
**Solution**: Add frontend URL to `_CORS_ORIGINS` in backend/.env

## Related Knowledge

- [Encryption Service](../components/encryption-service.md) - Uses encryption_salt from User model
- [Environment Configuration](../patterns/environment-configuration.md) - OAuth credentials setup
- [Session Management](../components/session-management.md) - Refresh token handling

## Future Improvements

- [ ] Implement token rotation on refresh
- [ ] Add support for multiple OAuth providers (GitHub, Microsoft)
- [ ] Implement "Remember me" functionality
- [ ] Add rate limiting on auth endpoints
- [ ] Support for OAuth scopes customization
- [ ] Add 2FA/MFA support
- [ ] Implement device fingerprinting
- [ ] Add session management UI (view/revoke sessions)
