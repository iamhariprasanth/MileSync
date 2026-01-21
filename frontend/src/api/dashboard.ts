import { api } from './client';
import type { DashboardStats } from '../types/goal';

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await api.get('/api/dashboard/stats');
  return response.data;
}
