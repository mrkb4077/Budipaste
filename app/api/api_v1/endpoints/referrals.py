from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Referral])
def read_referrals(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve referral records.
    """
    query = db.query(models.Referral)
    if participant_id:
        query = query.filter(models.Referral.participant_id == participant_id)
    referrals = query.offset(skip).limit(limit).all()
    return referrals


@router.post("/", response_model=schemas.Referral)
def create_referral(
    *,
    db: Session = Depends(get_db),
    referral_in: schemas.ReferralCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new referral record.
    """
    referral = models.Referral(
        **referral_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)
    return referral


@router.get("/{referral_id}", response_model=schemas.Referral)
def read_referral(
    *,
    db: Session = Depends(get_db),
    referral_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get referral record by ID.
    """
    referral = db.query(models.Referral).filter(models.Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral record not found")
    return referral


@router.put("/{referral_id}", response_model=schemas.Referral)
def update_referral(
    *,
    db: Session = Depends(get_db),
    referral_id: str,
    referral_in: schemas.ReferralUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a referral record.
    """
    referral = db.query(models.Referral).filter(models.Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral record not found")
    update_data = referral_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(referral, field, value)
    db.add(referral)
    db.commit()
    db.refresh(referral)
    return referral


@router.delete("/{referral_id}", response_model=schemas.Referral)
def delete_referral(
    *,
    db: Session = Depends(get_db),
    referral_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a referral record.
    """
    referral = db.query(models.Referral).filter(models.Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral record not found")
    db.delete(referral)
    db.commit()
    return referral