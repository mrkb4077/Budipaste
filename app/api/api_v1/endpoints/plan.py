import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db, sync_participant_reference
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.Plan])
def read_plans(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    participant_uuid: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve plan records.
    """
    query = db.query(models.Plan)
    if participant_uuid:
        query = query.filter(models.Plan.participant_uuid == participant_uuid)
    elif participant_id:
        query = query.filter(models.Plan.participant_id == participant_id)
    plans = query.offset(skip).limit(limit).all()
    return plans


@router.post("/", response_model=schemas.Plan)
def create_plan(
    *,
    db: Session = Depends(get_db),
    plan_in: schemas.PlanCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new plan record.
    """
    plan_data = sync_participant_reference(db, plan_in.model_dump(), required=True)
    plan = models.Plan(
        id=str(uuid.uuid4()),
        **plan_data,
        recorded_by=current_user.id
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/{plan_id}", response_model=schemas.Plan)
def read_plan(
    *,
    db: Session = Depends(get_db),
    plan_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get plan record by ID.
    """
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan record not found")
    return plan


@router.put("/{plan_id}", response_model=schemas.Plan)
def update_plan(
    *,
    db: Session = Depends(get_db),
    plan_id: str,
    plan_in: schemas.PlanUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a plan record.
    """
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan record not found")
    update_data = plan_in.model_dump(exclude_unset=True)
    update_data = sync_participant_reference(db, update_data)
    for field, value in update_data.items():
        setattr(plan, field, value)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", response_model=schemas.Plan)
def delete_plan(
    *,
    db: Session = Depends(get_db),
    plan_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a plan record.
    """
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan record not found")
    db.delete(plan)
    db.commit()
    return plan