"""
User Profile model for psychological and behavioral profiling.

Used by agents to personalize coaching and recommendations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class LearningStyle(str, Enum):
    """User's preferred learning style."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING = "reading"
    KINESTHETIC = "kinesthetic"


class MotivationType(str, Enum):
    """User's primary motivation type."""
    INTRINSIC = "intrinsic"       # Internal satisfaction
    EXTRINSIC = "extrinsic"       # External rewards
    ACHIEVEMENT = "achievement"   # Goal-focused
    AFFILIATION = "affiliation"   # Social connection
    POWER = "power"               # Influence/impact


class PersonalityType(str, Enum):
    """Simplified personality classification."""
    DRIVER = "driver"             # Results-oriented
    ANALYTICAL = "analytical"     # Data-driven
    EXPRESSIVE = "expressive"     # Creative, big-picture
    AMIABLE = "amiable"           # Relationship-focused


class UserProfile(SQLModel, table=True):
    """
    User Profile model for storing behavioral and psychological insights.
    
    Built over time by the agent system to personalize coaching.
    """
    
    __tablename__ = "user_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    # Psychological profiling
    learning_style: Optional[LearningStyle] = Field(default=None)
    motivation_type: Optional[MotivationType] = Field(default=None)
    personality_type: Optional[PersonalityType] = Field(default=None)
    
    # Energy and productivity patterns
    best_time_of_day: Optional[str] = Field(default=None, max_length=50)  # morning/afternoon/evening
    best_days: Optional[str] = Field(default=None, max_length=100)  # comma-separated
    avg_focus_duration: Optional[int] = Field(default=None)  # minutes
    
    # Goal preferences
    preferred_goal_type: Optional[str] = Field(default=None, max_length=50)
    preferred_task_size: Optional[str] = Field(default=None, max_length=50)  # small/medium/large
    
    # Engagement metrics
    total_goals_completed: int = Field(default=0)
    total_tasks_completed: int = Field(default=0)
    avg_completion_rate: float = Field(default=0.0)
    longest_streak: int = Field(default=0)
    
    # Psychological state tracking
    current_stress_level: int = Field(default=5, ge=1, le=10)
    current_motivation_level: int = Field(default=5, ge=1, le=10)
    current_confidence_level: int = Field(default=5, ge=1, le=10)
    
    # Communication preferences
    preferred_reminder_frequency: Optional[str] = Field(default="daily", max_length=50)
    preferred_communication_style: Optional[str] = Field(default="supportive", max_length=50)
    
    # JSON fields for flexible data
    strengths: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    challenges: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    values: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
