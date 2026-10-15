"""Concept management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.concept import Concept
from app.models.user import User
from app.schemas.concept import ConceptCreate, ConceptRead, ConceptUpdate


router = APIRouter(prefix="/concepts", tags=["concepts"])


def get_owned_concept(
    concept_id: UUID,
    user_id: UUID,
    db: Session,
) -> Concept:
    """Find a concept owned by the specified user."""

    concept = db.scalar(
        select(Concept).where(
            Concept.id == concept_id,
            Concept.user_id == user_id,
        )
    )

    if concept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept not found",
        )

    return concept


@router.post(
    "",
    response_model=ConceptRead,
    status_code=status.HTTP_201_CREATED,
)
def create_concept(
    concept_data: ConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Concept:
    """Create a concept for the authenticated user."""

    concept = Concept(
        user_id=current_user.id,
        **concept_data.model_dump(),
    )

    db.add(concept)
    db.commit()
    db.refresh(concept)

    return concept


@router.get("", response_model=list[ConceptRead])
def list_concepts(
    q: str | None = Query(default=None, max_length=200),
    subject: str | None = Query(default=None, max_length=120),
    archived: bool = False,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Concept]:
    """List the authenticated user's concepts."""

    statement = select(Concept).where(
        Concept.user_id == current_user.id,
        Concept.is_archived == archived,
    )

    if q:
        pattern = f"%{q}%"
        statement = statement.where(
            or_(
                Concept.title.ilike(pattern),
                Concept.question.ilike(pattern),
            )
        )

    if subject:
        statement = statement.where(Concept.subject == subject)

    statement = (
        statement
        .order_by(Concept.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


@router.get("/{concept_id}", response_model=ConceptRead)
def get_concept(
    concept_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Concept:
    """Retrieve one concept owned by the authenticated user."""

    return get_owned_concept(concept_id, current_user.id, db)


@router.patch("/{concept_id}", response_model=ConceptRead)
def update_concept(
    concept_id: UUID,
    concept_data: ConceptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Concept:
    """Update an owned concept or change its archive status."""

    concept = get_owned_concept(concept_id, current_user.id, db)

    changes = concept_data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(concept, field, value)

    db.commit()
    db.refresh(concept)

    return concept


@router.delete(
    "/{concept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_concept(
    concept_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Permanently delete an owned concept."""

    concept = get_owned_concept(concept_id, current_user.id, db)

    db.delete(concept)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)