"""Goal, Milestone, and Task database models."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class GoalCategory(str, Enum):
    """Category types for goals."""
    HEALTH = "health"
    CAREER = "career"
    EDUCATION = "education"
    FINANCE = "finance"
    PERSONAL = "personal"
    OTHER = "other"


class GoalType(str, Enum):
    """Goal duration classification."""
    SHORT_TERM = "short_term"  # <3 months
    LONG_TERM = "long_term"    # 3-12 months
    RESOLUTION = "resolution"  # Year-long commitment


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


class TaskFrequency(str, Enum):
    """How often a task should be performed."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


class Goal(SQLModel, table=True):
    """
    Goal model for storing user goals.

    Goals are created from finalized chat sessions and contain
    milestones and tasks for tracking progress.
    Extended with SMART fields and agent-specific data.
    """

    __tablename__ = "goals"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    chat_session_id: Optional[int] = Field(default=None, index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: GoalCategory = Field(default=GoalCategory.OTHER)
    goal_type: GoalType = Field(default=GoalType.LONG_TERM)
    target_date: Optional[date] = Field(default=None)
    status: GoalStatus = Field(default=GoalStatus.ACTIVE)
    progress: int = Field(default=0, ge=0, le=100)
    
    # Foundation Agent scores
    motivation_score: Optional[int] = Field(default=None, ge=1, le=10)
    feasibility_score: Optional[int] = Field(default=None, ge=1, le=10)
    clarity_score: Optional[int] = Field(default=None, ge=1, le=10)
    
    # SMART goal fields (from Planning Agent)
    smart_specific: Optional[str] = Field(default=None, max_length=1000)
    smart_measurable: Optional[str] = Field(default=None, max_length=1000)
    smart_achievable: Optional[str] = Field(default=None, max_length=1000)
    smart_relevant: Optional[str] = Field(default=None, max_length=1000)
    smart_time_bound: Optional[str] = Field(default=None, max_length=1000)
    
    # Sustainability tracking
    sustainability_score: Optional[int] = Field(default=None, ge=0, le=100)
    burnout_risk: Optional[str] = Field(default="LOW", max_length=20)
    
    # JSON fields for complex data
    identified_obstacles: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    success_criteria: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
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
    Extended with frequency and streak tracking for habits.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    milestone_id: Optional[int] = Field(default=None, foreign_key="milestones.id", index=True)
    goal_id: int = Field(foreign_key="goals.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[date] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    
    # Frequency and habit tracking
    frequency: TaskFrequency = Field(default=TaskFrequency.ONE_TIME)
    estimated_minutes: int = Field(default=30)
    streak_count: int = Field(default=0)
    best_streak: int = Field(default=0)
    last_completed_at: Optional[datetime] = Field(default=None)
    times_completed: int = Field(default=0)
    times_skipped: int = Field(default=0)
    
    # Habit loop fields (from Sustainability Agent)
    habit_cue: Optional[str] = Field(default=None, max_length=500)
    habit_reward: Optional[str] = Field(default=None, max_length=500)
    
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True
