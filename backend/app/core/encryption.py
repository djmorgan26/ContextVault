"""
Encryption service for vault data.

Implements AES-256-GCM for content encryption and PBKDF2 for key derivation.
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

from app.core.config import settings


class EncryptionError(Exception):
    """Raised when encryption or decryption fails."""
    pass


def derive_master_key(google_id: str, encryption_salt: bytes) -> bytes:
    """
    Derive user's master encryption key from Google ID and app secret.

    The key is derived using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    This makes brute-force attacks computationally expensive.

    Args:
        google_id: User's Google ID from OAuth
        encryption_salt: User's random salt (32 bytes from users.encryption_salt)

    Returns:
        32-byte master key for AES-256

    Raises:
        EncryptionError: If key derivation fails
    """
    try:
        # Combine Google ID with app secret as password
        password = (google_id + settings.APP_SECRET_KEY).encode('utf-8')

        # Configure PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashlib.sha256(),
            length=settings.AES_KEY_SIZE,  # 32 bytes = 256 bits
            salt=encryption_salt,
            iterations=settings.PBKDF2_ITERATIONS,  # 100,000
            backend=default_backend()
        )

        # Derive key
        master_key = kdf.derive(password)
        return master_key

    except Exception as e:
        raise EncryptionError(f"Failed to derive master key: {str(e)}")


def encrypt_content(plaintext: str, master_key: bytes) -> str:
    """
    Encrypt content using AES-256-GCM.

    AES-GCM provides authenticated encryption, meaning it protects both
    confidentiality and integrity. Any tampering with the ciphertext
    will be detected during decryption.

    Args:
        plaintext: Data to encrypt
        master_key: 32-byte master key from derive_master_key()

    Returns:
        Base64-encoded string: nonce||ciphertext||auth_tag

    Raises:
        EncryptionError: If encryption fails
    """
    try:
        # Initialize AES-GCM cipher
        aesgcm = AESGCM(master_key)

        # Generate random 12-byte nonce (96 bits, recommended for GCM)
        nonce = os.urandom(12)

        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')

        # Encrypt and authenticate
        # GCM mode returns: ciphertext || 16-byte authentication tag
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, associated_data=None)

        # Combine: nonce || ciphertext || tag
        encrypted = nonce + ciphertext

        # Encode as base64 for storage
        return base64.b64encode(encrypted).decode('utf-8')

    except Exception as e:
        raise EncryptionError(f"Failed to encrypt content: {str(e)}")


def decrypt_content(encrypted_b64: str, master_key: bytes) -> str:
    """
    Decrypt content using AES-256-GCM.

    Verifies the authentication tag before decryption. If the tag is invalid
    (data was tampered with), raises EncryptionError.

    Args:
        encrypted_b64: Base64-encoded encrypted data
        master_key: 32-byte master key from derive_master_key()

    Returns:
        Decrypted plaintext string

    Raises:
        EncryptionError: If decryption fails or authentication tag is invalid
    """
    try:
        # Decode from base64
        encrypted = base64.b64decode(encrypted_b64)

        # Extract nonce (first 12 bytes)
        nonce = encrypted[:12]

        # Extract ciphertext + tag (remaining bytes)
        ciphertext = encrypted[12:]

        # Initialize AES-GCM cipher
        aesgcm = AESGCM(master_key)

        # Decrypt and verify authentication tag
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

        # Convert bytes to string
        return plaintext_bytes.decode('utf-8')

    except InvalidTag:
        raise EncryptionError("Authentication tag verification failed. Data may have been tampered with.")
    except Exception as e:
        raise EncryptionError(f"Failed to decrypt content: {str(e)}")


def hash_refresh_token(refresh_token: str) -> str:
    """
    Hash refresh token for secure storage.

    Uses SHA-256 to create a one-way hash. The original token cannot be
    recovered from the hash, protecting users if the database is breached.

    Args:
        refresh_token: Raw refresh token

    Returns:
        Hex-encoded SHA-256 hash (64 characters)
    """
    token_bytes = refresh_token.encode('utf-8')
    hash_bytes = hashlib.sha256(token_bytes).digest()
    return hash_bytes.hex()


def generate_encryption_salt() -> str:
    """
    Generate a random salt for PBKDF2 key derivation.

    Returns:
        Hex-encoded 32-byte salt (64 characters)
    """
    salt_bytes = os.urandom(32)
    return salt_bytes.hex()


def verify_decryption(plaintext: str, encrypted: str, master_key: bytes) -> bool:
    """
    Verify that encryption is working correctly.

    Encrypts plaintext and checks if it can be decrypted back to original.

    Args:
        plaintext: Original text
        encrypted: Encrypted version
        master_key: Master encryption key

    Returns:
        True if encryption/decryption round-trip works
    """
    try:
        decrypted = decrypt_content(encrypted, master_key)
        return decrypted == plaintext
    except EncryptionError:
        return False
