from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Literal
from enum import Enum

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
    # available_timeslots: Optional[str]
