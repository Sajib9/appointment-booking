from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Literal, List
from enum import Enum
from datetime import datetime

class UserType(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: constr(regex=r'^\+88\d{11}$')
    password: constr(
        min_length=8,
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./<>?]).+$'
    )
    user_type: UserType
    division: str
    district: str
    thana: str
    license_number: Optional[str]
    experience_years: Optional[int]
    consultation_fee: Optional[int]

class UserUpdate(BaseModel):
    full_name: Optional[str]
    mobile: Optional[constr(regex=r'^\+88\d{11}$')]
    password: Optional[
        constr(
            min_length=8,
            regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./<>?]).+$'
        )
    ]
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]
    profile_image: Optional[str]

    # Doctor-only fields
    license_number: Optional[str]
    experience_years: Optional[int]
    consultation_fee: Optional[int]

class DoctorList(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]
    license_number: Optional[str]
    experience_years: Optional[int]
    consultation_fee: Optional[int]

    class Config:
        orm_mode = True

class DoctorBasic(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        orm_mode = True

class AppointmentBasic(BaseModel):
    id: int
    appointment_datetime: datetime
    status: str
    notes: Optional[str] = None
    doctor: DoctorBasic

    class Config:
        orm_mode = True

class PatientWithAppointments(BaseModel):
    id: int
    full_name: str
    email: str
    appointments: List[AppointmentBasic] = []

    class Config:
        orm_mode = True