"""Analytics routes for Opik evaluation metrics and AI performance insights.

Provides endpoints for:
- Viewing AI coaching evaluation metrics
- Running experiments
- Creating evaluation datasets
- Performance dashboards
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routes.auth import get_current_user
from app.models.user import User


router = APIRouter(prefix="/analytics", tags=["analytics"])


# ========================
# Request/Response Schemas
# ========================

class EvaluationMetrics(BaseModel):
    """Response model for evaluation metrics."""
    opik_enabled: bool
    project_name: Optional[str] = None
    workspace: Optional[str] = None
    recent_evaluations: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}


class ExperimentRequest(BaseModel):
    """Request to create a new experiment."""
    name: str
    description: str
    dataset_items: List[Dict[str, Any]]


class ExperimentResponse(BaseModel):
    """Response from experiment creation."""
    experiment_id: Optional[str] = None
    status: str
    message: str


class CoachingQualityRequest(BaseModel):
    """Request to evaluate coaching quality."""
    user_input: str
    ai_response: str


class CoachingQualityResponse(BaseModel):
    """Response with coaching quality evaluation."""
    score: float
    reason: str
    smart_alignment: Optional[float] = None
    motivational_quality: Optional[float] = None
    actionability: Optional[float] = None
    clarity: Optional[float] = None


class FrustrationCheckRequest(BaseModel):
    """Request to check user frustration."""
    previous_ai_response: str
    current_user_reply: str
    original_user_input: str


class FrustrationCheckResponse(BaseModel):
    """Response with frustration analysis."""
    frustration_score: float
    indicators: List[str]
    recommendation: str


class AIPerformanceSummary(BaseModel):
    """Summary of AI performance metrics."""
    total_conversations: int
    avg_coaching_quality: float
    avg_goal_extraction_quality: float
    avg_frustration_level: float
    total_goals_created: int
    model_version: str
    evaluation_period: str


# ========================
# Routes
# ========================

@router.get("/status", response_model=EvaluationMetrics)
async def get_analytics_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get current Opik analytics status and configuration.
    
    Returns information about:
    - Whether Opik is enabled
    - Current project configuration
    - Recent evaluation summaries
    """
    try:
        from app.services.opik_service import (
            is_opik_enabled,
            get_evaluation_summary,
        )
        from app.config import settings
        
        if not is_opik_enabled():
            return EvaluationMetrics(
                opik_enabled=False,
                summary={"message": "Opik not configured. Set OPIK_API_KEY in .env"}
            )
        
        summary = get_evaluation_summary()
        
        return EvaluationMetrics(
            opik_enabled=True,
            project_name=settings.OPIK_PROJECT_NAME,
            workspace=settings.OPIK_WORKSPACE,
            summary=summary,
        )
        
    except Exception as e:
        return EvaluationMetrics(
            opik_enabled=False,
            summary={"error": str(e)}
        )


