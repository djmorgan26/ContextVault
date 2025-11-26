# Context Vault - Security Architecture

## Security Principles

1. **Privacy by Design**: User data never leaves their control
2. **Zero-Knowledge**: Backend cannot decrypt vault content without user session
3. **Ephemeral Processing**: AI processing happens in temporary containers that are destroyed
4. **Defense in Depth**: Multiple layers of encryption and security controls
5. **Least Privilege**: Services only have access to what they need
6. **Transparency**: User knows what data is stored and where

## Threat Model

### What We Protect Against

✅ **Database Breach**
- Vault content encrypted with user-specific keys
- Even with full database dump, attacker cannot decrypt user data
- OAuth tokens encrypted, refresh tokens hashed

✅ **Compromised Backend Server**
- Master keys never stored on server
- Derived on-demand from user's Google ID + app secret
- Attacker with server access still cannot decrypt vaults

✅ **Malicious Administrator**
- Database admin cannot decrypt user data
- No "master key" or "admin backdoor"
- User data is truly private

✅ **Container Escape (LLM)**
- Ephemeral containers with no persistent storage
- tmpfs mounts (RAM-only, wiped on destruction)
- Even if attacker escapes container, no data to steal

✅ **Network Sniffing**
- All communication over HTTPS/TLS 1.3
- Certificate pinning in mobile apps (future)
- No sensitive data in URLs or query parameters

✅ **Token Theft**
- Short-lived access tokens (30 min)
- Refresh tokens stored hashed (SHA-256)
- Token rotation on refresh

✅ **CSRF Attacks**
- State parameter in OAuth flows (cryptographically random)
- SameSite cookies for session management
- Double-submit cookie pattern for sensitive operations

✅ **SQL Injection**
- All queries use parameterized statements (SQLAlchemy ORM)
- Input validation with Pydantic
- No raw SQL concatenation

### What We Don't Protect Against (Out of Scope for MVP)

❌ **Compromised User Device**
- Malware on user's computer could intercept decrypted data
- Keyloggers could capture credentials
- Mitigation: Educate users on device security

❌ **Compromised Google Account**
- Attacker with Google OAuth access can authenticate as user
- Mitigation: Rely on Google's 2FA, suggest enabling it

❌ **Insider Threat (Application Developer)**
- Malicious code update could exfiltrate data
- Mitigation: Code review, open source portions, security audits

❌ **Quantum Computing Attacks**
- AES-256 currently quantum-resistant but future uncertain
- Mitigation: Monitor NIST post-quantum standards, plan migration path

❌ **Physical Server Access**
- Attacker with physical access to Render/Railway servers
- Mitigation: Trust cloud provider's physical security

❌ **Side-Channel Attacks**
- Timing attacks, spectre/meltdown on shared hardware
- Mitigation: Rely on cloud provider's isolation

## Encryption Architecture

### Key Hierarchy

```
┌─────────────────────────────────────────────────┐
│  App Secret Key (Environment Variable)          │
│  - Single secret for entire application         │
│  - 32-byte random value                         │
│  - NEVER committed to git                       │
│  - Rotated annually                             │
└─────────────────────┬───────────────────────────┘
                      │
                      │ + User's Google ID
                      │ + User's Salt (random 32 bytes)
                      ▼
┌─────────────────────────────────────────────────┐
│  User Master Key (Derived via PBKDF2)           │
│  - 32 bytes (256 bits)                          │
│  - 100,000 iterations SHA-256                   │
│  - Never stored, computed on-demand             │
│  - Unique per user                              │
└─────────────────────┬───────────────────────────┘
                      │
                      │ Used to encrypt...
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Vault    │  │  Vault    │  │  OAuth    │  │  File     │
│  Item 1   │  │  Item 2   │  │  Tokens   │  │  Storage  │
│  Content  │  │  Content  │  │           │  │           │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
  AES-256-GCM    AES-256-GCM    AES-256-GCM    AES-256-GCM
  Unique nonce   Unique nonce   Unique nonce   Unique nonce
```

### Key Derivation Function (PBKDF2)

**Implementation:**

