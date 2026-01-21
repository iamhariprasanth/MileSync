# MileSync - Initial Setup & Feature Documentation

## Feature Documentation Template

When working on a feature, document it here with the following sections:

---

## Current Feature: Project Setup

### Description
Initialize the MileSync project with all required configuration, dependencies, and infrastructure.

### Examples
Reference code patterns in `examples/` folder (at root):
- `fastapi-route.py` - Backend route pattern
- `react-query-hook.ts` - Frontend data fetching pattern
- `auth-middleware.py` - Authentication dependency pattern

### Documentation References

#### Backend
- FastAPI: https://fastapi.tiangolo.com/
- SQLModel: https://sqlmodel.tiangolo.com/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- python-jose (JWT): https://python-jose.readthedocs.io/

#### Frontend
- React: https://react.dev/
- Vite: https://vitejs.dev/
- TailwindCSS: https://tailwindcss.com/
- React Query: https://tanstack.com/query/latest
- React Router: https://reactrouter.com/

#### AI Integration
- OpenAI API: https://platform.openai.com/docs/

### Other Considerations

#### Edge Cases
- Handle database connection failures gracefully
- Manage OpenAI API rate limits
- Handle OAuth callback errors

#### Common Pitfalls
- Forgetting CORS configuration for frontend-backend communication
- Not setting up proper environment variable handling
- Circular imports in Python modules
- Missing type definitions in TypeScript

#### Project-Specific Requirements
- All API routes under `/api` prefix
- JWT tokens expire after 24 hours
- OAuth requires configured redirect URIs in Google/GitHub consoles
- OpenAI API key must be valid and have sufficient credits

---

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start
```bash
# Clone and enter directory
cd MileSync

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
# - DATABASE_URL
# - SECRET_KEY
# - OPENAI_API_KEY
# - GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
# - GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET

# Start all services
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
