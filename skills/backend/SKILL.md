# Backend Development Skill - MileSync

## Description
Specialized skill for developing FastAPI backend components following MileSync patterns.

## Expertise Areas
- FastAPI REST API development
- SQLModel ORM with PostgreSQL
- JWT authentication & OAuth integration
- OpenAI API integration
- Service layer architecture

## Code Style
- Thin routes (receive request -> call service -> return response)
- Fat services (all business logic)
- Pydantic schemas for all request/response validation
- Type hints everywhere
- Max 500 lines per file

## File Structure Pattern
```
backend/app/
├── routes/      # API endpoints (thin)
├── services/    # Business logic (fat)
├── models/      # SQLModel database models
├── schemas/     # Pydantic schemas
└── utils/       # Utilities and dependencies
```

## Validation Commands
```bash
ruff check backend/
pytest backend/tests/
```

## Example Usage
See `examples/fastapi-route.py` for route patterns.
See `examples/auth-middleware.py` for auth dependency patterns.

## Common Gotchas
- Always use Depends(get_db) for database sessions
- Use Depends(get_current_user) for protected routes
- Handle database commits in service layer, not routes
- Validate OpenAI API key exists before making calls
