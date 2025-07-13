from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.appoitment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdateStatus
from app.models.user import User, UserType
from datetime import datetime
from app.routers.auth import get_current_user
from app.schemas.paginated import PaginatedResponse
from math import ceil
import json
from app.models.doctor_schedule import DoctorSchedule, ScheduleStatus

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AppointmentResponse)
def book_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.patient:
        raise HTTPException(status_code=403, detail="Only patients can book appointments")

    if appointment.appointment_datetime < datetime.now():
        raise HTTPException(status_code=400, detail="Appointment time cannot be in the past")

    doctor = db.query(User).filter(User.id == appointment.doctor_id, User.user_type == UserType.doctor).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check doctor's schedule availability
    schedule = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == appointment.doctor_id,
        DoctorSchedule.date == appointment.appointment_datetime.date(),
        DoctorSchedule.start_time <= appointment.appointment_datetime.time(),
        DoctorSchedule.end_time > appointment.appointment_datetime.time(),
        DoctorSchedule.status == "available"
    ).first()

    if not schedule:
        raise HTTPException(status_code=400, detail="Doctor is not available at this time")

    # Check appointment conflict
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_datetime == appointment.appointment_datetime,
        Appointment.status != AppointmentStatus.cancelled
    ).first()

    if existing_appointment:
        raise HTTPException(status_code=400, detail="This timeslot is already booked")

    new_appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=appointment.doctor_id,
        appointment_datetime=appointment.appointment_datetime,
        notes=appointment.notes,
        status=AppointmentStatus.pending,
    )
    schedule.status = "booked"
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@router.get("/", response_model=PaginatedResponse[AppointmentResponse])
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(Appointment)

    if current_user.user_type == UserType.patient:
        query = query.filter(Appointment.patient_id == current_user.id)
    elif current_user.user_type == UserType.doctor:
        query = query.filter(Appointment.doctor_id == current_user.id)

    total = query.count()
    total_pages = ceil(total / limit)
    appointments = query.order_by(Appointment.appointment_datetime.desc()) \
        .offset((page - 1) * limit) \
        .limit(limit) \
        .all()

    return PaginatedResponse(
        data=appointments,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.put("/status-update")
def update_appointment_status(
    data: AppointmentUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Admin can update any appointment to any status
    if current_user.user_type == UserType.admin:
        appointment.status = data.status
        db.commit()
        return {"message": f"Appointment status updated to {data.status} by admin"}

    # Doctor can update only their own appointments
    elif current_user.user_type == UserType.doctor:
        if appointment.doctor_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update your own appointments")
        appointment.status = data.status
        db.commit()
        return {"message": f"Appointment status updated to {data.status} by doctor"}

    # Patient can only cancel their own appointment
    elif current_user.user_type == UserType.patient:
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update your own appointments")
        if data.status != AppointmentStatus.cancelled:
            raise HTTPException(status_code=403, detail="You can only cancel appointments")
        if appointment.status == AppointmentStatus.cancelled:
            raise HTTPException(status_code=400, detail="Appointment already cancelled")
        if appointment.appointment_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Cannot cancel past appointments")

        # Mark appointment as cancelled
        appointment.status = AppointmentStatus.cancelled

        # Free up schedule
        schedule = db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == appointment.doctor_id,
            DoctorSchedule.date == appointment.appointment_datetime.date(),
            DoctorSchedule.start_time <= appointment.appointment_datetime.time(),
            DoctorSchedule.end_time > appointment.appointment_datetime.time(),
            DoctorSchedule.status == ScheduleStatus.booked
        ).first()

        if schedule:
            schedule.status = ScheduleStatus.available

        db.commit()
        return {"message": "Appointment cancelled by patient and slot freed"}

    raise HTTPException(status_code=403, detail="Unauthorized action")


