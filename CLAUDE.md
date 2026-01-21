# Claude AI Development Guidelines - MileSync

## Core Principles

### Verification First
- Never hallucinate libraries or functions - only use known, verified Python packages
- Check package documentation before using unfamiliar APIs
- Never assume missing information - ask clarifying questions when uncertain

### File Integrity
- Never delete or overwrite existing code unless explicitly instructed
- Always read files before editing to understand context
- Preserve existing functionality when adding new features

## Code Standards

### File Length
- Maximum 500 lines per file
- Split into feature-focused modules with clear separation of concerns

### Backend (Python/FastAPI)
- Thin routes: receive request -> call service -> return response
- Fat services: all business logic lives in service layer
- Pydantic schemas for all request/response validation
- Type hints on all functions
- Google-style docstrings for public functions

### Frontend (React/TypeScript)
- Functional components only
- Custom hooks for reusable logic
- Type all props, state, and function parameters
- Feature-based folder organization

### Comments
- Add inline `# Reason:` comments for complex or non-obvious logic
- Don't comment obvious code
- Update comments when changing code

## Testing Requirements
- Always create pytest unit tests for new backend features
- Tests should cover:
  - Expected use cases
  - Edge cases
  - Failure scenarios

## Environment Management
- Use python-dotenv for configuration
- Never commit .env files
- Document all required env vars in .env.example

## Task Tracking
- Update TASK.md with discovered items during development
- Reference PLANNING.md for architecture decisions
- Follow PRPs when implementing features

## Anti-Patterns to Avoid
- Don't hardcode secrets or credentials
- Don't skip error handling
- Don't create circular imports
- Don't mix business logic in routes
- Don't use global mutable state
