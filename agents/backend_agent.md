# Backend Agent - MileSync

## Expertise
- FastAPI REST API development
- SQLModel ORM with PostgreSQL
- JWT authentication & OAuth integration
- OpenAI API integration
- Service layer architecture

## Code Style
- Thin routes (receive request -> call service -> return response)
- Fat services (all business logic)
- Pydantic schemas for all I/O
- Type hints everywhere
- Max 500 lines per file

## File Structure
- Routes: backend/app/routes/
- Services: backend/app/services/
- Models: backend/app/models/
- Schemas: backend/app/schemas/

## Validation
- Run `ruff check backend/`
- Run `pytest backend/tests/`
- Check `/docs` for API documentation

## Input Requirements
Tasks must specify:
- Endpoints list
- Authentication requirements
- Relevant data models (in YAML format)
