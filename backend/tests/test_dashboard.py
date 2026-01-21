"""Tests for dashboard API endpoints."""

import pytest
from datetime import datetime
from sqlmodel import Session

from app.models.goal import Goal, Milestone, Task, GoalStatus, TaskStatus


class TestDashboardStats:
    """Tests for GET /api/dashboard/stats endpoint."""

    def test_get_stats_empty(self, client, auth_headers):
        """Test dashboard stats with no data."""
        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["active_goals"] == 0
        assert data["completed_tasks"] == 0
        assert data["total_tasks"] == 0
        assert data["completion_rate"] == 0
        assert data["current_streak"] == 0
        assert data["upcoming_tasks"] == []

    def test_get_stats_with_goals(
        self, client, auth_headers, session, test_goal, test_milestone, test_task
    ):
        """Test dashboard stats with existing data."""
        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["active_goals"] == 1
        assert data["total_tasks"] == 1
        assert data["completed_tasks"] == 0
        assert data["completion_rate"] == 0
        assert len(data["upcoming_tasks"]) == 1
        assert data["upcoming_tasks"][0]["title"] == "Test Task"

    def test_get_stats_with_completed_tasks(
        self, client, auth_headers, session, test_goal, test_milestone
    ):
        """Test dashboard stats with completed tasks."""
        # Create 3 tasks, 2 completed
        for i in range(3):
            task = Task(
                milestone_id=test_milestone.id,
                goal_id=test_goal.id,
                title=f"Task {i}",
                status=TaskStatus.COMPLETED if i < 2 else TaskStatus.PENDING,
                completed_at=datetime.utcnow() if i < 2 else None,
            )
            session.add(task)
        session.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total_tasks"] == 3
        assert data["completed_tasks"] == 2
        assert data["completion_rate"] == 66  # 2/3 = 66%

    def test_get_stats_requires_auth(self, client):
        """Test that auth is required for dashboard stats."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 401

    def test_upcoming_tasks_only_from_active_goals(
        self, client, auth_headers, session, test_user
    ):
        """Test that upcoming tasks only come from active goals."""
        # Create completed goal with task
        completed_goal = Goal(
            user_id=test_user.id,
            title="Completed Goal",
            status=GoalStatus.COMPLETED,
        )
        session.add(completed_goal)
        session.commit()

        milestone = Milestone(
            goal_id=completed_goal.id,
            title="Milestone",
            order=0,
        )
        session.add(milestone)
        session.commit()

        task = Task(
            milestone_id=milestone.id,
            goal_id=completed_goal.id,
            title="Completed Goal Task",
            status=TaskStatus.PENDING,
        )
        session.add(task)
        session.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Should not include tasks from completed goals
        assert data["active_goals"] == 0
        assert len(data["upcoming_tasks"]) == 0
