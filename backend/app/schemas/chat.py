"""Chat request/response schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.chat import ChatStatus, MessageRole


class SendMessageRequest(BaseModel):
    """Request to send a message in a chat session."""
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Single chat message response."""
    id: int
    session_id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Chat session metadata response."""
    id: int
    user_id: int
    title: Optional[str] = None
    status: ChatStatus
    goal_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessages(BaseModel):
    """Chat session with all messages."""
    session: ChatSessionResponse
    messages: List[MessageResponse]


class StartChatResponse(BaseModel):
    """Response when starting a new chat session."""
    session: ChatSessionResponse
    initial_message: MessageResponse


class SendMessageResponse(BaseModel):
    """Response after sending a message."""
    user_message: MessageResponse
    assistant_message: MessageResponse


class ChatListItem(BaseModel):
    """Chat session summary for list view."""
    id: int
    title: Optional[str] = None
    status: ChatStatus
    message_count: int
    last_message_preview: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FinalizeRequest(BaseModel):
    """Request to finalize a chat and create a goal."""
    # Reason: Empty for now, will be extended when Goal model is added
    pass


class FinalizeResponse(BaseModel):
    """Response after finalizing a chat session."""
    session: ChatSessionResponse
    message: str
    # Reason: goal field added when Goal model is implemented
