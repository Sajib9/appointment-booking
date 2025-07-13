import sys
import os

# Append the project root directory (one level up from 'seed')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.database import SessionLocal
from app.models.user import User, UserType
from app.utils.hash import hash_password
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.doctor_schedule import DoctorSchedule


def seed_users():
    db: Session = SessionLocal()
    try:
        users = [
            User(
                full_name="Admin User",
                email="admin@example.com",
                mobile="+8801000000001",
                password=hash_password("Admin@123"),
                user_type=UserType.admin,
                division="Dhaka",
                district="Dhaka",
                thana="Dhanmondi",
            ),
            User(
                full_name="Dr. Alice Smith",
                email="alice@example.com",
                mobile="+8801000000002",
                password=hash_password("Doctor@123"),
                user_type=UserType.doctor,
                division="Chattogram",
                district="Chattogram",
                thana="Panchlaish",
                license_number="DOC-12345",
                experience_years=8,
                consultation_fee=1000,
                # available_timeslots='["10:00-11:00", "14:00-15:00"]'
            ),
            User(
                full_name="Patient One",
                email="patient@example.com",
                mobile="+8801000000003",
                password=hash_password("Patient@123"),
                user_type=UserType.patient,
                division="Rajshahi",
                district="Rajshahi",
                thana="Boalia"
            ),
        ]

        for user in users:
            exists = db.query(User).filter_by(email=user.email).first()
            if not exists:
                db.add(user)

        db.commit()
        print("✅ Seeded users successfully.")
    except IntegrityError as e:
        db.rollback()
        print("⚠️ Integrity Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
