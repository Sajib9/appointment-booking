# appointment-booking system
## 📌 Features

- 👤 JWT-based Authentication (Admin, Doctor, Patient)
-  👤 Profile management
- 📅 Doctor Schedule Management
- 🩺 Patient Appointment Booking
- 📤 Background Jobs (Reminders, Monthly Reports)
- 🔍 Filtering (Doctors, Patients, Appointments)
- 🛡️ Strong Validation (Mobile, Password, File Uploads)
- 🔁 RESTful APIs documented with Swagger UI

---

## 🚀 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL 8
- **Docker**: Used for Database Access
- **ORM**: SQLAlchemy + Alembic
- **Authentication**: JWT (Access/Refresh)
- **Background Scheduler**: APScheduler
- **Documentation**: Swagger UI (`/docs`)
## ⚙️ Setup Instructions

---

- **Python Version**: 3.10 or higher
- **Clone Project**:git clone https://github.com/Sajib9/appointment-booking.git
- **Navigate to Project Directory**:
  ```bash
  cd appointment-booking
  ```
- **Install Dependencies**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Create `.env` File**: Copy `.env.example` to `.env` and update with your database credentials.
- **Run Migrations**: 
  ```bash
  alembic upgrade head
  ```
- **Run Seeder**:
- ```bash
  python seed/users.py
  ```
- **Start the Application**: 
  ```bash
    uvicorn app.main:app --reload
    ```
- **Access Swagger UI**: Open your browser and go to `http://127.0.0.1:8000/docs`
## ⚙️ Database Schema Explanation

---

### Users Table
-Stores all user types: Admin, Doctor, and Patient.

### Appointments Table
- Contains appointment details, linked to both Doctor and Patient.
- Status field to track appointment state (Pending, Confirmed, Cancelled,Completed).
- Date and time fields for scheduling.
- Foreign keys to link to Users table for both doctor and patient.
### Doctor Schedule Table
- Contains schedule details for each doctor.
- Includes fields for start and end times, and days.
- Foreign key to link to Users table for the doctor.
- ### Background Jobs
- Handles reminders and monthly reports.

---
### Challenges
- **Background Jobs**: Setting up APScheduler for background tasks like reminders and reports.
- **Database Migrations**: Managing schema changes with Alembic.
- **Seeder**: Creating a seeder script to populate initial data for testing.



