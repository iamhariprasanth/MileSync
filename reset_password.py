
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, "/var/www/milesync/backend")

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.services.auth_service import hash_password, verify_password

def reset_and_verify():
    print("Checking database connection...")
    try:
        with Session(engine) as session:
            print("Connected to database.")
            
            # 1. Fetch Admin User
            admin = session.exec(select(User).where(User.email == "admin@milesync.demo")).first()
            if not admin:
                print("❌ Admin user not found!")
                return
            
            print(f"Found admin user: {admin.email}")
            print(f"Current hash prefix: {admin.password_hash[:10]}...")
            
            # 2. Reset Password
            new_password = "admin123"
            new_hash = hash_password(new_password)
            admin.password_hash = new_hash
            session.add(admin)
            session.commit()
            print(f"✓ Reset password for {admin.email} to '{new_password}'")
            
            # 3. Verify immediately
            session.refresh(admin)
            is_valid = verify_password(new_password, admin.password_hash)
            print(f"✓ Immediate verification check: {'PASSED' if is_valid else 'FAILED'}")

            # 4. Fetch Regular User
            user = session.exec(select(User).where(User.email == "user@milesync.demo")).first()
            if user:
                print(f"Found regular user: {user.email}")
                user_pass = "user123"
                user.password_hash = hash_password(user_pass)
                session.add(user)
                session.commit()
                print(f"✓ Reset password for {user.email} to '{user_pass}'")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_and_verify()
