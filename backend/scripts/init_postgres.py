#!/usr/bin/env python3
"""
Script to initialize PostgreSQL database with demo data.
Run this after deploying to Render to create demo users.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.user import User
from app.services.auth_service import hash_password


def init_database():
    """Initialize database with tables and demo users."""
    print("Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created successfully")

    print("\nCreating demo users...")
    with Session(engine) as session:
        # Check if admin already exists
        existing_admin = session.exec(
            select(User).where(User.email == "admin@milesync.demo")
        ).first()
        
        if existing_admin:
            print("✓ Admin user already exists")
        else:
            admin = User(
                email="admin@milesync.demo",
                name="Admin",
                password_hash=hash_password("admin123"),
                is_active=True,
                is_superuser=True,
            )
            session.add(admin)
            print("✓ Created admin user (admin@milesync.demo / admin123)")

        # Check if regular user already exists
        existing_user = session.exec(
            select(User).where(User.email == "user@milesync.demo")
        ).first()
        
        if existing_user:
            print("✓ Regular user already exists")
        else:
            user = User(
                email="user@milesync.demo",
                name="Super User",
                password_hash=hash_password("user123"),
                is_active=True,
                is_superuser=False,
            )
            session.add(user)
            print("✓ Created regular user (user@milesync.demo / user123)")

        session.commit()

    print("\n✅ Database initialization complete!")
    print("\nDemo Accounts:")
    print("  Admin: admin@milesync.demo / admin123")
    print("  User:  user@milesync.demo / user123")


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
