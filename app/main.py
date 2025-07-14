from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, users,upload,appointments, doctor_schedule
from app.utils.scheduler import start as start_scheduler

start_scheduler()

app = FastAPI(title="Appointments Booking System")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(upload.router, prefix="/api", tags=["Image Upload"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(doctor_schedule.router, prefix="/api/doctor-schedule", tags=["Doctor Schedule"])
