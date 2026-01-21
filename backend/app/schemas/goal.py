"""Goal, Milestone, and Task request/response schemas."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.goal import GoalCategory, GoalStatus, TaskPriority, TaskStatus


# ===================
# Task Schemas
# ===================


class TaskCreate(BaseModel):
    """Request to create a task."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[date] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    """Request to update a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(BaseModel):
    """Task response."""
    id: int
    milestone_id: int
    goal_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: TaskStatus
    priority: TaskPriority
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===================
# Milestone Schemas
# ===================


class MilestoneCreate(BaseModel):
    """Request to create a milestone."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    target_date: Optional[date] = None
    order: int = 0


class MilestoneUpdate(BaseModel):
    """Request to update a milestone."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    target_date: Optional[date] = None
    is_completed: Optional[bool] = None


class MilestoneResponse(BaseModel):
    """Milestone response."""
    id: int
    goal_id: int
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    order: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MilestoneWithTasks(MilestoneResponse):
    """Milestone with its tasks."""
    tasks: List[TaskResponse] = []


# ===================
# Goal Schemas
# ===================


class GoalCreate(BaseModel):
    """Request to create a goal manually."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: GoalCategory = GoalCategory.OTHER
    target_date: Optional[date] = None


class GoalUpdate(BaseModel):
    """Request to update a goal."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[GoalCategory] = None
    target_date: Optional[date] = None
    status: Optional[GoalStatus] = None


class GoalResponse(BaseModel):
    """Goal response without nested data."""
    id: int
    user_id: int
    chat_session_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    category: GoalCategory
    target_date: Optional[date] = None
    status: GoalStatus
    progress: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalWithMilestones(GoalResponse):
    """Goal with milestones and tasks."""
    milestones: List[MilestoneWithTasks] = []


class GoalListItem(BaseModel):
    """Goal summary for list view."""
    id: int
    title: str
    description: Optional[str] = None
    category: GoalCategory
    target_date: Optional[date] = None
    status: GoalStatus
    progress: int
    milestone_count: int
    task_count: int
    completed_task_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===================
# AI Generation Schemas
# ===================


class AITaskGeneration(BaseModel):
    """Task data from AI generation."""
    title: str
    description: Optional[str] = None
    priority: str = "medium"


class AIMilestoneGeneration(BaseModel):
    """Milestone data from AI generation."""
    title: str
    description: Optional[str] = None
    target_date: Optional[str] = None
    tasks: List[AITaskGeneration] = []


class AIGoalGeneration(BaseModel):
    """Complete goal data from AI extraction."""
    title: str
    description: Optional[str] = None
    category: str = "other"
    target_date: Optional[str] = None
    milestones: List[AIMilestoneGeneration] = []


class FinalizeWithGoalResponse(BaseModel):
    """Response after finalizing chat and creating goal."""
    goal: GoalResponse
    message: str


# ===================
# Dashboard Schemas
# ===================


class UpcomingTask(BaseModel):
    """Task item for dashboard upcoming tasks list."""
    id: int
    title: str
    goal_id: int
    goal_title: str
    due_date: Optional[date] = None
    priority: TaskPriority

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Dashboard statistics for the current user."""
    active_goals: int
    completed_tasks: int
    total_tasks: int
    completion_rate: int
    current_streak: int
    upcoming_tasks: List[UpcomingTask] = []
