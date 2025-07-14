import sys
import os
from datetime import date, timedelta, time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.database import SessionLocal
from app.models.user import User
from app.models.doctor_schedule import DoctorSchedule, ScheduleStatus
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def seed_doctor_schedules():
    db: Session = SessionLocal()

    try:
        doctor = db.query(User).filter(User.email == "alice@example.com").first()
        if not doctor:
            print("Doctor not found. Please seed users first.")
            return

        # Clear old schedules
        db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor.id).delete()

        schedules = []
        today = date.today()
        for i in range(7):  # next 7 days
            schedule_date = today + timedelta(days=i)
            schedules.append(DoctorSchedule(
                doctor_id=doctor.id,
                date=schedule_date,
                start_time=time(10, 0),
                end_time=time(11, 0),
                status=ScheduleStatus.available
            ))
            schedules.append(DoctorSchedule(
                doctor_id=doctor.id,
                date=schedule_date,
                start_time=time(14, 0),
                end_time=time(15, 0),
                status=ScheduleStatus.available
            ))

        db.bulk_save_objects(schedules)
        db.commit()
        print(f"Seeded schedules for Dr. Alice Smith for {len(schedules)} slots.")

    except IntegrityError as e:
        db.rollback()
        print("Integrity Error:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_doctor_schedules()
