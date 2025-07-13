from pydantic import BaseModel,Field
from datetime import date, time
from typing import List, Literal
from app.models.doctor_schedule import ScheduleStatus
from typing import Optional

class ScheduleCreate(BaseModel):
    date: date
    start_time: time = Field(example="10:00:00")
    end_time: time = Field(example="11:00:00")
    status: ScheduleStatus = ScheduleStatus.available

class ScheduleBulkCreate(BaseModel):
    schedules: List[ScheduleCreate]

class ScheduleResponse(BaseModel):
    id: int
    doctor_id: int
    date: date
    start_time: time
    end_time: time
    status: str

    class Config:
        orm_mode = True


class ScheduleResponse(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    status: str

    class Config:
        orm_mode = True


class DoctorBasicInfo(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]
    consultation_fee: Optional[int]

    # Add schedules list here:
    schedule: List[ScheduleResponse] = []
