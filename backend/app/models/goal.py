"""Goal, Milestone, and Task database models."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class GoalCategory(str, Enum):
    """Category types for goals."""
    HEALTH = "health"
    CAREER = "career"
    EDUCATION = "education"
    FINANCE = "finance"
    PERSONAL = "personal"
    OTHER = "other"


class GoalStatus(str, Enum):
    """Status of a goal."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class TaskPriority(str, Enum):
    """Priority level for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Goal(SQLModel, table=True):
    """
    Goal model for storing user goals.

    Goals are created from finalized chat sessions and contain
    milestones and tasks for tracking progress.
    """

    __tablename__ = "goals"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    chat_session_id: Optional[int] = Field(default=None, index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: GoalCategory = Field(default=GoalCategory.OTHER)
    target_date: Optional[date] = Field(default=None)
    status: GoalStatus = Field(default=GoalStatus.ACTIVE)
    progress: int = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True


class Milestone(SQLModel, table=True):
    """
    Milestone model for major checkpoints within a goal.

    Milestones break down goals into manageable phases,
    each containing multiple tasks.
    """

    __tablename__ = "milestones"

    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: int = Field(foreign_key="goals.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    target_date: Optional[date] = Field(default=None)
    order: int = Field(default=0)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True


class Task(SQLModel, table=True):
    """
    Task model for actionable items within milestones.

    Tasks are the smallest unit of work that users complete
    to make progress toward their goals.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    milestone_id: int = Field(foreign_key="milestones.id", index=True)
    goal_id: int = Field(foreign_key="goals.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[date] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True
