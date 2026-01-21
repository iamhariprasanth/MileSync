import { api } from './client';
import type {
  Goal,
  GoalCreate,
  GoalListItem,
  GoalUpdate,
  GoalWithMilestones,
  Milestone,
  MilestoneCreate,
  MilestoneUpdate,
  Task,
  TaskCreate,
  TaskUpdate,
} from '../types/goal';

export async function listGoals(): Promise<GoalListItem[]> {
  const response = await api.get('/api/goals');
  return response.data;
}

export async function createGoal(data: GoalCreate): Promise<Goal> {
  const response = await api.post('/api/goals', data);
  return response.data;
}

export async function getGoal(goalId: number): Promise<GoalWithMilestones> {
  const response = await api.get(`/api/goals/${goalId}`);
  return response.data;
}

export async function updateGoal(goalId: number, data: GoalUpdate): Promise<Goal> {
  const response = await api.put(`/api/goals/${goalId}`, data);
  return response.data;
}

export async function deleteGoal(goalId: number): Promise<void> {
  await api.delete(`/api/goals/${goalId}`);
}

export async function updateTask(
  goalId: number,
  taskId: number,
  data: TaskUpdate
): Promise<Task> {
  const response = await api.put(`/api/goals/${goalId}/tasks/${taskId}`, data);
  return response.data;
}

export async function completeTask(goalId: number, taskId: number): Promise<Task> {
  const response = await api.post(`/api/goals/${goalId}/tasks/${taskId}/complete`);
  return response.data;
}

export async function uncompleteTask(goalId: number, taskId: number): Promise<Task> {
  const response = await api.post(`/api/goals/${goalId}/tasks/${taskId}/uncomplete`);
  return response.data;
}

export async function createTask(
  goalId: number,
  milestoneId: number,
  data: TaskCreate
): Promise<Task> {
  const response = await api.post(`/api/goals/${goalId}/tasks?milestone_id=${milestoneId}`, data);
  return response.data;
}

export async function deleteTask(goalId: number, taskId: number): Promise<void> {
  await api.delete(`/api/goals/${goalId}/tasks/${taskId}`);
}

export async function createMilestone(goalId: number, data: MilestoneCreate): Promise<Milestone> {
  const response = await api.post(`/api/goals/${goalId}/milestones`, data);
  return response.data;
}

export async function updateMilestone(
  goalId: number,
  milestoneId: number,
  data: MilestoneUpdate
): Promise<Milestone> {
  const response = await api.put(`/api/goals/${goalId}/milestones/${milestoneId}`, data);
  return response.data;
}

export async function deleteMilestone(goalId: number, milestoneId: number): Promise<void> {
  await api.delete(`/api/goals/${goalId}/milestones/${milestoneId}`);
}
