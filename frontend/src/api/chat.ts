import { api } from './client';
import type {
  ChatListItem,
  ChatSessionWithMessages,
  SendMessageRequest,
  SendMessageResponse,
  StartChatResponse,
} from '../types/chat';
import type { FinalizeWithGoalResponse } from '../types/goal';

export async function startChat(): Promise<StartChatResponse> {
  const response = await api.post('/api/chat/start');
  return response.data;
}

export async function listSessions(): Promise<ChatListItem[]> {
  const response = await api.get('/api/chat/sessions');
  return response.data;
}

export async function getSession(sessionId: number): Promise<ChatSessionWithMessages> {
  const response = await api.get(`/api/chat/${sessionId}`);
  return response.data;
}

export async function sendMessage(
  sessionId: number,
  data: SendMessageRequest
): Promise<SendMessageResponse> {
  const response = await api.post(`/api/chat/${sessionId}/message`, data);
  return response.data;
}

export async function finalizeSession(sessionId: number): Promise<FinalizeWithGoalResponse> {
  const response = await api.post(`/api/chat/${sessionId}/finalize`, {});
  return response.data;
}

export async function deleteSession(sessionId: number): Promise<void> {
  await api.delete(`/api/chat/${sessionId}`);
}
