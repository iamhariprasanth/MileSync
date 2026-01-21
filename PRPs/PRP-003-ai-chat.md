# PRP-003: AI Chat System

## Goal
Build conversational AI interface for goal coaching.

## Why
Core feature - users define goals through natural conversation with AI coach.

## Success Criteria
- [ ] User can start a chat session
- [ ] Messages sent to OpenAI and responses returned
- [ ] Conversation persisted to database
- [ ] Chat history loadable
- [ ] Streaming responses display smoothly (optional)

## Files to Create/Update
```
backend/app/models/chat.py (ChatSession, ChatMessage)
backend/app/schemas/chat.py
backend/app/routes/chat.py
backend/app/services/ai_service.py

frontend/src/pages/Chat.tsx
frontend/src/components/common/ChatMessage.tsx
frontend/src/components/common/ChatInput.tsx
frontend/src/api/chat.ts
frontend/src/hooks/useChat.ts
```

## Task Sequence
1. CREATE ChatSession model (id, user_id, status, created_at, updated_at)
2. CREATE ChatMessage model (id, session_id, role, content, created_at)
3. CREATE chat schemas
4. CREATE ai_service.py with OpenAI client and system prompt
5. CREATE chat routes (/start, /{session_id}/message, /{session_id}/history)
6. CREATE Chat page with message list and input
7. CREATE useChat hook for state management
8. VALIDATE conversation flow works

## System Prompt
```
You are an AI goal coach. Help users define SMART goals, understand their motivations,
identify obstacles, and create actionable plans. Ask clarifying questions to understand
their goal deeply before suggesting a roadmap.
```

## Anti-Patterns
- Don't store API key in frontend code
- Don't make OpenAI calls from frontend directly
- Don't lose conversation context between messages

## Gotchas
- OpenAI API key must be set in environment
- Handle rate limits gracefully
- Long conversations need context management (token limits)

## Documentation References
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
