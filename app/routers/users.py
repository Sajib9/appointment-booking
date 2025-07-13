from fastapi import APIRouter, Depends, HTTPException,Body
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.utils.hash import hash_password
from app.database import get_db
from app.models.user import User
from typing import List
import json
from app.routers.auth import get_current_user
from app.schemas.user import UserType

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == user.email) | (User.mobile == user.mobile)).first():
        raise HTTPException(status_code=400, detail="Email or Mobile already exists")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        mobile=user.mobile,
        password=hash_password(user.password),
        user_type=user.user_type,
        division=user.division,
        district=user.district,
        thana=user.thana,
        license_number=user.license_number,
        experience_years=user.experience_years,
        consultation_fee=user.consultation_fee,
        # available_timeslots=user.available_timeslots,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

