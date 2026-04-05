import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.api_v1.endpoints.auth import get_current_user, get_db, sync_participant_reference
from app.models import models

router = APIRouter()


@router.get("/", response_model=List[schemas.NewAttendanceAbsence])
def read_new_attendance_absences(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    participant_id: str = None,
    participant_uuid: str = None,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve attendance absence summary records.
    """
    query = db.query(models.NewAttendanceAbsence)
    if participant_uuid:
        query = query.filter(models.NewAttendanceAbsence.participant_uuid == participant_uuid)
    elif participant_id:
        query = query.filter(models.NewAttendanceAbsence.participant_id == participant_id)
    absences = query.offset(skip).limit(limit).all()
    return absences


@router.post("/", response_model=schemas.NewAttendanceAbsence)
def create_new_attendance_absence(
    *,
    db: Session = Depends(get_db),
    absence_in: schemas.NewAttendanceAbsenceCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new attendance absence summary record.
    """
    absence_data = sync_participant_reference(db, absence_in.model_dump(), required=True)
    absence = models.NewAttendanceAbsence(id=str(uuid.uuid4()), **absence_data)
    db.add(absence)
    db.commit()
    db.refresh(absence)
    return absence


@router.get("/{absence_id}", response_model=schemas.NewAttendanceAbsence)
def read_new_attendance_absence(
    *,
    db: Session = Depends(get_db),
    absence_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get attendance absence summary record by ID.
    """
    absence = db.query(models.NewAttendanceAbsence).filter(models.NewAttendanceAbsence.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=404, detail="New attendance absence record not found")
    return absence


@router.put("/{absence_id}", response_model=schemas.NewAttendanceAbsence)
def update_new_attendance_absence(
    *,
    db: Session = Depends(get_db),
    absence_id: str,
    absence_in: schemas.NewAttendanceAbsenceUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update an attendance absence summary record.
    """
    absence = db.query(models.NewAttendanceAbsence).filter(models.NewAttendanceAbsence.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=404, detail="New attendance absence record not found")
    update_data = absence_in.model_dump(exclude_unset=True)
    update_data = sync_participant_reference(db, update_data)
    for field, value in update_data.items():
        setattr(absence, field, value)
    db.add(absence)
    db.commit()
    db.refresh(absence)
    return absence


@router.delete("/{absence_id}", response_model=schemas.NewAttendanceAbsence)
def delete_new_attendance_absence(
    *,
    db: Session = Depends(get_db),
    absence_id: str,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete an attendance absence summary record.
    """
    absence = db.query(models.NewAttendanceAbsence).filter(models.NewAttendanceAbsence.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=404, detail="New attendance absence record not found")
    db.delete(absence)
    db.commit()
    return absence