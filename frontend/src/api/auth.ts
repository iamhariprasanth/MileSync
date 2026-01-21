import { api } from './client';
import type { User, LoginRequest, RegisterRequest, AuthResponse } from '../types/user';

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await api.post('/api/auth/login', data);
  return response.data;
}

export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await api.post('/api/auth/register', data);
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get('/api/auth/me');
  return response.data;
}

export function getGoogleAuthUrl(): string {
  return '/api/auth/google';
}

export function getGitHubAuthUrl(): string {
  return '/api/auth/github';
}
