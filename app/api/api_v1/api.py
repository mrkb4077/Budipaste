from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth, participants, enrolment, attendance,
    new_attendance, new_attendance_absence, activities,
    exercise, assessments, brain_check, notes,
    referrals, contacts, school, plan, makers_and_breakers
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(participants.router, prefix="/participants", tags=["participants"])
api_router.include_router(enrolment.router, prefix="/enrolment", tags=["enrolment"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(new_attendance.router, prefix="/new-attendance", tags=["new-attendance"])
api_router.include_router(new_attendance_absence.router, prefix="/new-attendance-absence", tags=["new-attendance-absence"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(school.router, prefix="/school", tags=["school"])
api_router.include_router(exercise.router, prefix="/exercise", tags=["exercise"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(brain_check.router, prefix="/brain-check", tags=["brain-check"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(plan.router, prefix="/plan", tags=["plan"])
api_router.include_router(makers_and_breakers.router, prefix="/makers-and-breakers", tags=["makers-and-breakers"])