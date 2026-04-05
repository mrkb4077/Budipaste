from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="staff")  # admin, manager, staff
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Participant(Base):
    __tablename__ = "participants"

    id = Column(String, primary_key=True, index=True)  # Budibase _id format
    identifier = Column(String, unique=True, index=True, nullable=False)  # "Full Name | YYYY-MM-DD"
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String)  # Male | Female | Gender Fluid/Non-binary | Other/Prefer not to say
    cultural_identity = Column(Text)  # JSON array as string
    living_situation = Column(Text)
    employment = Column(Text)  # JSON array as string
    address_1 = Column(String)
    address_2 = Column(String)
    address_3 = Column(String)
    contact_ph_1 = Column(String)
    contact_ph_2 = Column(String)
    contact_ph_3 = Column(String)
    is_enrolled = Column(Boolean, default=True)
    date_last_attended = Column(DateTime)
    date_commenced = Column(DateTime)
    dietary_needs = Column(Text)
    medical_needs = Column(Text)  # HIGH sensitivity
    neuro_diverse = Column(Text)
    learning_disorder = Column(Text)
    physical_disorder = Column(Text)
    cannot_be_around = Column(Text)  # exclusion/safety constraints
    contact_1_name = Column(String)
    contact_1_relationship = Column(String)
    contact_2_name = Column(String)
    contact_2_relationship = Column(String)
    contact_3_name = Column(String)
    contact_3_relationship = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrolments = relationship("Enrolment", back_populates="participant")
    attendances = relationship("Attendance", back_populates="participant")
    new_attendances = relationship("NewAttendance", back_populates="participant")
    new_attendance_absences = relationship("NewAttendanceAbsence", back_populates="participant")
    activities = relationship("Activity", back_populates="participant")
    exercises = relationship("Exercise", back_populates="participant")
    assessments = relationship("Assessment", back_populates="participant")
    brain_checks = relationship("BrainCheck", back_populates="participant")
    notes = relationship("Note", back_populates="participant")
    referrals = relationship("Referral", back_populates="participant")
    contacts = relationship("Contact", back_populates="participant")
    schools = relationship("School", back_populates="participant")
    plans = relationship("Plan", back_populates="participant")
    makers_and_breakers = relationship("MakersAndBreakers", back_populates="participant")


class Enrolment(Base):
    __tablename__ = "enrolment"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    term = Column(Integer, nullable=False)  # 1-4
    year = Column(Integer, nullable=False)
    days = Column(Text)  # JSON array as string: ["Monday", "Wednesday"]
    dual_enrollment = Column(Boolean, default=False)
    dual_enrolment_details = Column(Text)
    number_of_carers = Column(Integer)
    research_project = Column(String)  # Yes with Parent and Participant Consent | Yes with Participant Consent only | No | Unsure
    transition_plan = Column(Text)
    transition_outcome_end_of_term = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="enrolments")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_name = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    term_1_attendance = Column(Integer, default=0)
    term_2_attendance = Column(Integer, default=0)
    term_3_attendance = Column(Integer, default=0)
    term_4_attendance = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="attendances")


class NewAttendance(Base):
    __tablename__ = "new_attendance"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    check_time = Column(DateTime, nullable=False)
    check_in_out = Column(String, nullable=False)  # Sign IN | Sign OUT | Non Attendance
    is_absent = Column(Boolean, default=False)
    is_trial = Column(Boolean, default=False)
    non_attendance_reason = Column(String)  # Explained Absence | Unexplained Absence | Program Cancelled by Yili | Other
    non_attendance_explanation = Column(Text)
    guardian_name = Column(String)
    guardian_contact = Column(String)
    number_of_carers = Column(Integer)
    debug_participant_match = Column(String)  # Internal field - exclude from reporting
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="new_attendances")


