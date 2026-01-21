# MileSync - Architecture & Planning

## Project Overview
MileSync is an AI goal coach that helps users set, track, and achieve their goals through personalized roadmaps, daily tasks, and visual progress insights.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL
- **Auth**: JWT tokens + OAuth (Google, GitHub)
- **AI**: OpenAI GPT-4 API

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State**: React Query (server state), Context (auth state)
- **Routing**: React Router v6

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (production)

## Architecture Patterns

### Backend: Service Layer Architecture
```
Route (thin) -> Service (fat) -> Model
     |              |
  Schemas      Business Logic
```

- **Routes**: HTTP handling, request validation, response formatting
- **Services**: Business logic, database operations, external API calls
- **Models**: Database schema definitions (SQLModel)
- **Schemas**: Request/response validation (Pydantic)

### Frontend: Feature-Based Organization
```
src/
  pages/         # Route components
  components/    # UI components by feature
  hooks/         # Custom React hooks
  api/           # API client functions
  context/       # React context providers
  types/         # TypeScript interfaces
```

## Database Schema

### Users
- Authentication and profile information
- Supports email/password and OAuth providers

### ChatSessions & ChatMessages
- Stores AI coaching conversations
- Links to goals when finalized

### Goals
- User's goals with metadata
- Links to originating chat session

### Milestones
- Major checkpoints within a goal
- Ordered sequence with target dates

### Tasks
- Actionable items within milestones
- Daily tracking with completion status

## API Design

### URL Structure
- Base: `/api`
- Versioning: Not initially (add `/v1` if needed later)
- Resources: plural nouns (`/goals`, `/tasks`)
- Actions: use HTTP verbs (GET, POST, PUT, DELETE)

### Authentication
- Bearer token in Authorization header
- JWT with 24-hour expiration
- Refresh tokens for extended sessions

### Response Format
```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error Format
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

## Naming Conventions

### Python
- Files: snake_case (`auth_service.py`)
- Classes: PascalCase (`UserService`)
- Functions: snake_case (`get_current_user`)
- Constants: UPPER_SNAKE_CASE (`SECRET_KEY`)

### TypeScript
- Files: PascalCase for components (`Dashboard.tsx`), camelCase for utils (`helpers.ts`)
- Components: PascalCase (`GoalCard`)
- Functions: camelCase (`useGoals`)
- Types/Interfaces: PascalCase (`Goal`, `UserResponse`)

### Database
- Tables: snake_case plural (`users`, `chat_sessions`)
- Columns: snake_case (`created_at`, `user_id`)
- Foreign keys: `{table}_id` (`user_id`, `goal_id`)

## Security Considerations

### Authentication
- Password hashing with bcrypt (12 rounds)
- JWT signed with HS256
- HTTP-only cookies for refresh tokens
- CORS configured for frontend origin only

### Data Protection
- User can only access their own data
- Validate ownership in service layer
- Sanitize all user inputs

### API Keys
- Store in environment variables
- Never log or expose in responses
- Use server-side proxy for OpenAI calls
