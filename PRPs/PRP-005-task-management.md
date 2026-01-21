# PRP-005: Task Management & Daily View

## Goal
Enable users to view and complete daily tasks.

## Why
Daily task completion drives goal progress.

## Success Criteria
- [ ] /tasks/today returns today's tasks
- [ ] User can mark tasks complete/incomplete
- [ ] Task status updates reflect in progress
- [ ] Streak tracking works

## Files to Create/Update
```
backend/app/routes/tasks.py
backend/app/services/task_service.py

frontend/src/pages/Dashboard.tsx (add tasks widget)
frontend/src/components/tasks/TaskList.tsx
frontend/src/components/tasks/TaskItem.tsx
frontend/src/api/tasks.ts
```

## Task Sequence
1. CREATE task_service.py (get_tasks_by_date, update_task_status, calculate_streak)
2. CREATE tasks routes (GET /tasks, GET /tasks/today, PUT /tasks/{id})
3. CREATE TaskList and TaskItem components
4. ADD tasks widget to Dashboard
5. IMPLEMENT streak calculation (consecutive days with completed tasks)
6. VALIDATE task completion flow

## Anti-Patterns
- Don't allow completing future tasks
- Don't break streak calculation on timezone changes
- Don't update task without optimistic UI

## Gotchas
- Streak calculation needs to handle timezone differences
- Consider user's local date vs server date
- Batch task updates for better UX

## Documentation References
- [Date handling in JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
