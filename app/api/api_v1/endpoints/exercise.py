import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db, sync_participant_reference
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Exercise])
def read_exercises(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    participant_uuid: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve exercise records.
    """
    query = db.query(models.Exercise)
    if participant_uuid:
        query = query.filter(models.Exercise.participant_uuid == participant_uuid)
    elif participant_id:
        query = query.filter(models.Exercise.participant_id == participant_id)
    exercises = query.offset(skip).limit(limit).all()
    return exercises


@router.post("/", response_model=schemas.Exercise)
def create_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_in: schemas.ExerciseCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new exercise record.
    """
    exercise_data = sync_participant_reference(db, exercise_in.model_dump(), required=True)
    exercise = models.Exercise(
        id=str(uuid.uuid4()),
        **exercise_data,
        recorded_by=current_user.id
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.get("/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get exercise record by ID.
    """
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise record not found")
    return exercise


@router.put("/{exercise_id}", response_model=schemas.Exercise)
def update_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: str,
    exercise_in: schemas.ExerciseUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update an exercise record.
    """
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise record not found")
    update_data = exercise_in.model_dump(exclude_unset=True)
    update_data = sync_participant_reference(db, update_data)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}", response_model=schemas.Exercise)
def delete_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete an exercise record.
    """
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise record not found")
    db.delete(exercise)
    db.commit()
    return exercise