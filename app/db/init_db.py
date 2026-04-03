from app.db.base_class import Base
from app.db.session import engine

def init_db():
    # Import all models here to ensure they are registered with SQLAlchemy
    from app.models import models  # noqa: F401

    Base.metadata.create_all(bind=engine)