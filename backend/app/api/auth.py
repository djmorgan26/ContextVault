from fastapi import APIRouter, HTTPException, Header, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from app.schemas.auth import (
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    LogoutRequest,
    UserProfile,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/google/login")
async def google_login(redirect_to: Optional[str] = Query(None)):
    """Initiate Google OAuth login flow.

    Args:
        redirect_to: Optional URL to redirect after login

    Returns:
        RedirectResponse: Redirect to Google consent screen
    """
    auth_url = await auth_service.initiate_google_oauth(redirect_to)
    return RedirectResponse(auth_url)


@router.get("/google/callback", response_model=LoginResponse)
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
):
    """Handle Google OAuth callback.

    Args:
        code: Authorization code from Google
        state: State token for CSRF validation

    Returns:
        LoginResponse: Access token, refresh token, and user info

    Raises:
        HTTPException: 400 if state invalid, 401 if token exchange fails
    """
    try:
        result = await auth_service.handle_google_callback(code, state)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest):
    """Refresh access token.

    Args:
        request: Contains refresh_token

    Returns:
        TokenRefreshResponse: New access token

    Raises:
        HTTPException: 401 if refresh token invalid
    """
    try:
        result = await auth_service.refresh_access_token(request.refresh_token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@router.post("/logout", status_code=204)
async def logout(request: LogoutRequest):
    """Logout by invalidating session.

    Args:
        request: Contains refresh_token

    Returns:
        204 No Content
    """
    await auth_service.logout(request.refresh_token)


@router.get("/me", response_model=UserProfile)
async def get_current_user(authorization: str = Header(...)):
    """Get current user profile.

    Args:
        authorization: Bearer token in Authorization header

    Returns:
        UserProfile: Current user information

    Raises:
        HTTPException: 401 if token missing or invalid
    """
    # Extract token from "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    access_token = authorization[7:]  # Remove "Bearer " prefix

    try:
        user = await auth_service.get_current_user(access_token)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")
