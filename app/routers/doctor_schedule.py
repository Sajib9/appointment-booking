from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal
from app.models.doctor_schedule import DoctorSchedule
from app.models.user import User, UserType
from app.schemas.doctor_schedule import ScheduleBulkCreate, ScheduleResponse
from app.routers.auth import get_current_user
from math import ceil
from app.schemas.paginated import PaginatedResponse
from datetime import datetime, time, date
from typing import Optional
from app.schemas.doctor_schedule import DoctorBasicInfo

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


BUSINESS_START = time(9, 0)  # 09:00
BUSINESS_END = time(18, 0)   # 18:00

@router.post("/set-availability")
def set_availability(
    payload: ScheduleBulkCreate,
    doctor_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type == UserType.doctor:
        target_doctor_id = current_user.id
    elif current_user.user_type == UserType.admin:
        if not doctor_id:
            raise HTTPException(status_code=400, detail="doctor_id is required for admin.")
        doctor = db.query(User).filter(User.id == doctor_id, User.user_type == UserType.doctor).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found.")
        target_doctor_id = doctor.id
    else:
        raise HTTPException(status_code=403, detail="Only doctor or admin can set availability.")


    inserted_count = 0
    skipped_count = 0

    today = date.today()
    now = datetime.now().time()

    for schedule in payload.schedules:
        #Check if date/time is not in the past
        if schedule.date < today or (schedule.date == today and schedule.start_time <= now):
            raise HTTPException(
                status_code=400,
                detail=f"Schedule {schedule.date} {schedule.start_time} is in the past."
            )

        #Check if timeslot within business hours
        if schedule.start_time < BUSINESS_START or schedule.end_time > BUSINESS_END:
            raise HTTPException(
                status_code=400,
                detail=f"Schedule {schedule.start_time} to {schedule.end_time} is outside business hours."
            )

        #Check for existing schedule
        exists = db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == target_doctor_id,
            DoctorSchedule.date == schedule.date,
            DoctorSchedule.start_time == schedule.start_time,
            DoctorSchedule.end_time == schedule.end_time
        ).first()

        if not exists:
            new_slot = DoctorSchedule(
                doctor_id=target_doctor_id,
                date=schedule.date,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                status=schedule.status
            )
            db.add(new_slot)
            inserted_count += 1
        else:
            skipped_count += 1

    db.commit()
    return {
        "message": "Availability update completed",
        "inserted": inserted_count,
        "skipped_existing": skipped_count
    }


@router.get("/doctor-availability/{doctor_id}", response_model=PaginatedResponse[ScheduleResponse])
def get_doctor_schedule(
    doctor_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    doctor = db.query(User).filter(User.id == doctor_id, User.user_type == UserType.doctor).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    query = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_id)
    total = query.count()
    total_pages = ceil(total / limit)

    schedules = query.order_by(DoctorSchedule.date, DoctorSchedule.start_time) \
                     .offset((page - 1) * limit) \
                     .limit(limit) \
                     .all()

    return PaginatedResponse(
        data=schedules,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.delete("/delete/{schedule_id}")
def delete_schedule(
    schedule_id: int = Path(..., description="Schedule ID to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.doctor:
        raise HTTPException(status_code=403, detail="Only doctors can delete their availability")

    schedule = db.query(DoctorSchedule).filter(
        DoctorSchedule.id == schedule_id,
        DoctorSchedule.doctor_id == current_user.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found or not owned by doctor")

    db.delete(schedule)
    db.commit()
    return {"message": f"Schedule ID {schedule_id} deleted successfully"}

@router.get("/doctor-availability", response_model=PaginatedResponse[DoctorBasicInfo])
def get_all_doctor_schedules(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type not in [UserType.admin, UserType.patient]:
        raise HTTPException(status_code=403, detail="Only Admin or Patient can access all doctor schedules")

    # Base query from User filtered by doctors
    query = db.query(User).options(
        joinedload(User.schedules)
    ).filter(
        User.user_type == UserType.doctor
    )

    total = query.count()
    total_pages = ceil(total / limit)

    doctors = query.order_by(User.full_name) \
                   .offset((page - 1) * limit) \
                   .limit(limit) \
                   .all()

    response_data = []
    for doctor in doctors:
        available_schedules = [
            {
                "id": sched.id,
                "date": sched.date,
                "start_time": sched.start_time,
                "end_time": sched.end_time,
                'status': sched.status,
            }
            for sched in doctor.schedules if getattr(sched, 'status', 'available') == 'available'
        ]

        doc_dict = {
            "id": doctor.id,
            "full_name": doctor.full_name,
            "email": doctor.email,
            "mobile": doctor.mobile,
            "division": doctor.division,
            "district": doctor.district,
            "thana": doctor.thana,
            "schedule": available_schedules,
        }
        response_data.append(doc_dict)

    return PaginatedResponse(
        data=response_data,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

