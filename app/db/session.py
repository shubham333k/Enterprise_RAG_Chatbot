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
    """Create all tables and seed default users if empty."""
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed default users if database is fresh
    from app.db.models import User
    from app.api.core.security import hash_password
    
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            default_users = [
                {"username": "admin",      "password": "admin123",  "role": "admin",       "email": "admin@company.com"},
                {"username": "hr_user",    "password": "hr123",     "role": "hr",          "email": "hr@company.com"},
                {"username": "eng_user",   "password": "eng123",    "role": "engineering", "email": "eng@company.com"},
                {"username": "sales_user", "password": "sales123",  "role": "sales",       "email": "sales@company.com"},
                {"username": "employee",   "password": "emp123",    "role": "employee",    "email": "employee@company.com"},
            ]
            for u in default_users:
                user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                )
                db.add(user)
            db.commit()
    except Exception as e:
        db.rollback()
        # Non-fatal error during auto-seed
        import logging
        logging.getLogger(__name__).warning(f"Auto-seeding skipped: {e}")
    finally:
        db.close()



def get_db() -> Session:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
