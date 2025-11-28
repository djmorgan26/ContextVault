from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from jose import JWTError

from app.config import settings
from app.core.security import (
    generate_pkce_pair,
    generate_state_token,
    generate_nonce,
    create_access_token,
    verify_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.core.oauth import fetch_oidc_config, fetch_jwks, validate_id_token
from app.services.state_store import oauth_state_store, session_store, user_store

# Google OIDC issuer
GOOGLE_ISSUER = "https://accounts.google.com"


async def initiate_google_oauth(redirect_to: str | None = None) -> str:
    """Initiate Google OAuth flow.

    Args:
        redirect_to: Optional URL to redirect after login

    Returns:
        str: Google authorization URL
    """
    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # Generate state and nonce
    state = generate_state_token()
    nonce = generate_nonce()

    # Save state for CSRF validation
    oauth_state_store.save_oauth_state(
        state,
        {
            "code_verifier": code_verifier,
            "nonce": nonce,
            "redirect_to": redirect_to,
        },
        ttl_seconds=300,  # 5 minutes
    )

    # Fetch Google OIDC configuration
    oidc_config = await fetch_oidc_config(GOOGLE_ISSUER)
    auth_endpoint = oidc_config["authorization_endpoint"]

    # Build authorization URL
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{auth_endpoint}?{urlencode(params)}"
    return auth_url


async def handle_google_callback(code: str, state: str) -> dict:
    """Handle Google OAuth callback.

    Args:
        code: Authorization code from Google
        state: State token for CSRF validation

    Returns:
        dict: Login response with tokens and user info

    Raises:
        HTTPException: If validation fails
    """
    # Validate state (CSRF protection)
    state_data = oauth_state_store.get_oauth_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    code_verifier = state_data["code_verifier"]
    nonce = state_data["nonce"]

    # Fetch Google OIDC config
    oidc_config = await fetch_oidc_config(GOOGLE_ISSUER)
    token_endpoint = oidc_config["token_endpoint"]
    jwks_uri = oidc_config.get("jwks_uri")

    # Exchange code for tokens
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_endpoint,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=401,
                detail=f"Token exchange failed: {response.text}"
            )

        token_response = response.json()

    # Validate id_token
    id_token = token_response.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    if not jwks_uri:
        raise HTTPException(status_code=500, detail="Missing JWKS URI")

    jwks = await fetch_jwks(jwks_uri)
    claims = await validate_id_token(
        id_token,
        jwks,
        settings.GOOGLE_OAUTH_CLIENT_ID,
        GOOGLE_ISSUER,
        nonce
    )

    # Extract user info from id_token
    google_id = claims.get("sub")
    email = claims.get("email")
    name = claims.get("name")
    picture = claims.get("picture")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Missing user info in id_token")

    # Create or retrieve user
    user = user_store.get_user_by_google_id(google_id)
    if not user:
        user = user_store.create_user(google_id, email, name, picture)

    # Generate app tokens
    access_token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
    })

    refresh_token = create_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token)

    # Create session
    session_store.create_session(
        user["id"],
        refresh_token_hash,
        ttl_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Return login response
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name"),
            "picture_url": user.get("picture_url"),
        },
    }


async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh access token using refresh token.

    Args:
        refresh_token: Refresh token

    Returns:
        dict: New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Hash refresh token
    token_hash = hash_refresh_token(refresh_token)

    # Get session
    session = session_store.get_session(token_hash)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Get user
    user = user_store.get_user(session["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Generate new access token
    access_token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def logout(refresh_token: str):
    """Logout by invalidating session.

    Args:
        refresh_token: Refresh token to invalidate
    """
    token_hash = hash_refresh_token(refresh_token)
    session_store.delete_session(token_hash)


async def get_current_user(access_token: str) -> dict:
    """Get current user from access token.

    Args:
        access_token: JWT access token

    Returns:
        dict: User profile

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = verify_access_token(access_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = user_store.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": user["id"],
        "email": user["email"],
        "name": user.get("name"),
        "picture_url": user.get("picture_url"),
    }
