"""
Agent API routes for MileSync.

Provides endpoints for direct agent interactions and multi-agent pipelines.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.agents.base_agent import AgentContext, AgentType
from app.agents.coordinator import get_agent_coordinator
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


# Request/Response schemas

class AgentRequest(BaseModel):
    """Request to a specific agent."""
    message: str
    goal_id: Optional[int] = None
    session_id: Optional[int] = None
    request_type: Optional[str] = None  # daily_checkin, pattern_analysis, etc.


class AgentRouteRequest(BaseModel):
    """Request that will be routed to the appropriate agent."""
    messages: List[dict] = Field(default_factory=list)
    goal_id: Optional[int] = None
    session_id: Optional[int] = None


class IntakeRequest(BaseModel):
    """Request to start goal intake."""
    initial_message: str
    session_id: Optional[int] = None


class PlanRequest(BaseModel):
    """Request to generate a plan."""
    goal_summary: str
    goal_type: str = "long_term"
    motivation_score: int = 7
    feasibility_score: int = 7
    obstacles: List[str] = Field(default_factory=list)


class CheckinRequest(BaseModel):
    """Daily check-in request."""
    goal_id: int
    completed_task_ids: List[int] = Field(default_factory=list)
    notes: Optional[str] = None


class MotivationRequest(BaseModel):
    """Request for motivational support."""
    message: str
    goal_id: Optional[int] = None


# Helper functions

def _build_context(
    user: User,
    goal_id: Optional[int] = None,
    session_id: Optional[int] = None,
    messages: Optional[List[dict]] = None,
    additional_context: Optional[dict] = None,
    db: Optional[Session] = None
) -> AgentContext:
    """Build an AgentContext from request data."""
    context = AgentContext(
        user_id=user.id,
        goal_id=goal_id,
        session_id=session_id,
        messages=messages or [],
        additional_context=additional_context or {}
    )
    
    # Load goal if exists
    if goal_id and db:
        from app.models.goal import Goal
        goal = db.get(Goal, goal_id)
        if goal and goal.user_id == user.id:
            context.current_goal = {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "category": goal.category,
                "target_date": str(goal.target_date) if goal.target_date else None,
                "progress": goal.progress
            }
    
    return context


# Endpoints

@router.get("/info")
async def get_agents_info(
    current_user: User = Depends(get_current_user)
):
    """Get information about all available agents."""
    coordinator = get_agent_coordinator()
    return {
        "agents": coordinator.get_agent_info(),
        "total_agents": len(coordinator.agents)
    }


@router.post("/route")
async def route_to_agent(
    request: AgentRouteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Route a request to the appropriate agent automatically.
    
    The coordinator analyzes the context and routes to the best agent.
    """
    context = _build_context(
        user=current_user,
        goal_id=request.goal_id,
        session_id=request.session_id,
        messages=request.messages,
        db=db
    )
    
    coordinator = get_agent_coordinator()
    response = await coordinator.route(context)
    
    return {
        "agent_type": response.agent_type,
        "success": response.success,
        "message": response.message,
        "data": response.data,
        "requires_user_input": response.requires_user_input
    }


