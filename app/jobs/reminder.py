import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.appoitment import Appointment
from app.models.user import User
from sqlalchemy.orm import Session
from app.utils.email import send_email

def send_appointment_reminders():
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        next_24_hours = now + timedelta(hours=24)

        appointments = db.query(Appointment).filter(
            Appointment.status == "confirmed",
            Appointment.appointment_datetime >= now,
            Appointment.appointment_datetime <= next_24_hours
        ).all()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for appt in appointments:
            patient: User = appt.patient
            subject = "Appointment Reminder"
            body = f"""
                <p>Dear {patient.full_name},</p>
                <p>This is a reminder for your appointment with Dr. ID {appt.doctor_id} on {appt.appointment_datetime.strftime('%Y-%m-%d %H:%M')}.</p>
                <p>Thank you!</p>
            """
            loop.run_until_complete(send_email(subject, [patient.email], body))
        db.close()
    except Exception as e:
        db.rollback()
        print("❌ Error in appointment reminder job:", e)

