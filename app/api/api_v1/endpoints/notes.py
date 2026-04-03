import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Note])
def read_notes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve note records.
    """
    query = db.query(models.Note)
    if participant_id:
        query = query.filter(models.Note.participant_id == participant_id)
    notes = query.offset(skip).limit(limit).all()
    return notes


@router.post("/", response_model=schemas.Note)
def create_note(
    *,
    db: Session = Depends(get_db),
    note_in: schemas.NoteCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new note record.
    """
    note = models.Note(
        id=str(uuid.uuid4()),
        **note_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=schemas.Note)
def read_note(
    *,
    db: Session = Depends(get_db),
    note_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get note record by ID.
    """
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note record not found")
    return note


@router.put("/{note_id}", response_model=schemas.Note)
def update_note(
    *,
    db: Session = Depends(get_db),
    note_id: str,
    note_in: schemas.NoteUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a note record.
    """
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note record not found")
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", response_model=schemas.Note)
def delete_note(
    *,
    db: Session = Depends(get_db),
    note_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a note record.
    """
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note record not found")
    db.delete(note)
    db.commit()
    return note