@router.post("/intake")
async def start_intake(
    request: IntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start goal intake with the Foundation Agent.
    
    Initiates a comprehensive goal exploration conversation.
    """
    context = _build_context(
        user=current_user,
        session_id=request.session_id,
        messages=[{"role": "user", "content": request.initial_message}],
        additional_context={"agent_type": "foundation"},
        db=db
    )
    
    coordinator = get_agent_coordinator()
    response = await coordinator.route(context)
    
    return {
        "agent_type": "foundation",
        "message": response.message,
        "data": response.data,
        "requires_user_input": response.requires_user_input
    }


@router.post("/plan")
async def generate_plan(
    request: PlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a SMART plan with the Planning Agent.
    
    Creates milestones, tasks, and schedules from goal information.
    """
    context = _build_context(
        user=current_user,
        messages=[{"role": "user", "content": request.goal_summary}],
        additional_context={
            "agent_type": "planning",
            "previous_output": {
                "goal_summary": request.goal_summary,
                "goal_type": request.goal_type,
                "motivation_score": request.motivation_score,
                "feasibility_score": request.feasibility_score,
                "identified_obstacles": request.obstacles
            }
        },
        db=db
    )
    
    coordinator = get_agent_coordinator()
    response = await coordinator.route(context)
    
    return {
        "agent_type": "planning",
        "message": response.message,
        "smart_goal": response.data.get("smart_goal"),
        "milestones": response.data.get("milestones"),
        "task_schedule": response.data.get("task_schedule")
    }


@router.get("/daily")
async def get_daily_tasks(
    goal_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily tasks and summary from the Execution Agent.
    """
    # Load task history
    task_history = []
    if goal_id:
        from app.models.goal import Task
        from sqlmodel import select
        
        statement = select(Task).where(Task.goal_id == goal_id)
        tasks = db.exec(statement).all()
        task_history = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "created_at": str(t.created_at),
                "completed_at": str(t.completed_at) if t.completed_at else None
            }
            for t in tasks
        ]
    
    context = _build_context(
        user=current_user,
        goal_id=goal_id,
        additional_context={"request_type": "daily_summary"},
        db=db
    )
    context.task_history = task_history
    
    coordinator = get_agent_coordinator()
    agent = coordinator.get_agent(AgentType.EXECUTION)
    response = await agent.process(context)
    
    return {
        "agent_type": "execution",
        "daily_summary": response.data.get("daily_summary"),
        "next_actions": response.data.get("next_actions"),
        "motivational_message": response.data.get("motivational_message")
    }


@router.post("/checkin")
async def daily_checkin(
    request: CheckinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform daily check-in workflow.
    
    Runs Execution → Sustainability → Psychological (if needed) pipeline.
    """
    # Load task history
    from app.models.goal import Task
    from sqlmodel import select
    
    statement = select(Task).where(Task.goal_id == request.goal_id)
    tasks = db.exec(statement).all()
    task_history = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "created_at": str(t.created_at),
            "completed_at": str(t.completed_at) if t.completed_at else None
        }
        for t in tasks
    ]
    
    messages = []
    if request.notes:
        messages.append({"role": "user", "content": request.notes})
    
    context = _build_context(
        user=current_user,
        goal_id=request.goal_id,
        messages=messages,
        additional_context={"request_type": "daily_checkin"},
        db=db
    )
    context.task_history = task_history
    
    coordinator = get_agent_coordinator()
    results = await coordinator.run_daily_checkin(context)
    
    return {
        "execution": results.get("execution"),
        "sustainability": results.get("sustainability"),
        "psychological": results.get("psychological")
    }


@router.get("/insights")
async def get_insights(
    goal_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sustainability insights and pattern analysis.
    """
    # Load task history
    task_history = []
    if goal_id:
        from app.models.goal import Task
        from sqlmodel import select
        
        statement = select(Task).where(Task.goal_id == goal_id)
        tasks = db.exec(statement).all()
        task_history = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "created_at": str(t.created_at),
                "completed_at": str(t.completed_at) if t.completed_at else None
            }
            for t in tasks
        ]
    
    context = _build_context(
        user=current_user,
        goal_id=goal_id,
        db=db
    )
    context.task_history = task_history
    
    coordinator = get_agent_coordinator()
    agent = coordinator.get_agent(AgentType.SUSTAINABILITY)
    response = await agent.process(context)
    
    return {
        "agent_type": "sustainability",
        "habit_analysis": response.data.get("habit_analysis"),
        "pattern_insights": response.data.get("pattern_insights"),
        "sustainability_score": response.data.get("sustainability_score"),
        "burnout_risk": response.data.get("burnout_risk"),
        "recommendations": response.data.get("recommendations")
    }


@router.get("/resources")
async def get_resources(
    goal_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get resource recommendations from the Support Agent.
    """
    context = _build_context(
        user=current_user,
        goal_id=goal_id,
        db=db
    )
    
    coordinator = get_agent_coordinator()
    agent = coordinator.get_agent(AgentType.SUPPORT)
    response = await agent.process(context)
    
    return {
        "agent_type": "support",
        "recommended_resources": response.data.get("recommended_resources"),
        "integration_suggestions": response.data.get("integration_suggestions"),
        "community_matches": response.data.get("community_matches")
    }


@router.post("/motivation")
async def get_motivation_support(
    request: MotivationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get motivational support from the Psychological Agent.
    """
    context = _build_context(
        user=current_user,
        goal_id=request.goal_id,
        messages=[{"role": "user", "content": request.message}],
        db=db
    )
    
    coordinator = get_agent_coordinator()
    agent = coordinator.get_agent(AgentType.PSYCHOLOGICAL)
    response = await agent.process(context)
    
    return {
        "agent_type": "psychological",
        "emotional_assessment": response.data.get("emotional_assessment"),
        "intervention": response.data.get("intervention"),
        "affirmations": response.data.get("affirmations"),
        "progress_celebration": response.data.get("progress_celebration")
    }


@router.post("/pipeline/intake")
async def run_intake_pipeline(
    request: IntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run the full intake pipeline: Foundation → Planning.
    
    Takes initial goal description and returns complete plan.
    """
    context = _build_context(
        user=current_user,
        session_id=request.session_id,
        messages=[{"role": "user", "content": request.initial_message}],
        additional_context={"generate_assessment": True},
        db=db
    )
    
    coordinator = get_agent_coordinator()
    results = await coordinator.run_intake_pipeline(context)
    
    return {
        "foundation": results.get("foundation"),
        "planning": results.get("planning")
    }
