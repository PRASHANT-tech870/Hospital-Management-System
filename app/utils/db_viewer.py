from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Patient, Doctor, Staff, DoctorSchedule

# Create database connection
engine = create_engine("sqlite:///hospital.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Query all users
users = db.query(User).all()
for user in users:
    print(f"\nUser ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Role: {user.role}")
    
    # Get role-specific details
    if user.role == "PATIENT":
        patient = user.patient
        print(f"Emergency Contact: {patient.emergency_contact}")
        print(f"Medical History: {patient.medical_history}")
    elif user.role == "DOCTOR":
        doctor = user.doctor
        print(f"Specialization: {doctor.specialization}")
        print(f"Consultation Fee: {doctor.consultation_fee}")
    elif user.role == "STAFF":
        staff = user.staff
        print(f"Position: {staff.position}")

# Add this to your db_viewer.py to check schedules
def view_doctor_schedules():
    doctors = db.query(Doctor).all()
    for doctor in doctors:
        print(f"\nDoctor: {doctor.user.username}")
        schedules = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor.id).all()
        for schedule in schedules:
            print(f"Day {schedule.day_of_week}: {schedule.start_time} - {schedule.end_time}")

if __name__ == "__main__":
    view_doctor_schedules()

db.close() 