from pydantic import BaseModel, EmailStr
from typing import Optional


class UserProfile(BaseModel):
    """User profile information."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    picture_url: Optional[str] = None


class LoginResponse(BaseModel):
    """Response from successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class TokenRefreshRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Response from token refresh."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    """Request to logout (invalidate session)."""
    refresh_token: str
