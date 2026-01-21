"""Dashboard routes for user statistics and overview."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_db
from app.models.user import User
from app.schemas.goal import DashboardStats
from app.services import goal_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get dashboard statistics for the current user.

    Returns active goals count, completed tasks, streak, and upcoming tasks.
    """
    return goal_service.get_dashboard_stats(db, current_user.id)
