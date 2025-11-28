---
type: component
name: Encryption Service
status: implemented
created: 2025-11-28
updated: 2025-11-28
files:
  - backend/app/core/encryption.py
  - backend/app/models/user.py
related:
  - .ai/knowledge/features/google-oauth-authentication.md
tags: [encryption, security, aes-gcm, pbkdf2, cryptography]
---

# Encryption Service

## What It Does

Provides cryptographic functions for encrypting vault data at rest using AES-256-GCM and deriving user-specific master keys using PBKDF2-HMAC-SHA256. Ensures that vault content remains encrypted in the database and can only be decrypted with the user's derived key.

## How It Works

### Key Derivation (PBKDF2)

Each user gets a unique master encryption key derived from:
- **Password**: `google_id + APP_SECRET_KEY`
- **Salt**: Random 32-byte salt stored in `users.encryption_salt`
- **Iterations**: 100,000 (makes brute-force expensive)
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Output**: 32-byte (256-bit) key

```python
master_key = derive_master_key(google_id, encryption_salt_bytes)
```

**Critical**: Master keys are NEVER stored - always derived on-demand from user's Google ID and salt.

### Content Encryption (AES-256-GCM)

Uses authenticated encryption providing both confidentiality and integrity:

1. Generate random 12-byte nonce
2. Encrypt plaintext with AES-256-GCM
3. Include 16-byte authentication tag
4. Encode as Base64: `nonce || ciphertext || auth_tag`

```python
encrypted = encrypt_content("sensitive data", master_key)
# Returns: base64(12-byte nonce + ciphertext + 16-byte tag)
```

### Content Decryption

1. Decode Base64 string
2. Extract nonce (first 12 bytes)
3. Extract ciphertext + tag (remaining bytes)
4. Verify authentication tag (detects tampering)
5. Decrypt with master key
6. Return plaintext

```python
plaintext = decrypt_content(encrypted_b64, master_key)
# Raises EncryptionError if tampered or wrong key
```

### Key Files

- `backend/app/core/encryption.py:23` - `derive_master_key()` function
- `backend/app/core/encryption.py:61` - `encrypt_content()` function
- `backend/app/core/encryption.py:95` - `decrypt_content()` function
- `backend/app/core/encryption.py:126` - `hash_refresh_token()` for session tokens
- `backend/app/core/encryption.py:136` - `generate_encryption_salt()` helper

## Important Decisions

**Why AES-256-GCM?**
- **AES-256**: Industry standard, FIPS 140-2 approved, proven security
- **GCM mode**: Provides authentication (tamper detection) + encryption in one operation
- **Performance**: Hardware-accelerated on modern CPUs

**Why PBKDF2 with 100k iterations?**
- Makes brute-force attacks expensive (~100ms per attempt)
- NIST recommended for password-based key derivation
- Balance between security and UX (acceptable latency)

**Why derive keys on-demand vs storing?**
- **Zero-knowledge architecture**: Backend can't decrypt without user authentication
- **Database breach protection**: Encrypted data remains secure even if DB is compromised
- **Per-user isolation**: Each user's data encrypted with unique key

**Why unique salt per user?**
- Prevents rainbow table attacks
- Ensures different keys even if two users have same Google ID (impossible, but defense in depth)
- Generated once on account creation, stored in DB

## Usage Example

```python
from app.core.encryption import (
    derive_master_key,
    encrypt_content,
    decrypt_content,
    generate_encryption_salt
)

# New user signup
salt_hex = generate_encryption_salt()  # 64-char hex string
user.encryption_salt = salt_hex

# Later, when storing vault item
salt_bytes = bytes.fromhex(user.encryption_salt)
master_key = derive_master_key(user.google_id, salt_bytes)
encrypted = encrypt_content("My secret note", master_key)
vault_item.content_encrypted = encrypted

# When retrieving vault item
master_key = derive_master_key(user.google_id, salt_bytes)
plaintext = decrypt_content(vault_item.content_encrypted, master_key)
```

## Security Guarantees

### Confidentiality
- ✅ Vault content cannot be read without user's Google ID + app secret
- ✅ Different nonces ensure same plaintext produces different ciphertext
- ✅ AES-256 provides 128-bit security level (quantum-resistant for now)

### Integrity
- ✅ Authentication tag detects any modification to ciphertext
- ✅ Decrypt fails if data tampered with
- ✅ GCM provides both confidentiality and authenticity

### Threat Protection
- ✅ **Database breach**: Encrypted data useless without APP_SECRET_KEY
- ✅ **Compromised admin**: Cannot decrypt user data without Google authentication
- ✅ **Rainbow tables**: Unique salt per user prevents precomputed attacks
- ✅ **Brute force**: 100k PBKDF2 iterations make each attempt expensive

## Configuration

```bash
# In .env
APP_SECRET_KEY=your-random-256-bit-secret  # Required, keep secure!
PBKDF2_ITERATIONS=100000  # Default, adjust for security/performance balance
AES_KEY_SIZE=32  # 256 bits, do not change
```

## Testing

Key test cases needed:
- [ ] Encrypt → Decrypt returns original plaintext
- [ ] Decryption with wrong key raises EncryptionError
- [ ] Key derivation is deterministic (same inputs = same key)
- [ ] Different users get different keys (different salts)
- [ ] Nonces are unique across encryptions
- [ ] Tampering with ciphertext fails decryption (InvalidTag)
- [ ] Same plaintext encrypted twice produces different ciphertext

## Common Issues

### Issue: "Authentication tag verification failed"
**Cause**: Ciphertext was modified or wrong key used
**Solution**: Verify master key derivation uses correct google_id and salt

### Issue: Key derivation too slow (>500ms)
**Cause**: PBKDF2_ITERATIONS set too high or slow CPU
**Solution**: Reduce iterations (min 50,000) or optimize user flow to cache keys

### Issue: Encryption salt not found
**Cause**: User record missing or corrupted
**Solution**: Regenerate salt and re-encrypt user's vault (requires user re-authentication)

## Related Knowledge

- [Google OAuth Authentication](../features/google-oauth-authentication.md) - Provides google_id for key derivation
- [Vault Data Model](../components/vault-data-model.md) - Stores encrypted content
- [Session Management](../components/session-management.md) - Uses refresh token hashing

## API Reference

### `derive_master_key(google_id: str, encryption_salt: bytes) -> bytes`
Derives 32-byte master key using PBKDF2.

### `encrypt_content(plaintext: str, master_key: bytes) -> str`
Encrypts plaintext, returns Base64-encoded ciphertext.

### `decrypt_content(encrypted_b64: str, master_key: bytes) -> str`
Decrypts Base64-encoded ciphertext, returns plaintext.

### `hash_refresh_token(refresh_token: str) -> str`
Hashes refresh token with SHA-256 for storage.

### `generate_encryption_salt() -> str`
Generates random 32-byte salt as 64-char hex string.

## Future Improvements

- [ ] Support for key rotation (re-encrypt with new salt)
- [ ] Add AES-256-SIV mode for deterministic encryption (deduplication)
- [ ] Implement key caching in Redis (short TTL for performance)
- [ ] Add encrypted file chunking for large files
- [ ] Support for hardware security modules (HSM)
- [ ] Implement zero-knowledge password reset flow
- [ ] Add encryption performance metrics/monitoring
