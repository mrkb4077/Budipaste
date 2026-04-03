from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db
from app.models import models

router = APIRouter()


# Term-level aggregated attendance endpoints
@router.get("/", response_model=List[schemas.Attendance])
def read_attendance(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_name: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve aggregated attendance records.
    """
    query = db.query(models.Attendance)
    if participant_name:
        query = query.filter(models.Attendance.participant_name == participant_name)
    attendance = query.offset(skip).limit(limit).all()
    return attendance


@router.post("/", response_model=schemas.Attendance)
def create_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_in: schemas.AttendanceCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new aggregated attendance record.
    """
    attendance = models.Attendance(id=str(uuid.uuid4()), **attendance_in.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/{attendance_id}", response_model=schemas.Attendance)
def read_attendance_record(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get aggregated attendance record by ID.
    """
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.put("/{attendance_id}", response_model=schemas.Attendance)
def update_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    attendance_in: schemas.AttendanceUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update an aggregated attendance record.
    """
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    update_data = attendance_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.delete("/{attendance_id}", response_model=schemas.Attendance)
def delete_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete an aggregated attendance record.
    """
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(attendance)
    db.commit()
    return attendance


# Session-level attendance (NewAttendance) endpoints
@router.get("/session/", response_model=List[schemas.NewAttendance])
def read_session_attendance(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve session-level attendance records (check-in/check-out events).
    """
    query = db.query(models.NewAttendance)
    if participant_id:
        query = query.filter(models.NewAttendance.participant_id == participant_id)
    attendance = query.offset(skip).limit(limit).all()
    return attendance


@router.post("/session/", response_model=schemas.NewAttendance)
def create_session_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_in: schemas.NewAttendanceCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new session-level attendance record (check-in/check-out).
    """
    attendance = models.NewAttendance(
        **attendance_in.model_dump(),
        recorded_by=current_user.id
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/session/{attendance_id}", response_model=schemas.NewAttendance)
def read_session_attendance_record(
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
        raise HTTPException(status_code=404, detail="Session attendance record not found")
    return attendance