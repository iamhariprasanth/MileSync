# Pydantic schemas for request/response validation

from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.schemas.chat import (
    SendMessageRequest,
    MessageResponse,
    ChatSessionResponse,
    ChatSessionWithMessages,
    StartChatResponse,
    SendMessageResponse,
    ChatListItem,
    FinalizeRequest,
    FinalizeResponse,
)
from app.schemas.goal import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneResponse,
    MilestoneWithTasks,
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalWithMilestones,
    GoalListItem,
    AIGoalGeneration,
    FinalizeWithGoalResponse,
)

__all__ = [
    # User schemas
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    "UserUpdate",
    # Chat schemas
    "SendMessageRequest",
    "MessageResponse",
    "ChatSessionResponse",
    "ChatSessionWithMessages",
    "StartChatResponse",
    "SendMessageResponse",
    "ChatListItem",
    "FinalizeRequest",
    "FinalizeResponse",
    # Goal schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "MilestoneCreate",
    "MilestoneUpdate",
    "MilestoneResponse",
    "MilestoneWithTasks",
    "GoalCreate",
    "GoalUpdate",
    "GoalResponse",
    "GoalWithMilestones",
    "GoalListItem",
    "AIGoalGeneration",
    "FinalizeWithGoalResponse",
]
