# PRP-001: Project Setup & Infrastructure

## Goal
Initialize the MileSync project with all required configuration and dependencies.

## Why
Establish a solid foundation for development with proper tooling, containerization, and environment setup.

## Success Criteria
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] PostgreSQL connects successfully
- [ ] Docker Compose orchestrates all services

## Files to Create
```
backend/
├── app/__init__.py
├── app/main.py
├── app/config.py
├── app/database.py
├── requirements.txt
├── Dockerfile
└── .env.example

frontend/
├── src/main.tsx
├── src/App.tsx
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── index.html
└── Dockerfile

docker-compose.yml
.env.example
```

## Task Sequence
1. CREATE `backend/requirements.txt` with FastAPI, SQLModel, python-jose, bcrypt, openai, python-dotenv, httpx
2. CREATE `backend/app/config.py` with Pydantic Settings for env vars
3. CREATE `backend/app/database.py` with PostgreSQL connection
4. CREATE `backend/app/main.py` with FastAPI app, CORS, router includes
5. CREATE `backend/Dockerfile` with Python 3.11, pip install
6. CREATE `frontend/` with Vite React TypeScript template
7. CONFIGURE TailwindCSS in frontend
8. CREATE `docker-compose.yml` with postgres, backend, frontend services
9. VALIDATE all services start with `docker-compose up`

## Anti-Patterns
- Don't hardcode database credentials
- Don't skip CORS configuration
- Don't use SQLite for development (use PostgreSQL throughout)

## Gotchas
- Ensure CORS allows frontend origin
- PostgreSQL needs time to initialize on first run
- Environment variables must be set before starting services

## Documentation References
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vite](https://vitejs.dev/)
- [Docker Compose](https://docs.docker.com/compose/)
