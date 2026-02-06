"""Goal service for CRUD operations and business logic."""

from datetime import datetime, date
from typing import List, Optional

from sqlmodel import Session, select, func

from app.models.goal import (
    Goal,
    GoalCategory,
    GoalStatus,
    Milestone,
    Task,
    TaskPriority,
    TaskStatus,
)
from app.schemas.goal import (
    AIGoalGeneration,
    DashboardStats,
    GoalCreate,
    GoalListItem,
    GoalUpdate,
    GoalWithMilestones,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneWithTasks,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    UpcomingTask,
)


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_category(category_str: str) -> GoalCategory:
    """Parse category string to enum."""
    try:
        return GoalCategory(category_str.lower())
    except ValueError:
        return GoalCategory.OTHER


def parse_priority(priority_str: str) -> TaskPriority:
    """Parse priority string to enum."""
    try:
        return TaskPriority(priority_str.lower())
    except ValueError:
        return TaskPriority.MEDIUM


# ===================
# Goal Operations
# ===================


def create_goal(db: Session, user_id: int, data: GoalCreate) -> Goal:
    """Create a new goal."""
    goal = Goal(
        user_id=user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        target_date=data.target_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def create_goal_from_ai(
    db: Session,
    user_id: int,
    chat_session_id: int,
    data: AIGoalGeneration,
) -> Goal:
    """
    Create a complete goal with milestones and tasks from AI generation.

    Args:
        db: Database session
        user_id: User's ID
        chat_session_id: Chat session that generated this goal
        data: AI-generated goal structure

    Returns:
        Created goal with all nested entities
    """
    # Create the goal
    goal = Goal(
        user_id=user_id,
        chat_session_id=chat_session_id,
        title=data.title,
        description=data.description,
        category=parse_category(data.category),
        target_date=parse_date(data.target_date),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    # Create milestones and tasks
    for order, milestone_data in enumerate(data.milestones):
        milestone = Milestone(
            goal_id=goal.id,
            title=milestone_data.title,
            description=milestone_data.description,
            target_date=parse_date(milestone_data.target_date),
            order=order,
        )
        db.add(milestone)
        db.commit()
        db.refresh(milestone)

        # Create tasks for this milestone
        for task_data in milestone_data.tasks:
            task = Task(
                milestone_id=milestone.id,
                goal_id=goal.id,
                title=task_data.title,
                description=task_data.description,
                priority=parse_priority(task_data.priority),
            )
            db.add(task)

    db.commit()
    return goal


def get_goal_by_id(db: Session, goal_id: int, user_id: int) -> Optional[Goal]:
    """Get a goal by ID, verifying ownership."""
    statement = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    return db.exec(statement).first()


def get_goals_for_user(db: Session, user_id: int) -> List[GoalListItem]:
    """Get all goals for a user with summary stats."""
    statement = (
        select(Goal)
        .where(Goal.user_id == user_id)
        .order_by(Goal.created_at.desc())
    )
    goals = db.exec(statement).all()

    result = []
    for goal in goals:
        # Count milestones
        milestone_count = db.exec(
            select(func.count(Milestone.id)).where(Milestone.goal_id == goal.id)
        ).one()

        # Count tasks
        task_count = db.exec(
            select(func.count(Task.id)).where(Task.goal_id == goal.id)
        ).one()

        # Count completed tasks
        completed_count = db.exec(
            select(func.count(Task.id)).where(
                Task.goal_id == goal.id,
                Task.status == TaskStatus.COMPLETED,
            )
        ).one()

        result.append(GoalListItem(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            category=goal.category,
            target_date=goal.target_date,
            status=goal.status,
            progress=goal.progress,
            milestone_count=milestone_count,
            task_count=task_count,
            completed_task_count=completed_count,
            created_at=goal.created_at,
        ))

    return result


def get_goal_with_milestones(
    db: Session,
    goal_id: int,
    user_id: int,
) -> Optional[GoalWithMilestones]:
    """Get a goal with all its milestones and tasks."""
    goal = get_goal_by_id(db, goal_id, user_id)
    if not goal:
        return None

    # Get milestones
    milestones_stmt = (
        select(Milestone)
        .where(Milestone.goal_id == goal_id)
        .order_by(Milestone.order)
    )
    milestones = db.exec(milestones_stmt).all()

    milestone_responses = []
    for milestone in milestones:
        # Get tasks for this milestone
        tasks_stmt = (
            select(Task)
            .where(Task.milestone_id == milestone.id)
            .order_by(Task.created_at)
        )
        tasks = db.exec(tasks_stmt).all()

        milestone_responses.append(MilestoneWithTasks(
            id=milestone.id,
            goal_id=milestone.goal_id,
            title=milestone.title,
            description=milestone.description,
            target_date=milestone.target_date,
            order=milestone.order,
            is_completed=milestone.is_completed,
            completed_at=milestone.completed_at,
            created_at=milestone.created_at,
            tasks=[TaskResponse.model_validate(t) for t in tasks],
        ))

    return GoalWithMilestones(
        id=goal.id,
        user_id=goal.user_id,
        chat_session_id=goal.chat_session_id,
        title=goal.title,
        description=goal.description,
        category=goal.category,
        target_date=goal.target_date,
        status=goal.status,
        progress=goal.progress,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
        milestones=milestone_responses,
    )


def update_goal(db: Session, goal: Goal, data: GoalUpdate) -> Goal:
    """Update a goal's basic information."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)
    goal.updated_at = datetime.utcnow()
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, goal: Goal) -> None:
    """Delete a goal and all its milestones and tasks."""
    # Delete tasks first
    tasks = db.exec(select(Task).where(Task.goal_id == goal.id)).all()
    for task in tasks:
        db.delete(task)

    # Delete milestones
    milestones = db.exec(select(Milestone).where(Milestone.goal_id == goal.id)).all()
    for milestone in milestones:
        db.delete(milestone)

    # Delete goal
    db.delete(goal)
    db.commit()


def update_goal_progress(db: Session, goal_id: int) -> None:
    """Recalculate and update goal progress based on completed tasks."""
    # Count total and completed tasks
    total = db.exec(
        select(func.count(Task.id)).where(Task.goal_id == goal_id)
    ).one()

    if total == 0:
        return

    completed = db.exec(
        select(func.count(Task.id)).where(
            Task.goal_id == goal_id,
            Task.status == TaskStatus.COMPLETED,
        )
    ).one()

    progress = int((completed / total) * 100)

    goal = db.get(Goal, goal_id)
    if goal:
        goal.progress = progress
        goal.updated_at = datetime.utcnow()
        db.add(goal)
        db.commit()


# ===================
# Task Operations
# ===================


def update_task_status(
    db: Session,
    task_id: int,
    user_id: int,
    status: TaskStatus,
) -> Optional[Task]:
    """Update a task's status, verifying ownership through goal."""
    task = db.get(Task, task_id)
    if not task:
        return None

    # Verify ownership
    goal = db.get(Goal, task.goal_id)
    if not goal or goal.user_id != user_id:
        return None

    task.status = status
    if status == TaskStatus.COMPLETED:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    db.add(task)
    db.commit()
    db.refresh(task)

    # Update goal progress
    update_goal_progress(db, task.goal_id)

    # Check if milestone should be marked complete
    check_milestone_completion(db, task.milestone_id)

    return task


def check_milestone_completion(db: Session, milestone_id: int) -> None:
    """Check and update milestone completion status."""
    milestone = db.get(Milestone, milestone_id)
    if not milestone:
        return

    # Count incomplete tasks
    incomplete = db.exec(
        select(func.count(Task.id)).where(
            Task.milestone_id == milestone_id,
            Task.status != TaskStatus.COMPLETED,
            Task.status != TaskStatus.SKIPPED,
        )
    ).one()

    was_completed = milestone.is_completed
    milestone.is_completed = incomplete == 0

    if milestone.is_completed and not was_completed:
        milestone.completed_at = datetime.utcnow()
    elif not milestone.is_completed:
        milestone.completed_at = None

    db.add(milestone)
    db.commit()


# ===================
# Dashboard Operations
# ===================


def get_dashboard_stats(db: Session, user_id: int) -> DashboardStats:
    """
    Get dashboard statistics for a user.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        Dashboard statistics including counts and upcoming tasks
    """
    # Count active goals
    active_goals = db.exec(
        select(func.count(Goal.id)).where(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.ACTIVE,
        )
    ).one()

    # Count total tasks for user's goals
    total_tasks = db.exec(
        select(func.count(Task.id))
        .join(Goal, Task.goal_id == Goal.id)
        .where(Goal.user_id == user_id)
    ).one()

    # Count completed tasks
    completed_tasks = db.exec(
        select(func.count(Task.id))
        .join(Goal, Task.goal_id == Goal.id)
        .where(
            Goal.user_id == user_id,
            Task.status == TaskStatus.COMPLETED,
        )
    ).one()

    # Calculate completion rate
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = int((completed_tasks / total_tasks) * 100)

    # Calculate streak (consecutive days with completed tasks)
    current_streak = _calculate_streak(db, user_id)

    # Get upcoming tasks (pending tasks, sorted by priority and due date)
    upcoming_tasks = _get_upcoming_tasks(db, user_id, limit=5)

    return DashboardStats(
        active_goals=active_goals,
        completed_tasks=completed_tasks,
        total_tasks=total_tasks,
        completion_rate=completion_rate,
        current_streak=current_streak,
        upcoming_tasks=upcoming_tasks,
    )


def _calculate_streak(db: Session, user_id: int) -> int:
    """
    Calculate the current streak of consecutive days with completed tasks.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        Number of consecutive days with completed tasks
    """
    from datetime import timedelta

    # Get all completion dates for the user
    # join with Goal to ensure user ownership
    results = db.exec(
        select(Task.completed_at)
        .join(Goal, Task.goal_id == Goal.id)
        .where(
            Goal.user_id == user_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at != None
        )
    ).all()

    if not results:
        return 0

    # Convert to set of dates
    completed_dates = {dt.date() for dt in results if dt}

    today = date.today()
    streak = 0
    current_date = today

    # Logic:
    # 1. Check if we have a streak continuing from today or yesterday
    # If today is completed, streak starts including today.
    # If today is NOT completed, but yesterday IS, streak starts from yesterday.
    # If neither, streak is 0.
    
    # Check today
    if current_date in completed_dates:
        streak += 1
        current_date -= timedelta(days=1)
        # Continue checking previous days
        while current_date in completed_dates:
            streak += 1
            current_date -= timedelta(days=1)
    else:
        # Check yesterday
        current_date -= timedelta(days=1)
        while current_date in completed_dates:
            streak += 1
            current_date -= timedelta(days=1)

    return streak


def _get_upcoming_tasks(db: Session, user_id: int, limit: int = 5) -> List[UpcomingTask]:
    """
    Get upcoming/pending tasks for a user.

    Args:
        db: Database session
        user_id: User's ID
        limit: Maximum number of tasks to return

    Returns:
        List of upcoming tasks with goal information
    """
    # 1. Get IDs of active goals for this user
    goal_stmt = select(Goal.id, Goal.title).where(
        Goal.user_id == user_id,
        Goal.status == GoalStatus.ACTIVE
    )
    active_goals_rows = db.exec(goal_stmt).all()
    
    if not active_goals_rows:
        return []
        
    active_goal_ids = [row[0] for row in active_goals_rows]
    goal_titles = {row[0]: row[1] for row in active_goals_rows}

    # 2. Get pending/in_progress tasks for these goals
    # We fetch all candidates and sort in Python to avoid complex SQL sorting with Enums/Nulls
    task_stmt = select(Task).where(
        Task.goal_id.in_(active_goal_ids),
        (Task.status == TaskStatus.PENDING) | (Task.status == TaskStatus.IN_PROGRESS)
    )
    tasks = db.exec(task_stmt).all()

    # Sort in Python: High priority first, then due date (earliest first, None last)
    priority_map = {
        TaskPriority.HIGH: 0,
        TaskPriority.MEDIUM: 1,
        TaskPriority.LOW: 2
    }
    
    def task_sort_key(t):
        prio_score = priority_map.get(t.priority, 1)
        # For due_date: if None, treat as very far future
        date_score = t.due_date if t.due_date else date.max
        return (prio_score, date_score)

    sorted_tasks = sorted(tasks, key=task_sort_key)[:limit]

    return [
        UpcomingTask(
            id=task.id,
            title=task.title,
            goal_id=task.goal_id,
            goal_title=goal_titles.get(task.goal_id, "Unknown Goal"),
            due_date=task.due_date,
            priority=task.priority,
        )
        for task in sorted_tasks
    ]


# ===================
# Milestone Operations
# ===================


def get_milestone_by_id(
    db: Session,
    milestone_id: int,
    user_id: int,
) -> Optional[Milestone]:
    """Get a milestone by ID, verifying ownership through goal."""
    milestone = db.get(Milestone, milestone_id)
    if not milestone:
        return None

    # Verify ownership through goal
    goal = db.get(Goal, milestone.goal_id)
    if not goal or goal.user_id != user_id:
        return None

    return milestone


def update_milestone(
    db: Session,
    milestone: Milestone,
    data: MilestoneUpdate,
) -> Milestone:
    """Update a milestone's information."""
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(milestone, key, value)

    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return milestone


def create_milestone(
    db: Session,
    goal_id: int,
    user_id: int,
    data: MilestoneCreate,
) -> Optional[Milestone]:
    """Create a new milestone for a goal."""
    # Verify goal ownership
    goal = get_goal_by_id(db, goal_id, user_id)
    if not goal:
        return None

    # Get the next order value
    max_order = db.exec(
        select(func.max(Milestone.order)).where(Milestone.goal_id == goal_id)
    ).one() or -1

    milestone = Milestone(
        goal_id=goal_id,
        title=data.title,
        description=data.description,
        target_date=data.target_date,
        order=max_order + 1,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return milestone


def delete_milestone(db: Session, milestone: Milestone) -> None:
    """Delete a milestone and all its tasks."""
    # Delete tasks first
    tasks = db.exec(select(Task).where(Task.milestone_id == milestone.id)).all()
    for task in tasks:
        db.delete(task)

    db.delete(milestone)
    db.commit()

    # Update goal progress
    update_goal_progress(db, milestone.goal_id)


def create_task(
    db: Session,
    goal_id: int,
    milestone_id: int,
    user_id: int,
    data: TaskCreate,
) -> Optional[Task]:
    """Create a new task for a milestone."""
    # Verify goal and milestone ownership
    goal = get_goal_by_id(db, goal_id, user_id)
    if not goal:
        return None

    milestone = db.get(Milestone, milestone_id)
    if not milestone or milestone.goal_id != goal_id:
        return None

    task = Task(
        milestone_id=milestone_id,
        goal_id=goal_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        priority=data.priority,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Update goal progress
    update_goal_progress(db, goal_id)

    return task


def delete_task(db: Session, task: Task) -> None:
    """Delete a task."""
    goal_id = task.goal_id
    milestone_id = task.milestone_id

    db.delete(task)
    db.commit()

    # Update goal progress
    update_goal_progress(db, goal_id)

    # Check milestone completion
    check_milestone_completion(db, milestone_id)
