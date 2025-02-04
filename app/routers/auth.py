from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Doctor, Patient, DoctorSchedule, Staff, Department, TimeSlot
from app.schemas import LoginRequest, DoctorCreate, PatientCreate, StaffCreate
from app import crud
from datetime import time, datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/doctor")
async def register_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    try:
        # Check if username exists
        if db.query(User).filter(User.username == doctor.username).first():
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Check if department exists
        department = db.query(Department).filter(Department.id == doctor.department_id).first()
        if not department:
            raise HTTPException(
                status_code=400,
                detail=f"Department with ID {doctor.department_id} does not exist"
            )

        # Create user
        user = User(
            username=doctor.username,
            email=doctor.email,
            password=doctor.password,  # In production, hash the password
            role="DOCTOR"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create doctor
        new_doctor = Doctor(
            user_id=user.id,
            specialization=doctor.specialization,
            consultation_fee=doctor.consultation_fee,
            department_id=doctor.department_id
        )
        db.add(new_doctor)
        db.commit()  # Commit to get the doctor's ID
        db.refresh(new_doctor)

        # Add default schedule for weekdays (Monday to Friday)
        for day in range(0, 5):  # 0 = Monday, 4 = Friday
            schedule = DoctorSchedule(
                doctor_id=new_doctor.id,
                day_of_week=day,
                start_time=time(9, 0),  # 9:00 AM
                end_time=time(17, 0),   # 5:00 PM
                is_available=True
            )
            db.add(schedule)

        # Create default time slots for the next 30 days
        today = datetime.now().date()
        for i in range(30):
            current_date = today + timedelta(days=i)
            if current_date.weekday() < 5:  # Monday to Friday
                for hour in range(9, 17):  # 9 AM to 5 PM
                    time_slot = TimeSlot(
                        doctor_id=new_doctor.id,
                        date=current_date,
                        start_time=time(hour, 0),
                        end_time=time(hour + 1, 0),
                        is_available=True
                    )
                    db.add(time_slot)

        db.commit()
        return {"message": "Doctor registered successfully"}
        
    except Exception as e:
        db.rollback()
        print(f"Error registering doctor: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error registering doctor: {str(e)}"
        )

@router.post("/register/patient")
def register_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        user = User(
            username=patient.username,
            email=patient.email,
            password=patient.password,
            role="PATIENT"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        new_patient = Patient(
            user_id=user.id,
            medical_history=patient.medical_history,
            emergency_contact=patient.emergency_contact
        )
        db.add(new_patient)
        db.commit()
        return {"message": "Patient registered successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(
            User.username == request.username,
            User.role == request.role
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        if user.password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
            
        # Get role-specific ID
        role_id = None
        if user.role == "PATIENT":
            role_id = user.patient.id
        elif user.role == "DOCTOR":
            role_id = user.doctor.id
        elif user.role == "STAFF":
            role_id = user.staff.id
            
        response_data = {
            "message": "Login successful",
            "role": request.role,
            "username": user.username,
            "id": role_id  # Use role-specific ID instead of user.id
        }
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/create-test-user")
def create_test_user(db: Session = Depends(get_db)):
    try:
        test_user = PatientCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            medical_history="None",
            emergency_contact="1234567890"
        )
        
        patient = crud.create_patient(db=db, patient=test_user)
        return {"message": "Test user created successfully", "user_id": patient.id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/register/staff", response_model=StaffCreate)
async def register_staff(staff_data: StaffCreate, db: Session = Depends(get_db)):
    # Check if username exists
    if db.query(User).filter(User.username == staff_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Create user
    user = User(
        username=staff_data.username,
        email=staff_data.email,
        password=staff_data.password,  # In production, hash the password
        role="STAFF"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create staff
    staff = Staff(
        user_id=user.id,
        name=staff_data.name
    )
    db.add(staff)
    db.commit()
    
    return staff_data
