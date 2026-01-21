"""Authentication routes for login, register, and OAuth."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.config import settings
from app.database import get_db
from app.models.user import AuthProvider
from app.schemas.user import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.services import auth_service, oauth_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.

    Returns JWT token and user data on success.
    """
    # Check if user already exists
    existing_user = auth_service.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = auth_service.create_user(db, data)

    # Generate token
    access_token = auth_service.create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns JWT token and user data on success.
    """
    user = auth_service.authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update the current authenticated user's profile.
    """
    updated_user = auth_service.update_user_profile(db, current_user, data)
    return UserResponse.model_validate(updated_user)


# ===================
# Google OAuth
# ===================


@router.get("/google")
async def google_auth():
    """Redirect to Google OAuth authorization page."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured",
        )
    auth_url = oauth_service.get_google_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.

    Creates or retrieves user and redirects to frontend with token.
    """
    user_info = await oauth_service.get_google_user_info(code)
    if not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from Google",
        )

    # Check if user exists
    user = auth_service.get_user_by_email(db, user_info["email"])

    if not user:
        # Create new user
        user = auth_service.create_oauth_user(
            db,
            email=user_info["email"],
            name=user_info["name"],
            provider=AuthProvider.GOOGLE,
            avatar_url=user_info.get("avatar_url"),
        )

    # Generate token
    access_token = auth_service.create_access_token(user.id)

    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_URL}/oauth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)


# ===================
# GitHub OAuth
# ===================


@router.get("/github")
async def github_auth():
    """Redirect to GitHub OAuth authorization page."""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured",
        )
    auth_url = oauth_service.get_github_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle GitHub OAuth callback.

    Creates or retrieves user and redirects to frontend with token.
    """
    user_info = await oauth_service.get_github_user_info(code)
    if not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from GitHub",
        )

    # Check if user exists
    user = auth_service.get_user_by_email(db, user_info["email"])

    if not user:
        # Create new user
        user = auth_service.create_oauth_user(
            db,
            email=user_info["email"],
            name=user_info["name"],
            provider=AuthProvider.GITHUB,
            avatar_url=user_info.get("avatar_url"),
        )

    # Generate token
    access_token = auth_service.create_access_token(user.id)

    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_URL}/oauth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)