```python
import hashlib
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_master_key(google_id: str, app_secret: str, salt: bytes) -> bytes:
    """
    Derive a user's master encryption key.

    Args:
        google_id: User's unique Google ID (from OAuth)
        app_secret: Application-wide secret key (from env)
        salt: User-specific 32-byte random salt (from database)

    Returns:
        32-byte master key for AES-256
    """
    # Combine Google ID and app secret as password
    password = f"{google_id}{app_secret}".encode('utf-8')

    # PBKDF2 with SHA-256, 100k iterations
    kdf = PBKDF2HMAC(
        algorithm=hashlib.sha256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    return kdf.derive(password)
```

**Why PBKDF2?**
- Industry standard (NIST recommended)
- Slow by design (100k iterations) to resist brute force
- Better than plain hashing (prevents rainbow tables)

**Why 100,000 iterations?**
- OWASP recommends 100k+ for PBKDF2-SHA256
- Balance between security and performance
- Takes ~100ms on modern CPU (acceptable UX)

**Salt Storage:**
- 32-byte random salt generated on user creation
- Stored in `users.encryption_salt` (plain text, not sensitive)
- Prevents identical keys for users with same Google ID on different instances

### Content Encryption (AES-256-GCM)

**Algorithm:** AES-256 in Galois/Counter Mode (GCM)

**Why AES-256-GCM?**
- **Confidentiality**: Data is encrypted
- **Authenticity**: Detects tampering via auth tag
- **Performance**: Hardware-accelerated (AES-NI)
- **Standard**: NIST approved, widely audited

**Implementation:**

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

def encrypt_content(plaintext: str, master_key: bytes) -> str:
    """
    Encrypt content using AES-256-GCM.

    Args:
        plaintext: Data to encrypt
        master_key: 32-byte master key

    Returns:
        Base64-encoded: nonce || ciphertext || auth_tag
    """
    # Initialize AES-GCM cipher
    aesgcm = AESGCM(master_key)

    # Generate random 96-bit nonce (MUST be unique per encryption)
    nonce = os.urandom(12)

    # Encrypt and authenticate
    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext_with_tag = aesgcm.encrypt(
        nonce=nonce,
        data=plaintext_bytes,
        associated_data=None  # Could add item_id for binding
    )

    # Format: nonce (12 bytes) || ciphertext || auth_tag (16 bytes)
    encrypted = nonce + ciphertext_with_tag

    # Base64 encode for database storage
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_content(encrypted_b64: str, master_key: bytes) -> str:
    """
    Decrypt content using AES-256-GCM.

    Args:
        encrypted_b64: Base64-encoded encrypted data
        master_key: 32-byte master key

    Returns:
        Decrypted plaintext

    Raises:
        InvalidTag: If authentication fails (tampering detected)
    """
    # Decode base64
    encrypted = base64.b64decode(encrypted_b64)

    # Extract nonce and ciphertext
    nonce = encrypted[:12]
    ciphertext_with_tag = encrypted[12:]

    # Initialize cipher
    aesgcm = AESGCM(master_key)

    # Decrypt and verify auth tag
    try:
        plaintext_bytes = aesgcm.decrypt(
            nonce=nonce,
            data=ciphertext_with_tag,
            associated_data=None
        )
        return plaintext_bytes.decode('utf-8')
    except Exception as e:
        # Invalid auth tag = tampering or wrong key
        raise ValueError("Decryption failed: data may be corrupted or tampered") from e
```

**Nonce Requirements:**
- MUST be unique for each encryption with same key
- 96 bits (12 bytes) for GCM
- Random generation via `os.urandom()` (cryptographically secure)
- Collision probability negligible (2^96 possible values)

**Auth Tag:**
- 128 bits (16 bytes)
- Automatically included in `ciphertext_with_tag` by AESGCM
- Verifies ciphertext integrity and authenticity
- Prevents tampering and chosen-ciphertext attacks

### File Encryption

**Process:**

1. User uploads file (e.g., medical_report.pdf)
2. Backend extracts text content (if applicable)
3. Encrypt file with AES-256-GCM (same as vault items)
4. Store encrypted file: `/data/uploads/{user_id}/{file_id}.enc`
5. Store metadata in database (encrypted JSON with original filename, size, etc.)

**Implementation:**

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_file(file_path: str, master_key: bytes, output_path: str):
    """
    Encrypt a file using AES-256-GCM.

    Args:
        file_path: Path to original file
        master_key: 32-byte master key
        output_path: Path to save encrypted file
    """
    aesgcm = AESGCM(master_key)
    nonce = os.urandom(12)

    # Read file
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    # Encrypt
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)

    # Write: nonce || ciphertext || tag
    with open(output_path, 'wb') as f:
        f.write(nonce)
        f.write(ciphertext_with_tag)

def decrypt_file(encrypted_path: str, master_key: bytes, output_path: str):
    """
    Decrypt a file using AES-256-GCM.

    Args:
        encrypted_path: Path to encrypted file
        master_key: 32-byte master key
        output_path: Path to save decrypted file
    """
    aesgcm = AESGCM(master_key)

    # Read encrypted file
    with open(encrypted_path, 'rb') as f:
        nonce = f.read(12)
        ciphertext_with_tag = f.read()

    # Decrypt
    plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

    # Write decrypted file
    with open(output_path, 'wb') as f:
        f.write(plaintext)
```

