from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/test")
def test_school():
    return {"message": "School router is working", "status": "ok"}


@router.get("/", response_model=List[schemas.School])
def read_schools(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    # current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve school records. TEST
    """
    query = db.query(models.School)
    if participant_id:
        query = query.filter(models.School.participant_id == participant_id)
    schools = query.offset(skip).limit(limit).all()
    return schools


@router.post("/", response_model=schemas.School)
def create_school(
    *,
    db: Session = Depends(get_db),
    school_in: schemas.SchoolCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new school record.
    """
    school = models.School(
        **school_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(school)
    db.commit()
    db.refresh(school)
    return school


@router.get("/{school_id}", response_model=schemas.School)
def read_school(
    *,
    db: Session = Depends(get_db),
    school_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get school record by ID.
    """
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School record not found")
    return school


@router.put("/{school_id}", response_model=schemas.School)
def update_school(
    *,
    db: Session = Depends(get_db),
    school_id: str,
    school_in: schemas.SchoolUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a school record.
    """
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School record not found")
    update_data = school_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)
    db.add(school)
    db.commit()
    db.refresh(school)
    return school


@router.delete("/{school_id}", response_model=schemas.School)
def delete_school(
    *,
    db: Session = Depends(get_db),
    school_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a school record.
    """
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School record not found")
    db.delete(school)
    db.commit()
    return school