import asyncio
from datetime import datetime
from app.database import SessionLocal
from app.models.appoitment import Appointment
from app.models.user import User
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.utils.email import send_email

def generate_monthly_reports():
    db: Session = SessionLocal()
    try:
        today = datetime.today()
        first_day = today.replace(day=1)
        last_day = today

        doctors = db.query(User).filter(User.user_type == "doctor").all()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for doc in doctors:
            stats = db.query(
                func.count(Appointment.id).label("total_appointments"),
                func.count(func.distinct(Appointment.patient_id)).label("total_patients"),
                func.sum(Appointment.consultation_fee).label("total_earned")
            ).filter(
                Appointment.doctor_id == doc.id,
                Appointment.appointment_datetime >= first_day,
                Appointment.appointment_datetime <= last_day,
                Appointment.status == "completed"
            ).first()

            subject = f"Monthly Report for {doc.full_name}"
            body = f"""
                <h3>Monthly Report</h3>
                <p>Appointments: {stats.total_appointments}</p>
                <p>Patients: {stats.total_patients}</p>
                <p>Total Earned: ৳{stats.total_earned or 0}</p>
            """
            loop.run_until_complete(send_email(subject, [doc.email], body))

        db.close()
    except Exception as e:
        db.rollback()
        print("❌ Error generating monthly report:", e)