**File Size Considerations:**
- GCM can handle files up to ~64 GB (2^36 - 32 bytes)
- For MVP, limit uploads to 10 MB
- Future: Stream encryption/decryption for large files

### Token Encryption

**OAuth Tokens Storage:**

OAuth tokens (Epic, Fitbit) are sensitive and must be encrypted.

**Implementation:**

```python
def encrypt_token(token: str, master_key: bytes) -> str:
    """Same as encrypt_content()"""
    return encrypt_content(token, master_key)

def decrypt_token(encrypted_token: str, master_key: bytes) -> str:
    """Same as decrypt_content()"""
    return decrypt_content(encrypted_token, master_key)
```

**Refresh Token Hashing:**

Refresh tokens for user sessions are hashed (one-way), not encrypted.

```python
import hashlib

def hash_refresh_token(token: str) -> str:
    """
    Hash refresh token for database storage.

    Args:
        token: Raw refresh token (32-byte random)

    Returns:
        SHA-256 hash (hex encoded)
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()
```

**Why hash instead of encrypt?**
- Refresh tokens don't need to be decrypted (only validated)
- Hashing prevents token theft even if database is compromised
- Following OAuth best practices (RFC 6749)

## Authentication & Authorization

### Google OAuth 2.0 Flow

**Step-by-Step:**

```
1. User clicks "Sign in with Google"
   Frontend → Backend: GET /api/auth/google/login

2. Backend generates state (CSRF protection)
   state = secrets.token_urlsafe(32)
   store in Redis with 5-min TTL

3. Backend redirects to Google OAuth
   https://accounts.google.com/o/oauth2/v2/auth?
     client_id={GOOGLE_CLIENT_ID}&
     redirect_uri={BACKEND_URL}/api/auth/google/callback&
     response_type=code&
     scope=openid%20email%20profile&
     state={state}

4. User authorizes on Google, redirected back
   GET /api/auth/google/callback?code={auth_code}&state={state}

5. Backend validates state (prevent CSRF)
   verify state exists in Redis and matches

6. Backend exchanges code for tokens
   POST https://oauth2.googleapis.com/token
   {
     code: {auth_code},
     client_id: {GOOGLE_CLIENT_ID},
     client_secret: {GOOGLE_CLIENT_SECRET},
     redirect_uri: {BACKEND_URL}/api/auth/google/callback,
     grant_type: authorization_code
   }

   Response: {access_token, id_token, expires_in}

7. Backend verifies id_token (JWT)
   - Verify signature using Google's JWKS
   - Verify issuer = https://accounts.google.com
   - Verify audience = GOOGLE_CLIENT_ID
   - Verify expiration

8. Backend extracts user info from id_token
   {
     sub: "google_user_id",
     email: "user@example.com",
     name: "John Doe",
     picture: "https://..."
   }

9. Backend creates or retrieves user
   - If new: generate encryption salt, create user record
   - If existing: update profile if changed

10. Backend generates app tokens
    access_token = JWT(user_id, email, exp=30min)
    refresh_token = secrets.token_urlsafe(32)

11. Backend stores refresh token (hashed)
    INSERT INTO sessions (user_id, refresh_token_hash, expires_at)

12. Backend returns tokens to frontend
    {
      access_token,
      refresh_token,
      token_type: "bearer",
      expires_in: 1800,
      user: {...}
    }
```

**Security Controls:**
- **State parameter**: Prevents CSRF attacks
- **HTTPS only**: Tokens never sent over plain HTTP
- **Short-lived access token**: 30 minutes (limits exposure)
- **Refresh token rotation**: New refresh token issued on each refresh
- **Token binding**: Refresh token tied to user_id and session_id

