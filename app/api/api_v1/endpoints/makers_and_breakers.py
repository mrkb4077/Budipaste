import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db, sync_participant_reference
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.MakersAndBreakers])
def read_makers_and_breakers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    participant_uuid: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve makers and breakers records.
    """
    query = db.query(models.MakersAndBreakers)
    if participant_uuid:
        query = query.filter(models.MakersAndBreakers.participant_uuid == participant_uuid)
    elif participant_id:
        query = query.filter(models.MakersAndBreakers.participant_id == participant_id)
    makers_and_breakers = query.offset(skip).limit(limit).all()
    return makers_and_breakers


@router.post("/", response_model=schemas.MakersAndBreakers)
def create_makers_and_breakers(
    *,
    db: Session = Depends(get_db),
    makers_and_breakers_in: schemas.MakersAndBreakersCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new makers and breakers record.
    """
    makers_and_breakers_data = sync_participant_reference(db, makers_and_breakers_in.model_dump(), required=True)
    makers_and_breakers = models.MakersAndBreakers(
        id=str(uuid.uuid4()),
        **makers_and_breakers_data,
        recorded_by=current_user.id
    )
    db.add(makers_and_breakers)
    db.commit()
    db.refresh(makers_and_breakers)
    return makers_and_breakers


@router.get("/{makers_and_breakers_id}", response_model=schemas.MakersAndBreakers)
def read_makers_and_breakers_record(
    *,
    db: Session = Depends(get_db),
    makers_and_breakers_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get makers and breakers record by ID.
    """
    makers_and_breakers = db.query(models.MakersAndBreakers).filter(models.MakersAndBreakers.id == makers_and_breakers_id).first()
    if not makers_and_breakers:
        raise HTTPException(status_code=404, detail="Makers and breakers record not found")
    return makers_and_breakers


@router.put("/{makers_and_breakers_id}", response_model=schemas.MakersAndBreakers)
def update_makers_and_breakers(
    *,
    db: Session = Depends(get_db),
    makers_and_breakers_id: str,
    makers_and_breakers_in: schemas.MakersAndBreakersUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a makers and breakers record.
    """
    makers_and_breakers = db.query(models.MakersAndBreakers).filter(models.MakersAndBreakers.id == makers_and_breakers_id).first()
    if not makers_and_breakers:
        raise HTTPException(status_code=404, detail="Makers and breakers record not found")
    update_data = makers_and_breakers_in.model_dump(exclude_unset=True)
    update_data = sync_participant_reference(db, update_data)
    for field, value in update_data.items():
        setattr(makers_and_breakers, field, value)
    db.add(makers_and_breakers)
    db.commit()
    db.refresh(makers_and_breakers)
    return makers_and_breakers


@router.delete("/{makers_and_breakers_id}", response_model=schemas.MakersAndBreakers)
def delete_makers_and_breakers(
    *,
    db: Session = Depends(get_db),
    makers_and_breakers_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a makers and breakers record.
    """
    makers_and_breakers = db.query(models.MakersAndBreakers).filter(models.MakersAndBreakers.id == makers_and_breakers_id).first()
    if not makers_and_breakers:
        raise HTTPException(status_code=404, detail="Makers and breakers record not found")
    db.delete(makers_and_breakers)
    db.commit()
    return makers_and_breakers