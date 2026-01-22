"""
Base Agent class and supporting types for MileSync multi-agent system.

All specialized agents inherit from BaseAgent and implement the process() method.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of agents in the MileSync system."""
    FOUNDATION = "foundation"
    PLANNING = "planning"
    EXECUTION = "execution"
    SUSTAINABILITY = "sustainability"
    SUPPORT = "support"
    PSYCHOLOGICAL = "psychological"


class GoalType(str, Enum):
    """Goal duration classification."""
    SHORT_TERM = "short_term"    # <3 months
    LONG_TERM = "long_term"      # 3-12 months
    RESOLUTION = "resolution"    # Year-long commitment


class TaskFrequency(str, Enum):
    """How often a task should be performed."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


class AgentContext(BaseModel):
    """Context passed to agents for processing."""
    
    user_id: int
    goal_id: Optional[int] = None
    session_id: Optional[int] = None
    messages: List[Dict[str, str]] = Field(default_factory=list)
    user_profile: Optional[Dict[str, Any]] = None
    current_goal: Optional[Dict[str, Any]] = None
    task_history: Optional[List[Dict[str, Any]]] = None
    additional_context: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"


class AgentResponse(BaseModel):
    """Standard response from any agent."""
    
    agent_type: AgentType
    success: bool = True
    message: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)
    next_agent: Optional[AgentType] = None  # For agent chaining
    requires_user_input: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None  # For Opik tracing
    
    class Config:
        use_enum_values = True


class BaseAgent(ABC):
    """
    Abstract base class for all MileSync agents.
    
    Each agent specializes in one aspect of goal coaching:
    - Foundation: Initial intake and profiling
    - Planning: SMART goals and task breakdown
    - Execution: Active task management
    - Sustainability: Habit formation
    - Support: Resource recommendations
    - Psychological: Motivation and mindset
    """
    
    agent_type: AgentType
    agent_name: str
    agent_description: str
    
    def __init__(self):
        """Initialize the base agent."""
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for this agent."""
        self.logger = logging.getLogger(f"agent.{self.agent_type.value}")
    
    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process a request with the given context.
        
        Args:
            context: AgentContext with user, goal, and message data
            
        Returns:
            AgentResponse with results and next steps
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        Returns:
            System prompt string for the LLM
        """
        pass
    
    async def generate_response(
        self,
        context: AgentContext,
        user_message: str
    ) -> str:
        """
        Generate an LLM response using this agent's prompt.
        
        Args:
            context: Current agent context
            user_message: The user's message
            
        Returns:
            Generated response string
        """
        from app.services.ai_service import get_openai_client
        
        client = get_openai_client()
        if not client:
            raise ValueError("OpenAI client not configured")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
        ]
        
        # Add conversation history
        for msg in context.messages:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def create_response(
        self,
        success: bool = True,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        next_agent: Optional[AgentType] = None,
        requires_user_input: bool = False
    ) -> AgentResponse:
        """
        Create a standardized agent response.
        
        Args:
            success: Whether the operation succeeded
            message: Human-readable message
            data: Structured data from the agent
            next_agent: Optional next agent in chain
            requires_user_input: Whether user input is needed
            
        Returns:
            Formatted AgentResponse
        """
        import uuid
        
        return AgentResponse(
            agent_type=self.agent_type,
            success=success,
            message=message,
            data=data or {},
            next_agent=next_agent,
            requires_user_input=requires_user_input,
            trace_id=str(uuid.uuid4())
        )


# Output schemas for each agent type

class FoundationOutput(BaseModel):
    """Output from Foundation Agent."""
    goal_summary: str
    goal_type: GoalType
    motivation_score: int = Field(ge=1, le=10)
    feasibility_score: int = Field(ge=1, le=10)
    clarity_score: int = Field(ge=1, le=10)
    identified_obstacles: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    baseline_metrics: Dict[str, Any] = Field(default_factory=dict)
    user_constraints: Dict[str, Any] = Field(default_factory=dict)
    recommended_adjustments: List[str] = Field(default_factory=list)


class SMARTGoal(BaseModel):
    """SMART goal breakdown."""
    specific: str
    measurable: str
    achievable: str
    relevant: str
    time_bound: str


class TaskScheduleItem(BaseModel):
    """A scheduled task item."""
    title: str
    description: Optional[str] = None
    frequency: TaskFrequency
    estimated_minutes: int = 30
    priority: str = "medium"


class TaskSchedule(BaseModel):
    """Complete task schedule."""
    daily: List[TaskScheduleItem] = Field(default_factory=list)
    weekly: List[TaskScheduleItem] = Field(default_factory=list)
    monthly: List[TaskScheduleItem] = Field(default_factory=list)


class MilestoneOutput(BaseModel):
    """Milestone from planning."""
    id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    success_criteria: List[str] = Field(default_factory=list)
    tasks: List[TaskScheduleItem] = Field(default_factory=list)


class PlanningOutput(BaseModel):
    """Output from Planning Agent."""
    smart_goal: SMARTGoal
    milestones: List[MilestoneOutput] = Field(default_factory=list)
    task_schedule: TaskSchedule = Field(default_factory=TaskSchedule)
    dependencies: List[Dict[str, str]] = Field(default_factory=list)
    total_estimated_hours: int = 0
    critical_path: List[str] = Field(default_factory=list)


class DailySummary(BaseModel):
    """Daily execution summary."""
    tasks_completed: int = 0
    tasks_pending: int = 0
    streak_count: int = 0
    completion_rate: float = 0.0


class ExecutionOutput(BaseModel):
    """Output from Execution Agent."""
    daily_summary: DailySummary = Field(default_factory=DailySummary)
    adjustments_recommended: List[str] = Field(default_factory=list)
    blockers_identified: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    motivational_message: str = ""


class HabitLoop(BaseModel):
    """Habit loop structure."""
    cue: str
    routine: str
    reward: str


class HabitAnalysis(BaseModel):
    """Habit formation analysis."""
    habit_score: int = Field(default=0, ge=0, le=100)
    days_consistent: int = 0
    habit_loops: List[HabitLoop] = Field(default_factory=list)


class PatternInsights(BaseModel):
    """Pattern detection insights."""
    best_days: List[str] = Field(default_factory=list)
    best_times: List[str] = Field(default_factory=list)
    failure_patterns: List[str] = Field(default_factory=list)


class SustainabilityOutput(BaseModel):
    """Output from Sustainability Agent."""
    habit_analysis: HabitAnalysis = Field(default_factory=HabitAnalysis)
    pattern_insights: PatternInsights = Field(default_factory=PatternInsights)
    sustainability_score: int = Field(ge=0, le=100, default=50)
    burnout_risk: str = "LOW"  # LOW, MEDIUM, HIGH
    recommendations: List[str] = Field(default_factory=list)


class Resource(BaseModel):
    """Recommended resource."""
    type: str  # COURSE, BOOK, TOOL, COMMUNITY, EXPERT
    name: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    time_commitment: Optional[str] = None
    cost: str = "Free"


class SupportOutput(BaseModel):
    """Output from Support Agent."""
    recommended_resources: List[Resource] = Field(default_factory=list)
    integration_suggestions: List[str] = Field(default_factory=list)
    community_matches: List[str] = Field(default_factory=list)
    expert_recommendations: List[str] = Field(default_factory=list)


class EmotionalAssessment(BaseModel):
    """Emotional state assessment."""
    motivation_level: int = Field(ge=1, le=10, default=5)
    stress_level: int = Field(ge=1, le=10, default=5)
    confidence_level: int = Field(ge=1, le=10, default=5)
    detected_patterns: List[str] = Field(default_factory=list)


class Intervention(BaseModel):
    """Psychological intervention."""
    type: str
    technique: str
    message: str
    exercises: List[str] = Field(default_factory=list)


class PsychologicalOutput(BaseModel):
    """Output from Psychological Agent."""
    emotional_assessment: EmotionalAssessment = Field(default_factory=EmotionalAssessment)
    intervention: Optional[Intervention] = None
    affirmations: List[str] = Field(default_factory=list)
    progress_celebration: str = ""
