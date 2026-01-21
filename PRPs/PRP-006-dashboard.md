# PRP-006: Dashboard & Progress Visualization

## Goal
Build progress dashboard with charts and stats.

## Why
Visual feedback motivates users and shows progress.

## Success Criteria
- [ ] Dashboard shows overall stats
- [ ] Progress charts display correctly
- [ ] Streak counter visible
- [ ] Upcoming tasks listed

## Files to Create/Update
```
backend/app/routes/dashboard.py

frontend/src/pages/Dashboard.tsx
frontend/src/components/dashboard/StatsCard.tsx
frontend/src/components/dashboard/ProgressChart.tsx
frontend/src/components/dashboard/StreakCounter.tsx
frontend/src/components/dashboard/UpcomingTasks.tsx
frontend/src/api/dashboard.ts
```

## Task Sequence
1. CREATE dashboard route (GET /dashboard/stats)
2. CALCULATE stats: active goals, completed tasks, overall progress %, current streak
3. CREATE StatsCard component
4. CREATE ProgressChart using chart library (recharts)
5. CREATE StreakCounter with visual flair
6. CREATE UpcomingTasks widget
7. ASSEMBLE Dashboard page
8. VALIDATE all widgets display correctly

## Dashboard Stats Response
```json
{
  "active_goals": 3,
  "completed_goals": 5,
  "total_tasks": 47,
  "completed_tasks": 32,
  "completion_rate": 68.1,
  "current_streak": 7,
  "longest_streak": 14,
  "upcoming_tasks": [...]
}
```

## Anti-Patterns
- Don't fetch all data on every render
- Don't use heavy animations that hurt performance
- Don't show stale data without indication

## Gotchas
- Cache dashboard stats for performance
- Use skeleton loaders for better UX
- Charts need responsive sizing

## Documentation References
- [Recharts](https://recharts.org/)
- [React Query](https://tanstack.com/query/latest)
