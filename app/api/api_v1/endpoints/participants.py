from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Participant])
def read_participants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve participants.
    """
    participants = db.query(models.Participant).offset(skip).limit(limit).all()
    return participants


@router.post("/", response_model=schemas.Participant)
def create_participant(
    *,
    db: Session = Depends(get_db),
    participant_in: schemas.ParticipantCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new participant.
    """
    # Generate identifier: "Full Name | YYYY-MM-DD"
    identifier = f"{participant_in.full_name} | {participant_in.date_of_birth.strftime('%Y-%m-%d')}"

    # Check if identifier already exists
    existing = db.query(models.Participant).filter(models.Participant.identifier == identifier).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Participant with this name and date of birth already exists"
        )

    participant = models.Participant(
        identifier=identifier,
        **participant_in.model_dump()
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


@router.get("/{participant_id}", response_model=schemas.Participant)
def read_participant(
    *,
    db: Session = Depends(get_db),
    participant_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get participant by ID.
    """
    participant = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant


@router.put("/{participant_id}", response_model=schemas.Participant)
def update_participant(
    *,
    db: Session = Depends(get_db),
    participant_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a participant.
    """
    participant = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    update_data = participant_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(participant, field, value)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


@router.delete("/{participant_id}", response_model=schemas.Participant)
def delete_participant(
    *,
    db: Session = Depends(get_db),
    participant_id: int,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a participant.
    """
    participant = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    db.delete(participant)
    db.commit()
    return participant