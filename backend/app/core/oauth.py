import httpx
from jose import jwt
from fastapi import HTTPException


async def fetch_oidc_config(issuer: str) -> dict:
    """Fetch OpenID Connect discovery configuration.

    Args:
        issuer: OIDC issuer URL (e.g., https://accounts.google.com)

    Returns:
        dict: OIDC configuration with endpoints

    Raises:
        HTTPException: If request fails
    """
    url = issuer.rstrip("/") + "/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        r.raise_for_status()
        return r.json()


async def fetch_jwks(jwks_uri: str) -> dict:
    """Fetch JSON Web Key Set for JWT signature validation.

    Args:
        jwks_uri: JWKS endpoint URL

    Returns:
        dict: JWKS with public keys

    Raises:
        HTTPException: If request fails
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(jwks_uri, timeout=10)
        r.raise_for_status()
        return r.json()


async def validate_id_token(
    id_token: str,
    jwks: dict,
    client_id: str,
    issuer: str,
    nonce: str | None = None
) -> dict:
    """Validate OIDC id_token signature and claims.

    Args:
        id_token: JWT id_token from OAuth provider
        jwks: JSON Web Key Set from provider
        client_id: OAuth client_id (validates audience claim)
        issuer: Expected issuer URL
        nonce: Expected nonce value (optional)

    Returns:
        dict: Decoded id_token claims

    Raises:
        HTTPException: If validation fails
    """
    try:
        # Decode and validate id_token
        claims = jwt.decode(
            id_token,
            jwks,
            audience=client_id,
            issuer=issuer,
            options={"verify_at_hash": False}
        )

        # Validate nonce if provided
        if nonce and claims.get("nonce") != nonce:
            raise ValueError("Nonce mismatch")

        return claims

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"id_token validation failed: {str(e)}"
        )
