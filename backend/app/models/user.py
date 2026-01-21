"""User database model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class AuthProvider(str, Enum):
    """Authentication provider types."""
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"


class User(SQLModel, table=True):
    """User model for authentication and profile data."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: Optional[str] = Field(default=None, max_length=255)
    name: str = Field(max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    auth_provider: AuthProvider = Field(default=AuthProvider.EMAIL)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True
