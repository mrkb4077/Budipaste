from sqlalchemy import inspect, text

from app.db.base_class import Base
from app.db.session import engine


LEGACY_COLUMN_PATCHES = {
    "participants": {
        "identifier": "VARCHAR",
        "first_name": "VARCHAR",
        "last_name": "VARCHAR",
        "full_name": "VARCHAR",
        "gender": "VARCHAR",
        "cultural_identity": "TEXT",
        "living_situation": "TEXT",
        "employment": "TEXT",
        "address_1": "VARCHAR",
        "address_2": "VARCHAR",
        "address_3": "VARCHAR",
        "contact_ph_1": "VARCHAR",
        "contact_ph_2": "VARCHAR",
        "contact_ph_3": "VARCHAR",
        "is_enrolled": "BOOLEAN DEFAULT TRUE",
        "date_last_attended": "DATETIME",
        "date_commenced": "DATETIME",
        "dietary_needs": "TEXT",
        "medical_needs": "TEXT",
        "neuro_diverse": "TEXT",
        "learning_disorder": "TEXT",
        "physical_disorder": "TEXT",
        "cannot_be_around": "TEXT",
        "contact_1_name": "VARCHAR",
        "contact_1_relationship": "VARCHAR",
        "contact_2_name": "VARCHAR",
        "contact_2_relationship": "VARCHAR",
        "contact_3_name": "VARCHAR",
        "contact_3_relationship": "VARCHAR",
    },
    "activities": {
        "brain_games_booklets_minutes": "FLOAT DEFAULT 0",
        "brain_curriculum_minutes": "FLOAT DEFAULT 0",
        "online_cognitive_programs_minutes": "FLOAT DEFAULT 0",
        "cognitive_games_minutes": "FLOAT DEFAULT 0",
        "cultural_activity_minutes": "FLOAT DEFAULT 0",
        "social_and_emotional": "FLOAT DEFAULT 0",
        "literacy": "FLOAT DEFAULT 0",
        "numeracy": "FLOAT DEFAULT 0",
        "podcasting": "FLOAT DEFAULT 0",
        "music": "FLOAT DEFAULT 0",
        "art": "FLOAT DEFAULT 0",
        "virtual_reality": "FLOAT DEFAULT 0",
        "drones": "FLOAT DEFAULT 0",
        "made_by_mob": "FLOAT DEFAULT 0",
        "driving_sim": "FLOAT DEFAULT 0",
        "equine_therapy": "FLOAT DEFAULT 0",
        "job_readiness": "FLOAT DEFAULT 0",
        "life_skills": "FLOAT DEFAULT 0",
        "other_minutes": "FLOAT DEFAULT 0",
    },
    "attendance": {
        "participant_name": "VARCHAR",
        "term_1_attendance": "INTEGER DEFAULT 0",
        "term_2_attendance": "INTEGER DEFAULT 0",
        "term_3_attendance": "INTEGER DEFAULT 0",
        "term_4_attendance": "INTEGER DEFAULT 0",
    },
}


def upgrade_legacy_schema() -> None:
    inspector = inspect(engine)
    existing_columns_by_table = {}

    with engine.begin() as connection:
        for table_name, columns in LEGACY_COLUMN_PATCHES.items():
            if not inspector.has_table(table_name):
                continue

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name not in existing_columns:
                    connection.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    )
                    existing_columns.add(column_name)

            existing_columns_by_table[table_name] = existing_columns

        if inspector.has_table("participants"):
            participant_columns = existing_columns_by_table.get(
                "participants",
                {column["name"] for column in inspector.get_columns("participants")},
            )
            select_columns = [
                "id",
                "date_of_birth",
                "identifier",
                "first_name",
                "last_name",
                "full_name",
                "is_enrolled",
            ]
            if "name" in participant_columns:
                select_columns.append("name")
            if "is_active" in participant_columns:
                select_columns.append("is_active")

            rows = connection.execute(
                text(f"SELECT {', '.join(select_columns)} FROM participants")
            ).mappings().all()

            for row in rows:
                full_name = row.get("full_name") or row.get("name") or "Unknown Participant"
                first_name, _, remaining_name = full_name.partition(" ")
                last_name = row.get("last_name") or remaining_name
                date_of_birth = str(row.get("date_of_birth") or "unknown")[:10]
                identifier = row.get("identifier") or f"{full_name} | {date_of_birth}"
                is_enrolled = row.get("is_enrolled")
                if is_enrolled is None:
                    is_enrolled = bool(row.get("is_active", True))

                connection.execute(
                    text(
                        """
                        UPDATE participants
                        SET identifier = :identifier,
                            first_name = COALESCE(first_name, :first_name),
                            last_name = COALESCE(last_name, :last_name),
                            full_name = COALESCE(full_name, :full_name),
                            is_enrolled = COALESCE(is_enrolled, :is_enrolled)
                        WHERE id = :participant_id
                        """
                    ),
                    {
                        "identifier": identifier,
                        "first_name": first_name or full_name,
                        "last_name": last_name,
                        "full_name": full_name,
                        "is_enrolled": is_enrolled,
                        "participant_id": row["id"],
                    },
                )

            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_participants_identifier "
                    "ON participants (identifier)"
                )
            )

        # Drop legacy FK constraints that point to participants.identifier
        # (all participant_id columns are now plain strings, not foreign keys)
        fk_drops = [
            ("enrolment", "enrolment_participant_id_fkey"),
            ("attendance", "attendance_participant_name_fkey"),
            ("new_attendance", "new_attendance_participant_id_fkey"),
            ("new_attendance_absence", "new_attendance_absence_participant_id_fkey"),
            ("activities", "activities_participant_id_fkey"),
            ("exercise", "exercise_participant_id_fkey"),
            ("assessments", "assessments_participant_id_fkey"),
            ("brain_check", "brain_check_participant_id_fkey"),
            ("notes", "notes_participant_id_fkey"),
            ("referrals", "referrals_participant_id_fkey"),
            ("contacts", "contacts_participant_id_fkey"),
            ("school", "school_participant_id_fkey"),
            ("plan", "plan_participant_id_fkey"),
            ("makers_and_breakers", "makers_and_breakers_participant_id_fkey"),
        ]
        for table_name, constraint_name in fk_drops:
            if inspector.has_table(table_name):
                connection.execute(
                    text(
                        f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}"
                    )
                )

        if inspector.has_table("attendance"):
            attendance_columns = existing_columns_by_table.get(
                "attendance",
                {column["name"] for column in inspector.get_columns("attendance")},
            )
            if "participant_id" in attendance_columns and "participant_name" in attendance_columns:
                connection.execute(
                    text(
                        """
                        UPDATE attendance
                        SET participant_name = COALESCE(participant_name, participant_id)
                        WHERE participant_name IS NULL OR participant_name = ''
                        """
                    )
                )

        if inspector.has_table("activities"):
            activity_columns = existing_columns_by_table.get(
                "activities",
                {column["name"] for column in inspector.get_columns("activities")},
            )
            if "duration_minutes" in activity_columns:
                connection.execute(
                    text(
                        """
                        UPDATE activities
                        SET other_minutes = COALESCE(other_minutes, duration_minutes, 0)
                        WHERE other_minutes IS NULL
                        """
                    )
                )


def init_db():
    # Import all models here to ensure they are registered with SQLAlchemy
    from app.models import models  # noqa: F401

    # Repair legacy schemas first so dependent foreign keys can be created safely.
    upgrade_legacy_schema()
    Base.metadata.create_all(bind=engine)