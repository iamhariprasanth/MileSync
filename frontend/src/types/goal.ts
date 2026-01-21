export type GoalCategory = 'health' | 'career' | 'education' | 'finance' | 'personal' | 'other';
export type GoalStatus = 'active' | 'completed' | 'paused' | 'abandoned';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'skipped';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;
  milestone_id: number;
  goal_id: number;
  title: string;
  description: string | null;
  due_date: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  completed_at: string | null;
  created_at: string;
}

export interface Milestone {
  id: number;
  goal_id: number;
  title: string;
  description: string | null;
  target_date: string | null;
  order: number;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
  tasks: Task[];
}

export interface Goal {
  id: number;
  user_id: number;
  chat_session_id: number | null;
  title: string;
  description: string | null;
  category: GoalCategory;
  target_date: string | null;
  status: GoalStatus;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface GoalWithMilestones extends Goal {
  milestones: Milestone[];
}

export interface GoalListItem {
  id: number;
  title: string;
  description: string | null;
  category: GoalCategory;
  target_date: string | null;
  status: GoalStatus;
  progress: number;
  milestone_count: number;
  task_count: number;
  completed_task_count: number;
  created_at: string;
}

export interface GoalCreate {
  title: string;
  description?: string;
  category: GoalCategory;
  target_date?: string;
}

export interface GoalUpdate {
  title?: string;
  description?: string;
  category?: GoalCategory;
  target_date?: string;
  status?: GoalStatus;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  due_date?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
}

export interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
  priority?: TaskPriority;
}

export interface MilestoneCreate {
  title: string;
  description?: string;
  target_date?: string;
}

export interface MilestoneUpdate {
  title?: string;
  description?: string;
  target_date?: string;
  is_completed?: boolean;
}

export interface FinalizeWithGoalResponse {
  goal: Goal;
  message: string;
}

export interface UpcomingTask {
  id: number;
  title: string;
  goal_id: number;
  goal_title: string;
  due_date: string | null;
  priority: TaskPriority;
}

export interface DashboardStats {
  active_goals: number;
  completed_tasks: number;
  total_tasks: number;
  completion_rate: number;
  current_streak: number;
  upcoming_tasks: UpcomingTask[];
}
