"""Pytest configuration and fixtures for MileSync tests."""

import pytest
from datetime import datetime
from typing import Generator

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.goal import Goal, Milestone, Task, GoalCategory, GoalStatus, TaskStatus
from app.services.auth_service import hash_password, create_access_token


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("testpassword123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User) -> dict:
    """Create authorization headers for test user."""
    token = create_access_token(user_id=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="test_goal")
def test_goal_fixture(session: Session, test_user: User) -> Goal:
    """Create a test goal."""
    goal = Goal(
        user_id=test_user.id,
        title="Test Goal",
        description="A test goal for unit tests",
        category=GoalCategory.PERSONAL,
        status=GoalStatus.ACTIVE,
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@pytest.fixture(name="test_milestone")
def test_milestone_fixture(session: Session, test_goal: Goal) -> Milestone:
    """Create a test milestone."""
    milestone = Milestone(
        goal_id=test_goal.id,
        title="Test Milestone",
        description="A test milestone",
        order=0,
    )
    session.add(milestone)
    session.commit()
    session.refresh(milestone)
    return milestone


@pytest.fixture(name="test_task")
def test_task_fixture(session: Session, test_goal: Goal, test_milestone: Milestone) -> Task:
    """Create a test task."""
    task = Task(
        milestone_id=test_milestone.id,
        goal_id=test_goal.id,
        title="Test Task",
        description="A test task",
        status=TaskStatus.PENDING,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
