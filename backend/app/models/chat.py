"""Chat database models for AI coaching sessions."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ChatStatus(str, Enum):
    """Status of a chat session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FINALIZED = "finalized"  # Goal created from this session


class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(SQLModel, table=True):
    """
    Chat session model for storing AI coaching conversations.

    Each session represents a goal-definition conversation that may
    result in a goal being created when finalized.
    """

    __tablename__ = "chat_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    status: ChatStatus = Field(default=ChatStatus.ACTIVE)
    goal_id: Optional[int] = Field(default=None, foreign_key="goals.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True


class ChatMessage(SQLModel, table=True):
    """
    Chat message model for storing individual messages in a session.

    Messages track the conversation flow between user and AI coach.
    """

    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", index=True)
    role: MessageRole = Field(default=MessageRole.USER)
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True
