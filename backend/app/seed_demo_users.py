"""Seed script to create demo users for testing.

Run with: python -m app.seed_demo_users
"""

from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models.user import User, AuthProvider
from app.services.auth_service import hash_password


DEMO_USERS = [
    {
        "email": "admin@milesync.demo",
        "name": "Admin User",
        "password": "admin123",
    },
    {
        "email": "user@milesync.demo",
        "name": "Demo User",
        "password": "user123",
    },
]


def seed_demo_users():
    """Create demo users if they don't exist."""
    create_db_and_tables()

    with Session(engine) as session:
        created_count = 0

        for user_data in DEMO_USERS:
            # Check if user already exists
            existing = session.exec(
                select(User).where(User.email == user_data["email"])
            ).first()

            if existing:
                print(f"User '{user_data['email']}' already exists, skipping.")
                continue

            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                password_hash=hash_password(user_data["password"]),
                auth_provider=AuthProvider.EMAIL,
                is_active=True,
            )
            session.add(user)
            created_count += 1
            print(f"Created user: {user_data['email']}")

        session.commit()
        print(f"\nDone! Created {created_count} new user(s).")
        print("\n--- Demo Credentials ---")
        print("Admin:  admin@milesync.demo / admin123")
        print("User:   user@milesync.demo / user123")


if __name__ == "__main__":
    seed_demo_users()