class NewAttendanceAbsence(Base):
    __tablename__ = "new_attendance_absence"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    participant_name = Column(String)
    attendance_percentage = Column(Float)
    num_of_attendances = Column(Integer, default=0)
    num_of_total_absences = Column(Integer, default=0)
    explained_absences = Column(Integer, default=0)
    unexplained_absences = Column(Integer, default=0)
    program_cancelled_by_yili = Column(Integer, default=0)
    other = Column(Integer, default=0)
    paused_enrollment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="new_attendance_absences")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    date = Column(DateTime, nullable=False)
    brain_games_booklets_minutes = Column(Float, default=0)
    brain_curriculum_minutes = Column(Float, default=0)
    online_cognitive_programs_minutes = Column(Float, default=0)
    cognitive_games_minutes = Column(Float, default=0)
    cultural_activity_minutes = Column(Float, default=0)
    social_and_emotional = Column(Float, default=0)
    literacy = Column(Float, default=0)
    numeracy = Column(Float, default=0)
    podcasting = Column(Float, default=0)
    music = Column(Float, default=0)
    art = Column(Float, default=0)
    virtual_reality = Column(Float, default=0)
    drones = Column(Float, default=0)
    made_by_mob = Column(Float, default=0)
    driving_sim = Column(Float, default=0)
    equine_therapy = Column(Float, default=0)
    job_readiness = Column(Float, default=0)
    life_skills = Column(Float, default=0)
    other_minutes = Column(Float, default=0)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="activities")


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    date = Column(DateTime, nullable=False)  # NOTE: lowercase in export
    exercise_type = Column(String)
    minutes = Column(Float, default=0)  # NOTE: lowercase in export
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="exercises")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    date_of_completion = Column(DateTime, nullable=False)
    assessment = Column(String)  # CARS Literacy | Multi-lit Sight Words | CAMS Math | CogniFit | GEMS Youth Wellbeing Tool
    cars_score = Column(String)  # Grade/letter format
    multilit_score = Column(Float)
    cams_score = Column(Float)
    cognifit_score = Column(Float)
    gem_hifaml_score = Column(Float)  # GEMS sub-score
    gems_tamel_score = Column(Float)  # GEMS sub-score
    gems_total = Column(Float)  # GEMS composite total
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="assessments")


class BrainCheck(Base):
    __tablename__ = "brain_check"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    date = Column(DateTime, nullable=False)
    options = Column(String)  # Pre-frontal (GREEN) | Limbic (AMBER) | Brain Stem (RED)
    check = Column(String)  # Check In | Check Out
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="brain_checks")


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    date = Column(DateTime, nullable=False)
    incident_occurred = Column(Boolean)
    strengths = Column(Text)
    concerns = Column(Text)
    engagement_strategies = Column(Text)
    staff_reflections = Column(Text)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="notes")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    referred_from = Column(String)
    referee_first_name = Column(String)
    referee_last_name = Column(String)
    referee_full_name = Column(String)
    referee_details = Column(Text)
    referee_email = Column(String)
    phone_number = Column(String)
    court_order_to_attend_yili = Column(Boolean, default=False)
    court_order_types = Column(Text)  # JSON array: ["Youth Justice", "Custody"]
    court_order_details = Column(Text)
    reason_for_referral = Column(Text)
    special_circumstances = Column(Text)
    risk_assessment_safety_info = Column(Text)  # HIGH sensitivity
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="referrals")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    contact_name = Column(String)
    contact_relationship = Column(String)  # Legal Guardian | YJ Case Manager | Child Safety Officer | Team Leader | Other
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    add_detail = Column(Text)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="contacts")


class School(Base):
    __tablename__ = "school"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    school_name = Column(String)
    year_level = Column(Integer)
    last_date_of_school_attendance = Column(DateTime)
    attendance_percentage = Column(Float)
    usi = Column(String)  # Unique Student Identifier
    internal_school_supports = Column(String)
    school_support_comment = Column(Text)
    external_school_supports = Column(Text)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="schools")


class Plan(Base):
    __tablename__ = "plan"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    plan_type = Column(String)  # Yili Plan (additional types may be added)
    date_of_upload = Column(DateTime)  # NOTE: camelCase in export
    file = Column(Text)  # JSON object with name, size, extension, signed URL
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="plans")


class MakersAndBreakers(Base):
    __tablename__ = "makers_and_breakers"

    id = Column(String, primary_key=True, index=True)  # Budibase _id
    participant_id = Column(String, ForeignKey("participants.identifier"), nullable=False)
    participant_uuid = Column(String, index=True)
    date = Column(DateTime, nullable=False)

    # All 16 fields use: Not Observed | Somewhat Observed | Frequently Observed
    helped_others = Column(String)
    was_patient_with_others = Column(String)
    expressed_gratitude = Column(String)
    asked_for_help = Column(String)
    kept_going_when_it_was_hard = Column(String)
    distracted_others = Column(String)
    disclosed_loss_or_disconnection = Column(String)
    expressed_shame = Column(String)
    refused_to_participate_or_follow_instruction = Column(String)
    intimidates_threatened_or_hurt_others = Column(String)
    played_in_a_team = Column(String)
    came_back_punctually = Column(String)
    was_friendly_with_others = Column(String)
    self_reflected = Column(String)
    spent_time_in_nature = Column(String)
    shared_took_turns = Column(String)

    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="makers_and_breakers")