from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Contact])
def read_contacts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve contact records.
    """
    query = db.query(models.Contact)
    if participant_id:
        query = query.filter(models.Contact.participant_id == participant_id)
    contacts = query.offset(skip).limit(limit).all()
    return contacts


@router.post("/", response_model=schemas.Contact)
def create_contact(
    *,
    db: Session = Depends(get_db),
    contact_in: schemas.ContactCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new contact record.
    """
    contact = models.Contact(
        **contact_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get contact record by ID.
    """
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return contact


@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    contact_in: schemas.ContactUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a contact record.
    """
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact record not found")
    update_data = contact_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", response_model=schemas.Contact)
def delete_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a contact record.
    """
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact record not found")
    db.delete(contact)
    db.commit()
    return contact