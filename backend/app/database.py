"""Database connection and session management."""

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Create database engine with appropriate settings
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # Reason: SQLite needs check_same_thread=False for FastAPI
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_db():
    """
    Dependency to get database session.

    Usage:
        @router.get("/")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    with Session(engine) as session:
        yield session
