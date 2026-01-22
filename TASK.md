# MileSync - Task Tracking

## Current Phase
**Phase 3: Observability & Evaluation**

## Active Tasks

### In Progress
(None)

### Pending
(None)

## Completed
- [x] Create project plan
- [x] Define tech stack
- [x] Create folder structure
- [x] Set up .claude configuration
- [x] Initialize backend with FastAPI
- [x] Initialize frontend with Vite + React + TypeScript
- [x] Set up Docker Compose with PostgreSQL
- [x] Implement user authentication (PRP-002)
  - [x] Email/password registration and login
  - [x] JWT token generation and validation
  - [x] Google OAuth integration
  - [x] GitHub OAuth integration
  - [x] Protected route middleware
- [x] Build AI chat system (PRP-003)
  - [x] ChatSession and ChatMessage models
  - [x] Chat API routes (start, message, history, finalize)
  - [x] OpenAI integration for AI responses
  - [x] Frontend chat UI with real-time messaging
- [x] Create goal/roadmap generation (PRP-004)
  - [x] Goal, Milestone, and Task models
  - [x] Goal schemas for API requests/responses
  - [x] Goal service with CRUD operations
  - [x] AI-powered goal extraction using OpenAI function calling
  - [x] Finalize endpoint creates goals from chat conversations
  - [x] Goals API routes (list, create, get, update, delete)
  - [x] Task completion/toggle endpoints
  - [x] Frontend Goals list page with real API
  - [x] Frontend GoalDetail page with roadmap visualization
  - [x] Task completion toggles with progress updates
- [x] Implement task management enhancements (PRP-005)
  - [x] Milestone CRUD endpoints (create, update, delete)
  - [x] Task CRUD endpoints (create, update, delete)
  - [x] Frontend UI for adding milestones
  - [x] Frontend UI for adding/deleting tasks
  - [x] Goal progress auto-updates on task changes
- [x] Build dashboard (PRP-006)
  - [x] Dashboard stats API endpoint
  - [x] Active goals count, completed tasks count
  - [x] Completion rate calculation
  - [x] Task completion streak tracking
  - [x] Upcoming tasks list with priority sorting
  - [x] Frontend Dashboard with real API data
  - [x] Task completion from dashboard
- [x] Unit tests for new endpoints
  - [x] Dashboard stats tests
  - [x] Milestone CRUD tests
  - [x] Task CRUD tests
- [x] **Opik LLM Observability & Evaluation Integration**
  - [x] Opik SDK installation and configuration
  - [x] OpenAI client wrapped with track_openai for automatic tracing
  - [x] @track decorators on AI service functions (chat, summarize, extract)
  - [x] Custom LLM-as-judge metrics:
    - [x] GoalCoachingQualityMetric (SMART alignment, motivational quality)
    - [x] GoalExtractionQualityMetric (extraction completeness, quality)
    - [x] UserFrustrationDetector (conversation friction detection)
  - [x] Analytics API endpoints (/api/analytics/*)
  - [x] Frontend Analytics dashboard with performance visualizations
  - [x] Automatic evaluation logging in chat and finalize endpoints
  - [x] Experiment runner script for batch evaluation
  - [x] Evaluation datasets for testing
  - [x] Unit tests for Opik integration
  - [x] OPIK_INTEGRATION.md documentation

## Discovered Items
_Items discovered during development that need attention_

- Consider adding chat session history page to view past conversations
- Add ability to edit milestones and tasks manually
- Consider adding due date reminders/notifications

## Blockers
_Issues blocking progress_

(None yet)

## Notes
- Follow PRPs in `.claude/PRPs/` for feature implementation
- Update this file as tasks progress
- Add discovered items when found during development
- OpenAI API key required in .env for AI chat and goal extraction functionality
- **Opik API key required in .env for LLM observability and evaluation**
- See `backend/OPIK_INTEGRATION.md` for Opik setup instructions

