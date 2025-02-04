from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import json
from app.db import SessionLocal, engine, get_db
from app.models import Base, Admin, Department
from app.routers import patients, auth, appointments, doctors, medical_history, billing, admin, staff


# Add this if you're using SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_default_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            # Create default admin
            admin = Admin(
                username="admin",
                password="admin123",  # In production, use hashed password
                email="admin@hospital.com"
            )
            db.add(admin)
            db.commit()
            print("Default admin account created")
    except Exception as e:
        print(f"Error creating admin account: {e}")
    finally:
        db.close()

def create_default_departments():
    db = SessionLocal()
    try:
        # Check if departments exist
        if db.query(Department).count() == 0:
            departments = [
                Department(name="Cardiology", budget=100000),
                Department(name="Neurology", budget=120000),
                Department(name="Pediatrics", budget=90000),
                Department(name="Orthopedics", budget=110000),
                Department(name="General Medicine", budget=80000)
            ]
            db.add_all(departments)
            db.commit()
            print("Default departments created")
    except Exception as e:
        print(f"Error creating departments: {e}")
    finally:
        db.close()

# Call this after Base.metadata.create_all(bind=engine)
create_default_admin()
create_default_departments()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files BEFORE the root route
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(medical_history.router)
app.include_router(billing.router)
app.include_router(admin.router)
app.include_router(staff.router)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse('app/static/index.html')

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return FileResponse('app/static/register.html')

@app.get("/patient-dashboard", response_class=HTMLResponse)
async def patient_dashboard():
    return FileResponse('app/static/patient-dashboard.html')

@app.get("/doctor-dashboard", response_class=HTMLResponse)
async def doctor_dashboard():
    return FileResponse('app/static/doctor-dashboard.html')

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    return FileResponse('app/static/admin-dashboard.html')

@app.get("/staff-dashboard", response_class=HTMLResponse)
async def staff_dashboard():
    return FileResponse('app/static/staff-dashboard.html')

@app.get("/admin-login", response_class=HTMLResponse)
async def admin_login_page():
    return FileResponse('app/static/admin-login.html')
