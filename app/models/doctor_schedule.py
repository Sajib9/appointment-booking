from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Enum
from app.database import Base
from sqlalchemy.orm import relationship
import enum

class ScheduleStatus(str, enum.Enum):
    available = "available"
    booked = "booked"
class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.available, nullable=False)

    doctor = relationship("User", back_populates="schedules")
