"""
Seed default users and roles into the database.
Run once after first setup: python scripts/seed_users.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import create_tables, SessionLocal
from app.db.models import User
from app.api.core.security import hash_password

DEFAULT_USERS = [
    {"username": "admin",      "password": "admin123",  "role": "admin",       "email": "admin@company.com"},
    {"username": "hr_user",    "password": "hr123",     "role": "hr",          "email": "hr@company.com"},
    {"username": "eng_user",   "password": "eng123",    "role": "engineering", "email": "eng@company.com"},
    {"username": "sales_user", "password": "sales123",  "role": "sales",       "email": "sales@company.com"},
    {"username": "employee",   "password": "emp123",    "role": "employee",    "email": "employee@company.com"},
]


def seed():
    print("Creating database tables...")
    create_tables()

    db = SessionLocal()
    try:
        created = 0
        for u in DEFAULT_USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if existing:
                print(f"  [SKIP] User '{u['username']}' already exists, skipping.")
                continue
            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            created += 1
            print(f"  [OK]   Created user '{u['username']}' with role '{u['role']}'")

        db.commit()
        print(f"\n[DONE] Seeding complete. {created} new users created.")
        print("\nDefault credentials:")
        print("  admin / admin123       -> All access")
        print("  hr_user / hr123        -> HR docs")
        print("  eng_user / eng123      -> Engineering docs")
        print("  sales_user / sales123  -> Sales docs")
        print("  employee / emp123      -> Public docs only")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
