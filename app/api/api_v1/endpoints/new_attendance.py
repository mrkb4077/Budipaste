from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.NewAttendance])
def read_new_attendances(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve session-level attendance records.
    """
    query = db.query(models.NewAttendance)
    if participant_id:
        query = query.filter(models.NewAttendance.participant_id == participant_id)
    attendances = query.offset(skip).limit(limit).all()
    return attendances


@router.post("/", response_model=schemas.NewAttendance)
def create_new_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_in: schemas.NewAttendanceCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new session-level attendance record.
    """
    attendance = models.NewAttendance(
        **attendance_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/{attendance_id}", response_model=schemas.NewAttendance)
def read_new_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get session-level attendance record by ID.
    """
    attendance = db.query(models.NewAttendance).filter(models.NewAttendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="New attendance record not found")
    return attendance


@router.put("/{attendance_id}", response_model=schemas.NewAttendance)
def update_new_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    attendance_in: schemas.NewAttendanceUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update a session-level attendance record.
    """
    attendance = db.query(models.NewAttendance).filter(models.NewAttendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="New attendance record not found")
    update_data = attendance_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.delete("/{attendance_id}", response_model=schemas.NewAttendance)
def delete_new_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete a session-level attendance record.
    """
    attendance = db.query(models.NewAttendance).filter(models.NewAttendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="New attendance record not found")
    db.delete(attendance)
    db.commit()
    return attendance