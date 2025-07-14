from sqlalchemy import Column, Integer, String, Enum, Text
from app.database import Base
import enum
from sqlalchemy.orm import relationship

class UserType(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True, nullable=False)
    mobile = Column(String(14), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), default="patient")
    division = Column(String(100))
    district = Column(String(100))
    thana = Column(String(100))
    profile_image = Column(String(255), nullable=True)

    # Doctor-specific
    license_number = Column(String(100), nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Integer, nullable=True)
    # available_timeslots = Column(Text, nullable=True)  # JSON string

    schedules = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")

    # Patients -> appointments they booked
    appointments = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id")

    # Doctors -> appointments they received
    doctor_appointments = relationship("Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id")
