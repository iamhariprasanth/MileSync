"""Goals routes for managing user goals, milestones, and tasks."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models.goal import Goal, Task, TaskStatus
from app.models.user import User
from app.schemas.goal import (
    GoalCreate,
    GoalListItem,
    GoalResponse,
    GoalUpdate,
    GoalWithMilestones,
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services import goal_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=List[GoalListItem])
async def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all goals for the current user.

    Returns goals with summary statistics (milestone count, task count, progress).
    """
    return goal_service.get_goals_for_user(db, current_user.id)


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new goal manually (without chat).

    For goals created through chat, use the /chat/{id}/finalize endpoint.
    """
    goal = goal_service.create_goal(db, current_user.id, data)
    return GoalResponse.model_validate(goal)


@router.get("/{goal_id}", response_model=GoalWithMilestones)
async def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a goal with all its milestones and tasks.

    Returns the complete roadmap structure for displaying the goal detail page.
    """
    goal = goal_service.get_goal_with_milestones(db, goal_id, current_user.id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a goal's information.
    """
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    updated_goal = goal_service.update_goal(db, goal, data)
    return GoalResponse.model_validate(updated_goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a goal and all its milestones and tasks.
    """
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    goal_service.delete_goal(db, goal)


# ===================
# Task Routes
# ===================


@router.put("/{goal_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    goal_id: int,
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a task's status or other properties.

    Commonly used to mark tasks as completed.
    """
    # Verify goal ownership first
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    task = db.get(Task, task_id)
    if not task or task.goal_id != goal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update task fields
    update_data = data.model_dump(exclude_unset=True)

    # Handle status change specially to update progress
    if "status" in update_data:
        updated_task = goal_service.update_task_status(
            db, task_id, current_user.id, update_data["status"]
        )
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        # Apply other updates if any
        del update_data["status"]
        if update_data:
            for key, value in update_data.items():
                setattr(updated_task, key, value)
            db.add(updated_task)
            db.commit()
            db.refresh(updated_task)
        return TaskResponse.model_validate(updated_task)

    # Non-status updates
    for key, value in update_data.items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.post("/{goal_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    goal_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as completed.

    Convenience endpoint for quickly completing tasks.
    """
    # Verify goal ownership
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    task = goal_service.update_task_status(
        db, task_id, current_user.id, TaskStatus.COMPLETED
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.post("/{goal_id}/tasks/{task_id}/uncomplete", response_model=TaskResponse)
async def uncomplete_task(
    goal_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as pending (undo completion).
    """
    # Verify goal ownership
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    task = goal_service.update_task_status(
        db, task_id, current_user.id, TaskStatus.PENDING
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.post("/{goal_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    goal_id: int,
    milestone_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task within a milestone.
    """
    task = goal_service.create_task(db, goal_id, milestone_id, current_user.id, data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal or milestone not found",
        )

    return TaskResponse.model_validate(task)


@router.delete("/{goal_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    goal_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a task.
    """
    # Verify goal ownership
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    task = db.get(Task, task_id)
    if not task or task.goal_id != goal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    goal_service.delete_task(db, task)


# ===================
# Milestone Routes
# ===================


@router.post("/{goal_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    goal_id: int,
    data: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new milestone for a goal.
    """
    milestone = goal_service.create_milestone(db, goal_id, current_user.id, data)

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return MilestoneResponse.model_validate(milestone)


@router.put("/{goal_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    goal_id: int,
    milestone_id: int,
    data: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a milestone's information.
    """
    # Verify goal ownership
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    milestone = goal_service.get_milestone_by_id(db, milestone_id, current_user.id)
    if not milestone or milestone.goal_id != goal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    updated = goal_service.update_milestone(db, milestone, data)
    return MilestoneResponse.model_validate(updated)


@router.delete("/{goal_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    goal_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a milestone and all its tasks.
    """
    # Verify goal ownership
    goal = goal_service.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    milestone = goal_service.get_milestone_by_id(db, milestone_id, current_user.id)
    if not milestone or milestone.goal_id != goal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    goal_service.delete_milestone(db, milestone)
