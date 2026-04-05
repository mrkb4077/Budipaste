from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "staff"


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Participant schemas
class ParticipantBase(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: datetime
    gender: Optional[str] = None
    cultural_identity: Optional[str] = None  # JSON string
    living_situation: Optional[str] = None
    employment: Optional[str] = None  # JSON string
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    address_3: Optional[str] = None
    contact_ph_1: Optional[str] = None
    contact_ph_2: Optional[str] = None
    contact_ph_3: Optional[str] = None
    is_enrolled: bool = True
    date_last_attended: Optional[datetime] = None
    date_commenced: Optional[datetime] = None
    dietary_needs: Optional[str] = None
    medical_needs: Optional[str] = None
    neuro_diverse: Optional[str] = None
    learning_disorder: Optional[str] = None
    physical_disorder: Optional[str] = None
    cannot_be_around: Optional[str] = None
    contact_1_name: Optional[str] = None
    contact_1_relationship: Optional[str] = None
    contact_2_name: Optional[str] = None
    contact_2_relationship: Optional[str] = None
    contact_3_name: Optional[str] = None
    contact_3_relationship: Optional[str] = None


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(ParticipantBase):
    is_enrolled: Optional[bool] = None


class Participant(ParticipantBase):
    id: str
    identifier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Enrolment schemas
class EnrolmentBase(BaseModel):
    participant_id: str
    term: int
    year: int
    days: Optional[str] = None  # JSON string
    dual_enrollment: bool = False
    dual_enrolment_details: Optional[str] = None
    number_of_carers: Optional[int] = None
    research_project: Optional[str] = None
    transition_plan: Optional[str] = None
    transition_outcome_end_of_term: Optional[str] = None


class EnrolmentCreate(EnrolmentBase):
    pass


class EnrolmentUpdate(BaseModel):
    days: Optional[str] = None
    dual_enrollment: Optional[bool] = None
    dual_enrolment_details: Optional[str] = None
    number_of_carers: Optional[int] = None
    research_project: Optional[str] = None
    transition_plan: Optional[str] = None
    transition_outcome_end_of_term: Optional[str] = None


class Enrolment(EnrolmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Attendance schemas (aggregated term-level)
class AttendanceBase(BaseModel):
    participant_name: str
    term_1_attendance: int = 0
    term_2_attendance: int = 0
    term_3_attendance: int = 0
    term_4_attendance: int = 0


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    term_1_attendance: Optional[int] = None
    term_2_attendance: Optional[int] = None
    term_3_attendance: Optional[int] = None
    term_4_attendance: Optional[int] = None


class Attendance(AttendanceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# NewAttendance schemas (session-level check-in/out)
class NewAttendanceBase(BaseModel):
    participant_id: str
    check_time: Optional[datetime] = None  # defaults to server time if not provided
    check_in_out: str  # Sign IN | Sign OUT | Non Attendance
    is_absent: bool = False
    is_trial: bool = False
    non_attendance_reason: Optional[str] = None
    non_attendance_explanation: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None
    number_of_carers: Optional[int] = None

    @field_validator("check_time", mode="before")
    @classmethod
    def coerce_empty_check_time(cls, v):
        """Allow Budibase to send empty/whitespace string or null — all become None (server sets UTC time)."""
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v


class NewAttendanceCreate(NewAttendanceBase):
    pass


class NewAttendanceUpdate(BaseModel):
    check_time: Optional[datetime] = None
    check_in_out: Optional[str] = None
    is_absent: Optional[bool] = None
    is_trial: Optional[bool] = None
    non_attendance_reason: Optional[str] = None
    non_attendance_explanation: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None
    number_of_carers: Optional[int] = None

    @field_validator("check_time", mode="before")
    @classmethod
    def coerce_empty_check_time(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v


class NewAttendance(NewAttendanceBase):
    id: str
    debug_participant_match: Optional[str] = None
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# NewAttendanceAbsence schemas
class NewAttendanceAbsenceBase(BaseModel):
    participant_id: str
    participant_name: Optional[str] = None
    attendance_percentage: Optional[float] = None
    num_of_attendances: int = 0
    num_of_total_absences: int = 0
    explained_absences: int = 0
    unexplained_absences: int = 0
    program_cancelled_by_yili: int = 0
    other: int = 0
    paused_enrollment: Optional[str] = None


class NewAttendanceAbsenceCreate(NewAttendanceAbsenceBase):
    pass


class NewAttendanceAbsenceUpdate(BaseModel):
    participant_name: Optional[str] = None
    attendance_percentage: Optional[float] = None
    num_of_attendances: Optional[int] = None
    num_of_total_absences: Optional[int] = None
    explained_absences: Optional[int] = None
    unexplained_absences: Optional[int] = None
    program_cancelled_by_yili: Optional[int] = None
    other: Optional[int] = None
    paused_enrollment: Optional[str] = None


class NewAttendanceAbsence(NewAttendanceAbsenceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Activity schemas
class ActivityBase(BaseModel):
    participant_id: str
    date: datetime
    brain_games_booklets_minutes: float = 0
    brain_curriculum_minutes: float = 0
    online_cognitive_programs_minutes: float = 0
    cognitive_games_minutes: float = 0
    cultural_activity_minutes: float = 0
    social_and_emotional: float = 0
    literacy: float = 0
    numeracy: float = 0
    podcasting: float = 0
    music: float = 0
    art: float = 0
    virtual_reality: float = 0
    drones: float = 0
    made_by_mob: float = 0
    driving_sim: float = 0
    equine_therapy: float = 0
    job_readiness: float = 0
    life_skills: float = 0
    other_minutes: float = 0


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    brain_games_booklets_minutes: Optional[float] = None
    brain_curriculum_minutes: Optional[float] = None
    online_cognitive_programs_minutes: Optional[float] = None
    cognitive_games_minutes: Optional[float] = None
    cultural_activity_minutes: Optional[float] = None
    social_and_emotional: Optional[float] = None
    literacy: Optional[float] = None
    numeracy: Optional[float] = None
    podcasting: Optional[float] = None
    music: Optional[float] = None
    art: Optional[float] = None
    virtual_reality: Optional[float] = None
    drones: Optional[float] = None
    made_by_mob: Optional[float] = None
    driving_sim: Optional[float] = None
    equine_therapy: Optional[float] = None
    job_readiness: Optional[float] = None
    life_skills: Optional[float] = None
    other_minutes: Optional[float] = None


class Activity(ActivityBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Exercise schemas
class ExerciseBase(BaseModel):
    participant_id: str
    date: datetime
    exercise_type: Optional[str] = None
    minutes: float = 0


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    exercise_type: Optional[str] = None
    minutes: Optional[float] = None


class Exercise(ExerciseBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Assessment schemas
class AssessmentBase(BaseModel):
    participant_id: str
    date_of_completion: datetime
    assessment: Optional[str] = None
    cars_score: Optional[str] = None
    multilit_score: Optional[float] = None
    cams_score: Optional[float] = None
    cognifit_score: Optional[float] = None
    gem_hifaml_score: Optional[float] = None
    gems_tamel_score: Optional[float] = None
    gems_total: Optional[float] = None


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    assessment: Optional[str] = None
    cars_score: Optional[str] = None
    multilit_score: Optional[float] = None
    cams_score: Optional[float] = None
    cognifit_score: Optional[float] = None
    gem_hifaml_score: Optional[float] = None
    gems_tamel_score: Optional[float] = None
    gems_total: Optional[float] = None


class Assessment(AssessmentBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# BrainCheck schemas
class BrainCheckBase(BaseModel):
    participant_id: str
    date: datetime
    options: Optional[str] = None  # Pre-frontal (GREEN) | Limbic (AMBER) | Brain Stem (RED)
    check: Optional[str] = None  # Check In | Check Out


class BrainCheckCreate(BrainCheckBase):
    pass


class BrainCheckUpdate(BaseModel):
    options: Optional[str] = None
    check: Optional[str] = None


class BrainCheck(BrainCheckBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Note schemas
class NoteBase(BaseModel):
    participant_id: str
    date: datetime
    incident_occurred: Optional[bool] = None
    strengths: Optional[str] = None
    concerns: Optional[str] = None
    engagement_strategies: Optional[str] = None
    staff_reflections: Optional[str] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    incident_occurred: Optional[bool] = None
    strengths: Optional[str] = None
    concerns: Optional[str] = None
    engagement_strategies: Optional[str] = None
    staff_reflections: Optional[str] = None


class Note(NoteBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Referral schemas
class ReferralBase(BaseModel):
    participant_id: str
    referred_from: Optional[str] = None
    referee_first_name: Optional[str] = None
    referee_last_name: Optional[str] = None
    referee_full_name: Optional[str] = None
    referee_details: Optional[str] = None
    referee_email: Optional[str] = None
    phone_number: Optional[str] = None
    court_order_to_attend_yili: bool = False
    court_order_types: Optional[str] = None  # JSON array
    court_order_details: Optional[str] = None
    reason_for_referral: Optional[str] = None
    special_circumstances: Optional[str] = None
    risk_assessment_safety_info: Optional[str] = None


class ReferralCreate(ReferralBase):
    pass


class ReferralUpdate(BaseModel):
    referred_from: Optional[str] = None
    referee_first_name: Optional[str] = None
    referee_last_name: Optional[str] = None
    referee_full_name: Optional[str] = None
    referee_details: Optional[str] = None
    referee_email: Optional[str] = None
    phone_number: Optional[str] = None
    court_order_to_attend_yili: Optional[bool] = None
    court_order_types: Optional[str] = None
    court_order_details: Optional[str] = None
    reason_for_referral: Optional[str] = None
    special_circumstances: Optional[str] = None
    risk_assessment_safety_info: Optional[str] = None


class Referral(ReferralBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Contact schemas
class ContactBase(BaseModel):
    participant_id: str
    contact_name: Optional[str] = None
    contact_relationship: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    add_detail: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    contact_name: Optional[str] = None
    contact_relationship: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    add_detail: Optional[str] = None


class Contact(ContactBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# School schemas
class SchoolBase(BaseModel):
    participant_id: str
    school_name: Optional[str] = None
    year_level: Optional[int] = None
    last_date_of_school_attendance: Optional[datetime] = None
    attendance_percentage: Optional[float] = None
    usi: Optional[str] = None
    internal_school_supports: Optional[str] = None
    school_support_comment: Optional[str] = None
    external_school_supports: Optional[str] = None


class SchoolCreate(SchoolBase):
    pass


class SchoolUpdate(BaseModel):
    school_name: Optional[str] = None
    year_level: Optional[int] = None
    last_date_of_school_attendance: Optional[datetime] = None
    attendance_percentage: Optional[float] = None
    usi: Optional[str] = None
    internal_school_supports: Optional[str] = None
    school_support_comment: Optional[str] = None
    external_school_supports: Optional[str] = None


class School(SchoolBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Plan schemas
class PlanBase(BaseModel):
    participant_id: str
    plan_type: Optional[str] = None
    date_of_upload: Optional[datetime] = None
    file: Optional[str] = None  # JSON object


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    plan_type: Optional[str] = None
    date_of_upload: Optional[datetime] = None
    file: Optional[str] = None


class Plan(PlanBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# MakersAndBreakers schemas
class MakersAndBreakersBase(BaseModel):
    participant_id: str
    date: datetime
    helped_others: Optional[str] = None
    was_patient_with_others: Optional[str] = None
    expressed_gratitude: Optional[str] = None
    asked_for_help: Optional[str] = None
    kept_going_when_it_was_hard: Optional[str] = None
    distracted_others: Optional[str] = None
    disclosed_loss_or_disconnection: Optional[str] = None
    expressed_shame: Optional[str] = None
    refused_to_participate_or_follow_instruction: Optional[str] = None
    intimidates_threatened_or_hurt_others: Optional[str] = None
    played_in_a_team: Optional[str] = None
    came_back_punctually: Optional[str] = None
    was_friendly_with_others: Optional[str] = None
    self_reflected: Optional[str] = None
    spent_time_in_nature: Optional[str] = None
    shared_took_turns: Optional[str] = None


class MakersAndBreakersCreate(MakersAndBreakersBase):
    pass


class MakersAndBreakersUpdate(BaseModel):
    helped_others: Optional[str] = None
    was_patient_with_others: Optional[str] = None
    expressed_gratitude: Optional[str] = None
    asked_for_help: Optional[str] = None
    kept_going_when_it_was_hard: Optional[str] = None
    distracted_others: Optional[str] = None
    disclosed_loss_or_disconnection: Optional[str] = None
    expressed_shame: Optional[str] = None
    refused_to_participate_or_follow_instruction: Optional[str] = None
    intimidates_threatened_or_hurt_others: Optional[str] = None
    played_in_a_team: Optional[str] = None
    came_back_punctually: Optional[str] = None
    was_friendly_with_others: Optional[str] = None
    self_reflected: Optional[str] = None
    spent_time_in_nature: Optional[str] = None
    shared_took_turns: Optional[str] = None


class MakersAndBreakers(MakersAndBreakersBase):
    id: str
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None