import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Assessment])
def read_assessments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve assessment records.
    """
    query = db.query(models.Assessment)
    if participant_id:
        query = query.filter(models.Assessment.participant_id == participant_id)
    assessments = query.offset(skip).limit(limit).all()
    return assessments


@router.post("/", response_model=schemas.Assessment)
def create_assessment(
    *,
    db: Session = Depends(get_db),
    assessment_in: schemas.AssessmentCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new assessment record.
    """
    assessment = models.Assessment(
        id=str(uuid.uuid4()),
        **assessment_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/{assessment_id}", response_model=schemas.Assessment)
def read_assessment(
    *,
    db: Session = Depends(get_db),
    assessment_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get assessment record by ID.
    """
    assessment = db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment record not found")
    return assessment


@router.put("/{assessment_id}", response_model=schemas.Assessment)
def update_assessment(
    *,
    db: Session = Depends(get_db),
    assessment_id: str,
    assessment_in: schemas.AssessmentUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update an assessment record.
    """
    assessment = db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment record not found")
    update_data = assessment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.delete("/{assessment_id}", response_model=schemas.Assessment)
def delete_assessment(
    *,
    db: Session = Depends(get_db),
    assessment_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete an assessment record.
    """
    assessment = db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment record not found")
    db.delete(assessment)
    db.commit()
    return assessment