### JWT Access Token

**Payload:**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1643125800,
  "exp": 1643127600
}
```

**Signing:**

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str, email: str) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User's UUID
        email: User's email

    Returns:
        Signed JWT token
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }

    return jwt.encode(
        payload,
        key=settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )
```

**Verification:**

```python
from jose import jwt, JWTError
from fastapi import HTTPException, status

def verify_access_token(token: str) -> dict:
    """
    Verify JWT access token.

    Args:
        token: JWT token from Authorization header

    Returns:
        Decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

**Token Storage (Frontend):**

```typescript
// NEVER store in localStorage (vulnerable to XSS)
// Store in memory (React state) or HttpOnly cookie

// Option 1: Memory (preferred for SPA)
const [accessToken, setAccessToken] = useState<string | null>(null);

// Option 2: HttpOnly cookie (set by backend)
// More secure but requires SameSite=Strict and CSRF protection
```

### Authorization Middleware

**FastAPI Dependency:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user.

    Usage:
        @app.get("/api/vault/items")
        async def get_items(user: User = Depends(get_current_user)):
            # user is authenticated
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    user = await get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

**Per-Endpoint Authorization:**

```python
@app.get("/api/vault/items/{item_id}")
async def get_vault_item(
    item_id: str,
    user: User = Depends(get_current_user)
):
    """Get vault item (with ownership check)."""
    item = await get_vault_item_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Authorization check: user must own this item
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return item
```

## Ephemeral Container Security

### Container Isolation

**Docker Security Configuration:**

```python
container = client.containers.run(
    image="ollama/ollama:latest",
    detach=True,
    remove=True,  # Auto-remove on stop

    # Resource limits
    mem_limit="4g",
    memswap_limit="4g",  # No swap (prevent disk writes)
    cpu_quota=200000,  # 2 CPUs

    # Network isolation
    network_mode="bridge",  # Isolated network
    dns=[],  # No DNS (no internet access)

    # Filesystem
    tmpfs={"/tmp": "size=2g"},  # RAM-only tmpfs
    read_only=True,  # Root filesystem read-only

    # Security
    cap_drop=["ALL"],  # Drop all capabilities
    security_opt=["no-new-privileges"],
    user="nobody",  # Non-root user

    # Environment
    environment={
        "OLLAMA_HOST": "0.0.0.0:11434",
        "OLLAMA_MODELS": "/tmp/models"  # tmpfs (RAM)
    }
)
```

**Why these settings?**

- **`mem_limit` + `memswap_limit`**: Prevent memory exhaustion and swap (no disk writes)
- **`tmpfs`**: All file operations in RAM, wiped on container stop
- **`read_only=True`**: Root filesystem immutable (prevents malicious writes)
- **`cap_drop=ALL`**: Drop all Linux capabilities (minimize attack surface)
- **`no-new-privileges`**: Prevent privilege escalation
- **`user=nobody`**: Run as unprivileged user (UID 65534)
- **No DNS/Internet**: Container cannot exfiltrate data

### Container Lifecycle

**Creation:**

```python
from docker import DockerClient
import uuid

client = DockerClient.from_env()

def create_ephemeral_llm_container():
    """Create isolated LLM container."""
    container_id = f"vault-llm-{uuid.uuid4().hex[:8]}"

    container = client.containers.run(
        image="ollama/ollama:latest",
        name=container_id,
        detach=True,
        # ... security config above ...
    )

    # Wait for Ollama to start (max 5 seconds)
    # ...

    return container
```

**Usage:**

```python
async def chat_with_llm(prompt: str, context: str):
    """Process chat request with ephemeral container."""
    container = create_ephemeral_llm_container()

    try:
        # Send request to Ollama API inside container
        response = await httpx.post(
            f"http://{container.attrs['NetworkSettings']['IPAddress']}:11434/api/generate",
            json={
                "model": "llama3.1:8b",
                "prompt": f"{context}\n\nUser: {prompt}\nAssistant:",
                "stream": True
            },
            timeout=60.0
        )

        # Stream response back to user
        async for chunk in response.aiter_bytes():
            yield chunk

    finally:
        # ALWAYS destroy container (even if exception)
        try:
            container.stop(timeout=1)
            container.remove(force=True)
        except Exception as e:
            logger.error(f"Failed to cleanup container: {e}")
