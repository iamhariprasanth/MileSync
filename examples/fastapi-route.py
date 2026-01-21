# Example: FastAPI Route Pattern
# This shows the "thin route, fat service" pattern used in MileSync

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.schemas.example import ExampleCreate, ExampleResponse
from app.services.example_service import ExampleService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("/", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    data: ExampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new example resource.

    - Thin route: just receives request, calls service, returns response
    - All business logic is in the service layer
    """
    service = ExampleService(db)
    result = service.create(data, user_id=current_user.id)
    return result


@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(
    example_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single example by ID."""
    service = ExampleService(db)
    result = service.get_by_id(example_id, user_id=current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found"
        )
    return result


@router.get("/", response_model=list[ExampleResponse])
async def list_examples(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """List all examples for the current user."""
    service = ExampleService(db)
    return service.get_all(user_id=current_user.id, skip=skip, limit=limit)
