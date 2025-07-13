from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_datetime: datetime = Field(
        example="2025-07-13T07:05:59"
    )
    notes: Optional[str]

    @validator("appointment_datetime")
    def remove_microseconds(cls, value: datetime) -> datetime:
        return value.replace(microsecond=0)

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_datetime: datetime
    notes: Optional[str]
    status: AppointmentStatus

    class Config:
        orm_mode = True

class AppointmentUpdateStatus(BaseModel):
    appointment_id: int
    status: AppointmentStatus

