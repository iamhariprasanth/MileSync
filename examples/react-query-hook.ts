// Example: React Query Hook Pattern
// This shows how to create custom hooks for API calls in MileSync

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Goal, GoalCreate } from '../types/goal';

// Query keys - centralized for cache invalidation
export const goalKeys = {
  all: ['goals'] as const,
  lists: () => [...goalKeys.all, 'list'] as const,
  list: (filters: string) => [...goalKeys.lists(), { filters }] as const,
  details: () => [...goalKeys.all, 'detail'] as const,
  detail: (id: number) => [...goalKeys.details(), id] as const,
};

// Fetch all goals
export function useGoals() {
  return useQuery({
    queryKey: goalKeys.lists(),
    queryFn: async (): Promise<Goal[]> => {
      const response = await api.get('/goals');
      return response.data;
    },
  });
}

// Fetch single goal
export function useGoal(id: number) {
  return useQuery({
    queryKey: goalKeys.detail(id),
    queryFn: async (): Promise<Goal> => {
      const response = await api.get(`/goals/${id}`);
      return response.data;
    },
    enabled: !!id, // Only fetch when id is provided
  });
}

// Create goal mutation
export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: GoalCreate): Promise<Goal> => {
      const response = await api.post('/goals', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate goals list to refetch
      queryClient.invalidateQueries({ queryKey: goalKeys.lists() });
    },
  });
}

// Update goal mutation
export function useUpdateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<Goal> }): Promise<Goal> => {
      const response = await api.put(`/goals/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: goalKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: goalKeys.lists() });
    },
  });
}

// Delete goal mutation
export function useDeleteGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      await api.delete(`/goals/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: goalKeys.lists() });
    },
  });
}
