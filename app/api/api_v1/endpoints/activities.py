import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db, sync_participant_reference
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Activity])
def read_activities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    participant_uuid: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve activity records.
    """
    query = db.query(models.Activity)
    if participant_uuid:
        query = query.filter(models.Activity.participant_uuid == participant_uuid)
    elif participant_id:
        query = query.filter(models.Activity.participant_id == participant_id)
    activities = query.offset(skip).limit(limit).all()
    return activities


@router.post("/", response_model=schemas.Activity)
def create_activity(
    *,
    db: Session = Depends(get_db),
    activity_in: schemas.ActivityCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new activity record.
    """
    activity_data = sync_participant_reference(db, activity_in.model_dump(), required=True)
    activity = models.Activity(
        id=str(uuid.uuid4()),
        **activity_data,
        recorded_by=current_user.id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("/{activity_id}", response_model=schemas.Activity)
def read_activity(
    *,
    db: Session = Depends(get_db),
    activity_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get activity record by ID.
    """
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity record not found")
    return activity


@router.put("/{activity_id}", response_model=schemas.Activity)
def update_activity(
    *,
    db: Session = Depends(get_db),
    activity_id: str,
    activity_in: schemas.ActivityUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update an activity record.
    """
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity record not found")
    update_data = activity_in.model_dump(exclude_unset=True)
    update_data = sync_participant_reference(db, update_data)
    for field, value in update_data.items():
        setattr(activity, field, value)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", response_model=schemas.Activity)
def delete_activity(
    *,
    db: Session = Depends(get_db),
    activity_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete an activity record.
    """
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity record not found")
    db.delete(activity)
    db.commit()
    return activity