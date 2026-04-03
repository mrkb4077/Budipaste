from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Enrolment])
def read_enrolments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve enrolment records.
    """
    query = db.query(models.Enrolment)
    if participant_id:
        query = query.filter(models.Enrolment.participant_id == participant_id)
    enrolments = query.offset(skip).limit(limit).all()
    return enrolments


@router.post("/", response_model=schemas.Enrolment)
def create_enrolment(
    *,
    db: Session = Depends(get_db),
    enrolment_in: schemas.EnrolmentCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new enrolment record.
    """
    enrolment = models.Enrolment(**enrolment_in.model_dump())
    db.add(enrolment)
    db.commit()
    db.refresh(enrolment)
    return enrolment


@router.get("/{enrolment_id}", response_model=schemas.Enrolment)
def read_enrolment(
    *,
    db: Session = Depends(get_db),
    enrolment_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get enrolment record by ID.
    """
    enrolment = db.query(models.Enrolment).filter(models.Enrolment.id == enrolment_id).first()
    if not enrolment:
        raise HTTPException(status_code=404, detail="Enrolment record not found")
    return enrolment


@router.put("/{enrolment_id}", response_model=schemas.Enrolment)
def update_enrolment(
    *,
    db: Session = Depends(get_db),
    enrolment_id: str,
    enrolment_in: schemas.EnrolmentUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update an enrolment record.
    """
    enrolment = db.query(models.Enrolment).filter(models.Enrolment.id == enrolment_id).first()
    if not enrolment:
        raise HTTPException(status_code=404, detail="Enrolment record not found")
    update_data = enrolment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(enrolment, field, value)
    db.add(enrolment)
    db.commit()
    db.refresh(enrolment)
    return enrolment


@router.delete("/{enrolment_id}", response_model=schemas.Enrolment)
def delete_enrolment(
    *,
    db: Session = Depends(get_db),
    enrolment_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete an enrolment record.
    """
    enrolment = db.query(models.Enrolment).filter(models.Enrolment.id == enrolment_id).first()
    if not enrolment:
        raise HTTPException(status_code=404, detail="Enrolment record not found")
    db.delete(enrolment)
    db.commit()
    return enrolment