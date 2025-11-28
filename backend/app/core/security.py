import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge.

    Returns:
        tuple[str, str]: (code_verifier, code_challenge)
    """
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("utf-8")).digest()
    ).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


def generate_state_token() -> str:
    """Generate cryptographically random state token for CSRF protection."""
    return secrets.token_urlsafe(32)


def generate_nonce() -> str:
    """Generate cryptographically random nonce for OIDC id_token validation."""
    return secrets.token_urlsafe(32)


def create_access_token(data: dict) -> str:
    """Create JWT access token.

    Args:
        data: Payload to encode (should include user_id, email)

    Returns:
        str: Signed JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_access_token(token: str) -> dict:
    """Verify and decode JWT access token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise


def create_refresh_token() -> str:
    """Generate opaque refresh token.

    Returns:
        str: Base64-encoded random 32-byte token
    """
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")


def hash_refresh_token(token: str) -> str:
    """Hash refresh token with SHA-256 for storage.

    Args:
        token: Refresh token string

    Returns:
        str: Hex-encoded SHA-256 hash
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
