"""Tests for milestone and task CRUD API endpoints."""

import pytest
from sqlmodel import Session

from app.models.goal import Milestone, Task, TaskStatus, TaskPriority


class TestMilestoneEndpoints:
    """Tests for milestone CRUD endpoints."""

    def test_create_milestone(self, client, auth_headers, test_goal):
        """Test creating a new milestone."""
        response = client.post(
            f"/api/goals/{test_goal.id}/milestones",
            headers=auth_headers,
            json={"title": "New Milestone", "description": "A new milestone"},
        )
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "New Milestone"
        assert data["description"] == "A new milestone"
        assert data["goal_id"] == test_goal.id

    def test_create_milestone_minimal(self, client, auth_headers, test_goal):
        """Test creating a milestone with minimal data."""
        response = client.post(
            f"/api/goals/{test_goal.id}/milestones",
            headers=auth_headers,
            json={"title": "Minimal Milestone"},
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Minimal Milestone"

    def test_create_milestone_invalid_goal(self, client, auth_headers):
        """Test creating milestone for non-existent goal."""
        response = client.post(
            "/api/goals/99999/milestones",
            headers=auth_headers,
            json={"title": "Test"},
        )
        assert response.status_code == 404

    def test_update_milestone(self, client, auth_headers, test_goal, test_milestone):
        """Test updating a milestone."""
        response = client.put(
            f"/api/goals/{test_goal.id}/milestones/{test_milestone.id}",
            headers=auth_headers,
            json={"title": "Updated Milestone", "description": "Updated description"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Milestone"
        assert data["description"] == "Updated description"

    def test_update_milestone_partial(self, client, auth_headers, test_goal, test_milestone):
        """Test partial update of milestone."""
        response = client.put(
            f"/api/goals/{test_goal.id}/milestones/{test_milestone.id}",
            headers=auth_headers,
            json={"title": "Only Title Updated"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Only Title Updated"

    def test_update_milestone_not_found(self, client, auth_headers, test_goal):
        """Test updating non-existent milestone."""
        response = client.put(
            f"/api/goals/{test_goal.id}/milestones/99999",
            headers=auth_headers,
            json={"title": "Test"},
        )
        assert response.status_code == 404

    def test_delete_milestone(self, client, auth_headers, session, test_goal, test_milestone):
        """Test deleting a milestone."""
        response = client.delete(
            f"/api/goals/{test_goal.id}/milestones/{test_milestone.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify milestone is deleted
        milestone = session.get(Milestone, test_milestone.id)
        assert milestone is None

    def test_delete_milestone_cascades_tasks(
        self, client, auth_headers, session, test_goal, test_milestone, test_task
    ):
        """Test that deleting milestone also deletes its tasks."""
        task_id = test_task.id

        response = client.delete(
            f"/api/goals/{test_goal.id}/milestones/{test_milestone.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify task is also deleted
        task = session.get(Task, task_id)
        assert task is None

    def test_milestone_requires_auth(self, client, test_goal):
        """Test that milestone endpoints require authentication."""
        response = client.post(
            f"/api/goals/{test_goal.id}/milestones",
            json={"title": "Test"},
        )
        assert response.status_code == 401


class TestTaskEndpoints:
    """Tests for task CRUD endpoints."""

    def test_create_task(self, client, auth_headers, test_goal, test_milestone):
        """Test creating a new task."""
        response = client.post(
            f"/api/goals/{test_goal.id}/tasks?milestone_id={test_milestone.id}",
            headers=auth_headers,
            json={"title": "New Task", "priority": "high"},
        )
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "New Task"
        assert data["priority"] == "high"
        assert data["goal_id"] == test_goal.id
        assert data["milestone_id"] == test_milestone.id

    def test_create_task_default_priority(self, client, auth_headers, test_goal, test_milestone):
        """Test creating task with default priority."""
        response = client.post(
            f"/api/goals/{test_goal.id}/tasks?milestone_id={test_milestone.id}",
            headers=auth_headers,
            json={"title": "Task with Default Priority"},
        )
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"

    def test_create_task_invalid_goal(self, client, auth_headers, test_milestone):
        """Test creating task for non-existent goal."""
        response = client.post(
            f"/api/goals/99999/tasks?milestone_id={test_milestone.id}",
            headers=auth_headers,
            json={"title": "Test"},
        )
        assert response.status_code == 404

    def test_update_task(self, client, auth_headers, test_goal, test_task):
        """Test updating a task."""
        response = client.put(
            f"/api/goals/{test_goal.id}/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "Updated Task", "priority": "high"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["priority"] == "high"

    def test_update_task_status(self, client, auth_headers, test_goal, test_task):
        """Test updating task status."""
        response = client.put(
            f"/api/goals/{test_goal.id}/tasks/{test_task.id}",
            headers=auth_headers,
            json={"status": "completed"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert response.json()["completed_at"] is not None

    def test_delete_task(self, client, auth_headers, session, test_goal, test_task):
        """Test deleting a task."""
        task_id = test_task.id

        response = client.delete(
            f"/api/goals/{test_goal.id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify task is deleted
        task = session.get(Task, task_id)
        assert task is None

    def test_delete_task_not_found(self, client, auth_headers, test_goal):
        """Test deleting non-existent task."""
        response = client.delete(
            f"/api/goals/{test_goal.id}/tasks/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_complete_task(self, client, auth_headers, test_goal, test_task):
        """Test marking task as completed."""
        response = client.post(
            f"/api/goals/{test_goal.id}/tasks/{test_task.id}/complete",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_uncomplete_task(self, client, auth_headers, session, test_goal, test_task):
        """Test marking task as pending (uncomplete)."""
        # First complete the task
        test_task.status = TaskStatus.COMPLETED
        session.add(test_task)
        session.commit()

        response = client.post(
            f"/api/goals/{test_goal.id}/tasks/{test_task.id}/uncomplete",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    def test_task_requires_auth(self, client, test_goal, test_milestone):
        """Test that task endpoints require authentication."""
        response = client.post(
            f"/api/goals/{test_goal.id}/tasks?milestone_id={test_milestone.id}",
            json={"title": "Test"},
        )
        assert response.status_code == 401


class TestGoalProgressUpdate:
    """Tests for goal progress updates when tasks change."""

    def test_progress_updates_on_complete(
        self, client, auth_headers, session, test_goal, test_milestone
    ):
        """Test that goal progress updates when task is completed."""
        # Create 2 tasks
        for i in range(2):
            task = Task(
                milestone_id=test_milestone.id,
                goal_id=test_goal.id,
                title=f"Task {i}",
            )
            session.add(task)
        session.commit()

        # Get task IDs
        tasks = session.query(Task).filter(Task.goal_id == test_goal.id).all()
        task_id = tasks[0].id

        # Complete one task
        client.post(
            f"/api/goals/{test_goal.id}/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        # Check goal progress
        response = client.get(f"/api/goals/{test_goal.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["progress"] == 50  # 1 of 2 tasks

    def test_progress_updates_on_delete(
        self, client, auth_headers, session, test_goal, test_milestone
    ):
        """Test that goal progress updates when task is deleted."""
        # Create 2 tasks, one completed
        completed_task = Task(
            milestone_id=test_milestone.id,
            goal_id=test_goal.id,
            title="Completed Task",
            status=TaskStatus.COMPLETED,
        )
        pending_task = Task(
            milestone_id=test_milestone.id,
            goal_id=test_goal.id,
            title="Pending Task",
            status=TaskStatus.PENDING,
        )
        session.add(completed_task)
        session.add(pending_task)
        session.commit()

        # Delete pending task
        client.delete(
            f"/api/goals/{test_goal.id}/tasks/{pending_task.id}",
            headers=auth_headers,
        )

        # Check goal progress (should be 100% now)
        response = client.get(f"/api/goals/{test_goal.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["progress"] == 100
