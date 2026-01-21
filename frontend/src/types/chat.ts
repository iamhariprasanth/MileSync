export type ChatSessionStatus = 'active' | 'completed' | 'finalized';
export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatSession {
  id: number;
  user_id: number;
  title: string | null;
  status: ChatSessionStatus;
  goal_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface SendMessageRequest {
  content: string;
}

export interface StartChatResponse {
  session: ChatSession;
  initial_message: ChatMessage;
}

export interface SendMessageResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
}

export interface ChatSessionWithMessages {
  session: ChatSession;
  messages: ChatMessage[];
}

export interface ChatListItem {
  id: number;
  title: string | null;
  status: ChatSessionStatus;
  message_count: number;
  last_message_preview: string | null;
  created_at: string;
  updated_at: string;
}

export interface FinalizeResponse {
  session: ChatSession;
  message: string;
}

// Re-export from goal types for convenience
export type { FinalizeWithGoalResponse } from './goal';