```

**Destruction:**

```python
def destroy_container(container):
    """Forcefully destroy container."""
    try:
        # Stop (sends SIGTERM, then SIGKILL after timeout)
        container.stop(timeout=1)

        # Remove (deletes all container data)
        container.remove(force=True)

    except docker.errors.NotFound:
        # Already destroyed
        pass
    except Exception as e:
        logger.error(f"Container cleanup failed: {e}")
        # Escalate to manual cleanup job
```

**Cleanup Job (Cron):**

```python
# Run every 5 minutes to catch orphaned containers
@cron("*/5 * * * *")
def cleanup_orphaned_containers():
    """Remove any containers older than 10 minutes."""
    client = DockerClient.from_env()

    for container in client.containers.list():
        if not container.name.startswith("vault-llm-"):
            continue

        # Check age
        created_at = container.attrs["Created"]
        age = datetime.now() - datetime.fromisoformat(created_at.rstrip('Z'))

        if age > timedelta(minutes=10):
            logger.warning(f"Destroying orphaned container: {container.name}")
            container.remove(force=True)
```

### Data Flow Security

**No Persistent Storage:**

```
User's vault data → Backend decrypts → Builds prompt with context
                                             ↓
                          Ephemeral container receives prompt
                                             ↓
                          LLM processes in RAM (no disk writes)
                                             ↓
                          Response streamed back to backend
                                             ↓
                          Container destroyed (RAM wiped)
```

**Key Points:**
- Vault data never written to container's disk
- All processing in RAM (tmpfs)
- Container destroyed after single request
- No logs of vault content

## Additional Security Measures

### HTTPS/TLS

**Certificate Management:**
- Vercel: Automatic Let's Encrypt certificates
- Render: Automatic SSL for custom domains
- Force HTTPS redirects (no plain HTTP)

**TLS Configuration:**
- Minimum TLS 1.2 (prefer TLS 1.3)
- Strong cipher suites only (no RC4, 3DES)
- HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### CORS Configuration

**FastAPI Setup:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev
        "https://contextvault.vercel.app"  # Prod
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600  # Cache preflight for 1 hour
)
```

### Rate Limiting

**Implementation (SlowAPI):**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("20/minute")
async def chat(request: Request, ...):
    """Chat endpoint with rate limit."""
    ...
```

**Limits:**
- Auth endpoints: 10/minute
- Vault CRUD: 100/minute
- Chat: 20/minute
- File upload: 10/minute
- Integration sync: 5/hour

### Input Validation

**Pydantic Schemas:**

```python
from pydantic import BaseModel, Field, validator

