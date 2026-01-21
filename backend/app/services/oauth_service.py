"""OAuth service for Google and GitHub authentication."""

from typing import Optional
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.models.user import AuthProvider


# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# GitHub OAuth URLs
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


def get_google_auth_url(state: Optional[str] = None) -> str:
    """
    Generate Google OAuth authorization URL.

    Args:
        state: Optional state parameter for CSRF protection

    Returns:
        Authorization URL to redirect user to
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    if state:
        params["state"] = state
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def get_google_user_info(code: str) -> Optional[dict]:
    """
    Exchange authorization code for user info from Google.

    Args:
        code: Authorization code from Google callback

    Returns:
        User info dict with email, name, picture, or None if failed
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
        )

        if token_response.status_code != 200:
            return None

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return None

        # Get user info
        user_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_response.status_code != 200:
            return None

        user_data = user_response.json()
        return {
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "avatar_url": user_data.get("picture"),
            "provider": AuthProvider.GOOGLE,
        }


# ===================
# GitHub OAuth
# ===================


def get_github_auth_url(state: Optional[str] = None) -> str:
    """
    Generate GitHub OAuth authorization URL.

    Args:
        state: Optional state parameter for CSRF protection

    Returns:
        Authorization URL to redirect user to
    """
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
    }
    if state:
        params["state"] = state
    return f"{GITHUB_AUTH_URL}?{urlencode(params)}"


async def get_github_user_info(code: str) -> Optional[dict]:
    """
    Exchange authorization code for user info from GitHub.

    Args:
        code: Authorization code from GitHub callback

    Returns:
        User info dict with email, name, avatar_url, or None if failed
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )

        if token_response.status_code != 200:
            return None

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Get user info
        user_response = await client.get(GITHUB_USERINFO_URL, headers=headers)

        if user_response.status_code != 200:
            return None

        user_data = user_response.json()

        # Get user email (may be private)
        email = user_data.get("email")
        if not email:
            # Fetch emails separately if not in profile
            emails_response = await client.get(GITHUB_EMAILS_URL, headers=headers)
            if emails_response.status_code == 200:
                emails = emails_response.json()
                # Find primary verified email
                for email_obj in emails:
                    if email_obj.get("primary") and email_obj.get("verified"):
                        email = email_obj.get("email")
                        break

        if not email:
            return None

        return {
            "email": email,
            "name": user_data.get("name") or user_data.get("login"),
            "avatar_url": user_data.get("avatar_url"),
            "provider": AuthProvider.GITHUB,
        }

