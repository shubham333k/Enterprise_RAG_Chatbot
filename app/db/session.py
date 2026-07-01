"""
Database session management.
Dev: SQLite   Production: PostgreSQL (change DATABASE_URL in .env)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.api.core.config import settings
from app.db.models import Base

# SQLite needs connect_args; PostgreSQL does not
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables. Called once at startup."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