class VaultItemCreate(BaseModel):
    type: str = Field(..., regex="^(note|file|medical_record|preference|measurement|other)$")
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=1048576)  # 1MB
    tags: list[str] = Field(default=[], max_items=10)

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tag names."""
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Tag name too long (max 50 chars)")
            if not tag.isalnum() and not any(c in tag for c in ['-', '_']):
                raise ValueError("Tag must be alphanumeric or contain - or _")
        return v
```

### Logging Security

**What to Log:**
- Authentication events (login, logout, refresh)
- Failed authentication attempts
- Authorization failures (403 errors)
- API errors (500 errors)
- Integration sync events

**What NOT to Log:**
- Vault content (encrypted or decrypted)
- OAuth tokens
- User passwords or encryption keys
- Full request bodies (may contain sensitive data)

**Log Sanitization:**

```python
import logging

def sanitize_log(message: dict) -> dict:
    """Remove sensitive fields from log messages."""
    sensitive_keys = [
        'password', 'token', 'access_token', 'refresh_token',
        'content', 'content_encrypted', 'authorization'
    ]

    return {
        k: '***REDACTED***' if k.lower() in sensitive_keys else v
        for k, v in message.items()
    }

logger.info(sanitize_log(request_data))
```

### Security Headers

**FastAPI Middleware:**

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection
        response.headers["X-Content-Type-Options"] = "nosniff"

        # HSTS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # CSP (Content Security Policy)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

app.add_middleware(SecurityHeadersMiddleware)
```

## Security Auditing

### Automated Scanning

**Dependency Scanning:**
```bash
# Python
pip install safety
safety check

# Node.js
npm audit
```

**SAST (Static Analysis):**
```bash
# Python
pip install bandit
bandit -r app/

# TypeScript
npm install --save-dev eslint-plugin-security
```

### Manual Security Review

**Before Production:**
- [ ] All secrets in environment variables (not hardcoded)
- [ ] Database credentials rotated from defaults
- [ ] OAuth redirect URIs whitelisted
- [ ] HTTPS enforced everywhere
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] SQL injection testing (use SQLMap)
- [ ] XSS testing (use OWASP ZAP)
- [ ] CSRF protection verified
- [ ] Container isolation tested
- [ ] Encryption tested (encrypt/decrypt cycle)
- [ ] Token expiration tested
- [ ] Error messages don't leak sensitive info

### Penetration Testing (Future)

**Recommended Tools:**
- OWASP ZAP (automated vulnerability scanning)
- Burp Suite (manual testing)
- SQLMap (SQL injection)
- Nmap (network scanning)

**Scope:**
- API authentication bypass
- Authorization flaws (access other users' data)
- Container escape attempts
- Database injection
- XSS and CSRF
- Token theft and replay

## Incident Response Plan

### Security Incident Classification

**Critical (P0):**
- Database breach with encrypted data exposed
- OAuth token theft
- Container escape with data exfiltration
- Authentication bypass

**High (P1):**
- Denial of service attack
- Rate limiting bypass
- Failed login brute force

**Medium (P2):**
- Suspicious API usage patterns
- Integration errors
- Failed container cleanup

### Response Procedure

**1. Detection:**
- Monitor logs for anomalies (use Sentry or similar)
- Set up alerts for failed auth attempts (>10/minute)
- Monitor container lifecycle (orphaned containers)

**2. Containment:**
- Revoke compromised OAuth tokens
- Invalidate all user sessions (force re-login)
- Block suspicious IP addresses
- Take affected services offline if needed

**3. Investigation:**
- Review access logs
- Identify affected users
- Determine attack vector
- Assess data exposure

**4. Recovery:**
- Patch vulnerability
- Rotate secrets (app secret, database password)
- Notify affected users
- Restore from backup if needed

**5. Post-Mortem:**
- Document incident timeline
- Implement additional controls
- Update threat model
- Security training for team

## Compliance Considerations

### GDPR (General Data Protection Regulation)

**User Rights:**
- ✅ Right to access: `GET /api/vault/export`
- ✅ Right to deletion: `DELETE /api/auth/me?delete_all=true`
- ✅ Right to portability: JSON export of all data
- ✅ Consent: OAuth consent screen
- ✅ Data minimization: Only collect necessary data

### HIPAA (Health Insurance Portability and Accountability Act)

**Requirements for Epic Integration:**
- ✅ Encryption at rest (vault items, OAuth tokens)
- ✅ Encryption in transit (HTTPS)
- ✅ Access controls (authentication + authorization)
- ✅ Audit logging (all data access logged)
- ✅ Data integrity (AES-GCM auth tags)
- ⚠️  Business Associate Agreement (BAA) with Epic
- ⚠️  BAA with hosting providers (Render, Railway)

**Note:** Full HIPAA compliance requires legal review and formal BAAs. MVP may not be HIPAA-compliant until these are in place.

### SOC 2 (Future)

**Security Controls:**
- Access control (authentication, authorization)
- Change management (git, code review)
- Risk management (threat model, incident response)
- Monitoring (logging, alerts)

## Security Roadmap

### MVP (Phase 1)
- ✅ Google OAuth authentication
- ✅ AES-256-GCM encryption
- ✅ PBKDF2 key derivation
- ✅ Ephemeral LLM containers
- ✅ HTTPS everywhere
- ✅ Input validation
- ✅ Rate limiting

### Phase 2
- End-to-end encryption (zero-knowledge)
- Hardware security key support (WebAuthn)
- Audit logs (user-visible)
- Security dashboard (failed logins, active sessions)
- Automated secret rotation

### Phase 3
- SOC 2 certification
- Penetration testing
- Bug bounty program
- Security training for users
- Compliance automation

---

**Next Steps:**
1. Implement encryption service (see code examples above)
2. Set up Google OAuth (credentials ready)
3. Configure Docker container security
4. Add security headers middleware
5. Test encryption/decryption cycle
