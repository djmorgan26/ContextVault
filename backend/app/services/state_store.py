import threading
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional


class OAuthStateStore:
    """Thread-safe in-memory store for OAuth state tokens (CSRF protection)."""

    def __init__(self):
        self._store: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def save_oauth_state(self, state: str, data: dict, ttl_seconds: int = 300):
        """Save OAuth state with TTL.

        Args:
            state: State token
            data: Data to store (code_verifier, nonce, redirect_to)
            ttl_seconds: Time to live in seconds (default: 5 minutes)
        """
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._store[state] = {**data, "expires_at": expires_at}

    def get_oauth_state(self, state: str) -> Optional[dict]:
        """Retrieve and delete OAuth state (one-time use).

        Args:
            state: State token

        Returns:
            dict or None: Stored data if valid, None if expired or not found
        """
        with self._lock:
            data = self._store.pop(state, None)
            if data is None:
                return None

            # Check expiration
            if datetime.utcnow() > data["expires_at"]:
                return None

            # Remove expires_at from returned data
            data.pop("expires_at")
            return data

    def cleanup_expired_states(self):
        """Remove expired state entries."""
        with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                state for state, data in self._store.items()
                if now > data["expires_at"]
            ]
            for key in expired_keys:
                del self._store[key]


class SessionStore:
    """Thread-safe in-memory store for user sessions."""

    def __init__(self):
        self._sessions: Dict[str, dict] = {}  # refresh_token_hash -> session data
        self._lock = threading.Lock()

    def create_session(
        self,
        user_id: str,
        refresh_token_hash: str,
        ttl_days: int = 30
    ) -> str:
        """Create a new session.

        Args:
            user_id: User identifier
            refresh_token_hash: Hashed refresh token
            ttl_days: Session lifetime in days

        Returns:
            str: Session identifier (same as refresh_token_hash)
        """
        with self._lock:
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(days=ttl_days)

            self._sessions[refresh_token_hash] = {
                "user_id": user_id,
                "created_at": created_at,
                "expires_at": expires_at,
            }

            return refresh_token_hash

    def get_session(self, refresh_token_hash: str) -> Optional[dict]:
        """Get session by refresh token hash.

        Args:
            refresh_token_hash: Hashed refresh token

        Returns:
            dict or None: Session data if valid, None if expired or not found
        """
        with self._lock:
            session = self._sessions.get(refresh_token_hash)
            if session is None:
                return None

            # Check expiration
            if datetime.utcnow() > session["expires_at"]:
                del self._sessions[refresh_token_hash]
                return None

            return session

    def delete_session(self, refresh_token_hash: str):
        """Delete a specific session (logout).

        Args:
            refresh_token_hash: Hashed refresh token
        """
        with self._lock:
            self._sessions.pop(refresh_token_hash, None)

    def delete_user_sessions(self, user_id: str):
        """Delete all sessions for a user (logout all devices).

        Args:
            user_id: User identifier
        """
        with self._lock:
            to_delete = [
                token_hash for token_hash, session in self._sessions.items()
                if session["user_id"] == user_id
            ]
            for token_hash in to_delete:
                del self._sessions[token_hash]

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        with self._lock:
            now = datetime.utcnow()
            expired_hashes = [
                token_hash for token_hash, session in self._sessions.items()
                if now > session["expires_at"]
            ]
            for token_hash in expired_hashes:
                del self._sessions[token_hash]


class UserStore:
    """Thread-safe in-memory store for user data."""

    def __init__(self):
        self._users: Dict[str, dict] = {}  # user_id -> user data
        self._google_id_index: Dict[str, str] = {}  # google_id -> user_id
        self._email_index: Dict[str, str] = {}  # email -> user_id
        self._lock = threading.Lock()

    def create_user(
        self,
        google_id: str,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None
    ) -> dict:
        """Create a new user.

        Args:
            google_id: Google user identifier
            email: User email
            name: User display name
            picture: User profile picture URL

        Returns:
            dict: Created user data with id
        """
        with self._lock:
            # Generate user ID
            user_id = f"user_{secrets.token_urlsafe(16)}"

            user_data = {
                "id": user_id,
                "google_id": google_id,
                "email": email,
                "name": name,
                "picture_url": picture,
                "created_at": datetime.utcnow(),
            }

            self._users[user_id] = user_data
            self._google_id_index[google_id] = user_id
            self._email_index[email] = user_id

            return user_data

    def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            dict or None: User data if found
        """
        with self._lock:
            return self._users.get(user_id)

    def get_user_by_google_id(self, google_id: str) -> Optional[dict]:
        """Get user by Google ID.

        Args:
            google_id: Google user identifier

        Returns:
            dict or None: User data if found
        """
        with self._lock:
            user_id = self._google_id_index.get(google_id)
            if user_id:
                return self._users.get(user_id)
            return None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email.

        Args:
            email: User email

        Returns:
            dict or None: User data if found
        """
        with self._lock:
            user_id = self._email_index.get(email)
            if user_id:
                return self._users.get(user_id)
            return None


# Global singleton instances
oauth_state_store = OAuthStateStore()
session_store = SessionStore()
user_store = UserStore()
