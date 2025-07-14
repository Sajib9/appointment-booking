from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session, joinedload
from app.schemas.user import UserCreate
from app.utils.hash import hash_password
from app.database import get_db
from app.models.user import User
from app.schemas.paginated import PaginatedResponse
from app.routers.auth import get_current_user
from app.schemas.user import UserType,UserUpdate,DoctorList
from math import ceil
from app.models.appoitment import Appointment
from app.schemas.user import PatientWithAppointments
from datetime import date
from app.models.doctor_schedule import DoctorSchedule, ScheduleStatus

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

@router.put("/update-profile")
def update_profile(
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = updates.dict(exclude_unset=True)

    restricted_email_mobile = {"email"}
    if restricted_email_mobile & update_data.keys():
        raise HTTPException(status_code=403, detail="You cannot change email.")

    # Prevent non-doctors from updating doctor-specific fields
    if current_user.user_type != UserType.doctor:
        restricted_fields = {"license_number", "experience_years", "consultation_fee"}
        if restricted_fields & update_data.keys():
            raise HTTPException(status_code=403, detail="Only doctors can update doctor-specific fields")
    if "password" in update_data:
        hashed = hash_password(update_data["password"])
        update_data["password"] = hashed
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}

@router.get("/doctors", response_model=PaginatedResponse[DoctorList])
def get_doctors_list_with_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    full_name: str = Query(None),
    division: str = Query(None),
    district: str = Query(None),
    thana: str = Query(None),
    available_date: date = Query(None)
):
    if current_user.user_type not in [UserType.admin, UserType.patient]:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    query = db.query(User).filter(User.user_type == UserType.doctor)

    # Apply filters
    if full_name:
        query = query.filter(User.full_name.ilike(f"%{full_name}%"))
    if division:
        query = query.filter(User.division == division)
    if district:
        query = query.filter(User.district == district)
    if thana:
        query = query.filter(User.thana == thana)

    # Filter by doctor availability
    if available_date:
        available_doctor_ids = db.query(DoctorSchedule.doctor_id).filter(
            DoctorSchedule.date == available_date,
            DoctorSchedule.status == ScheduleStatus.available
        ).distinct().all()
        available_ids = [d[0] for d in available_doctor_ids]

        query = query.filter(User.id.in_(available_ids))

    # Pagination
    total = query.count()
    total_pages = ceil(total / limit)
    doctors = query.order_by(User.full_name) \
        .offset((page - 1) * limit) \
        .limit(limit) \
        .all()

    return PaginatedResponse(
        data=doctors,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/patients", response_model=PaginatedResponse[PatientWithAppointments])
def get_patients_list_with_filters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    full_name: str = Query(None),
):
    skip = (page - 1) * limit

    if current_user.user_type == UserType.admin:
        query = db.query(User).filter(User.user_type == UserType.patient)

        #  Apply full_name filter
        if full_name:
            query = query.filter(User.full_name.ilike(f"%{full_name}%"))

        total = query.count()
        total_pages = ceil(total / limit)

        patients = query.options(
            joinedload(User.appointments).joinedload(Appointment.doctor)
        ).order_by(User.full_name).offset(skip).limit(limit).all()

        return PaginatedResponse(
            data=patients,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    elif current_user.user_type == UserType.doctor:
        patient_ids_query = (
            db.query(Appointment.patient_id)
            .filter(Appointment.doctor_id == current_user.id)
            .distinct()
        )

        if full_name:
            # Join patient info to apply full_name filter
            patient_ids_query = patient_ids_query.join(User, Appointment.patient_id == User.id)
            patient_ids_query = patient_ids_query.filter(User.full_name.ilike(f"%{full_name}%"))

        total = patient_ids_query.count()
        total_pages = ceil(total / limit)

        patient_ids = patient_ids_query.order_by(Appointment.patient_id).offset(skip).limit(limit).all()
        patient_ids = [pid for (pid,) in patient_ids]

        patients = db.query(User).filter(User.id.in_(patient_ids)).options(
            joinedload(User.appointments.and_(
                Appointment.doctor_id == current_user.id
            )).joinedload(Appointment.doctor)
        ).all()

        return PaginatedResponse(
            data=patients,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    else:
        raise HTTPException(status_code=403, detail="Not authorized to view patients")