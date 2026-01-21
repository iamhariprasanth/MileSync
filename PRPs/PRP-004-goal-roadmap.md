# PRP-004: Goal & Roadmap Generation

## Goal
Convert AI conversations into structured goals with milestones and tasks.

## Why
Transform freeform chat into actionable, trackable roadmaps.

## Success Criteria
- [ ] /finalize endpoint extracts goal from conversation
- [ ] AI generates milestones (3-7 checkpoints)
- [ ] AI generates tasks for each milestone
- [ ] Goal saved with all related entities
- [ ] Goal detail page shows roadmap visualization

## Files to Create/Update
```
backend/app/models/goal.py
backend/app/models/milestone.py
backend/app/models/task.py
backend/app/schemas/goal.py
backend/app/routes/goals.py
backend/app/routes/chat.py (add /finalize)
backend/app/services/goal_service.py

frontend/src/pages/Goals.tsx
frontend/src/pages/GoalDetail.tsx
frontend/src/components/goals/RoadmapView.tsx
frontend/src/components/goals/MilestoneCard.tsx
frontend/src/api/goals.ts
```

## Task Sequence
1. CREATE Goal model (id, user_id, chat_session_id, title, description, category, target_date, status)
2. CREATE Milestone model (id, goal_id, title, description, target_date, order, is_completed)
3. CREATE Task model (id, milestone_id, goal_id, title, description, due_date, status, priority)
4. CREATE goal schemas
5. CREATE goal_service.py with CRUD operations
6. UPDATE ai_service.py with extract_goal_from_conversation() using function calling
7. CREATE /finalize endpoint that calls AI to structure the goal
8. CREATE goals routes (GET /goals, GET /goals/{id}, PUT, DELETE)
9. CREATE Goals list page
10. CREATE GoalDetail page with RoadmapView component
11. VALIDATE full flow: chat -> finalize -> view roadmap

## AI Extraction Prompt
```
Based on this conversation, extract:
1. Goal title (concise, action-oriented)
2. Goal description (1-2 sentences)
3. Target date
4. Category (health, career, education, finance, personal, other)
5. Milestones (3-7 major checkpoints with dates)
6. Tasks for each milestone (specific, actionable items)
```

## Anti-Patterns
- Don't create goals without user confirmation
- Don't generate unrealistic task counts
- Don't ignore conversation context

## Gotchas
- Use OpenAI function calling for structured extraction
- Validate dates are in the future
- Handle cases where AI can't extract meaningful data

## Documentation References
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