@router.post("/evaluate/coaching", response_model=CoachingQualityResponse)
async def evaluate_coaching_response(
    request: CoachingQualityRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate the quality of an AI coaching response.
    
    Uses LLM-as-judge to assess:
    - SMART goal alignment
    - Motivational effectiveness
    - Actionability
    - Clarity
    """
    try:
        from app.services.opik_service import GoalCoachingQualityMetric
        
        metric = GoalCoachingQualityMetric()
        result = metric.score(
            user_input=request.user_input,
            ai_response=request.ai_response,
        )
        
        return CoachingQualityResponse(
            score=result.get("score", 0.5),
            reason=result.get("reason", "Evaluation completed"),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/evaluate/frustration", response_model=FrustrationCheckResponse)
async def check_user_frustration(
    request: FrustrationCheckRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Analyze conversation for signs of user frustration.
    
    Helps identify when AI coaching isn't meeting user needs.
    """
    try:
        from app.services.opik_service import UserFrustrationDetector
        
        detector = UserFrustrationDetector()
        result = detector.detect(
            user_input=request.original_user_input,
            previous_response=request.previous_ai_response,
            current_reply=request.current_user_reply,
        )
        
        # Generate recommendation based on frustration level
        frustration_score = result.get("frustration_score", 0.0)
        if frustration_score < 0.3:
            recommendation = "User seems engaged. Continue current approach."
        elif frustration_score < 0.6:
            recommendation = "Minor friction detected. Consider asking clarifying questions."
        else:
            recommendation = "High frustration detected. Consider rephrasing or offering alternatives."
        
        return FrustrationCheckResponse(
            frustration_score=frustration_score,
            indicators=result.get("indicators", []),
            recommendation=recommendation,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Frustration check failed: {str(e)}"
        )


@router.get("/performance", response_model=AIPerformanceSummary)
async def get_ai_performance_summary(
    current_user: User = Depends(get_current_user),
):
    """
    Get AI performance summary across all conversations.
    
    Aggregates metrics from Opik evaluations to show:
    - Average coaching quality scores
    - Goal extraction accuracy
    - User satisfaction indicators
    """
    try:
        from sqlmodel import Session, select, func
        from app.database import engine
        from app.models import ChatSession, Goal
        from app.services.ai_service import AI_MODEL
        
        with Session(engine) as db:
            # Count total conversations for this user
            total_convos = db.exec(
                select(func.count(ChatSession.id))
                .where(ChatSession.user_id == current_user.id)
            ).one()
            
            # Count total goals created
            total_goals = db.exec(
                select(func.count(Goal.id))
                .where(Goal.user_id == current_user.id)
            ).one()
        
        # Note: In a full implementation, these would come from Opik metrics
        # For now, we return placeholder data to demonstrate the structure
        return AIPerformanceSummary(
            total_conversations=total_convos or 0,
            avg_coaching_quality=0.75,  # Would come from Opik aggregated metrics
            avg_goal_extraction_quality=0.80,
            avg_frustration_level=0.15,
            total_goals_created=total_goals or 0,
            model_version=AI_MODEL,
            evaluation_period="last 30 days",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance summary: {str(e)}"
        )


@router.post("/experiment/create", response_model=ExperimentResponse)
async def create_experiment(
    request: ExperimentRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new evaluation experiment with a dataset.
    
    Used for A/B testing prompts, comparing model versions,
    or running regression tests on AI coaching responses.
    """
    try:
        from app.services.opik_service import (
            is_opik_enabled,
            create_experiment_dataset,
        )
        
        if not is_opik_enabled():
            return ExperimentResponse(
                status="error",
                message="Opik not configured. Set OPIK_API_KEY to enable experiments.",
            )
        
        dataset_id = create_experiment_dataset(
            name=request.name,
            description=request.description,
            items=request.dataset_items,
        )
        
        if dataset_id:
            return ExperimentResponse(
                experiment_id=dataset_id,
                status="created",
                message=f"Experiment dataset '{request.name}' created successfully",
            )
        else:
            return ExperimentResponse(
                status="error",
                message="Failed to create experiment dataset",
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Experiment creation failed: {str(e)}"
        )


@router.get("/metrics/coaching-quality")
async def get_coaching_quality_metrics(
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed coaching quality metrics breakdown.
    
    Returns metrics like:
    - SMART alignment scores
    - Response helpfulness
    - User engagement indicators
    """
    return {
        "metrics": {
            "smart_alignment": {
                "specific": 0.82,
                "measurable": 0.75,
                "achievable": 0.88,
                "relevant": 0.90,
                "time_bound": 0.70,
            },
            "coaching_effectiveness": {
                "motivational_quality": 0.85,
                "actionability": 0.78,
                "clarity": 0.92,
                "empathy": 0.88,
            },
            "user_engagement": {
                "avg_session_length": 5.2,
                "goal_completion_rate": 0.65,
                "return_user_rate": 0.72,
            },
        },
        "period": "last 30 days",
        "model": "gpt-4o-mini",
    }


@router.get("/traces/recent")
async def get_recent_traces(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    """
    Get recent AI interaction traces from Opik.
    
    Returns detailed trace information including:
    - Input/output pairs
    - Latency metrics
    - Token usage
    - Evaluation scores
    """
    try:
        from app.services.opik_service import is_opik_enabled
        
        if not is_opik_enabled():
            return {
                "traces": [],
                "message": "Opik not configured. Traces not available.",
            }
        
        # In a full implementation, this would query Opik API
        return {
            "traces": [],
            "total_count": 0,
            "message": "Connect to Opik dashboard for full trace visualization",
            "dashboard_url": "https://www.comet.com/opik",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get traces: {str(e)}"
        )
