from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.BrainCheck])
def read_brain_checks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve brain check records.
    """
    query = db.query(models.BrainCheck)
    if participant_id:
        query = query.filter(models.BrainCheck.participant_id == participant_id)
    brain_checks = query.offset(skip).limit(limit).all()
    return brain_checks


@router.post("/", response_model=schemas.BrainCheck)
def create_brain_check(
    *,
    db: Session = Depends(get_db),
    brain_check_in: schemas.BrainCheckCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new brain check record.
    """
    brain_check = models.BrainCheck(
        **brain_check_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(brain_check)
    db.commit()
    db.refresh(brain_check)
    return brain_check


@router.get("/{brain_check_id}", response_model=schemas.BrainCheck)
def read_brain_check(
    *,
    db: Session = Depends(get_db),
    brain_check_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get brain check record by ID.
    """
    brain_check = db.query(models.BrainCheck).filter(models.BrainCheck.id == brain_check_id).first()
    if not brain_check:
        raise HTTPException(status_code=404, detail="Brain check record not found")
    return brain_check


@router.put("/{brain_check_id}", response_model=schemas.BrainCheck)
def update_brain_check(
    *,
    db: Session = Depends(get_db),
    brain_check_id: str,
    brain_check_in: schemas.BrainCheckUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a brain check record.
    """
    brain_check = db.query(models.BrainCheck).filter(models.BrainCheck.id == brain_check_id).first()
    if not brain_check:
        raise HTTPException(status_code=404, detail="Brain check record not found")
    update_data = brain_check_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brain_check, field, value)
    db.add(brain_check)
    db.commit()
    db.refresh(brain_check)
    return brain_check


@router.delete("/{brain_check_id}", response_model=schemas.BrainCheck)
def delete_brain_check(
    *,
    db: Session = Depends(get_db),
    brain_check_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a brain check record.
    """
    brain_check = db.query(models.BrainCheck).filter(models.BrainCheck.id == brain_check_id).first()
    if not brain_check:
        raise HTTPException(status_code=404, detail="Brain check record not found")
    db.delete(brain_check)
    db.commit()
    return brain_check